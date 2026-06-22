import nfp_playbook  # Import your new module
import streamlit as st
import pandas as pd
from streamlit_lightweight_charts import renderLightweightCharts

# --- CRITICAL: MUST BE AT THE TOP ---
# This ensures that if a button was clicked, we set the date before the chart loads
if "target_date" in st.session_state:
    selected_date = st.session_state.target_date
else:
    selected_date = None # Will be handled by your default logic later
    
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

def get_candle_markers(plot_df, threshold):
    markers = []
    for _, row in plot_df.iterrows():
        # Filter based on the dynamic threshold selected by the user
        if row['body_size'] >= threshold:
            markers.append({
                "time": row['time'],
                "position": 'aboveBar',
                "color": '#26a69a' if row['Close'] >= row['Open'] else '#ef5350',
                "shape": 'none',
                "text": str(row['body_size'])
            })
    return markers

def add_snapshot_button():
    # Streamlit doesn't natively "take a screenshot" of a JS component, 
    # so we provide a link to the user to use their browser's print-to-file
    # or use a screenshot utility.
    st.sidebar.info("Tip: Use 'Print Screen' or Browser 'Save Page' to capture.")
    if st.sidebar.button("Save chart as JPEG"):
        st.sidebar.warning("Note: Lightweight Charts are rendered in a canvas. "
                           "Right-click the chart area and select 'Save Image As' "
                           "to download the current view directly.")
                           
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
    date_list = list(df['Date'].unique())
    
    # 1. Determine the date (Priority: Session State -> Default to list[0])
    target = st.session_state.get("target_date", date_list[0])
    
    # 2. Force the selectbox to update to the target
    # We find the index of our target, or default to 0
    default_idx = date_list.index(target) if target in date_list else 0
    
    selected_date = st.sidebar.selectbox("Select Date", date_list, index=default_idx)
    
    # 3. If the user changed the date manually via dropdown, clear the session trigger
    # This prevents the button-click from "getting stuck" in session state
    if "target_date" in st.session_state:
        del st.session_state.target_date
        
    plot_df = df[df['Date'] == selected_date].copy()
   
    chart_data = plot_df.rename(columns={'Open': 'open', 'High': 'high', 'Low': 'low', 'Close': 'close'})[['time', 'open', 'high', 'low', 'close']].to_dict(orient="records")
   
    # ADDED DYNAMIC TITLE
    st.title(f"DAX {selected_date} - 5 Minute Chart")
    
    # Sidebar control
    threshold = st.sidebar.selectbox(
        "Show candle numbers for size over:",
        [10, 15, 20, 25, 30, 35, 40]
    )
    
    # ADDED BUTTON
    add_snapshot_button()
    
    renderLightweightCharts([{
        "chart": {
            "width": 1200, "height":700,
            "timeScale": {"timeVisible": True, "secondsVisible": False, "barSpacing": 40}
        },
        "series": [{
            "type": "Candlestick",
            "data": chart_data,
            "options": get_series_options(),
            "markers": get_candle_markers(plot_df, threshold)
        }]
    }], key=f"dax-{selected_date}")
except Exception as e:
    st.error(f"Render Error: {e}")

# Bottom of app.py
st.sidebar.markdown("---")
st.sidebar.subheader("Data Event Playbook")
selected_month = st.sidebar.selectbox("Select NFP Month:", list(nfp_playbook.get_nfp_data().keys()))

event_dates = nfp_playbook.get_event_dates(selected_month)
st.sidebar.write(f"**Analyzing {selected_month}:**")

# Use radio buttons instead of regular buttons
event_choice = st.sidebar.radio(
    "Choose Date Window:",
    options=[event_dates['before'], event_dates['nfp'], event_dates['after']],
    format_func=lambda x: "Pre" if x == event_dates['before'] else ("NFP" if x == event_dates['nfp'] else "Post")
)

# If the user selects a radio option, set the session state and rerun
if event_choice:
    st.session_state.target_date = event_choice
    st.rerun()