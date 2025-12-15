import os
import uuid
import random
from flask import Flask, render_template, redirect, request, url_for, jsonify, make_response
from sqlalchemy import and_, text
from api.models.models import Car, db


app = Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI'] = "sqlite:///carcatlog.db"
app.config['SECRET_KEY'] = 'mysecretkey'
app.config['SESSION_COOKIE_SAMESITE'] = 'None'
app.config['SESSION_COOKIE_HTTPONLY'] = True
app.config['SESSION_COOKIE_SECURE'] = True
app.config['PREFERRED_URL_SCHEME'] = 'https'

db.init_app(app)


@app.route('/', methods=['GET'])
def index():
    return "Hello World!!"

def create_app():
    with app.app_context():
        db.drop_all()
        db.create_all()

        for i in range(1, 101):
            if i <= 33:
                brand = 'Honda'
            elif i <= 66:
                brand = 'Ford'
            else:
                brand = 'BMW'
        
            model = brand + ' ' + str(i)
        
            if i % 2 != 0:
                transmission = 'AUTOMATIC'
            else:
                transmission = 'MANUAL'
        
            price = random.randint(30000, 80000)
            release_year = 2020 + (i % 3)

            car = Car( str(uuid.uuid4()), brand, model, transmission, price, release_year )
            db.session.add(car)
            db.session.commit()

    return app
from api.src.v1 import v1_bp
app.register_blueprint(v1_bp)


if __name__ == '__main__':
    app = create_app()
    app.run()