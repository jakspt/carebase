import { Component, inject } from '@angular/core';
import { ActionCard } from '../action-card/action-card';
import { Router } from '@angular/router';
import { MatIconModule } from '@angular/material/icon';

@Component({
  imports: [ActionCard, MatIconModule],
  selector: 'app-landing-page',
  styleUrl: './landing-page.css',
  templateUrl: './landing-page.html',
})
export class LandingPage {
  router = inject(Router);

  visitDoctorSite() {
    this.router.navigate(['doctor']);
  }
  visitAdminSite() {
    this.router.navigate(['admin']);
  }
}
