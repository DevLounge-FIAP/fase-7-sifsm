"""Regra booleana da colônia e prioridade dos alertas.

ALERTA = (consumo_alto AND modulo_critico) OR bateria_baixa

Responsável: Victor
Critério: Circuitos lógicos e automação (1,0)
"""


def avaliar_alerta(consumo_alto, modulo_critico, bateria_baixa) -> bool:
    """Aplica a regra booleana da colônia."""
    raise NotImplementedError


def tabela_verdade() -> list:
    """Retorna as 8 combinações de entrada com a saída da regra."""
    raise NotImplementedError


def classificar_prioridade(linha) -> int:
    """Retorna a prioridade (1 a 5) de uma linha do dataset."""
    raise NotImplementedError


if __name__ == "__main__":
    print("logic_rules.py: testes rápidos aqui")
