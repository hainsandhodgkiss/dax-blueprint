# nfp_playbook.py

def get_nfp_data():
    # Dictionary of NFP release dates for 2026
    return {
        "June 2026": {"before": "2026-07-01", "nfp": "2026-07-02", "after": "2026-07-03"},
        "May 2026": {"before": "2026-06-04", "nfp": "2026-06-05", "after": "2026-06-06"},
        "April 2026": {"before": "2026-05-07", "nfp": "2026-05-08", "after": "2026-05-09"},
    }

def get_event_dates(month_selection):
    events = get_nfp_data()
    return events.get(month_selection)