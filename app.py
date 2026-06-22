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

# LINEAR EXECUTION - NO TRY/EXCEPT BLOCK
df = load_data()
selected_date = st.sidebar.selectbox("Select Date", df['Date'].unique())
plot_df = df[df['Date'] == selected_date].copy()

# --- TIMEFRAME & SCHOOL RUN LOGIC ---
timeframe = st.sidebar.radio("Select Timeframe:", ["5min", "15min"], horizontal=True)
show_school_run = st.sidebar.checkbox("Show School Run (2nd 15m candle)", key="school_run_toggle")
school_run_lines = []

if timeframe == "15min":
    # 1. Resample
    resampled = plot_df.resample('15min', on='dt_obj').agg({
        'Open': 'first', 'High': 'max', 'Low': 'min', 'Close': 'last'
    }).dropna()
    
    # 2. Update plot_df
    plot_df = resampled.reset_index().rename(columns={'dt_obj': 'time'})
    plot_df['time'] = plot_df['time'].apply(lambda x: int(x.timestamp()))
    plot_df['body_size'] = (plot_df['Close'] - plot_df['Open']).abs().round(2)
    
    # 3. Calculate School Run Lines ONLY when we are in 15min mode
    if show_school_run and len(plot_df) >= 2:
        second_candle = plot_df.iloc[1]
        sr_high = float(second_candle['High']) + 2.0
        sr_low = float(second_candle['Low']) - 2.0
        school_run_lines = [
            {"price": sr_high, "color": "#ff0000", "lineWidth": 2, "lineStyle": 0, "axisLabelVisible": True, "title": "SR High"},
            {"price": sr_low, "color": "#ff0000", "lineWidth": 2, "lineStyle": 0, "axisLabelVisible": True, "title": "SR Low"}
        ]
# ----------------------------

chart_data = plot_df.rename(columns={'Open': 'open', 'High': 'high', 'Low': 'low', 'Close': 'close'})[['time', 'open', 'high', 'low', 'close']].to_dict(orient="records")

# Fixed: Only one title showing the active timeframe
st.title(f"DAX {selected_date} - {timeframe} Chart")
threshold = st.sidebar.selectbox("Show candle numbers for size over:", [10, 15, 20, 25, 30, 35, 40])
st.sidebar.markdown("---")

st.sidebar.subheader("Data Event Playbook")
selected_month = st.sidebar.selectbox("Select NFP Month:", list(nfp_playbook.get_nfp_data().keys()))

if st.sidebar.button("Load NFP Window"):
    event_dates = nfp_playbook.get_event_dates(selected_month)
    st.write(f"Analyzing {selected_month}:")
    st.write(f"Before: {event_dates['before']} | NFP: {event_dates['nfp']} | After: {event_dates['after']}")

add_snapshot_button()

# --- SCHOOL RUN LOGIC ---
# --- DEBUGGING SCHOOL RUN LOGIC ---
show_school_run = st.sidebar.checkbox("Show School Run (2nd 15m candle)")
school_run_lines = []

if show_school_run and timeframe == "15min":
    # Let's see what's actually in our plot_df
    st.write(f"DEBUG: Candles available after resample: {len(plot_df)}")
    
    if len(plot_df) >= 2:
        second_candle = plot_df.iloc[1] 
        sr_high = float(second_candle['High']) + 2.0
        sr_low = float(second_candle['Low']) - 2.0
        
        school_run_lines = [
            {"price": sr_high, "color": "#ff0000", "lineWidth": 2, "lineStyle": 0, "axisLabelVisible": True, "title": "SR High"},
            {"price": sr_low, "color": "#ff0000", "lineWidth": 2, "lineStyle": 0, "axisLabelVisible": True, "title": "SR Low"}
        ]
    else:
        st.error("Not enough 15m candles to calculate School Run!")
# --------------------------------
# -------------------------
st.write(f"DEBUG: School Run Lines: {school_run_lines}")
renderLightweightCharts([{
    "chart": {
        "width": 1200, "height": 700,
        "timeScale": {"timeVisible": True, "secondsVisible": False, "barSpacing": 40}
    },
    "series": [{
        "type": "Candlestick",
        "data": chart_data,
        "options": {
            **get_series_options(), 
            "priceLines": school_run_lines # This must be inside 'options'
        },
        "markers": get_candle_markers(plot_df, threshold)
    }]
}], key=f"dax-{selected_date}")