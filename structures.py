"""Estruturas de dados da Aurora Siger: tabela hash, fila e grafo.

Responsável: Bruno

Estruturas usadas e por quê:
  - Tabela hash (dict): achar um sensor ou módulo pelo código na hora (O(1)),
    sem percorrer todas as leituras do banco.
  - Fila (deque): chamados de manutenção. Os mais urgentes (prioridade 5) ficam na
    frente e, se a prioridade for igual, quem chegou primeiro é atendido primeiro (FIFO).
  - Grafo (lista de adjacência) + BFS: descobre quais módulos são afetados quando
    um módulo falha.
"""

import sqlite3
from collections import deque

import database

# ---------------------------------------------------------------------------
# 1. TABELA HASH (dict)
# ---------------------------------------------------------------------------
indice_sensores = {}  # código do sensor -> dados do sensor e do módulo
indice_modulos = {}   # id do módulo -> dados do módulo


def carregar_indices():
    """Lê o banco e preenche as tabelas hash. Retorna True se deu certo."""
    conexao = None
    modulos = {}
    sensores = {}
    try:
        conexao = database.conectar()
        for linha in conexao.execute("SELECT * FROM modulos"):
            modulos[linha["modulo_id"]] = {
                "modulo_id": linha["modulo_id"],
                "modulo_nome": linha["modulo_nome"],
                "modulo_tipo": linha["modulo_tipo"],
                "modulo_critico": bool(linha["modulo_critico"]),
            }
        for linha in conexao.execute("SELECT * FROM sensores"):
            sensor = dict(modulos[linha["modulo_id"]])  # copia os dados do módulo
            sensor["sensor_id"] = linha["sensor_id"]
            sensores[linha["sensor_id"]] = sensor
    except sqlite3.Error as erro:
        print(f"[ERRO] Não foi possível ler o banco: {erro}")
        return False
    else:
        indice_modulos.clear()
        indice_modulos.update(modulos)
        indice_sensores.clear()
        indice_sensores.update(sensores)
        return True
    finally:
        if conexao is not None:
            conexao.close()


def buscar_sensor(codigo):
    """Busca um sensor pelo código. Retorna um dicionário ou None se não existir."""
    codigo = str(codigo).strip()
    if codigo not in indice_sensores:
        carregar_indices()  # pode ser um sensor cadastrado há pouco: recarrega
    return indice_sensores.get(codigo)


def buscar_modulo(modulo_id):
    """Busca um módulo pelo id. Retorna um dicionário ou None se não existir."""
    try:
        modulo_id = int(modulo_id)
    except (TypeError, ValueError):
        return None
    if modulo_id not in indice_modulos:
        carregar_indices()
    return indice_modulos.get(modulo_id)


# ---------------------------------------------------------------------------
# 2. FILA DE CHAMADOS DE MANUTENÇÃO (deque)
# ---------------------------------------------------------------------------
fila_chamados = deque()


def enfileirar_chamado(alerta):
    """Cria um chamado a partir de um alerta e coloca na fila, pela prioridade.

    `alerta` é um dicionário com 'leitura_id' e 'prioridade' (1 a 5).
    Retorna o chamado criado, ou None se o alerta for inválido ou se a leitura
    já tiver um chamado na fila.
    """
    try:
        prioridade = int(alerta["prioridade"])
        leitura_id = int(alerta["leitura_id"])
    except (KeyError, TypeError, ValueError):
        print("[ERRO] Alerta inválido: precisa de 'leitura_id' e 'prioridade' numéricos.")
        return None
    if prioridade < 1 or prioridade > 5:
        print(f"[ERRO] Prioridade fora da faixa de 1 a 5: {prioridade}")
        return None

    for existente in fila_chamados:  # não cria dois chamados para a mesma leitura
        if existente["leitura_id"] == leitura_id:
            return None

    chamado = {
        "leitura_id": leitura_id,
        "prioridade": prioridade,
        "modulo_id": alerta.get("modulo_id"),
        "modulo_nome": alerta.get("modulo_nome"),
        "sensor_id": alerta.get("sensor_id"),
        "timestamp": alerta.get("timestamp"),
    }

    # Procura o primeiro chamado com prioridade MENOR: o novo entra antes dele.
    # Se não houver, entra no fim da fila.
    posicao = len(fila_chamados)
    for i, existente in enumerate(fila_chamados):
        if existente["prioridade"] < prioridade:
            posicao = i
            break
    fila_chamados.insert(posicao, chamado)
    return chamado


def proximo_chamado():
    """Tira e retorna o chamado da frente da fila (ou None se a fila estiver vazia)."""
    if len(fila_chamados) == 0:
        return None
    return fila_chamados.popleft()


def listar_fila():
    """Retorna uma lista com os chamados na ordem de atendimento (sem tirar da fila)."""
    return list(fila_chamados)


# ---------------------------------------------------------------------------
# 3. GRAFO DE DEPENDÊNCIA + BUSCA EM LARGURA (BFS)
# ---------------------------------------------------------------------------
# "energia": [...] significa: se a energia falha, esses módulos são afetados.
# É uma hipótese do grupo e pode ser ajustada. Os nomes precisam ser iguais ao
# modulo_tipo do CSV (minúsculo, sem acento, com _ no lugar de espaço).
DEPENDENCIAS = {
    "energia": ["suporte_medico", "agricultura", "laboratorio", "comunicacao"],
    "suporte_medico": ["habitacao"],
    "agricultura": ["habitacao"],
    "laboratorio": [],
    "comunicacao": [],
    "habitacao": [],
}


