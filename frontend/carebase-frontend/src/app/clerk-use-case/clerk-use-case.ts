import { Component, computed, inject, signal } from '@angular/core';
import { CommonModule, DatePipe } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { MatAutocompleteModule } from '@angular/material/autocomplete';
import { MatStepper, MatStepperModule } from '@angular/material/stepper';
import { MatInputModule } from '@angular/material/input';
import { MatFormFieldModule } from '@angular/material/form-field';
import { MatButtonModule } from '@angular/material/button';
import { MatChipsModule } from '@angular/material/chips';
import { MatIconModule } from '@angular/material/icon';
import { MatCardModule } from '@angular/material/card';
import { MatSelectModule } from '@angular/material/select';
import { MatDatepickerModule } from '@angular/material/datepicker';
import { provideNativeDateAdapter } from '@angular/material/core';
import { MatSnackBar, MatSnackBarModule } from '@angular/material/snack-bar';
import { MatProgressSpinnerModule } from '@angular/material/progress-spinner';
import { MatDividerModule } from '@angular/material/divider';
import { takeUntilDestroyed, toObservable, toSignal } from '@angular/core/rxjs-interop';
import {
  Subject,
  debounceTime,
  distinctUntilChanged,
  firstValueFrom,
  map,
  of,
  switchMap,
  timer,
} from 'rxjs';
import { Clerk, CreateAppointmentRequest, Doctor, Patient, TimeSlot } from '../models/models';
import { ClerkService } from '../services/clerk-service';

@Component({
  imports: [
    CommonModule,
    FormsModule,
    MatAutocompleteModule,
    MatStepperModule,
    MatInputModule,
    MatFormFieldModule,
    MatButtonModule,
    MatChipsModule,
    MatIconModule,
    MatCardModule,
    MatSelectModule,
    MatDatepickerModule,
    MatSnackBarModule,
    MatProgressSpinnerModule,
    MatDividerModule,
    DatePipe,
  ],
  providers: [provideNativeDateAdapter()],
  selector: 'app-clerk-use-case',
  styleUrl: './clerk-use-case.css',
  templateUrl: './clerk-use-case.html',
})
export class ClerkUseCase {
  private readonly clerkService = inject(ClerkService);
  private readonly snackBar = inject(MatSnackBar);

  // ── Clerk Profile ──
  readonly activeClerk = this.clerkService.getActiveClerk();
  readonly clerkSearchQuery = signal('');
  readonly clerkSearchResults = this.clerkService.searchClerks(this.clerkSearchQuery);
  readonly availableClerks = computed<Clerk[]>(() => {
    if (this.clerkSearchResults.hasValue()) {
      return this.clerkSearchResults.value()?.clerks ?? [];
    }
    return [];
  });

  // ── Step 1: Patient Search ──
  readonly patientSearchQuery = signal('');
  readonly patientInputValue = signal('');
  private readonly patientSearchSubject$ = new Subject<string>();
  readonly patientSearchResults = this.clerkService.searchPatients(this.patientSearchQuery);

  private readonly spinnerDelayMs = 250;
  readonly showPatientSpinner = toSignal(
    toObservable(this.patientSearchResults.isLoading).pipe(
      switchMap((loading) =>
        loading ? timer(this.spinnerDelayMs).pipe(map(() => true)) : of(false),
      ),
    ),
    { initialValue: false },
  );

  readonly patients = computed<Patient[]>(() => {
    if (this.patientSearchResults.hasValue()) {
      return this.patientSearchResults.value()?.patients ?? [];
    }
    return [];
  });
  readonly selectedPatient = signal<Patient | null>(null);

  constructor() {
    this.patientSearchSubject$
      .pipe(debounceTime(300), distinctUntilChanged(), takeUntilDestroyed())
      .subscribe((query) => {
        this.patientSearchQuery.set(query);
      });
  }

