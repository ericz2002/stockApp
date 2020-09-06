import { Injectable } from '@angular/core';
import { Router } from '@angular/router';
import { HttpClient } from '@angular/common/http';
import { BehaviorSubject, Observable } from 'rxjs';
import { map } from 'rxjs/operators';

import { environment } from '@environments/environment';
import { User, Group, StockQuote, APIResult } from '@app/_models';
import { GroupAssets, UserAssets, UserListAssets } from '../_models/user';

@Injectable({ providedIn: 'root' })
export class AccountService {
    private userSubject: BehaviorSubject<User>;
    public user: Observable<User>;
    public groupinfo;

    constructor(
        private router: Router,
        private http: HttpClient
    ) {
        this.userSubject = new BehaviorSubject<User>(JSON.parse(localStorage.getItem('user')));
        this.user = this.userSubject.asObservable();
    }

    public get userValue(): User {
        return this.userSubject.value;
    }

    login(username, password) {
        const formData = new FormData();
        formData.append('grant_type', 'password');
        formData.append('username', username);
        formData.append('password', password);
        return this.http.post<User>(`${environment.apiUrl}/token`, formData)
            .pipe(map(user => {
                // store user details and jwt token in local storage to keep user logged in between page refreshes
                localStorage.setItem('user', JSON.stringify(user));
                this.userSubject.next(user);
                return user;
            }));
    }

    logout() {
        // remove user from local storage and set current user to null
        localStorage.removeItem('user');
        this.userSubject.next(null);
        this.router.navigate(['/account/login']);
    }

    register(is_admin: boolean, user: User) {
        if (is_admin) {
            return this.http.post(`${environment.apiUrl}/admin/register`, user);
        } else {
            return this.http.post(`${environment.apiUrl}/users/register`, user);
        }
    }

    addUser(user: User, group: string) {
        user.groupname = group;
        return this.http.post<APIResult>(`${environment.apiUrl}/admin/add_user`, user)
            .pipe(map(x => {
                if (x.result !== 'ok') {
                    throw new Error(x.reason);
                } else {
                    return x;
                }
            }));
    }

    fillUserCash(username: string, amount: number) {
        return this.http.post<APIResult>(`${environment.apiUrl}/admin/fill_user_cash`,
            { username, amount })
            .pipe(map(x => {
                if (x.result !== 'ok') {
                    throw new Error(x.reason);
                } else {
                    return x;
                }
            }));
    }

    fillGroupCash(groupname: string, amount: number) {
        return this.http.post<APIResult>(`${environment.apiUrl}/admin/fill_group_cash`,
            { groupname, amount })
            .pipe(map(x => {
                if (x.result !== 'ok') {
                    throw new Error(x.reason);
                } else {
                    return x;
                }
            }));
    }

    addGroup(group) {
        return this.http.post<APIResult>(`${environment.apiUrl}/admin/add_group`, group)
            .pipe(map(x => {
                if (x.result !== 'ok') {
                    throw new Error(x.reason);
                } else {
                    return x;
                }
            }));
    }

    getUsers(name: string) {
        return this.http.post<{ users: User[] }>(`${environment.apiUrl}/admin/list_users`, { groupname: name });
    }

    getGroups() {
        return this.http.get<{ groups: Group[] }>(`${environment.apiUrl}/groups`);
    }

    deleteGroup(name: string) {
        return this.http.post<APIResult>(`${environment.apiUrl}/admin/delete_users_by_group`,
            { groupname: name })
            .pipe(map(x => {
                if (x.result !== 'ok') {
                    throw new Error(x.reason);
                } else {
                    return x;
                }
            }));
    }

    getGroupById(groupname: string) {
        return this.http.get<Group>(`${environment.apiUrl}/admin/group_by_groupname`,
            {
                params: { groupname }
            });
    }

    getById(username: string) {
        return this.http.get<User>(`${environment.apiUrl}/admin/user_by_username`,
            {
                params: { username }
            });
    }

    listGroupAssets(groupname: string) {
        return this.http.post<GroupAssets>(`${environment.apiUrl}/admin/list_group_assets`,
            { groupname }
        );
    }

    listUserAssets(username: string) {
        return this.http.get<UserAssets>(`${environment.apiUrl}/admin/list_user_assets`,
            {
                params: { username }
            });
    }

    userListAssets() {
        return this.http.get<UserListAssets>(`${environment.apiUrl}/users/assets`);
    }

    buyStock(params) {
        return this.http.post<APIResult>(`${environment.apiUrl}/stock/buy`, params)
            .pipe(map(x => {
                if (x.result !== 'ok') {
                    throw new Error(x.reason);
                } else {
                    return x;
                }
            }));
    }

    sellStock(params) {
        return this.http.post<APIResult>(`${environment.apiUrl}/stock/sell`, params)
            .pipe(map(x => {
                if (x.result !== 'ok') {
                    throw new Error(x.reason);
                } else {
                    return x;
                }
            }));
    }

    getStockQuote(symbol: string) {
        return this.http.get<StockQuote>(`${environment.apiUrl}/stock/quote`,
            { params: { symbol } })
            .pipe(map(x => {
                if (x.result !== 'ok') {
                    throw new Error(`Failed to quote stock price for ${symbol}`);
                } else {
                    return x;
                }
            }));
    }

    update(username, params) {
        return this.http.post(`${environment.apiUrl}/admin/update_user`, params)
            .pipe(map(x => {
                // update stored user if the logged in user updated their own record
                if (username === this.userValue.username) {
                    // update local storage
                    const user = { ...this.userValue, ...params };
                    localStorage.setItem('user', JSON.stringify(user));

                    // publish updated user to subscribers
                    this.userSubject.next(user);
                }
                return x;
            }));
    }

    userUpdate(params) {
        return this.http.post(`${environment.apiUrl}/users/update`, params)
            .pipe(map(x => {
                const user = { ...this.userValue, ...params };
                localStorage.setItem('user', JSON.stringify(user));
                this.userSubject.next(user);
                return x;
            }));
    }

    updateGroup(groupname, params) {
        params.groupname = groupname;
        return this.http.post<APIResult>(`${environment.apiUrl}/admin/update_group`, params)
            .pipe(map(x => {
                if (x.result !== 'ok') {
                    throw new Error(x.reason);
                } else {
                    return x;
                }
            }));
    }

    delete(username: string) {
        return this.http.post(`${environment.apiUrl}/admin/delete_users`, { usernames: [username] })
            .pipe(map(x => {
                // auto logout if the logged in user deleted their own record
                if (username === this.userValue.username) {
                    this.logout();
                }
                return x;
            }));
    }
}
