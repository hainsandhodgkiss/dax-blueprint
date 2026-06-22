import streamlit as st
import pandas as pd
from streamlit_lightweight_charts import renderLightweightCharts

# --- MODULAR ADD-ONS ---

def get_series_options():
    return {
        "upColor": "#26a69a",
        "downColor": "#ef5350",
        "wickUpColor": "#26a69a",
        "wickDownColor": "#ef5350",
        "borderVisible": False,
        "priceLineVisible": True,
        "lastValueVisible": True
    }

def get_candle_markers(plot_df):
    markers = []
    for _, row in plot_df.iterrows():
        markers.append({
            "time": row['time'],
            "position": 'aboveBar',
            "color": '#26a69a' if row['Close'] >= row['Open'] else '#ef5350',
            "shape": 'circle',
            "text": str(row['body_size'])
        })
    return markers

# --- MAIN CORE CODE ---

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
    chart_data = plot_df[['time', 'Open', 'High', 'Low', 'Close']].rename(
        columns={'Open': 'open', 'High': 'high', 'Low': 'low', 'Close': 'close'}
    ).to_dict(orient="records")
    
    renderLightweightCharts([
        {
            "chart": {
                "width": 1000, 
                "height": 500,
                # Increased spacing to prevent bunching
                "timeScale": {
                    "timeVisible": True, 
                    "secondsVisible": False, 
                    "barSpacing": 25, 
                    "minBarSpacing": 15
                }
            },
            "series": [{
                "type": "Candlestick",
                "data": chart_data,
                "options": get_series_options(),
                "markers": get_candle_markers(plot_df)
            }]
        }
    ], key=f"dax-{selected_date}")

except Exception as e:
    st.error(f"Render Error: {e}")