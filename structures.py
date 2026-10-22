"""Estruturas de dados: hash de sensores, fila de chamados e grafo de módulos.

Responsável: Bruno
Critério: Estruturas de dados em sistemas complexos (1,0)
"""


def buscar_sensor(codigo):
    """Busca um sensor/módulo pelo código em O(1) (tabela hash)."""
    raise NotImplementedError


def enfileirar_chamado(alerta):
    """Adiciona um chamado de manutenção à fila."""
    raise NotImplementedError


def proximo_chamado():
    """Retira e retorna o próximo chamado da fila."""
    raise NotImplementedError


def impacto_falha(modulo_id) -> list:
    """BFS no grafo de dependências: módulos afetados pela falha de `modulo_id`."""
    raise NotImplementedError


if __name__ == "__main__":
    print("structures.py: testes rápidos aqui")
