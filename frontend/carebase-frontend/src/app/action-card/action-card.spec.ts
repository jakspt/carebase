import { ComponentFixture, TestBed } from '@angular/core/testing';
import { ActionCard } from './action-card';

describe('ActionCard', () => {
  let component: ActionCard;
  let fixture: ComponentFixture<ActionCard>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [ActionCard],
    }).compileComponents();

    fixture = TestBed.createComponent(ActionCard);
    fixture.componentRef.setInput('title', 'Test Action');
    fixture.componentRef.setInput('buttonText', 'Execute');
    component = fixture.componentInstance;
    await fixture.whenStable();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
