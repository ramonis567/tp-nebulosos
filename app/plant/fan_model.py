"""
Gate 2 – Fan / Actuator Model

This module implements the discrete-time fan inertia model and the
mapping from fan speed to cooling power.

Equations:
    u_fan[k+1] = u_fan[k] + alpha * (u_fuzzy[k] - u_fan[k])
    alpha = DT / TAU_FAN

    Q_cool[k] = Q_MAX * (u_fan[k] / 100)
"""

from app.config.parameters import DT, TAU_FAN, Q_MAX


def _compute_alpha() -> float:
    """Returns the discrete-time gain alpha for the fan inertia model."""
    return DT / TAU_FAN if TAU_FAN > 0 else 1.0


def update_fan_speed(u_fan_current: float, u_fuzzy: float) -> float:
    """Update fan command with first-order inertial dynamics.

    Args:
        u_fan_current (float): Current fan command (%), typically 0–100.
        u_fuzzy (float): Fuzzy controller output (%), desired fan reference.

    Returns:
        float: Updated fan command (%), saturated between 0 and 100.
    """
    alpha = _compute_alpha()

    # First-order approach to the reference
    u_next = u_fan_current + alpha * (u_fuzzy - u_fan_current)

    # Saturation to physical limits
    if u_next < 0.0:
        u_next = 0.0
    elif u_next > 100.0:
        u_next = 100.0

    return u_next


def compute_cooling_power(u_fan: float) -> float:
    """Maps fan command (%) to cooling power (W).

    Args:
        u_fan (float): Fan command (%), typically 0–100.

    Returns:
        float: Cooling power in watts.
    """
    # Clamp input defensively
    u = max(0.0, min(100.0, u_fan))
    return Q_MAX * (u / 100.0)
