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

- `.claude/skills/decode-and-code/` — a skill e seus scripts, todo determinismo
- `.claude/rules/` — a camada normativa: guideline por arquivo entra com `paths:`;
  [`principles.md`](rules/principles.md) carrega sempre, sem `paths:` — código é custo,
  subtração antes de adição, evidência acima de opinião, fluxo de decodificação e protocolo de
  exceção
- `docs/plan/` — planos e unidades, destino de todo trabalho novo
- `docs/plan/system/` — fundação: norma, política de linguagem, `huddle.md`
- `.claude/plugin.json` — o manifesto **fonte** do plugin, ao lado das outras fontes que
  `empacotar.construir` copia (`D-10` do plano `0004`: a raiz do repositório carrega só o
  marketplace, nunca o plugin)
- `.claude-plugin/marketplace.json` — o catálogo do marketplace `future-ride-today` (owner
  `Future Ride Today`); a entrada do plugin referencia `source: archive` — zip anexado a um
  GitHub Release, não caminho no clone (`D-11` do plano `0004`)
- `dist/decode-and-code/` — staging **gitignorado**: `empacotar.construir` o escreve do zero a
  cada build. O que se distribui é o zip que `empacotar.empacotar_zip` produz dali, publicado
  como asset de Release

## Recursos Instalados

| Recurso | Tipo | Descrição |
|---|---|---|
| `decode-and-code` | skill | Executa a norma de Unidades de Desenvolvimento em três modos — revisa um plano, deriva estrutura e unidades, ou implementa uma unidade em cold-start. Delega todo determinismo aos scripts em `scripts/` |

## Restrições

**Invariantes**
- Uma fonte por fato — norma citada em dois lugares é drift esperando acontecer
- Nada específico de projeto viaja no plugin — guardrail e guideline são do projeto que instala, o
  plugin carrega o mecanismo, nunca a instância
- `state` e `verified_at` nunca se editam à mão — são projetados por script a partir do teste
- Nunca editar o miolo entre marcadores (`<!-- backlog:start -->`, `<!-- planos:start -->`) — é
  projeção, e será sobrescrita
- Português brasileiro na documentação; identificadores em inglês

**Git**
- `dev` é o branch default e recebe todo o trabalho normal — plano, doc e código entram por PR para `dev`
- `main` é produção: só recebe promoção de `dev` no release (merge + tag), nunca commit direto
- PRs exigem revisão manual — convenção, não regra no GitHub
- Force push proibido em `main`; em `dev` é permitido

**Autonomia**
- Decisões arquiteturais exigem aprovação prévia
- Ações que afetam mais de 5 arquivos exigem apresentação de plano antes de executar

## Relação com o AmFlow

Os dois repositórios têm papéis distintos, e confundi-los é o que produz drift:

| Repositório | Papel |
|---|---|
| `DecodeAndCode` | Onde o método é **desenvolvido**. Única cópia editável |
| `AmFlow` | Onde o método é **provado**. Primeiro consumidor real, e campo de prova das guidelines e guardrails — é lá que existem os incidentes registrados |

A skill `dev-units` do AmFlow está **congelada desde 2026-08-22**: somente uso, nenhuma escrita.
Correção descoberta durante o desenvolvimento entra aqui. Se o AmFlow precisar dela antes da
conclusão, entra lá como cherry-pick registrado como tal.

> **Por que o campo de prova fica no AmFlow.** Guardrail e guideline se escolhem por evidência de
> falha, não por elegância. Repo novo é greenfield e não tem incidente nenhum — as unidades entregam
> o **mecanismo** aqui e a **instância de prova** contra o AmFlow.

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
