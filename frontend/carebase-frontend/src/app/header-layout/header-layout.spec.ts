import { ComponentFixture, TestBed } from '@angular/core/testing';
import { provideHttpClient } from '@angular/common/http';
import { provideRouter } from '@angular/router';
import { HeaderLayout } from './header-layout';

describe('HeaderLayout', () => {
  let component: HeaderLayout;
  let fixture: ComponentFixture<HeaderLayout>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [HeaderLayout],
      providers: [provideHttpClient(), provideRouter([])],
    }).compileComponents();

    fixture = TestBed.createComponent(HeaderLayout);
    component = fixture.componentInstance;
    await fixture.whenStable();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
