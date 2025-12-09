"""
Gate 1 – Pure Thermal Plant Model

This module implements the discrete-time thermal difference equation:

    T_{k+1} = T_k + (DT / C_THERMAL) * (Q_dist - Q_cool)

No fan, no fuzzy, no UI logic is allowed here.
This is a pure physical integrator.
"""

from app.config.parameters import DT, C_THERMAL


def update_temperature(T_current: float, Q_dist: float, Q_cool: float) -> float:
    """
    Computes the next temperature using the discrete thermal balance equation.

    Args:
        T_current (float): Current room temperature (°C)
        Q_dist (float): Disturbance thermal power (W)
        Q_cool (float): Cooling thermal power (W)

    Returns:
        float: Updated room temperature (°C)
    """
    dT = (DT / C_THERMAL) * (Q_dist - Q_cool)
    T_next = T_current + dT
    return T_next
