import { ComponentFixture, TestBed } from '@angular/core/testing';
import { provideHttpClient } from '@angular/common/http';
import { provideAnimationsAsync } from '@angular/platform-browser/animations/async';
import { DoctorUseCase } from './doctor-use-case';

describe('DoctorUseCase', () => {
  let component: DoctorUseCase;
  let fixture: ComponentFixture<DoctorUseCase>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [DoctorUseCase],
      providers: [provideHttpClient(), provideAnimationsAsync()],
    }).compileComponents();

    fixture = TestBed.createComponent(DoctorUseCase);
    component = fixture.componentInstance;
    await fixture.whenStable();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
