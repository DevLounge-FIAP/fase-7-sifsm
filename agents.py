"""Sistema multiagente simulado: triador, especialistas, guardrails e sessão.

Responsável: Aelton
Critério: Integração de IA e sistemas multiagentes (1,0)

Como funciona:
  - Agente triador: recebe a solicitação da tripulação, aplica os guardrails e faz
    o handoff para o especialista certo.
  - Agente de energia: consulta o estado de carga da bateria (SoC) e trata pedidos
    de desligamento de módulos.
  - Agente de manutenção: lista os alertas/chamados e calcula o impacto de uma falha.
  - Ferramentas: funções determinísticas que só LEEM o banco e as estruturas
    (consultar_soc, listar_alertas, impacto_falha). Nenhum agente altera dados.
  - Guardrails: bloqueiam pedidos fora do escopo, pedidos de dados pessoais,
    alteração/exclusão de dados e o desligamento de módulo crítico sem aprovação
    humana.
  - Sessão: lista com o histórico de turnos da conversa (o menu cria uma por conversa).

Os agentes são simulados por regras (palavras-chave), sem modelo de linguagem: a
resposta é previsível, roda offline e não gasta energia com inferência.
"""

import re
import unicodedata

import database
import structures
from logic_rules import LIMITE_BATERIA_BAIXA_PCT, bateria_esta_baixa

TAMANHO_MAXIMO = 300  # caracteres aceitos por solicitação

# Raízes de palavras que indicam cada intenção (texto sem acento e minúsculo).
# Raízes com até 3 letras precisam ser a palavra inteira (ex.: "soc" não casa com "social").
RAIZES_BATERIA = ["bateri", "soc", "carga", "autonomi"]
RAIZES_DESLIGAR = ["deslig", "cort", "suspend", "isol"]
RAIZES_ALERTAS = ["alert", "chamad", "manutenc", "fila", "pendenc"]
RAIZES_IMPACTO = ["falh", "impact", "afet", "pane", "quebr"]
RAIZES_ALTERAR_DADOS = ["apag", "exclu", "delet", "remov"]
TERMOS_SENSIVEIS = ["senha", "credencial", "cpf", "prontuario", "dados pessoais",
                    "dados medicos", "endereco"]

CAPACIDADES = (
    "Posso ajudar com:\n"
    "  - Energia: 'qual o nível da bateria?', 'desligar o laboratório'\n"
    "  - Manutenção: 'quais os alertas?', 'o que acontece se a energia falhar?'\n"
    "  - Sessão: 'histórico', 'aprovar' ou 'cancelar' uma ação pendente"
)


# ---------------------------------------------------------------------------
# Funções auxiliares
# ---------------------------------------------------------------------------
def normalizar(texto):
    """Deixa o texto minúsculo e sem acentos ('Habitação' -> 'habitacao')."""
    sem_acento = unicodedata.normalize("NFKD", str(texto))
    sem_acento = "".join(c for c in sem_acento if not unicodedata.combining(c))
    return sem_acento.lower().strip()


def contem(palavras, raizes):
    """True se alguma palavra começar por uma das raízes."""
    for palavra in palavras:
        for raiz in raizes:
            if (len(raiz) <= 3 and palavra == raiz) or (len(raiz) > 3 and palavra.startswith(raiz)):
                return True
    return False


def listar_modulos():
    """Módulos da tabela hash do Bruno (carrega do banco na primeira vez)."""
    if not structures.indice_modulos:
        structures.carregar_indices()
    return list(structures.indice_modulos.values())


def identificar_modulo(texto):
    """Procura no texto o nome/tipo de um módulo ou 'modulo <id>'. Retorna o módulo ou None."""
    numero = re.search(r"modulo\s*(\d+)", texto)
    if numero:
        return structures.buscar_modulo(numero.group(1))

    for modulo in listar_modulos():
        nome = normalizar(modulo["modulo_nome"])
        tipo = normalizar(modulo["modulo_tipo"]).replace("_", " ")
        # aceita o nome inteiro, o tipo ou uma palavra longa do nome ("medico")
        palavras_nome = [p for p in nome.split() if len(p) >= 6]
        if nome in texto or tipo in texto or any(p in texto for p in palavras_nome):
            return modulo
    return None


