import { Routes } from '@angular/router';
import { LandingPage } from './landing-page/landing-page';
import { HeaderLayout } from './header-layout/header-layout';
import { AdminPage } from './admin-page/admin-page';
import { DoctorPage } from './doctor-page/doctor-page';
import { DoctorUseCase } from './doctor-use-case/doctor-use-case';
import { homeRedirectGuardGuard } from './guards/home-redirect-guard-guard';
import { doctorGuard } from './guards/doctor-guard';
import { adminGuard } from './guards/admin-guard';

export const routes: Routes = [
  { path: '', component: LandingPage, canActivate: [homeRedirectGuardGuard] },
  {
    path: '',
    component: HeaderLayout,
    children: [
      { path: 'admin', component: AdminPage, canActivate: [adminGuard] },
      {
        path: 'doctor',
        component: DoctorPage,
        canActivate: [doctorGuard],
        canActivateChild: [doctorGuard],
        children: [
          { path: 'usecase', component: DoctorUseCase },
          { path: 'report', component: DoctorUseCase },
        ],
      },
    ],
  },
];
