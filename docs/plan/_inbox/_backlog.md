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
| B-04 | **Isolar o `git` real de `scripts/move-md.py` nos testes.** Medido em 2026-08-25 com um shim de `git` no `PATH`: a suíte executava **16** `git ls-files --error-unmatch` de verdade, todas de [`move-md.py:196`](../../../scripts/move-md.py), que confere se a origem está versionada antes de usar `git mv`. Não quebrava nada e era pré-existente — o registro existiu porque foi essa suposição não conferida que tornou falsa a afirmação *"nenhum teste executa `git` de verdade"* da unidade `0001-15` (`L-28`). **Resolvido mockando `esta_versionado` nos quatro arquivos que movem plano** — `test_scaffold` (9), `test_derive_por_porte` (5), `test_config` (1) e `test_porte_e_aprovacao` (1). O mock devolve `False`, que é o que o git já respondia para arquivo em `tempfile`: nenhum comportamento muda, só a chamada some. **Remedido com o mesmo shim: 16 → 0**, e as 22 invocações que restam são as do `TestComandoContraGitReal`, deliberadas. **A primeira tentativa foi outra e falhou:** uma guarda em `esta_versionado` para não perguntar por caminho fora do `REPO_ROOT` não removeu nenhuma das 16 — os testes patcham `move_md.REPO_ROOT` para o próprio `tempfile`, então o caminho está *dentro* do repo do ponto de vista do script. Descartada | problema | — | Claude | model | 2026-08-25 | `scripts/move-md.py` | — (correção direta, fora de unidade) | 2026-08-25 |
