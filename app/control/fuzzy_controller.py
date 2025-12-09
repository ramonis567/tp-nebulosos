"""
Gate 3 – Error-Based Fuzzy HVAC Controller

Implements a fuzzy controller that uses:
  - Temperature error: e = T - T_set
  - Humidity: H (%)

and outputs:
  - Fan speed reference u_fuzzy (%)

Plant dynamics, fan inertia and thermal integrator are handled elsewhere.
"""

from skfuzzy import control as ctrl

from app.control.membership import (
    create_error_antecedent,
    create_humidity_antecedent,
    create_fan_consequent,
)


class ErrorHumidityFuzzyController:
    """
    Error-based fuzzy controller for HVAC fan speed.

    Inputs:
      - T (°C): current temperature
      - T_set (°C): setpoint temperature
      - humidity (%RH): ambient humidity

    Output:
      - u_fuzzy (%): fan speed reference in [0, 100]
    """

    def __init__(self) -> None:
        # Create fuzzy variables
        self.error = create_error_antecedent()
        self.humidity = create_humidity_antecedent()
        self.fan = create_fan_consequent()

        # Build rule base
        self._build_rules()

    def _build_rules(self) -> None:
        """
        Creates the fuzzy rules according to the agreed rule table:

        Error vs Humidity → Fan:

          PL & Dry   → Medium
          PL & Ideal → High
          PL & Humid → High

          PS & Dry   → Low
          PS & Ideal → Medium
          PS & Humid → High

          ZE & any   → Low
          NS & any   → Off
          NL & any   → Off
        """
        e = self.error
        h = self.humidity
        f = self.fan

        rules = []

        # PL (way too hot)
        rules.append(ctrl.Rule(e["PL"] & h["Dry"], f["Medium"]))
        rules.append(ctrl.Rule(e["PL"] & (h["Ideal"] | h["Humid"]), f["High"]))

        # PS (slightly hot)
        rules.append(ctrl.Rule(e["PS"] & h["Dry"], f["Low"]))
        rules.append(ctrl.Rule(e["PS"] & h["Ideal"], f["Medium"]))
        rules.append(ctrl.Rule(e["PS"] & h["Humid"], f["High"]))

        # ZE (on target) – any humidity
        rules.append(ctrl.Rule(e["ZE"], f["Low"]))

        # NS or NL (too cold) – any humidity
        rules.append(ctrl.Rule(e["NS"] | e["NL"], f["Off"]))

        system = ctrl.ControlSystem(rules)
        self._system = system

    def compute_u_fuzzy(self, T: float, T_set: float, humidity: float) -> float:
        """
        Computes the fan reference u_fuzzy (%) given current conditions.

        Args:
            T (float): Current room temperature (°C)
            T_set (float): Temperature setpoint (°C)
            humidity (float): Humidity (%)

        Returns:
            float: Fan speed reference in [0, 100].
        """
        error_value = T - T_set

        sim = ctrl.ControlSystemSimulation(self._system)
        sim.input["error"] = error_value
        sim.input["humidity"] = humidity

        sim.compute()

        u_fuzzy = float(sim.output["fan"])
        # Clamp defensively
        if u_fuzzy < 0.0:
            u_fuzzy = 0.0
        elif u_fuzzy > 100.0:
            u_fuzzy = 100.0

        return u_fuzzy