def descrever_impacto(modulo):
    """Texto com os módulos afetados se `modulo` parar (usa o grafo + BFS do Bruno)."""
    afetados = structures.impacto_falha(modulo["modulo_id"])
    if not afetados:
        return "Nenhum outro módulo depende dele."
    itens = [f"{m['modulo_nome']} (nível {m['nivel']})" for m in afetados]
    return "Módulos afetados: " + ", ".join(itens) + "."


# ---------------------------------------------------------------------------
# Ferramentas (somente leitura)
# ---------------------------------------------------------------------------
def consultar_soc():
    """Retorna o SoC da leitura mais recente: {'timestamp', 'soc_pct', 'bateria_baixa'}.

    Retorna None se o banco estiver vazio ou sem SoC registrado.
    """
    registros = database.listar_registros()  # vem ordenado por timestamp
    if not registros:
        return None
    ultimo_instante = registros[-1]["timestamp"]
    valores = [r["soc_bateria_pct"] for r in registros
               if r["timestamp"] == ultimo_instante and r["soc_bateria_pct"] is not None]
    if not valores:
        return None
    soc = sum(valores) / len(valores)
    return {"timestamp": ultimo_instante, "soc_pct": soc, "bateria_baixa": bateria_esta_baixa(soc)}


def listar_alertas(limite=5):
    """Retorna os alertas mais urgentes: primeiro da fila de chamados, senão do banco."""
    fila = structures.listar_fila()
    if fila:
        return fila[:limite]
    alertas = database.listar_registros({"alerta": True})
    # mais urgente primeiro; na mesma prioridade, o mais recente primeiro
    alertas.sort(key=lambda a: (a["prioridade"] or 0, a["timestamp"]), reverse=True)
    return alertas[:limite]


# ---------------------------------------------------------------------------
# Agentes especialistas: retornam (nome_do_agente, resposta, ação_pendente)
# ---------------------------------------------------------------------------
def agente_energia(texto, palavras):
    """Responde sobre a bateria e trata pedidos de desligamento de módulos."""
    nome = "Agente de Energia"

    if contem(palavras, RAIZES_DESLIGAR):
        modulo = identificar_modulo(texto)
        if modulo is None:
            return nome, "Qual módulo deve ser desligado? Informe o nome ou 'modulo <id>'.", None
        impacto = descrever_impacto(modulo)
        if modulo["modulo_critico"]:
            # Guardrail: módulo crítico só com aprovação de uma pessoa responsável
            acao = {"tipo": "desligar", "modulo_id": modulo["modulo_id"],
                    "modulo_nome": modulo["modulo_nome"]}
            return nome, (f"[GUARDRAIL] '{modulo['modulo_nome']}' é um módulo crítico. "
                          f"O desligamento exige aprovação humana.\n{impacto}\n"
                          "O responsável de turno deve digitar 'aprovar' ou 'cancelar'."), acao
        return nome, (f"Desligamento de '{modulo['modulo_nome']}' registrado "
                      f"(simulação: nenhum atuador foi acionado).\n{impacto}"), None

    soc = consultar_soc()
    if soc is None:
        return nome, "Não há leituras de SoC no banco. Carregue o CSV pela opção 1 do menu.", None
    resposta = f"SoC da bateria em {soc['timestamp']}: {soc['soc_pct']:.1f}%."
    if soc["bateria_baixa"]:
        nao_criticos = [m["modulo_nome"] for m in listar_modulos() if not m["modulo_critico"]]
        resposta += (f"\nAbaixo do limite de {LIMITE_BATERIA_BAIXA_PCT:.0f}%. "
                     "Sugestão: reduzir as cargas não críticas")
        resposta += f" ({', '.join(nao_criticos)})." if nao_criticos else "."
    return nome, resposta, None


