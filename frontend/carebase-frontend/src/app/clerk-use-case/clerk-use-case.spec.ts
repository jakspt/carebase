import { ComponentFixture, TestBed } from '@angular/core/testing';
import { provideHttpClient } from '@angular/common/http';
import { provideAnimationsAsync } from '@angular/platform-browser/animations/async';
import { provideNativeDateAdapter } from '@angular/material/core';
import { ClerkUseCase } from './clerk-use-case';
import { ClerkService } from '../services/clerk-service';
import { of, throwError } from 'rxjs';
import { Clerk, Doctor, Patient } from '../models/models';

describe('ClerkUseCase', () => {
  let component: ClerkUseCase;
  let fixture: ComponentFixture<ClerkUseCase>;
  let clerkService: ClerkService;

  const mockClerk: Clerk = { id: '1001', name: 'Erika Mustermann', ssn: '1001' };
  const mockPatient: Patient = {
    id: '2041',
    name: 'Johann Schmidt',
    ssn: '2041',
    insurance: 'ÖGK',
    nacaScore: 2,
  };
  const mockDoctors: Doctor[] = [
    {
      id: '3011',
      name: 'Dr. Sarah Connor',
      ssn: '3011',
      specialty: 'Cardiology',
      position: 'Chief Physician',
      department: 'Cardiology',
    },
    {
      id: '3012',
      name: 'Dr. John Smith',
      ssn: '3012',
      specialty: 'Neurology',
      position: 'Specialist',
      department: 'Neurology',
    },
  ];

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [ClerkUseCase],
      providers: [
        provideHttpClient(),
        provideAnimationsAsync(),
        provideNativeDateAdapter(),
        ClerkService,
      ],
    }).compileComponents();

    clerkService = TestBed.inject(ClerkService);
    clerkService.setActiveClerk(mockClerk);

    fixture = TestBed.createComponent(ClerkUseCase);
    component = fixture.componentInstance;
    await fixture.whenStable();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });

  it('should reflect active clerk from ClerkService', () => {
    expect(component.activeClerk()).toEqual(mockClerk);
  });

  it('should set selected patient and reset downstream selections', () => {
    component.selectPatient(mockPatient);
    expect(component.selectedPatient()).toEqual(mockPatient);
    expect(component.selectedTimeSlot()).toBeNull();
  });

  it('should filter doctors by selected department', () => {
    // Mock doctor list in component
    (component as any).allDoctorsSignal.set(mockDoctors);
    component.selectedDepartment.set('Cardiology');

    expect(component.filteredDoctors().length).toBe(1);
    expect(component.filteredDoctors()[0].name).toBe('Dr. Sarah Connor');
  });

  it('should clear selected time slot when doctor or department changes', () => {
    component.selectedTimeSlot.set('09:00');
    component.onDepartmentChange('Cardiology');
    expect(component.selectedTimeSlot()).toBeNull();

    component.selectedTimeSlot.set('09:00');
    component.onDoctorChange(mockDoctors[0]);
    expect(component.selectedTimeSlot()).toBeNull();
  });

  it('should correctly identify severe NACA scores (5-7)', () => {
    expect(component.isSevereNaca(undefined)).toBe(false);
    expect(component.isSevereNaca(2)).toBe(false);
    expect(component.isSevereNaca(4)).toBe(false);
    expect(component.isSevereNaca(5)).toBe(true);
    expect(component.isSevereNaca(7)).toBe(true);
  });

  it('should book appointment successfully via ClerkService', async () => {
    const bookSpy = vi.spyOn(clerkService, 'bookAppointment').mockReturnValue(
      of({
        success: true,
        appointmentId: 42,
        message: 'Appointment successfully scheduled',
      }),
    );

    component.selectPatient(mockPatient);
    component.selectDoctor(mockDoctors[0]);
    component.selectedDate.set(new Date(2026, 9, 15));
    component.selectedTimeSlot.set('09:00');
    component.reason.set('Routine checkup');

    await component.confirmBooking();

    expect(bookSpy).toHaveBeenCalledWith(
      expect.objectContaining({
        patientSsn: '2041',
        doctorSsn: '3011',
        date: '2026-10-15',
        time: '09:00',
        reason: 'Routine checkup',
        clerkSsn: '1001',
      }),
    );
    expect(component.bookingSuccess()).toBe(true);
  });

  it('should allow clearing active clerk profile', () => {
    expect(component.activeClerk()).toEqual(mockClerk);
    component.clearClerk();
    expect(component.activeClerk()).toBeNull();
  });

  it('should initialize minDate at midnight (00:00:00) so today is selectable', () => {
    expect(component.minDate.getHours()).toBe(0);
    expect(component.minDate.getMinutes()).toBe(0);
    expect(component.minDate.getSeconds()).toBe(0);
    expect(component.minDate.getMilliseconds()).toBe(0);
  });

  it('should toggle time slot selection on click', () => {
    component.selectTimeSlot('09:00');
    expect(component.selectedTimeSlot()).toBe('09:00');

    // Clicking the same slot toggles it off
    component.selectTimeSlot('09:00');
    expect(component.selectedTimeSlot()).toBeNull();

    // Selecting a different slot sets it
    component.selectTimeSlot('09:30');
    expect(component.selectedTimeSlot()).toBe('09:30');
  });

  it('should compare doctors by SSN accurately', () => {
    expect(component.compareDoctor(mockDoctors[0], mockDoctors[0])).toBe(true);
    expect(component.compareDoctor(mockDoctors[0], { ...mockDoctors[0] })).toBe(true);
    expect(component.compareDoctor(mockDoctors[0], mockDoctors[1])).toBe(false);
    expect(component.compareDoctor(mockDoctors[0], null)).toBe(false);
  });

  it('should reset workflow state while preserving active clerk profile', () => {
    component.selectPatient(mockPatient);
    component.selectDoctor(mockDoctors[0]);
    component.selectedTimeSlot.set('09:00');
    component.reason.set('Routine checkup');
    (component as any).bookingSuccess.set(true);

    component.resetWorkflow();

    expect(component.selectedPatient()).toBeNull();
    expect(component.selectedDoctor()).toBeNull();
    expect(component.selectedTimeSlot()).toBeNull();
    expect(component.reason()).toBe('');
    expect(component.bookingSuccess()).toBe(false);
    expect(component.activeClerk()).toEqual(mockClerk); // Preserved per AC-1.1.2
  });

  it('should handle 409 conflict during booking and reload slots', async () => {
    vi.spyOn(clerkService, 'bookAppointment').mockReturnValue(
      throwError(() => ({
        status: 409,
        error: { error: 'The doctor already has an appointment scheduled at this time.' },
      })),
    );
    const reloadSpy = vi.spyOn(component.timeSlotsResource, 'reload').mockReturnValue(true);
    const mockStepper = { selectedIndex: 3 } as any;

    component.selectPatient(mockPatient);
    component.selectDoctor(mockDoctors[0]);
    component.selectedDate.set(new Date(2026, 9, 15));
    component.selectedTimeSlot.set('09:00');

    await component.confirmBooking(mockStepper);

    expect(component.bookingSuccess()).toBe(false);
    expect(component.selectedTimeSlot()).toBeNull();
    expect(reloadSpy).toHaveBeenCalled();
    expect(mockStepper.selectedIndex).toBe(2);
  });

  it('should update patientInputValue immediately on typing and debounce search query', async () => {
    vi.useFakeTimers();
    try {
      const mockEvent = { target: { value: 'Johann' } } as unknown as Event;
      component.onPatientSearchInput(mockEvent);

      expect(component.patientInputValue()).toBe('Johann');
      expect(component.patientSearchQuery()).toBe(''); // Debounced

      vi.advanceTimersByTime(300);
      expect(component.patientSearchQuery()).toBe('Johann');
    } finally {
      vi.useRealTimers();
    }
  });

  it('should format patient details into patientInputValue when selecting patient', () => {
    component.selectPatient(mockPatient);
    expect(component.patientInputValue()).toBe('Johann Schmidt (SSN: 2041)');
    expect(component.patientSearchQuery()).toBe('Johann Schmidt');
  });

  it('should clear patientInputValue and patientSearchQuery on workflow reset', () => {
    component.patientInputValue.set('Johann');
    component.patientSearchQuery.set('Johann');
    component.resetWorkflow();
    expect(component.patientInputValue()).toBe('');
    expect(component.patientSearchQuery()).toBe('');
  });
});
