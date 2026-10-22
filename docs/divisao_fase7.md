# Projeto Aurora Fase 7 - Divisão de Responsabilidades

Para que o desenvolvimento ocorra sem gargalos em 18 dias (22/10 a 08/11) e sem retrabalho, os membros trabalham **em paralelo** desde o terceiro dia, apoiados em um contrato de dados e de interfaces congelado no início do projeto e em uma **amostra oficial** do dataset publicada antes de qualquer desenvolvimento. Todos os módulos são congelados em **02/11**, a integração ocorre em 03 e 04/11, o dia 09/11 fica como reserva para imprevistos e a entrega oficial é em **10/11**.

**Cenário adotado:** Sistema Integrado de Futuro Sustentável em Marte (SIFSM) focado na gestão de energia e recursos dos módulos da colônia Aurora Siger.

## Grade de Pontuação Oficial

Cada critério da grade oficial da Fase 7 tem um único responsável, para que nenhum ponto fique sem dono:

| Critério | Descrição | Peso | Responsável |
| --- | --- | --- | --- |
| Organização dos dados, banco e CRUD | Uso coerente de dados da Aurora Siger, banco de dados ou arquivos, operações de cadastro, consulta, alteração e exclusão, tratamento de erros e organização das informações. | 1,5 | Bruno |
| Circuitos lógicos e automação | Aplicação de lógica booleana, expressão lógica, regra de decisão, circuito lógico, sensores, atuadores, Arduino ou simulação no Tinkercad, quando utilizada. | 1,0 | Victor |
| Estruturas de dados em sistemas complexos | Uso adequado e justificado de listas, filas, pilhas, *hash*, árvores, grafos ou outras estruturas estudadas, conectadas ao funcionamento do protótipo. | 1,0 | Bruno |
| Simulação computacional e integração matemática | Construção ou apresentação de simulação coerente, uso de variáveis, gráficos, métodos computacionais ou conceitos de integração matemática relacionados ao problema. | 1,5 | Michelly |
| Modelagem linear e tomada de decisão | Aplicação de regressão ou modelo linear simples, análise exploratória, interpretação dos coeficientes e avaliação dos resultados. | 1,0 | Michelly |
| Integração de IA e sistemas multiagentes | Proposta coerente de agentes, ferramentas, *handoffs*, *guardrails*, sessões, RAG ou fluxos inteligentes, implementados, simulados ou descritos com clareza. | 1,0 | Aelton |
| Arquitetura computacional e desempenho | Relação entre o protótipo e CPU, GPU, NPU, TPU, memória, movimentação de dados, paralelismo, aceleração ou computação heterogênea. | 1,0 | Victor |
| Sustentabilidade, cidadania digital e impacto socioambiental | Análise conectada ao projeto sobre sustentabilidade, privacidade, impacto socioambiental, inovação responsável, diversidade e supervisão humana. | 1,0 | Aelton |
| Clareza da entrega, código e apresentação | Pasta organizada, README claro, relatório estruturado, código comentado, evidências de execução e vídeo demonstrativo objetivo. | 1,0 | Aelton (com todos) |
| **Total** | | **10,0** | |

**Pontuação por membro:** Bruno = 2,5 · Victor = 2,0 · Michelly = 2,5 · Aelton = 3,0.

O critério "Clareza da entrega" depende de todos: código comentado e mensagens claras no terminal são responsabilidade de cada autor no próprio módulo, e o Aelton responde pela pasta, README, relatório e vídeo.

## Divisão de Responsabilidades por Membro

### Membro 1 - Banco de Dados, Estruturas de Dados e Integração do Código (Bruno)

**Peso na rubrica:** 2,5 (Organização dos dados, banco e CRUD: 1,5 · Estruturas de dados em sistemas complexos: 1,0)

