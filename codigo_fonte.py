"""Arquivo principal do SIFSM: menu interativo no terminal.

Responsável: Bruno (menu e integração)
Para executar:  python codigo_fonte.py
"""

import os

import pandas as pd

import database
from structures import buscar_sensor, enfileirar_chamado, impacto_falha, proximo_chamado

margem = " " * 4

# ---------------------------------------------------------------------------
# STUBS: funções dos outros membros que ainda não foram entregues.
# Têm as mesmas assinaturas do contrato de interfaces.
# Na integração (03 e 04/11), apague os stubs e troque pelos imports reais:
#   from logic_rules import avaliar_alerta, tabela_verdade
#   from simulacao_computacional import simular_soc
#   from ml_model import treinar_modelo, avaliar_modelo, prever_consumo
#   from agents import agente_triador
# ---------------------------------------------------------------------------
def tabela_verdade():  # Victor
    print(margem + "[STUB] logic_rules ainda não foi entregue.")
    return []


def avaliar_alerta(consumo_alto, modulo_critico, bateria_baixa):  # Victor
    print(margem + "[STUB] logic_rules ainda não foi entregue.")
    return False


def simular_soc(df, cenario):  # Michelly
    print(margem + "[STUB] simulacao_computacional ainda não foi entregue.")
    return df


def treinar_modelo(df):  # Michelly
    print(margem + "[STUB] ml_model ainda não foi entregue.")
    return None


def avaliar_modelo(modelo, df):  # Michelly
    return {}


def prever_consumo(modelo, df):  # Michelly
    return df


def agente_triador(solicitacao, sessao):  # Aelton
    return "[STUB] agents ainda não foi entregue."


# ---------------------------------------------------------------------------
# Perguntas do cadastro: (coluna, pergunta)
# ---------------------------------------------------------------------------
CAMPOS = [("modulo_id", "ID do módulo"),
          ("modulo_nome", "Nome do módulo"),
          ("modulo_tipo", "Tipo do módulo (ex.: energia)"),
          ("modulo_critico", "Módulo crítico? (S/N)"),
          ("sensor_id", "Código do sensor (ex.: S-ENE-01)"),
          ("timestamp", "Data/hora (ex.: 2026-10-22T08:00:00)"),
          ("temperatura_c", "Temperatura (°C)"),
          ("ocupacao", "Ocupação (nº de pessoas)"),
          ("geracao_solar_kw", "Geração solar (kW)"),
          ("consumo_kw", "Consumo (kW)"),
          ("consumo_alto", "Consumo alto? (S/N)"),
          ("status", "Status (ex.: ok)")]


# ---------------------------------------------------------------------------
# Opções do menu
# ---------------------------------------------------------------------------
def carregar_csv():
    print("----- CARREGAR CSV NO BANCO -----\n")
    arquivo = input(margem + "Nome do arquivo CSV (ex.: dados_amostra.csv): ").strip()
    database.carregar_csv(arquivo)


def cadastrar():
    print("----- CADASTRAR LEITURA -----\n")
    dados = {}
    for coluna, pergunta in CAMPOS:
        dados[coluna] = input(margem + pergunta + ": ")
    database.cadastrar_registro(dados)


def listar():
    print("----- LISTAR LEITURAS -----\n")
    modulo = input(margem + "ID do módulo (ENTER = todos): ").strip()
    if modulo == "":
        registros = database.listar_registros()
    else:
        registros = database.listar_registros({"modulo_id": modulo})
    if len(registros) > 0:
        tabela = pd.DataFrame(registros)
        print(tabela[["leitura_id", "timestamp", "modulo_nome", "sensor_id",
                      "consumo_kw", "alerta", "prioridade"]])


def alterar():
    print("----- ALTERAR LEITURA -----\n")
    id_leitura = input(margem + "ID da leitura: ").strip()
    registros = database.listar_registros({"leitura_id": id_leitura})
    if len(registros) == 0:
        return
    print(margem + "Digite o novo valor ou ENTER para manter.\n")
    novos = {}
    for coluna in database.EDITAVEIS:
        valor = input(margem + f"{coluna} [{registros[0][coluna]}]: ").strip()
        if valor != "":
            novos[coluna] = valor
    if len(novos) == 0:
        print(margem + "Nada foi alterado.")
    else:
        database.alterar_registro(id_leitura, novos)


def excluir():
    print("----- EXCLUIR LEITURA -----\n")
    id_leitura = input(margem + "ID da leitura: ").strip()
    database.excluir_registro(id_leitura)


def regra_booleana():
    print("----- REGRA: ALERTA = (consumo_alto E modulo_critico) OU bateria_baixa -----\n")
    for linha in tabela_verdade():
        print(margem, linha)
    consumo_alto = input(margem + "Consumo alto? (S/N): ").strip().lower() == "s"
    modulo_critico = input(margem + "Módulo crítico? (S/N): ").strip().lower() == "s"
    bateria_baixa = input(margem + "Bateria baixa? (S/N): ").strip().lower() == "s"
    if avaliar_alerta(consumo_alto, modulo_critico, bateria_baixa):
        print(margem + "Resultado: ALERTA ACIONADO")
    else:
        print(margem + "Resultado: sem alerta")
    print("\n" + margem + "Circuito equivalente no Tinkercad (Arduino): potenciômetro = consumo,")
    print(margem + "botão = módulo crítico, sensor de luz = bateria, LED = alerta.")
    print(margem + "Veja circuito_logico.png ou link_tinkercad.txt.")


