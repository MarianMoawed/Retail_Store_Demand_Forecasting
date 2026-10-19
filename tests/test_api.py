from datetime import date

from fastapi.testclient import TestClient

from app import app

client = TestClient(app)


def test_root_route():
    response = client.get("/")
    assert response.status_code == 200
    assert "message" in response.json()


def test_health_route():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_predict_valid_record():
    payload = {
        "Date": "2024-04-18",
        "Price": 79.99,
        "Discount": 15.0,
        "Promotion": 1,
        "store_number": 1,
        "product_number": 1,
        "Category": "Groceries",
        "Region": "North",
        "Seasonality": "Spring",
    }

    response = client.post("/predict", json=payload)
    assert response.status_code == 200
    body = response.json()
    assert body["status"] == "success"
    assert isinstance(body["predicted_demand"], (int, float))
    assert body["predicted_demand"] >= 0


def test_predict_invalid_store_number_fails():
    payload = {
        "Date": "2024-04-18",
        "Price": 79.99,
        "Discount": 15.0,
        "Promotion": 1,
        "store_number": 99,
        "product_number": 1,
        "Category": "Groceries",
        "Region": "North",
        "Seasonality": "Spring",
    }

    response = client.post("/predict", json=payload)
    assert response.status_code == 400


def test_predict_invalid_category_fails():
    payload = {
        "Date": "2024-04-18",
        "Price": 79.99,
        "Discount": 15.0,
        "Promotion": 1,
        "store_number": 1,
        "product_number": 1,
        "Category": "UnknownCategory",
        "Region": "North",
        "Seasonality": "Spring",
    }

    response = client.post("/predict", json=payload)
    assert response.status_code == 400
