from typing import Optional, List
from sqlalchemy import * 
from database import *
from sqlalchemy.orm import Session, sessionmaker
from fastapi import Depends, FastAPI, HTTPException, status
import models, schemas
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from jose import JWTError, jwt
from datetime import datetime, timedelta
import hashlib
import finnhub
import uvicorn
import logging
from fastapi.middleware.cors import CORSMiddleware
import os

# database
SQLALCHEMY_DATABASE_URL = "mysql+mysqlconnector://{username}:{password}@localhost:3306/eclass"\
    .format(username=os.environ.get('mysql_username'), password=os.environ.get('mysql_password'))

engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

ugroups.create(engine, checkfirst=True)

users.create(engine, checkfirst=True)

cash.create(engine, checkfirst=True)

stocks.create(engine, checkfirst=True)

# jwt_key and finnhub_token are passed in by env vars
SECRET_KEY = os.environ.get('jwt_key')
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

configuration = finnhub.Configuration(
    api_key={
        'token': os.environ.get('finnhub_token')
    }
)
finnhub_client = finnhub.DefaultApi(finnhub.ApiClient(configuration))

models.Base.metadata.create_all(bind=engine)

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/token")


app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["GET", "POST"],
    allow_headers=["*"],
)


def get_db():
    db = None
    try:
        db = SessionLocal()
        yield db
    finally:
        db.close()


def verify_password(plain_password, hashed_password):
    return hashed_password == get_password_hash(plain_password)


def get_password_hash(password):
    return hashlib.sha1(str(password).encode('utf-8')).hexdigest()


def get_user_by_username(db: Session, username: str):
    return db.query(models.User).filter(models.User.username == username).first()


def get_admin(db: Session):
    return db.query(models.User).filter(models.User.is_admin).first()


def get_group_by_groupname(db: Session, groupname: str):
    return db.query(models.Group).filter(models.Group.groupname == groupname).first()


def create_default_group(db: Session):
    if get_group_by_groupname(db, groupname="default") is not None:
        logging.warning("group default exists")
        return None
    db_default_group = models.Group(groupname="default", description="default group")
    db.add(db_default_group)
    db.commit()
    db.refresh(db_default_group)
    return db_default_group


def create_group(db: Session, group: schemas.Group):
    if get_group_by_groupname(db, group.groupname) is not None:
        logging.warning("group %s exists" % group.groupname)
        return None
    db_group = models.Group(groupname=group.groupname, description=group.description)
    db.add(db_group)
    db.commit()
    db.refresh(db_group)
    return db_group


def delete_group_by_groupname(db: Session, groupname: str):
    if groupname == "default":
        logging.warning("group default can not be deleted")
        return
    if get_group_by_groupname(db, groupname) is None:
        logging.warning("group %s not exists" % groupname)
        return
    # move group memebers to default group
    db.query(models.User).filter(models.User.groupname == groupname).update({models.User.groupname:"default"})
    db.query(models.Group).filter(models.Group.groupname == groupname).delete()
    db.commit()


def create_user(db: Session, user: schemas.UserCreate):
    if get_user_by_username(db, user.username) is not None:
        logging.info("user %s exists" % user.username)
        return None
    if user.groupname is None:
        logging.info("groupname not specified, use default")
        user.groupname = "default"
    elif get_group_by_groupname(db, user.groupname) is None:
        logging.warning("group %s undefined, use default" % user.groupname)
        user.groupname = "default"
    hashed = get_password_hash(user.password)
    db_user = models.User(username=user.username, password=hashed, firstname=user.firstname, lastname=user.lastname,
                          groupname=user.groupname, is_admin=user.is_admin)
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user


def delete_user_by_username(db: Session, username: str):
    logging.info("username: %s" % username)
    db_user = get_user_by_username(db, username=username)
    if db_user is None:
        logging.warning("no db user: %s" % username)
        return
    db.query(models.Cash).filter(models.Cash.userID == db_user.id).delete()
    db.query(models.Stock).filter(models.Stock.userID == db_user.id).delete()
    db.query(models.User).filter(models.User.username == username).delete()
    db.commit()


