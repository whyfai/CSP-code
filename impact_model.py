from functools import lru_cache
from pathlib import Path

import pandas as pd
from sklearn.linear_model import LinearRegression


DATA_DIR = Path(__file__).resolve().parent
CRUDE_PRICE_COLUMN = "Oil price - Crude prices since 1861"


def _load_training_frame(target_filename: str) -> pd.DataFrame:
    crude_prices = pd.read_csv(DATA_DIR / "crude-oil-prices.csv")
    target_values = pd.read_csv(DATA_DIR / target_filename)

    crude_prices.columns = crude_prices.columns.str.strip()
    target_values.columns = target_values.columns.str.strip()

    training_frame = crude_prices[["Year", CRUDE_PRICE_COLUMN]].merge(
        target_values[["Year", "Value"]],
        on="Year",
        how="inner",
    )
    return training_frame.rename(
        columns={
            CRUDE_PRICE_COLUMN: "crude_price",
            "Value": "target_value",
        }
    )


@lru_cache(maxsize=1)
def _fit_models() -> dict[str, LinearRegression]:
    models: dict[str, LinearRegression] = {}
    for label, filename in (
        ("Transportation", "transportation.csv"),
        ("Food Cost", "food.csv"),
        ("Annual Expenditure", "annual-expenditure.csv"),
        ("Healthcare", "healthcare.csv"),
    ):
        training_frame = _load_training_frame(filename)
        model = LinearRegression()
        model.fit(training_frame[["crude_price"]], training_frame["target_value"])
        models[label] = model
    return models


def _predict(model: LinearRegression, crude_price: float) -> float:
    input_frame = pd.DataFrame({"crude_price": [float(crude_price)]})
    return float(model.predict(input_frame)[0])


def calculate_impacts(crude_price: float) -> dict[str, float]:
    """Return estimated downstream costs for a given crude oil price.

    The estimates are learned from the CSV files in this workspace using a
    one-feature scikit-learn regression per series. Crude oil prices are the
    independent variable, while the target CSVs provide the historical data
    points used for fitting.

    The UI expects four downstream categories, each backed by its own learned
    regression trained from the matching CSV file.
    """
    models = _fit_models()

    transportation = _predict(models["Transportation"], crude_price)
    food_cost = _predict(models["Food Cost"], crude_price)
    annual_expenditure = _predict(models["Annual Expenditure"], crude_price)
    healthcare = _predict(models["Healthcare"], crude_price)

    return {
        "Crude Oil": float(crude_price),
        "Transportation": transportation,
        "Food Cost": food_cost,
        "Annual Expenditure": annual_expenditure,
        "Healthcare": healthcare,
    }
