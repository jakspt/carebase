import { Component, inject } from '@angular/core';
import { ActionCard } from '../action-card/action-card';
import { MatCardModule } from '@angular/material/card';
import { Router } from '@angular/router';

@Component({
  imports: [ActionCard, MatCardModule],
  selector: 'app-clerk-page',
  styleUrl: './clerk-page.css',
  templateUrl: './clerk-page.html',
})
export class ClerkPage {
  private router = inject(Router);

  toUseCase() {
    this.router.navigate(['/clerk/usecase']);
  }

  toReport() {
    this.router.navigate(['/clerk/report']);
  }
}