def list_users_by_groupname(db: Session, groupname: str):
    pass


def authenticate_user(db: Session, username: str, password: str):
    db_user = get_user_by_username(db, username=username)
    if db_user is None:
        return False
    return verify_password(password, db_user.password)


def authenticate_admin(db: Session, username: str, password: str):
    admin = get_user_by_username(db, username=username)
    if admin is None:
        return False
    if not admin.is_admin:
        return False
    return verify_password(password, admin.password)


def create_cash(db: Session, amount: float, userID: int):
    db_cash = models.Cash(amount=amount, userID=userID)
    db.add(db_cash)
    db.commit()
    db.refresh(db_cash)
    return db_cash


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


def update_stock_by_id(db: Session, symbol: str, amount: int, cost: float, userID: int):
    stock = db.query(models.Stock).filter(models.Stock.userID == userID, models.Stock.symbol == symbol).first()
    if stock is None:
        db_stock = models.Stock(symbol=symbol, amount=amount, cost=cost, userID=userID)
        db.add(db_stock)
        db.commit()
    else:
        total_amount = stock.amount + amount
        total_cost = stock.cost + cost
        if (total_amount == 0):
            db.query(models.Stock).filter(models.Stock.userID == userID, models.Stock.symbol == symbol).delete()
        else:
            db.query(models.Stock).filter(models.Stock.userID == userID, models.Stock.symbol == symbol).update({models.Stock.amount:total_amount, models.Stock.cost:total_cost})
        db.commit()


def get_stock_by_id(db: Session, symbol: str, id: int):
    stock = db.query(models.Stock).filter(models.Stock.userID == id, models.Stock.symbol == symbol).first()
    return stock


def get_stocks_by_id(db: Session, id: int):
    stocks = db.query(models.Stock).filter(models.Stock.userID == id)
    return stocks


def get_cash_amount_by_id(db: Session, id: int):
    cash = db.query(models.Cash).filter(models.Cash.userID == id).first()
    if cash is None:
        return 0;
    else:
        return cash.amount


def get_cash_amount_by_username(db: Session, username: str):
    user = get_user_by_username(db, username)
    if user is None:
        logging.warning("username not found in users table")
        return None
    return get_cash_amount_by_id(db, user.id)


def get_assets_by_id(db: Session, id: int):
    assets = []
    cash = get_cash_amount_by_id(db, id)
    assets.append({"type": "cash", "value": cash, "symbol": "USD"})
    stocks = get_stocks_by_id(db, id)
    for stock in stocks:
        stock_price = finnhub_client.quote(stock.symbol.upper())
        value = stock_price.c * stock.amount
        assets.append({"type": "stock", "value": value, "symbol": stock.symbol})
    return assets


def update_cash_by_id(db: Session, id:int, cash: float):
    user = db.query(models.User).filter(models.User.id == id).first()
    if user is None:
        logging.warning("userID not found in users table")
        return
    db.query(models.Cash).filter(models.Cash.userID == id).update({models.Cash.amount:cash})
    db.commit()


def update_cash_by_username(db: Session, username: str, cash: float):
    user = get_user_by_username(db, username)
    if user is None:
        logging.warning("username not found in users table")
        return
    logging.info("update userID %d cash to %f" % (user.id, cash))
    update_cash_by_id(db, id=user.id, cash=cash)


def update_cash_by_groupname(db: Session, groupname: str, cash: float):
    users = db.query(models.User).filter(models.User.groupname == groupname)
    for user in users:
        logging.info("update cash for user %s" % user.username)
        update_cash_by_username(db, username=user.username, cash=cash)


async def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
        token_data = schemas.TokenData(username=username)
    except JWTError:
        raise credentials_exception
    user = get_user_by_username(db, username=token_data.username)
    if user is None:
        raise credentials_exception
    return user