  // ── Step 2: Department & Doctor Selection ──
  readonly doctorsResource = this.clerkService.getDoctors();
  // Signal used for tests or live data
  readonly allDoctorsSignal = signal<Doctor[] | null>(null);
  readonly allDoctors = computed<Doctor[]>(() => {
    if (this.allDoctorsSignal()) {
      return this.allDoctorsSignal()!;
    }
    if (this.doctorsResource.hasValue()) {
      return this.doctorsResource.value()?.doctors ?? [];
    }
    return [];
  });

  readonly departments = computed<string[]>(() => {
    const list = this.allDoctors();
    const depts = new Set<string>();
    for (const d of list) {
      if (d.department) depts.add(d.department);
    }
    return Array.from(depts).sort();
  });

  readonly selectedDepartment = signal<string>('');
  readonly filteredDoctors = computed<Doctor[]>(() => {
    const dept = this.selectedDepartment();
    const all = this.allDoctors();
    if (!dept) return all;
    return all.filter((d) => d.department === dept);
  });

  readonly selectedDoctor = signal<Doctor | null>(null);

  // ── Step 3: Date & Time Slot Selection ──
  readonly minDate = (() => {
    const d = new Date();
    d.setHours(0, 0, 0, 0);
    return d;
  })();
  readonly selectedDate = signal<Date | null>(this.minDate);
  readonly formattedDate = computed<string>(() => {
    const raw = this.selectedDate();
    if (!raw) return '';
    const d = raw instanceof Date ? raw : new Date(raw);
    if (isNaN(d.getTime())) return '';
    const year = d.getFullYear();
    const month = String(d.getMonth() + 1).padStart(2, '0');
    const day = String(d.getDate()).padStart(2, '0');
    return `${year}-${month}-${day}`;
  });

  readonly selectedTimeSlot = signal<string | null>(null);

  // Query parameter signal for slot loading
  readonly slotParams = computed(() => {
    const date = this.formattedDate();
    const doctor = this.selectedDoctor();
    const patient = this.selectedPatient();
    if (!date || !doctor) return undefined;
    return {
      date,
      doctorSsn: doctor.ssn,
      patientSsn: patient?.ssn,
    };
  });

  readonly timeSlotsResource = this.clerkService.getTimeSlots(this.slotParams);

  // Debounced spinner for slots (<250ms threshold)
  readonly showSlotSpinner = toSignal(
    toObservable(this.timeSlotsResource.isLoading).pipe(
      switchMap((loading) =>
        loading ? timer(this.spinnerDelayMs).pipe(map(() => true)) : of(false),
      ),
    ),
    { initialValue: false },
  );

  readonly timeSlots = computed<TimeSlot[]>(() => {
    if (this.timeSlotsResource.hasValue()) {
      return this.timeSlotsResource.value()?.slots ?? [];
    }
    return [];
  });

  readonly hasAvailableSlots = computed<boolean>(() => {
    return this.timeSlots().some((s) => s.available);
  });

  // ── Step 4: Reason & Booking Review ──
  readonly reason = signal<string>('');
  readonly isSubmitting = signal<boolean>(false);
  readonly bookingSuccess = signal<boolean>(false);
  readonly createdAppointmentId = signal<number | null>(null);

  // ── Methods & Handlers ──

  onClerkSearchInput(event: Event): void {
    const val = (event.target as HTMLInputElement).value;
    this.clerkSearchQuery.set(val);
  }

  selectClerk(clerk: Clerk): void {
    this.clerkService.setActiveClerk(clerk);
    this.clerkSearchQuery.set('');
  }

  clearClerk(): void {
    this.clerkService.setActiveClerk(null);
    this.clerkSearchQuery.set('');
  }

  onPatientSearchInput(event: Event): void {
    const val = (event.target as HTMLInputElement).value;
    this.patientInputValue.set(val);
    this.patientSearchSubject$.next(val);
  }

  selectPatient(patient: Patient, stepper?: MatStepper): void {
    this.selectedPatient.set(patient);
    this.patientInputValue.set(this.displayPatient(patient));
    this.patientSearchQuery.set(patient ? patient.name : '');
    this.selectedTimeSlot.set(null);
    if (stepper) {
      stepper.next();
    }
  }

