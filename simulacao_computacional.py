"""Simulação do estado de carga (SoC) da bateria por integração numérica.

SoC(t) = SoC0 + (1/C) * integral de (P_solar - P_consumo) dt

Responsável: Michelly
Critério: Simulação computacional e integração matemática (1,5)
"""
import pandas as pd
import matplotlib.pyplot as plt

# Informações básicas usadas ao longo do código
CAPACIDADE_KWH = 500
SOC_INICIAL = 80
BATERIA_BAIXA = 20
INTERVALO_HORAS = 1

# Informações sobre a simulação de tempestade
DIA_INICIO_TEMPESTADE = 10
DIAS_TEMPESTADE = 3
FATOR_SOL_TEMPESTADE = 0.7

# Informações sobre a simulação de tempestade extrema
DIA_INICIO_TEMPESTADE_EXTREMA = 15
DIAS_TEMPESTADE_EXTREMA = 2
FATOR_SOL_TEMPESTADE_EXTREMA = 0.4

def sol_por_hora(df, cenario):
    """
        Obtém os dados do sol a partir do CSV e a partir disso calcula a geração de energia no dia
    """
    horarios = df["timestamp"].unique() #puxa todos os horários
    sol = []

    for i in range(len(horarios)):
        leituras = df[df["timestamp"] == horarios[i]]
        geracao = list(leituras["geracao_solar_kw"])[0]

        dia = i // 24 #identifica em qual dia está
        if cenario == "tempestade": #verifica qual o cenário simulado do dia
            if dia >= DIA_INICIO_TEMPESTADE and dia < DIA_INICIO_TEMPESTADE + DIAS_TEMPESTADE:
                geracao = geracao * FATOR_SOL_TEMPESTADE
            if dia >= DIA_INICIO_TEMPESTADE_EXTREMA and dia < DIA_INICIO_TEMPESTADE_EXTREMA + DIAS_TEMPESTADE_EXTREMA:
                geracao = geracao * FATOR_SOL_TEMPESTADE_EXTREMA

        sol.append(geracao)

    return sol

def consumo_por_hora(df):
    """
        Obtém os dados de consumo de cada módulo a partir do CSV e a partir disso calcula o total
        de energia consumido
    """
    horarios = df["timestamp"].unique()
    consumo = []

    for hora in horarios:
        leituras = df[df["timestamp"] == hora]
        consumo.append(leituras["consumo_kw"].sum())

    return consumo

def calcular_bateria(sol, consumo):
    """
        Com base na geração do sol e do consumo geral de cada hora, calcula a carga da bateria
        hora a hora pela regra do trapézio, limitada entre 0% e 100%
    """

    bateria = [SOC_INICIAL]

    for i in range(1, len(sol)):
        balanco_anterior = sol[i - 1] - consumo[i - 1]
        balanco_atual = sol[i] - consumo[i]

        energia = (balanco_anterior + balanco_atual) / 2 * INTERVALO_HORAS
        carga = bateria[i - 1] + energia / CAPACIDADE_KWH * 100

        if carga > 100:
            carga = 100
        if carga < 0:
            carga = 0

        bateria.append(round(carga, 2))

    return bateria

def energia_acumulada(df, modulo_id):
    """
        Calcula a energia total consumida por um módulo no período (kWh), somando o consumo
        hora a hora pela regra do trapézio
    """
    leituras = df[df["modulo_id"] == modulo_id]
    if len(leituras) == 0:
        raise ValueError("módulo não encontrado")

    consumo = list(leituras["consumo_kw"])
    energia = 0

    for i in range(1, len(consumo)):
        energia = energia + (consumo[i - 1] + consumo[i]) / 2 * INTERVALO_HORAS

    return energia

def simular_soc(df, cenario="normal"):
    """
        Simula SOC de acordo com o cenário desejado (normal ou tempestade)
    """
    if cenario != "normal" and cenario != "tempestade":
        raise ValueError("cenário deve ser 'normal' ou 'tempestade'")

    sol = sol_por_hora(df, cenario)
    consumo = consumo_por_hora(df)
    bateria = calcular_bateria(sol, consumo)

    resultado = pd.DataFrame({
        "timestamp": df["timestamp"].unique(),
        "geracao_solar_kw": sol,
        "consumo_total_kw": consumo,
        "soc_bateria_pct": bateria
    })
    return resultado

