# Checklist de Entrega - SIFSM

Roteiro das etapas finais (Aelton): revisão cruzada, teste pelo README, empacotamento e envio.

## 08/11 - Revisão cruzada da parte do Victor

Conferir contra a grade oficial (Circuitos lógicos e automação; Arquitetura computacional e desempenho):

- [ ] `logic_rules.py`: expressão `ALERTA = (consumo_alto ∧ modulo_critico) ∨ bateria_baixa` comentada no código
- [ ] `tabela_verdade()` retorna as 8 combinações, coerentes com `avaliar_alerta()`
- [ ] `classificar_prioridade()` retorna 1 a 5 e segue a regra documentada (base 1 sem alerta; com alerta, 2 + crítico + bateria < 20% + consumo 20% acima do previsto, teto 5)
- [ ] `python logic_rules.py` roda sem erro
- [ ] CSV final: nenhuma linha com `alerta` verdadeiro e `prioridade` vazia; colunas não renomeadas
- [ ] Limite de bateria baixa igual a 20% no `logic_rules.py` e na simulação
- [ ] `circuito_logico.png`, `circuito_logico.ino` e `link_tinkercad.txt` presentes; o link abre o circuito
- [ ] Prints dos 5 testes em `graficos_ou_imagens/`, com legenda
- [ ] Capítulo 5.7 cita CPU, GPU/NPU/TPU, memória, movimentação de dados, paralelismo e custo energético, sempre ligados ao protótipo
- [ ] Nota técnica 5.2 coerente com o código (mesmos nomes de funções e limites)

Registrar os apontamentos como comentário no PR ou mensagem ao Victor; ele faz as correções no próprio módulo.

## 09/11 - Teste pelo README

Em uma pasta nova, simulando o avaliador:

```bash
git clone https://github.com/DevLounge-FIAP/fase-7-sifsm.git teste-entrega
cd teste-entrega
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
python codigo_fonte.py
```

- [ ] Instalação sem erro a partir do `requirements.txt`
- [ ] Opções 1 a 11 do menu executam sem `[EM CONSTRUÇÃO]` e sem exceção
- [ ] Os testes de cada módulo (seção "Testes rápidos" do README) passam
- [ ] `link_video.txt` preenchido; o link abre em janela anônima e o vídeo está como não listado
- [ ] RMs dos quatro integrantes no README e no relatório
- [ ] `relatorio_tecnico.pdf` gerado a partir do `.md` final, com as figuras visíveis

## 09/11 - Empacotamento

Gerar o `.zip` a partir da `main` atualizada, sem `.venv`, banco local nem arquivos ignorados pelo `.gitignore`:

```bash
git switch main && git pull
git archive --format=zip --prefix=fase-7-sifsm/ -o fase7_sifsm.zip main
```

Conferir o conteúdo do `.zip`:

- [ ] `codigo_fonte.py` e todos os módulos `.py`
- [ ] `script_banco.sql`, `dados_aurora_siger.csv`, `dados_amostra.csv`
- [ ] `circuito_logico.png`, `circuito_logico.ino`, `link_tinkercad.txt`
- [ ] `graficos_ou_imagens/` completa
- [ ] `relatorio_tecnico.md` e `relatorio_tecnico.pdf`
- [ ] `README.md`, `requirements.txt`, `link_video.txt`

Se o `.pdf` não estiver versionado, adicioná-lo ao `.zip` depois do `git archive`.

## 10/11 - Envio

- [ ] Enviar o `.zip` na plataforma da FIAP
- [ ] Conferir se o arquivo enviado abre e se o link do vídeo funciona
- [ ] Avisar o grupo que a entrega foi feita