**Escopo técnico:** Criar o `script_banco.sql` (tabelas `modulos`, `sensores`, `leituras` e `alertas`) e o módulo `database.py`: conexão Python com Oracle (ou SQLite, justificado no README), carga do `dados_aurora_siger.csv` no banco e operações CRUD completas (`cadastrar_registro()`, `listar_registros()`, `alterar_registro()`, `excluir_registro()`) com tratamento de erros via `try`, `except`, `else` e `finally` para entradas inválidas, registros inexistentes e falhas de conexão. Implementar no módulo `structures.py`: tabela hash (`dict`) para busca de sensores e módulos por código em $O(1)$; fila FIFO (`collections.deque`) de chamados de manutenção gerados pelos alertas, ordenada por prioridade na entrada; e grafo de dependência entre módulos (lista de adjacência, ex.: energia → suporte à vida → habitação) com busca em largura (BFS) para identificar os módulos afetados quando um módulo falha. Montar desde o início a interface principal (`codigo_fonte.py`, menu interativo CLI) chamando *stubs* com as assinaturas do contrato, para que o menu rode do primeiro ao último dia e cada módulo real substitua seu *stub* sem alterar o menu, e liderar a integração.

**Agenda:**

| Período | Tarefa |
| --- | --- |
| 22/10 a 23/10 | Publica o schema do banco (tabelas e campos) |
| 24/10 a 26/10 | `script_banco.sql`, conexão Python ↔ banco, carga da amostra oficial; `codigo_fonte.py` com menu completo sobre *stubs* |
| 27/10 a 30/10 | CRUD completo com tratamento de erros sobre a base completa |
| 31/10 a 02/11 | `structures.py` (hash, fila e grafo com BFS) e nota técnica (seções 5.1 e 5.3) |
| 03/11 a 04/11 | Lidera a integração: substitui os *stubs* pelos módulos reais e roda os testes de ponta a ponta |

**Entregável:** `script_banco.sql`, `database.py`, `structures.py`, `codigo_fonte.py` integrado e nota técnica.



### Membro 2 - Lógica Embarcada e Arquitetura Computacional (Victor)

**Peso na rubrica:** 2,0 (Circuitos lógicos e automação: 1,0 · Arquitetura computacional e desempenho: 1,0)

**Escopo técnico:** Implementar o módulo `logic_rules.py` com a regra booleana da colônia:

$$ALERTA = (consumo\_alto \land modulo\_critico) \lor bateria\_baixa$$

acompanhada da tabela verdade (8 combinações) e da função `classificar_prioridade()` (escala de 1 a 5, baseada na criticidade do módulo, no SoC e no desvio entre consumo real e previsto). Aplicar a regra linha a linha sobre o CSV enriquecido para preencher as colunas `alerta` e `prioridade`. Montar o circuito equivalente no Tinkercad (Arduino, potenciômetro como leitura de consumo, botão como módulo crítico, sensor de luminosidade como nível da bateria e LED como atuador de alerta). Redigir o capítulo de Arquiteturas Modernas e Aceleração Computacional (seção 5.7), ligado ao protótipo: CPU para o CRUD e as regras, GPU/NPU para treino de modelos e inferência dos agentes, processamento paralelo nas simulações, hierarquia de memória, movimentação de dados e custo energético da computação na colônia.

**Agenda:**

| Período | Tarefa |
| --- | --- |
| 24/10 a 25/10 | `avaliar_alerta()`, expressão lógica e tabela verdade |
| 26/10 a 29/10 | Circuito no Tinkercad, `circuito_logico.png` e `link_tinkercad.txt` |
| 30/10 a 31/10 | `classificar_prioridade()` e rascunho do capítulo 5.7 |
| 02/11 | Aplica a regra ao CSV enriquecido (colunas `alerta` e `prioridade`), finaliza o capítulo 5.7 e a nota técnica (seções 5.2 e 5.7) |

**Entregável:** `logic_rules.py`, `circuito_logico.png`, `link_tinkercad.txt`, CSV final com `alerta` e `prioridade`, capítulo 5.7 e nota técnica.



### Membro 3 - Dados Simulados, Simulação Computacional e Regressão Linear (Michelly)

**Peso na rubrica:** 2,5 (Simulação computacional e integração matemática: 1,5 · Modelagem linear e tomada de decisão: 1,0)

