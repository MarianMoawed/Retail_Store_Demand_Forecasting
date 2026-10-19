from pathlib import Path

import joblib
import pandas as pd


BASE_DIR = Path(__file__).resolve().parent.parent
MODEL_PATH = BASE_DIR / "models" / "demand_model.joblib"

MODEL_BUNDLE = joblib.load(MODEL_PATH)
MODEL = MODEL_BUNDLE["model"]
FEATURE_COLUMNS = MODEL_BUNDLE["feature_columns"]
CATEGORY_OPTIONS = MODEL_BUNDLE["category_options"]

NUMERIC_FIELDS = [
    "Price",
    "Discount",
    "Promotion",
    "Year",
    "Month",
    "Day",
    "DayOfWeek",
    "DayOfYear",
    "WeekOfYear",
    "Is_Weekend",
]

CATEGORICAL_FIELDS = [
    "Store ID",
    "Product ID",
    "Category",
    "Region",
    "Seasonality",
]

FIELD_ALIASES = {
    "Store_ID": "Store ID",
    "Store ID": "Store ID",
    "store_id": "Store ID",
    "store_number": "Store ID",
    "Product_ID": "Product ID",
    "Product ID": "Product ID",
    "product_id": "Product ID",
    "product_number": "Product ID",
    "date": "Date",
    "Date": "Date",
}


def normalize_record(record: dict) -> dict:
    normalized = {}

    for key, value in record.items():
        normalized[str(key).strip()] = value

    alias_map = {
        "Store_ID": "Store ID",
        "store_id": "Store ID",
        "Product_ID": "Product ID",
        "product_id": "Product ID",
        "date": "Date",
    }

    for old_name, new_name in alias_map.items():
        if old_name in normalized and new_name not in normalized:
            normalized[new_name] = normalized[old_name]

    if "store_number" in normalized:
        store_number = int(normalized["store_number"])
        if not 1 <= store_number <= 5:
            raise ValueError("Store number must be between 1 and 5.")
        normalized["Store ID"] = f"S{store_number:03d}"

    if "product_number" in normalized:
        product_number = int(normalized["product_number"])
        if not 1 <= product_number <= 20:
            raise ValueError("Product number must be between 1 and 20.")
        normalized["Product ID"] = f"P{product_number:04d}"

    if "Date" in normalized and not all(
        key in normalized
        for key in [
            "Year",
            "Month",
            "Day",
            "DayOfWeek",
            "DayOfYear",
            "WeekOfYear",
            "Is_Weekend",
        ]
    ):
        date = pd.to_datetime(normalized["Date"])
        normalized["Year"] = int(date.year)
        normalized["Month"] = int(date.month)
        normalized["Day"] = int(date.day)
        normalized["DayOfWeek"] = int(date.dayofweek)
        normalized["DayOfYear"] = int(date.dayofyear)
        normalized["WeekOfYear"] = int(date.isocalendar().week)
        normalized["Is_Weekend"] = int(date.dayofweek in [5, 6])

    return normalized


def build_feature_frame(record: dict) -> pd.DataFrame:
    normalized = normalize_record(record)

    for field in ["Price", "Discount", "Promotion"]:
        if field not in normalized:
            raise ValueError(f"Missing required field: {field}")

    for field in NUMERIC_FIELDS:
        if field not in normalized:
            if field not in ["Year", "Month", "Day", "DayOfWeek", "DayOfYear", "WeekOfYear", "Is_Weekend"]:
                raise ValueError(f"Missing required field: {field}")

    for field in CATEGORICAL_FIELDS:
        if field not in normalized:
            raise ValueError(f"Missing required field: {field}")

    feature_row = {column: 0.0 for column in FEATURE_COLUMNS}

    for field in NUMERIC_FIELDS:
        if field not in normalized:
            continue
        feature_row[field] = float(normalized[field])

    for category_name in CATEGORICAL_FIELDS:
        selected_value = str(normalized[category_name])
        valid_values = [str(option) for option in CATEGORY_OPTIONS[category_name]]

        if selected_value not in valid_values:
            raise ValueError(f"Invalid value for {category_name}: {selected_value}")

        column_name = f"{category_name}_{selected_value}"
        if column_name in feature_row:
            feature_row[column_name] = 1.0

    return pd.DataFrame([feature_row], columns=FEATURE_COLUMNS)


def predict_demand(record: dict) -> float:
    feature_frame = build_feature_frame(record)
    prediction = MODEL.predict(feature_frame)[0]
    return round(max(float(prediction), 0.0), 2)
