"""
Gate 5 – Streamlit Entry Point

Launch with:
    streamlit run app/main.py
"""

import streamlit as st

from app.ui.dashboard import render_dashboard


def main() -> None:
    st.set_page_config(
        page_title="HVAC Fuzzy Simulator",
        page_icon="🌀",
        layout="wide",
    )
    render_dashboard()


if __name__ == "__main__":
    main()
