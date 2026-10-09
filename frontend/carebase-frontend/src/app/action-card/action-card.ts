import { Component, input, output } from '@angular/core';
import { MatCardModule } from '@angular/material/card';
import { MatButtonModule } from '@angular/material/button';
import { MatIconModule } from '@angular/material/icon';

export type ThemePalette = 'primary' | 'secondary' | 'tertiary' | 'error' | 'neutral';

@Component({
  imports: [MatCardModule, MatButtonModule, MatIconModule],
  selector: 'app-action-card',
  styleUrl: './action-card.css',
  templateUrl: './action-card.html',
  host: {
    '(click)': 'onCardClick($event)',
  },
})
export class ActionCard {
  title = input.required<string>();
  description = input<string>('');

  icon = input<string>('face');
  iconColor = input<ThemePalette>('primary');
  actionText = input<string>('');
  buttonText = input.required<string>();

  actionClicked = output<void>();

  protected onCardClick(event: MouseEvent) {
    const target = event.target as HTMLElement | null;
    if (target?.closest('button, a, input, select, textarea, [role="button"]')) {
      return;
    }
    this.actionClicked.emit();
  }

  protected onButtonClick(event?: MouseEvent) {
    event?.stopPropagation();
    this.actionClicked.emit();
  }
}
