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