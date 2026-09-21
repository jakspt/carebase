import { Component, computed, inject } from '@angular/core';
import { RouterOutlet } from '@angular/router';
import { MatToolbarModule } from '@angular/material/toolbar';
import { MatIconModule } from '@angular/material/icon';
import { MatMenuModule } from '@angular/material/menu';
import { MatDividerModule } from '@angular/material/divider';
import { MatAnchor } from '@angular/material/button';
import { User, UserService } from '../services/user-service';

@Component({
  imports: [
    RouterOutlet,
    MatToolbarModule,
    MatIconModule,
    MatMenuModule,
    MatDividerModule,
    MatAnchor,
  ],
  selector: 'app-header-layout',
  styleUrl: './header-layout.css',
  templateUrl: './header-layout.html',
})
export class HeaderLayout {
  private userService = inject(UserService);
  userDisplay = computed(() => {
    let currentUser = this.userService.getCurrentUser()();
    if (currentUser === 'doctor') {
      return 'Doctor';
    } else if (currentUser === 'admin') {
      return 'Admin';
    } else {
      throw new Error('there should be a user defined by now, but there was not');
    }
  });

  switchRole(user: User) {
    this.userService.setUser(user);
  }
  logout() {
    this.userService.logout();
  }
}
