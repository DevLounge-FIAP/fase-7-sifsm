# Relatório Técnico - SIFSM

Sistema Integrado de Futuro Sustentável em Marte (SIFSM) - Missão Aurora Siger, Fase 7.

| Integrante | RM | Responsabilidade principal |
| --- | --- | --- |
| Aelton Soares de Menezes | 573694 | IA e sistemas multiagentes, sustentabilidade, documentação e entrega |
| Bruno Santos Martins | 572073 | Banco de dados, CRUD, estruturas de dados e integração do menu |
| Michelly Nunes dos Santos | 573625 | Base de dados simulada, simulação computacional e modelagem linear |
| Victor Gonçalves Mantovani | 570608 | Lógica booleana, circuito no Tinkercad e arquitetura computacional |

## 1. Contexto da solução

A colônia Aurora Siger depende de um único sistema de energia, formado por painéis solares e por uma bateria, para manter seis módulos funcionando: Habitação, Agricultura, Laboratório, Suporte Médico, Comunicação e Energia. Três deles (Habitação, Suporte Médico e Energia) são críticos, porque sustentam diretamente a vida da tripulação. Em Marte, a geração solar varia ao longo do sol (o dia marciano) e cai durante tempestades de poeira, então qualquer desperdício de energia ou atraso em um alerta pode comprometer a missão.

O SIFSM é um protótipo de linha de comando que reúne, em um único menu, as ferramentas para a equipe de solo e a tripulação acompanharem essa operação:

- registrar e consultar as leituras dos sensores (banco de dados com CRUD);
- decidir quando uma leitura gera alerta (regra booleana, também montada como circuito no Tinkercad);
- organizar os chamados e calcular o efeito em cascata de uma falha (estruturas de dados);
- prever o estado de carga da bateria em diferentes cenários (simulação por integração numérica);
- estimar o consumo esperado de cada módulo (regressão linear);
- responder às solicitações da tripulação com agentes especializados, sob supervisão humana (sistema multiagente);
- avaliar o impacto sustentável e social das decisões tomadas pelo sistema.

## 2. Objetivos

1. Integrar em um protótipo funcional os conteúdos da Fase 7: banco de dados, lógica, estruturas de dados, simulação, modelagem linear, IA, arquitetura computacional e sustentabilidade.
2. Usar uma única base de dados da missão como contrato entre os módulos, para que cada parte possa ser desenvolvida de forma independente e integrada no final.
3. Apoiar a decisão humana, sem substituí-la: o sistema recomenda, e as ações críticas dependem de aprovação de uma pessoa responsável.

## 3. Arquitetura da solução

```text
dados_aurora_siger.csv ──► database.py (SQLite + CRUD) ──► codigo_fonte.py (menu CLI)
                                   │                              │
                 ┌─────────────────┼──────────────┬───────────────┼──────────────┐
                 ▼                 ▼              ▼               ▼              ▼
          structures.py     logic_rules.py  simulacao_       ml_model.py     agents.py
          hash, fila,       regra booleana  computacional.py regressão       triador +
          grafo + BFS       e prioridade    SoC (trapézio)   linear          especialistas
```

O CSV é o contrato de dados: suas colunas foram congeladas no início do projeto, e cada etapa preenche as colunas sob sua responsabilidade (`soc_bateria_pct` e `consumo_previsto_kw` pela simulação e pela regressão, `alerta` e `prioridade` pela regra lógica). O banco espelha o CSV, e o menu `codigo_fonte.py` chama as funções públicas de cada módulo, cujas assinaturas também foram congeladas no início (ver `docs/divisao_fase7.md`).

## 4. Dados da missão

A base `dados_aurora_siger.csv` é gerada pelo script `gerar_dados.py` com semente fixa (`random_seed=42`), o que torna os resultados reproduzíveis. Ela contém leituras horárias dos 6 módulos durante 30 dias (720 horas), totalizando 4.320 registros, a partir de 14/10/2026. A amostra `dados_amostra.csv` (48 linhas) serviu de base para o desenvolvimento paralelo.

