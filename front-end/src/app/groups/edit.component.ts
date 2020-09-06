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

    constructor(
        private formBuilder: FormBuilder,
        private route: ActivatedRoute,
        private router: Router,
        private accountService: AccountService,
        private alertService: AlertService
    ) { }

    ngOnInit() {
        this.id = this.route.snapshot.params.id;
        console.log(`editing group ${this.id}`);

        this.form = this.formBuilder.group({
            description: ['', Validators.required]
        });

        if (this.accountService.userValue.is_admin) {
            this.accountService.getGroupById(this.id)
                .pipe(first())
                .subscribe(x => {
                    this.f.groupname.setValue(x.groupname);
                    this.f.description.setValue(x.description);
                });
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
            this.updateGroup();
        } else {
            this.alertService.error('User has no permission', { keepAfterRouteChange: true });
            this.router.navigate(['.', { relativeTo: this.route }]);
        }

    }

    private updateGroup() {
        this.accountService.updateGroup(this.id, this.form.value)
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

}
