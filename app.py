import nfp_playbook
import streamlit as st
import pandas as pd
from streamlit_lightweight_charts import renderLightweightCharts

st.set_page_config(layout="wide")

# --- CORE FUNCTIONS ---
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
    st.sidebar.info("Tip: Right-click chart to 'Save Image As'")

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

# --- MAIN RENDERING ---
df = load_data()
date_list = list(df['Date'].unique())

# Logic for target date
target = st.session_state.get("target_date", date_list[0])
default_idx = date_list.index(target) if target in date_list else 0

# Selectbox
selected_date = st.sidebar.selectbox("Select Date", date_list, index=default_idx)

# Clear trigger
if "target_date" in st.session_state:
    del st.session_state.target_date

# Rendering
try:
    plot_df = df[df['Date'] == selected_date].copy()
    chart_data = plot_df.rename(columns={'Open': 'open', 'High': 'high', 'Low': 'low', 'Close': 'close'})[['time', 'open', 'high', 'low', 'close']].to_dict(orient="records")
    st.title(f"DAX {selected_date} - 5 Minute Chart")
    threshold = st.sidebar.selectbox("Show candle numbers for size over:", [10, 15, 20, 25, 30, 35, 40])
    add_snapshot_button()
    
    renderLightweightCharts([{
        "chart": {
            "width": 1200, "height": 700,
            "timeScale": {"timeVisible": True, "secondsVisible": False, "barSpacing": 40}
        },
        "series": [{"type": "Candlestick", "data": chart_data, "options": get_series_options(), "markers": get_candle_markers(plot_df, threshold)}]
    }], key=f"dax-{selected_date}")
except Exception as e:
    st.error(f"Render Error: {e}")

# --- PLAYBOOK ---
st.sidebar.markdown("---")
st.sidebar.subheader("Data Event Playbook")
selected_month = st.sidebar.selectbox("Select NFP Month:", list(nfp_playbook.get_nfp_data().keys()))
event_dates = nfp_playbook.get_event_dates(selected_month)

col1, col2, col3 = st.sidebar.columns(3)
if col1.button("Pre"):
    st.session_state.target_date = event_dates['before']
    st.rerun()
if col2.button("NFP"):
    st.session_state.target_date = event_dates['nfp']
    st.rerun()
if col3.button("Post"):
    st.session_state.target_date = event_dates['after']
    st.rerun()