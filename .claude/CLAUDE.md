---
# about
name: DecodeAndCode
type: instruction
project: DecodeAndCode
description: Plugin Claude Code que carrega o método decode-and-code — norma em camadas, porte de plano e o ciclo plano → unidade → cold-start
tags: [decode-and-code, plugin, claude-code, norma, dev-units]

# identity
project_type: "AI Builder"
segment: ""
category: ""

# history
author: Bortoli
created: 2026-08-22
status: draft
version: 1.0.0
updated: 2026-08-28

# system
scope: project
auto_load: true
dependencies: []
---

# DecodeAndCode — Instruções do Projeto

## Identidade

| Campo | Valor |
|---|---|
| Tipo de projeto | AI Builder |
| Segmento de mercado | — |
| Categoria de mercado | — |

## Visão Geral

Plugin Claude Code que empacota o método **decode-and-code**: a norma em camadas (princípio,
guideline, guardrail), o porte de plano, e o ciclo `plano → unidade → cold-start` que o antecede.

Origem: a skill `dev-units` do AmFlow, medida funcionando — 15 de 15 unidades executadas por Sonnet
em sessões novas, sem uma pergunta sobre conteúdo de unidade. Os **scripts e testes migraram**; a
camada normativa nasce aqui, sem as premissas do AmFlow.

## Arquitetura

- `.claude/skills/` — `decode-and-code/`, pasta compartilhada sem `SKILL.md` (`scripts/`, todo
  determinismo, e `config.json`), e as sete skills: os modos `review-plan`, `derive` e
  `implement`; `intake`, antes do ciclo; `huddle`, sobre o que ficou em aberto; `setup`, primeiro
  uso; `rethink`, revisão da norma após mudança de rumo. Sem agent
- `.claude/rules/` — guideline entra com `paths:`; sem `paths:`, carrega sempre
- `.claude/hooks/` — os quatro hooks do `settings.json`; `pre_tool_use.py` aplica
  `.claude/guardrails.json`. Uso registrado em `.claude/log/` (gitignorado)
- `docs/plan/` — planos e unidades; `docs/plan/system/` — norma, política de linguagem, `huddle/`
- `docs/recursos/` — uma descrição por recurso do plugin
- Fontes do plugin: `_fontes()` em `empacotar.py`, manifesto em `.claude/plugin.json`. A raiz
  carrega só o marketplace (`.claude-plugin/marketplace.json`, `source: archive`: zip em GitHub
  Release — `D-10` e `D-11` do plano `0004`)
- `dist/decode-and-code/` — staging gitignorado, reescrito a cada build
- Testes: `scripts/test-python.sh` roda a suíte inteira, inclusive o lint das skills; o CI
  (`.github/workflows/ci.yml`) roda em Python 3.10 fixo

## Recursos Instalados

Descrição, modelo e modo de invocação: frontmatter de cada `SKILL.md`. Hooks que viajam no
pacote: `_EVENTOS_DO_PACOTE` em `empacotar.py`.

## Restrições

**Invariantes**
- Uma fonte por fato — norma citada em dois lugares é drift esperando acontecer
- Nada específico de projeto viaja no plugin — guardrail e guideline são do projeto que instala, o
  plugin carrega o mecanismo, nunca a instância
- `state` e `verified_at` nunca se editam à mão — são projetados por script a partir do teste
- Nunca editar o miolo entre marcadores (`<!-- backlog:start -->`, `<!-- planos:start -->`) — é
  projeção, e será sobrescrita
- Idioma e nomenclatura seguem [`voice-and-language.md`](rules/voice-and-language.md) — pt-BR na
  documentação e no chat, identificadores em inglês

**Git**
- `dev` é o branch default e recebe todo o trabalho normal — plano, doc e código entram por PR para `dev`
- `main` é produção: só recebe promoção de `dev` no release (merge + tag), nunca commit direto
- PRs exigem revisão manual — convenção, não regra no GitHub
- Force push proibido em `main`; em `dev` é permitido

**Autonomia**
- Decisões arquiteturais exigem aprovação prévia
- Ações que afetam mais de 5 arquivos exigem apresentação de plano antes de executar

## Trabalho novo passa pelo modelo

| # | Etapa | Quem |
|---|---|---|
| 1 | Plano nasce em `docs/plan/_inbox/` | Opus |
| 2 | Revisão | Opus |
| 3 | **Aprovação** | **humano** |
| 4 | Derivação | Opus |
| 5 | Implementação, uma unidade por vez em cold-start | Sonnet |

Quem executa uma unidade **entrega arquivos e relatório, não commita**. Se a execução revelar que a
unidade estava insuficiente, a correção é **da unidade**, registrada como lacuna `L-XX` no plano.

## Linguagem

Os scripts seguem a [norma de linguagem](../docs/plan/system/language-policy.md).
