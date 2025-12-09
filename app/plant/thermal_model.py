"""
Este módulo implementa o modelo de balanço térmico discreto para a planta.
"""

from app.config.parameters import DT, C_THERMAL


def update_temperature(T_current: float, Q_dist: float, Q_cool: float) -> float:
    """
    Computa a próxima temperatura do ambiente com base no balanço térmico.

    Args:
        T_current (float): Temperatura atual do ambiente (°C).
        Q_dist (float): Carga térmica de distúrbio (W).
        Q_cool (float): Carga térmica de resfriamento (W).

    Returns:
        float: Próxima temperatura do ambiente (°C).
    """
    dT = (DT / C_THERMAL) * (Q_dist - Q_cool)
    T_next = T_current + dT
    return T_next
