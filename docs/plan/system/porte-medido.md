---
# about
name: porte-medido
type: doc
project: DecodeAndCode
description: Tabela append-only do porte declarado contra o porte real de cada plano fechado — recalibra o vocabulário de pequeno/médio/grande com dado, não com impressão
tags: [decode-and-code, porte, medicao, instrumentacao]

# history
author: Bortoli
created: 2026-08-25
status: draft
version: 1.0.0
updated: ""

# system
scope: project
auto_load: false
dependencies: []
---

# Porte medido

> **Esta tabela é append-only.** `porte.registrar` acrescenta uma linha no instante em que um
> plano fecha — nunca reescreve, nunca recalcula uma linha existente. Não há marcadores de região
> aqui de propósito: toda outra escrita de script neste repositório é projeção, recalculada a
> partir da fonte a cada execução; esta tabela é o contrário — o fato que ela registra só existe
> naquele instante, e recalculá-lo depois daria outro número sobre o mesmo plano.

| Plano | Porte declarado | Unidades ou tarefas | Arquivos declarados | Linhas alteradas | Fechado em |
|---|---|---|---|---|---|
| [0001-decode-and-code-foundation](../model/0001-decode-and-code-foundation/0001-decode-and-code-foundation.md) | grande | 21 | 69 | 8740 | 2026-08-27 |
| [0002-record-plan-closure](../model/0002-record-plan-closure.md) | pequeno | — | não declarado | — | 2026-08-27 |
| [0003-derive-handoff-prompt](../model/0003-derive-handoff-prompt.md) | médio | 6 | não declarado | — | 2026-08-27 |
| [0004-installable-method](../model/0004-installable-method/0004-installable-method.md) | grande | 6 | 21 | 1426 | 2026-09-01 |
