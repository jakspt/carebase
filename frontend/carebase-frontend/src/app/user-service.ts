import { Service, signal } from '@angular/core';

export type User = 'doctor' | 'admin' | undefined;

@Service()
export class UserService {
  private currentUser = signal<User>(undefined);

  public setUser(user: User) {
    this.currentUser.set(user);
  }
  public logout() {
    this.setUser(undefined);
  }
  public getCurrentUser() {
    return this.currentUser.asReadonly();
  }
}
