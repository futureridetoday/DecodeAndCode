---
# about
name: backlog
type: doc
project: DecodeAndCode
description: Onde problema, ideia e feature ficam registrados antes de virarem plano
tags: [backlog, decode-and-code, pre-plano]

# history
author: Bortoli
created: 2026-08-22
status: draft
version: 1.0.0
updated: 2026-08-22

# system
scope: project
auto_load: false
dependencies: []
---

# Backlog

Onde problema, ideia e feature ficam registrados **antes** de virarem plano.

O modelo começa no plano, e plano já é um compromisso: nome, alvo declarado, independência
argumentada, escopo em unidades. Muita coisa que vale registrar ainda não merece esse custo — ou
porque não está madura, ou porque ninguém decidiu se vai ser feita. Sem um lugar antes do plano,
essas coisas vivem em conversa e se perdem.

## O que isto não é

- **Não é plano.** Item daqui não tem `plan_id`, não recebe número, não entra em
  [`_planos.md`](../_planos.md) e não segue o formato de plano.
- **Não é projeção de script.** O arquivo é escrito à mão, inteiro. Em particular, **não usar os
  marcadores `<!-- backlog:start -->` / `<!-- backlog:end -->`** aqui: eles pertencem ao
  `backlog.py`, que projeta o backlog de *unidades* dentro do arquivo de um plano. Nome igual,
  mecanismo oposto — e o script sobrescreve o miolo sem perguntar.
- **Não é lista de tarefas.** Tarefa de execução vive na unidade, com contrato e critério de aceite.

## Problemas abertos

| # | Item | Tipo | Prioridade | Autor | Core | Data de inclusão | Onde vive |
|---|---|---|---|---|---|---|---|
| B-01 | **Checagem de consistência entre normas.** A doc do Claude Code afirma que instruções contraditórias fazem o modelo escolher arbitrariamente. Com `CLAUDE.md` + norma + princípios + N guidelines ativas, a superfície de contradição cresce e nada a mede. **Gatilho, e é mecânico:** escrever quando **duas rules ativas casarem o mesmo path** — condição observável, não impressão. A unidade `05` (`activation-notice`) já vê todo carregamento e é o detector natural, sem construir nada. É a `L-05` do plano em curso | problema | — | Claude | model | 2026-08-22 | `.claude/rules/` |
| B-02 | **Verificador de invariantes de guideline.** Nasce como instrução em markdown e sem oráculo. **Quando escrever:** na primeira divergência observada entre duas instalações, não numa data. É a exclusão declarada no *Escopo* do plano em curso | feature | — | Claude | model | 2026-08-22 | Guideline (Fase 3) |
| B-03 | **Migrar as seis skills normativas restantes do AmFlow.** `hub-env`, `security-testing`, `data-architecture`, `data-privacy-lgpd`, `digital-twin-product` e `user-modeling` são norma com escopo, vestidas de skill. A unidade `06` migra **uma** — a `hub-front` — de propósito: migrar sete de uma vez é o over-engineering que o plano combate, e migrar uma **mede o custo real** da migração. Este item é o que sobra depois dessa medição | feature | — | Claude | model | 2026-08-22 | Guideline (Fase 3) |

## Solução planejada

| # | Item | Tipo | Prioridade | Autor | Core | Data de inclusão | Onde vive | Plano |
|---|---|---|---|---|---|---|---|---|

_Nenhum item ainda._

## Problemas resolvidos

| # | Item | Tipo | Prioridade | Autor | Core | Data de inclusão | Onde vive | Plano | Data de conclusão |
|---|---|---|---|---|---|---|---|---|---|

_Nenhum item ainda._
