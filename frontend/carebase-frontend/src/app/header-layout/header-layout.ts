import { Component, computed, inject } from '@angular/core';
import { RouterOutlet, RouterLinkWithHref, RouterLinkActive, Router } from '@angular/router';
import { MatToolbarModule } from '@angular/material/toolbar';
import { MatIconModule } from '@angular/material/icon';
import { MatMenuModule } from '@angular/material/menu';
import { MatDividerModule } from '@angular/material/divider';
import { MatAnchor } from '@angular/material/button';
import { User, UserService } from '../services/user-service';
import { TitleCasePipe, UpperCasePipe } from '@angular/common';
import { MatTooltipModule } from '@angular/material/tooltip';

@Component({
  imports: [
    RouterOutlet,
    MatToolbarModule,
    MatIconModule,
    MatMenuModule,
    MatDividerModule,
    MatTooltipModule,
    MatAnchor,
    TitleCasePipe,
    UpperCasePipe,
    RouterLinkWithHref,
  ],
  selector: 'app-header-layout',
  styleUrl: './header-layout.css',
  templateUrl: './header-layout.html',
})
export class HeaderLayout {
  private userService = inject(UserService);
  private router = inject(Router);
  currentUser = this.userService.getCurrentUser();

  switchRole(user: User) {
    this.userService.setUser(user);
    this.router.navigate(['/']);
  }
  logout() {
    this.switchRole(undefined);
  }
}
