export interface Appointment {
  id: number;
  date: string;
  time: string;
  doctorName: string;
  reason: string;
}

export interface Patient {
  id: string | number;
  name: string;
  ssn: string;
  insurance: string;
  appointments?: Appointment[];
}

export interface Medication {
  id: number;
  name: string;
}

export interface Treatment {
  description: string;
  cost: number;
  medications: Medication[];
}

export interface DoctorEarnings {
  id: number;
  name: string;
  specialty: string;
  department: string;
  year: number;
  totalCosts: number;
}

export interface DbStatus {
  dbType: 'MariaDB' | 'MongoDB';
}
