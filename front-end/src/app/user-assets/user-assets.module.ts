import { NgModule } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { ReactiveFormsModule } from '@angular/forms';

import { LayoutComponent } from './layout.component';
import { ListComponent } from './list.component';
import { UserAssetsRoutingModule } from './user-assets-routing.module';
import { BuySellComponent } from './buy-sell.component';

@NgModule({
  declarations: [
    LayoutComponent,
    ListComponent,
    BuySellComponent
  ],
  imports: [
    CommonModule,
    FormsModule,
    ReactiveFormsModule,
    UserAssetsRoutingModule
  ]
})
export class UserAssetsModule { }
