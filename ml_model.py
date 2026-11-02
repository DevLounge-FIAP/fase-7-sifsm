"""Regressão linear múltipla para prever o consumo de energia dos módulos.

consumo_previsto = a + b1 * temperatura + b2 * ocupacao + b3 * turno + (consumo base do módulo)

Responsável: Michelly
Critério: Modelagem linear e tomada de decisão (1,0)
"""

import pandas as pd
import matplotlib.pyplot as plt
from sklearn.linear_model import LinearRegression
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
from simulacao_computacional import simular_soc, SOC_INICIAL

INICIO_TURNO = 8
FIM_TURNO = 18
PORCENTAGEM_TESTE = 0.2
RANDOM = 50
CENARIO_CSV = "tempestade"

COLUNAS = ["temperatura_c", "ocupacao", "turno","modulo_1", "modulo_2", "modulo_3", "modulo_4", "modulo_5", "modulo_6"]

def preparar_colunas(df):
    """
        Analisa a coluna de horário e adiciona na cópia do CSV uma coluna chamada "turno" que indica se o horário faz parte
        ou não do período indicado como turno. Também cria uma coluna para cada módulo, indicando de qual módulo é a linha
    """
    df = df.copy()
    turno = []
    for horario in df["timestamp"]:
        hora = int(horario[11:13])
        if hora >= INICIO_TURNO and hora < FIM_TURNO:
            turno.append(1) # faz parte do turno
        else:
            turno.append(0) # não faz parte do turno
    df["turno"] = turno

    for modulo_id in range(1, 7):
        df["modulo_" + str(modulo_id)] = df["modulo_id"] == modulo_id # cria uma coluna de sim ou não para cada módulo

    return df

def treinar_modelo(df):
    """
        Usa 80% dos dados do CSV para treinar o modelo que calcula a fórmula de regressão através da função
        LinearRegression do sklearn e guarda os outros 20% para o teste
    """
    df = preparar_colunas(df)
    X = df[COLUNAS]
    y = df["consumo_kw"]

    X_treino, X_teste, y_treino, y_teste = train_test_split(X, y, test_size=PORCENTAGEM_TESTE, random_state=RANDOM)

    modelo = LinearRegression()
    modelo.fit(X_treino, y_treino)
    return modelo

def avaliar_modelo(modelo, df):
    """
        Usa o restante dos dados do CSV que não foram usados para treinar o modelo (20%) e calcula os erros MAE, RMSE e R²
    """
    df = preparar_colunas(df)
    X = df[COLUNAS]
    y = df["consumo_kw"]

    X_treino, X_teste, y_treino, y_teste = train_test_split(X, y, test_size=PORCENTAGEM_TESTE, random_state=RANDOM)
    previsto = modelo.predict(X_teste)

    mae = mean_absolute_error(y_teste, previsto)
    rmse = mean_squared_error(y_teste, previsto) ** 0.5 # raiz quadrada, pra voltar o erro pra kW
    r2 = r2_score(y_teste, previsto)

    return {"MAE": round(mae, 2), "RMSE": round(rmse, 2), "R2": round(r2, 2)}

def prever_consumo(modelo, df):
    """
        Usa o modelo para prever o consumo de todas as linhas do CSV e retira as colunas criadas para o cálculo
    """
    df = preparar_colunas(df)
    previsto = modelo.predict(df[COLUNAS])

    resultado = df.drop(columns=["turno", "modulo_1", "modulo_2", "modulo_3", "modulo_4", "modulo_5", "modulo_6"])
    resultado["consumo_previsto_kw"] = previsto.round(2)
    return resultado

def mostrar_correlacao(df):
    """
        Através da função corr, indica a relação entre temperatura, ocupação, turno e consumo com números entre -1 e 1
    """
    df = preparar_colunas(df)
    tabela = df[["temperatura_c", "ocupacao", "turno", "consumo_kw"]].corr()
    print(tabela["consumo_kw"].round(2))

def mostrar_coeficientes(modelo):
    """
        Mostra o valor inicial (a) e o peso de cada coluna na fórmula da regressão
    """
    print("Consumo de partida (a):", round(modelo.intercept_, 2), "kW")
    for i in range(len(COLUNAS)):
        print(COLUNAS[i], ":", round(modelo.coef_[i], 2), "kW")

