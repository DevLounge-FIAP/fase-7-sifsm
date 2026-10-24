"""Banco de dados (SQLite) e CRUD da Aurora Siger.

Responsável: Bruno

O CRUD trabalha com as LEITURAS dos sensores. Cada registro é um dicionário com as
colunas do contrato de dados, por exemplo:
    {"modulo_id": 1, "modulo_nome": "Energia", "modulo_tipo": "energia",
     "modulo_critico": True, "sensor_id": "S-ENE-01",
     "timestamp": "2026-10-22T08:00:00", "consumo_kw": 5.1}
"""

import csv
import os
import sqlite3
from datetime import datetime
from pathlib import Path

from dotenv import load_dotenv

load_dotenv()  # lê o arquivo .env (onde fica o SQLITE_PATH)

PASTA = Path(__file__).resolve().parent

# ----- Colunas do contrato de dados, agrupadas por tipo -----
CAMPOS_INTEIROS = ["leitura_id", "modulo_id", "ocupacao", "prioridade"]
CAMPOS_DECIMAIS = ["temperatura_c", "geracao_solar_kw", "consumo_kw",
                   "soc_bateria_pct", "consumo_previsto_kw"]
CAMPOS_LOGICOS = ["modulo_critico", "consumo_alto", "alerta"]  # verdadeiro/falso

COLUNAS_MODULO = ["modulo_id", "modulo_nome", "modulo_tipo", "modulo_critico"]
COLUNAS_LEITURA = ["sensor_id", "timestamp", "temperatura_c", "ocupacao",
                   "geracao_solar_kw", "consumo_kw", "consumo_alto", "status",
                   "soc_bateria_pct", "consumo_previsto_kw"]
COLUNAS_ALERTA = ["alerta", "prioridade"]
TODAS_COLUNAS = COLUNAS_MODULO + COLUNAS_LEITURA + COLUNAS_ALERTA

# Campos que o usuário precisa preencher ao cadastrar
OBRIGATORIOS = ["modulo_id", "modulo_nome", "modulo_tipo", "modulo_critico",
                "sensor_id", "timestamp"]
# Campos que podem ser alterados depois de cadastrados
EDITAVEIS = ["timestamp", "temperatura_c", "ocupacao", "geracao_solar_kw",
             "consumo_kw", "consumo_alto", "status", "soc_bateria_pct",
             "consumo_previsto_kw"]
# Colunas da visão v_leituras (as únicas que podem ser usadas como filtro)
COLUNAS_FILTRO = ["leitura_id"] + TODAS_COLUNAS


# ---------------------------------------------------------------------------
# Conexão com o banco
# ---------------------------------------------------------------------------
def conectar():
    """Abre a conexão com o SQLite e cria as tabelas se elas ainda não existirem."""
    caminho = Path(os.getenv("SQLITE_PATH", "aurora_siger.db"))
    if not caminho.is_absolute():
        caminho = PASTA / caminho

    conexao = sqlite3.connect(caminho)
    conexao.row_factory = sqlite3.Row            # permite ler colunas pelo nome
    conexao.execute("PRAGMA foreign_keys = ON")  # ativa as chaves estrangeiras
    script = (PASTA / "script_banco.sql").read_text(encoding="utf-8")
    conexao.executescript(script)                # cria as tabelas (se faltarem)
    return conexao


# ---------------------------------------------------------------------------
# Funções auxiliares: conferem e convertem os dados
# ---------------------------------------------------------------------------
def para_bool(texto):
    """Converte 'sim', 'true', '1'... em True e 'nao', 'false', '0'... em False."""
    texto = texto.lower()
    if texto in ["true", "1", "s", "sim", "verdadeiro"]:
        return True
    if texto in ["false", "0", "n", "nao", "não", "falso"]:
        return False
    raise ValueError("valor lógico inválido")


