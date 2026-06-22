import nfp_playbook
import streamlit as st
import pandas as pd
from streamlit_lightweight_charts import renderLightweightCharts

def get_series_options():
    return {
        "upColor": "#26a63b", "downColor": "#ef5350",
        "wickUpColor": "#26a63b", "wickDownColor": "#ef5350",
        "borderVisible": False, "priceLineVisible": True, "lastValueVisible": True
    }

def get_candle_markers(plot_df, threshold):
    markers = []
    for _, row in plot_df.iterrows():
        if row['body_size'] >= threshold:
            markers.append({
                "time": row['time'], "position": 'aboveBar',
                "color": '#26a69a' if row['Close'] >= row['Open'] else '#ef5350',
                "shape": 'none', "text": str(row['body_size'])
            })
    return markers

def add_snapshot_button():
    st.sidebar.info("Tip: Use 'Print Screen' or Browser 'Save Page' to capture.")
    if st.sidebar.button("Save chart as JPEG"):
        st.sidebar.warning("Right-click the chart area and select 'Save Image As'.")
                            
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

# LINEAR EXECUTION
df = load_data()
selected_date = st.sidebar.selectbox("Select Date", df['Date'].unique())
plot_df = df[df['Date'] == selected_date].copy()

# 1. UI INPUTS (Define these BEFORE the chart is rendered)
timeframe = st.sidebar.radio("Select Timeframe:", ["5min", "15min"], horizontal=True)
show_school_run = st.sidebar.checkbox("Show School Run (2nd 15m candle)", key="sr_toggle")
threshold = st.sidebar.selectbox("Show candle numbers for size over:", [10, 15, 20, 25, 30, 35, 40])
st.sidebar.markdown("---")

# 2. LOGIC (Handle Resampling and Lines)
# --- LOGIC ---
# 2. LOGIC (Handle Resampling and Lines)
plot_df = df[df['Date'] == selected_date].copy()
school_run_lines = []
sr_series = []

if timeframe == "15min":
    # Perform resampling exactly once
    resampled = plot_df.resample('15min', on='dt_obj').agg({
        'Open': 'first', 'High': 'max', 'Low': 'min', 'Close': 'last'
    }).dropna()
    
    # Update plot_df for rendering
    plot_df = resampled.reset_index().rename(columns={'dt_obj': 'time'})
    plot_df['time'] = plot_df['time'].apply(lambda x: int(x.timestamp()))
    plot_df['body_size'] = (plot_df['Close'] - plot_df['Open']).abs().round(2)
    
    # Calculate School Run math & build series
    if show_school_run and len(plot_df) >= 2:
        second_candle = plot_df.iloc[1]
        school_run_lines = [
            {"price": float(second_candle['High']) + 2.0, "color": "#ff0000", "lineWidth": 2, "lineStyle": 2, "title": "SR High"},
            {"price": float(second_candle['Low']) - 2.0, "color": "#ff0000", "lineWidth": 2, "lineStyle": 2, "title": "SR Low"}
        ]
        
        # Build the 'Line' series layers (for SR lines)
        for line in school_run_lines:
            sr_series.append({
                "type": "Line",
                "data": [{"time": int(t), "value": float(line['price'])} for t in plot_df['time']],
                "options": {
                    "color": line['color'],
                    "lineWidth": line['lineWidth'],
                    "lineStyle": 2, 
                    "title": line['title']
                }
            })
        st.sidebar.write(f"Lines: High={school_run_lines[0]['price']}, Low={school_run_lines[1]['price']}")

# 3. PREPARE CHART DATA
chart_data = plot_df.rename(columns={'Open': 'open', 'High': 'high', 'Low': 'low', 'Close': 'close'})[['time', 'open', 'high', 'low', 'close']].to_dict(orient="records")

# 4. RENDER
st.title(f"DAX {selected_date} - {timeframe} Chart")
# 4. RENDER
st.title(f"DAX {selected_date} - {timeframe} Chart")

# We render the chart first
chart_data_dicts = plot_df.rename(columns={'Open': 'open', 'High': 'high', 'Low': 'low', 'Close': 'close'})[['time', 'open', 'high', 'low', 'close']].to_dict(orient="records")

# Create the chart component
chart = renderLightweightCharts([{
    "chart": {
        "width": 1200, "height": 700,
        "timeScale": {"timeVisible": True, "secondsVisible": False, "barSpacing": 40}
    },
    "series": [
        {
            "type": "Candlestick",
            "data": chart_data,
            "options": {**get_series_options()},
            "markers": get_candle_markers(plot_df, threshold)
        },
        *sr_series  # This adds the lines as an extra layer
    ]
}], key=f"dax-{selected_date}-{timeframe}")