**Escopo técnico:** Publicar a amostra oficial (`dados_amostra.csv`, cerca de 50 linhas com todas as colunas do contrato, inclusive as das etapas seguintes com valores provisórios) e, em seguida, a base completa da missão (`dados_aurora_siger.csv`) com leituras horárias simuladas dos módulos da colônia (habitação, agricultura, laboratório, suporte médico, comunicação e energia). Desenvolver o módulo `simulacao_computacional.py` (ou `.ipynb`) para simular o estado de carga (SoC) da bateria da colônia ao longo do tempo, usando integração numérica (regra do trapézio via NumPy/SciPy) sobre o balanço de potência:

$$SoC(t) = SoC_0 + \frac{1}{C}\int_0^t \left(P_{solar}(\tau) - P_{consumo}(\tau)\right)d\tau$$

Calcular a energia acumulada consumida por módulo (área sob a curva) e a média de consumo no período, comparando ao menos dois cenários (operação normal vs. tempestade de poeira com geração solar reduzida) e explicitando as limitações da simulação. Desenvolver o pipeline de regressão linear múltipla com Scikit-Learn no módulo `ml_model.py` para estimar o consumo dos módulos a partir de temperatura, ocupação e horário: análise exploratória com correlação, divisão formal entre treino e teste, interpretação dos coeficientes e cálculo obrigatório de MAE, RMSE e $R^2$. Gerar gráficos (curva de SoC por cenário, consumo acumulado, valores reais vs. previstos e resíduos) via Matplotlib exportados para a pasta `graficos_ou_imagens/`. Executar a inferência em todo o dataset e preencher as colunas reais `soc_bateria_pct` e `consumo_previsto_kw`.

**Agenda:**

| Período | Tarefa |
| --- | --- |
| 22/10 a 23/10 | Publica o formato do CSV (colunas, unidades e período simulado) |
| 24/10 (até 12h) | Publica `dados_amostra.csv` no repositório (**marco M0**) |
| 24/10 a 26/10 | Gera `dados_aurora_siger.csv` completo |
| 27/10 | Publica a base completa (**marco M1**) |
| 27/10 a 29/10 | Simulação do SoC e comparação de cenários |
| 30/10 a 01/11 | Regressão linear: exploração, treino/teste, coeficientes e métricas; publica o CSV enriquecido com `soc_bateria_pct` e `consumo_previsto_kw` reais (**marco M2**, 01/11) |
| 02/11 | Gráficos finais exportados e nota técnica (seções 5.4 e 5.5) |

**Entregável:** `dados_amostra.csv`, `dados_aurora_siger.csv`, `simulacao_computacional.py` (ou `.ipynb`), `ml_model.py`, gráficos em `graficos_ou_imagens/`, CSV enriquecido e nota técnica.



### Membro 4 - IA, Sustentabilidade, Documentação e Entrega (Aelton)

**Peso na rubrica:** 3,0 (Integração de IA e sistemas multiagentes: 1,0 · Sustentabilidade, cidadania digital e impacto socioambiental: 1,0 · Clareza da entrega, código e apresentação: 1,0)

**Escopo técnico:** Criar o repositório com a estrutura de pastas da entrega e consolidar o contrato de dados e de interfaces. Implementar no módulo `agents.py` a simulação de um sistema multiagente: agente triador que interpreta a solicitação da tripulação e faz *handoff* para o agente de energia ou o agente de manutenção; ferramentas determinísticas que consultam o banco e as estruturas (`consultar_soc()`, `listar_alertas()`, `impacto_falha()`); *guardrails* que bloqueiam ações fora do escopo e o desligamento de módulos críticos sem aprovação humana; e histórico de sessão. Redigir o capítulo de Sustentabilidade, Cidadania Digital e Impacto Socioambiental (seção 5.8), conectado ao protótipo e cobrindo: simulação evitando desperdício, privacidade dos dados da tripulação, impacto ambiental de *data centers* e IA, inovação responsável avaliando benefícios e riscos, diversidade e inclusão na concepção dos agentes, e supervisão humana sobre as decisões dos agentes, já que a grade cobra explicitamente diversidade e supervisão humana. Consolidar o `relatorio_tecnico.md/.pdf` a partir das notas técnicas, escrever o `README.md` (dependências e modo de execução), roteirizar e editar o vídeo de 5 minutos, publicá-lo no YouTube como não listado, preencher `link_video.txt` e empacotar o `.zip` final.

