"""
Módulo de diagnóstico da simulação.

Transforma a leitura dos estados da simulação em diagnósticos categóricos
e quantitativos para interpretação e explicação ao modelo.
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
    if q_dist < 3000.0:
        return "light"
    if q_dist < 5500.0:
        return "moderate"
    return "heavy"


def _classify_comfort_state(T: float, T_set: float) -> ComfortState:
    if T < T_set - 1.0:
        return "below comfort"
    if T > T_set + 1.0:
        return "above comfort"
    return "inside comfort"


def _classify_aggressiveness(u_fuzzy: float) -> Aggressiveness:
    u = u_fuzzy
    if u < 25.0:
        return "weak"
    if u < 60.0:
        return "moderate"
    return "strong"


def _classify_energy_balance(q_cool: float, q_dist: float) -> EnergyBalanceState:
    delta_q = q_cool - q_dist
    if delta_q < -500.0:
        return "deficit"
    if delta_q > 500.0:
        return "surplus"
    return "balanced"


def build_diagnostics(
    state: SimulationState,
    T_set: float,
    humidity: float,
) -> Diagnostics:
    """
    Constroí um objeto de diagnóstico para ler os estados da simulação.
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