def gerar_graficos(df, simulacao):
    dias = []
    for i in range(len(simulacao)):
        dias.append(i / 24)

    plt.figure(figsize=(10, 5))
    plt.plot(dias, simulacao["soc_bateria_pct"], color="blue", label="Carga da bateria")
    plt.axvspan(DIA_INICIO_TEMPESTADE, DIA_INICIO_TEMPESTADE + DIAS_TEMPESTADE, color="orange", alpha=0.2, label="Tempestade")
    plt.axvspan(DIA_INICIO_TEMPESTADE_EXTREMA, DIA_INICIO_TEMPESTADE_EXTREMA + DIAS_TEMPESTADE_EXTREMA, color="brown", alpha=0.2, label="Tempestade extrema")
    plt.axhline(BATERIA_BAIXA, color="red", linestyle="--", label="Bateria baixa")
    plt.xlabel("Dia")
    plt.ylabel("Carga da bateria (%)")
    plt.title("Carga da bateria da colônia Aurora Siger")
    plt.legend()
    plt.savefig("graficos_ou_imagens/soc_cenarios.png")
    plt.close()

    plt.figure(figsize=(10, 5))
    for modulo_id in range(1, 7):
        leituras = df[df["modulo_id"] == modulo_id]
        nome = list(leituras["modulo_nome"])[0]
        consumo = list(leituras["consumo_kw"])

        acumulado = [0]
        for i in range(1, len(consumo)):
            acumulado.append(acumulado[i - 1] + (consumo[i - 1] + consumo[i]) / 2 * INTERVALO_HORAS)

        plt.plot(dias, acumulado, label=nome)

    plt.xlabel("Dia")
    plt.ylabel("Energia consumida (kWh)")
    plt.title("Consumo acumulado por módulo")
    plt.legend()
    plt.savefig("graficos_ou_imagens/consumo_acumulado.png")
    plt.close()


" TESTES "
if __name__ == "__main__":
    dados = pd.read_csv("dados_aurora_siger.csv")

    print("\n=== TESTE 1: Simulação no cenário normal ===")
    normal = simular_soc(dados, "normal")
    assert len(normal) == 720, "Esperava 720 horas (30 dias x 24 h)"
    assert list(normal["soc_bateria_pct"])[0] == SOC_INICIAL, "A bateria deve começar na carga inicial"
    for carga in normal["soc_bateria_pct"]:
        assert carga >= 0 and carga <= 100, "A carga deve ficar entre 0% e 100%"
    print("✓ Simulação normal válida")

    print("\n=== TESTE 2: Simulação no cenário de tempestade ===")
    tempestade = simular_soc(dados, "tempestade")
    assert len(tempestade) == len(normal), "Os dois cenários devem ter o mesmo número de horas"
    hora_tempestade = DIA_INICIO_TEMPESTADE * 24 + 12
    assert list(tempestade["geracao_solar_kw"])[hora_tempestade] < list(normal["geracao_solar_kw"])[hora_tempestade], "Na tempestade o sol deve ser menor"
    assert tempestade["soc_bateria_pct"].min() < normal["soc_bateria_pct"].min(), "A tempestade deve deixar a bateria mais baixa"
    print("✓ Simulação de tempestade válida")

    print("\n=== TESTE 3: Cenário inválido ===")
    try:
        simular_soc(dados, "chuva")
        assert False, "Cenário inválido deveria dar erro"
    except ValueError:
        print("✓ Cenário inválido bloqueado")

    print("\n=== TESTE 4: Cálculo da bateria (regra do trapézio) ===")
    assert calcular_bateria([0, 0], [17, 17]) == [SOC_INICIAL, 76.6], "Sem sol, a bateria deve descarregar 3,4%"
    assert calcular_bateria([1000, 1000], [0, 0])[1] == 100, "A bateria não pode passar de 100%"
    assert calcular_bateria([0, 0], [1000, 1000])[1] == 0, "A bateria não pode ficar abaixo de 0%"
    print("✓ Cálculo da bateria válido")

    print("\n=== TESTE 5: Energia acumulada por módulo ===")
    for modulo_id in range(1, 7):
        assert energia_acumulada(dados, modulo_id) > 0, "Todo módulo deve ter consumo"
    try:
        energia_acumulada(dados, 99)
        assert False, "Módulo inexistente deveria dar erro"
    except ValueError:
        pass
    print("✓ Energia acumulada válida")

    print("\nEnergia gasta por módulo:")
    horas = len(tempestade) - 1
    for modulo_id in range(1, 7):
        nome = list(dados[dados["modulo_id"] == modulo_id]["modulo_nome"])[0]
        energia = energia_acumulada(dados, modulo_id)
        print(nome, ":", round(energia, 1), "kWh | Média:", round(energia / horas, 2), "kW")

    gerar_graficos(dados, tempestade)
    print("\n✓ Gráficos salvos na pasta graficos_ou_imagens")

