# Roteiro do Vídeo Demonstrativo - SIFSM

**Duração total:** até 5 minutos · **Formato:** gravação de tela com narração · **Publicação:** YouTube, não listado (Aelton, 09/11)

## Como gravar o seu trecho

- Grave entre **05/11 e 06/11** e envie o arquivo ao Aelton até **06/11 às 23h** (Google Drive do grupo).
- Use a versão integrada da `main`, com o banco já carregado (opção 1 do menu).
- Resolução de 1920x1080, terminal com fonte grande (pelo menos 16 pt) e fundo escuro.
- Comece falando o seu nome e o que vai mostrar. Fale olhando para o resultado na tela, não para o código inteiro.
- Respeite o tempo indicado: o vídeo inteiro não pode passar de 5 minutos.
- Gravadores sugeridos: OBS Studio, ou a gravação de tela do próprio sistema (Win + Alt + R no Windows).

## Estrutura

| Tempo | Trecho | Quem grava | O que aparece na tela |
| --- | --- | --- | --- |
| 0:00 a 0:20 | Abertura | Aelton | Título do projeto, integrantes e o menu principal |
| 0:20 a 1:30 | Banco, CRUD e estruturas de dados | Bruno | Opções 1, 2, 3, 5 e 7 do menu |
| 1:30 a 2:40 | Regra booleana e circuito | Victor | Opção 6 do menu e circuito no Tinkercad |
| 2:40 a 3:50 | Simulação e regressão linear | Michelly | Opções 8 e 9 do menu e gráficos |
| 3:50 a 5:00 | Agentes de IA, sustentabilidade e encerramento | Aelton | Opções 10 e 11 do menu |

## Falas sugeridas

As falas são um guia; cada um pode adaptar com as próprias palavras, mantendo o tempo.

### Abertura (Aelton, 20 s)

> "Olá! Este é o SIFSM, o Sistema Integrado de Futuro Sustentável em Marte, que desenvolvemos para a missão Aurora Siger. Ele ajuda a colônia a gerenciar a energia dos seus seis módulos, três deles críticos para a vida da tripulação. Somos Aelton, Bruno, Michelly e Victor, e cada um vai mostrar uma parte do sistema, todas reunidas neste menu."

### Banco, CRUD e estruturas de dados (Bruno, 1 min 10 s)

1. **Opção 1:** carrega as 4.320 leituras do CSV no banco SQLite. Explicar em uma frase por que usamos SQLite.
2. **Opções 2 e 3:** cadastra uma leitura e lista para mostrar que ela entrou.
3. **Opção 5:** exclui um ID que não existe para mostrar o tratamento de erro, e depois exclui a leitura cadastrada.
4. **Opção 7:** busca um sensor pelo código (hash), mostra a fila de chamados por prioridade e o impacto da falha do módulo de Energia (grafo com BFS).

### Regra booleana e circuito (Victor, 1 min 10 s)

1. **Opção 6:** mostra a expressão `ALERTA = (consumo_alto E modulo_critico) OU bateria_baixa` e a tabela verdade.
2. Explica a prioridade de 1 a 5.
3. **Tinkercad:** mostra o circuito funcionando: potenciômetro como consumo, botão como módulo crítico, sensor de luz como bateria e LED acendendo no alerta. Mostrar pelo menos o caso normal e o de bateria baixa.

### Simulação e regressão linear (Michelly, 1 min 10 s)

1. **Opção 8:** roda o cenário normal e o de tempestade e compara: no normal, a bateria não cai abaixo de 51%; na tempestade, passa 34 horas abaixo de 20%.
2. Mostra o gráfico `soc_cenarios.png` e explica a regra do trapézio em uma frase.
3. **Opção 9:** treina a regressão, mostra MAE, RMSE e R² e interpreta um coeficiente (por exemplo, quanto o consumo sobe por pessoa no módulo).
4. Mostra o gráfico de valores reais vs. previstos.

### Agentes de IA, sustentabilidade e encerramento (Aelton, 1 min 10 s)

1. **Opção 10**, digitando:
   - `qual o nível da bateria?` → *handoff* para o Agente de Energia;
   - `o que acontece se a energia falhar?` → Agente de Manutenção com o impacto em cascata;
   - `desligar a habitação` → guardrail pede aprovação humana; digitar `cancelar`;
   - `qual a senha do sistema?` → guardrail de dados sensíveis.
2. **Opção 11:** mostra a análise de sustentabilidade, que junta banco, regra, fila, simulação e regressão, e termina lembrando que a decisão final é de uma pessoa.
3. **Encerramento:**

> "Na colônia, cada kWh importa. Por isso o SIFSM simula antes de agir, usa modelos leves e deixa as decisões críticas sempre com uma pessoa. Obrigado!"

## Edição (Aelton, 07/11)

- Juntar os trechos na ordem da tabela, com um cartão de 2 s com o nome do trecho e de quem apresenta.
- Cortar pausas e erros; acelerar carregamentos longos.
- Conferir o áudio de todos os trechos no mesmo volume.
- Exportar em 1080p e mandar ao grupo para revisão do corte em 07/11.
- Publicar em 09/11 como **não listado**, testar o link em uma janela anônima e preencher `link_video.txt`.
