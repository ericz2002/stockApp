import { Component, OnInit } from '@angular/core';
import { Router, ActivatedRoute } from '@angular/router';
import { FormBuilder, FormGroup, Validators } from '@angular/forms';
import { first } from 'rxjs/operators';

import { AccountService, AlertService } from '@app/_services';

@Component({ templateUrl: 'add.component.html' })
export class AddComponent implements OnInit {
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
        console.log(`adding user to group ${this.id}`);

        // password not required in edit mode
        const passwordValidators = [Validators.minLength(6)];
        passwordValidators.push(Validators.required);

        this.form = this.formBuilder.group({
            firstname: ['', Validators.required],
            lastname: ['', Validators.required],
            username: ['', Validators.required],
            password: ['', passwordValidators]
        });

        this.f.firstname.setValue(null);
        this.f.lastname.setValue(null);
        this.f.groupname.setValue(null);
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
            this.createUser();
        } else {
            this.alertService.error('User has no permission to add new user', { keepAfterRouteChange: true });
            this.router.navigate(['']);
        }
    }

    private createUser() {
        this.accountService.addUser(this.form.value, this.id)
            .pipe(first())
            .subscribe(
                data => {
                    this.alertService.success('User added successfully', { keepAfterRouteChange: true });
                    this.router.navigate(['.', { relativeTo: this.route }]);
                },
                error => {
                    this.alertService.error(error);
                    this.loading = false;
                });
    }

}
