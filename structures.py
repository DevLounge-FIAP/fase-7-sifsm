"""Estruturas de dados da Aurora Siger: tabela hash, fila e grafo.

Responsável: Bruno

  - Tabela hash (dict): busca de sensores e módulos pelo código em O(1).
  - Fila FIFO (deque): chamados de manutenção gerados pelos alertas, ordenados
    por prioridade na entrada (prioridade 5 = mais urgente).
  - Grafo (lista de adjacência) com busca em largura (BFS): descobre quais
    módulos são afetados quando um módulo falha.
"""

import sqlite3
from collections import deque

import database
indice_sensores = {} 
indice_modulos = {}   


def carregar_indices():
    """Lê o banco e preenche as duas tabelas hash."""
    conexao = None
    try:
        conexao = database.conectar()
        indice_modulos.clear()
        indice_sensores.clear()
        for linha in conexao.execute("SELECT * FROM modulos"):
            modulo = dict(linha)
            modulo["modulo_critico"] = bool(modulo["modulo_critico"])  
            indice_modulos[linha["modulo_id"]] = modulo
        for linha in conexao.execute("SELECT * FROM sensores"):
            sensor = dict(indice_modulos[linha["modulo_id"]])  
            sensor["sensor_id"] = linha["sensor_id"]           
            indice_sensores[linha["sensor_id"]] = sensor
    except sqlite3.Error as erro:
        print(f"[ERRO] Falha no banco de dados: {erro}")
    finally:
        if conexao is not None:
            conexao.close()


def buscar_sensor(codigo):
    """Busca o sensor pelo código. Retorna um dicionário ou None se não existir."""
    if codigo not in indice_sensores:
        carregar_indices()  
    return indice_sensores.get(codigo)


def buscar_modulo(modulo_id):
    """Busca o módulo pelo id. Retorna um dicionário ou None se não existir."""
    try:
        modulo_id = int(modulo_id)
    except (TypeError, ValueError):
        return None
    if modulo_id not in indice_modulos:
        carregar_indices()
    return indice_modulos.get(modulo_id)

fila_chamados = deque()


def enfileirar_chamado(alerta):
    """Cria um chamado a partir de um alerta e coloca na fila, pela prioridade.

    `alerta` é um dicionário com 'leitura_id' e 'prioridade'.
    Os mais urgentes ficam na frente; na mesma prioridade, quem chegou primeiro sai primeiro.
    """
    try:
        prioridade = int(alerta["prioridade"])
        chamado = {"leitura_id": alerta["leitura_id"],
                   "prioridade": prioridade,
                   "modulo_nome": alerta.get("modulo_nome"),
                   "sensor_id": alerta.get("sensor_id"),
                   "timestamp": alerta.get("timestamp")}
    except (KeyError, TypeError, ValueError):
        print("[ERRO] Alerta inválido: precisa ter 'leitura_id' e 'prioridade' numérica.")
        return None
    posicao = len(fila_chamados)
    for i in range(len(fila_chamados)):
        if fila_chamados[i]["prioridade"] < prioridade:
            posicao = i
            break
    fila_chamados.insert(posicao, chamado)
    return chamado


def proximo_chamado():
    """Tira e retorna o chamado da frente da fila (None se a fila estiver vazia)."""
    if len(fila_chamados) == 0:
        return None
    return fila_chamados.popleft()

DEPENDENCIAS = {
    "energia": ["suporte_medico", "agricultura", "laboratorio", "comunicacao"],
    "suporte_medico": ["habitacao"],
    "agricultura": ["habitacao"],
    "laboratorio": [],
    "comunicacao": [],
    "habitacao": [],
}


def impacto_falha(modulo_id):
    """Retorna a lista de módulos (nomes) afetados quando o módulo `modulo_id` falha."""
    modulo = buscar_modulo(modulo_id)
    if modulo is None:
        print(f"[ERRO] Módulo {modulo_id} não encontrado.")
        return []

    origem = modulo["modulo_tipo"]
    visitados = [origem]
    fila = deque([origem])
    while len(fila) > 0:
        atual = fila.popleft()
        for vizinho in DEPENDENCIAS.get(atual, []):
            if vizinho not in visitados:
                visitados.append(vizinho)
                fila.append(vizinho)

    afetados = []
    for tipo in visitados[1:]:
        for outro in indice_modulos.values():
            if outro["modulo_tipo"] == tipo:
                afetados.append(outro["modulo_nome"])
    return afetados

if __name__ == "__main__":
    import os
    import tempfile

    with tempfile.TemporaryDirectory() as pasta_temp:
        database.CAMINHO_BANCO = os.path.join(pasta_temp, "teste.db")

        tipos = ["energia", "suporte_medico", "habitacao", "agricultura",
                 "laboratorio", "comunicacao"]
        for numero, tipo in enumerate(tipos, start=1):
            database.cadastrar_registro({
                "modulo_id": numero, "modulo_nome": tipo.capitalize(), "modulo_tipo": tipo,
                "modulo_critico": True, "sensor_id": f"S-{numero}",
                "timestamp": "2026-10-22T08:00:00"})

        print("\n--- Tabela hash ---")
        print(buscar_sensor("S-1"))
        print(buscar_sensor("S-99"))

        print("\n--- Fila (prioridades enfileiradas: 3, 5, 1, 5) ---")
        for leitura, prioridade in [(1, 3), (2, 5), (3, 1), (4, 5)]:
            enfileirar_chamado({"leitura_id": leitura, "prioridade": prioridade})
        chamado = proximo_chamado()
        while chamado is not None:
            print("Atendendo leitura", chamado["leitura_id"], "- prioridade", chamado["prioridade"])
            chamado = proximo_chamado()

        print("\n--- Grafo e BFS ---")
        print("Falha na energia afeta:", impacto_falha(1))
        print("Falha na habitação afeta:", impacto_falha(3))
        print("Módulo inexistente:", impacto_falha(99))
