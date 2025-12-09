"""
Gate 5 – Plot Utilities

Provides matplotlib plots for:
  - Temperature vs time with setpoint band.
  - Fan speed vs time (fan & fuzzy output).
  - Cooling and disturbance powers vs time.
"""

from __future__ import annotations

from typing import Iterable

import matplotlib.pyplot as plt

from app.simulation.history import SimulationHistory


def _minutes(time_s: Iterable[float]) -> list[float]:
    """
    Convert seconds to minutes for nicer x-axis.
    """
    return [t / 60.0 for t in time_s]


def plot_temperature_and_setpoint(
    history: SimulationHistory,
    T_set: float,
) -> plt.Figure:
    """
    Plot temperature trajectory and setpoint.

    Args:
        history: SimulationHistory instance.
        T_set: Setpoint temperature (°C).

    Returns:
        Matplotlib Figure.
    """
    t_min = _minutes(history.time)

    fig, ax = plt.subplots(figsize=(8, 4))
    ax.plot(t_min, history.temperature, label="Temperature (°C)", linewidth=2)

    ax.axhline(T_set, linestyle="--", label="Setpoint (°C)")
    ax.fill_between(
        t_min,
        [T_set - 1.0] * len(t_min),
        [T_set + 1.0] * len(t_min),
        alpha=0.1,
        label="Comfort band ±1 °C",
    )

    ax.set_xlabel("Time (minutes)")
    ax.set_ylabel("Temperature (°C)")
    ax.set_title("Room Temperature vs Time")
    ax.grid(True, alpha=0.3)
    ax.legend(loc="best")

    fig.tight_layout()
    return fig


def plot_fan_speeds(history: SimulationHistory) -> plt.Figure:
    """
    Plot fan speed (actual) and fuzzy output (%).

    Args:
        history: SimulationHistory instance.

    Returns:
        Matplotlib Figure.
    """
    t_min = _minutes(history.time)

    fig, ax = plt.subplots(figsize=(8, 4))
    ax.plot(t_min, history.fan_speed, label="Fan Speed (%)", linewidth=2)
    ax.plot(
        t_min,
        history.fuzzy_output,
        label="Fuzzy Output (%)",
        linestyle="--",
        linewidth=1.5,
    )

    ax.set_xlabel("Time (minutes)")
    ax.set_ylabel("Percentage (%)")
    ax.set_title("Fan Speed and Fuzzy Output vs Time")
    ax.grid(True, alpha=0.3)
    ax.legend(loc="best")

    fig.tight_layout()
    return fig


def plot_powers(history: SimulationHistory) -> plt.Figure:
    """
    Plot cooling power and disturbance power vs time.

    Args:
        history: SimulationHistory instance.

    Returns:
        Matplotlib Figure.
    """
    t_min = _minutes(history.time)

    fig, ax = plt.subplots(figsize=(8, 4))
    ax.plot(t_min, history.q_cool, label="Cooling Power Q_cool (W)", linewidth=2)
    ax.plot(
        t_min,
        history.q_dist,
        label="Disturbance Power Q_dist (W)",
        linestyle="--",
        linewidth=1.5,
    )

    ax.set_xlabel("Time (minutes)")
    ax.set_ylabel("Power (W)")
    ax.set_title("Cooling vs Disturbance Power")
    ax.grid(True, alpha=0.3)
    ax.legend(loc="best")

    fig.tight_layout()
    return fig
