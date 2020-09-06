import { Component, OnInit } from '@angular/core';
import { Router, ActivatedRoute } from '@angular/router';
import { FormBuilder, FormGroup, Validators } from '@angular/forms';
import { first } from 'rxjs/operators';

import { AccountService, AlertService } from '@app/_services';

@Component({ templateUrl: 'fund-group.component.html' })
export class FundGroupComponent implements OnInit {
    form: FormGroup;
    loading = false;
    submitted = false;
    id: string;

    constructor(
        private formBuilder: FormBuilder,
        private route: ActivatedRoute,
        private router: Router,
        private accountService: AccountService,
        private alertService: AlertService
    ) { }

    ngOnInit() {
        this.id = this.route.snapshot.params.id;
        console.log(`fund group ${this.id}`);

        this.form = this.formBuilder.group({
            amount: ['', [Validators.required, Validators.min(0)]]
        });

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

        if (this.accountService.userValue.is_admin) {
            this.fundGroup();
        } else {
            this.alertService.error('User has no permission', { keepAfterRouteChange: true });
            this.router.navigate(['']);
        }

        this.loading = true;

    }

    private fundGroup() {
        this.accountService.fillGroupCash(this.id, this.form.value.amount)
            .pipe(first())
            .subscribe(
                data => {
                    this.alertService.success('Group fund added successfully', { keepAfterRouteChange: true });
                    this.router.navigate(['.', { relativeTo: this.route }]);
                },
                error => {
                    this.alertService.error(error);
                    this.loading = false;
                });
    }

}
