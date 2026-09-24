import { Component, inject } from '@angular/core';
import { ActionCard } from '../action-card/action-card';
import { Router } from '@angular/router';
import { MatIconModule } from '@angular/material/icon';
import { UserService } from '../services/user-service';
import { MatCardModule } from '@angular/material/card';

@Component({
  imports: [ActionCard, MatIconModule, MatCardModule],
  selector: 'app-landing-page',
  styleUrl: './landing-page.css',
  templateUrl: './landing-page.html',
})
export class LandingPage {
  private router = inject(Router);
  private userService = inject(UserService);

  visitDoctorSite() {
    this.userService.setUser('doctor');
    this.router.navigate(['doctor']);
  }

  visitAdminSite() {
    this.userService.setUser('admin');
    this.router.navigate(['admin']);
  }
}
