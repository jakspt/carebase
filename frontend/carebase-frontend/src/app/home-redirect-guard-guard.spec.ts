import { TestBed } from '@angular/core/testing';
import { CanActivateFn } from '@angular/router';
import { homeRedirectGuardGuard } from './home-redirect-guard-guard';

describe('homeRedirectGuardGuard', () => {
  const executeGuard: CanActivateFn = (...guardParameters) =>
    TestBed.runInInjectionContext(() => homeRedirectGuardGuard(...guardParameters));

  beforeEach(() => {
    TestBed.configureTestingModule({});
  });

  it('should be created', () => {
    expect(executeGuard).toBeTruthy();
  });
});
