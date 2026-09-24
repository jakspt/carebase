import { TestBed } from '@angular/core/testing';
import { SeedingService } from './seeding-service';

describe('SeedingService', () => {
  let service: SeedingService;

  beforeEach(() => {
    TestBed.configureTestingModule({});
    service = TestBed.inject(SeedingService);
  });

  it('should be created', () => {
    expect(service).toBeTruthy();
  });
});
