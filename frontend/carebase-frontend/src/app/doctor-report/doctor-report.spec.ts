import { ComponentFixture, TestBed } from '@angular/core/testing';
import { provideHttpClient } from '@angular/common/http';
import { provideAnimationsAsync } from '@angular/platform-browser/animations/async';
import { DoctorReport } from './doctor-report';

describe('DoctorReport', () => {
  let component: DoctorReport;
  let fixture: ComponentFixture<DoctorReport>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [DoctorReport],
      providers: [provideHttpClient(), provideAnimationsAsync()],
    }).compileComponents();

    fixture = TestBed.createComponent(DoctorReport);
    component = fixture.componentInstance;
    await fixture.whenStable();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
