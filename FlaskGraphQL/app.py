from cProfile import run
from flask import Flask, render_template, redirect, request, url_for, jsonify
from werkzeug.middleware.proxy_fix import ProxyFix
from flask_sqlalchemy import SQLAlchemy
import uuid
from ariadne import QueryType, load_schema_from_path, make_executable_schema, graphql_sync, MutationType


app = Flask(__name__)

app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///cars.db"
db = SQLAlchemy(app)

app.config['SECRET_KEY'] = 'mysecretkey'
app.config['SESSION_COOKIE_SAMESITE'] = 'None'
app.config['SESSION_COOKIE_HTTPONLY'] = True
app.config['SESSION_COOKIE_SECURE'] = True
app.config['PREFERRED_URL_SCHEME'] = 'https'


@app.route("/")
def index():
    print('Received headers', request.headers)
    return render_template('index.html')


@app.route("/redirect/")
def redirect_to_index():
    return redirect(url_for('index'))


class Car(db.Model):
    __tablename__ = 'cars'

    car_id = db.Column(db.String(36), primary_key=True)
    brand = db.Column(db.String(50), nullable=False)
    model = db.Column(db.String(50), nullable=False)
    transmission = db.Column(db.String(20), nullable=False)
    price = db.Column(db.Integer)
    release_year = db.Column(db.Integer)
    description = db.Column(db.String(50))
    engine_id = db.Column(db.String(36), db.ForeignKey('engines.engine_id'))
    engine = db.relationship('Engine')
    features = db.relationship('Feature', backref='car')
 
    def __init__(self, car_id, brand, model, transmission, price, release_year, description, engine_id):
        self.car_id = car_id
        self.brand = brand
        self.model = model
        self.transmission = transmission
        self.price = price
        self.release_year = release_year
        self.description = description
        self.engine_id = engine_id

    def to_dict(self):
        return {
            'car_id': self.car_id,
            'brand': self.brand, 
            'model': self.model,
            'transmission': self.transmission,
            'price': self.price,
            'release_year': self.release_year,
            'description': self.description,
            'engine_id': self.engine_id,
            'features': [f.to_dict() for f in self.features]
        }


class Engine(db.Model):
    __tablename__ = 'engines'
    
    engine_id = db.Column(db.String(36), primary_key=True)
    name = db.Column(db.String(50), nullable=False)
    capacity_cc = db.Column(db.Integer)
    horsepower = db.Column(db.Integer)
    torque = db.Column(db.Integer)

    def __init__(self, engine_id, name, capacity_cc, horsepower, torque):
        self.engine_id = engine_id
        self.name = name
        self.capacity_cc = capacity_cc
        self.horsepower = horsepower
        self.torque = torque
        
    def to_dict(self):
        return {
            'engine_id': self.engine_id, 
            'name': self.name,
            'capacity_cc': self.capacity_cc,
            'horsepower': self.horsepower,
            'torque': self.torque
        }


class Feature(db.Model):
    __tablename__ = 'features'

    feature_id = db.Column(db.String(36), primary_key=True)
    name = db.Column(db.String(50), nullable=False)
    installation_price = db.Column(db.Integer)
    car_id = db.Column(db.String(36), db.ForeignKey('cars.car_id'))

    def __init__(self, feature_id, name, installation_price):
        self.feature_id = feature_id
        self.name = name
        self.installation_price = installation_price

    def to_dict(self):
        return {
            'feature_id': self.feature_id, 
            'name': self.name,
            'installation_price': self.installation_price,
            'car_id': self.car_id
        }


