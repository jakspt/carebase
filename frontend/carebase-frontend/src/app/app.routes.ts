import { Routes } from '@angular/router';
import { ActionCard } from './action-card/action-card';
import { LandingPage } from './landing-page/landing-page';
import { MinimalLayout } from './minimal-layout/minimal-layout';
import { HeaderLayout } from './header-layout/header-layout';
import { AdminPage } from './admin-page/admin-page';
import { DoctorPage } from './doctor-page/doctor-page';
import { DoctorUseCase } from './doctor-use-case/doctor-use-case';
import { homeRedirectGuardGuard } from './guards/home-redirect-guard-guard';

export const routes: Routes = [
  { path: '', component: LandingPage, canActivate: [homeRedirectGuardGuard] },
  {
    path: '',
    component: HeaderLayout,
    children: [
      { path: 'admin', component: AdminPage },
      {
        path: 'doctor',
        component: DoctorPage,
        children: [
          { path: 'usecase', component: DoctorUseCase },
          { path: 'report', component: DoctorUseCase },
        ],
      },
    ],
  },
];
