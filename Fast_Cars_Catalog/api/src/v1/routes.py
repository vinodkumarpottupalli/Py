from fastapi import APIRouter
from typing import List

from . import schemas
from .resources.get_cars import get_cars
from .resources.getcars_bypage import get_cars_by_page
from .resources.getcars_multisort import get_cars_by_multisort

router = APIRouter(prefix='/requests', tags=["requests"])

router.get('/getcars', response_model=List[schemas.CarSchema])(get_cars)
router.get('/getcarsbypage')(get_cars_by_page)
router.get('/getcarsbypagebymultisort')(get_cars_by_multisort)
