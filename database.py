"""Banco de dados e CRUD da Aurora Siger.

Responsável: Bruno
Critério: Organização dos dados, banco e CRUD (1,5)
"""


def conectar():
    """Abre a conexão com o banco definido em DB_ENGINE (.env)."""
    raise NotImplementedError


def cadastrar_registro(dados):
    """Insere um registro. `dados` é um dict com as colunas do contrato."""
    raise NotImplementedError


def listar_registros(filtro=None):
    """Retorna os registros, opcionalmente filtrados."""
    raise NotImplementedError


def alterar_registro(id, dados):
    """Atualiza o registro `id` com os campos de `dados`."""
    raise NotImplementedError


def excluir_registro(id):
    """Remove o registro `id`."""
    raise NotImplementedError


if __name__ == "__main__":
    print("database.py: testes rápidos aqui")
