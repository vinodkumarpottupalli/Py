import math
import uuid
import logging
from typing import Optional
from pydantic import BaseModel
from models import Base, Car, CarSummary
from sqlalchemy.exc import SQLAlchemyError
from contextlib import asynccontextmanager
from database import async_session, engine
from sqlalchemy import select, and_, func, text
from sqlalchemy.ext.asyncio import AsyncSession
from logging.handlers import RotatingFileHandler
from fastapi.middleware.cors import CORSMiddleware
from fastapi import FastAPI, Depends, Query, HTTPException


class CarCreate(BaseModel):
    brand: str
    model: str
    transmission: str
    price: int
    release_year: int


class CarIdList(BaseModel):
    ids: list[str]


# Adding handlers for startup
@asynccontextmanager
async def lifespan(app: FastAPI):
    # create tables if not exist
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    logger.info("Database tables ensured on startup")
    yield


app = FastAPI(title="Fast Pagination API", lifespan=lifespan)

# Allow all origins
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


async def get_session() -> AsyncSession:
    async with async_session() as session:
        yield session


# Configure rotating file logger (5 MB max, keep 5 backups)
logger = logging.getLogger("fast_pagination")
logger.setLevel(logging.INFO)
if not logger.handlers:
    fh = RotatingFileHandler("fast_pagination.log", maxBytes=5 * 1024 * 1024, backupCount=5)
    formatter = logging.Formatter("%(asctime)s %(levelname)s %(name)s %(message)s")
    fh.setFormatter(formatter)
    logger.addHandler(fh)
    # also log to console at INFO
    ch = logging.StreamHandler()
    ch.setFormatter(formatter)
    logger.addHandler(ch)


def _validate_sort_field(field: str):
    # Basic validation: ensure attribute exists on model
    # Accept fields present on either the full Car model or the CarSummary view
    if not (hasattr(Car, field) or hasattr(CarSummary, field)):
        raise HTTPException(status_code=400, detail=f"Invalid sort field: {field}")


@app.get("/api/cars")
async def find_cars(
    page: int = Query(1, ge=1),
    size: int = Query(10, ge=1, le=1000),
    brand: str = "%",
    model: str = "%",
    transmission: str = "%",
    price_operator: Optional[str] = None,
    price: int = 0,
    price_max: Optional[int] = None,
    sort_by: Optional[str] = None,
    sort_direction: str = "asc",
    session: AsyncSession = Depends(get_session),
):
    try:
        filters = [
            Car.brand.ilike(f"%{brand}%"),
            Car.model.ilike(f"%{model}%"),
            Car.transmission.ilike(f"%{transmission}%"),
        ]

        if price_operator == 'lte':
            filters.append(Car.price <= price)
        elif price_operator == 'gte':
            filters.append(Car.price >= price)
        elif price_operator == 'between':
            if price_max is None:
                price_max = price + 1
            filters.append(Car.price >= price)
            filters.append(Car.price <= price_max)

        order_by_clause = None
        if sort_by:
            _validate_sort_field(sort_by)
            col = getattr(Car, sort_by)
            order_by_clause = col.asc() if sort_direction == 'asc' else col.desc()

        # total count
        total_q = select(func.count()).select_from(Car).where(and_(*filters))
        total_result = await session.execute(total_q)
        total = total_result.scalar_one()

        offset = (page - 1) * size
        q = select(Car).where(and_(*filters))
        if order_by_clause is not None:
            q = q.order_by(order_by_clause)
        q = q.offset(offset).limit(size)

        result = await session.execute(q)
        cars = result.scalars().all()

        total_pages = math.ceil(total / size) if size else 0

        logger.info("find_cars: page=%s size=%s filters=%s sort=%s %s", page, size, [brand, model, transmission], sort_by, sort_direction)

        return {
            "data": [c.to_dict() for c in cars],
            "page": page,
            "size": size,
            "total_element": total,
            "total_page": total_pages,
        }
    except HTTPException:
        raise
    except SQLAlchemyError as e:
        logger.exception("Database error in find_cars: %s", e)
        raise HTTPException(status_code=500, detail="Database error")
    except Exception as e:
        logger.exception("Unexpected error in find_cars: %s", e)
        raise HTTPException(status_code=500, detail="Internal Server Error")


@app.get("/api/cars/{car_id}")
async def get_car_by_id(
    car_id: str,
    session: AsyncSession = Depends(get_session),
):
    """Get a single car by its ID."""
    try:
        q = select(Car).where(Car.id == car_id)
        result = await session.execute(q)
        car = result.scalars().first()

        if not car:
            raise HTTPException(status_code=404, detail=f"Car with ID {car_id} not found")

        return {"data": car.to_dict()}
    except HTTPException:
        raise
    except SQLAlchemyError as e:
        logger.exception("Database error in get_car_by_id: %s", e)
        raise HTTPException(status_code=500, detail="Database error")
    except Exception as e:
        logger.exception("Unexpected error in get_car_by_id: %s", e)
        raise HTTPException(status_code=500, detail="Internal Server Error")


