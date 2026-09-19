import { ComponentFixture, TestBed } from '@angular/core/testing';
import { DoctorUseCase } from './doctor-use-case';

describe('DoctorUseCase', () => {
  let component: DoctorUseCase;
  let fixture: ComponentFixture<DoctorUseCase>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [DoctorUseCase],
    }).compileComponents();

    fixture = TestBed.createComponent(DoctorUseCase);
    component = fixture.componentInstance;
    await fixture.whenStable();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