def converter(campo, valor):
    """Converte o valor para o tipo certo do campo. Vazio vira None."""
    if valor is None:
        return None
    valor = str(valor).strip()
    if valor == "":
        return None
    try:
        if campo in CAMPOS_INTEIROS:
            return int(valor)
        if campo in CAMPOS_DECIMAIS:
            return float(valor)
        if campo in CAMPOS_LOGICOS:
            return para_bool(valor)
    except ValueError:
        raise ValueError(f"valor inválido para '{campo}': {valor}")
    return valor  # os demais campos são texto


def validar_data(texto):
    """Confere se a data está no formato ISO 8601 (ex.: 2026-10-22T08:00:00)."""
    try:
        datetime.fromisoformat(texto)
    except (TypeError, ValueError):
        raise ValueError("o timestamp deve ser como 2026-10-22T08:00:00")


def preparar_dados(dados):
    """Converte todos os campos e confere os obrigatórios. Dá ValueError se algo estiver errado."""
    limpos = {}
    for campo in TODAS_COLUNAS:
        limpos[campo] = converter(campo, dados.get(campo))

    for campo in OBRIGATORIOS:
        if limpos[campo] is None:
            raise ValueError(f"o campo '{campo}' é obrigatório")
    validar_data(limpos["timestamp"])
    if limpos["alerta"] and limpos["prioridade"] is None:
        raise ValueError("informe a prioridade (1 a 5) quando houver alerta")
    return limpos


def inserir_leitura(conexao, d, ignorar_repetida=False):
    """Grava módulo, sensor, leitura e (se houver) alerta. Retorna o id da leitura.

    Com ignorar_repetida=True, uma leitura que já existe é pulada e retorna None.
    """
    # Módulo e sensor: se já existirem, o OR IGNORE não faz nada
    conexao.execute(
        "INSERT OR IGNORE INTO modulos (modulo_id, modulo_nome, modulo_tipo, modulo_critico) "
        "VALUES (?, ?, ?, ?)",
        (d["modulo_id"], d["modulo_nome"], d["modulo_tipo"], d["modulo_critico"]))
    conexao.execute(
        "INSERT OR IGNORE INTO sensores (sensor_id, modulo_id) VALUES (?, ?)",
        (d["sensor_id"], d["modulo_id"]))

    comando = "INSERT OR IGNORE" if ignorar_repetida else "INSERT"
    cursor = conexao.execute(
        comando + " INTO leituras (sensor_id, timestamp, temperatura_c, ocupacao, "
        "geracao_solar_kw, consumo_kw, consumo_alto, status, soc_bateria_pct, "
        "consumo_previsto_kw) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
        tuple(d[coluna] for coluna in COLUNAS_LEITURA))
    if cursor.rowcount == 0:  # a leitura já existia
        return None
    leitura_id = cursor.lastrowid

    if d["alerta"]:
        conexao.execute(
            "INSERT INTO alertas (leitura_id, alerta, prioridade) VALUES (?, 1, ?)",
            (leitura_id, d["prioridade"]))
    return leitura_id


# ---------------------------------------------------------------------------
# CRUD
# ---------------------------------------------------------------------------
def cadastrar_registro(dados):
    """Cadastra uma leitura. Retorna o id criado ou None se der erro."""
    conexao = None
    novo_id = None
    try:
        dados_prontos = preparar_dados(dados)
        conexao = conectar()
        novo_id = inserir_leitura(conexao, dados_prontos)
        conexao.commit()  # confirma a gravação
    except ValueError as erro:
        print(f"[ERRO] Dados inválidos: {erro}")
    except sqlite3.IntegrityError as erro:
        print(f"[ERRO] O banco não aceitou os dados: {erro}")
    except sqlite3.Error as erro:
        print(f"[ERRO] Falha no banco de dados: {erro}")
    else:
        print(f"[OK] Registro cadastrado com id {novo_id}.")
    finally:
        if conexao is not None:
            conexao.close()  # sempre fecha a conexão
    return novo_id


