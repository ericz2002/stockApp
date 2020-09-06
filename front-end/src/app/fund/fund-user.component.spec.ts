import { async, ComponentFixture, TestBed } from '@angular/core/testing';

import { FundUserComponent } from './fund-user.component';

describe('FundUserComponent', () => {
  let component: FundUserComponent;
  let fixture: ComponentFixture<FundUserComponent>;

  beforeEach(async(() => {
    TestBed.configureTestingModule({
      declarations: [ FundUserComponent ]
    })
    .compileComponents();
  }));

  beforeEach(() => {
    fixture = TestBed.createComponent(FundUserComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
