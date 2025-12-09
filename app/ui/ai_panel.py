# app/ui/ai_panel.py
"""
Gate 5+ – AI Assistant Panel (Explainable Fuzzy HVAC)

This module defines the Streamlit UI for the AI assistant.
It mirrors the legacy "Tutor IA" behavior, but now explains the
FULL closed-loop HVAC simulation state.
"""

from __future__ import annotations

import streamlit as st

from app.ai.assistant import generate_ai_explanation
from app.simulation.state import SimulationState


def _get_current_context() -> tuple[SimulationState, float, float]:
    """
    Safely retrieve the current simulation context from session_state.

    Returns:
        (state, T_set, humidity)

    Raises:
        RuntimeError if the simulation has not been run yet.
    """
    if "final_state" not in st.session_state:
        raise RuntimeError("Simulation has not been executed yet.")

    state = st.session_state["final_state"]
    T_set = st.session_state["T_set"]
    humidity = st.session_state["humidity"]

    return state, T_set, humidity


def _render_system_summary(state: SimulationState, T_set: float, humidity: float) -> None:
    """
    Renders a compact live textual summary of the current system state.
    """
    error_value = state.temperature - T_set

    st.markdown("### 📊 Current System Snapshot")

    col1, col2, col3 = st.columns(3)

    with col1:
        st.metric("🌡️ Temperature", f"{state.temperature:.2f} °C")
        st.metric("🎯 Setpoint", f"{T_set:.2f} °C")

    with col2:
        st.metric("📉 Error (T − T_set)", f"{error_value:+.2f} °C")
        st.metric("💧 Humidity", f"{humidity:.1f} %")

    with col3:
        st.metric("🌀 Fan Speed", f"{state.fan_speed:.1f} %")
        st.metric("❄️ Cooling Power", f"{state.q_cool:.0f} W")

    st.markdown("---")


def render_ai_panel() -> None:
    """
    Main rendering function for the AI Assistant tab.
    """
    st.header("🤖 AI Assistant — Explainable Fuzzy HVAC")

    # -------------------------
    # Safety check: Has the simulation been run?
    # -------------------------
    try:
        state, T_set, humidity = _get_current_context()
    except RuntimeError:
        st.info("Run the simulation first to enable the AI assistant.")
        return

    # -------------------------
    # Live system snapshot
    # -------------------------
    _render_system_summary(state, T_set, humidity)

    # -------------------------
    # Initialize chat history
    # -------------------------
    if "ai_messages" not in st.session_state:
        st.session_state.ai_messages = []

    # -------------------------
    # Quick explanation buttons
    # -------------------------
    st.markdown("### ⚡ Quick Explanations")

    col_q1, col_q2, col_q3 = st.columns(3)

    if col_q1.button("📖 Explain current state", use_container_width=True):
        question = "Explain the current state of the HVAC system."
        _handle_ai_interaction(question, state, T_set, humidity)

    if col_q2.button("🌀 Why this fan speed?", use_container_width=True):
        question = "Why is the fan operating at this speed right now?"
        _handle_ai_interaction(question, state, T_set, humidity)

    if col_q3.button("🔥 Load vs Cooling", use_container_width=True):
        question = "Is the cooling power sufficient compared to the thermal load?"
        _handle_ai_interaction(question, state, T_set, humidity)

    st.markdown("---")

    # -------------------------
    # Chat history display
    # -------------------------
    st.markdown("### 💬 Conversation")

    for message in st.session_state.ai_messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    # -------------------------
    # User free-form question
    # -------------------------
    user_prompt = st.chat_input("Ask something about the HVAC system...")

    if user_prompt:
        _handle_ai_interaction(user_prompt, state, T_set, humidity)

    # -------------------------
    # Clear conversation button
    # -------------------------
    if st.button("🗑️ Clear AI Conversation"):
        st.session_state.ai_messages = []
        st.rerun()


def _handle_ai_interaction(
    question: str,
    state: SimulationState,
    T_set: float,
    humidity: float,
) -> None:
    """
    Handles a full user → AI interaction loop:
      - Appends user message
      - Calls the AI assistant
      - Appends assistant response
    """
    # Store and show user message
    st.session_state.ai_messages.append(
        {"role": "user", "content": question}
    )

    with st.chat_message("user"):
        st.markdown(question)

    # Generate AI response
    answer = generate_ai_explanation(
        state=state,
        T_set=T_set,
        humidity=humidity,
        user_question=question,
    )

    # Store and show assistant message
    st.session_state.ai_messages.append(
        {"role": "assistant", "content": answer}
    )

    with st.chat_message("assistant"):
        st.markdown(answer)
