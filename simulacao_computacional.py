"""Simulação do estado de carga (SoC) da bateria por integração numérica.

SoC(t) = SoC0 + (1/C) * integral de (P_solar - P_consumo) dt

Responsável: Aelton
Critério: Simulação computacional e integração matemática (1,5)
"""


def simular_soc(df, cenario):
    """Simula o SoC ao longo do tempo para o `cenario` informado. Retorna DataFrame."""
    raise NotImplementedError


def energia_acumulada(df, modulo_id) -> float:
    """Energia consumida pelo módulo no período (área sob a curva)."""
    raise NotImplementedError


if __name__ == "__main__":
    print("simulacao_computacional.py: testes rápidos aqui")
