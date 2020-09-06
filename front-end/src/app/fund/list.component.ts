import { Component, OnInit } from '@angular/core';
import { first } from 'rxjs/operators';

import { AccountService } from '@app/_services';
import { UserAssets } from '../_models/user';


@Component({ templateUrl: 'list.component.html' })
export class ListComponent implements OnInit {

    public group = 'default';
    public groupList = null;
    public groupAssets: Array<UserAssets> = null;

    constructor(private accountService: AccountService) { }

    ngOnInit() {
        this.accountService.getGroups()
            .pipe(first())
            .subscribe(groups => { this.groupList = groups.groups; });
        this.accountService.listGroupAssets(this.group)
            .pipe(first())
            .subscribe(groupAssets => { this.groupAssets = groupAssets.assets; });
    }

    onGroupChange(newValue) {
        console.log(`change group to: ${newValue}`);
        this.group = newValue;
        this.accountService.listGroupAssets(this.group)
            .pipe(first())
            .subscribe(x => { this.groupAssets = x.assets; });
    }

    public getCash(index): number {
        const assets = this.groupAssets[index].assets;
        for (const asset of assets) {
            if (asset.type === 'cash') {
                return asset.value;
            }
        }
   }

}
