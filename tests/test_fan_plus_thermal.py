"""
Gate 2 – Integration Tests: Fan Model + Thermal Model

These tests validate that the fan inertia and cooling power mapping,
when combined with the thermal plant, produce physically consistent
cooling behavior.
"""

from app.plant.thermal_model import update_temperature
from app.plant.fan_model import update_fan_speed, compute_cooling_power
from app.config import parameters


def simulate_closed_loop_without_fuzzy(T0, u_fan0, u_ref, Q_dist, steps):
    """Runs an open-loop simulation with a fixed fan reference (u_ref).

    The fan dynamics follow the inertia model; the plant is driven by the
    resulting cooling power and constant disturbance power.
    """
    T = T0
    u_fan = u_fan0

    for _ in range(steps):
        # Fan inertia towards fixed reference
        u_fan = update_fan_speed(u_fan, u_ref)

        # Cooling power from fan command
        Q_cool = compute_cooling_power(u_fan)

        # Temperature update
        T = update_temperature(T, Q_dist, Q_cool)

    return T, u_fan


def test_fan_and_thermal_cooling_behavior():
    """With a strong cooling command, temperature must fall significantly.

    Scenario:
      - Initial T = 30°C
      - Constant disturbance Q_dist = 5500 W
      - Fan reference u_ref = 100%

    Expectation:
      - Fan ramps up towards 100%
      - Cooling power increases
      - After some minutes, temperature must be well below the initial value.
    """
    T0 = parameters.T_INITIAL
    u_fan0 = 0.0
    u_ref = 100.0

    Q_dist = 5500.0

    # Simulate for 20 minutes
    steps = int(20 * 60 / parameters.DT)

    T_final, u_fan_final = simulate_closed_loop_without_fuzzy(
        T0=T0,
        u_fan0=u_fan0,
        u_ref=u_ref,
        Q_dist=Q_dist,
        steps=steps,
    )

    # Fan should be close to saturation
    assert u_fan_final > 90.0, f"Fan did not ramp up as expected: {u_fan_final}%"

    # Temperature should drop well below the initial value
    assert T_final < T0 - 5.0, (
        f"Cooling effect too small: T_final={T_final}, T_initial={T0}"
    )
