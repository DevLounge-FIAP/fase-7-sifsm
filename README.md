# Fase 7 - Sistema Integrado de Futuro Sustentável em Marte (SIFSM) 🚀

Protótipo da missão Aurora Siger para gestão de energia e recursos dos módulos da colônia: banco de dados com CRUD, regra booleana e circuito no Tinkercad, estruturas de dados, simulação do estado de carga da bateria, regressão linear para prever consumo e um sistema multiagente simulado, tudo reunido em um menu de terminal.

## 👥 Integrantes

* Aelton Soares de Menezes - RM 573694
* Bruno Santos Martins - RM 572073
* Michelly Nunes dos Santos - RM 573625
* Victor Gonçalves Mantovani - RM 570608

## 🎬 Vídeo demonstrativo

O link do vídeo (YouTube, não listado) está em [`link_video.txt`](link_video.txt).

## 📋 Pré-requisitos

* Python 3.10 ou superior (o menu usa `match/case`)
* Nenhum servidor de banco: o projeto usa SQLite, que já vem com o Python

## 🚀 Como executar

1. **Clone o repositório** (ou extraia o `.zip` da entrega):

   ```bash
   git clone https://github.com/DevLounge-FIAP/fase-7-sifsm.git
   cd fase-7-sifsm
   ```

2. **Crie o ambiente virtual e instale as dependências:**

   ```bash
   python -m venv .venv
   source .venv/bin/activate      # Linux/Mac
   # ou: .venv\Scripts\activate   # Windows
   pip install -r requirements.txt
   ```

3. **Execute o menu:**

   ```bash
   python codigo_fonte.py
   ```

4. **Na primeira execução, escolha a opção 1** para carregar o `dados_aurora_siger.csv` no banco. O arquivo `aurora_siger.db` é criado automaticamente na pasta do projeto.

## 🧭 Opções do menu

| Opção | O que faz | Módulo |
| --- | --- | --- |
| 1 | Carrega o CSV da missão no banco | `database.py` |
| 2 a 5 | Cadastra, lista, altera e exclui leituras (CRUD) | `database.py` |
| 6 | Regra booleana do alerta e tabela verdade | `logic_rules.py` |
| 7 | Estruturas de dados: busca por hash, fila de chamados e impacto de falha (grafo + BFS) | `structures.py` |
| 8 | Simulação do estado de carga da bateria (cenário normal ou tempestade) | `simulacao_computacional.py` |
| 9 | Regressão linear: previsão de consumo e métricas | `ml_model.py` |
| 10 | Agentes de IA: triador, energia e manutenção, com guardrails e aprovação humana | `agents.py` |
| 11 | Análise de sustentabilidade da colônia, integrando os módulos | `codigo_fonte.py` |
| 0 | Sai do sistema | |

Exemplos de solicitações para a opção 10: `qual o nível da bateria?`, `quais os alertas?`, `o que acontece se a energia falhar?`, `desligar a habitação` (pede aprovação humana), `histórico`, `ajuda`. Deixe a linha em branco e pressione ENTER para voltar ao menu.

## 🧪 Testes rápidos de cada módulo

Cada módulo pode ser executado sozinho para rodar os próprios testes:

```bash
python database.py                  # CRUD e tratamento de erros
python logic_rules.py               # regra booleana, tabela verdade e prioridade
python structures.py                # hash, fila e grafo
python simulacao_computacional.py   # SoC nos dois cenários e gráficos em graficos_ou_imagens/
python ml_model.py                  # regressão linear e métricas
python agents.py                    # handoff, ferramentas, guardrails e sessão (banco temporário)
```

Para gerar novamente a base de dados simulada (semente fixa, mesmo resultado): `python gerar_dados.py`.

## 🗄️ Por que SQLite

O enunciado permite Oracle ou outro banco. Escolhemos o SQLite porque ele dispensa servidor, credenciais e VPN: qualquer pessoa que baixe o projeto consegue executar o CRUD sem configuração. O schema em [`script_banco.sql`](script_banco.sql) usa SQL padrão (tabelas `modulos`, `sensores`, `leituras` e `alertas`, com chaves estrangeiras), então pode ser migrado para Oracle com poucos ajustes de tipos.

## 📁 Arquivos da entrega

| Arquivo | Conteúdo | Responsável |
| --- | --- | --- |
| `codigo_fonte.py` | Menu principal (CLI) e integração | Bruno |
| `database.py`, `script_banco.sql` | Banco e CRUD | Bruno |
| `structures.py` | Hash, fila e grafo | Bruno |
| `logic_rules.py`, `circuito_logico.ino`, `circuito_logico.png`, `link_tinkercad.txt` | Regra booleana e circuito | Victor |
| `dados_aurora_siger.csv`, `dados_amostra.csv`, `gerar_dados.py` | Base de dados simulada | Michelly |
| `simulacao_computacional.py`, `ml_model.py` | Simulação e regressão | Michelly |
| `agents.py` | Sistema multiagente | Aelton |
| `relatorio_tecnico.md` / `.pdf` | Relatório técnico | Aelton |
| `link_video.txt` | Vídeo no YouTube (não listado) | Aelton |
| `README.md` | Documentação de execução | Aelton |
| `graficos_ou_imagens/` | Gráficos e evidências | Todos |
| `docs/` | Divisão de tarefas e roteiro do vídeo | Aelton |

## 🤝 Como contribuir

* A `main` é protegida: todo código entra por Pull Request com 1 aprovação.
* Branches: `feat/`, `fix/`, `docs/`, `refactor/`.
* Commits no padrão Conventional Commits.
* Divisão de tarefas e cronograma: [`docs/divisao_fase7.md`](docs/divisao_fase7.md).
