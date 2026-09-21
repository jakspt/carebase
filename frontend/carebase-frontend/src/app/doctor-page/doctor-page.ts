import { Component } from '@angular/core';
import { ActionCard } from '../action-card/action-card';

@Component({
  imports: [ActionCard],
  selector: 'app-doctor-page',
  styleUrl: './doctor-page.css',
  templateUrl: './doctor-page.html',
})
export class DoctorPage {}
