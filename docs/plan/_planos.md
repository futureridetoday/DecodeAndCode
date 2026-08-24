---
# about
name: planos
type: doc
project: DecodeAndCode
description: Registro dos planos aprovados para desenvolvimento — fonte da numeração sequencial e da situação de cada plano
tags: [plan, registro, decode-and-code]

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

# Planos aprovados

Registro dos planos que entraram em desenvolvimento. Planos no `_inbox/` **não aparecem aqui** — só
entram na aprovação, momento em que recebem o número.

Este arquivo é a **fonte da numeração**: o script lê o maior número em uso e toma o próximo.

<!-- planos:start -->
| # | Plano | Core | Módulo | Origem | Situação | Aprovado |
|---|---|---|---|---|---|---|
| 0001 | [decode-and-code-foundation](model/0001-decode-and-code-foundation/0001-decode-and-code-foundation.md) | model | decode-and-code | — | concluído | 2026-08-23 |
<!-- planos:end -->

> A **situação** é projetada a partir do estado das unidades — `em desenvolvimento` enquanto houver
> unidade não verificada, `concluído` quando todas passarem. Nunca se edita à mão.

> O miolo entre `<!-- planos:start -->` e `<!-- planos:end -->` é **projeção de script**. Texto
> escrito ali se perde na próxima execução.
