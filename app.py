import streamlit as st
import pandas as pd
from streamlit_lightweight_charts import renderLightweightCharts
import nfp_playbook

st.set_page_config(layout="wide")

# --- DATA LOAD ---
df = pd.read_csv("DAX_Cash_2026.csv", sep=';')
df.columns = df.columns.str.strip()
for col in ['Open', 'High', 'Low', 'Close']:
    df[col] = pd.to_numeric(df[col], errors='coerce')
df['body_size'] = (df['Close'] - df['Open']).abs().round(2)
df['dt_obj'] = pd.to_datetime(df['Date'] + ' ' + df['Time'], dayfirst=True)
df['time'] = df['dt_obj'].apply(lambda x: int(x.timestamp()))
df = df.dropna()

# --- SIDEBAR & STATE ---
date_list = list(df['Date'].unique())
selected_date = st.sidebar.selectbox("Select Date", date_list)
threshold = st.sidebar.selectbox("Show candle numbers for size over:", [10, 15, 20, 25, 30, 35, 40])

# --- CHART PREP ---
plot_df = df[df['Date'] == selected_date].copy()
chart_data = plot_df.rename(columns={'Open': 'open', 'High': 'high', 'Low': 'low', 'Close': 'close'})[['time', 'open', 'high', 'low', 'close']].to_dict(orient="records")

# --- MARKER LOGIC ---
markers = []
for _, row in plot_df.iterrows():
    if row['body_size'] >= threshold:
        markers.append({
            "time": row['time'], 
            "position": 'aboveBar', 
            "color": '#26a69a' if row['Close'] >= row['Open'] else '#ef5350', 
            "shape": 'none', 
            "text": str(row['body_size'])
        })

# --- RENDER ---
st.title(f"DAX {selected_date} - 5 Minute Chart")
renderLightweightCharts([{
    "chart": {
        "width": 1200, 
        "height": 700, 
        "timeScale": {"timeVisible": True, "secondsVisible": False, "barSpacing": 40}
    },
    "series": [{
        "type": "Candlestick", 
        "data": chart_data, 
        "options": {
            "upColor": "#26a63b", "downColor": "#ef5350", 
            "wickUpColor": "#26a63b", "wickDownColor": "#ef5350"
        }, 
        "markers": markers
    }]
}])

# --- PLAYBOOK ---
st.sidebar.markdown("---")
st.sidebar.subheader("Data Event Playbook")
selected_month = st.sidebar.selectbox("Select NFP Month:", list(nfp_playbook.get_nfp_data().keys()))
event_dates = nfp_playbook.get_event_dates(selected_month)
col1, col2, col3 = st.sidebar.columns(3)
if col1.button("Pre"): st.write(f"Target: {event_dates['before']}")
if col2.button("NFP"): st.write(f"Target: {event_dates['nfp']}")
if col3.button("Post"): st.write(f"Target: {event_dates['after']}")