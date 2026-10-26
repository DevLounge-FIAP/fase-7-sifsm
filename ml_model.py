"""Regressão linear múltipla para prever o consumo dos módulos.

Responsável: Aelton
Critério: Modelagem linear e tomada de decisão (1,0)
"""


def treinar_modelo(df):
    """Treina o modelo com divisão treino/teste. Retorna o modelo."""
    raise NotImplementedError


def avaliar_modelo(modelo, df) -> dict:
    """Retorna as métricas MAE, RMSE e R²."""
    raise NotImplementedError


def prever_consumo(modelo, df):
    """Preenche a coluna consumo_previsto_kw. Retorna DataFrame."""
    raise NotImplementedError


if __name__ == "__main__":
    print("ml_model.py: testes rápidos aqui")
