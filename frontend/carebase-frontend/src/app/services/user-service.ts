import { Service, signal } from '@angular/core';

export type User = 'doctor' | 'admin' | 'clerk' | undefined;

@Service()
export class UserService {
  private currentUser = signal<User>(undefined);

  public setUser(user: User) {
    this.currentUser.set(user);
  }

  public getCurrentUser() {
    return this.currentUser.asReadonly();
  }
}
