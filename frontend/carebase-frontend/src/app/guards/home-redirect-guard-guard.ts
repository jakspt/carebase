import { inject } from '@angular/core';
import { CanActivateFn, Router } from '@angular/router';
import { UserService } from '../services/user-service';

export const homeRedirectGuardGuard: CanActivateFn = (route, state) => {
  const router = inject(Router);
  const currentUser = inject(UserService).getCurrentUser();

  switch (currentUser()) {
    case 'admin':
      return router.createUrlTree(['/admin']);
    case 'doctor':
      return router.createUrlTree(['/doctor']);
    default:
      break;
  }

  return true;
};
