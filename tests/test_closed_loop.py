"""
Gate 4 – Closed-Loop Integration Tests

Validates the complete loop:
  Fuzzy → Fan Inertia → Cooling Power → Thermal Plant → Temperature.

We check qualitative behavior:
  - From hot initial condition, temperature moves towards setpoint.
  - Higher thermal load leads to higher fan effort and higher final temperature.
"""

from app.config import parameters
from app.simulation.engine import run_simulation


def test_closed_loop_cools_towards_setpoint():
    """
    From an initially hot condition, the closed loop should cool
    the room towards the setpoint and not stay saturated forever.
    """
    T_set = 24.0
    humidity = 60.0
    q_extra = 3000.0  # W

    # Start from a hot room
    T0 = 30.0

    # Simulate 45 minutes
    duration_s = 45 * 60

    final_state, _ = run_simulation(
        duration_s=duration_s,
        T_set=T_set,
        humidity=humidity,
        q_extra=q_extra,
        T0=T0,
    )

    # Temperature must be lower than initial
    assert final_state.temperature < T0 - 3.0, (
        f"Closed loop did not cool enough: "
        f"T_final={final_state.temperature}, T_initial={T0}"
    )

    # Temperature should be reasonably close to setpoint
    assert abs(final_state.temperature - T_set) < 3.0, (
        f"Temperature too far from setpoint: "
        f"T_final={final_state.temperature}, T_set={T_set}"
    )

    # Fan should not be stuck at 100% at the end (some regulation)
    assert final_state.fan_speed < 95.0, (
        f"Fan still saturated at end: u_fan={final_state.fan_speed}"
    )


def test_higher_load_requires_more_fan_and_gives_higher_temperature():
    """
    With higher thermal load (Q_extra), the controller should:
      - Use more fan on average.
      - End at a higher temperature than in a lighter load scenario.
    """
    T_set = 24.0
    humidity = 60.0
    T0 = 30.0
    duration_s = 30 * 60

    # Light load
    q_extra_light = 1000.0
    final_light, history_light = run_simulation(
        duration_s=duration_s,
        T_set=T_set,
        humidity=humidity,
        q_extra=q_extra_light,
        T0=T0,
    )

    # Heavy load
    q_extra_heavy = 5000.0
    final_heavy, history_heavy = run_simulation(
        duration_s=duration_s,
        T_set=T_set,
        humidity=humidity,
        q_extra=q_extra_heavy,
        T0=T0,
    )

    # Final temperature under heavy load should be higher
    assert final_heavy.temperature > final_light.temperature, (
        f"Heavy load final T {final_heavy.temperature} "
        f"not higher than light load final T {final_light.temperature}"
    )

    # Average fan speed under heavy load should be higher
    avg_fan_light = sum(history_light.fan_speed) / len(history_light.fan_speed)
    avg_fan_heavy = sum(history_heavy.fan_speed) / len(history_heavy.fan_speed)

    assert avg_fan_heavy > avg_fan_light, (
        f"Average fan under heavy load ({avg_fan_heavy}) "
        f"not greater than light load ({avg_fan_light})"
    )
