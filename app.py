import streamlit as st
import pandas as pd
from streamlit_lightweight_charts import renderLightweightCharts

def get_series_options():
    return {
        "upColor": "#26a63b",
        "downColor": "#ef5350",
        "wickUpColor": "#26a63b",
        "wickDownColor": "#ef5350",
        "borderVisible": False,
        "priceLineVisible": True,
        "lastValueVisible": True
    }

def get_candle_markers(plot_df):
    markers = []
    for _, row in plot_df.iterrows():
        # Only show markers for candles with body_size 20 or greater
        if row['body_size'] >= 20:
            markers.append({
                "time": row['time'],
                "position": 'aboveBar',
                "color": '#26a69a' if row['Close'] >= row['Open'] else '#ef5350',
                "shape": 'none',
                "text": str(row['body_size'])
            })
    return markers

st.set_page_config(layout="wide")

@st.cache_data
def load_data():
    df = pd.read_csv("DAX_Cash_2026.csv", sep=';')
    df.columns = df.columns.str.strip()
    for col in ['Open', 'High', 'Low', 'Close']:
        df[col] = pd.to_numeric(df[col], errors='coerce')
    df['body_size'] = (df['Close'] - df['Open']).abs().round(2)
    df['dt_obj'] = pd.to_datetime(df['Date'] + ' ' + df['Time'], dayfirst=True)
    df['time'] = df['dt_obj'].apply(lambda x: int(x.timestamp()))
    return df.dropna()

try:
    df = load_data()
    selected_date = st.sidebar.selectbox("Select Date", df['Date'].unique())
    plot_df = df[df['Date'] == selected_date].copy()
    chart_data = plot_df.rename(columns={'Open': 'open', 'High': 'high', 'Low': 'low', 'Close': 'close'})[['time', 'open', 'high', 'low', 'close']].to_dict(orient="records")
    
    renderLightweightCharts([{
        "chart": {
            "width": 1200, "height":700,
            "timeScale": {"timeVisible": True, "secondsVisible": False, "barSpacing": 40}
        },
        "series": [{
            "type": "Candlestick",
            "data": chart_data,
            "options": get_series_options(),
            "markers": get_candle_markers(plot_df)
        }]
    }], key=f"dax-{selected_date}")
except Exception as e:
    st.error(f"Render Error: {e}")