| Grupo de colunas | Colunas |
| --- | --- |
| Identificação | `timestamp`, `modulo_id`, `modulo_nome`, `modulo_tipo`, `modulo_critico`, `sensor_id` |
| Leituras | `temperatura_c`, `ocupacao`, `geracao_solar_kw`, `consumo_kw`, `consumo_alto`, `status` |
| Simulação e regressão | `soc_bateria_pct`, `consumo_previsto_kw` |
| Regra lógica | `alerta`, `prioridade` |

A geração solar segue uma curva diária (0 kW à noite e até 90 kW ao meio-dia), reduzida em até 10% pela poeira. O consumo de cada módulo combina uma carga base, a ocupação, o turno de trabalho e o aquecimento necessário quando a temperatura fica abaixo da temperatura de conforto. Nenhuma coluna identifica pessoas: a ocupação é apenas a contagem de tripulantes no módulo.

## 5. Desenvolvimento

### 5.1 Banco de dados e CRUD (Bruno)

> *A consolidar a partir da nota técnica do Bruno (prevista para 02/11): modelo das tabelas `modulos`, `sensores`, `leituras` e `alertas`, carga do CSV, operações de cadastro, consulta, alteração e exclusão, tratamento de erros e justificativa do SQLite.*

### 5.2 Regra lógica e circuito (Victor)

> *A consolidar a partir da nota técnica do Victor (prevista para 02/11): expressão $ALERTA = (consumo\_alto \land modulo\_critico) \lor bateria\_baixa$, tabela verdade, `classificar_prioridade()` e circuito no Tinkercad com as evidências dos 5 testes.*

### 5.3 Estruturas de dados (Bruno)

> *A consolidar a partir da nota técnica do Bruno (prevista para 02/11): tabela hash de sensores e módulos, fila de chamados por prioridade e grafo de dependência com busca em largura.*

### 5.4 Simulação computacional e integração matemática (Michelly)

> *A consolidar a partir da nota técnica da Michelly (prevista para 02/11): modelo do SoC pela regra do trapézio, cenários normal e tempestade, energia acumulada por módulo, gráficos e limitações.*

### 5.5 Modelagem linear e tomada de decisão (Michelly)

> *A consolidar a partir da nota técnica da Michelly (prevista para 02/11): análise exploratória, divisão treino/teste, coeficientes, MAE, RMSE, $R^2$ e gráficos de valores reais vs. previstos e resíduos.*

### 5.6 Integração de IA e sistemas multiagentes (Aelton)

O módulo `agents.py` simula um sistema multiagente que atende às solicitações da tripulação em linguagem natural (por exemplo, "qual o nível da bateria?" ou "o que acontece se a energia falhar?"). Ele segue os conceitos dos frameworks de agentes: **agentes** com papéis definidos, **ferramentas**, **handoffs**, **guardrails** e **sessões**. Os agentes são implementados por regras, sem modelo de linguagem, como se discute ao final desta seção.

**Agentes e handoff.** A função pública do contrato, `agente_triador(solicitacao, sessao)`, recebe o texto da tripulação, normaliza-o (minúsculas e sem acentos, para aceitar "Habitação" e "habitacao") e identifica a intenção por raízes de palavras. Em seguida, faz o *handoff* para um dos dois especialistas:

| Agente | Responde a | Exemplo de solicitação |
| --- | --- | --- |
| Triador | Comandos da sessão (`ajuda`, `histórico`, `aprovar`, `cancelar`) e encaminhamento | "histórico" |
| Agente de Energia | Estado de carga da bateria e pedidos de desligamento de módulos | "desligar o laboratório" |
| Agente de Manutenção | Alertas pendentes e impacto da falha de um módulo | "o que acontece se a energia falhar?" |

Toda resposta indica o caminho percorrido (por exemplo, `[Triador -> Agente de Manutenção]`), o que torna o *handoff* visível para quem usa o sistema.

**Ferramentas.** Os especialistas só agem por meio de ferramentas determinísticas e **somente de leitura**, que reutilizam os outros módulos do projeto:

- `consultar_soc()`: lê no banco o SoC da leitura mais recente e usa `bateria_esta_baixa()` do `logic_rules.py`, com o mesmo limite de 20% da regra booleana e da simulação;
- `listar_alertas()`: busca os chamados na fila de prioridade do `structures.py` ou, se ela estiver vazia, os alertas do banco, ordenados por prioridade;
- `impacto_falha()`: usa o grafo de dependência e a busca em largura do `structures.py` para listar os módulos afetados por uma falha, com o nível de distância (por exemplo, uma falha em Energia atinge Suporte Médico, Agricultura, Laboratório e Comunicação no nível 1 e Habitação no nível 2).

