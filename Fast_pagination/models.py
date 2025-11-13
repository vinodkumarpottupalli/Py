from sqlalchemy import Column, String, Integer, DDL
from sqlalchemy import event
from sqlalchemy.orm import declarative_base

Base = declarative_base()


class Car(Base):
    __tablename__ = 'car'

    id = Column(String(50), primary_key=True)
    brand = Column(String(50), index=True)
    model = Column(String(50), index=True)
    transmission = Column(String(20), index=True)
    price = Column(Integer, index=True)
    release_year = Column(Integer)

    def to_dict(self):
        return {
            "id": self.id,
            "brand": self.brand,
            "model": self.model,
            "transmission": self.transmission,
            "price": self.price,
            "release_year": self.release_year,
        }


#View to increase performance
class CarSummary(Base):
    __tablename__ = 'car_summary'

    id = Column(String(50), primary_key=True)
    brand = Column(String(50))
    price = Column(Integer)

    def to_dict(self):
        return {
            "id": self.id,
            "brand": self.brand,
            "price": self.price,
        }


# Create SQL view after tables are created.
create_view_ddl = DDL(
    "CREATE VIEW IF NOT EXISTS car_summary AS SELECT id, brand, price FROM car;"
)
drop_view_ddl = DDL("DROP VIEW IF EXISTS car_summary;")

event.listen(Base.metadata, "after_create", create_view_ddl)
event.listen(Base.metadata, "before_drop", drop_view_ddl)
