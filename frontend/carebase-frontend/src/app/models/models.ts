export interface Appointment {
  id: number;
  date: string; // TODO: check if date type would be better
  time: string;
  doctorName: string;
  reason: string;
}

export interface Patient {
  id: number;
  name: string;
  insurance: string;
  appointments: Appointment[];
}

export interface Medication {
  name: string;
  id: string;
}

export interface Treatment {
  patientId: number;
  appointmentId: number;
  description: string;
  cost: number;
  medications: Medication[];
}

export interface DoctorEarnings {
  id: string;
  name: string;
  specialty: string;
  department: string;
  year: number;
  totalEarnings: number;
}
