"""
Gate 3 – Fuzzy Membership Definitions

Centralizes all fuzzy membership functions for:
- Temperature error (e = T - T_set)
- Humidity
- Fan speed output

This module defines only the fuzzy variables (Antecedents/Consequents).
Rules and inference live in fuzzy_controller.py.
"""

import numpy as np
import skfuzzy as fuzz
from skfuzzy import control as ctrl


def create_error_antecedent() -> ctrl.Antecedent:
    """
    Creates the temperature error antecedent:
        e = T - T_set  (°C)

    Universe: [-10, 10] °C
    Sets:
      NL – Negative Large
      NS – Negative Small
      ZE – Zero
      PS – Positive Small
      PL – Positive Large
    """
    universe = np.arange(-10.0, 10.01, 0.1)
    error = ctrl.Antecedent(universe, "error")

    error["NL"] = fuzz.trimf(error.universe, [-10.0, -10.0, -5.0])
    error["NS"] = fuzz.trimf(error.universe, [-6.0, -3.75, -1.5])
    error["ZE"] = fuzz.trimf(error.universe, [-2.0, 0.0, 2.0])
    error["PS"] = fuzz.trimf(error.universe, [1.5, 3.75, 6.0])
    error["PL"] = fuzz.trimf(error.universe, [5.0, 10.0, 10.0])

    return error


def create_humidity_antecedent() -> ctrl.Antecedent:
    """
    Creates the humidity antecedent (%RH).

    Universe: [0, 100] %
    Sets:
      Dry   – 0 to 40%
      Ideal – 30 to 70%
      Humid – 60 to 100%
    """
    universe = np.arange(0.0, 100.1, 1.0)
    humidity = ctrl.Antecedent(universe, "humidity")

    humidity["Dry"] = fuzz.trimf(humidity.universe, [0.0, 0.0, 40.0])
    humidity["Ideal"] = fuzz.trimf(humidity.universe, [30.0, 50.0, 70.0])
    humidity["Humid"] = fuzz.trimf(humidity.universe, [60.0, 100.0, 100.0])

    return humidity


def create_fan_consequent() -> ctrl.Consequent:
    """
    Creates the fan speed consequent (%).

    Universe: [0, 100] %
    Sets:
      Off    – ~0 to 20%
      Low    – ~20 to 50%
      Medium – ~40 to 75%
      High   – ~70 to 100%
    """
    universe = np.arange(0.0, 100.1, 1.0)
    fan = ctrl.Consequent(universe, "fan")

    fan["Off"] = fuzz.trimf(fan.universe, [0.0, 0.0, 20.0])
    fan["Low"] = fuzz.trimf(fan.universe, [20.0, 35.0, 50.0])
    fan["Medium"] = fuzz.trimf(fan.universe, [40.0, 57.5, 75.0])
    fan["High"] = fuzz.trimf(fan.universe, [70.0, 100.0, 100.0])

    return fan
