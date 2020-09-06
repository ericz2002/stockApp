import { Component, OnInit } from '@angular/core';
import { Router, ActivatedRoute } from '@angular/router';
import { FormBuilder, FormGroup, Validators } from '@angular/forms';
import { first } from 'rxjs/operators';

import { AccountService, AlertService } from '@app/_services';

@Component({ templateUrl: 'edit.component.html' })
export class EditComponent implements OnInit {
    form: FormGroup;
    id: string;
    loading = false;
    submitted = false;
    ugroups = null;

    constructor(
        private formBuilder: FormBuilder,
        private route: ActivatedRoute,
        private router: Router,
        private accountService: AccountService,
        private alertService: AlertService
    ) { }

    ngOnInit() {
        this.id = this.route.snapshot.params.id;
        console.log(`editing user ${this.id}`);

        this.accountService.getGroups()
        .pipe(first())
        .subscribe(groups => { this.ugroups = groups.groups; });

        // password not required in edit mode
        const passwordValidators = [Validators.minLength(6)];

        this.form = this.formBuilder.group({
            firstname: ['', Validators.required],
            lastname: ['', Validators.required],
            groupname: ['', Validators.required],
            password: ['', passwordValidators]
        });

        if (this.accountService.userValue.is_admin) {
            this.accountService.getById(this.id)
                .pipe(first())
                .subscribe(x => {
                    this.f.firstname.setValue(x.firstname);
                    this.f.lastname.setValue(x.lastname);
                    this.f.groupname.setValue(x.groupname);
                });
        } else {
            this.f.firstname.setValue(this.accountService.userValue.firstname);
            this.f.lastname.setValue(this.accountService.userValue.lastname);
            this.f.groupname.setValue(this.accountService.userValue.groupname);
        }
    }

    // convenience getter for easy access to form fields
    get f() { return this.form.controls; }

    get is_admin() { return this.accountService.userValue.is_admin; }

    onSubmit() {
        this.submitted = true;

        // reset alerts on submit
        this.alertService.clear();

        // stop here if form is invalid
        if (this.form.invalid) {
            return;
        }

        this.loading = true;

        if (this.accountService.userValue.username !== this.id) {
            this.updateUser();
        } else {
            this.userUpdateInfo();
        }
    }

    private updateUser() {
        this.form.value.username = this.id;
        this.accountService.update(this.id, this.form.value)
            .pipe(first())
            .subscribe(
                data => {
                    this.alertService.success('Update successful', { keepAfterRouteChange: true });
                    this.router.navigate(['..', { relativeTo: this.route }]);
                },
                error => {
                    this.alertService.error(error);
                    this.loading = false;
                });
    }

    private userUpdateInfo() {
        this.form.value.username = this.id;
        this.accountService.userUpdate(this.form.value)
            .pipe(first())
            .subscribe(
                data => {
                    this.alertService.success('Update successful', { keepAfterRouteChange: true });
                    this.router.navigate(['']);
                },
                error => {
                    this.alertService.error(error);
                    this.loading = false;
                });
    }
}
