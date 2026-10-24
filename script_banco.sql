-- Tabelas da Aurora Siger (SIFSM - Fase 7) - SQLite
-- Responsável: Bruno
-- Os booleanos são guardados como 0 (falso) ou 1 (verdadeiro).

CREATE TABLE IF NOT EXISTS modulos (
    modulo_id       INTEGER PRIMARY KEY,
    modulo_nome     TEXT NOT NULL,
    modulo_tipo     TEXT NOT NULL,
    modulo_critico  INTEGER NOT NULL
);

CREATE TABLE IF NOT EXISTS sensores (
    sensor_id  TEXT PRIMARY KEY,
    modulo_id  INTEGER NOT NULL,
    FOREIGN KEY (modulo_id) REFERENCES modulos (modulo_id)
);

CREATE TABLE IF NOT EXISTS leituras (
    leitura_id           INTEGER PRIMARY KEY AUTOINCREMENT,
    sensor_id            TEXT NOT NULL,
    timestamp            TEXT NOT NULL,
    temperatura_c        REAL,
    ocupacao             INTEGER,
    geracao_solar_kw     REAL,
    consumo_kw           REAL,
    consumo_alto         INTEGER,
    status               TEXT,
    soc_bateria_pct      REAL,
    consumo_previsto_kw  REAL,
    FOREIGN KEY (sensor_id) REFERENCES sensores (sensor_id)
);

CREATE TABLE IF NOT EXISTS alertas (
    alerta_id   INTEGER PRIMARY KEY AUTOINCREMENT,
    leitura_id  INTEGER NOT NULL,
    alerta      INTEGER NOT NULL,
    prioridade  INTEGER NOT NULL,
    FOREIGN KEY (leitura_id) REFERENCES leituras (leitura_id)
);
