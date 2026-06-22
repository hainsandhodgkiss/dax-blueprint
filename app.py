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
    """Generates markers to display body_size above/below candles."""
    markers = []
    for _, row in plot_df.iterrows():
        # Place marker above/below based on candle direction
        position = 'aboveBar'
        color = '#26a69a' if row['Close'] >= row['Open'] else '#ef5350'
        
        markers.append({
            "time": row['time'],
            "position": position,
            "color": color,
            "shape": 'circle',
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
    
    # Calculate values
    df['body_size'] = (df['Close'] - df['Open']).abs().round(2)
    df['range_size'] = (df['High'] - df['Low']).round(2)
    
    df['dt_obj'] = pd.to_datetime(df['Date'] + ' ' + df['Time'], dayfirst=True)
    df['time'] = df['dt_obj'].apply(lambda x: int(x.timestamp()))
    return df.dropna()

try:
    df = load_data()
    selected_date = st.sidebar.selectbox("Select Date", df['Date'].unique())
    plot_df = df[df['Date'] == selected_date].copy()
    
    # Map to list of dicts
    chart_data = []
    for _, row in plot_df.iterrows():
        chart_data.append({
            "time": row['time'],
            "open": row['Open'],
            "high": row['High'],
            "low": row['Low'],
            "close": row['Close'],
            # This 'text' field is used by the chart to render labels above candles
            "text": f"{row['body_size']}" 
        })
    
    renderLightweightCharts([
        {
            "chart": {
                "width": 1000, "height": 500,
                "timeScale": {"timeVisible": True, "secondsVisible": False, "barSpacing": 15}
            },
            "series": [{
                "type": "Candlestick",
                "data": chart_data,
                "options": get_series_options(),
                "markers": get_candle_markers(plot_df) # <--- CALL THE ADD-ON HERE
            }]
            
        }
    ], key=f"dax-{selected_date}")
except Exception as e:
    st.error(f"Render Error: {e}")