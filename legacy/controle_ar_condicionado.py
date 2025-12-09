import numpy as np
import skfuzzy as fuzz
from skfuzzy import control as ctrl


def criar_sistema_fuzzy():
    """
    Cria e retorna o sistema de controle fuzzy para o ar-condicionado.
    
    Returns:
        tuple: (sistema_ctrl, temperatura, umidade, velocidade_fan)
    """
    # Define os antecedentes (entradas)
    temperatura = ctrl.Antecedent(np.arange(0, 41, 1), 'temperatura')
    umidade = ctrl.Antecedent(np.arange(0, 101, 1), 'umidade')
    
    # Define o consequente (saída)
    velocidade_fan = ctrl.Consequent(np.arange(0, 101, 1), 'velocidade_fan')
    
    # Define as funções de pertinência para temperatura
    temperatura['Baixa'] = fuzz.trimf(temperatura.universe, [0, 0, 20])
    temperatura['Media'] = fuzz.trimf(temperatura.universe, [15, 25, 35])
    temperatura['Alta'] = fuzz.trimf(temperatura.universe, [30, 40, 40])
    
    # Define as funções de pertinência para umidade
    umidade['Seca'] = fuzz.trimf(umidade.universe, [0, 0, 40])
    umidade['Ideal'] = fuzz.trimf(umidade.universe, [30, 50, 70])
    umidade['Umida'] = fuzz.trimf(umidade.universe, [60, 100, 100])
    
    # Define as funções de pertinência para velocidade do fan
    velocidade_fan['Desligado'] = fuzz.trimf(velocidade_fan.universe, [0, 0, 30])
    velocidade_fan['Baixo'] = fuzz.trimf(velocidade_fan.universe, [20, 50, 80])
    velocidade_fan['Alto'] = fuzz.trimf(velocidade_fan.universe, [70, 100, 100])
    
    # Define as regras fuzzy (conjunto completo para cobrir todos os casos)
    regra1 = ctrl.Rule(temperatura['Alta'] & umidade['Umida'], velocidade_fan['Alto'])
    regra2 = ctrl.Rule(temperatura['Alta'] & umidade['Ideal'], velocidade_fan['Alto'])
    regra3 = ctrl.Rule(temperatura['Alta'] & umidade['Seca'], velocidade_fan['Baixo'])
    regra4 = ctrl.Rule(temperatura['Media'], velocidade_fan['Baixo'])
    regra5 = ctrl.Rule(temperatura['Baixa'], velocidade_fan['Desligado'])
    
    # Cria o sistema de controle
    sistema_ctrl = ctrl.ControlSystem([regra1, regra2, regra3, regra4, regra5])
    
    return sistema_ctrl, temperatura, umidade, velocidade_fan


def calcular_ar_condicionado(temp_val, umid_val):
    """
    Calcula a velocidade do fan do ar-condicionado com base na temperatura e umidade.
    
    Args:
        temp_val (float): Valor da temperatura (0-40)
        umid_val (float): Valor da umidade (0-100)
    
    Returns:
        tuple: (velocidade_calculada, objeto_simulacao, temperatura, umidade, velocidade_fan)
    """
    # Cria o sistema fuzzy e obtém as variáveis
    sistema, temperatura, umidade, velocidade_fan = criar_sistema_fuzzy()
    
    # Cria a simulação
    simulacao = ctrl.ControlSystemSimulation(sistema)
    
    # Define os valores de entrada
    simulacao.input['temperatura'] = temp_val
    simulacao.input['umidade'] = umid_val
    
    # Executa a computação
    simulacao.compute()
    
    # Retorna a velocidade calculada, o objeto de simulação e as variáveis fuzzy
    velocidade_calculada = simulacao.output['velocidade_fan']
    
    return velocidade_calculada, simulacao, temperatura, umidade, velocidade_fan


# Exemplo de uso
if __name__ == "__main__":
    # Teste 1: Temperatura alta e umidade alta
    temp = 35
    umid = 80
    velocidade, sim, t, u, v = calcular_ar_condicionado(temp, umid)
    print(f"Temperatura: {temp}°C, Umidade: {umid}%")
    print(f"Velocidade do Fan: {velocidade:.2f}%\n")
    
    # Teste 2: Temperatura média
    temp = 25
    umid = 50
    velocidade, sim, t, u, v = calcular_ar_condicionado(temp, umid)
    print(f"Temperatura: {temp}°C, Umidade: {umid}%")
    print(f"Velocidade do Fan: {velocidade:.2f}%\n")
    
    # Teste 3: Temperatura baixa
    temp = 15
    umid = 40
    velocidade, sim, t, u, v = calcular_ar_condicionado(temp, umid)
    print(f"Temperatura: {temp}°C, Umidade: {umid}%")
    print(f"Velocidade do Fan: {velocidade:.2f}%")
