import { Routes } from '@angular/router';
import { LandingPage } from './landing-page/landing-page';
import { HeaderLayout } from './header-layout/header-layout';
import { homeRedirectGuardGuard } from './guards/home-redirect-guard-guard';
import { doctorGuard } from './guards/doctor-guard';
import { adminGuard } from './guards/admin-guard';

export const routes: Routes = [
  { path: '', component: LandingPage, canActivate: [homeRedirectGuardGuard] },
  {
    path: '',
    component: HeaderLayout,
    children: [
      {
        path: 'admin',
        loadComponent: () => import('./admin-page/admin-page').then((m) => m.AdminPage),
        canActivate: [adminGuard],
      },
      {
        path: 'doctor',
        canActivateChild: [doctorGuard],
        children: [
          {
            path: '',
            loadComponent: () => import('./doctor-page/doctor-page').then((m) => m.DoctorPage),
          },
          {
            path: 'usecase',
            loadComponent: () =>
              import('./doctor-use-case/doctor-use-case').then((m) => m.DoctorUseCase),
          },
          {
            path: 'report',
            loadComponent: () =>
              import('./doctor-report/doctor-report').then((m) => m.DoctorReport),
          },
        ],
      },
    ],
  },
];
