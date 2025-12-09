# app/ai/assistant.py
"""
High-level AI assistant integration for the HVAC fuzzy simulator.

This module wraps:
  - Diagnostics extraction
  - Prompt building
  - Gemini API call
  - Fallback explanation in case of API failure
"""

from __future__ import annotations

import streamlit as st
import google.generativeai as genai

from app.simulation.state import SimulationState
from app.ai.diagnostics import build_diagnostics
from app.ai.prompt_builder import build_assistant_prompt


def generate_ai_explanation(
    state: SimulationState,
    T_set: float,
    humidity: float,
    user_question: str,
) -> str:
    """
    Generate an explanation about the current system state or answer the
    user's question, using Google Gemini when possible.

    Falls back to a deterministic, non-AI explanation if the API call fails.
    """
    diagnostics = build_diagnostics(state, T_set, humidity)

    try:
        # Configure Gemini API from Streamlit secrets
        api_key = st.secrets["GEMINI_API_KEY"]
        genai.configure(api_key=api_key)

        model = genai.GenerativeModel("gemini-2.5-flash")

        prompt = build_assistant_prompt(
            state=state,
            T_set=T_set,
            humidity=humidity,
            diagnostics=diagnostics,
            user_question=user_question,
        )

        response = model.generate_content(prompt)
        return response.text

    except Exception as e:
        # Fallback deterministic explanation – no external AI
        d = diagnostics
        explanation = "⚠️ **Não foi possível conectar ao serviço de IA.**\n\n"
        explanation += "Aqui vai uma explicação básica baseada apenas no modelo interno:\n\n"

        explanation += "### 📊 Estado Atual\n"
        explanation += f"- 🌡️ Temperatura atual: **{state.temperature:.2f} °C**\n"
        explanation += f"- 🎯 Setpoint: **{T_set:.2f} °C**\n"
        explanation += f"- 📉 Erro de temperatura: **{d.error_value:.2f} °C** (classe: `{d.error_label}`)\n"
        explanation += f"- 💧 Umidade: **{humidity:.1f} %**\n"
        explanation += f"- 🔥 Carga térmica total (Q_dist): **{state.q_dist:.1f} W** ({d.load_regime})\n"
        explanation += f"- ❄️ Potência de refrigeração (Q_cool): **{state.q_cool:.1f} W** ({d.energy_balance_state})\n"
        explanation += f"- 🌀 Sinal fuzzy (u_fuzzy): **{state.fuzzy_output:.1f} %**\n"
        explanation += f"- 🧭 Velocidade do ventilador (u_fan): **{state.fan_speed:.1f} %** ({d.fan_regime})\n"
        explanation += f"- 🙂 Conforto térmico: **{d.comfort_state}**\n\n"

        explanation += "### 🧠 Interpretação Básica\n"
        if d.comfort_state == "above comfort":
            explanation += (
                "O ambiente está **mais quente** que o desejado, por isso o "
                "controlador aumenta a velocidade do ventilador para remover calor.\n"
            )
        elif d.comfort_state == "below comfort":
            explanation += (
                "O ambiente está **mais frio** que o desejado, então o ventilador "
                "tende a ficar desligado para evitar super-resfriamento.\n"
            )
        else:
            explanation += (
                "A temperatura está **dentro da faixa de conforto**, então o ventilador "
                "atua de forma mais branda, apenas mantendo circulação de ar.\n"
            )

        if d.energy_balance_state == "deficit":
            explanation += (
                "No momento, a refrigeração **não está vencendo** a carga térmica, "
                "então a temperatura tende a subir ou demorar a descer.\n"
            )
        elif d.energy_balance_state == "surplus":
            explanation += (
                "A potência de refrigeração está **acima** da carga térmica, "
                "fazendo a temperatura tender a cair em direção ao setpoint.\n"
            )
        else:
            explanation += (
                "A carga térmica e a refrigeração estão **mais ou menos balanceadas**, "
                "o que tende a manter a temperatura próxima do valor atual.\n"
            )

        if d.saturation_flag:
            explanation += (
                "\n⚠️ O ventilador está próximo da **saturação máxima**, o que indica "
                "uma condição de carga pesada ou erro grande de temperatura.\n"
            )

        explanation += f"\n_Detalhes técnicos do erro: `{str(e)}`_\n"
        return explanation
