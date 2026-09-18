import { Component, signal } from '@angular/core';
import { RouterOutlet } from '@angular/router';
import { ActionCard } from './action-card/action-card';

@Component({
  selector: 'app-root',
  imports: [RouterOutlet, ActionCard],
  templateUrl: './app.html',
  styleUrl: './app.css',
})
export class App {
  protected readonly title = signal('carebase-frontend');
}