def gerar_graficos(df_previsto):
    """
        Gera os gráficos de consumo real x previsto e dos resíduos da regressão
    """
    real = df_previsto["consumo_kw"]
    previsto = df_previsto["consumo_previsto_kw"]
    maior_consumo_real = real.max()

    plt.figure(figsize=(7, 7))
    plt.scatter(real, previsto, s=5, alpha=0.4)
    plt.plot([0, maior_consumo_real], [0, maior_consumo_real], color="red", linestyle="--", label="Acerto perfeito")
    plt.xlabel("Consumo real (kW)")
    plt.ylabel("Consumo previsto (kW)")
    plt.title("Consumo real x previsto")
    plt.legend()
    plt.savefig("graficos_ou_imagens/real_vs_previsto.png")
    plt.close()

    residuos = real - previsto

    plt.figure(figsize=(10, 5))
    plt.scatter(previsto, residuos, s=5, alpha=0.4)
    plt.axhline(0, color="red", linestyle="--")
    plt.xlabel("Consumo previsto (kW)")
    plt.ylabel("Erro (real - previsto) em kW")
    plt.title("Resíduos da regressão")
    plt.savefig("graficos_ou_imagens/residuos.png")
    plt.close()

def popular_base_dados(modelo, df):
    """
        Preenche as colunas soc_bateria_pct e consumo_previsto_kw do CSV
    """
    resultado = prever_consumo(modelo, df)
    simulacao = simular_soc(df, CENARIO_CSV)

    carga_por_horario = {}
    horarios = list(simulacao["timestamp"])
    cargas = list(simulacao["soc_bateria_pct"])
    for i in range(len(horarios)):
        carga_por_horario[horarios[i]] = cargas[i]

    soc = []
    for horario in resultado["timestamp"]:
        soc.append(carga_por_horario[horario])
    resultado["soc_bateria_pct"] = soc

    resultado.to_csv("dados_aurora_siger.csv", index=False)
    return resultado


if __name__ == "__main__":
    dados = pd.read_csv("dados_aurora_siger.csv")

    print("\n=== Correlação com o consumo ===")
    mostrar_correlacao(dados)

    print("\n=== TESTE 1: Treinamento do modelo ===")
    modelo = treinar_modelo(dados)
    assert len(modelo.coef_) == len(COLUNAS), "Deve ter um coeficiente para cada coluna"
    print("✓ Modelo treinado")

    print("\n=== Coeficientes ===")
    mostrar_coeficientes(modelo)

    print("\n=== TESTE 2: Avaliação do modelo ===")
    metricas = avaliar_modelo(modelo, dados)
    print("MAE:", metricas["MAE"], "kW | RMSE:", metricas["RMSE"], "kW | R²:", metricas["R2"])
    assert metricas["MAE"] >= 0, "O MAE não pode ser negativo"
    assert metricas["RMSE"] >= metricas["MAE"], "O RMSE deve ser maior ou igual ao MAE"
    assert metricas["R2"] > 0.5, "O modelo deve explicar mais da metade do consumo"
    print("✓ Métricas válidas")

    print("\n=== TESTE 3: Previsão do consumo ===")
    previsto = prever_consumo(modelo, dados)
    assert len(previsto) == len(dados), "Deve ter uma previsão para cada linha"
    assert "turno" not in previsto.columns, "As colunas auxiliares não devem ir para o resultado"
    for valor in previsto["consumo_previsto_kw"]:
        assert valor > 0, "O consumo previsto deve ser positivo"
    print("✓ Previsão válida")

    gerar_graficos(previsto)
    print("\n✓ Gráficos salvos na pasta graficos_ou_imagens")

    print("\n=== TESTE 4: Preenchimento da base de dados ===")
    base = popular_base_dados(modelo, dados)
    assert len(base) == len(dados), "A base deve continuar com todas as linhas"
    assert list(base.columns) == list(dados.columns), "As colunas do CSV não podem mudar"
    primeira_hora = base[base["timestamp"] == list(base["timestamp"])[0]]
    for carga in primeira_hora["soc_bateria_pct"]:
        assert carga == SOC_INICIAL, "Os 6 módulos da mesma hora devem ter a mesma carga"
    for valor in base["consumo_previsto_kw"]:
        assert valor != 0.0, "O consumo previsto não pode ficar provisório"
    print("✓ dados_aurora_siger.csv preenchido com o cenário", CENARIO_CSV)
