"""
Global configuration parameters for Gate 1 & Gate 2.
All numeric values are centralized here to avoid magic numbers
inside the physical models and tests.
"""

# =============================
# Simulation Time Parameters
# =============================

# Discrete simulation time step (seconds)
DT = 1.0

# =============================
# Thermal Plant Parameters
# =============================

# Effective thermal capacitance of the 200 m² industrial room (J/K)
# Represents air + walls + equipment thermal inertia
C_THERMAL = 1.0e6

# Initial room temperature (°C)
T_INITIAL = 30.0

# =============================
# Disturbance Parameters (Gate 1+)
# =============================

# Base thermal load (W)
Q_BASE = 2500.0

# Extra disturbance load (W) – can be overridden in tests or UI later
Q_EXTRA_DEFAULT = 0.0

# =============================
# Cooling Power Parameters (Gate 1 & Gate 2)
# =============================

# Fixed cooling power used in pure plant-only tests (Gate 1)
Q_COOL_DEFAULT = 0.0

# Maximum cooling capacity of the HVAC unit (W) – used in Gate 2+
Q_MAX = 18_000.0

# =============================
# Fan / Actuator Parameters (Gate 2)
# =============================

# Fan time constant (seconds) – how fast the fan reacts to changes
TAU_FAN = 10.0