with app.app_context():
    db.drop_all()
    db.create_all()

    car_ids = [
        'bc467c74-9e09-4468-99c3-876a55a550d2',
        '02f7d4af-d328-4f5a-a4e1-6b91e5894212',
        '7888dc2c-d29f-40f8-b87b-db742f3b8c24',
        '2fa568ad-ec8c-4f4d-941d-ee76149a0eb1',
        '10d2c29b-8070-4f71-aba9-b409c132d803',
        'b2bb6c51-cb35-4252-9ad4-7d58d9c68671',
        '2ce64548-1a60-4848-a1db-3081dc93116a',
        'c5363cd0-ba44-4013-84d9-451ecc1e57f4',
        '4fbf9eb1-3b46-4162-ae0e-875c5ae5b86a',
        'a80f0718-c2fe-4422-9c41-d31f5fcb1212'
        ]

    engine_ids = [
        '29c59a2a-a289-4ffc-8b4d-57b6d612a6f8',
        'e879773c-b2b8-418f-9b03-63d992ebbe27',
        '7c68089d-0c6b-4119-94c8-5f46cf5ecce1',
        '3092b838-4518-4d88-9cc9-65749f20f1ea'
        ]

    engine_1 = Engine( engine_ids[0], 'Dummy Engine 1', 1500, 450, 456 )
    engine_2 = Engine( engine_ids[1], 'Dummy Engine 2', 1600, 500, 507 )
    engine_3 = Engine( engine_ids[2], 'Dummy Engine 3', 1700, 600, 558 )
    engine_4 = Engine( engine_ids[3], 'Dummy Engine 4', 1800, 650, 609 )

    db.session.add_all( [engine_1, engine_2, engine_3, engine_4] )
    db.session.commit()

    for i in range(0, 10):
        if i < 3:
            brand = 'Honda'
        elif i < 6:
            brand = 'Ford'
        else:
            brand = 'BMW'
 
        model = brand + ' ' + str(i)
 
        if i % 2 != 0:
            transmission = 'AUTOMATIC'
        else:
            transmission = 'MANUAL'
 
        price = 50000 + i
        release_year = 2021 + (i % 3)
 
        engine_id = engine_ids[i % len(engine_ids)]
 
        car = Car( car_ids[i], brand, model, transmission, price, release_year, 'description ' + str(i), engine_id )
        
        feature_a = Feature( str(uuid.uuid4()), 'Feature for ' + model + ' A', 100 + i)
        feature_b = Feature( str(uuid.uuid4()), 'Feature for ' + model + ' B', 100 + i)
        
        feature_a.car = car
        feature_b.car = car
        
        db.session.add(car)
        db.session.add_all( [feature_a, feature_b] ) 
        
        db.session.commit()

################# FLASK API #######################################
@app.route('/api/cars', methods=['GET'])
def find_cars():
    cars = Car.query.all()
 
    response = [car.to_dict() for car in cars]
 
    return jsonify(response), 200
    

@app.route('/api/car/<car_id>', methods=['GET'])
def find_car(car_id):
    car = Car.query.filter(Car.car_id.__eq__(car_id)).first()
 
    return jsonify(car.to_dict()), 200


@app.route('/api/engine/<engine_id>', methods=['GET'])
def find_engine(engine_id):
    engine = Engine.query.filter(Engine.engine_id.__eq__(engine_id)).first()
 
    return jsonify(engine.to_dict()), 200


##########################################


query = QueryType()
mutation = MutationType()

graphql_schema_def = load_schema_from_path("cars.graphql")
schema = make_executable_schema(
    graphql_schema_def, query, mutation
)


@query.field("find_cars")
def resolve_find_cars(_, info):
    return Car.query.all()

@query.field("find_car_by_id")
def resolve_find_car_by_id(_, info, car_id):
    return Car.query.filter(Car.car_id.__eq__(car_id)).first()

@query.field("find_engine_by_id")
def resolve_find_engine_by_id(_, info, engine_id):
    return Engine.query.filter(Engine.engine_id.__eq__(engine_id)).first()

@app.route("/graphql", methods=["POST"])
def graphql_server():
    data = request.get_json()
    success, result = graphql_sync(
        schema,
        data,
        context_value=request,
        debug=app.debug
    )
    status_code = 200 if success else 400

    return jsonify(result), status_code

@mutation.field("create_engine")
def resolve_create_engine(_, info, name, capacity_cc=0, horsepower=0, torque=0):
    new_engine_id = str(uuid.uuid4())
    new_engine = Engine( new_engine_id, name, capacity_cc, horsepower, torque)
    db.session.add(new_engine)
    db.session.commit()
 
    return {
        "success": True,
        "engine_id": new_engine_id
    }

@mutation.field("create_car")   
def resolve_create_car(_, info, brand, model, transmission, price, release_year, description, engine_id, features):
    new_car_id = str(uuid.uuid4())
 
    new_car = Car( new_car_id, brand, model, transmission, price, release_year, description, engine_id )
 
    db.session.add(new_car)
 
    for f in features:
        new_car_feature = Feature( str(uuid.uuid4()), f["name"], f["installation_price"])
        new_car_feature.car = new_car
        db.session.add(new_car_feature)
 
    db.session.commit()
 
    return {
        "success": True,
        "car_id": new_car_id
    }

@mutation.field("delete_car_by_id")
def resolve_delete_car_by_id(_, info, car_id):
    Feature.query.filter(Feature.car_id.__eq__(car_id)).delete()
    Car.query.filter(Car.car_id.__eq__(car_id)).delete()
    
    db.session.commit()
    
    return {
        "success": True,
        "car_id": car_id
    }

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080)