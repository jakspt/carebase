import { Component, inject } from '@angular/core';
import { ActionCard } from '../action-card/action-card';
import { MatIconModule } from '@angular/material/icon';
import { Router } from '@angular/router';

@Component({
  imports: [ActionCard, MatIconModule],
  selector: 'app-doctor-page',
  styleUrl: './doctor-page.css',
  templateUrl: './doctor-page.html',
})
export class DoctorPage {
  private router = inject(Router);

  toUseCase() {
    this.router.navigate(['/doctor/usecase']);
  }
  toReport() {
    this.router.navigate(['/doctor/report']);
  }
}
