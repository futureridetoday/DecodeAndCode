---
# ── claude code — campos nativos ──────────────────────────────────────────────
description: Delega a implementação de uma unidade ao agent developer, sem sair da sessão atual.
argument-hint: "<unidade>"
allowed-tools: "Agent"
model: sonnet

# ── amflow — rastreabilidade ───────────────────────────────────────────────────
name: delegate
type: command
project: DecodeAndCode
author: Bortoli
created: 2026-08-28
status: draft
version: 1.0.0
updated: "2026-08-28"
scope: project
auto_load: false
tags: [decode-and-code, unidade, cold-start, agente]
dependencies: [decode-and-code]

hub_id: ""
source: local
---

# /delegate

Delega a implementação da unidade `$1` ao agent `developer`, sem sair desta sessão.

Pensado para a **sessão de orquestração**: ela guarda o contexto do plano e não deve gastá-lo
executando a unidade — o agent roda em cold-start próprio, isolado desta conversa.

Vale só para unidades de plano **porte grande** — são as únicas que o modelo deriva.

## Execução

Invoque o Agent tool com `subagent_type: "developer"`, pedindo para implementar a unidade `$1`.

Quando o agent retornar: revise a entrega (norma, seção *Como revisar uma entrega* — medir, não
reler o relatório) antes de registrar ou versionar.
