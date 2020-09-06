import { Component, OnInit } from '@angular/core';
import { first } from 'rxjs/operators';

import { AccountService } from '@app/_services';


@Component({ templateUrl: 'list.component.html' })
export class ListComponent implements OnInit {

    ugroups = null;

    constructor(private accountService: AccountService) { }

    ngOnInit() {
        this.accountService.getGroups()
            .pipe(first())
            .subscribe(groups => { this.ugroups = groups.groups; });
    }

    deleteGroup(groupname: string) {
        const ugroup = this.ugroups.find(x => x.groupname === groupname);
        ugroup.isDeleting = true;
        this.accountService.deleteGroup(groupname)
            .pipe(first())
            .subscribe(() => {
                this.ugroups = this.ugroups.filter(x => x.groupname !== groupname);
            });
    }

}
