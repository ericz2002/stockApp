import { async, ComponentFixture, TestBed } from '@angular/core/testing';

import { FundGroupComponent } from './fund-group.component';

describe('FundGroupComponent', () => {
  let component: FundGroupComponent;
  let fixture: ComponentFixture<FundGroupComponent>;

  beforeEach(async(() => {
    TestBed.configureTestingModule({
      declarations: [ FundGroupComponent ]
    })
    .compileComponents();
  }));

  beforeEach(() => {
    fixture = TestBed.createComponent(FundGroupComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
