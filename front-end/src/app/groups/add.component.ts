import { Component, OnInit } from '@angular/core';
import { Router, ActivatedRoute } from '@angular/router';
import { FormBuilder, FormGroup, Validators } from '@angular/forms';
import { first } from 'rxjs/operators';

import { AccountService, AlertService } from '@app/_services';

@Component({ templateUrl: 'add.component.html' })
export class AddComponent implements OnInit {
    form: FormGroup;
    loading = false;
    submitted = false;

    constructor(
        private formBuilder: FormBuilder,
        private route: ActivatedRoute,
        private router: Router,
        private accountService: AccountService,
        private alertService: AlertService
    ) { }

    ngOnInit() {
        console.log(`adding group`);

        this.form = this.formBuilder.group({
            groupname: ['', Validators.required],
            description: ['', Validators.required]
        });

        if (this.accountService.userValue.is_admin) {
            this.f.groupname.setValue(null);
            this.f.description.setValue(null);
        }
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
        if (this.accountService.userValue.is_admin) {
            this.createGroup();
        } else {
            this.alertService.error('User has no permission', { keepAfterRouteChange: true });
            this.router.navigate(['.', { relativeTo: this.route }]);
        }

    }

    private createGroup() {
        this.accountService.addGroup(this.form.value)
            .pipe(first())
            .subscribe(
                data => {
                    this.alertService.success('Group added successfully', { keepAfterRouteChange: true });
                    this.router.navigate(['.', { relativeTo: this.route }]);
                },
                error => {
                    this.alertService.error(error);
                    this.loading = false;
                });
    }

}
