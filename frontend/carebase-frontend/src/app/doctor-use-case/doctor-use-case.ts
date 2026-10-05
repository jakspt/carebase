import { Component, signal } from '@angular/core';
import { MatAutocompleteModule } from '@angular/material/autocomplete';
import { MatStepperModule } from '@angular/material/stepper';
import { MatInputModule } from '@angular/material/input';
import { MatFormFieldModule } from '@angular/material/form-field';
import { MatAnchor, MatButtonModule } from '@angular/material/button';
import { form, max, min, minLength, required } from '@angular/forms/signals';
import { Medication } from '../models/models';

interface TreatmentFormModel {
  description: string | null;
  cost: number | null;
  medications: Medication[];
}

@Component({
  imports: [
    MatAutocompleteModule,
    MatStepperModule,
    MatInputModule,
    MatFormFieldModule,
    MatButtonModule,
  ],
  selector: 'app-doctor-use-case',
  styleUrl: './doctor-use-case.css',
  templateUrl: './doctor-use-case.html',
})
export class DoctorUseCase {
  readonly treatmentModel = signal<TreatmentFormModel>({
    cost: null,
    description: null,
    medications: [],
  });

  readonly treatmentForm = form(this.treatmentModel, (tree) => {
    required(tree.description);
    min(tree.cost, 0);
    max(tree.cost, 9999);
  });

  readonly options = signal(['abs', 'ded', 'xcz']);
}
