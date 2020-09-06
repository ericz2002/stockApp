from sqlalchemy import * 
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

meta = MetaData()

ugroups = Table('ugroups', meta,
        Column('id', Integer, primary_key=True, index=True),
        Column('groupname', String(16), unique=True),
        Column('description', String(128))
        )

users = Table('users', meta, 
        Column('id', Integer, primary_key=True, index=True),
        Column('username', String(16), unique=True),
        Column('password', String(40)),
        Column('firstname', String(16)),
        Column('lastname', String(20)),
        Column('groupname', String(16)),
        Column('is_admin', Boolean)
        )

cash = Table('cash', meta,
        Column('id', Integer, primary_key=True, index=True),
        Column('amount', Float),
        Column('userID', Integer, ForeignKey("users.id"))
        )

stocks = Table('stocks', meta,
        Column('id', Integer, primary_key=True, index=True),
        Column('symbol', String(8)),
        Column('amount', Integer),
        Column('cost', Float),
        Column('userID', Integer, ForeignKey("users.id"))
        )