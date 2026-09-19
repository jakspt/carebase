import { Component } from '@angular/core';
import { RouterOutlet } from '@angular/router';
import { MatToolbarModule } from '@angular/material/toolbar';
import { MatIconModule } from '@angular/material/icon';

@Component({
  imports: [RouterOutlet, MatToolbarModule, MatIconModule],
  selector: 'app-header-layout',
  styleUrl: './header-layout.css',
  templateUrl: './header-layout.html',
})
export class HeaderLayout {}
