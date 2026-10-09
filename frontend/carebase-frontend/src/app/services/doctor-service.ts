import { HttpClient, httpResource } from '@angular/common/http';
import { Service, inject } from '@angular/core';
import { Observable } from 'rxjs';
import { DoctorEarnings, Medication, Patient, Treatment } from '../models/models';

@Service()
export class DoctorService {
  private readonly http = inject(HttpClient);

  searchPatients(query: () => string) {
    return httpResource<{ patients: Patient[] }>(() => {
      const q = query()?.trim();
      if (!q) return undefined;
      return `/api/doctor/patients/search?q=${encodeURIComponent(q)}`;
    });
  }

  getPatientDetails(patientId: () => string | number | null | undefined) {
    return httpResource<Patient>(() => {
      const id = patientId();
      if (!id) return undefined;
      return `/api/doctor/patients/${id}`;
    });
  }

  getMedications() {
    return httpResource<{ medications: Medication[] }>(() => '/api/doctor/medications');
  }

  addTreatment(
    patientId: string | number,
    appointmentId: number,
    treatment: Treatment,
  ): Observable<{ success: boolean }> {
    return this.http.post<{ success: boolean }>(
      `/api/doctor/patients/${patientId}/appointments/${appointmentId}/treatments`,
      treatment,
    );
  }

  getReport(year: () => number) {
    return httpResource<{ year: number; data: DoctorEarnings[] }>(() => {
      const y = year();
      return `/api/doctor/report?year=${y}`;
    });
  }
}