@app.post("/api/cars")
async def create_car(
    car: CarCreate,
    session: AsyncSession = Depends(get_session),
):
    """Create a new car entry in the database."""
    try:
        new_car = Car(
            id=str(uuid.uuid4()),
            brand=car.brand,
            model=car.model,
            transmission=car.transmission,
            price=car.price,
            release_year=car.release_year,
        )
        session.add(new_car)
        await session.commit()
        await session.refresh(new_car)

        logger.info("Car created: %s", new_car.id)

        return {
            "data": new_car.to_dict(),
            "message": "Car created successfully",
        }
    except SQLAlchemyError as e:
        logger.exception("Database error in create_car: %s", e)
        raise HTTPException(status_code=500, detail="Database error")
    except Exception as e:
        logger.exception("Unexpected error in create_car: %s", e)
        raise HTTPException(status_code=500, detail="Internal Server Error")


@app.post("/api/cars/search/by-ids")
async def search_cars_by_ids(
    payload: CarIdList,
    session: AsyncSession = Depends(get_session),
):
    """Search for multiple cars by their IDs."""
    try:
        if not payload.ids:
            raise HTTPException(status_code=400, detail="ids list cannot be empty")

        q = select(Car).where(Car.id.in_(payload.ids))
        result = await session.execute(q)
        cars = result.scalars().all()

        logger.info("search_cars_by_ids: requested=%s found=%s", len(payload.ids), len(cars))

        return {
            "data": [c.to_dict() for c in cars],
            "count": len(cars),
            "requested_ids": payload.ids,
        }
    except HTTPException:
        raise
    except SQLAlchemyError as e:
        logger.exception("Database error in search_cars_by_ids: %s", e)
        raise HTTPException(status_code=500, detail="Database error")
    except Exception as e:
        logger.exception("Unexpected error in search_cars_by_ids: %s", e)
        raise HTTPException(status_code=500, detail="Internal Server Error")


@app.get("/api/multisort")
async def find_cars_multisort(
    page: int = Query(1, ge=1),
    size: int = Query(10, ge=1, le=1000),
    brand: str = "%",
    model: str = "%",
    transmission: str = "%",
    price_operator: Optional[str] = None,
    price: int = 0,
    price_max: Optional[int] = None,
    sort_by: Optional[str] = None,
    sort_direction: str = "asc",
    session: AsyncSession = Depends(get_session),
):
    try:
        filters = [
            Car.brand.ilike(f"%{brand}%"),
            Car.model.ilike(f"%{model}%"),
            Car.transmission.ilike(f"%{transmission}%"),
        ]

        if price_operator == 'lte':
            filters.append(Car.price <= price)
        elif price_operator == 'gte':
            filters.append(Car.price >= price)
        elif price_operator == 'between':
            if price_max is None:
                price_max = price + 1
            filters.append(Car.price >= price)
            filters.append(Car.price <= price_max)

        order_by_clauses = []
        if sort_by:
            list_sort_by = [s.strip() for s in sort_by.split(',') if s.strip()]
            list_sort_direction = [s.strip() for s in sort_direction.split(',') if s.strip()]

            # pad directions
            while len(list_sort_direction) < len(list_sort_by):
                list_sort_direction.append('asc')

            for idx, sb in enumerate(list_sort_by):
                _validate_sort_field(sb)
                col = getattr(Car, sb)
                dir = list_sort_direction[idx] if idx < len(list_sort_direction) else 'asc'
                order_by_clauses.append(col.asc() if dir == 'asc' else col.desc())

        # total count
        total_q = select(func.count()).select_from(Car).where(and_(*filters))
        total_result = await session.execute(total_q)
        total = total_result.scalar_one()

        offset = (page - 1) * size
        q = select(Car).where(and_(*filters))
        if order_by_clauses:
            q = q.order_by(*order_by_clauses)
        q = q.offset(offset).limit(size)

        result = await session.execute(q)
        cars = result.scalars().all()

        total_pages = math.ceil(total / size) if size else 0

        logger.info("find_cars_multisort: page=%s size=%s filters=%s sort_by=%s sort_dir=%s", page, size, [brand, model, transmission], sort_by, sort_direction)

        return {
            "data": [c.to_dict() for c in cars],
            "page": page,
            "size": size,
            "total_element": total,
            "total_page": total_pages,
        }
    except HTTPException:
        raise
    except SQLAlchemyError as e:
        logger.exception("Database error in find_cars_multisort: %s", e)
        raise HTTPException(status_code=500, detail="Database error")
    except Exception as e:
        logger.exception("Unexpected error in find_cars_multisort: %s", e)
        raise HTTPException(status_code=500, detail="Internal Server Error")


@app.get("/api/getcars")
async def getcars(
    page: int = Query(1, ge=1),
    size: int = Query(10, ge=1, le=1000),
    session: AsyncSession = Depends(get_session),
):
    """Return paginated rows from the `car_summary` view (id, brand, price)."""
    try:
        # total count from view
        total_q = select(func.count()).select_from(CarSummary)
        total_result = await session.execute(total_q)
        total = total_result.scalar_one()

        offset = (page - 1) * size
        q = select(CarSummary).offset(offset).limit(size)

        result = await session.execute(q)
        rows = result.scalars().all()

        total_pages = math.ceil(total / size) if size else 0

        logger.info("getcars: page=%s size=%s returned=%s total=%s", page, size, len(rows), total)

        return {
            "data": [r.to_dict() for r in rows],
            "page": page,
            "size": size,
            "total_element": total,
            "total_page": total_pages,
        }
    except SQLAlchemyError as e:
        logger.exception("Database error in getcars: %s", e)
        raise HTTPException(status_code=500, detail="Database error")
    except Exception as e:
        logger.exception("Unexpected error in getcars: %s", e)
        raise HTTPException(status_code=500, detail="Internal Server Error")