"""Banco de dados (SQLite) e CRUD da Aurora Siger.

Responsável: Bruno

Cada registro é uma leitura de sensor, guardada como um dicionário com as colunas
do contrato de dados (modulo_id, sensor_id, timestamp, consumo_kw, ...).
"""

import csv
import os
import sqlite3

PASTA = os.path.dirname(os.path.abspath(__file__))
CAMINHO_BANCO = os.path.join(PASTA, "aurora_siger.db")
CAMINHO_SCRIPT = os.path.join(PASTA, "script_banco.sql")

# Colunas do contrato de dados, separadas por tipo
INTEIROS = ["leitura_id", "modulo_id", "ocupacao", "prioridade"]
DECIMAIS = ["temperatura_c", "geracao_solar_kw", "consumo_kw",
            "soc_bateria_pct", "consumo_previsto_kw"]
LOGICOS = ["modulo_critico", "consumo_alto", "alerta"]  # verdadeiro/falso

COLUNAS = ["modulo_id", "modulo_nome", "modulo_tipo", "modulo_critico", "sensor_id",
           "timestamp", "temperatura_c", "ocupacao", "geracao_solar_kw", "consumo_kw",
           "consumo_alto", "status", "soc_bateria_pct", "consumo_previsto_kw",
           "alerta", "prioridade"]
OBRIGATORIAS = ["modulo_id", "modulo_nome", "modulo_tipo", "modulo_critico",
                "sensor_id", "timestamp"]
EDITAVEIS = ["timestamp", "temperatura_c", "ocupacao", "geracao_solar_kw", "consumo_kw",
             "consumo_alto", "status", "soc_bateria_pct", "consumo_previsto_kw"]

# Colunas que podem ser usadas como filtro em listar_registros()
FILTROS = {"leitura_id": "l.leitura_id", "modulo_id": "m.modulo_id",
           "sensor_id": "l.sensor_id", "alerta": "COALESCE(a.alerta, 0)"}


def conectar():
    """Abre a conexão com o banco e cria as tabelas, se ainda não existirem."""
    conexao = sqlite3.connect(CAMINHO_BANCO)
    conexao.row_factory = sqlite3.Row  # permite ler as colunas pelo nome
    conexao.execute("PRAGMA foreign_keys = ON")
    with open(CAMINHO_SCRIPT, encoding="utf-8") as arquivo:
        conexao.executescript(arquivo.read())
    return conexao


def converter(coluna, valor):
    """Converte o valor (que pode vir como texto) para o tipo da coluna. Vazio vira None."""
    if valor is None or str(valor).strip() == "":
        return None
    if coluna in INTEIROS:
        return int(valor)
    if coluna in DECIMAIS:
        return float(valor)
    if coluna in LOGICOS:
        return str(valor).strip().lower() in ["true", "1", "s", "sim"]
    return str(valor).strip()


def preparar(dados):
    """Converte todos os campos e confere os obrigatórios (ValueError se algo estiver errado)."""
    pronto = {}
    for coluna in COLUNAS:
        pronto[coluna] = converter(coluna, dados.get(coluna))
    for coluna in OBRIGATORIAS:
        if pronto[coluna] is None:
            raise ValueError(f"o campo '{coluna}' é obrigatório")
    return pronto


def inserir_leitura(conexao, d):
    """Grava o módulo, o sensor, a leitura e (se houver) o alerta. Retorna o id da leitura."""
    # Se o módulo ou o sensor já existirem, o OR IGNORE não faz nada
    conexao.execute("INSERT OR IGNORE INTO modulos VALUES (?, ?, ?, ?)",
                    (d["modulo_id"], d["modulo_nome"], d["modulo_tipo"], d["modulo_critico"]))
    conexao.execute("INSERT OR IGNORE INTO sensores VALUES (?, ?)",
                    (d["sensor_id"], d["modulo_id"]))
    cursor = conexao.execute(
        "INSERT INTO leituras (sensor_id, timestamp, temperatura_c, ocupacao, "
        "geracao_solar_kw, consumo_kw, consumo_alto, status, soc_bateria_pct, "
        "consumo_previsto_kw) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
        (d["sensor_id"], d["timestamp"], d["temperatura_c"], d["ocupacao"],
         d["geracao_solar_kw"], d["consumo_kw"], d["consumo_alto"], d["status"],
         d["soc_bateria_pct"], d["consumo_previsto_kw"]))
    leitura_id = cursor.lastrowid
    if d["alerta"]:
        conexao.execute("INSERT INTO alertas (leitura_id, alerta, prioridade) VALUES (?, 1, ?)",
                        (leitura_id, d["prioridade"]))
    return leitura_id