Quando a bateria está abaixo do limite, o Agente de Energia sugere reduzir as cargas **não críticas** (Agricultura, Laboratório e Comunicação), em vez de qualquer módulo que sustente a vida.

**Guardrails.** Antes de qualquer *handoff*, o triador aplica guardrails de entrada, e o Agente de Energia aplica um guardrail de ação:

| Guardrail | O que bloqueia | Resposta |
| --- | --- | --- |
| Entrada vazia ou longa demais | Textos vazios ou com mais de 300 caracteres | Pede uma solicitação válida |
| Dados sensíveis | Senhas, credenciais, CPF, prontuário, dados médicos ou pessoais | Encaminha ao responsável humano |
| Alteração de dados | Pedidos para apagar, excluir ou remover registros | Lembra que alterações são feitas por uma pessoa no menu CRUD |
| Fora do escopo | Qualquer pedido sem relação com energia ou manutenção | Lista o que os agentes sabem fazer |
| Módulo crítico | Desligar Habitação, Suporte Médico ou Energia | Mostra o impacto da falha e deixa a ação pendente até alguém digitar `aprovar` ou `cancelar` |

Mesmo uma ação aprovada é apenas registrada: o protótipo não aciona atuadores, o que deixa claro que a execução física fica a cargo da equipe.

**Sessão.** O histórico da conversa é uma lista de turnos (solicitação, agente que respondeu, resposta e ação pendente). Ele permite consultar o `histórico` e liga a aprovação humana ao pedido que a originou: `aprovar` só vale para a última ação pendente e não pode ser usada duas vezes. O menu cria uma sessão nova a cada conversa.

**Evidências.** O bloco de testes do módulo (`python agents.py`) monta um banco temporário e verifica 15 turnos de conversa: as duas ferramentas, os quatro tipos de *handoff*, os seis guardrails, a aprovação, o cancelamento e o histórico. Todos os testes passam, e os agentes podem ser usados pela opção 10 do menu.

**Por que agentes por regras.** Um modelo de linguagem entenderia frases mais livres, mas exigiria inferência em GPU ou conexão com a Terra, que pode ter de 4 a 24 minutos de atraso de comunicação. As regras dão respostas previsíveis e auditáveis, rodam em CPU e sem conexão e não gastam energia com inferência, o que é coerente com a escassez de energia da colônia (ver seção 5.8). A arquitetura permite evoluir sem mudar o contrato: um modelo de linguagem poderia substituir apenas a etapa de classificação de intenção do triador, mantendo as mesmas ferramentas e os mesmos guardrails. Outra melhoria seria um fluxo de RAG sobre os manuais de manutenção dos módulos, para que o Agente de Manutenção explique como resolver cada alerta.

### 5.7 Arquitetura computacional e desempenho (Victor)

> *A consolidar a partir do capítulo 5.7 do Victor (previsto para 02/11): CPU, GPU/NPU/TPU, paralelismo, hierarquia de memória, movimentação de dados e custo energético da computação na colônia.*

### 5.8 Sustentabilidade, cidadania digital e impacto socioambiental (Aelton)

Em uma colônia marciana, sustentabilidade não é um tema à parte: a energia disponível é limitada, não há como repor peças rapidamente e cada decisão automatizada afeta diretamente a vida da tripulação. Esta seção analisa como o SIFSM trata essas questões e o que cada escolha do protótipo ensina para sistemas semelhantes na Terra.

#### 5.8.1 Simulação para evitar desperdício

A simulação do estado de carga (seção 5.4) permite testar decisões antes de executá-las. Nos 30 dias simulados, os painéis geram cerca de 17.105 kWh, e os módulos consomem cerca de 13.602 kWh. No cenário normal, a bateria nunca fica abaixo de 51%. No cenário com tempestades de poeira, ela passa 34 horas abaixo do limite de 20% e 12 horas descarregada. Sem a simulação, a equipe só perceberia o problema quando ele já estivesse acontecendo. Com ela, pode planejar com antecedência, por exemplo reduzindo as cargas não críticas antes da tempestade ou adiando atividades do laboratório.

