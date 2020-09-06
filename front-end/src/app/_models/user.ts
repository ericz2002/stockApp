export class User {
    username: string;
    firstname: string;
    lastname: string;
    groupname: string;
    access_token: string;
    token_type: string;
    is_admin: boolean;
}

export class Group {
    groupname: string;
    description: string;
}

export class Asset {
    type: string;
    value: number;
    symbol: string;
}

export class UserListAssets {
    assets: Array<Asset>;
}

export class UserAssets {
    user: User;
    assets: Array<Asset>;
    total: number;
}

export class GroupAssets {
    assets: Array<UserAssets>;
}
