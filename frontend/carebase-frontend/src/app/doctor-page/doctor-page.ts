import { Component, inject } from '@angular/core';
import { ActionCard } from '../action-card/action-card';
import { MatCard, MatCardModule } from '@angular/material/card';
import { Router } from '@angular/router';

@Component({
  imports: [ActionCard, MatCardModule],
  selector: 'app-doctor-page',
  styleUrl: './doctor-page.css',
  templateUrl: './doctor-page.html',
})
export class DoctorPage {
  private router = inject(Router);

  toUseCase() {
    this.router.navigate(['usecase']);
  }
  toReport() {
    this.router.navigate(['report']);
  }
}
