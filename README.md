# CSP-code

Tkinter app that simulates how crude oil price changes impact related costs (transportation, food cost, annual expenditure, and healthcare), with live visualization.

The model is trained with scikit-learn using the CSV files in this workspace: crude oil prices provide the input feature, and the category CSVs provide the historical target values.

## Run the app

```bash
python3 oil_impact_simulator.py
```

## Run the Streamlit version

```bash
streamlit run streamlit_oil_impact_simulator.py
```

## Run tests

```bash
python3 -m unittest -q
```
