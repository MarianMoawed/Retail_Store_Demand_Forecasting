from datetime import date

import streamlit as st

from src.predict import CATEGORY_OPTIONS, predict_demand


def build_record_from_inputs(
    forecast_date,
    price,
    discount,
    promotion,
    store_number,
    product_number,
    category,
    region,
    seasonality,
):
    record = {
        "Date": forecast_date.isoformat(),
        "Price": float(price),
        "Discount": float(discount),
        "Promotion": int(promotion),
        "store_number": int(store_number),
        "product_number": int(product_number),
        "Category": str(category),
        "Region": str(region),
        "Seasonality": str(seasonality),
    }

    if not 1 <= int(store_number) <= 5:
        raise ValueError("Store number must be between 1 and 5.")
    if not 1 <= int(product_number) <= 20:
        raise ValueError("Product number must be between 1 and 20.")

    valid_categories = set(CATEGORY_OPTIONS["Category"])
    valid_regions = set(CATEGORY_OPTIONS["Region"])
    valid_seasons = set(CATEGORY_OPTIONS["Seasonality"])

    if record["Category"] not in valid_categories:
        raise ValueError("Invalid category selected.")
    if record["Region"] not in valid_regions:
        raise ValueError("Invalid region selected.")
    if record["Seasonality"] not in valid_seasons:
        raise ValueError("Invalid seasonality selected.")

    return record


def render_form():
    st.set_page_config(
        page_title="Retail Demand Forecasting",
        page_icon="📦",
        layout="centered",
    )

    st.title("Retail Store Demand Forecasting")
    st.caption("Predict the next-day demand for a store and product using the trained model.")

    with st.form("forecast_form"):
        col1, col2 = st.columns(2)

        with col1:
            forecast_date = st.date_input("Forecast Date", value=date.today())
            price = st.number_input("Price", min_value=0.0, value=79.99, step=0.01)
            discount = st.number_input("Discount", min_value=0.0, value=15.0, step=0.01)
            promotion = st.selectbox("Promotion", [0, 1])
            store_number = st.number_input("Store Number", min_value=1, max_value=5, value=1, step=1)

        with col2:
            product_number = st.number_input("Product Number", min_value=1, max_value=20, value=1, step=1)
            category = st.selectbox("Category", CATEGORY_OPTIONS["Category"])
            region = st.selectbox("Region", CATEGORY_OPTIONS["Region"])
            seasonality = st.selectbox("Seasonality", CATEGORY_OPTIONS["Seasonality"])

        submitted = st.form_submit_button("Predict Demand")

    if submitted:
        try:
            record = build_record_from_inputs(
                forecast_date,
                price,
                discount,
                promotion,
                store_number,
                product_number,
                category,
                region,
                seasonality,
            )
            prediction = predict_demand(record)
            st.success(f"Predicted demand: {prediction} items")
        except ValueError as exc:
            st.error(f"Invalid input: {exc}")
        except Exception as exc:
            st.error(f"Prediction failed: {exc}")


if __name__ == "__main__":
    render_form()