async def get_current_admin(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
        token_data = schemas.TokenData(username=username)
    except JWTError:
        raise credentials_exception

    user = get_user_by_username(db, username=token_data.username)
    if user is None or not user.is_admin:
        raise credentials_exception
    return user


@app.post("/api/users/register", response_model=schemas.UserInfo)
async def register_user(user: schemas.UserCreate, db: Session = Depends(get_db)):
    user.is_admin = False
    db_user = get_user_by_username(db, username=user.username)
    if db_user:
        raise HTTPException(status_code=400, detail="Username already registered")
    # zero out cash amount for self-registered user
    user.cash = 0.0
    db_user = create_user(db=db, user=user)
    create_cash(db=db, amount=user.cash, userID=db_user.id)
    return db_user


@app.post("/api/admin/register", response_model=schemas.UserInfo)
async def register_admin(user: schemas.UserCreate, db: Session = Depends(get_db)):
    user.is_admin = True
    db_admin = get_admin(db)
    if db_admin:
        raise HTTPException(status_code=400, detail="Admin already registered")
    db_user = get_user_by_username(db, username=user.username)
    if db_user:
        raise HTTPException(status_code=400, detail="Username already registered")
    db_user = create_user(db=db, user=user)
    return db_user


@app.post("/api/admin/update_user", response_model=schemas.UserInfo)
async def update_password(user: schemas.UserCreate, db: Session = Depends(get_db),
                          current_user: schemas.UserInfo = Depends(get_current_user)):
    if not current_user.is_admin:
        return {"result": "failed", "reason": "%s is not the admin" % current_user.username }
    db_user = get_user_by_username(db=db, username=user.username)
    if db_user is None:
        return {"result": "failed", "reason": "username %s not found" % user.username }
    if user.password is not None and user.password != "":
        hashed = get_password_hash(user.password)
        db_user.password = hashed
    if user.firstname is not None and user.firstname != "":
        db_user.firstname = user.firstname
    if user.lastname is not None and user.lastname != "":
        db_user.lastname = user.lastname
    if user.groupname is not None and user.groupname != "":
        db_user.groupname = user.groupname
    db.commit()
    return get_user_by_username(db=db, username=user.username)


@app.post("/api/users/update", response_model=schemas.UserInfo)
async def update_password(user: schemas.UserCreate, db: Session = Depends(get_db),
                          current_user: schemas.UserInfo = Depends(get_current_user)):
    if current_user is None:
        return {"result": "failed", "reason": "current user not valid!" }
    if user.password is not None and user.password != "":
        hashed = get_password_hash(user.password)
        current_user.password = hashed
    if user.firstname is not None and user.firstname != "":
        current_user.firstname = user.firstname
    if user.lastname is not None and user.lastname != "":
        current_user.lastname = user.lastname
    if user.groupname is not None and user.groupname != "":
        current_user.groupname = user.groupname
    db.commit()
    return get_user_by_username(db=db, username=user.username)


@app.post("/api/admin/delete_users", response_model=schemas.OpResult)
async def delete_users(usernames: schemas.DeleteUsers, db: Session = Depends(get_db), current_user: schemas.UserInfo = Depends(get_current_user)):
    # only the admin can do the operation
    if not current_user.is_admin:
        return {"result": "failed", "reason": "%s is not the admin" % current_user.username }
    if usernames.usernames is None or len(usernames.usernames) == 0:
        return {"result": "failed", "reason": "users not specified"}
    for username in usernames.usernames:
        # skip self
        if username == current_user.username:
            logging.info("skip deleting current user")
            continue
        delete_user_by_username(db=db, username=username)
    return {"result": "ok"}


@app.post("/api/admin/delete_users_by_group", response_model=schemas.OpResult)
async def delete_users_by_group(group: schemas.Group, db: Session = Depends(get_db), current_user: schemas.UserInfo = Depends(get_current_user)):
    if not current_user.is_admin:
        return {"result": "failed", "reason": "%s is not the admin" % current_user.username }
    db_users = db.query(models.User).filter(models.User.groupname == group.groupname).all()
    for user in db_users:
        # skip self
        if user.username == current_user.username:
            logging.info("skip deleting current user")
            continue
        delete_user_by_username(db=db, username=user.username)
    delete_group_by_groupname(db, group.groupname)
    return {"result": "ok"}


@app.post("/api/admin/add_user", response_model=schemas.OpResult)
async def add_user(user: schemas.UserCreate, db: Session = Depends(get_db), current_user: schemas.UserInfo = Depends(get_current_user)):
    if not current_user.is_admin:
        return {"result": "failed", "reason": "%s is not the admin" % current_user.username }
    if user is None or user.username is None:
        return {"result": "failed", "reason": "user not specified"}
    db_user = create_user(db=db, user=user)
    if db_user is None:
        return {"result": "failed", "reason": "user exists"}
    else:
        create_cash(db=db, amount=0.0, userID=db_user.id)
    return {"result": "ok"}


@app.post("/api/admin/add_users", response_model=schemas.OpResult)
async def add_users(users: schemas.UsersCreate, db: Session = Depends(get_db), current_user: schemas.UserInfo = Depends(get_current_user)):
    if not current_user.is_admin:
        return {"result": "failed", "reason": "%s is not the admin" % current_user.username }
    if users is None or len(users.users) == 0:
        return {"result": "failed", "reason": "users not specified"}
    for user in users.users:
        db_user = create_user(db=db, user=user)
        if db_user is None:
            return {"result": "failed", "reason": "failed to create user %s, may already exist" % user}
        else:
            create_cash(db=db, amount=0.0, userID=db_user.id)
    return {"result": "ok"}


@app.post("/api/admin/fill_user_cash", response_model=schemas.OpResult)
async def fill_user_cash(user_cashinfo: schemas.FillUserCash, db: Session = Depends(get_db), current_user: schemas.UserInfo = Depends(get_current_user)):
    if not current_user.is_admin:
        return {"result": "failed", "reason": "%s is not the admin" % current_user.username }
    update_cash_by_username(db, username=user_cashinfo.username, cash=user_cashinfo.amount)
    updated = get_cash_amount_by_username(db, user_cashinfo.username)
    if updated is None or updated != user_cashinfo.amount:
        return {"result": "failed", "reason": "failed to verify cash amount for user %s" % user_cashinfo.username}
    else:
        return {"result": "ok"}


@app.post("/api/admin/add_group", response_model=schemas.OpResult)
async def add_group(group: schemas.Group, db: Session = Depends(get_db), current_user: schemas.UserInfo = Depends(get_current_user)):
    if not current_user.is_admin:
        return {"result": "failed", "reason": "%s is not the admin" % current_user.username}
    if get_group_by_groupname(db, group.groupname) is not None:
        return {"result": "ok","reason": "group exists"}
    db_group = create_group(db, group)
    if db_group is None:
        return {"result": "failed", "reason": "failed to add group %s into database" % group.groupname}
    else:
        return {"result": "ok"}


@app.post("/api/admin/delete_group", response_model=schemas.OpResult)
async def delete_group(group: schemas.Group, db: Session = Depends(get_db), current_user: schemas.UserInfo = Depends(get_current_user)):
    if not current_user.is_admin:
        return {"result": "failed", "reason": "%s is not the admin" % current_user.username}
    if group.groupname == "default":
        return {"result": "failed", "reason": "can not delete default group"}
    delete_group_by_groupname(db, group.groupname)
    return {"result": "ok"}


@app.post("/api/admin/update_group", response_model=schemas.OpResult)
async def update_group(group: schemas.Group, db: Session = Depends(get_db), current_user: schemas.UserInfo = Depends(get_current_user)):
    if not current_user.is_admin:
        return {"result": "failed", "reason": "%s is not the admin" % current_user.username}
    db_group = db.query(models.Group).filter(models.Group.groupname == group.groupname).first()
    if db_group is None:
        return {"result": "failed","reason": "group not found"}
    db_group.description = group.description
    db.commit()
    return {"result": "ok"}


@app.get("/api/groups", response_model=schemas.GroupList)
async def list_group(db: Session = Depends(get_db)):
    groups = []
    db_groups = db.query(models.Group)
    for group in db_groups:
        groups.append({"groupname": group.groupname, "description": group.description})
    return {"groups": groups}


@app.post("/api/admin/list_users", response_model=schemas.UserList)
async def list_users(group: schemas.Group, db: Session = Depends(get_db), current_user: schemas.UserInfo = Depends(get_current_user)):
    if not current_user.is_admin:
        logging.warning("only admin can list users")
        return {"users": []}
    db_users = db.query(models.User).filter(models.User.groupname == group.groupname).all()
    users = []
    for user in db_users:
        # skip self
        if user.username == current_user.username:
            logging.info("skip listing current user")
            continue
        users.append({"username": user.username, "firstname": user.firstname, "lastname": user.lastname})
    return {"users": users}


@app.get("/api/admin/list_user_assets", response_model=schemas.UserAsset)
async def list_user_assets(username: str, db: Session = Depends(get_db), current_user: schemas.UserInfo = Depends(get_current_user)):
    if not current_user.is_admin:
        logging.warning("only admin can list user assets")
        return {}
    db_user = db.query(models.User).filter(models.User.username == username).first()    
    userassets = get_assets_by_id(db, db_user.id)
    total = 0.0
    for userasset in userassets:
        total += userasset["value"]
    return {"user": {"username": username, "firstname": db_user.firstname, "lastname": db_user.lastname}, "assets": userassets, "total": total}


@app.post("/api/admin/list_group_assets", response_model=schemas.UserAssetList)
async def list_group_assets(group: schemas.Group, db: Session = Depends(get_db), current_user: schemas.UserInfo = Depends(get_current_user)):
    if not current_user.is_admin:
        logging.warning("only admin can list group assets")
        return {"assets": []}
    db_users = db.query(models.User).filter(models.User.groupname == group.groupname).all()
    assets = []
    for user in db_users:
        # skip self
        if user.username == current_user.username:
            logging.info("skip current user")
            continue
        userinfo = {"username": user.username, "firstname": user.firstname, "lastname": user.lastname}
        userassets = get_assets_by_id(db, user.id)
        total = 0.0
        for userasset in userassets:
            total += userasset["value"]
        assets.append({"user": userinfo, "assets": userassets, "total": total})
    return {"assets": assets}


@app.post("/api/admin/fill_group_cash", response_model=schemas.OpResult)
async def fillall_cash(group_cashinfo: schemas.FillGroupCash, db: Session = Depends(get_db), current_user: schemas.UserInfo = Depends(get_current_user)):
    if not current_user.is_admin:
        return {"result": "failed", "reason": "%s is not the admin" % current_user.username }
    update_cash_by_groupname(db, groupname=group_cashinfo.groupname, cash=group_cashinfo.amount)
    return {"result": "ok"}


@app.post("/api/token", response_model=schemas.Token)
async def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    user = get_user_by_username(db, username=form_data.username)
    if user is None or not verify_password(form_data.password, user.password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": form_data.username}, expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer",
            "username": user.username, "firstname": user.firstname,
            "lastname": user.lastname, "is_admin": user.is_admin}


@app.get("/api/users/me", response_model=schemas.UserInfoBase)
async def read_users_me(current_user: schemas.UserInfoBase = Depends(get_current_user)):
    return {"username": current_user.username,
            "firstname": current_user.firstname,
            "lastname": current_user.lastname,
            "is_admin": current_user.is_admin}

@app.get("/api/admin/user_by_username", response_model=schemas.UserInfo)
async def get_user_info_by_username(username: str, db: Session = Depends(get_db),
                                    current_user: schemas.UserInfo = Depends(get_current_user)):
    if not current_user.is_admin:
        return {"result": "failed", "reason": "%s is not the admin" % current_user.username }
    return get_user_by_username(db, username)
    

@app.get("api/admin/group_by_groupname", response_model=schemas.Group)
async def get_group_info_by_groupname(groupname: str, db: Session = Depends(get_db),
                                      current_user: schemas.UserInfo = Depends(get_current_user)):
    if not current_user.is_admin:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="%s is not the admin" % current_user.username,
            headers={"WWW-Authenticate": "Bearer"},
        )
    db_group = db.query(models.Group).filter(models.Group.groupname == groupname).first()    
    return {"groupname": db_group.groupname, "description": db_group.description}                       


