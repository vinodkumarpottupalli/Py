import uuid
import random
import uvicorn
from fastapi import FastAPI
from api.models.session import init_db, SessionLocal
from api.models.models import Car
from api.src.v1 import v1_router
from sqlalchemy.orm import Session


app = FastAPI(title="Fast Cars Catalog")


@app.on_event("startup")
def startup_event():
    # Initialize DB and populate sample data
    init_db()
    db = SessionLocal()
    try:
        # Seed with 100 cars
        for i in range(1, 101):
            if i <= 33:
                brand = 'Honda'
            elif i <= 66:
                brand = 'Ford'
            else:
                brand = 'BMW'

            model = f"{brand} {i}"
            transmission = 'AUTOMATIC' if i % 2 != 0 else 'MANUAL'
            price = random.randint(30000, 80000)
            release_year = 2020 + (i % 3)
            car = Car(str(uuid.uuid4()), brand, model, transmission, price, release_year)
            db.add(car)
        db.commit()
    finally:
        db.close()


app.include_router(v1_router)


@app.get('/')
def read_root():
    return {"message": "FastAPI Cars Catalog"}


if __name__ == '__main__':
    uvicorn.run("app:app", host="127.0.0.1", port=8000, reload=True)
