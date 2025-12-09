"""
Gate 5 – Dashboard UI

Defines the Streamlit UI:
  - Sidebar controls (setpoint, humidity, disturbance, duration).
  - Run button.
  - Metrics and plots.
"""
from __future__ import annotations

import statistics

import streamlit as st

from app.ui.realtime_panel import render_realtime_panel
from app.ui.ai_panel import render_ai_panel
from app.config import parameters
from app.simulation.engine import run_simulation
from app.ui.plots import (
    plot_temperature_and_setpoint,
    plot_fan_speeds,
    plot_powers,
)


def _run_simulation_from_ui() -> None:
    """
    Reads UI controls, runs the simulation, and stores results
    in st.session_state.
    """
    T_set = st.session_state["T_set"]
    humidity = st.session_state["humidity"]
    q_extra = st.session_state["q_extra"]
    duration_min = st.session_state["duration_min"]
    T0 = st.session_state["T_initial"]

    duration_s = duration_min * 60.0

    final_state, history = run_simulation(
        duration_s=duration_s,
        T_set=T_set,
        humidity=humidity,
        q_extra=q_extra,
        T0=T0,
    )

    st.session_state["final_state"] = final_state
    st.session_state["history"] = history


def render_dashboard() -> None:
    """
    Main UI rendering function.
    """
    st.title("🌀 HVAC Fuzzy Control Simulator")

    # -------------------------
    # Sidebar – Simulation Controls
    # -------------------------
    st.sidebar.header("Simulation Settings")

    if "T_set" not in st.session_state:
        # Initialize defaults
        st.session_state["T_set"] = 24.0
        st.session_state["humidity"] = 60.0
        st.session_state["q_extra"] = 3000.0
        st.session_state["duration_min"] = 45
        st.session_state["T_initial"] = parameters.T_INITIAL

    st.sidebar.slider(
        "Setpoint Temperature (°C)",
        min_value=18.0,
        max_value=30.0,
        step=0.5,
        key="T_set",
    )

    st.sidebar.slider(
        "Humidity (%RH)",
        min_value=20.0,
        max_value=90.0,
        step=5.0,
        key="humidity",
    )

    st.sidebar.slider(
        "Extra Heat Load Q_extra (W)",
        min_value=0.0,
        max_value=8000.0,
        step=500.0,
        key="q_extra",
        help="Additional thermal load beyond the base load.",
    )

    st.sidebar.slider(
        "Simulation Duration (minutes)",
        min_value=10,
        max_value=120,
        step=5,
        key="duration_min",
    )

    st.sidebar.slider(
        "Initial Temperature (°C)",
        min_value=18.0,
        max_value=35.0,
        step=0.5,
        key="T_initial",
    )

    run_button = st.sidebar.button("▶ Run Simulation", use_container_width=True)

    # -------------------------
    # Run simulation when requested
    # -------------------------
    if run_button:
        _run_simulation_from_ui()

    # -------------------------
    # Main Area – Results
    # -------------------------
    col1, col2, col3 = st.columns(3)

    T_set = st.session_state["T_set"]

    if "final_state" in st.session_state and "history" in st.session_state:
        final_state = st.session_state["final_state"]
        history = st.session_state["history"]

        # Metrics
        with col1:
            st.metric(
                label="Setpoint Temperature",
                value=f"{T_set:.1f} °C",
            )

        with col2:
            delta_T = final_state.temperature - T_set
            st.metric(
                label="Final Temperature",
                value=f"{final_state.temperature:.1f} °C",
                delta=f"{delta_T:+.1f} °C vs setpoint",
            )

        with col3:
            avg_fan = statistics.fmean(history.fan_speed)
            st.metric(
                label="Average Fan Speed",
                value=f"{avg_fan:.1f} %",
                delta=f"Final: {final_state.fan_speed:.1f} %",
            )

        st.markdown("---")

        # Plots
        tab1, tab2, tab3, tab4, tab5 = st.tabs(
            [
                "Temperature (Batch)",
                "Fan & Fuzzy Output (Batch)",
                "Powers (Batch)",
                "🤖 AI Assistant",
                "⏱️ Real-Time Simulation",
            ]
        )


        with tab1:
            fig_temp = plot_temperature_and_setpoint(history, T_set)
            st.pyplot(fig_temp, clear_figure=True)

        with tab2:
            fig_fan = plot_fan_speeds(history)
            st.pyplot(fig_fan, clear_figure=True)

        with tab3:
            fig_powers = plot_powers(history)
            st.pyplot(fig_powers, clear_figure=True)

        with tab4:
            render_ai_panel()

        with tab5:
            render_realtime_panel()


    else:
        with col1:
            st.info("Adjust parameters on the left and click **Run Simulation**.")