def listar_registros(filtro=None):
    """Retorna a lista de leituras (cada uma é um dicionário).

    `filtro` é opcional, por exemplo {"modulo_id": 2}.
    """
    conexao = None
    registros = []
    try:
        consulta = "SELECT * FROM v_leituras"
        valores = []
        if filtro:
            condicoes = []
            for coluna, valor in filtro.items():
                if coluna not in COLUNAS_FILTRO:  # só aceita colunas conhecidas (segurança)
                    raise ValueError(f"não é possível filtrar por '{coluna}'")
                condicoes.append(coluna + " = ?")
                valores.append(converter(coluna, valor))
            consulta += " WHERE " + " AND ".join(condicoes)
        consulta += " ORDER BY timestamp, leitura_id"

        conexao = conectar()
        for linha in conexao.execute(consulta, valores):
            registro = dict(linha)
            for campo in CAMPOS_LOGICOS:
                registro[campo] = bool(registro[campo])  # 0/1 vira False/True
            registros.append(registro)
    except ValueError as erro:
        print(f"[ERRO] Filtro inválido: {erro}")
    except sqlite3.Error as erro:
        print(f"[ERRO] Falha no banco de dados: {erro}")
    else:
        if not registros:
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
        id = converter("leitura_id", id)
        if id is None:
            raise ValueError("informe o id do registro")
        if not dados:
            raise ValueError("nenhum campo informado para alterar")
        novos = {}
        for campo, valor in dados.items():
            if campo not in EDITAVEIS:
                raise ValueError(f"o campo '{campo}' não pode ser alterado")
            novos[campo] = converter(campo, valor)
        if "timestamp" in novos:
            validar_data(novos["timestamp"])

        conexao = conectar()
        atual = conexao.execute(
            "SELECT * FROM leituras WHERE leitura_id = ?", (id,)).fetchone()
        if atual is None:
            raise LookupError(f"não existe registro com id {id}")

        leitura = dict(atual)  # dados atuais...
        leitura.update(novos)  # ...com as mudanças por cima
        conexao.execute(
            "UPDATE leituras SET timestamp = ?, temperatura_c = ?, ocupacao = ?, "
            "geracao_solar_kw = ?, consumo_kw = ?, consumo_alto = ?, status = ?, "
            "soc_bateria_pct = ?, consumo_previsto_kw = ? WHERE leitura_id = ?",
            (leitura["timestamp"], leitura["temperatura_c"], leitura["ocupacao"],
             leitura["geracao_solar_kw"], leitura["consumo_kw"], leitura["consumo_alto"],
             leitura["status"], leitura["soc_bateria_pct"], leitura["consumo_previsto_kw"],
             id))
        conexao.commit()
        alterou = True
    except ValueError as erro:
        print(f"[ERRO] Dados inválidos: {erro}")
    except LookupError as erro:
        print(f"[ERRO] Registro inexistente: {erro}")
    except sqlite3.IntegrityError as erro:
        print(f"[ERRO] O banco não aceitou a alteração: {erro}")
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
        id = converter("leitura_id", id)
        if id is None:
            raise ValueError("informe o id do registro")

        conexao = conectar()
        existe = conexao.execute(
            "SELECT 1 FROM leituras WHERE leitura_id = ?", (id,)).fetchone()
        if existe is None:
            raise LookupError(f"não existe registro com id {id}")

        conexao.execute("DELETE FROM alertas WHERE leitura_id = ?", (id,))  # primeiro o alerta
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