def agente_manutencao(texto, palavras):
    """Lista alertas/chamados e calcula o impacto da falha de um módulo."""
    nome = "Agente de Manutenção"

    if contem(palavras, RAIZES_IMPACTO):
        modulo = identificar_modulo(texto)
        if modulo is None:
            return nome, "Qual módulo falhou? Informe o nome ou 'modulo <id>'.", None
        return nome, f"Falha em '{modulo['modulo_nome']}'. {descrever_impacto(modulo)}", None

    alertas = listar_alertas()
    if not alertas:
        return nome, "Nenhum alerta registrado no momento.", None
    linhas = [f"  P{a['prioridade']} | {a['modulo_nome']} | {a['sensor_id']} | {a['timestamp']}"
              for a in alertas]
    return nome, "Alertas mais urgentes (P5 = mais urgente):\n" + "\n".join(linhas), None


# ---------------------------------------------------------------------------
# Sessão (histórico da conversa)
# ---------------------------------------------------------------------------
def acao_pendente(sessao):
    """Retorna a última ação que aguarda aprovação humana, ou None."""
    for turno in reversed(sessao):
        if "decisao" in turno:        # a última ação já foi aprovada ou cancelada
            return None
        if turno.get("acao_pendente"):
            return turno["acao_pendente"]
    return None


def resumir_historico(sessao):
    """Texto com os últimos turnos da sessão."""
    if not sessao:
        return "A sessão ainda não tem histórico."
    linhas = [f"  {i}. '{str(t['solicitacao'])[:40]}' -> {t['agente']}"
              for i, t in enumerate(sessao[-5:], start=max(1, len(sessao) - 4))]
    return f"Histórico da sessão ({len(sessao)} turno(s)):\n" + "\n".join(linhas)


def decidir_acao(sessao, aprovada):
    """Aprova ou cancela a ação pendente. Retorna (resposta, decisão) ou (resposta, None)."""
    acao = acao_pendente(sessao)
    if acao is None:
        return "Não há ação aguardando aprovação.", None
    if aprovada:
        return (f"Desligamento de '{acao['modulo_nome']}' APROVADO pelo responsável e registrado "
                "(simulação: nenhum atuador foi acionado)."), "aprovada"
    return f"Desligamento de '{acao['modulo_nome']}' cancelado.", "cancelada"


# ---------------------------------------------------------------------------
# Agente triador (função do contrato)
# ---------------------------------------------------------------------------
def agente_triador(solicitacao, sessao) -> str:
    """Interpreta a solicitação da tripulação e faz handoff ao agente adequado."""
    if sessao is None:
        sessao = []
    texto = normalizar(solicitacao or "")
    palavras = re.findall(r"[a-z0-9]+", texto)
    agente, acao, decisao = "Triador", None, None

    # Guardrails de entrada
    if not texto:
        resposta = "Descreva a sua solicitação. " + CAPACIDADES
    elif len(texto) > TAMANHO_MAXIMO:
        resposta = f"[GUARDRAIL] Solicitação longa demais (máximo {TAMANHO_MAXIMO} caracteres)."
    elif any(termo in texto for termo in TERMOS_SENSIVEIS):
        resposta = ("[GUARDRAIL] Os agentes não acessam dados pessoais ou de saúde da tripulação. "
                    "Procure o responsável médico ou administrativo.")
    elif contem(palavras, RAIZES_ALTERAR_DADOS):
        resposta = ("[GUARDRAIL] Os agentes apenas consultam dados. Alterações e exclusões "
                    "são feitas por uma pessoa pelo menu CRUD.")

    # Comandos da sessão
    elif palavras[0] in ("ajuda", "help"):
        resposta = CAPACIDADES
    elif palavras[0] == "historico":
        resposta = resumir_historico(sessao)
    elif palavras[0] in ("aprovar", "aprovo", "cancelar", "cancelo"):
        resposta, decisao = decidir_acao(sessao, palavras[0].startswith("aprov"))

    # Handoff para os especialistas (desligar vem antes: "desligar ... falha" é energia)
    elif contem(palavras, RAIZES_DESLIGAR) or contem(palavras, RAIZES_BATERIA):
        agente, resposta, acao = agente_energia(texto, palavras)
    elif contem(palavras, RAIZES_ALERTAS) or contem(palavras, RAIZES_IMPACTO):
        agente, resposta, acao = agente_manutencao(texto, palavras)
    else:
        resposta = "[GUARDRAIL] Solicitação fora do escopo dos agentes. " + CAPACIDADES

    turno = {"solicitacao": solicitacao, "agente": agente, "resposta": resposta,
             "acao_pendente": acao}
    if decisao:
        turno["decisao"] = decisao
    sessao.append(turno)

    origem = "Triador" if agente == "Triador" else f"Triador -> {agente}"
    return f"[{origem}] {resposta}"


