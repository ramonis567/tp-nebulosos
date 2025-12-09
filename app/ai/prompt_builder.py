# app/ai/prompt_builder.py
"""
Prompt builder for the HVAC AI assistant.

Takes the current simulation state + diagnostics + user question and
builds a structured prompt for the Gemini model.
"""

from __future__ import annotations

from textwrap import dedent

from app.simulation.state import SimulationState
from app.ai.diagnostics import Diagnostics


def build_assistant_prompt(
    state: SimulationState,
    T_set: float,
    humidity: float,
    diagnostics: Diagnostics,
    user_question: str,
) -> str:
    """
    Construct a rich, structured prompt for the AI assistant.

    The AI is instructed to act as a professor of fuzzy control and
    HVAC systems, explaining the behavior of the current closed-loop
    system in simple, didactic terms.
    """
    d = diagnostics  # shortcut

    # System state description block
    system_block = f"""
    ESTADO ATUAL DO SISTEMA:
    - Temperatura ambiente atual: {state.temperature:.2f} °C
    - Temperatura de referência (setpoint): {T_set:.2f} °C
    - Erro de temperatura: {d.error_value:.2f} °C (classificado como {d.error_label})
    - Umidade relativa: {humidity:.1f} %
    - Comportamento térmico: {d.comfort_state}
    - Carga térmica (Q_dist): {state.q_dist:.1f} W (regime de carga: {d.load_regime})
    - Potência de refrigeração (Q_cool): {state.q_cool:.1f} W (estado energético: {d.energy_balance_state})
    - Sinal fuzzy de controle (u_fuzzy): {state.fuzzy_output:.1f} %
    - Velocidade efetiva do ventilador (u_fan): {state.fan_speed:.1f} % (regime: {d.fan_regime}, saturado: {d.saturation_flag})
    """

    # Fuzzy controller rules block – based on your error + humidity design
    rules_block = """
    REGRAS PRINCIPAIS DO CONTROLADOR FUZZY (baseado em erro e umidade):

    - Erro grande positivo (PL: ambiente bem mais quente que o setpoint):
        - Se o ar estiver seco → ventilação em nível Médio
        - Se o ar estiver ideal ou úmido → ventilação em nível Alto

    - Erro positivo pequeno (PS: ligeiramente acima do setpoint):
        - Ar seco → ventilação em nível Baixo
        - Ar ideal → ventilação em nível Médio
        - Ar úmido → ventilação em nível Alto

    - Erro quase zero (ZE: próximo ao setpoint):
        - Ventilação em nível Baixo (mantém circulação, evitando gasto excessivo)

    - Erro negativo (NS ou NL: ambiente mais frio que o setpoint):
        - Ventilador Desligado (Off) para evitar super-resfriamento
    """

    # Instructions block
    instructions_block = """
    INSTRUÇÕES PARA VOCÊ (ASSISTENTE IA):

    - Você é um professor de Lógica Fuzzy e Controle de HVAC.
    - Explique o que está acontecendo com base nos dados do ESTADO ATUAL DO SISTEMA.
    - Use as REGRAS PRINCIPAIS DO CONTROLADOR FUZZY para justificar as decisões.
    - Sempre explique:
        - Por que o erro atual leva a esse nível de ventilação.
        - Como a umidade influencia a decisão.
        - Se o sistema está em regime de carga leve, moderado ou pesado.
        - Se o ventilador está saturado ou não.
        - Se o sistema está se aproximando ou se afastando do setpoint.
    - Responda em português, de forma didática e amigável.
    - Use formatação Markdown básica (títulos, listas, negritos) e alguns emojis, mas sem exagero.
    - Mantenha a resposta relativamente curta (máximo ~250 palavras), a menos que o usuário peça mais detalhes.
    - Se a pergunta do usuário for geral sobre Lógica Fuzzy ou HVAC, responda de maneira educativa.
    - Se a pergunta não tiver relação com o sistema, responda educadamente, mas indique que seu foco principal é explicar o sistema de climatização.
    """

    user_block = f"""
    PERGUNTA DO USUÁRIO:
    {user_question}
    """

    prompt = dedent(
        f"""
        Você é um assistente especialista em Controle Fuzzy aplicado a sistemas de climatização (HVAC).
        Seu papel é explicar, em linguagem simples, como o controlador está agindo neste momento
        e o que isso significa para o conforto térmico e o consumo de energia.

        {system_block}

        {rules_block}

        {instructions_block}

        {user_block}

        Responda agora com uma explicação clara, organizada e útil para o usuário.
        """
    ).strip()

    return prompt
