"""
Gate 3 – Tests for Error-Based Fuzzy Controller

We validate qualitative behavior, not exact crisp values.
The controller must:
  - Command more fan when hotter.
  - Command more fan under humid conditions.
  - Turn off or very low when too cold.
"""

from app.control.fuzzy_controller import ErrorHumidityFuzzyController


def _ctrl(T: float, T_set: float, H: float) -> float:
    """Helper to call the controller and return u_fuzzy."""
    c = ErrorHumidityFuzzyController()
    return c.compute_u_fuzzy(T=T, T_set=T_set, humidity=H)


def test_hot_humid_more_than_hot_dry():
    """At same high temperature, humid air must demand more fan than dry."""
    T_set = 24.0
    T = 30.0

    u_hot_dry = _ctrl(T=T, T_set=T_set, H=30.0)
    u_hot_humid = _ctrl(T=T, T_set=T_set, H=80.0)

    assert u_hot_humid > u_hot_dry, (
        f"Expected more aggressive cooling for humid air: "
        f"dry={u_hot_dry}, humid={u_hot_humid}"
    )


def test_far_hot_more_than_slightly_hot():
    """Greater positive error must lead to stronger cooling."""
    T_set = 24.0

    u_slight_hot = _ctrl(T=26.0, T_set=T_set, H=50.0)
    u_far_hot = _ctrl(T=30.0, T_set=T_set, H=50.0)

    assert u_far_hot > u_slight_hot, (
        f"Expected far-hot > slight-hot: far={u_far_hot}, slight={u_slight_hot}"
    )


def test_near_set_more_than_cold():
    """Near setpoint must request more fan than clearly cold conditions."""
    T_set = 24.0

    u_near = _ctrl(T=24.0, T_set=T_set, H=50.0)
    u_cold = _ctrl(T=22.0, T_set=T_set, H=50.0)

    assert u_near > u_cold, (
        f"Expected near-set > cold: near={u_near}, cold={u_cold}"
    )

    # Cold should be almost off
    assert u_cold < 25.0, f"Cold case should be near Off: u_cold={u_cold}"


def test_very_cold_turns_off():
    """Strongly negative error should essentially turn the fan off."""
    T_set = 24.0

    u_very_cold = _ctrl(T=18.0, T_set=T_set, H=40.0)
    assert u_very_cold < 15.0, f"Very cold should be Off-ish: {u_very_cold}"


def test_slightly_hot_humid_more_than_slightly_hot_dry():
    """For the same slight positive error, humid should demand more cooling."""
    T_set = 24.0
    T = 26.0

    u_dry = _ctrl(T=T, T_set=T_set, H=30.0)
    u_humid = _ctrl(T=T, T_set=T_set, H=80.0)

    assert u_humid > u_dry, (
        f"Expected humid > dry for same slight positive error: dry={u_dry}, humid={u_humid}"
    )
