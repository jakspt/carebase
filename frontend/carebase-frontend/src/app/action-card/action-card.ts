import { Component, input, output } from '@angular/core';
import { MatCardModule } from '@angular/material/card';
import { MatButtonModule } from '@angular/material/button';
import { MatIconModule } from '@angular/material/icon';

@Component({
  imports: [MatCardModule, MatButtonModule, MatIconModule],
  selector: 'app-action-card',
  styleUrl: './action-card.css',
  templateUrl: './action-card.html',
})
export class ActionCard {
  title = input<string>('');
  description = input<string>('');

  icon = input<string>('face');
  iconColor = input<string>('inherit');
  actionText = input<string>('');
  buttonColor = input<'primary' | 'accent' | 'warn'>('primary');

  actionClicked = output<void>();

  // The Central "Card" Module. Requires Title, Description an Icon and a Button. Can also take and place content
  // Used nearly everywhere in this application
  // Something like: Header -> contains Title
  // Content -> contains Content (if it exists)
  // and also the other children (optional)
  // then the bottom contains the action button
}