def cadastrar_registro(dados):
    """Cadastra uma leitura. Retorna o id criado (ou None se der erro)."""
    conexao = None
    novo_id = None
    try:
        pronto = preparar(dados)
        conexao = conectar()
        novo_id = inserir_leitura(conexao, pronto)
        conexao.commit()
    except ValueError as erro:
        print(f"[ERRO] Dados inválidos (confira os números e os campos obrigatórios): {erro}")
    except sqlite3.Error as erro:
        print(f"[ERRO] Falha no banco de dados: {erro}")
    else:
        print(f"[OK] Registro cadastrado com id {novo_id}.")
    finally:
        if conexao is not None:
            conexao.close()
    return novo_id


def listar_registros(filtro=None):
    """Retorna a lista de leituras (cada uma é um dicionário).

    `filtro` é opcional: um dicionário como {'modulo_id': 2}.
    Colunas aceitas no filtro: leitura_id, modulo_id, sensor_id e alerta.
    """
    conexao = None
    registros = []
    try:
        consulta = (
            "SELECT l.leitura_id, m.modulo_id, m.modulo_nome, m.modulo_tipo, "
            "m.modulo_critico, l.sensor_id, l.timestamp, l.temperatura_c, l.ocupacao, "
            "l.geracao_solar_kw, l.consumo_kw, l.consumo_alto, l.status, "
            "l.soc_bateria_pct, l.consumo_previsto_kw, "
            "COALESCE(a.alerta, 0) AS alerta, a.prioridade "
            "FROM leituras l "
            "JOIN sensores s ON s.sensor_id = l.sensor_id "
            "JOIN modulos m ON m.modulo_id = s.modulo_id "
            "LEFT JOIN alertas a ON a.leitura_id = l.leitura_id")
        valores = []
        if filtro:
            condicoes = []
            for coluna, valor in filtro.items():
                if coluna not in FILTROS:
                    raise ValueError(f"não é possível filtrar por '{coluna}'")
                condicoes.append(FILTROS[coluna] + " = ?")
                valores.append(converter(coluna, valor))
            consulta += " WHERE " + " AND ".join(condicoes)
        consulta += " ORDER BY l.timestamp, l.leitura_id"

        conexao = conectar()
        for linha in conexao.execute(consulta, valores):
            registro = dict(linha)
            for coluna in LOGICOS:
                registro[coluna] = bool(registro[coluna])  # 0/1 vira False/True
            registros.append(registro)
    except ValueError as erro:
        print(f"[ERRO] Filtro inválido: {erro}")
    except sqlite3.Error as erro:
        print(f"[ERRO] Falha no banco de dados: {erro}")
    else:
        if len(registros) == 0:
            print("[AVISO] Nenhum registro encontrado.")
    finally:
        if conexao is not None:
            conexao.close()
    return registros


