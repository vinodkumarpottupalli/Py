from fastapi.testclient import TestClient
from app import app


client = TestClient(app)


def test_get_cars_root():
    response = client.get('/v1/carsdetails/requests/getcars')
    assert response.status_code == 200
    assert isinstance(response.json(), list)


def test_get_cars_by_page():
    response = client.get('/v1/carsdetails/requests/getcarsbypage?page=1&size=5')
    assert response.status_code == 200
    data = response.json()
    assert 'data' in data
    assert isinstance(data['data'], list)


def test_get_cars_multisort():
    response = client.get('/v1/carsdetails/requests/getcarsbypagebymultisort?sort_by=brand,price&sort_direction=asc,desc')
    assert response.status_code == 200
    data = response.json()
    assert 'data' in data
    assert isinstance(data['data'], list)
