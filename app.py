import streamlit as st
import pandas as pd
from streamlit_lightweight_charts import renderLightweightCharts

# 1. Load your data
@st.cache_data
def load_data():
    return pd.read_csv("DAX_Cash_2024.csv") # Ensure your CSV matches this name

df = load_data()

# 2. Setup the chart layout
st.title("DAX Blueprint Engine")

# This is where the rendering happens
renderLightweightCharts([
    {
        "chart": {
            "width": 800,
            "height": 400,
            "layout": {"backgroundColor": "#131722", "textColor": "#d1d4dc"},
            "grid": {"vertLines": {"color": "#334155"}, "horizLines": {"color": "#334155"}},
            "priceScale": {"borderColor": "#555"},
        },
        "series": [
            {
                "type": "Candlestick",
                "data": df.to_dict(orient="records") # Assumes CSV has columns: time, open, high, low, close
            }
        ],
    }
], "dax-chart")