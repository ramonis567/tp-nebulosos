"""
Guarda o histórico da simulação.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import List

from app.simulation.state import SimulationState


@dataclass
class SimulationHistory:
    time: List[float] = field(default_factory=list)
    temperature: List[float] = field(default_factory=list)
    fan_speed: List[float] = field(default_factory=list)
    fuzzy_output: List[float] = field(default_factory=list)
    q_cool: List[float] = field(default_factory=list)
    q_dist: List[float] = field(default_factory=list)

    def append(self, state: SimulationState) -> None:
        self.time.append(state.time)
        self.temperature.append(state.temperature)
        self.fan_speed.append(state.fan_speed)
        self.fuzzy_output.append(state.fuzzy_output)
        self.q_cool.append(state.q_cool)
        self.q_dist.append(state.q_dist)
