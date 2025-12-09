"""
Engine de simulação discreta para o sistema térmico com controle fuzzy.
"""

from __future__ import annotations

from typing import Tuple

from app.config import parameters
from app.control.fuzzy_controller import ErrorHumidityFuzzyController
from app.plant.fan_model import update_fan_speed, compute_cooling_power
from app.plant.thermal_model import update_temperature
from app.simulation.state import SimulationState
from app.simulation.history import SimulationHistory


def simulate_step(
    state: SimulationState,
    controller: ErrorHumidityFuzzyController,
    T_set: float,
    humidity: float,
    q_extra: float,
) -> SimulationState:
    """
    Roda uma etapa discreta de simulação.

    Fluxo:

    1 - Calcular erro: e = T - T_set (dentro do controlador fuzzy).
    2 - Controle fuzzy → u_fuzzy.
    3 - Inércia do ventilador → fan_speed_next.
    4 - Potência de resfriamento a partir da velocidade do ventilador.
    5 - Potência de perturbação a partir da base + extra.
    6 - Atualização térmica → nova temperatura.
    7 - Avançar o tempo.

    Retorna:
        SimulationState: Atualizado após execução.
    """
    # 1–2. Fuzzy control
    u_fuzzy = controller.compute_u_fuzzy(
        T=state.temperature,
        T_set=T_set,
        humidity=humidity,
    )

    # 3. Fan inertia
    fan_next = update_fan_speed(
        u_fan_current=state.fan_speed,
        u_fuzzy=u_fuzzy,
    )

    # 4. Cooling power
    q_cool = compute_cooling_power(fan_next)

    # 5. Disturbance power (constant in this step)
    q_dist = parameters.Q_BASE + q_extra

    # 6. Thermal update
    T_next = update_temperature(
        T_current=state.temperature,
        Q_dist=q_dist,
        Q_cool=q_cool,
    )

    # 7. Advance time
    t_next = state.time + parameters.DT

    # New state
    return SimulationState(
        time=t_next,
        temperature=T_next,
        fan_speed=fan_next,
        fuzzy_output=u_fuzzy,
        q_cool=q_cool,
        q_dist=q_dist,
    )


def run_simulation(
    duration_s: float,
    T_set: float,
    humidity: float,
    q_extra: float,
    T0: float | None = None,
) -> Tuple[SimulationState, SimulationHistory]:
    controller = ErrorHumidityFuzzyController()
    state = SimulationState.initial(T0=T0)
    history = SimulationHistory()

    n_steps = int(duration_s / parameters.DT)

    # Record initial state
    history.append(state)

    for _ in range(n_steps):
        state = simulate_step(
            state=state,
            controller=controller,
            T_set=T_set,
            humidity=humidity,
            q_extra=q_extra,
        )
        history.append(state)

    return state, history
