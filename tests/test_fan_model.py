"""
Gate 2 – Tests for Fan Model (Inertia + Cooling Power Mapping)

These tests validate:
 1) The fan inertia response to a step in u_fuzzy.
 2) The linear mapping from fan speed (%) to cooling power (W).
"""

import math

from app.plant.fan_model import update_fan_speed, compute_cooling_power
from app.config.parameters import DT, TAU_FAN, Q_MAX


def test_fan_inertia_step_response():
    """Fan should smoothly approach the reference, not jump instantly.

    For a step from 0% to 100%, after approximately one time constant
    (tau ≈ 8 s), the discrete first-order system should have reached
    around 60–70% of the final value.
    """
    u_fan = 0.0
    u_ref = 100.0

    steps = int(TAU_FAN / DT)  # approx one time constant

    for _ in range(steps):
        u_fan = update_fan_speed(u_fan, u_ref)

    # After one time constant of a first-order system, we expect ~63% of the step
    assert 60.0 <= u_fan <= 75.0, (
        f"Fan inertia response out of expected range: u_fan={u_fan}"
    )


def test_cooling_power_mapping():
    """Cooling power must scale linearly with fan command."""
    # 0% fan → 0 W
    assert math.isclose(compute_cooling_power(0.0), 0.0, rel_tol=1e-6)

    # 50% fan → 0.5 * Q_MAX
    q_50 = compute_cooling_power(50.0)
    assert math.isclose(q_50, 0.5 * Q_MAX, rel_tol=1e-6)

    # 100% fan → Q_MAX
    q_100 = compute_cooling_power(100.0)
    assert math.isclose(q_100, Q_MAX, rel_tol=1e-6)

    # Defensive clamping: >100% must be treated as 100%
    q_150 = compute_cooling_power(150.0)
    assert math.isclose(q_150, Q_MAX, rel_tol=1e-6)
