"""Arquivo principal do SIFSM: menu interativo no terminal.

Responsável: Bruno (menu e integração)
Para executar:  python codigo_fonte.py

As funções dos outros membros (Victor, Michelly e Aelton) são chamadas pela função
tentar(). Enquanto uma delas ainda não estiver pronta, o menu avisa
"[EM CONSTRUÇÃO]" e continua funcionando. Quando o módulo for entregue, o menu
passa a usá-lo sozinho, sem precisar mudar este arquivo.
"""

import os
from pathlib import Path

import pandas as pd

import database
from agents import agente_triador
from logic_rules import avaliar_alerta, tabela_verdade
from ml_model import avaliar_modelo, prever_consumo, treinar_modelo
from simulacao_computacional import energia_acumulada, simular_soc
from structures import (buscar_sensor, enfileirar_chamado, impacto_falha,
                        listar_fila, proximo_chamado)

PASTA = Path(__file__).resolve().parent
MARGEM = "    "

# Cenários da simulação (combinar os nomes com a Michelly)
CENARIOS = {"1": ("Operação normal", "normal"),
            "2": ("Tempestade de poeira", "tempestade")}

# Perguntas do cadastro: (campo, pergunta, obrigatório?)
CAMPOS_CADASTRO = [
    ("modulo_id", "ID do módulo (número)", True),
    ("modulo_nome", "Nome do módulo", True),
    ("modulo_tipo", "Tipo do módulo (ex.: habitacao, energia)", True),
    ("modulo_critico", "Módulo crítico? (S/N)", True),
    ("sensor_id", "Código do sensor (ex.: S-HAB-01)", True),
    ("timestamp", "Data/hora (ex.: 2026-10-22T08:00:00)", True),
    ("temperatura_c", "Temperatura (°C)", False),
    ("ocupacao", "Ocupação (nº de pessoas)", False),
    ("geracao_solar_kw", "Geração solar (kW)", False),
    ("consumo_kw", "Consumo (kW)", False),
    ("consumo_alto", "Consumo alto? (S/N)", False),
    ("status", "Status (ex.: ok)", False),
]


# ---------------------------------------------------------------------------
# Funções auxiliares
# ---------------------------------------------------------------------------
def limpar_tela():
    os.system("cls" if os.name == "nt" else "clear")


def pausar():
    input(f"\n{MARGEM}Pressione ENTER para continuar...")


def titulo(texto):
    print(f"\n----- {texto} -----\n")


def ler_texto(pergunta, obrigatorio=False):
    """Pergunta algo ao usuário. Se for obrigatório, pergunta de novo até ele responder."""
    while True:
        resposta = input(f"{MARGEM}{pergunta}: ").strip()
        if resposta != "" or not obrigatorio:
            return resposta
        print(f"{MARGEM}Este campo é obrigatório.")


def ler_sim_nao(pergunta):
    """Pergunta S ou N. Retorna True para sim e False para não."""
    while True:
        resposta = input(f"{MARGEM}{pergunta} (S/N): ").strip().lower()
        if resposta in ["s", "sim"]:
            return True
        if resposta in ["n", "nao", "não"]:
            return False
        print(f"{MARGEM}Digite S ou N.")


def tentar(funcao, *argumentos):
    """Chama a função de outro membro. Se ela ainda não estiver pronta, só avisa."""
    try:
        return funcao(*argumentos)
    except NotImplementedError:
        print(f"{MARGEM}[EM CONSTRUÇÃO] {funcao.__name__}() ainda não foi implementada.")
        return None


def valor(texto):
    """Mostra '-' no lugar de campos vazios."""
    return "-" if texto is None else str(texto)


def mostrar_registro(registro):
    """Mostra um dicionário, uma informação por linha."""
    for campo, conteudo in registro.items():
        print(f"{MARGEM}{campo:<22}: {conteudo}")


def mostrar_tabela(registros, limite=20):
    """Mostra as primeiras leituras em forma de tabela."""
    print(f"{'ID':>5} {'Data/hora':<20} {'Módulo':<16} {'Sensor':<10} "
          f"{'Consumo':>8} {'SoC %':>7} {'Alerta':<6}")
    for r in registros[:limite]:
        print(f"{r['leitura_id']:>5} {r['timestamp']:<20} {r['modulo_nome']:<16} "
              f"{r['sensor_id']:<10} {valor(r['consumo_kw']):>8} "
              f"{valor(r['soc_bateria_pct']):>7} {'SIM' if r['alerta'] else 'não':<6}")
    print(f"\n{len(registros)} registro(s) encontrado(s).", end="")
    if len(registros) > limite:
        print(f" Mostrando os {limite} primeiros.", end="")
    print()


