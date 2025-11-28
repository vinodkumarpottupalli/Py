from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import declarative_base

Base = declarative_base()


class Car(Base):
    __tablename__ = 'car'

    id = Column(String(50), primary_key=True)
    brand = Column(String(50))
    model = Column(String(50))
    transmission = Column(String(20))
    price = Column(Integer)
    release_year = Column(Integer)

    def __init__(self, id, brand, model, transmission, price, release_year):
        self.id = id
        self.brand = brand
        self.model = model
        self.transmission = transmission
        self.price = price
        self.release_year = release_year

    def to_json(self):
        return {
            'id': self.id,
            'brand': self.brand,
            'model': self.model,
            'transmission': self.transmission,
            'price': self.price,
            'release_year': self.release_year
        }
