from flask import Blueprint
from flask_restful import Api

from .resources.get_cars import GetCars
from .resources.getcars_bypage import GetCarsByPage
from .resources.getcars_multisort import GetCarsByMultiSort

request_bp = Blueprint('requests', __name__, url_prefix='/requests')
Api(request_bp).add_resource(GetCars, '/getcars')
Api(request_bp).add_resource(GetCarsByPage, '/getcarsbypage')
Api(request_bp).add_resource(GetCarsByMultiSort, '/getcarsbypagebymultisort')