def carregar_df():
    """Lê todas as leituras do banco em uma tabela do pandas (DataFrame)."""
    registros = database.listar_registros()
    if len(registros) == 0:
        print(f"{MARGEM}Banco vazio. Use a opção 1 para carregar o CSV.")
        return None
    return pd.DataFrame(registros)


# ---------------------------------------------------------------------------
# Opções do menu: banco de dados e CRUD
# ---------------------------------------------------------------------------
def opcao_carregar_csv():
    titulo("CARREGAR CSV NO BANCO")
    arquivo = "dados_amostra.csv"
    if (PASTA / "dados_aurora_siger.csv").exists():
        arquivo = "dados_aurora_siger.csv"
    caminho = ler_texto(f"Caminho do CSV [{arquivo}]")
    if caminho == "":
        caminho = arquivo
    caminho = Path(caminho)
    if not caminho.is_absolute():
        caminho = PASTA / caminho
    database.carregar_csv(caminho)


def opcao_cadastrar():
    titulo("CADASTRAR LEITURA")
    print(f"{MARGEM}(nos campos opcionais, aperte ENTER para pular)\n")
    dados = {}
    for campo, pergunta, obrigatorio in CAMPOS_CADASTRO:
        resposta = ler_texto(pergunta, obrigatorio)
        if resposta != "":
            dados[campo] = resposta
    database.cadastrar_registro(dados)


def opcao_listar():
    titulo("LISTAR LEITURAS")
    modulo = ler_texto("Filtrar por ID do módulo (ENTER = todos)")
    if modulo == "":
        registros = database.listar_registros()
    else:
        registros = database.listar_registros({"modulo_id": modulo})
    if len(registros) > 0:
        print()
        mostrar_tabela(registros)


def opcao_alterar():
    titulo("ALTERAR LEITURA")
    id_leitura = ler_texto("ID da leitura", obrigatorio=True)
    encontrados = database.listar_registros({"leitura_id": id_leitura})
    if len(encontrados) == 0:
        return
    print("\nRegistro atual:")
    mostrar_registro(encontrados[0])
    print(f"\n{MARGEM}Digite o novo valor ou aperte ENTER para manter.\n")

    novos = {}
    for campo in database.EDITAVEIS:
        resposta = ler_texto(f"{campo} [{encontrados[0][campo]}]")
        if resposta != "":
            novos[campo] = resposta
    if len(novos) == 0:
        print(f"{MARGEM}Nada foi alterado.")
        return
    database.alterar_registro(id_leitura, novos)


def opcao_excluir():
    titulo("EXCLUIR LEITURA")
    id_leitura = ler_texto("ID da leitura", obrigatorio=True)
    encontrados = database.listar_registros({"leitura_id": id_leitura})
    if len(encontrados) == 0:
        return
    print("\nRegistro encontrado:")
    mostrar_registro(encontrados[0])
    print()
    if ler_sim_nao("Confirma a exclusão?"):
        database.excluir_registro(id_leitura)
    else:
        print(f"{MARGEM}Operação cancelada.")


