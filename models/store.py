from db import db
from sqlalchemy import Column, String, Integer


class StoreModel(db.Model):
    __tablename__ = "store"

    id = Column(Integer, primary_key=True)
    name = Column(String(80), unique=True, nullable=False)


