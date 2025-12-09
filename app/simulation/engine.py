"""
Gate 4 – Simulation Engine

Connects:
    Fuzzy Controller → Fan Inertia → Cooling Power → Thermal Plant

Provides:
    - A single simulation step function.
    - A helper to run a full simulation for a given duration.
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
    Runs one discrete simulation step.

    Flow:
      1. Compute error: e = T - T_set (inside fuzzy controller).
      2. Fuzzy control → u_fuzzy.
      3. Fan inertia → fan_speed_next.
      4. Cooling power from fan speed.
      5. Disturbance power from base + extra.
      6. Thermal update → new temperature.
      7. Advance time.

    Args:
        state: Current simulation state.
        controller: Fuzzy controller instance.
        T_set: Temperature setpoint (°C).
        humidity: Humidity (%RH).
        q_extra: Extra disturbance load (W).

    Returns:
        SimulationState: Updated state after one time step.
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
    """
    Runs a full simulation for a given duration.

    Args:
        duration_s: Total simulation time in seconds.
        T_set: Temperature setpoint (°C).
        humidity: Humidity (%RH).
        q_extra: Extra disturbance load (W).
        T0: Optional initial temperature (°C). If None, uses parameters.T_INITIAL.

    Returns:
        (final_state, history)
    """
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
