from sqlalchemy import Column, Integer, String, Float
from database import  Base, meta 

class Group(Base):
    __table__ = meta.tables['ugroups']

    
class User(Base):
    __table__ = meta.tables['users']
    
#    __tablename__ = "users"
#    id = Column(Integer, primary_key=True, index=True)
#    username = Column(String, unique=True)
#    password = Column(String)
#    firstname = Column(String)
#    lastname = Column(String)
#    is_admin = Column(Bool)

class Cash(Base):
    __table__ = meta.tables['cash']

#    __tablename__ = "cash"
#    id = Column(Integer, primary_key=True, index=True)
#    amount = Column(Float)
#    userID = Column(Integer)
#
class Stock(Base):
    __table__ = meta.tables['stocks']

#    __tablename__ = "stocks"
#    id = Column(Integer, primary_key=True, index=True)
#    symbol = Column(String)
#    amount = Column(Integer)
#    cost = Column(Float)
#    userID = Column(Integer)