@app.get("/api/stock/quote", response_model=schemas.StockQuote)
async def stock_price(symbol: str, current_user: schemas.UserInfo = Depends(get_current_user)):
    try:
        price = finnhub_client.quote(symbol.upper()).c
    except:
        return {"result": "failed"}
    if type(price) is float:
        return {"result": "ok", "price": price}
    else:
        return {"result": "failed"}

@app.post("/api/stock/buy", response_model=schemas.OpResult)
async def buy_stock(stock: schemas.StockBuyInfo, current_user: schemas.UserInfo = Depends(get_current_user), db: Session = Depends(get_db)):
    amount = stock.amount
    try:
        stock_price = finnhub_client.quote(stock.symbol.upper())        
        cost = amount * stock_price.c
    except:
        return {"result": "failed", "reason": "invalid stock symbol"}
    available_cash = get_cash_amount_by_id(db, current_user.id)
    if (available_cash > cost):
        update_cash_by_id(db, current_user.id, available_cash - cost)
        update_stock_by_id(db, symbol=stock.symbol, amount=amount, cost=cost, userID=current_user.id)   
        return {"result": "ok"}
    else:
        return {"result": "failed", "reason": "Insufficient fund"}
        available_cash = get_cash_amount_by_id(db, current_user.id)


@app.post("/api/stock/sell", response_model=schemas.OpResult)
async def sell_stock(stock: schemas.StockSellInfo, current_user: schemas.UserInfo = Depends(get_current_user), db: Session = Depends(get_db)):
    try:
        stock_price = finnhub_client.quote(stock.symbol.upper())
        proceeding = stock.amount * stock_price.c
    except:
        return {"result": "failed", "reason": "invalid stock symbol"}
    availble_stock = get_stock_by_id(db, stock.symbol, current_user.id)
    if availble_stock is None:
        return {"result": "failed", "reason": "User does not have this stock"}
    availble_stock_amount = availble_stock.amount
    if availble_stock_amount < stock.amount:
        return {"result": "failed", "reason": "Insufficient stock"}
    else:
        available_cash = get_cash_amount_by_id(db, current_user.id)
        update_cash_by_id(db, current_user.id, available_cash + proceeding)
        update_stock_by_id(db, symbol=stock.symbol, amount=-stock.amount, cost=-proceeding, userID=current_user.id)
        return {"result": "ok"}


@app.get("/api/users/assets", response_model=schemas.TotalAssets)
async def list_assets(current_user: schemas.UserInfo = Depends(get_current_user), db: Session = Depends(get_db)):
    assets = []
    cash = get_cash_amount_by_id(db, current_user.id)
    assets.append({"type": "cash", "value": cash, "symbol": "USD"})
    stocks = get_stocks_by_id(db, current_user.id)
    for stock in stocks:
        stock_price = finnhub_client.quote(stock.symbol.upper())
        value = stock_price.c * stock.amount
        assets.append({"type": "stock", "value": value, "symbol": stock.symbol})
    return {"assets": assets}



if __name__ == "__main__":
    # make sure default group always exists before create user
    create_default_group(SessionLocal())
    uvicorn.run("main:app", host="0.0.0.0", port=8000, log_level="info")
