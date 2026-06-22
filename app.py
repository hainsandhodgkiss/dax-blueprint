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