# ---------------------------------------------------------------------------
# Carga do CSV
# ---------------------------------------------------------------------------
def carregar_csv(caminho):
    """Carrega o CSV da missão no banco. Pode rodar mais de uma vez (repetidas são puladas).

    Retorna (novos, repetidos). Se alguma linha der erro, nada é gravado.
    """
    conexao = None
    novos = 0
    repetidos = 0
    try:
        with open(caminho, newline="", encoding="utf-8") as arquivo:
            conexao = conectar()
            numero_linha = 1  # a linha 1 é o cabeçalho
            for linha in csv.DictReader(arquivo):
                numero_linha += 1
                try:
                    dados = preparar_dados(linha)
                except ValueError as erro:
                    raise ValueError(f"linha {numero_linha} do CSV: {erro}")
                if inserir_leitura(conexao, dados, ignorar_repetida=True) is None:
                    repetidos += 1
                else:
                    novos += 1
        conexao.commit()  # só grava se todas as linhas estiverem certas
    except FileNotFoundError:
        print(f"[ERRO] Arquivo não encontrado: {caminho}")
        novos = repetidos = 0
    except ValueError as erro:
        print(f"[ERRO] CSV inválido: {erro}")
        novos = repetidos = 0
    except sqlite3.Error as erro:
        print(f"[ERRO] Falha no banco de dados: {erro}")
        novos = repetidos = 0
    else:
        print(f"[OK] CSV carregado: {novos} novos registros, {repetidos} já existiam.")
    finally:
        if conexao is not None:
            conexao.close()
    return novos, repetidos


# ---------------------------------------------------------------------------
# Testes rápidos: python database.py (usa um banco temporário)
# ---------------------------------------------------------------------------
if __name__ == "__main__":
    import tempfile

    with tempfile.TemporaryDirectory() as pasta_temp:
        os.environ["SQLITE_PATH"] = os.path.join(pasta_temp, "teste.db")

        leitura = {
            "modulo_id": 1, "modulo_nome": "Habitação 1", "modulo_tipo": "habitacao",
            "modulo_critico": True, "sensor_id": "S-HAB-01",
            "timestamp": "2026-10-22T08:00:00", "temperatura_c": 21.5, "ocupacao": 4,
            "geracao_solar_kw": 3.2, "consumo_kw": 5.1, "consumo_alto": True,
            "status": "ok", "alerta": True, "prioridade": 4,
        }

        print("--- 1. Cadastrar (válido) ---")
        assert cadastrar_registro(leitura) == 1

        print("\n--- 2. Cadastrar repetido e dados inválidos (devem dar erro) ---")
        assert cadastrar_registro(leitura) is None
        assert cadastrar_registro({**leitura, "timestamp": "2026-10-22T09:00:00", "ocupacao": "abc"}) is None
        assert cadastrar_registro({**leitura, "timestamp": "2026-10-22T09:00:00", "soc_bateria_pct": 150}) is None

        print("\n--- 3. Listar ---")
        todos = listar_registros()
        assert len(todos) == 1 and todos[0]["alerta"] is True
        assert len(listar_registros({"modulo_id": 1})) == 1
        assert listar_registros({"modulo_id": 99}) == []
        assert listar_registros({"coluna_falsa": 1}) == []

        print("\n--- 4. Alterar ---")
        assert alterar_registro(1, {"consumo_kw": 2.5}) is True
        assert listar_registros({"leitura_id": 1})[0]["consumo_kw"] == 2.5
        assert alterar_registro(999, {"consumo_kw": 1}) is False
        assert alterar_registro(1, {"sensor_id": "outro"}) is False

        print("\n--- 5. Carregar CSV (duas vezes) ---")
        csv_teste = os.path.join(pasta_temp, "amostra.csv")
        with open(csv_teste, "w", encoding="utf-8") as f:
            f.write("timestamp,modulo_id,modulo_nome,modulo_tipo,modulo_critico,sensor_id,"
                    "consumo_kw,alerta,prioridade\n"
                    "2026-10-22T10:00:00,2,Energia,energia,True,S-ENE-01,8.0,True,5\n"
                    "2026-10-22T11:00:00,2,Energia,energia,True,S-ENE-01,3.0,False,\n")
        assert carregar_csv(csv_teste) == (2, 0)
        assert carregar_csv(csv_teste) == (0, 2)
        assert carregar_csv("nao_existe.csv") == (0, 0)

        print("\n--- 6. Excluir ---")
        assert excluir_registro(1) is True
        assert excluir_registro(1) is False
        assert len(listar_registros()) == 2

        print("\nTodos os testes do database.py passaram.")