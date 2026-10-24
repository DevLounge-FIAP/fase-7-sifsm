-- =====================================================================
-- Criação das tabelas da Aurora Siger (SIFSM - Fase 7)
-- Banco: SQLite (escolhido por não exigir servidor nem credenciais)
-- Responsável: Bruno
--
-- Booleanos são INTEGER com CHECK (0 = falso, 1 = verdadeiro).
-- O script é idempotente (IF NOT EXISTS): pode rodar mais de uma vez.
-- =====================================================================

PRAGMA foreign_keys = ON;

-- Módulos da colônia (habitação, agricultura, laboratório, suporte médico, comunicação, energia)
CREATE TABLE IF NOT EXISTS modulos (
    modulo_id       INTEGER PRIMARY KEY,
    modulo_nome     TEXT    NOT NULL,
    modulo_tipo     TEXT    NOT NULL,
    modulo_critico  INTEGER NOT NULL CHECK (modulo_critico IN (0, 1))
);

-- Sensores instalados em cada módulo
CREATE TABLE IF NOT EXISTS sensores (
    sensor_id  TEXT    PRIMARY KEY,
    modulo_id  INTEGER NOT NULL,
    FOREIGN KEY (modulo_id) REFERENCES modulos (modulo_id)
);

-- Leituras horárias (espelha o dados_aurora_siger.csv)
CREATE TABLE IF NOT EXISTS leituras (
    leitura_id           INTEGER PRIMARY KEY AUTOINCREMENT,
    sensor_id            TEXT    NOT NULL,
    timestamp            TEXT    NOT NULL,                              -- ISO 8601
    temperatura_c        REAL,
    ocupacao             INTEGER CHECK (ocupacao >= 0),
    geracao_solar_kw     REAL    CHECK (geracao_solar_kw >= 0),
    consumo_kw           REAL    CHECK (consumo_kw >= 0),
    consumo_alto         INTEGER CHECK (consumo_alto IN (0, 1)),
    status               TEXT,
    soc_bateria_pct      REAL    CHECK (soc_bateria_pct BETWEEN 0 AND 100),
    consumo_previsto_kw  REAL,
    FOREIGN KEY (sensor_id) REFERENCES sensores (sensor_id),
    UNIQUE (sensor_id, timestamp)          -- um sensor não tem duas leituras no mesmo instante
);

-- Alertas gerados pela regra booleana: leituras com alerta = verdadeiro
CREATE TABLE IF NOT EXISTS alertas (
    alerta_id   INTEGER PRIMARY KEY AUTOINCREMENT,
    leitura_id  INTEGER NOT NULL UNIQUE,
    alerta      INTEGER NOT NULL CHECK (alerta IN (0, 1)),
    prioridade  INTEGER NOT NULL CHECK (prioridade BETWEEN 1 AND 5),
    FOREIGN KEY (leitura_id) REFERENCES leituras (leitura_id)
);

-- Índices para as consultas mais comuns
CREATE INDEX IF NOT EXISTS idx_leituras_sensor ON leituras (sensor_id);
CREATE INDEX IF NOT EXISTS idx_leituras_tempo  ON leituras (timestamp);

-- Visão que junta leituras + sensor + módulo + alerta (facilita as consultas do Python)
CREATE VIEW IF NOT EXISTS v_leituras AS
SELECT l.leitura_id, m.modulo_id, m.modulo_nome, m.modulo_tipo, m.modulo_critico,
       l.sensor_id, l.timestamp, l.temperatura_c, l.ocupacao, l.geracao_solar_kw,
       l.consumo_kw, l.consumo_alto, l.status, l.soc_bateria_pct, l.consumo_previsto_kw,
       COALESCE(a.alerta, 0) AS alerta, a.prioridade
FROM leituras l
JOIN sensores s ON s.sensor_id = l.sensor_id
JOIN modulos m ON m.modulo_id = s.modulo_id
LEFT JOIN alertas a ON a.leitura_id = l.leitura_id;