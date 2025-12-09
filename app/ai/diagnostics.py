# app/ai/diagnostics.py
"""
Diagnostics module for the HVAC fuzzy simulator.

Transforms raw simulation state into semantic labels that can be used
by the AI assistant to explain the system behavior in human terms.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Literal, Dict

from app.simulation.state import SimulationState
from app.config import parameters


ErrorLabel = Literal["NL", "NS", "ZE", "PS", "PL"]
FanRegime = Literal["off", "low", "medium", "high", "saturated"]
LoadRegime = Literal["light", "moderate", "heavy"]
ComfortState = Literal["below comfort", "inside comfort", "above comfort"]
Aggressiveness = Literal["weak", "moderate", "strong"]
EnergyBalanceState = Literal["deficit", "balanced", "surplus"]


@dataclass
class Diagnostics:
    error_value: float
    error_label: ErrorLabel
    fan_regime: FanRegime
    load_regime: LoadRegime
    comfort_state: ComfortState
    control_aggressiveness: Aggressiveness
    energy_balance_state: EnergyBalanceState
    saturation_flag: bool

    def as_dict(self) -> Dict[str, object]:
        return {
            "error_value": self.error_value,
            "error_label": self.error_label,
            "fan_regime": self.fan_regime,
            "load_regime": self.load_regime,
            "comfort_state": self.comfort_state,
            "control_aggressiveness": self.control_aggressiveness,
            "energy_balance_state": self.energy_balance_state,
            "saturation_flag": self.saturation_flag,
        }


def _classify_error_label(error_value: float) -> ErrorLabel:
    """
    Classify temperature error according to the fuzzy universe:
        NL, NS, ZE, PS, PL
    """
    e = error_value
    if e <= -5.0:
        return "NL"
    if -5.0 < e <= -1.5:
        return "NS"
    if -1.5 < e < 1.5:
        return "ZE"
    if 1.5 <= e < 5.0:
        return "PS"
    return "PL"


def _classify_fan_regime(fan_speed: float) -> FanRegime:
    """
    Classify fan speed into qualitative regimes.
    """
    u = fan_speed
    if u < 5.0:
        return "off"
    if u < 30.0:
        return "low"
    if u < 60.0:
        return "medium"
    if u < 90.0:
        return "high"
    return "saturated"


def _classify_load_regime(q_dist: float) -> LoadRegime:
    """
    Classify total disturbance load as light / moderate / heavy.

    Uses rough thresholds around typical office/industrial ranges.
    """
    if q_dist < 3000.0:
        return "light"
    if q_dist < 5500.0:
        return "moderate"
    return "heavy"


def _classify_comfort_state(T: float, T_set: float) -> ComfortState:
    """
    Compare current temperature with comfort band around setpoint.
    """
    if T < T_set - 1.0:
        return "below comfort"
    if T > T_set + 1.0:
        return "above comfort"
    return "inside comfort"


def _classify_aggressiveness(u_fuzzy: float) -> Aggressiveness:
    """
    Classify fuzzy output level.
    """
    u = u_fuzzy
    if u < 25.0:
        return "weak"
    if u < 60.0:
        return "moderate"
    return "strong"


def _classify_energy_balance(q_cool: float, q_dist: float) -> EnergyBalanceState:
    """
    Compare cooling and disturbance power to indicate whether the system
    is currently winning or losing the thermal battle.
    """
    delta_q = q_cool - q_dist
    if delta_q < -500.0:
        return "deficit"
    if delta_q > 500.0:
        return "surplus"
    return "balanced"


def build_diagnostics(
    state: SimulationState,
    T_set: float,
    humidity: float,  # kept for possible future use in diagnostics
) -> Diagnostics:
    """
    Build a Diagnostics object from the current simulation state.

    Args:
        state: Current SimulationState.
        T_set: Temperature setpoint (°C).
        humidity: Ambient humidity (%). Currently not used for thresholds,
                  but included for future refinement.

    Returns:
        Diagnostics: semantic interpretation of the control situation.
    """
    error_value = state.temperature - T_set
    error_label = _classify_error_label(error_value)
    fan_regime = _classify_fan_regime(state.fan_speed)
    load_regime = _classify_load_regime(state.q_dist)
    comfort_state = _classify_comfort_state(state.temperature, T_set)
    control_aggressiveness = _classify_aggressiveness(state.fuzzy_output)
    energy_balance_state = _classify_energy_balance(state.q_cool, state.q_dist)
    saturation_flag = fan_regime == "saturated"

    return Diagnostics(
        error_value=error_value,
        error_label=error_label,
        fan_regime=fan_regime,
        load_regime=load_regime,
        comfort_state=comfort_state,
        control_aggressiveness=control_aggressiveness,
        energy_balance_state=energy_balance_state,
        saturation_flag=saturation_flag,
    )
