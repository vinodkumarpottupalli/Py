# Fast_pagination
Fast Api

Quick start (Windows CMD):

1. Create and activate a virtual environment, install dependencies:

```
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
```

2. Create DB and populate sample data (optional):

```
python create_data.py
```

3. Run the app with uvicorn:

```
uvicorn app:app --host 0.0.0.0 --port 8080 --reload
```

Endpoints:
- GET /api/cars - paginated, filter and sort support
- GET /api/multisort - same as `/api/cars` but accepts multi-field sort_by and sort_direction comma-separated