from fastapi import FastAPI, HTTPException

from src.predict import predict_demand

app = FastAPI(
    title="Retail Store Demand Forecasting API",
    version="1.0.0",
    description="Predict next-day demand from store, product, price, promotion, and date information.",
)


@app.get("/")
def root():
    return {
        "message": "Retail Store Demand Forecasting API is running.",
        "routes": ["GET /health", "POST /predict"],
    }


@app.get("/health")
def health_check():
    return {"status": "ok"}


@app.post("/predict")
def predict(payload: dict):
    try:
        record = payload.get("data", payload)

        if isinstance(record, list):
            if not record:
                raise ValueError("At least one record is required.")
            record = record[-1]

        if not isinstance(record, dict):
            raise ValueError("Request body must be a JSON object.")

        prediction = predict_demand(record)

        return {
            "status": "success",
            "predicted_demand": prediction,
            "unit": "items",
            "message": "Predicted demand for the selected date.",
        }

    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc))
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"Prediction failed: {str(exc)}")
