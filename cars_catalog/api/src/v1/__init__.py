from flask import Blueprint
from .routes import request_bp

v1_bp = Blueprint('v1', __name__, url_prefix='/v1/carsdetails')
v1_bp.register_blueprint(request_bp)