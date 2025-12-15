# Fast Cars Catalog (FastAPI)

This is a FastAPI conversion of the original Flask `cars_catalog` project. It keeps the same folder structure and adds modern dependency injection, Pydantic schemas, and async-ready environment (Uvicorn).

Usage
-----

1. Create a Python virtual environment

```cmd
python -m venv venv
venv\Scripts\activate
```

2. Install requirements

```cmd
pip install -r requirements.txt
```

3. Run the app

```cmd
python app.py
```

This will start a Uvicorn server on http://127.0.0.1:8000 and seed the DB with 100 sample cars on startup.

Endpoints
---------

- GET /v1/carsdetails/requests/getcars
- GET /v1/carsdetails/requests/getcarsbypage?page=1&size=10
- GET /v1/carsdetails/requests/getcarsbypagebymultisort?sort_by=brand,price&sort_direction=asc,desc
