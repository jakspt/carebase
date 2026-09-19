import { ComponentFixture, TestBed } from '@angular/core/testing';
import { DoctorPage } from './doctor-page';

describe('DoctorPage', () => {
  let component: DoctorPage;
  let fixture: ComponentFixture<DoctorPage>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [DoctorPage],
    }).compileComponents();

    fixture = TestBed.createComponent(DoctorPage);
    component = fixture.componentInstance;
    await fixture.whenStable();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