# ---------------------------------------------------------------------------
# Opções do menu: estruturas de dados (structures.py)
# ---------------------------------------------------------------------------
def opcao_estruturas():
    titulo("ESTRUTURAS DE DADOS")
    print(f"{MARGEM}1 - Buscar sensor por código (tabela hash)")
    print(f"{MARGEM}2 - Gerar chamados de manutenção a partir dos alertas (fila)")
    print(f"{MARGEM}3 - Ver a fila de chamados")
    print(f"{MARGEM}4 - Atender o próximo chamado (fila)")
    print(f"{MARGEM}5 - Impacto da falha de um módulo (grafo + BFS)\n")
    escolha = ler_texto("Escolha")
    print()

    if escolha == "1":
        codigo = ler_texto("Código do sensor", obrigatorio=True)
        sensor = buscar_sensor(codigo)
        if sensor is None:
            print(f"\n{MARGEM}Sensor não encontrado.")
        else:
            print()
            mostrar_registro(sensor)

    elif escolha == "2":
        alertas = database.listar_registros({"alerta": True})
        novos = 0
        for alerta in alertas:
            if enfileirar_chamado(alerta) is not None:
                novos += 1
        print(f"\n{MARGEM}{novos} chamado(s) novo(s) na fila de {len(alertas)} alerta(s).")

    elif escolha == "3":
        fila = listar_fila()
        if len(fila) == 0:
            print(f"{MARGEM}Fila vazia: nenhum chamado pendente.")
        posicao = 1
        for chamado in fila:
            print(f"{MARGEM}{posicao}. prioridade {chamado['prioridade']} | "
                  f"{chamado['modulo_nome']} | sensor {chamado['sensor_id']} | "
                  f"{chamado['timestamp']}")
            posicao += 1

    elif escolha == "4":
        chamado = proximo_chamado()
        if chamado is None:
            print(f"{MARGEM}Fila vazia: nenhum chamado pendente.")
        else:
            print(f"{MARGEM}Atendendo o chamado da leitura {chamado['leitura_id']}:\n")
            mostrar_registro(chamado)

    elif escolha == "5":
        modulo = ler_texto("ID do módulo que falhou", obrigatorio=True)
        afetados = impacto_falha(modulo)
        if len(afetados) == 0:
            print(f"{MARGEM}Nenhum módulo afetado (ou módulo inexistente).")
        for afetado in afetados:
            print(f"{MARGEM}nível {afetado['nivel']}: {afetado['modulo_nome']} "
                  f"(id {afetado['modulo_id']})")
    else:
        print(f"{MARGEM}Opção inválida.")


# ---------------------------------------------------------------------------
# Opções do menu: módulos dos outros membros
# ---------------------------------------------------------------------------
def opcao_regra_booleana():  # Victor
    titulo("REGRA: ALERTA = (consumo_alto E modulo_critico) OU bateria_baixa")
    tabela = tentar(tabela_verdade)
    if tabela is not None:
        for linha in tabela:
            print(f"{MARGEM}{linha}")
    print()
    if ler_sim_nao("Testar uma combinação?"):
        consumo_alto = ler_sim_nao("Consumo alto?")
        modulo_critico = ler_sim_nao("Módulo crítico?")
        bateria_baixa = ler_sim_nao("Bateria baixa?")
        alerta = tentar(avaliar_alerta, consumo_alto, modulo_critico, bateria_baixa)
        if alerta is not None:
            print(f"\n{MARGEM}Resultado: {'ALERTA ACIONADO' if alerta else 'sem alerta'}")


def opcao_simulacao():  # Michelly
    titulo("SIMULAÇÃO DO ESTADO DE CARGA (SoC) DA BATERIA")
    df = carregar_df()
    if df is None:
        return
    for numero, (nome, _) in CENARIOS.items():
        print(f"{MARGEM}{numero} - {nome}")
    escolha = ler_texto("Cenário", obrigatorio=True)
    if escolha not in CENARIOS:
        print(f"{MARGEM}Cenário inválido.")
        return
    resultado = tentar(simular_soc, df, CENARIOS[escolha][1])
    if resultado is not None:
        print()
        print(resultado.head(20).to_string(index=False))

    modulo = ler_texto("\nEnergia acumulada de qual módulo? (ID, ENTER = pular)")
    if modulo != "":
        if not modulo.isdigit():
            print(f"{MARGEM}O ID do módulo deve ser um número.")
        else:
            energia = tentar(energia_acumulada, df, int(modulo))
            if energia is not None:
                print(f"\n{MARGEM}Energia consumida pelo módulo {modulo}: {energia:.2f} kWh")


def opcao_regressao():  # Michelly
    titulo("REGRESSÃO LINEAR: PREVISÃO DE CONSUMO")
    df = carregar_df()
    if df is None:
        return
    modelo = tentar(treinar_modelo, df)
    if modelo is None:
        return
    metricas = tentar(avaliar_modelo, modelo, df)
    if metricas is not None:
        print("\nMétricas do modelo:")
        for nome, resultado in metricas.items():
            print(f"{MARGEM}{nome}: {resultado}")
    previsoes = tentar(prever_consumo, modelo, df)
    if previsoes is not None:
        print("\nPrimeiras previsões:")
        print(previsoes.head(10).to_string(index=False))


def opcao_agentes():  # Aelton
    titulo("AGENTES DE IA (ENTER sem texto volta ao menu)")
    sessao = []  # histórico da conversa (o formato final é definido pelo agents.py)
    while True:
        pedido = ler_texto("Solicitação da tripulação")
        if pedido == "":
            return
        resposta = tentar(agente_triador, pedido, sessao)
        if resposta is None:
            return
        print(f"\n{MARGEM}{resposta}\n")


