import { Component, OnInit } from '@angular/core';
import { Router, ActivatedRoute } from '@angular/router';
import { FormBuilder, FormGroup, Validators } from '@angular/forms';
import { first } from 'rxjs/operators';

import { AccountService, AlertService } from '@app/_services';

@Component({ templateUrl: 'buy-sell.component.html' })
export class BuySellComponent implements OnInit {
    form: FormGroup;
    id: string;
    loading = false;
    submitted = false;
    selling = false;

    constructor(
        private formBuilder: FormBuilder,
        private route: ActivatedRoute,
        private router: Router,
        private accountService: AccountService,
        private alertService: AlertService
    ) { }

    ngOnInit() {
        if (this.router.url.includes('addstock')) {
            this.id = null;
            this.selling = false;
            console.log(`adding stock`);
        } else {
            this.id = this.route.snapshot.params.id;
            if (this.router.url.includes('sell')) {
                this.selling = true;
                console.log(`selling stock ${this.id}`);
            } else {
                this.selling = false;
                console.log(`buy stock ${this.id}`);
            }
        }

        this.form = this.formBuilder.group({
            symbol: ['', Validators.required],
            amount: ['', Validators.required]
        });

        this.f.symbol.setValue(this.id);
        this.f.amount.setValue(null);
    }

    // convenience getter for easy access to form fields
    get f() { return this.form.controls; }

    onSubmit() {
        this.submitted = true;

        // reset alerts on submit
        this.alertService.clear();

        // stop here if form is invalid
        if (this.form.invalid) {
            return;
        }

        this.loading = true;
        if (this.selling) {
            this.sell();
        } else {
            this.buy();
        }
    }

    private buy() {
        this.accountService.buyStock(this.form.value)
            .pipe(first())
            .subscribe(
                data => {
                    console.log(data);
                    this.alertService.success('Buy successful', { keepAfterRouteChange: true });
                    this.router.navigate(['.', { relativeTo: this.route }]);
                },
                error => {
                    this.alertService.error(error);
                    this.loading = false;
                });
    }

    private sell() {
        this.accountService.sellStock(this.form.value)
            .pipe(first())
            .subscribe(
                data => {
                    console.log(data);
                    this.alertService.success('Sell successful', { keepAfterRouteChange: true });
                    this.router.navigate(['.', { relativeTo: this.route }]);
                },
                error => {
                    this.alertService.error(error);
                    this.loading = false;
                });
    }
}