A energia acumulada por módulo também mostra onde agir: Habitação (cerca de 2.977 kWh) e Agricultura (cerca de 2.615 kWh) são os maiores consumidores, enquanto Comunicação e Energia consomem cerca de metade disso. A regressão linear (seção 5.5) completa essa análise ao comparar o consumo real com o previsto: um consumo bem acima do previsto indica desperdício ou defeito, e esse desvio entra no cálculo da prioridade do alerta.

O mesmo raciocínio vale para a Terra: simular o balanço entre geração renovável e consumo é o que permite a microrredes solares, hospitais e comunidades isoladas economizar energia e evitar apagões (ODS 7, energia limpa e acessível, e ODS 12, consumo e produção responsáveis).

#### 5.8.2 Privacidade e proteção dos dados da tripulação

A base de dados foi desenhada para não guardar dados pessoais: a ocupação é apenas a contagem de pessoas em cada módulo, sem nomes, horários individuais ou dados de saúde. Esse é o princípio da minimização de dados da LGPD (Lei 13.709/2018): coletar apenas o necessário para a finalidade, que aqui é a gestão de energia.

Os agentes reforçam essa proteção: o guardrail de dados sensíveis recusa pedidos sobre senhas, credenciais, CPF, prontuários e dados médicos ou pessoais e encaminha o pedido ao responsável humano. As ferramentas dos agentes só leem o banco e não podem alterar nem excluir registros. As configurações sensíveis (como credenciais de banco) ficam fora do repositório, porque o `.gitignore` bloqueia arquivos `.env`, chaves e o próprio banco local.

Em uma versão real, a contagem de ocupação vinda de sensores de presença poderia, combinada com horários, revelar a rotina de cada tripulante. Por isso, a recomendação é agregar os dados por módulo e por hora, como faz o protótipo, e definir quem pode consultá-los.

#### 5.8.3 Impacto ambiental de data centers e da IA

Treinar e executar modelos de IA consome energia, água para resfriamento de *data centers* e hardware com minerais escassos. Na colônia, esse custo é ainda mais visível, porque cada kWh gasto com computação deixa de ir para o suporte à vida. O SIFSM foi pensado para ter baixo custo computacional:

- os agentes funcionam por regras, sem inferência de modelo de linguagem;
- a regressão linear treina em segundos em CPU, sem GPU;
- a simulação usa integração numérica simples sobre 720 pontos;
- o banco SQLite é um arquivo local, sem servidor ligado o tempo todo.

A escolha segue o princípio de usar o modelo mais simples que resolve o problema. Uma solução de IA mais pesada só se justificaria se o ganho de qualidade superasse o custo energético, comparação que o capítulo 5.7 detalha do ponto de vista do hardware.

#### 5.8.4 Inovação responsável: benefícios e riscos

| Benefício | Risco | Como o protótipo mitiga |
| --- | --- | --- |
| Alertas automáticos e priorizados | Excesso de confiança no alerta ou falso negativo | Regra simples e auditável (tabela verdade); prioridade explicada por critérios públicos |
| Previsão de consumo e de SoC | Modelo errar fora das condições simuladas | Métricas MAE, RMSE e $R^2$ publicadas; limitações declaradas no relatório |
| Agentes que respondem em linguagem natural | Ação indevida tomada por um agente | Ferramentas só de leitura; desligamento de módulo crítico exige aprovação humana |
| Cálculo do impacto em cascata de uma falha | Grafo de dependência desatualizado | Dependências declaradas em um único lugar (`structures.py`), fáceis de revisar |
| Dados centralizados em banco | Vazamento ou uso indevido dos dados | Minimização de dados; nenhum dado pessoal na base |

A concentração de alertas no módulo de Energia, que é crítico e tem picos de consumo, também é um aprendizado: uma regra única pode gerar alertas demais em um módulo e "cansar" a equipe, e por isso a prioridade de 1 a 5 é necessária para ordenar o atendimento.

#### 5.8.5 Diversidade e inclusão na concepção dos agentes

Uma tripulação de missão longa reúne pessoas de idiomas, formações e capacidades diferentes, e o sistema precisa servir a todas elas:

