import { Component, inject } from '@angular/core';
import { ActionCard } from '../action-card/action-card';
import { MatIconModule } from '@angular/material/icon';
import { Router } from '@angular/router';

@Component({
  imports: [ActionCard, MatIconModule],
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
