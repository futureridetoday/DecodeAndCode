---
# ── claude code — campos nativos ──────────────────────────────────────────────
description: Executa o modo implement da skill decode-and-code para uma unidade, em sessão nova.
argument-hint: "<unidade>"
allowed-tools: "Read Write Edit Bash Glob Grep"
model: sonnet

# ── amflow — rastreabilidade ───────────────────────────────────────────────────
name: implement
type: command
project: DecodeAndCode
author: Bortoli
created: 2026-08-28
status: draft
version: 1.0.0
updated: "2026-08-28"
scope: project
auto_load: false
tags: [decode-and-code, unidade, cold-start, implement]
dependencies: [decode-and-code]

hub_id: ""
source: local
---

# /implement

Executa o modo `implement` da skill `decode-and-code` para a unidade `$1`, nesta sessão.

Pensado para uma **sessão nova**: ela já chega em cold-start por conta própria, sem contexto de
conversas anteriores — não precisa do agent `developer` para isolar contexto.

Vale só para unidades de plano **porte grande** — são as únicas que o modelo deriva.

## Execução

Invoque a skill `decode-and-code`, modo `implement`, com `$1` como alvo, e siga o processo que ela
define: gate de entrada, teste declarado, código, gate de saída, backlog.

Ao final: entregue arquivos e relatório. **Não commite** — quem orquestra revisa antes de
versionar.