def alterar_registro(id, dados):
    """Altera os campos de `dados` na leitura `id`. Retorna True se alterou."""
    conexao = None
    alterou = False
    try:
        id = int(id)
        novos = {}
        for coluna, valor in dados.items():
            if coluna not in EDITAVEIS:
                raise ValueError(f"o campo '{coluna}' não pode ser alterado")
            novos[coluna] = converter(coluna, valor)

        conexao = conectar()
        existe = conexao.execute("SELECT 1 FROM leituras WHERE leitura_id = ?", (id,)).fetchone()
        if existe is None:
            raise LookupError(f"não existe registro com id {id}")

        atribuicoes = ", ".join(coluna + " = ?" for coluna in novos)
        conexao.execute("UPDATE leituras SET " + atribuicoes + " WHERE leitura_id = ?",
                        list(novos.values()) + [id])
        conexao.commit()
        alterou = True
    except ValueError as erro:
        print(f"[ERRO] Dados inválidos (confira os números e os campos obrigatórios): {erro}")
    except LookupError as erro:
        print(f"[ERRO] Registro inexistente: {erro}")
    except sqlite3.Error as erro:
        print(f"[ERRO] Falha no banco de dados: {erro}")
    else:
        print(f"[OK] Registro {id} atualizado.")
    finally:
        if conexao is not None:
            conexao.close()
    return alterou


def excluir_registro(id):
    """Exclui a leitura `id` (e o alerta dela, se houver). Retorna True se excluiu."""
    conexao = None
    excluiu = False
    try:
        id = int(id)
        conexao = conectar()
        existe = conexao.execute("SELECT 1 FROM leituras WHERE leitura_id = ?", (id,)).fetchone()
        if existe is None:
            raise LookupError(f"não existe registro com id {id}")

        conexao.execute("DELETE FROM alertas WHERE leitura_id = ?", (id,))  # o alerta primeiro
        conexao.execute("DELETE FROM leituras WHERE leitura_id = ?", (id,))
        conexao.commit()
        excluiu = True
    except ValueError as erro:
        print(f"[ERRO] Id inválido: {erro}")
    except LookupError as erro:
        print(f"[ERRO] Registro inexistente: {erro}")
    except sqlite3.Error as erro:
        print(f"[ERRO] Falha no banco de dados: {erro}")
    else:
        print(f"[OK] Registro {id} excluído.")
    finally:
        if conexao is not None:
            conexao.close()
    return excluiu


def carregar_csv(caminho):
    """Carrega o CSV da missão no banco. Se alguma linha der erro, nada é gravado."""
    conexao = None
    total = 0
    try:
        conexao = conectar()
        with open(caminho, newline="", encoding="utf-8") as arquivo:
            for linha in csv.DictReader(arquivo):
                inserir_leitura(conexao, preparar(linha))
                total += 1
        conexao.commit()  # só grava depois que todas as linhas foram lidas
    except FileNotFoundError:
        print(f"[ERRO] Arquivo não encontrado: {caminho}")
    except ValueError as erro:
        print(f"[ERRO] CSV com dados inválidos: {erro}")
    except sqlite3.Error as erro:
        print(f"[ERRO] Falha no banco de dados: {erro}")
    else:
        print(f"[OK] {total} registros carregados do CSV.")
    finally:
        if conexao is not None:
            conexao.close()


# Testes rápidos: python database.py (usa um banco temporário, não mexe no seu)
if __name__ == "__main__":
    import tempfile

    with tempfile.TemporaryDirectory() as pasta_temp:
        CAMINHO_BANCO = os.path.join(pasta_temp, "teste.db")

        leitura = {"modulo_id": 1, "modulo_nome": "Energia", "modulo_tipo": "energia",
                   "modulo_critico": True, "sensor_id": "S-ENE-01",
                   "timestamp": "2026-10-22T08:00:00", "consumo_kw": 5.1,
                   "consumo_alto": True, "alerta": True, "prioridade": 4}

        print("--- Cadastrar ---")
        id_novo = cadastrar_registro(leitura)
        print("\n--- Listar ---")
        print(listar_registros())
        print("\n--- Alterar ---")
        alterar_registro(id_novo, {"consumo_kw": 2.5})
        print("\n--- Excluir ---")
        excluir_registro(id_novo)

        print("\n--- Erros tratados ---")
        cadastrar_registro({"modulo_id": "abc"})   # valor inválido
        cadastrar_registro({"modulo_id": 1})       # campos obrigatórios faltando
        alterar_registro(999, {"consumo_kw": 1})   # registro inexistente
        excluir_registro(999)                      # registro inexistente
        carregar_csv("arquivo_que_nao_existe.csv")  # arquivo inexistente
