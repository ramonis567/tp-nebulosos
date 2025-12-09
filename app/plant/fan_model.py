"""
Implementa o modelo de inércia do ventilador e a conversão de comando
do ventilador em potência de resfriamento.
"""

from app.config.parameters import DT, TAU_FAN, Q_MAX


def _compute_alpha() -> float:
    return DT / TAU_FAN if TAU_FAN > 0 else 1.0


def update_fan_speed(u_fan_current: float, u_fuzzy: float) -> float:
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
    # Clamp input defensively
    u = max(0.0, min(100.0, u_fan))
    return Q_MAX * (u / 100.0)