**Agenda:**

| Período | Tarefa |
| --- | --- |
| 22/10 a 23/10 | Repositório com a estrutura de pastas da entrega; contrato de dados e de interfaces consolidado e congelado |
| 24/10 a 29/10 | `agents.py`: triador, especialistas, ferramentas, *handoff*, *guardrails* e histórico, sobre os *stubs* do contrato |
| 30/10 a 01/11 | Capítulo 5.8 |
| 02/11 | Esqueleto do relatório e roteiro do vídeo (~1 min 15 s por membro) |
| 03/11 a 04/11 | README e apoio à integração liderada pelo Bruno |
| 05/11 a 06/11 | Consolida o relatório com as notas técnicas; grava seu trecho do vídeo |
| 07/11 | Edita o vídeo |
| 09/11 | Publica o vídeo, preenche `link_video.txt`, testa a execução pelo README e zipa o projeto |

**Entregável final:** `agents.py`, capítulo 5.8 e o pacote `.zip` completo contendo o executável CLI unificado, o script do banco, a base de dados, a simulação, o circuito lógico, os gráficos, o relatório técnico, o README e o link do vídeo.



## Cronograma Consolidado

| Período | Bruno | Victor | Michelly | Aelton |
| --- | --- | --- | --- | --- |
| **22/10 a 23/10** | Schema do banco | Alinhamento | Formato do CSV | Repositório e contrato |
| **24/10 a 26/10** | Banco, carga da amostra e menu sobre *stubs* | Regra booleana e tabela verdade; início do Tinkercad | Amostra (M0) e base completa | `agents.py` |
| **27/10 a 31/10** | CRUD e erros; início das estruturas | Tinkercad; prioridade; rascunho 5.7 | Base (M1), simulação, regressão | `agents.py`; capítulo 5.8 |
| **01/11 a 02/11** | Estruturas e nota técnica | Aplica regra ao CSV; 5.7 e nota técnica | CSV enriquecido (M2), gráficos e nota técnica | Capítulo 5.8; relatório e roteiro |
| **03/11 a 04/11** | **Integração de ponta a ponta** | Correções da integração | Correções da integração | README; apoio à integração |
| **05/11 a 06/11** | Grava trecho do vídeo | Grava trecho do vídeo | Grava trecho do vídeo | Consolida relatório; grava trecho |
| **07/11** | Revisa o corte | Revisa o corte | Revisa o corte | Edita o vídeo |
| **08/11** | Revisão cruzada | Revisão cruzada | Revisão cruzada | Revisão cruzada |
| **09/11** | Reserva | Reserva | Reserva | Publica vídeo e zipa |
| **10/11** | **Entrega oficial** | | | |

### Marcos de Controle

| Marco | Data | Responsável | Critério de conclusão |
| --- | --- | --- | --- |
| **M0** | 24/10 (até 12h) | Michelly | `dados_amostra.csv` no repositório com todas as colunas do contrato |
| **M1** | 27/10 | Michelly e Victor | Base completa publicada; `avaliar_alerta()` testada |
| **M2** | 01/11 | Michelly | CSV com `soc_bateria_pct` e `consumo_previsto_kw` reais publicado |
| **Congelamento** | 02/11 | Todos | Módulos entregues como funções importáveis + notas técnicas |
| **Integração** | 04/11 | Bruno | Menu executando todas as opções com os módulos reais |
| **Entrega** | 10/11 | Aelton | `.zip` enviado e link do vídeo funcionando |

### Revisão Cruzada (08/11)

Cada membro confere a parte de outro contra os critérios da grade oficial: Bruno revisa Michelly, Michelly revisa Aelton, Aelton revisa Victor e Victor revisa Bruno.

