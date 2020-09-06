import { NgModule } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { ReactiveFormsModule } from '@angular/forms';
import { FundGroupComponent } from './fund-group.component';
import { FundUserComponent } from './fund-user.component';
import { LayoutComponent } from './layout.component';
import { ListComponent } from './list.component';
import { FundRoutingModule } from './fund-routing.module';

@NgModule({
  declarations: [
    FundGroupComponent,
    FundUserComponent,
    LayoutComponent,
    ListComponent
  ],
  imports: [
    CommonModule,
    FormsModule,
    ReactiveFormsModule,
    FundRoutingModule
  ]
})
export class FundModule { }
