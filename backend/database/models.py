from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import declarative_base


Base = declarative_base()

class Rental(Base):

    __tablename__ = "rentals"

    id = Column(Integer, primary_key=True)

    title = Column(String)
    price = Column(String)
    location = Column(String)
    link = Column(String)

class User(Base):

    __tablename__ = "users"

    id = Column(Integer, primary_key=True)

    username = Column(String, unique=True)

    email = Column(String, unique=True)

    password = Column(String)