def estruturas():
    print("----- ESTRUTURAS DE DADOS -----\n")
    print(margem + "1 - Buscar sensor por código (tabela hash)")
    print(margem + "2 - Gerar chamados de manutenção a partir dos alertas (fila)")
    print(margem + "3 - Atender o próximo chamado (fila)")
    print(margem + "4 - Módulos afetados por uma falha (grafo + BFS)\n")
    escolha = input(margem + "Escolha -> ").strip()
    print()

    match escolha:
        case "1":
            codigo = input(margem + "Código do sensor: ").strip()
            sensor = buscar_sensor(codigo)
            if sensor is None:
                print(margem + "Sensor não encontrado.")
            else:
                print(sensor)
        case "2":
            alertas = database.listar_registros({"alerta": True})
            for alerta in alertas:
                enfileirar_chamado(alerta)
            print(margem + f"{len(alertas)} chamado(s) colocado(s) na fila.")
        case "3":
            chamado = proximo_chamado()
            if chamado is None:
                print(margem + "Fila vazia: nenhum chamado pendente.")
            else:
                print(margem + "Atendendo o chamado:", chamado)
        case "4":
            modulo = input(margem + "ID do módulo que falhou: ").strip()
            afetados = impacto_falha(modulo)
            print(margem + "Módulos afetados:", afetados)
        case _:
            print(margem + "Opção inválida.")


def simulacao():
    print("----- SIMULAÇÃO DO ESTADO DE CARGA DA BATERIA -----\n")
    print(margem + "1 - Operação normal")
    print(margem + "2 - Tempestade de poeira\n")
    escolha = input(margem + "Cenário -> ").strip()
    cenario = "normal" if escolha == "1" else "tempestade"
    df = pd.DataFrame(database.listar_registros())
    print(simular_soc(df, cenario).head(10))


def regressao():
    print("----- REGRESSÃO LINEAR: PREVISÃO DE CONSUMO -----\n")
    df = pd.DataFrame(database.listar_registros())
    modelo = treinar_modelo(df)
    print(margem + "Métricas:", avaliar_modelo(modelo, df))
    print(prever_consumo(modelo, df).head(10))


def agentes():
    print("----- AGENTES DE IA (ENTER sem texto volta ao menu) -----\n")
    sessao = []
    while True:
        pedido = input(margem + "Solicitação da tripulação: ").strip()
        if pedido == "":
            break
        print(margem + agente_triador(pedido, sessao))


def analisar_sustentabilidade():
    print("----- ANALISAR SUSTENTABILIDADE DA COLÔNIA -----\n")

    # 1. Consulta o banco e identifica as leituras de consumo
    registros = database.listar_registros()
    if len(registros) == 0:
        print(margem + "Banco vazio. Carregue o CSV (opção 1).")
        return
    consumos = [r["consumo_kw"] for r in registros if r["consumo_kw"] is not None]
    media = sum(consumos) / len(consumos) if len(consumos) > 0 else 0
    print(margem + f"1. {len(registros)} leituras no banco. Consumo médio: {media:.2f} kW")

    # 2. Regra booleana: as leituras em alerta
    alertas = [r for r in registros if r["alerta"]]
    print(margem + f"2. {len(alertas)} leitura(s) em alerta (regra booleana).")

    # 3. Estrutura de dados: os alertas viram chamados na fila
    for alerta in alertas:
        enfileirar_chamado(alerta)
    print(margem + f"3. {len(alertas)} chamado(s) organizado(s) na fila por prioridade.")

    # 4. Simulação e 5. regressão linear
    df = pd.DataFrame(registros)
    print(margem + "4. Simulação do estado de carga:")
    simular_soc(df, "normal")
    print(margem + "5. Regressão linear:")
    modelo = treinar_modelo(df)
    print(margem + "   Métricas:", avaliar_modelo(modelo, df))

    # 6. Recomendação técnica
    print(margem + "6. Recomendação técnica:")
    if len(alertas) > 0:
        print(margem + "   - Atender primeiro os chamados de maior prioridade.")
    print(margem + "   - Reduzir o desperdício de energia nos módulos de maior consumo.")
    print(margem + "   - A decisão final deve ser validada por uma pessoa responsável.")
    print(margem + "Limitações: os dados são simulados e o modelo linear é simples.")


# ---------------------------------------------------------------------------
# Menu principal
# ---------------------------------------------------------------------------
while True:
    os.system("cls" if os.name == "nt" else "clear")  # limpa a tela
    print("---- SIFSM - AURORA SIGER ----")
    print("""
    1 - Carregar dados do CSV no banco
    2 - Cadastrar leitura
    3 - Listar leituras
    4 - Alterar leitura
    5 - Excluir leitura
    6 - Regra booleana e tabela verdade
    7 - Estruturas de dados (hash, fila, grafo)
    8 - Simulação do estado de carga da bateria
    9 - Regressão linear (previsão de consumo)
    10 - Agentes de IA
    11 - Analisar sustentabilidade da colônia
    0 - SAIR
    """)
    escolha = input(margem + "Escolha -> ").strip()
    if escolha == "0":
        break

    os.system("cls" if os.name == "nt" else "clear")
    match escolha:
        case "1": carregar_csv()
        case "2": cadastrar()
        case "3": listar()
        case "4": alterar()
        case "5": excluir()
        case "6": regra_booleana()
        case "7": estruturas()
        case "8": simulacao()
        case "9": regressao()
        case "10": agentes()
        case "11": analisar_sustentabilidade()
        case _: print(margem + "Digite um número entre 0 e 11.")

    input("\n" + margem + "Pressione ENTER")  # pausa para ler as mensagens

print("Obrigado por utilizar o SIFSM!")
