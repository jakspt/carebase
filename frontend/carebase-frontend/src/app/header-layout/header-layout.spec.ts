import { ComponentFixture, TestBed } from '@angular/core/testing';
import { HeaderLayout } from './header-layout';

describe('HeaderLayout', () => {
  let component: HeaderLayout;
  let fixture: ComponentFixture<HeaderLayout>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [HeaderLayout],
    }).compileComponents();

    fixture = TestBed.createComponent(HeaderLayout);
    component = fixture.componentInstance;
    await fixture.whenStable();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
