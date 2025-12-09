"""
Gate 4 – Simulation History

Stores time-series data for later visualization or analysis.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import List

from app.simulation.state import SimulationState


@dataclass
class SimulationHistory:
    """
    Buffers the evolution of the system over time.

    Attributes:
        time (List[float])
        temperature (List[float])
        fan_speed (List[float])
        fuzzy_output (List[float])
        q_cool (List[float])
        q_dist (List[float])
    """

    time: List[float] = field(default_factory=list)
    temperature: List[float] = field(default_factory=list)
    fan_speed: List[float] = field(default_factory=list)
    fuzzy_output: List[float] = field(default_factory=list)
    q_cool: List[float] = field(default_factory=list)
    q_dist: List[float] = field(default_factory=list)

    def append(self, state: SimulationState) -> None:
        """
        Append a snapshot of the state to the history.
        """
        self.time.append(state.time)
        self.temperature.append(state.temperature)
        self.fan_speed.append(state.fan_speed)
        self.fuzzy_output.append(state.fuzzy_output)
        self.q_cool.append(state.q_cool)
        self.q_dist.append(state.q_dist)
