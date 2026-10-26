# Fase 7 - Sistema Integrado de Futuro Sustentável em Marte (SIFSM) 🚀

Protótipo da missão Aurora Siger para gestão de energia e recursos dos módulos da colônia: banco de dados com CRUD, regra booleana e circuito no Tinkercad, estruturas de dados, simulação do estado de carga da bateria, regressão linear para prever consumo e um sistema multiagente simulado.

## 👥 Integrantes
* Aelton Soares de Menezes - RM 573694
* Bruno - RM XXXXX
* Michelly - RM XXXXX
* Victor - RM XXXXX

## 📋 Pré-requisitos
* Python 3.11+
* Oracle (credenciais FIAP) ou SQLite

## 🚀 Como Rodar Localmente

1. **Clone o repositório:**
   ```bash
   git clone https://github.com/DevLounge-FIAP/fase-7-sifsm.git
   cd fase-7-sifsm
   ```

2. **Configure o ambiente virtual / dependências:**
   ```bash
   python -m venv .venv
   source .venv/bin/activate  # Linux/Mac
   # ou: .venv\Scripts\activate  # Windows
   pip install -r requirements.txt
   ```

3. **Configure as variáveis de ambiente:**
   ```bash
   cp .env.example .env
   # Edite o .env com as configurações necessárias
   ```

4. **Execute o projeto:**
   ```bash
   python codigo_fonte.py
   ```

## 📁 Arquivos da Entrega

| Arquivo | Conteúdo | Responsável |
| --- | --- | --- |
| `codigo_fonte.py` | Menu principal (CLI) | Bruno |
| `database.py`, `script_banco.sql` | Banco e CRUD | Bruno |
| `structures.py` | Hash, fila e grafo | Bruno |
| `logic_rules.py`, `circuito_logico.png`, `link_tinkercad.txt` | Regra booleana e circuito | Victor |
| `dados_aurora_siger.csv`, `gerar_dados.py` | Base de dados simulada | Michelly |
| `simulacao_computacional.py`, `ml_model.py` | Simulação e regressão | Aelton |
| `agents.py` | Sistema multiagente | Aelton |
| `relatorio_tecnico.md` | Relatório técnico | Michelly |
| `link_video.txt` | Vídeo no YouTube (não listado) | Bruno |
| `README.md` | Documentação de execução | Michelly |
| `graficos_ou_imagens/` | Gráficos e evidências | Todos |

## 🤝 Como Contribuir

* A `main` é protegida: todo código entra por Pull Request com 1 aprovação.
* Branches: `feat/`, `fix/`, `docs/`, `refactor/`.
* Commits no padrão Conventional Commits.
* Divisão de tarefas e cronograma: [`docs/divisao_fase7.md`](docs/divisao_fase7.md).
