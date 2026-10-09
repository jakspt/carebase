import { HttpClient, httpResource } from '@angular/common/http';
import { Service, Injector, inject, signal } from '@angular/core';
import { Observable } from 'rxjs';
import {
  Clerk,
  Doctor,
  Patient,
  TimeSlot,
  TimeSlotsResponse,
  CreateAppointmentRequest,
  CreateAppointmentResponse,
  PatientVisitsReportResponse,
} from '../models/models';

const CLERK_SESSION_KEY = 'carebase_active_clerk';

@Service()
export class ClerkService {
  private readonly http = inject(HttpClient);
  private readonly injector = inject(Injector);
  private readonly activeClerk = signal<Clerk | null>(this.getInitialClerk());

  private getInitialClerk(): Clerk | null {
    try {
      if (typeof window !== 'undefined' && window.sessionStorage) {
        const stored = window.sessionStorage.getItem(CLERK_SESSION_KEY);
        return stored ? JSON.parse(stored) : null;
      }
    } catch {
      // In SSR or restricted environments
    }
    return null;
  }

  getActiveClerk() {
    return this.activeClerk.asReadonly();
  }

  setActiveClerk(clerk: Clerk | null): void {
    this.activeClerk.set(clerk);
    try {
      if (typeof window !== 'undefined' && window.sessionStorage) {
        if (clerk) {
          window.sessionStorage.setItem(CLERK_SESSION_KEY, JSON.stringify(clerk));
        } else {
          window.sessionStorage.removeItem(CLERK_SESSION_KEY);
        }
      }
    } catch {
      // Ignore storage errors
    }
  }

  searchClerks(query: () => string) {
    return httpResource<{ clerks: Clerk[] }>(
      () => {
        const q = query()?.trim() ?? '';
        return `/api/clerk/clerks/search?q=${encodeURIComponent(q)}`;
      },
      { injector: this.injector },
    );
  }

  searchPatients(query: () => string) {
    return httpResource<{ patients: Patient[] }>(
      () => {
        const q = query()?.trim();
        if (!q || q.length < 2) return undefined;
        return `/api/clerk/patients/search?q=${encodeURIComponent(q)}`;
      },
      { injector: this.injector },
    );
  }

  getDoctors() {
    return httpResource<{ doctors: Doctor[] }>(() => '/api/clerk/doctors', {
      injector: this.injector,
    });
  }

  getTimeSlots(params: () => { date: string; doctorSsn: string; patientSsn?: string } | undefined) {
    return httpResource<TimeSlotsResponse>(
      () => {
        const p = params();
        if (!p || !p.date || !p.doctorSsn) return undefined;
        let url = `/api/clerk/time-slots?date=${encodeURIComponent(p.date)}&doctorSsn=${encodeURIComponent(p.doctorSsn)}`;
        if (p.patientSsn) {
          url += `&patientSsn=${encodeURIComponent(p.patientSsn)}`;
        }
        return url;
      },
      { injector: this.injector },
    );
  }

  bookAppointment(payload: CreateAppointmentRequest): Observable<CreateAppointmentResponse> {
    return this.http.post<CreateAppointmentResponse>('/api/clerk/appointments', payload);
  }

  getPatientVisitsReport(dateRange: () => { startDate: string; endDate: string } | undefined) {
    return httpResource<PatientVisitsReportResponse>(
      () => {
        const range = dateRange();
        if (!range || !range.startDate || !range.endDate) return undefined;
        return `/api/clerk/reports/patient-visits?startDate=${encodeURIComponent(range.startDate)}&endDate=${encodeURIComponent(range.endDate)}`;
      },
      { injector: this.injector },
    );
  }
}
