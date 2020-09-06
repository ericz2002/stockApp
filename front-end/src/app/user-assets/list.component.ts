import { Component, OnInit } from '@angular/core';
import { first } from 'rxjs/operators';

import { AccountService } from '@app/_services';
import { UserListAssets, Asset } from '../_models/user';


@Component({ templateUrl: 'list.component.html' })
export class ListComponent implements OnInit {

    assets: Array<Asset>;
    sum = 0.0;

    constructor(private accountService: AccountService) { }

    ngOnInit() {
        this.accountService.userListAssets()
            .pipe(first())
            .subscribe(x => { this.assets = x.assets;
                              this.sum = 0.0;
                              this.assets.forEach(asset => {
                                this.sum += asset.value;
                              });
                              });
    }

}
