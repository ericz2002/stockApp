import { NgModule } from '@angular/core';
import { Routes, RouterModule } from '@angular/router';

import { LayoutComponent } from './layout.component';
import { ListComponent } from './list.component';
import { BuySellComponent } from './buy-sell.component';

const routes: Routes = [
    {
        path: '', component: LayoutComponent,
        children: [
            { path: '', component: ListComponent },
            { path: 'addstock', component: BuySellComponent },
            { path: 'buy/:id', component: BuySellComponent },
            { path: 'sell/:id', component: BuySellComponent }
        ]
    }
];

@NgModule({
    imports: [RouterModule.forChild(routes)],
    exports: [RouterModule]
})
export class UserAssetsRoutingModule { }
