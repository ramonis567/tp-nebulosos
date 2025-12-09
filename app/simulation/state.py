"""
Define o estado da simulação em um dado instante.
"""

from __future__ import annotations

from dataclasses import dataclass

from app.config import parameters


@dataclass
class SimulationState:
    time: float
    temperature: float
    fan_speed: float
    fuzzy_output: float
    q_cool: float
    q_dist: float

    @classmethod
    def initial(cls, T0: float | None = None) -> "SimulationState":
        if T0 is None:
            T0 = parameters.T_INITIAL

        return cls(
            time=0.0,
            temperature=T0,
            fan_speed=0.0,
            fuzzy_output=0.0,
            q_cool=0.0,
            q_dist=parameters.Q_BASE + parameters.Q_EXTRA_DEFAULT,
        )
