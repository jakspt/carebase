import { Component } from '@angular/core';
import { RouterOutlet } from '@angular/router';
import { MatToolbarModule } from '@angular/material/toolbar';
import { MatIconModule } from '@angular/material/icon';
import { MatMenuModule } from '@angular/material/menu';
import { MatDividerModule } from '@angular/material/divider';
import { MatAnchor } from '@angular/material/button';

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
  switchRole(user: string) {
    // switching happens here
  }
  logout() {
    //logging out happens here
  }
}
