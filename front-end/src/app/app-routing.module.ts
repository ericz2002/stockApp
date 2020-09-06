import { NgModule } from '@angular/core';
import { Routes, RouterModule } from '@angular/router';

import { HomeComponent } from './home';
import { AuthGuard } from './_helpers';

const accountModule = () => import('./account/account.module').then(x => x.AccountModule);
const usersModule = () => import('./users/users.module').then(x => x.UsersModule);
const groupsModule = () => import('./groups/groups.module').then(x => x.GroupsModule);
const fundModule = () => import('./fund/fund.module').then( x => x.FundModule);
const userAssetsModule = () => import('./user-assets/user-assets.module').then(x => x.UserAssetsModule);
const routes: Routes = [
    { path: '', component: HomeComponent, canActivate: [AuthGuard] },
    { path: 'users', loadChildren: usersModule, canActivate: [AuthGuard] },
    { path: 'account', loadChildren: accountModule },
    { path: 'groups', loadChildren: groupsModule, canActivate: [AuthGuard] },
    { path: 'groupassets', loadChildren: fundModule, canActivate: [AuthGuard] },
    { path: 'userassets', loadChildren: userAssetsModule, canActivate: [AuthGuard]},
    // otherwise redirect to home
    { path: '**', redirectTo: '' }
];

@NgModule({
    imports: [RouterModule.forRoot(routes)],
    exports: [RouterModule]
})
export class AppRoutingModule { }