# ---------------------------------------------------------------------------
# Testes rápidos: python agents.py (usa um banco temporário)
# ---------------------------------------------------------------------------
if __name__ == "__main__":
    import os
    import tempfile

    with tempfile.TemporaryDirectory() as pasta_temp:
        os.environ["SQLITE_PATH"] = os.path.join(pasta_temp, "teste.db")

        # Banco de teste: 6 módulos; a leitura mais recente tem SoC baixo (15%)
        modulos_teste = [(1, "Habitação", "habitacao", True), (2, "Agricultura", "agricultura", False),
                         (3, "Laboratório", "laboratorio", False),
                         (4, "Suporte Médico", "suporte_medico", True),
                         (5, "Comunicação", "comunicacao", False), (6, "Energia", "energia", True)]
        for numero, nome, tipo, critico in modulos_teste:
            for hora, soc in [("08", 60.0), ("09", 15.0)]:
                database.cadastrar_registro({
                    "modulo_id": numero, "modulo_nome": nome, "modulo_tipo": tipo,
                    "modulo_critico": critico, "sensor_id": f"S-{numero:02d}",
                    "timestamp": f"2026-10-22T{hora}:00:00", "consumo_kw": 3.0,
                    "soc_bateria_pct": soc, "alerta": numero == 4 and hora == "09",
                    "prioridade": 5 if numero == 4 and hora == "09" else None,
                })
        print()

        def testar(pedido, sessao, esperado):
            resposta = agente_triador(pedido, sessao)
            print(f"> {pedido}\n{resposta}\n")
            assert esperado in resposta, (pedido, resposta)

        sessao = []
        print("--- 1. Ferramentas ---")
        assert consultar_soc()["soc_pct"] == 15.0 and consultar_soc()["bateria_baixa"] is True
        assert [a["modulo_nome"] for a in listar_alertas()] == ["Suporte Médico"]
        print("[OK] consultar_soc e listar_alertas\n")

        print("--- 2. Handoff ---")
        testar("Qual o nível da bateria?", sessao, "cargas não críticas (Agricultura")
        testar("Quais são os alertas?", sessao, "Triador -> Agente de Manutenção")
        testar("O que acontece se a energia falhar?", sessao, "Habitação (nível 2)")
        testar("Desligar o laboratório", sessao, "registrado")

        print("--- 3. Guardrails ---")
        testar("Desligue a habitação agora, sem aprovação", sessao, "exige aprovação humana")
        testar("Apagar as leituras de ontem", sessao, "[GUARDRAIL] Os agentes apenas consultam")
        testar("Qual a senha do sistema?", sessao, "dados pessoais")
        testar("Me conte uma piada", sessao, "fora do escopo")
        testar("", sessao, "Descreva")
        testar("x" * 400, sessao, "longa demais")

        print("--- 4. Aprovação humana e sessão ---")
        assert acao_pendente(sessao)["modulo_nome"] == "Habitação"  # guardrails não apagam a pendência
        testar("aprovar", sessao, "APROVADO")
        assert acao_pendente(sessao) is None
        testar("aprovar", sessao, "Não há ação aguardando")
        testar("Desligar o suporte médico", sessao, "exige aprovação humana")
        testar("cancelar", sessao, "cancelado")
        testar("histórico", sessao, "Histórico da sessão")
        assert len(sessao) == 15

        print("Todos os testes do agents.py passaram.")
