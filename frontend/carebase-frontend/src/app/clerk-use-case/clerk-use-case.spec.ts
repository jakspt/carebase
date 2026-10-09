import { ComponentFixture, TestBed } from '@angular/core/testing';
import { provideHttpClient } from '@angular/common/http';
import { provideAnimationsAsync } from '@angular/platform-browser/animations/async';
import { provideNativeDateAdapter } from '@angular/material/core';
import { ClerkUseCase } from './clerk-use-case';
import { ClerkService } from '../services/clerk-service';
import { of, throwError } from 'rxjs';
import { Clerk, Doctor, Patient } from '../models/models';
import { By } from '@angular/platform-browser';
import { MatStepper } from '@angular/material/stepper';

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

  it('should return informative NACA tooltip text', () => {
    expect(component.getNacaTooltip(undefined)).toBe('');
    expect(component.getNacaTooltip(null)).toBe('');
    expect(component.getNacaTooltip(2)).toContain('NACA 2: Pre-hospital severity score');
    expect(component.getNacaTooltip(6)).toContain('NACA 6: Pre-hospital severity score');
  });

  it('should render a quiet, de-escalated NACA chip in the selected patient card without alarm icons', async () => {
    const severePatient: Patient = {
      id: '9999',
      name: 'Severe Record Patient',
      ssn: '9999',
      insurance: 'ÖGK',
      nacaScore: 6,
    };
    component.selectPatient(severePatient);
    fixture.detectChanges();
    await fixture.whenStable();

    const card = fixture.nativeElement.querySelector('.selected-entity-card');
    expect(card).toBeTruthy();

    const nacaChip = card.querySelector('.naca-chip');
    expect(nacaChip).toBeTruthy();
    expect(nacaChip.textContent).toContain('NACA 6');

    // Emergency alarm icon and critical class should NOT be present
    expect(card.querySelector('.naca-icon')).toBeNull();
    expect(nacaChip.classList.contains('naca-critical')).toBe(false);
  });

  it('should render the persistent clinical summary strip in Step 2 with patient details and unselected doctor placeholder', async () => {
    const stepper = fixture.debugElement.query(By.directive(MatStepper)).componentInstance as MatStepper;
    component.selectedPatient.set(mockPatient);
    fixture.detectChanges();
    stepper.selectedIndex = 1;
    fixture.detectChanges();
    await fixture.whenStable();

    expect(stepper.selectedIndex).toBe(1);
    const strip = fixture.nativeElement.querySelector('.clinical-summary-strip');
    expect(strip).toBeTruthy();

    const patientCol = strip.querySelector('.patient-col');
    expect(patientCol.textContent).toContain('Johann Schmidt');
    expect(patientCol.textContent).toContain('2041');
    expect(patientCol.textContent).toContain('ÖGK');

    const doctorCol = strip.querySelector('.doctor-col');
    expect(doctorCol.textContent).toContain('Not selected');
  });

  it('should eliminate the Step 3 memory bridge by displaying both patient and doctor context persistently', async () => {
    const stepper = fixture.debugElement.query(By.directive(MatStepper)).componentInstance as MatStepper;
    component.selectedPatient.set(mockPatient);
    component.selectedDoctor.set(mockDoctors[0]);
    fixture.detectChanges();
    stepper.selectedIndex = 2;
    fixture.detectChanges();
    await fixture.whenStable();

    expect(stepper.selectedIndex).toBe(2);
    const strip = fixture.nativeElement.querySelector('.clinical-summary-strip');
    expect(strip).toBeTruthy();

    // Patient context is fully preserved (no memory bridge!)
    const patientCol = strip.querySelector('.patient-col');
    expect(patientCol.textContent).toContain('Johann Schmidt');
    expect(patientCol.textContent).toContain('2041');
    expect(patientCol.textContent).toContain('ÖGK');

    // Doctor context is also visible simultaneously
    const doctorCol = strip.querySelector('.doctor-col');
    expect(doctorCol.textContent).toContain('Dr. Sarah Connor');
    expect(doctorCol.textContent).toContain('Cardiology');
  });

  it('should maintain the persistent clinical summary strip in Step 4', async () => {
    const stepper = fixture.debugElement.query(By.directive(MatStepper)).componentInstance as MatStepper;
    component.selectedPatient.set(mockPatient);
    component.selectedDoctor.set(mockDoctors[0]);
    component.selectedTimeSlot.set('09:00');
    fixture.detectChanges();
    stepper.selectedIndex = 3;
    fixture.detectChanges();
    await fixture.whenStable();

    expect(stepper.selectedIndex).toBe(3);
    const strip = fixture.nativeElement.querySelector('.clinical-summary-strip');
    expect(strip).toBeTruthy();

    expect(strip.querySelector('.patient-col').textContent).toContain('Johann Schmidt');
    expect(strip.querySelector('.doctor-col').textContent).toContain('Dr. Sarah Connor');
  });

  it('should remove clinical summary strip when workflow is reset', async () => {
    const stepper = fixture.debugElement.query(By.directive(MatStepper)).componentInstance as MatStepper;
    component.selectedPatient.set(mockPatient);
    component.selectedDoctor.set(mockDoctors[0]);
    fixture.detectChanges();
    stepper.selectedIndex = 2;
    fixture.detectChanges();
    await fixture.whenStable();

    expect(fixture.nativeElement.querySelector('.clinical-summary-strip')).toBeTruthy();

    component.resetWorkflow(stepper);
    fixture.detectChanges();
    await fixture.whenStable();

    expect(fixture.nativeElement.querySelector('.clinical-summary-strip')).toBeNull();
  });

  it('should not auto-advance stepper on patient selection', () => {
    const stepper = fixture.debugElement.query(By.directive(MatStepper)).componentInstance as MatStepper;
    stepper.selectedIndex = 0;
    component.selectPatient(mockPatient, stepper);
    expect(stepper.selectedIndex).toBe(0);
  });

  it('should render canonical bottom action bar in Step 1 with Next button bound to selectedPatient state', async () => {
    fixture.detectChanges();
    await fixture.whenStable();

    const stepContainers = fixture.nativeElement.querySelectorAll('.step-container');
    const step1Container = stepContainers[0];
    const step1Actions = step1Container.querySelector('.step-actions');
    expect(step1Actions).toBeTruthy();

    const nextBtn = step1Actions.querySelector('button[matStepperNext]') as HTMLButtonElement;
    expect(nextBtn).toBeTruthy();
    expect(nextBtn.disabled).toBe(true);

    component.selectPatient(mockPatient);
    fixture.detectChanges();
    await fixture.whenStable();

    expect(nextBtn.disabled).toBe(false);
  });

  it('should purge redundant inline Next buttons from entity preview cards in Step 1 and Step 2', async () => {
    component.selectPatient(mockPatient);
    fixture.detectChanges();
    await fixture.whenStable();

    const stepContainers = fixture.nativeElement.querySelectorAll('.step-container');
    const step1Card = stepContainers[0].querySelector('.selected-entity-card');
    expect(step1Card).toBeTruthy();
    expect(step1Card.querySelector('button')).toBeNull();

    // In Step 2
    component.onDoctorChange(mockDoctors[0]);
    fixture.detectChanges();
    await fixture.whenStable();

    const step2Card = stepContainers[1].querySelector('.selected-entity-card');
    expect(step2Card).toBeTruthy();
    expect(step2Card.querySelector('button')).toBeNull();

    // Step 2 canonical action bar still exists
    const step2Actions = stepContainers[1].querySelector('.step-actions');
    expect(step2Actions).toBeTruthy();
    const step2NextBtn = step2Actions.querySelector('button[matStepperNext]') as HTMLButtonElement;
    expect(step2NextBtn).toBeTruthy();
    expect(step2NextBtn.disabled).toBe(false);
  });
});
