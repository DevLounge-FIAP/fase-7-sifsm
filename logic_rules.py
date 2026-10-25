"""Regra booleana da colônia e prioridade dos alertas.

ALERTA = (consumo_alto AND modulo_critico) OR bateria_baixa

Responsável: Victor
Critério: Circuitos lógicos e automação (1,0)
"""

from itertools import product

# Abaixo desse SoC (em %), a bateria é considerada baixa.
# Valor escolhido pelo grupo; se mudar, só altere aqui.
LIMITE_BATERIA_BAIXA_PCT = 20.0


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


def classificar_prioridade(linha) -> int:
    """Retorna a prioridade (1 a 5) de uma linha do dataset. (5 = mais urgente)"""
    raise NotImplementedError


if __name__ == "__main__":
    print("--- Tabela verdade: ALERTA = (consumo_alto E modulo_critico) OU bateria_baixa ---")
    print(f"{'consumo_alto':<13}{'modulo_critico':<15}{'bateria_baixa':<14}ALERTA")
    for c, m, b, a in tabela_verdade():
        print(f"{str(c):<13}{str(m):<15}{str(b):<14}{a}")

    print("\n--- Testes ---")
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
    print("[OK] Todos os testes do logic_rules.py passaram.")