  displayPatient(patient: Patient | null): string {
    return patient ? `${patient.name} (SSN: ${patient.ssn})` : '';
  }

  displayClerk(clerk: Clerk | null): string {
    return clerk ? `${clerk.name} (SSN: ${clerk.ssn})` : '';
  }

  compareDoctor(d1: Doctor | null, d2: Doctor | null): boolean {
    return d1?.ssn === d2?.ssn;
  }

  isSevereNaca(score?: number | null): boolean {
    return score !== undefined && score !== null && score >= 5;
  }

  onDepartmentChange(dept: string): void {
    this.selectedDepartment.set(dept);
    this.selectedDoctor.set(null);
    this.selectedTimeSlot.set(null);
  }

  onDoctorChange(doctor: Doctor): void {
    this.selectedDoctor.set(doctor);
    this.selectedTimeSlot.set(null);
  }

  selectDoctor(doctor: Doctor, stepper?: MatStepper): void {
    this.selectedDoctor.set(doctor);
    this.selectedTimeSlot.set(null);
    if (stepper) {
      stepper.next();
    }
  }

  onDateChange(date: Date | null): void {
    this.selectedDate.set(date);
    this.selectedTimeSlot.set(null);
  }

  selectTimeSlot(time: string, stepper?: MatStepper): void {
    if (this.selectedTimeSlot() === time) {
      this.selectedTimeSlot.set(null);
    } else {
      this.selectedTimeSlot.set(time);
      if (stepper) {
        stepper.next();
      }
    }
  }

  async confirmBooking(stepper?: MatStepper): Promise<void> {
    const patient = this.selectedPatient();
    const doctor = this.selectedDoctor();
    const date = this.formattedDate();
    const time = this.selectedTimeSlot();
    const activeClerk = this.activeClerk();

    if (!patient || !doctor || !date || !time) {
      this.snackBar.open('Please fill in all required appointment details.', 'Close', {
        duration: 4000,
      });
      return;
    }

    const payload: CreateAppointmentRequest = {
      patientSsn: String(patient.ssn),
      doctorSsn: String(doctor.ssn),
      date,
      time,
      reason: this.reason().trim(),
      clerkSsn: activeClerk ? String(activeClerk.ssn) : undefined,
    };

    this.isSubmitting.set(true);

    try {
      const response = await firstValueFrom(this.clerkService.bookAppointment(payload));
      if (response.success) {
        this.bookingSuccess.set(true);
        this.createdAppointmentId.set(response.appointmentId ?? null);
        this.snackBar.open(
          `Appointment successfully scheduled (ID: ${response.appointmentId ?? 'N/A'})`,
          'Close',
          { duration: 5000 },
        );
      }
    } catch (err: any) {
      if (err?.status === 409) {
        this.snackBar.open(
          'Selected slot was just booked by another user. Please choose an alternate slot.',
          'Close',
          { duration: 6000 },
        );
        this.selectedTimeSlot.set(null);
        this.timeSlotsResource.reload();
        if (stepper) {
          stepper.selectedIndex = 2;
        }
      } else {
        const errorMsg =
          err?.error?.error || 'Failed to schedule appointment. Please check your data and retry.';
        this.snackBar.open(errorMsg, 'Close', { duration: 5000 });
      }
    } finally {
      this.isSubmitting.set(false);
    }
  }

  resetWorkflow(stepper?: MatStepper): void {
    this.selectedPatient.set(null);
    this.selectedDepartment.set('');
    this.selectedDoctor.set(null);
    this.selectedDate.set(this.minDate);
    this.selectedTimeSlot.set(null);
    this.reason.set('');
    this.bookingSuccess.set(false);
    this.createdAppointmentId.set(null);
    this.patientInputValue.set('');
    this.patientSearchQuery.set('');
    if (stepper) {
      stepper.reset();
    }
  }
}
