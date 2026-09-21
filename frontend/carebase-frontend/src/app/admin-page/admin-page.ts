import { Component } from '@angular/core';
import { ActionCard } from '../action-card/action-card';

@Component({
  imports: [ActionCard],
  selector: 'app-admin-page',
  styleUrl: './admin-page.css',
  templateUrl: './admin-page.html',
})
export class AdminPage {
  migrateDb() {
    throw new Error('Method not implemented.');
  }
  seedDb() {
    throw new Error('Method not implemented.');
  }
}