def busca_em_largura(origem):
    """BFS: retorna [(tipo, nivel), ...] com os tipos afetados pela falha de `origem`."""
    visitados = [origem]            # tipos que já foram vistos (evita repetir)
    fila = deque([(origem, 0)])     # cada item é (tipo, nível)
    afetados = []
    while len(fila) > 0:
        tipo, nivel = fila.popleft()
        for vizinho in DEPENDENCIAS.get(tipo, []):
            if vizinho not in visitados:
                visitados.append(vizinho)
                afetados.append((vizinho, nivel + 1))
                fila.append((vizinho, nivel + 1))
    return afetados


def impacto_falha(modulo_id):
    """Retorna os módulos afetados quando o módulo `modulo_id` falha.

    Cada item é um dicionário com modulo_id, modulo_nome, modulo_tipo e nivel
    (nivel 1 = depende direto, 2 = depende do nível 1, e assim por diante).
    Retorna lista vazia se ninguém depende dele ou se o módulo não existir.
    """
    modulo = buscar_modulo(modulo_id)
    if modulo is None:
        print(f"[ERRO] Módulo {modulo_id} não encontrado.")
        return []
    tipo = modulo["modulo_tipo"].strip().lower().replace(" ", "_")
    if tipo not in DEPENDENCIAS:
        print(f"[AVISO] O tipo '{modulo['modulo_tipo']}' não está no grafo de dependências.")
        return []

    resultado = []
    for tipo_afetado, nivel in busca_em_largura(tipo):
        for outro in indice_modulos.values():  # módulos desse tipo
            if outro["modulo_tipo"].strip().lower().replace(" ", "_") == tipo_afetado:
                resultado.append({
                    "modulo_id": outro["modulo_id"],
                    "modulo_nome": outro["modulo_nome"],
                    "modulo_tipo": outro["modulo_tipo"],
                    "nivel": nivel,
                })
    return resultado


# ---------------------------------------------------------------------------
# Testes rápidos: python structures.py (usa um banco temporário)
# ---------------------------------------------------------------------------
if __name__ == "__main__":
    import os
    import tempfile

    with tempfile.TemporaryDirectory() as pasta_temp:
        os.environ["SQLITE_PATH"] = os.path.join(pasta_temp, "teste.db")

        # Banco de teste: 6 módulos, cada um com 1 sensor
        modulos_teste = [(1, "Energia", "energia"), (2, "Suporte Médico", "suporte_medico"),
                         (3, "Habitação", "habitacao"), (4, "Agricultura", "agricultura"),
                         (5, "Laboratório", "laboratorio"), (6, "Comunicação", "comunicacao")]
        conexao = database.conectar()
        for numero, nome, tipo in modulos_teste:
            conexao.execute("INSERT INTO modulos VALUES (?, ?, ?, 1)", (numero, nome, tipo))
            conexao.execute("INSERT INTO sensores VALUES (?, ?)", (f"S-{numero:02d}", numero))
        conexao.commit()
        conexao.close()

        print("--- 1. Tabela hash ---")
        assert buscar_sensor("S-01")["modulo_nome"] == "Energia"
        assert buscar_sensor("S-99") is None
        assert buscar_modulo("2")["modulo_nome"] == "Suporte Médico"
        assert buscar_modulo("abc") is None
        print("[OK] busca de sensor e módulo")

        print("\n--- 2. Fila de chamados ---")
        for leitura, prioridade in [(1, 3), (2, 5), (3, 1), (4, 5), (5, 3)]:
            assert enfileirar_chamado({"leitura_id": leitura, "prioridade": prioridade}) is not None
        assert enfileirar_chamado({"leitura_id": 2, "prioridade": 5}) is None  # repetido
        assert enfileirar_chamado({"leitura_id": 9}) is None                   # sem prioridade
        assert enfileirar_chamado({"leitura_id": 9, "prioridade": 7}) is None  # prioridade inválida
        ordem = [chamado["leitura_id"] for chamado in listar_fila()]
        assert ordem == [2, 4, 1, 5, 3], ordem  # prioridade 5, 5, 3, 3, 1
        atendidos = []
        while len(listar_fila()) > 0:
            atendidos.append(proximo_chamado()["leitura_id"])
        assert atendidos == [2, 4, 1, 5, 3]
        assert proximo_chamado() is None  # fila vazia
        print("[OK] ordem por prioridade, FIFO na mesma prioridade, fila vazia")

        print("\n--- 3. Grafo e BFS ---")
        afetados = impacto_falha(1)  # falha na energia
        resumo = [(m["modulo_nome"], m["nivel"]) for m in afetados]
        assert resumo == [("Suporte Médico", 1), ("Agricultura", 1), ("Laboratório", 1),
                          ("Comunicação", 1), ("Habitação", 2)], resumo
        assert [m["modulo_nome"] for m in impacto_falha(2)] == ["Habitação"]
        assert impacto_falha(3) == []
        assert impacto_falha(999) == []
        print("[OK] BFS por níveis (habitação aparece uma vez só)")

        print("\nTodos os testes do structures.py passaram.")