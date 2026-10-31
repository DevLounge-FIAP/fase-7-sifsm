"""Regra booleana da colônia e prioridade dos alertas.

ALERTA = (consumo_alto AND modulo_critico) OR bateria_baixa

Responsável: Victor
Critério: Circuitos lógicos e automação (1,0)
"""

from itertools import product

# Abaixo desse SoC (em %), a bateria é considerada baixa.
# Valor escolhido pelo grupo (o mesmo da simulação); se mudar, só altere aqui.
LIMITE_BATERIA_BAIXA_PCT = 20.0

# O consumo real conta como "acima do previsto" quando passa deste percentual (0,20 = 20%).
LIMITE_DESVIO_CONSUMO = 0.20


def bateria_esta_baixa(soc_pct) -> bool:
    """Converte o SoC (%) em verdadeiro/falso: True se estiver abaixo do limite."""
    if soc_pct is None:  # leitura sem SoC: não dá pra afirmar que está baixa
        return False
    return float(soc_pct) < LIMITE_BATERIA_BAIXA_PCT


def avaliar_alerta(consumo_alto, modulo_critico, bateria_baixa) -> bool:
    """Aplica a regra booleana da colônia.

    Dispara alerta se (consumo alto E módulo crítico) OU bateria baixa.
    """
    return bool((consumo_alto and modulo_critico) or bateria_baixa)


def tabela_verdade() -> list:
    """Retorna as 8 combinações de entrada com a saída da regra.

    Cada linha é uma tupla: (consumo_alto, modulo_critico, bateria_baixa, alerta).
    """
    linhas = []
    for consumo_alto, modulo_critico, bateria_baixa in product([False, True], repeat=3):
        alerta = avaliar_alerta(consumo_alto, modulo_critico, bateria_baixa)
        linhas.append((consumo_alto, modulo_critico, bateria_baixa, alerta))
    return linhas


# ---------------------------------------------------------------------------
# Prioridade dos alertas (escala de 1 a 5, onde 5 é o mais urgente)
# ---------------------------------------------------------------------------
def _campo(linha, nome):
    """Lê um campo da linha (dicionário ou linha do pandas). Retorna None se não existir."""
    try:
        return linha[nome]
    except (KeyError, IndexError, TypeError):
        return None


def _como_bool(valor) -> bool:
    """Aceita True/False, 0/1 e textos como 'True' ou 'sim'. Vazio ou NaN viram False."""
    if valor is None or valor != valor:  # valor != valor só acontece com NaN
        return False
    if isinstance(valor, str):
        return valor.strip().lower() in ("true", "1", "s", "sim", "verdadeiro")
    return bool(valor)


def _numero(valor):
    """Converte para float. Retorna None se for vazio, texto inválido ou NaN."""
    try:
        numero = float(valor)
    except (TypeError, ValueError):
        return None
    if numero != numero:  # NaN
        return None
    return numero


def _consumo_acima_do_previsto(linha) -> bool:
    """True se o consumo real passou do previsto em pelo menos LIMITE_DESVIO_CONSUMO."""
    real = _numero(_campo(linha, "consumo_kw"))
    previsto = _numero(_campo(linha, "consumo_previsto_kw"))
    if real is None or previsto is None or previsto <= 0:
        return False  # sem previsão válida, o critério é pulado (evita dividir por zero)
    return real >= previsto * (1 + LIMITE_DESVIO_CONSUMO)


def classificar_prioridade(linha) -> int:
    """Retorna a prioridade (1 a 5) de uma linha do dataset. (5 = mais urgente)

    Sem alerta: prioridade 1. Com alerta, soma pontos a partir de 2:
      +1 se o módulo é crítico
      +1 se a bateria está baixa (SoC abaixo do limite)
      +1 se o consumo real está pelo menos 20% acima do previsto
    O máximo é 5.
    """
    consumo_alto = _como_bool(_campo(linha, "consumo_alto"))
    modulo_critico = _como_bool(_campo(linha, "modulo_critico"))
    bateria_baixa = bateria_esta_baixa(_numero(_campo(linha, "soc_bateria_pct")))

    if not avaliar_alerta(consumo_alto, modulo_critico, bateria_baixa):
        return 1

    pontos = 2
    if modulo_critico:
        pontos += 1
    if bateria_baixa:
        pontos += 1
    if _consumo_acima_do_previsto(linha):
        pontos += 1
    return min(pontos, 5)


