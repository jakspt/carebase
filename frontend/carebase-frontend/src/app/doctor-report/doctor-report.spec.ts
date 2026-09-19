import { ComponentFixture, TestBed } from '@angular/core/testing';
import { DoctorReport } from './doctor-report';

describe('DoctorReport', () => {
  let component: DoctorReport;
  let fixture: ComponentFixture<DoctorReport>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [DoctorReport],
    }).compileComponents();

    fixture = TestBed.createComponent(DoctorReport);
    component = fixture.componentInstance;
    await fixture.whenStable();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
