"""
Gate 4 – Simulation State

Defines the dynamic state of the HVAC system at a given time.
"""

from __future__ import annotations

from dataclasses import dataclass

from app.config import parameters


@dataclass
class SimulationState:
    """
    Represents the full dynamic state of the HVAC system.

    Attributes:
        time (float): Current simulation time (s)
        temperature (float): Room temperature (°C)
        fan_speed (float): Actual fan command after inertia (%)
        fuzzy_output (float): Fuzzy controller output (%)
        q_cool (float): Cooling power (W)
        q_dist (float): Disturbance (heat load) power (W)
    """

    time: float
    temperature: float
    fan_speed: float
    fuzzy_output: float
    q_cool: float
    q_dist: float

    @classmethod
    def initial(cls, T0: float | None = None) -> "SimulationState":
        """
        Factory to create an initial state with default values.

        Args:
            T0: Optional initial temperature. If None, uses parameters.T_INITIAL.

        Returns:
            SimulationState: Initialized state at t = 0.
        """
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
