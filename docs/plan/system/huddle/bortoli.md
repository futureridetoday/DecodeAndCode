---
# about
name: huddle
type: doc
project: claude-md-review-e0a97a
description: Fila do que ainda não foi decidido — pauta da conversa recorrente entre o humano e o modelo. Nada aqui é norma; entrada resolvida sai daqui e vai para o lugar de coisa resolvida
tags: [huddle, decode-and-code, pre-norma, pauta]

# history
author: ""
created: 2026-11-23
status: draft
version: 0.1.0
updated: ""

# huddle
owner: bortoli
last_huddle: ""
reminder_days: 7

# system
scope: project
auto_load: false
dependencies: []
---

# Huddle

**Nada aqui é autoritativo.** Entrada aberta é coisa que espera decisão, não regra a seguir. Quando
resolve, **sai** — para a norma, para uma guideline, ou para o `## Decisões` de um plano — e deixa
uma linha em `## Fechadas` com a data e o destino.

Formato, tipos, gatilhos e a regra de despejo: `<plan_root>/system/modelo-dev-units.md`, seção
*Huddle*. Aqui não se duplica a norma; aqui se usa.

## Abertas

### H-01 · `divergência` · 2026-11-23 · Claude

Num worktree, os scripts chamados pelas skills do checkout principal leem o estado do checkout principal, não o do worktree. O review-plan do persona-ablation-spike rodou o dc.py de /Users/.../DecodeAndCode/.claude/skills/review-plan/ e o concorrencia respondeu "sem conflito"; o mesmo comando com o dc.py do worktree achou o 0021 em desenvolvimento no core model. Causa: lib.repo_root() tenta __file__ antes do cwd, e o __file__ é o do checkout principal, cujo _planos.md não tem o 0021. A revisão contornou rodando os scripts do worktree; o defeito não foi corrigido.

Evidência: revisão: persona-ablation-spike

## Fechadas

| # | Tipo | Fechada em | Destino |
|---|---|---|---|
| H-02 | `divergência` | 2026-11-24 | spikes renumerados para 0022 e 0023 antes do merge |
