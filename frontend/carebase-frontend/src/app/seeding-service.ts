import { Service } from '@angular/core';
import { Observable, of, timer } from 'rxjs';

@Service()
export class SeedingService {
  public seedData(): Observable<number> {
    return timer(5000); // completes after 5 seconds
  }
}
