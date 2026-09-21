import { CanActivateFn, Router } from '@angular/router';
import { UserService } from '../services/user-service';
import { inject } from '@angular/core';

export const doctorGuard: CanActivateFn = (route, state) => {
  const currentUser = inject(UserService).getCurrentUser();
  const router = inject(Router);
  if (currentUser() !== 'doctor') return router.createUrlTree(['/']);
  return true;
};
