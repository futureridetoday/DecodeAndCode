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
| [0005-plugin-release-distribution](../model/0005-plugin-release-distribution.md) | médio | 9 | não declarado | — | 2026-09-02 |
| [0006-e2e-fixes](../model/0006-e2e-fixes.md) | médio | 7 | não declarado | — | 2026-10-17 |
| [0007-add-norm-writers](../model/0007-add-norm-writers.md) | médio | 7 | não declarado | — | 2026-11-15 |
| [0008-wire-huddle-cycle](../model/0008-wire-huddle-cycle.md) | médio | 10 | não declarado | — | 2026-11-15 |
| [0009-onboard-new-project](../model/0009-onboard-new-project/0009-onboard-new-project.md) | grande | 7 | 32 | 2113 | 2026-11-17 |
| [0010-fix-norma-entry-gate](../model/0010-fix-norma-entry-gate.md) | pequeno | — | não declarado | — | 2026-11-17 |
| [0011-fix-norma-config-claims](../model/0011-fix-norma-config-claims.md) | pequeno | — | não declarado | — | 2026-11-19 |
| [0012-add-plan-type](../model/0012-add-plan-type.md) | médio | 8 | não declarado | — | 2026-11-19 |
| [0014-fix-review-plan-claims](../model/0014-fix-review-plan-claims.md) | pequeno | — | não declarado | — | 2026-11-19 |
| [0013-fix-setup-validation](../model/0013-fix-setup-validation.md) | médio | 14 | não declarado | — | 2026-11-19 |
| [0015-add-plan-size-advice](../model/0015-add-plan-size-advice.md) | pequeno | — | não declarado | — | 2026-11-20 |
