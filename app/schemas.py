from pydantic import BaseModel
from typing import Optional, List
from enum import Enum, IntEnum



class Token(BaseModel):
    access_token: str
    token_type: str
    username: str
    firstname: str
    lastname: str
    is_admin: bool


class TokenData(BaseModel):
    username: Optional[str] = None


class Group(BaseModel):
    groupname: str
    description: Optional[str] = ""


class GroupDBInfo(Group):
    id: int
    class Config:
        orm_mode = True


class GroupList(BaseModel):
    groups: List[Group] = []


class UserInfoBase(BaseModel):
    username: str
    firstname: str
    lastname: str
    groupname: Optional[str] = "default"
    is_admin: Optional[bool] = False


class UserCreate(UserInfoBase):
    password: str
    cash: Optional[float] = 0.0


class UsersCreate(BaseModel):
    users: List[UserCreate] = []


class UserInfo(UserInfoBase):
    id: int

    class Config:
        orm_mode = True


class UserList(BaseModel):
    users: List[UserInfoBase] = []


class DeleteUsers(BaseModel):
    usernames: List[str] = []


class CashInfoBase(BaseModel):
    amount: float 
    userID: int


class CashInfo(CashInfoBase):
    id: int

    class Config:
        orm_mode = True


class StockInfoBase(BaseModel):
    symbol: str
    amount: int
    cost: float
    userID: int
 

class StockInfo(StockInfoBase):
    id: int

    class Config:
        orm_mode = True


class StockBuyInfo(BaseModel):
    symbol: str
    amount: int


class StockSellInfo(BaseModel):
    symbol: str
    amount: int


class ResultEnum(str, Enum):
    passed = 'ok'
    failed = 'failed'


class OpResult(BaseModel):
    result: ResultEnum
    reason: Optional[str] = None

class StockQuote(BaseModel):
    result: ResultEnum
    price: Optional[float] = None

class AssetTypeEnum(str, Enum):
    cash = 'cash'
    stock = 'stock'


class Asset(BaseModel):
    type: AssetTypeEnum
    value: float
    symbol: str


class TotalAssets(BaseModel):
    assets: List[Asset] = []


class UserAsset(BaseModel):
    user: UserInfoBase
    assets: List[Asset] = []
    total: float


class UserAssetList(BaseModel):
    assets: List[UserAsset] = []


class FillUserCash(BaseModel):
    username: str
    amount: float

class FillGroupCash(BaseModel):
    groupname: str
    amount: float
