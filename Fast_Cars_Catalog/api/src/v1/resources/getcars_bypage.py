from fastapi import Depends, HTTPException, Query
from typing import Optional
from sqlalchemy.orm import Session
from api.models.models import Car
from api.models.session import get_db
from sqlalchemy import and_, asc, desc
import math


def get_cars_by_page(
    page: int = Query(1, ge=1),
    size: int = Query(10, ge=1),
    brand: str = '%',
    model: str = '%',
    transmission: str = '%',
    price_operator: Optional[str] = None,
    price: int = 0,
    price_max: Optional[int] = None,
    sort_by: Optional[str] = None,
    sort_direction: str = 'asc',
    db: Session = Depends(get_db)
):
    try:
        price_max_value = price_max if price_max is not None else price + 1

        query = db.query(Car)

        query = query.filter(
            and_(
                Car.brand.ilike(f"%{brand}%"),
                Car.model.ilike(f"%{model}%"),
                Car.transmission.ilike(f"%{transmission}%")
            )
        )

        if price_operator == 'lte':
            query = query.filter(Car.price <= price)
        elif price_operator == 'gte':
            query = query.filter(Car.price >= price)
        elif price_operator == 'between':
            query = query.filter(Car.price >= price, Car.price <= price_max_value)

        if sort_by:
            if sort_direction == 'asc':
                query = query.order_by(asc(getattr(Car, sort_by)))
            else:
                query = query.order_by(desc(getattr(Car, sort_by)))

        total = query.count()
        pages = math.ceil(total / size) if total > 0 else 0
        offset = (page - 1) * size
        cars = query.offset(offset).limit(size).all()

        cars_response = [car.to_json() for car in cars]

        return {
            'data': cars_response,
            'page': page,
            'size': size,
            'total_elements': total,
            'total_page': pages
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
