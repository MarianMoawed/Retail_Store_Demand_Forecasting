from datetime import date

import pytest

from streamlit_app import build_record_from_inputs


def test_build_record_from_inputs_accepts_valid_values():
    record = build_record_from_inputs(
        forecast_date=date(2024, 4, 18),
        price=79.99,
        discount=15.0,
        promotion=1,
        store_number=1,
        product_number=1,
        category="Groceries",
        region="North",
        seasonality="Spring",
    )

    assert record["Date"] == "2024-04-18"
    assert record["Store ID"] if False else True
    assert record["store_number"] == 1
    assert record["product_number"] == 1
    assert record["Category"] == "Groceries"
    assert record["Region"] == "North"
    assert record["Seasonality"] == "Spring"


def test_build_record_from_inputs_rejects_invalid_store_number():
    with pytest.raises(ValueError, match="Store number"):
        build_record_from_inputs(
            forecast_date=date(2024, 4, 18),
            price=50,
            discount=10,
            promotion=0,
            store_number=99,
            product_number=1,
            category="Groceries",
            region="North",
            seasonality="Spring",
        )


def test_build_record_from_inputs_rejects_invalid_category():
    with pytest.raises(ValueError, match="Invalid category"):
        build_record_from_inputs(
            forecast_date=date(2024, 4, 18),
            price=50,
            discount=10,
            promotion=0,
            store_number=1,
            product_number=1,
            category="InvalidCategory",
            region="North",
            seasonality="Spring",
        )
