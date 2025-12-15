import os
from flask import jsonify, make_response
from flask_restful import Resource, Api
from api.models.models import Car


class GetCars(Resource):
    def get(self):
        try:
            cars = Car.query.all()

            cars_response = [car.to_json() for car in cars]
    
            return make_response(jsonify(cars_response), 200)
        except Exception as e:
            return {'error': str(e)}