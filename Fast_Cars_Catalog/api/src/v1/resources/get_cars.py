from fastapi import Depends, HTTPException
from typing import List
from sqlalchemy.orm import Session
from api.models.models import Car
from api.models.session import get_db


def get_cars(db: Session = Depends(get_db)) -> List[dict]:
    try:
        cars = db.query(Car).all()
        return [car.to_json() for car in cars]
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
