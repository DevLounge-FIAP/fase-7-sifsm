"""
Script de Geração da Base de Dados de Telemetria - Missão Aurora Siger (SCIC Fase 7)
Gera dados simulados realistas de energia (geração solar e consumo), temperatura e
ocupação dos módulos da colônia, em leituras horárias, para permitir a simulação do
estado de carga da bateria (SoC) e o treinamento da regressão linear.
"""

import numpy as np
import pandas as pd

# Geração solar da colônia em kW para cada momento do dia (madrugada, manhã, tarde e noite)
GERACAO_POR_HORA = [0, 0, 0, 0, 0, 0,          
                    5, 25, 45, 60, 75, 90,     
                    90, 75, 60, 45, 25, 5,     
                    0, 0, 0, 0, 0, 0]          

# Temperatura interna da colônia em °C para cada momento do dia (madrugada, manhã, tarde e noite)
TEMPERATURA_POR_HORA = [18, 17.5, 17, 16.5, 17.5, 18,   
                        18.5, 19, 19.5, 20, 20.5, 21,   
                        21.5, 22, 22.5, 22, 21.5, 21,   
                        20.5, 20, 19.5, 19, 18.5, 18]   

# Consumo extra de cada módulo no turno de trabalho
EXTRA_TURNO_KW = 0.5

# Temperatura de conforto usada como base para definir o consumo usado para o aquecimento
TEMPERATURA_CONFORTO = 20

def gerar_dataset_colonia(caminho_saida: str = "dados_aurora_siger.csv",
                          caminho_amostra: str = "dados_amostra.csv",
                          random_seed: int = 42, dias: int = 30):
    """
    Gera uma base consistente com leituras horárias de 6 módulos da colônia
    marciana Aurora Siger ao longo de `dias` dias (30 dias = 4320 registros).
    """
    np.random.seed(random_seed)

    # consumo_base_kw = consumo do módulo vazio
    # kw_por_pessoa = consumo em kW de cada pessoa no módulo
    # ocupacao_max = lotação máxima que o módulo suporta
    modulos_colonia = [
        # (id, nome, tipo, sigla_sensor, critico, consumo_base_kw, kw_por_pessoa, ocupacao_max)
        (1, "Habitacao", "habitacao", "HAB", True, 3.0, 0.3, 5),
        (2, "Agricultura", "agricultura", "AGR", False, 3.0, 0.1, 3),
        (3, "Laboratorio", "laboratorio", "LAB", False, 2.5, 0.3, 4),
        (4, "Suporte Medico", "suporte_medico", "MED", True, 2.0, 0.4, 5),
        (5, "Comunicacao", "comunicacao", "COM", False, 1.5, 0.1, 2),
        (6, "Energia", "energia", "ENE", True, 1.5, 0.1, 3)
    ]

    registros = []

    # Cada hora gera uma leitura por módulo
    horarios = pd.date_range("2026-10-14T00:00:00", periods=dias * 24, freq="h")

    for instante in horarios:
        hora = instante.hour

        # Geração solar da colônia reduzido em até 10% pela poeira
        geracao_solar = round(GERACAO_POR_HORA[hora] * np.random.uniform(0.9, 1.0), 2)

        for mod_id, nome, tipo, sigla, critico, base_kw, kw_pessoa, ocup_max in modulos_colonia:
            # Temperatura interna = temperatura estimada na hora + ruído do sensor
            temp = round(TEMPERATURA_POR_HORA[hora] + np.random.normal(0, 0.8), 2)

            # Aumento da ocupação dado o horário (das 8h ás 18h)
            turno = 8 <= hora < 18
            if turno:
                ocupacao = np.random.randint(ocup_max // 2, ocup_max + 1)
            else:
                ocupacao = np.random.randint(0, ocup_max // 2 + 1)

            # Aquecimento: abaixo de 21 °C, o módulo gasta 0,3 kW a mais para cada grau que falta
            
            aquecimento = 0.3 * max(0.0, TEMPERATURA_CONFORTO - temp)

            # Ruído: pequena variação aleatória do consumo
            ruido = np.random.normal(0, 0.2)

            # Cálculo do consumo de acordo com o uso do módulo
            consumo = round(base_kw + (kw_pessoa * ocupacao) + aquecimento + (EXTRA_TURNO_KW if turno else 0.0) + ruido, 2)
            consumo = max(consumo, 0.1)

            # Regra de status operacional com base no consumo 
            limite = base_kw + kw_pessoa * ocup_max + EXTRA_TURNO_KW   # consumo esperado com o módulo cheio 
            if consumo >= limite:
                status = "alerta_critico" if consumo >= limite * 1.2 else "alerta"
            else:
                status = "ativo"

            registros.append({
                "timestamp": instante.strftime("%Y-%m-%dT%H:%M:%S"),
                "modulo_id": mod_id,
                "modulo_nome": nome,
                "modulo_tipo": tipo,
                "modulo_critico": critico,
                "sensor_id": f"S-{sigla}-01",
                "temperatura_c": temp,
                "ocupacao": ocupacao,
                "geracao_solar_kw": geracao_solar,
                "consumo_kw": consumo,
                "consumo_alto": consumo >= limite,
                "status": status,
                
                "soc_bateria_pct": 0.0,        # a ser preenchida pela simulação 
                "consumo_previsto_kw": 0.0,    # a ser preenchida pela regressão 
                "alerta": False,               # a ser preenchida pelo Victor
                "prioridade": 1                # a ser preenchida pelo Victor
            })

    df = pd.DataFrame(registros)
    df.to_csv(caminho_saida, index=False, encoding="utf-8")
    print(f"✓ Base '{caminho_saida}' gerada com sucesso: {len(df)} registros ao longo de {dias} dias.")

    # Amostra oficial 
    df.head(48).to_csv(caminho_amostra, index=False, encoding="utf-8")
    print(f"✓ Amostra '{caminho_amostra}' gerada com sucesso: 48 registros.")
    return df

if __name__ == "__main__":
    gerar_dataset_colonia()
