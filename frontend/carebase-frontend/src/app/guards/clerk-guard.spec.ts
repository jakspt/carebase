import { TestBed } from '@angular/core/testing';
import { Router, ActivatedRouteSnapshot, RouterStateSnapshot } from '@angular/router';
import { clerkGuard } from './clerk-guard';
import { UserService } from '../services/user-service';

describe('clerkGuard', () => {
  let userService: UserService;
  let router: Router;

  beforeEach(() => {
    TestBed.configureTestingModule({});
    userService = TestBed.inject(UserService);
    router = TestBed.inject(Router);
  });

  it('should allow access if current user is clerk', () => {
    userService.setUser('clerk');
    const result = TestBed.runInInjectionContext(() =>
      clerkGuard({} as ActivatedRouteSnapshot, {} as RouterStateSnapshot),
    );
    expect(result).toBe(true);
  });

  it('should redirect to root if current user is not clerk', () => {
    userService.setUser('doctor');
    const result = TestBed.runInInjectionContext(() =>
      clerkGuard({} as ActivatedRouteSnapshot, {} as RouterStateSnapshot),
    );
    expect(result).not.toBe(true);
  });
});
