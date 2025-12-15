from flask_sqlalchemy import SQLAlchemy
db = SQLAlchemy()

class Car(db.Model):
    id = db.Column(db.String(50), primary_key=True)
    brand = db.Column(db.String(50))
    model = db.Column(db.String(50))
    transmission = db.Column(db.String(20))
    price = db.Column(db.Integer)
    release_year = db.Column(db.Integer)
 
    def __init__(self, id, brand, model, transmission, price, release_year):
        self.id = id
        self.brand = brand
        self.model = model
        self.transmission = transmission
        self.price = price
        self.release_year = release_year
    
    def to_json(self):
        return {
            'brand': self.brand, 
            'model': self.model,
            'transmission': self.transmission,
            'price': self.price,
            'release_year': self.release_year
        }