- o triador aceita texto com ou sem acentos e com variações de palavras ("desligar", "desligue", "corte"), para não exigir uma forma "correta" de escrever;
- as respostas usam linguagem simples, sem jargão técnico, e sempre dizem o que o agente pode fazer quando não entende o pedido;
- a interface de texto no terminal funciona com leitores de tela;
- as decisões dos agentes dependem da situação dos módulos, nunca do perfil de quem pergunta, o que evita tratar tripulantes de forma diferente.

O desenvolvimento em equipe, com quatro integrantes revisando o trabalho uns dos outros (revisão cruzada), também ajuda a reduzir pontos cegos de quem projeta o sistema. Como melhoria, os agentes poderiam ser testados com usuários de perfis diferentes e oferecer respostas em outros idiomas e em áudio.

#### 5.8.6 Supervisão humana sobre as decisões

O princípio central do SIFSM é que **o sistema recomenda e a pessoa decide**:

- os agentes não alteram nem excluem dados; o CRUD é usado por uma pessoa no menu;
- o desligamento de um módulo crítico fica pendente até que o responsável de turno digite `aprovar` ou `cancelar`, depois de ver quais módulos seriam afetados;
- mesmo depois de aprovada, a ação é apenas registrada, e a execução física continua com a equipe;
- a opção "Analisar sustentabilidade da colônia" termina sempre com o lembrete de que a decisão final deve ser validada por uma pessoa responsável;
- o histórico de sessão registra quem pediu o quê e qual agente respondeu, o que permite auditar as decisões depois.

Essa supervisão segue o que diretrizes de IA responsável, como o AI Act europeu e a Recomendação da UNESCO sobre a Ética da IA, exigem para sistemas de alto risco: transparência, rastreabilidade e controle humano efetivo.

#### 5.8.7 Cidadania digital

O protótipo trata a tecnologia como apoio à comunidade da colônia, e não como substituto da responsabilidade humana: os dados servem à segurança coletiva, as regras são públicas e explicáveis, e cada tripulante pode questionar uma recomendação do sistema. Na Terra, os mesmos princípios valem para cidades inteligentes e redes elétricas: transparência sobre o que é coletado, proteção dos dados das pessoas e participação humana nas decisões automatizadas.

## 6. Resultados e evidências

> *A consolidar em 05 a 07/11 com os resultados finais de cada módulo e as figuras de `graficos_ou_imagens/`: prints do circuito (5 testes), curva de SoC por cenário, consumo acumulado por módulo, gráficos da regressão e execução do menu integrado.*

## 7. Limitações e possíveis melhorias

### Limitações

- Os dados são simulados por um gerador com padrões fixos; sensores reais teriam ruído, falhas e sazonalidade marciana.
- A simulação considera uma bateria ideal de 500 kWh, sem perdas de carga e descarga nem degradação.
- A regressão linear supõe relações lineares entre temperatura, ocupação, horário e consumo.
- A regra booleana concentra boa parte dos alertas de consumo no módulo de Energia.
- Os agentes entendem apenas as intenções previstas nas regras de palavras-chave e não interpretam frases ambíguas.
- O banco SQLite é local e não atende vários usuários ao mesmo tempo.

### Possíveis melhorias

- Modelo de bateria com eficiência e degradação, e simulação de estratégias de corte de carga durante tempestades.
- Modelos que capturem relações não lineares, avaliados contra o custo energético de treino.
- Classificação de intenção com um modelo de linguagem pequeno, executado localmente, e RAG sobre os manuais de manutenção.
- Banco de dados em servidor (Oracle ou PostgreSQL), com controle de acesso por perfil.
- Testes de uso com tripulantes de perfis diversos e respostas em outros idiomas e em áudio.

## 8. Conclusão

> *A consolidar em 05 a 07/11, após a integração.*

## Referências

- BRASIL. Lei nº 13.709, de 14 de agosto de 2018. Lei Geral de Proteção de Dados Pessoais (LGPD).
- NAÇÕES UNIDAS. Objetivos de Desenvolvimento Sustentável (ODS 7, 12 e 13).
- UNESCO. Recomendação sobre a Ética da Inteligência Artificial, 2021.
- UNIÃO EUROPEIA. Regulamento (UE) 2024/1689 (AI Act).
- FIAP. Material da Fase 7 do curso.