def opcao_analisar():
    titulo("ANALISAR SUSTENTABILIDADE DA COLÔNIA")

    print("[1/6] Consultando o banco de dados...")
    df = carregar_df()
    if df is None:
        return
    consumo_medio = df.groupby("modulo_nome")["consumo_kw"].mean().sort_values(ascending=False)
    print(f"{MARGEM}{len(df)} leituras de {df['modulo_id'].nunique()} módulos.")
    print(f"{MARGEM}Consumo médio por módulo (kW):")
    print(consumo_medio.round(2).to_string())

    print("\n[2/6] Verificando os alertas (regra booleana)...")
    alertas = df[df["alerta"]]
    print(f"{MARGEM}{len(alertas)} leitura(s) em alerta.")

    print("\n[3/6] Organizando os alertas na fila de manutenção...")
    novos = 0
    for alerta in alertas.to_dict("records"):
        if enfileirar_chamado(alerta) is not None:
            novos += 1
    print(f"{MARGEM}{novos} chamado(s) novo(s) na fila.")

    print("\n[4/6] Simulando o estado de carga da bateria (cenário normal)...")
    tentar(simular_soc, df, CENARIOS["1"][1])

    print("\n[5/6] Estimando o consumo com regressão linear...")
    modelo = tentar(treinar_modelo, df)
    if modelo is not None:
        print(f"{MARGEM}Métricas: {tentar(avaliar_modelo, modelo, df)}")

    print("\n[6/6] Recomendação técnica:")
    if consumo_medio.dropna().empty:
        print(f"{MARGEM}Sem dados de consumo suficientes para recomendar.")
    else:
        print(f"{MARGEM}- Priorizar a eficiência energética do módulo "
              f"'{consumo_medio.idxmax()}' (maior consumo médio: {consumo_medio.max():.2f} kW).")
    if len(alertas) > 0:
        print(f"{MARGEM}- Atender primeiro os chamados de maior prioridade (4 e 5).")
    print(f"{MARGEM}- Toda decisão sugerida deve ser validada por uma pessoa responsável.")
    print(f"{MARGEM}Limitação: os dados são simulados e o modelo linear pode não captar picos.")


# ---------------------------------------------------------------------------
# Menu principal
# ---------------------------------------------------------------------------
def mostrar_menu():
    limpar_tela()
    print("SIFSM - Sistema Integrado de Futuro Sustentável em Marte")
    print("-------------------- AURORA SIGER --------------------\n")
    print(f"{MARGEM} 1 - Carregar dados do CSV no banco")
    print(f"{MARGEM} 2 - Cadastrar leitura")
    print(f"{MARGEM} 3 - Listar leituras")
    print(f"{MARGEM} 4 - Alterar leitura")
    print(f"{MARGEM} 5 - Excluir leitura")
    print(f"{MARGEM} 6 - Regra booleana e tabela verdade")
    print(f"{MARGEM} 7 - Estruturas de dados (hash, fila, grafo)")
    print(f"{MARGEM} 8 - Simulação do estado de carga da bateria")
    print(f"{MARGEM} 9 - Regressão linear (previsão de consumo)")
    print(f"{MARGEM}10 - Agentes de IA")
    print(f"{MARGEM}11 - Analisar sustentabilidade da colônia")
    print(f"{MARGEM} 0 - Sair")


def main():
    while True:
        mostrar_menu()
        escolha = input(f"\n{MARGEM}Escolha -> ").strip()

        if escolha == "0":
            break

        limpar_tela()
        if escolha == "1":
            opcao_carregar_csv()
        elif escolha == "2":
            opcao_cadastrar()
        elif escolha == "3":
            opcao_listar()
        elif escolha == "4":
            opcao_alterar()
        elif escolha == "5":
            opcao_excluir()
        elif escolha == "6":
            opcao_regra_booleana()
        elif escolha == "7":
            opcao_estruturas()
        elif escolha == "8":
            opcao_simulacao()
        elif escolha == "9":
            opcao_regressao()
        elif escolha == "10":
            opcao_agentes()
        elif escolha == "11":
            opcao_analisar()
        else:
            print(f"{MARGEM}Opção inválida. Digite um número do menu.")
        pausar()

    print("\nObrigado por utilizar o SIFSM!")


if __name__ == "__main__":
    main()