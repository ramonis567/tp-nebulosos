# app/ui/realtime_panel.py
"""
Real-time simulation panel for the HVAC fuzzy controller.

This panel runs the closed-loop simulation step-by-step, giving the
feeling of a live system:
    Fuzzy → Fan → Cooling → Thermal Plant → Temperature.
"""

from __future__ import annotations

import streamlit as st

from app.config import parameters
from app.control.fuzzy_controller import ErrorHumidityFuzzyController
from app.simulation.engine import simulate_step
from app.simulation.history import SimulationHistory
from app.simulation.state import SimulationState
from app.ui.plots import (
    plot_temperature_and_setpoint,
    plot_fan_speeds,
    plot_powers,
)


def _ensure_rt_initialized() -> None:
    """
    Ensure that the real-time simulation state exists in session_state.
    Uses the same configuration parameters as the batch simulation.
    """
    if "rt_initialized" in st.session_state and st.session_state["rt_initialized"]:
        return

    # Read current UI configuration
    T0 = st.session_state.get("T_initial", parameters.T_INITIAL)
    T_set = st.session_state.get("T_set", 24.0)
    humidity = st.session_state.get("humidity", 60.0)
    q_extra = st.session_state.get("q_extra", 3000.0)

    # Initial state & history
    state = SimulationState.initial(T0=T0)
    history = SimulationHistory()
    history.append(state)

    # Fuzzy controller instance
    controller = ErrorHumidityFuzzyController()

    st.session_state["rt_state"] = state
    st.session_state["rt_history"] = history
    st.session_state["rt_controller"] = controller
    st.session_state["rt_running"] = False
    st.session_state["rt_T_set"] = T_set
    st.session_state["rt_humidity"] = humidity
    st.session_state["rt_q_extra"] = q_extra
    st.session_state["rt_initialized"] = True


def _reset_rt_simulation() -> None:
    """
    Reset real-time simulation with current sidebar parameters.
    """
    # Clear initialization flag; next render will reinitialize
    st.session_state["rt_initialized"] = False
    _ensure_rt_initialized()


def _run_rt_steps(n_steps: int) -> None:
    """
    Run a given number of discrete simulation steps in real-time mode.
    """
    state: SimulationState = st.session_state["rt_state"]
    history: SimulationHistory = st.session_state["rt_history"]
    controller: ErrorHumidityFuzzyController = st.session_state["rt_controller"]

    T_set = st.session_state.get("rt_T_set", st.session_state.get("T_set", 24.0))
    humidity = st.session_state.get("rt_humidity", st.session_state.get("humidity", 60.0))
    q_extra = st.session_state.get("rt_q_extra", st.session_state.get("q_extra", 3000.0))

    for _ in range(n_steps):
        state = simulate_step(
            state=state,
            controller=controller,
            T_set=T_set,
            humidity=humidity,
            q_extra=q_extra,
        )
        history.append(state)

    st.session_state["rt_state"] = state
    st.session_state["rt_history"] = history
    st.session_state["rt_T_set"] = T_set
    st.session_state["rt_humidity"] = humidity
    st.session_state["rt_q_extra"] = q_extra


def render_realtime_panel() -> None:
    """
    Main rendering function for the real-time simulation tab.
    """
    st.header("⏱️ Real-Time HVAC Fuzzy Simulation")

    _ensure_rt_initialized()

    state: SimulationState = st.session_state["rt_state"]
    history: SimulationHistory = st.session_state["rt_history"]

    # Top controls
    st.markdown("### ▶ Controls")

    col1, col2, col3, col4 = st.columns(4)

    with col1:
        if st.button("🔄 Reset", use_container_width=True):
            _reset_rt_simulation()
            st.rerun()

    with col2:
        if not st.session_state["rt_running"]:
            if st.button("▶ Start", use_container_width=True):
                st.session_state["rt_running"] = True
                # Run a few steps immediately to start movement
                _run_rt_steps(5)
                st.rerun()
        else:
            if st.button("⏸ Pause", use_container_width=True):
                st.session_state["rt_running"] = False

    with col3:
        if st.button("⏭ Step", use_container_width=True):
            # Single step in paused mode
            _run_rt_steps(1)

    with col4:
        steps_per_cycle = st.slider(
            "Steps per refresh",
            min_value=1,
            max_value=20,
            value=5,
            step=1,
            help="Number of simulation steps executed each time the app refreshes while running.",
        )
        st.session_state["rt_steps_per_cycle"] = steps_per_cycle

    # Current configuration summary
    st.markdown("### ⚙ Current Configuration (Real-Time)")

    T_set = st.session_state.get("rt_T_set", st.session_state.get("T_set", 24.0))
    humidity = st.session_state.get("rt_humidity", st.session_state.get("humidity", 60.0))
    q_extra = st.session_state.get("rt_q_extra", st.session_state.get("q_extra", 3000.0))

    c1, c2, c3, c4 = st.columns(4)
    with c1:
        st.metric("Setpoint (°C)", f"{T_set:.1f}")
    with c2:
        st.metric("Humidity (%)", f"{humidity:.1f}")
    with c3:
        st.metric("Q_extra (W)", f"{q_extra:.0f}")
    with c4:
        sim_minutes = state.time / 60.0
        st.metric("Simulated Time", f"{sim_minutes:.1f} min")

    st.markdown("---")

    # Metrics of current state
    st.markdown("### 📊 Current State")

    e = state.temperature - T_set
    m1, m2, m3 = st.columns(3)
    with m1:
        st.metric("Temperature (°C)", f"{state.temperature:.2f}")
    with m2:
        st.metric("Error (T − T_set)", f"{e:+.2f} °C")
    with m3:
        st.metric("Fan Speed (%)", f"{state.fan_speed:.1f}")

    # Plots with current history
    st.markdown("---")
    st.markdown("### 📈 Real-Time Plots")

    tab_t, tab_fan, tab_power = st.tabs(
        ["Temperature", "Fan & Fuzzy Output", "Powers"]
    )

    with tab_t:
        fig_t = plot_temperature_and_setpoint(history, T_set)
        st.pyplot(fig_t, clear_figure=True)

    with tab_fan:
        fig_fan = plot_fan_speeds(history)
        st.pyplot(fig_fan, clear_figure=True)

    with tab_power:
        fig_p = plot_powers(history)
        st.pyplot(fig_p, clear_figure=True)

    # If running, advance the simulation and rerun
    if st.session_state["rt_running"]:
        steps = st.session_state.get("rt_steps_per_cycle", 5)
        _run_rt_steps(steps)
        st.rerun()
