import { Component, OnInit } from '@angular/core';
import { first } from 'rxjs/operators';

import { AccountService } from '@app/_services';
import { User } from '../_models/user';


@Component({ templateUrl: 'list.component.html' })
export class ListComponent implements OnInit {

    users = null;
    public group = 'default';
    public groupList = null;

    constructor(private accountService: AccountService) { }

    ngOnInit() {
        this.accountService.getGroups()
            .pipe(first())
            .subscribe(groups => { this.groupList = groups.groups; });
        this.accountService.getUsers(this.group)
            .pipe(first())
            .subscribe(users => { this.users = users.users; });
    }

    deleteUser(username: string) {
        const user = this.users.find(x => x.username === username);
        user.isDeleting = true;
        this.accountService.delete(username)
            .pipe(first())
            .subscribe(() => {
                this.users = this.users.filter(x => x.username !== username);
            });
    }

    onGroupChange(newValue) {
        console.log(`change group to: ${newValue}`);
        this.group = newValue;
        this.accountService.getUsers(this.group)
            .pipe(first())
            .subscribe(users => { this.users = users.users; });
    }
}
