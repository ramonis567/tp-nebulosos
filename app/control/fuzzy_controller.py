"""
Implementa um controlador fuzzy que utiliza:
- Erro de temperatura: e = T - T_set
- Umidade: H (%)

E produz:
- Referência de velocidade do ventilador u_fuzzy (%)

A dinâmica da planta, inércia do ventilador e integrador térmico são tratados em outro lugar.
"""

from skfuzzy import control as ctrl

from app.control.membership import (
    create_error_antecedent,
    create_humidity_antecedent,
    create_fan_consequent,
)


class ErrorHumidityFuzzyController:
    """
    Controlador fuzzy baseado no erro de temperatura e umidade ambiente.

    Inputs:
      Temperatura atual, Setpoint de temperatura, Umidade ambiente

    Output:
      Referência de velocidade do ventilador u_fuzzy (%)
    """

    def __init__(self) -> None:
        self.error = create_error_antecedent()
        self.humidity = create_humidity_antecedent()
        self.fan = create_fan_consequent()

        self._build_rules()

    def _build_rules(self) -> None:
        """
        Cria as regras fuzzy para o controlador.

        Regras:
        1. Se erro é PL (muito quente) e umidade é Dry,
            então ventilador é Medium
        2. Se erro é PL e umidade é Ideal ou Humid,
            então ventilador é High
        3. Se erro é PS (ligeiramente quente) e umidade é Dry,
            então ventilador é Low
        4. Se erro é PS e umidade é Ideal,
            então ventilador é Medium
        5. Se erro é PS e umidade é Humid,
            então ventilador é High
        6. Se erro é ZE (na meta),
            então ventilador é Low
        7. Se erro é NS (ligeiramente frio) ou NL (muito frio),
            então ventilador é Off
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
        Computa a referência de velocidade do ventilador u_fuzzy (%) dado
        a temperatura atual T (°C), setpoint T_set (°C) e um
        midade ambiente humidity (%).
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
