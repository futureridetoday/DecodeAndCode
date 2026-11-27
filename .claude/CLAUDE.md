---
# about
name: DecodeAndCode
type: instruction
project: DecodeAndCode
description: Plugin Claude Code que carrega o método decode-and-code — o codex, o workflow decode → code e os princípios, guidelines e guardrails do projeto
tags: [decode-and-code, plugin, claude-code, codex]

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

## Visão Geral

Plugin Claude Code que empacota o método **decode-and-code**. O método é o codex
(`.claude/skills/decode-and-code/codex/`): o workflow do pedido à entrega — decode, revisão, derive e
code —, os artefatos, as regras e os princípios, guidelines e guardrails que cada projeto define.

Origem: a skill `dev-units` do AmFlow, medida funcionando — 15 de 15 unidades executadas por Sonnet
em sessões novas, sem uma pergunta sobre conteúdo de unidade. Os **scripts e testes migraram**; a
método nasce aqui, sem as premissas do AmFlow.

## Arquitetura

- `.claude/skills/` — `decode-and-code/`, pasta compartilhada sem `SKILL.md` (`codex/`, o método;
  `procedures/`, o passo a passo que várias skills usam; `modules/`, os módulos; `scripts/`, todo
  determinismo; e `config.json`), e as skills: `decode`, `review-plan`, `derive` e `code`, o
  workflow; `huddle`, sobre o que ficou em aberto; `setup`, primeiro uso; `rethink`, revisão depois
  de uma mudança de rumo; `diagnose`, do módulo de correção. Sem agent
- `.claude/rules/` — guideline entra com `paths:`; sem `paths:`, carrega sempre
- `.claude/hooks/` — os quatro hooks do `settings.json`; `pre_tool_use.py` aplica
  `.claude/guardrails.json`. Uso registrado em `.claude/log/` (gitignorado)
- `docs/plan/` — planos indexados em `_planos.md`: os anteriores ao redesign em `model/`, os novos na
  raiz; `docs/plan/system/` — política de linguagem, `huddle/`, registro do método
- `docs/codex/` — registro do redesign que criou o codex; `docs/maintenance/` — o que só serve a
  quem mantém o plugin: o guia do codex, empacotamento, release, módulos, skills e scripts
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
- Uma fonte por fato — regra citada em dois lugares é drift esperando acontecer; o lint de repetição
  confere o codex contra as skills
- Nada específico de projeto viaja no plugin — guardrail e guideline são do projeto que instala, o
  plugin carrega o mecanismo, nunca a instância
- `state` e `verified_at` nunca se editam à mão — são projetados por script a partir do teste
- Nunca editar o miolo entre marcadores (`<!-- backlog:start -->`, `<!-- planos:start -->`) — é
  projeção, e será sobrescrita

**Git**
- `dev` é o branch default e recebe todo o trabalho normal — plano, doc e código entram por PR para `dev`
- `main` é produção: só recebe promoção de `dev` no release, nunca commit direto — passos em
  `docs/maintenance/release.md`
- PRs exigem revisão manual — convenção, não regra no GitHub
- Force push proibido em `main`; em `dev` é permitido

**Autonomia**
- Decisões arquiteturais exigem aprovação prévia
- Ações que afetam mais de 5 arquivos exigem apresentação de plano antes de executar

## Trabalho novo passa pelo modelo

O workflow é o do codex (*Workflow*): `decode` escreve a proposta no `_inbox/` (P1), o humano a
aprova (P2), `review-plan` escreve o plano técnico (P3), o humano o aprova e o plano recebe número
(P4), `derive` prepara as unidades no médio e no grande (P5), e `code` executa cada uma em sessão
nova (P6), com o teste e a aprovação do humano em cada entrega (P7). Correção segue o módulo `fix`,
pela skill `diagnose`.

Quem executa uma unidade **entrega arquivos e relatório, não commita**. Se a execução revelar que a
unidade estava insuficiente, Claude para e propõe o ajuste, registrado como lacuna `L-XX` no plano.