if __name__ == "__main__":
    print("--- Tabela verdade: ALERTA = (consumo_alto E modulo_critico) OU bateria_baixa ---")
    print(f"{'consumo_alto':<13}{'modulo_critico':<15}{'bateria_baixa':<14}ALERTA")
    for c, m, b, a in tabela_verdade():
        print(f"{str(c):<13}{str(m):<15}{str(b):<14}{a}")

    print("\n--- Testes da regra ---")
    # Estrutura da tabela
    assert len(tabela_verdade()) == 8
    # Bateria baixa sozinha já basta
    assert avaliar_alerta(False, False, True) is True
    # Consumo alto só importa se o módulo for crítico
    assert avaliar_alerta(True, False, False) is False
    assert avaliar_alerta(True, True, False) is True
    assert avaliar_alerta(False, True, False) is False
    # Tudo normal: sem alerta
    assert avaliar_alerta(False, False, False) is False
    # Em 5 das 8 combinações o alerta dispara
    assert sum(1 for linha in tabela_verdade() if linha[3]) == 5
    # Aceita 0/1 (como vêm do banco) e sempre devolve bool
    assert avaliar_alerta(1, 1, 0) is True
    assert avaliar_alerta(0, 1, 0) is False
    # Limite da bateria
    assert bateria_esta_baixa(19.9) is True
    assert bateria_esta_baixa(20.0) is False
    assert bateria_esta_baixa(80) is False
    assert bateria_esta_baixa(None) is False
    print("[OK] Regra booleana")

    print("\n--- Testes da prioridade ---")

    def linha(alto, critico, soc, real, previsto):
        return {"consumo_alto": alto, "modulo_critico": critico, "soc_bateria_pct": soc,
                "consumo_kw": real, "consumo_previsto_kw": previsto}

    # Sem alerta: sempre 1
    assert classificar_prioridade(linha(False, True, 80, 10, 10)) == 1   # crítico, mas sem consumo alto
    assert classificar_prioridade(linha(True, False, 80, 10, 10)) == 1   # consumo alto, mas não crítico
    assert classificar_prioridade(linha(False, False, 80, 15, 10)) == 1  # desvio sozinho não gera alerta
    # Com alerta: base 2 + pontos
    assert classificar_prioridade(linha(True, True, 80, 10, 10)) == 3    # crítico (+1)
    assert classificar_prioridade(linha(False, False, 15, 10, 10)) == 3  # bateria baixa (+1)
    assert classificar_prioridade(linha(False, False, 15, 13, 10)) == 4  # bateria (+1) e desvio (+1)
    assert classificar_prioridade(linha(True, True, 15, 13, 10)) == 5    # crítico + bateria + desvio
    # Limite do desvio: exatamente 20% acima conta; um pouco menos, não
    assert classificar_prioridade(linha(True, True, 80, 12.0, 10)) == 4
    assert classificar_prioridade(linha(True, True, 80, 11.99, 10)) == 3
    # Dados faltando: o critério é pulado, sem erro
    assert classificar_prioridade(linha(True, True, 80, 12, 0)) == 3          # previsto zero
    assert classificar_prioridade(linha(True, True, 80, 12, None)) == 3       # previsto vazio
    assert classificar_prioridade(linha(True, True, 80, 12, float("nan"))) == 3
    assert classificar_prioridade(linha(True, True, None, 10, 10)) == 3       # sem SoC
    assert classificar_prioridade({"consumo_alto": True, "modulo_critico": True}) == 3  # só 2 campos
    # Aceita textos e 0/1
    assert classificar_prioridade(linha("True", "True", "15", "13", "10")) == 5
    assert classificar_prioridade(linha(1, 1, 80, 10, 10)) == 3
    # Qualquer combinação devolve um inteiro entre 1 e 5
    for alto, critico, soc, real in product([False, True], [False, True], [10, 80], [10, 13]):
        valor = classificar_prioridade(linha(alto, critico, soc, real, 10))
        assert isinstance(valor, int) and 1 <= valor <= 5
    print("[OK] Prioridade de 1 a 5")

    print("\n[OK] Todos os testes do logic_rules.py passaram.")