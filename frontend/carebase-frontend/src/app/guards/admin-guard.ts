import { inject } from '@angular/core';
import { CanActivateFn, Router } from '@angular/router';
import { UserService } from '../services/user-service';

export const adminGuard: CanActivateFn = (route, state) => {
  const currentUser = inject(UserService).getCurrentUser();
  const router = inject(Router);
  if (currentUser() !== 'admin') return router.createUrlTree(['/']);
  return true;
};