## Contrato de Independência Técnica

Para garantir o desenvolvimento paralelo sem retrabalho entre os membros:

### Contrato de Dados (Dataset Pipeline)

O schema completo do `dados_aurora_siger.csv` é congelado em 23/10 e publicado já preenchido na amostra oficial de 24/10. As colunas das etapas seguintes existem desde a amostra com valores provisórios e são substituídas pelos valores reais conforme os marcos:

- **Geradas pela Michelly (M0/M1):** `timestamp` (str ISO 8601), `modulo_id` (int), `modulo_nome` (str), `modulo_tipo` (str), `modulo_critico` (bool), `sensor_id` (str), `temperatura_c` (float), `ocupacao` (int), `geracao_solar_kw` (float), `consumo_kw` (float), `consumo_alto` (bool), `status` (str).
- **Preenchidas pela Michelly (M2):** `soc_bateria_pct` (float), `consumo_previsto_kw` (float).
- **Preenchidas pelo Victor (congelamento):** `alerta` (bool, resultado da regra booleana) e `prioridade` (int de 1 a 5).

Nenhuma coluna é renomeada ou removida depois de 23/10. Uma coluna nova só entra com acordo de todos e registro no README. O banco de dados espelha a base: o Bruno faz a carga, o menu final usa o banco para as operações CRUD e o CSV serve de contrato entre os módulos.

### Contrato de Interfaces

As assinaturas abaixo são congeladas em 23/10. O Bruno cria um *stub* para cada uma no `codigo_fonte.py`, e cada membro entrega a implementação real com o mesmo nome e os mesmos parâmetros:

| Módulo | Funções públicas | Responsável |
| --- | --- | --- |
| `database.py` | `conectar()`, `cadastrar_registro(dados)`, `listar_registros(filtro=None)`, `alterar_registro(id, dados)`, `excluir_registro(id)` | Bruno |
| `structures.py` | `buscar_sensor(codigo)`, `enfileirar_chamado(alerta)`, `proximo_chamado()`, `impacto_falha(modulo_id) -> list` | Bruno |
| `logic_rules.py` | `avaliar_alerta(consumo_alto, modulo_critico, bateria_baixa) -> bool`, `tabela_verdade() -> list`, `classificar_prioridade(linha) -> int` | Victor |
| `simulacao_computacional.py` | `simular_soc(df, cenario) -> DataFrame`, `energia_acumulada(df, modulo_id) -> float` | Michelly |
| `ml_model.py` | `treinar_modelo(df) -> modelo`, `avaliar_modelo(modelo, df) -> dict`, `prever_consumo(modelo, df) -> DataFrame` | Michelly |
| `agents.py` | `agente_triador(solicitacao, sessao) -> str` | Aelton |

### Isolamento e Reutilização dos Módulos

Cada integrante desenvolve seu script com as funções do contrato acompanhadas de um bloco `if __name__ == "__main__":` com testes rápidos, garantindo que o código rode de forma independente sobre a amostra oficial antes de ser integrado. Junto com o código, cada membro entrega uma nota técnica curta da sua seção para que o relatório seja consolidado sem reescrita.

### Plano de Contingência

- Se um marco atrasar até 1 dia, os demais seguem sobre a amostra oficial sem impacto.
- Se atrasar mais de 1 dia, o Aelton apoia o responsável na finalização do módulo atrasado, e o dia 09/11 é usado como reserva.
- Nenhum membro altera o código de outro: correções na integração são pedidas ao responsável, que as faz no próprio módulo.

### Empacotamento Centralizado

Na integração (03/11 a 04/11), o Bruno substitui os *stubs* pelos imports reais (`from database import ...`, `from structures import ...`, `from logic_rules import ...`, `from simulacao_computacional import ...`, `from ml_model import ...`, `from agents import ...`) dentro do script central `codigo_fonte.py`, expondo todas as funcionalidades no menu do terminal, incluindo a opção "Analisar sustentabilidade da colônia", sem alterar a lógica interna desenvolvida pelos demais. Em seguida, o Aelton empacota a entrega final.
