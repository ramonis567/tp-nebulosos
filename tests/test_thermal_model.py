"""
Gate 1 – Tests for the Pure Thermal Plant Model

These tests validate ONLY the physical temperature integrator:

    T_{k+1} = T_k + (DT / C_THERMAL) * (Q_dist - Q_cool)

No fuzzy logic. No fan inertia. No UI.

Run with:
    pytest tests/test_thermal_model.py
"""

import math

from app.plant.thermal_model import update_temperature
from app.config import parameters


def simulate_temperature(T0, Q_dist, Q_cool, steps):
    """
    Runs a simple open-loop thermal simulation for a fixed number of steps.
    """
    T = T0
    for _ in range(steps):
        T = update_temperature(T, Q_dist, Q_cool)
    return T


# =========================================
# TEST 1 — EQUILIBRIUM (NO TEMPERATURE CHANGE)
# =========================================

def test_equilibrium_temperature():
    """
    If Q_dist == Q_cool, temperature must remain constant.
    """
    T0 = parameters.T_INITIAL
    Q_dist = 5000.0
    Q_cool = 5000.0

    steps = 3600  # 1 hour with DT = 1s

    T_final = simulate_temperature(T0, Q_dist, Q_cool, steps)

    assert math.isclose(T_final, T0, abs_tol=0.05), (
        f"Equilibrium failed: T_final={T_final}, expected ~{T0}"
    )


# =========================================
# TEST 2 — NET HEATING (TEMPERATURE MUST RISE)
# =========================================

def test_net_heating_temperature_rise():
    """
    If Q_dist > Q_cool, temperature must rise linearly.
    """
    T0 = parameters.T_INITIAL

    Q_dist = 7000.0
    Q_cool = 2000.0

    net_power = Q_dist - Q_cool  # 5000 W

    steps = 600  # 10 minutes

    T_final = simulate_temperature(T0, Q_dist, Q_cool, steps)

    expected_rise = (net_power / parameters.C_THERMAL) * (parameters.DT * steps)
    expected_T = T0 + expected_rise

    assert math.isclose(T_final, expected_T, abs_tol=0.1), (
        f"Heating failed: T_final={T_final}, expected ~{expected_T}"
    )


# =========================================
# TEST 3 — NET COOLING (TEMPERATURE MUST FALL)
# =========================================

def test_net_cooling_temperature_drop():
    """
    If Q_dist < Q_cool, temperature must fall linearly.
    """
    T0 = parameters.T_INITIAL

    Q_dist = 3000.0
    Q_cool = 12000.0

    net_power = Q_dist - Q_cool  # -9000 W

    steps = 600  # 10 minutes

    T_final = simulate_temperature(T0, Q_dist, Q_cool, steps)

    expected_drop = (net_power / parameters.C_THERMAL) * (parameters.DT * steps)
    expected_T = T0 + expected_drop

    assert math.isclose(T_final, expected_T, abs_tol=0.1), (
        f"Cooling failed: T_final={T_final}, expected ~{expected_T}"
    )
