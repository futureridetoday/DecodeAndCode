---
# about
name: planner-agent
type: unit
project: DecodeAndCode
description: O agente de planejamento nasce com papel e processo, sem embutir a norma — e junto vem o lint que recusa frontmatter de agente inventado, que é o que impede a próxima definição de nascer torta
tags: [decode-and-code, agent, planejamento, opus, lint]

# alvo
core: model
module: decode-and-code
block: ""
owner: model
unit_id: 0001-19
unit_type: dev

# verificação
state: spec
test: .claude/skills/decode-and-code/scripts/tests/test_agentes.py
verified_at: ""

# history
author: Bortoli
created: 2026-08-26
status: draft
version: 1.0.0
updated: ""

# system
scope: project
auto_load: false
dependencies: []
---

# 0001-19 — planner-agent

**Responsabilidade:** entregar o agente que revisa e deriva — `model: opus`, escrita restrita ao
que o planejamento produz — e o `lint_agente` que verifica os invariantes de qualquer definição de
agente, para que a `20` não repita a validação à mão.

## Contrato

| Campo | Detalhe |
|---|---|
| **Entrada** | `lint_agente.lint(caminho)` — a definição de um agente |
| **Saída** | Lista de problemas, vazia quando a definição está sã — mesmo padrão de `lint_unidade` e `lint_guideline` |
| **Auth** | — |
| **Efeito** | O lint só lê. A unidade cria `.claude/agents/planner.md` |
| **Erro** | Arquivo inexistente levanta `FileNotFoundError`; frontmatter quebrado entra como problema, nunca como exceção |

**O que `lint_agente` verifica**, e por que cada um é invariante e não gosto:

| Invariante | Por quê |
|---|---|
| Só **campos nativos** no frontmatter — `name`, `description`, `tools`, `model`, `skills`, `color` | Medido em 2026-08-26 nos 34 agentes instalados nesta máquina: `name` e `description` em 34, `model` em 26, `tools` em 25, `color` em 22. Campo que a ferramenta ignora é o defeito da `H-06`, onde quatro skills declaradas em `dependencies:` nunca carregaram |
| `model:` presente e dentro do vocabulário | A troca por modo é o que a `18` desbloqueia; agente sem `model` herda o da sessão e desfaz a decisão |
| Cada nome em `skills:` **existe em disco** | É o que separa declarar de carregar. Medido: **nenhum** dos 34 agentes declara `skills:` — só um *template* do builder o menciona. Ninguém sabe se ele carrega, e o lint verifica o que dá para verificar: que a skill nomeada existe |
| `tools:` presente e não vazio | Ausente concede o conjunto inteiro por default, que é o oposto de escopo declarado |

> **`tools:` não tem granularidade de caminho, e a unidade não finge que tem.** Medido nos agentes
> reais: `tools:` é lista de **nomes de ferramenta** (`Glob, Grep, LS, Read, ...`), sem qualquer
> expressão de path. *"Escrita restrita a `docs/plan/**`"* é portanto **declaração no corpo**, não
> restrição imposta pelo frontmatter — e o `lint` verifica que a declaração existe, jamais que ela
> é obedecida. Impor de verdade é trabalho de guardrail no projeto (`D-07`), e fica registrado como
> lacuna em vez de prometido aqui.

**O agente carrega papel e processo, nunca a norma** — a forma Anthropic, medida: `code-reviewer`
do `feature-dev` tem **46 linhas**, tools read-only, `model: sonnet`. Agente que embute norma cria
segunda fonte para o mesmo fato, e o `skills:` é a ponte que evita isso.

## Sequência

1. Escrever `lint_agente.py` com `lint(caminho)`, lendo o frontmatter por `regioes` e devolvendo lista de problemas.
2. Cobrir os quatro invariantes: campos nativos, `model` no vocabulário, `skills` existentes em disco, `tools` não vazio.
3. Escrever `.claude/agents/planner.md` — `model: opus`, `skills: [decode-and-code]`, `tools` com leitura ampla mais escrita, e o corpo declarando papel, processo numerado e o escopo `docs/plan/**`.
4. Manter o corpo na ordem da forma medida: papel → processo numerado → formato de saída, sem copiar norma.
5. Escrever `tests/test_agentes.py` cobrindo o lint por fixture **e** o `planner.md` real.
6. Rodar o gate e relatar.

## Arquivos

| Caminho | O que muda |
|---|---|
| `.claude/skills/decode-and-code/scripts/lint_agente.py` | **novo** — `lint(caminho)` |
| `.claude/agents/planner.md` | **novo** — o agente de planejamento |
| `.claude/skills/decode-and-code/scripts/tests/test_agentes.py` | **novo** — o teste declarado |
| `docs/plan/system/modelo-dev-units.md` | a seção curta que diz o que é um agente aqui e o que o lint exige |

## Dependências

A `0001-18`, que tira da norma a frase que põe agent fora de escopo — sem ela, esta unidade
contradiz a norma que a skill executa.

## Normas aplicáveis

| Norma | Onde |
|---|---|
| O planejador cobre planejar, revisar e derivar; planejar do zero é `fork`, não subagente | [`0001-decode-and-code-foundation.md`](0001-decode-and-code-foundation.md), `D-05` |
| Guardrail fica no projeto, nunca no frontmatter do agente | [`0001-decode-and-code-foundation.md`](0001-decode-and-code-foundation.md), `D-07` |
| Agente carrega papel e processo; a norma continua na norma | [`0001-decode-and-code-foundation.md`](0001-decode-and-code-foundation.md), *Agente: papel e processo, nunca a norma* |
| Campo declarado que a ferramenta ignora é falha silenciosa | [`huddle.md`](../../system/huddle.md), `H-06` |

## Critério de aceite

`lint_agente.lint` devolve `[]` sobre uma definição sã e **um problema por invariante violado**,
cada violação num caso próprio: campo não-nativo declarado, `model` ausente, `model` fora do
vocabulário, `skills` nomeando skill que não existe em disco, e `tools` ausente. Cinco violações,
cinco casos — nenhum item enumerado sem caso atrás.

`lint_agente.lint(".claude/agents/planner.md")` devolve `[]` — **o caso contra o artefato real**,
não só contra fixture. Sem ele, o lint prova o mecanismo e nunca a instância, que é a `L-31`.

O `planner.md` declara `model: opus`, `skills: [decode-and-code]` — e o teste confere que essa skill
existe em disco —, e o corpo declara o escopo `docs/plan/**`. O teste procura a declaração de escopo
no corpo, e afirma explicitamente, em nome de caso, que isso é **declaração e não imposição**.

**A suíte inteira continua verde.**

## Verificação

```
./scripts/test-python.sh .claude/skills/decode-and-code/scripts/tests/test_agentes.py
```

## Fonte

- [`0001-decode-and-code-foundation.md`](0001-decode-and-code-foundation.md), *Escopo* → *Fase 6*
- `D-25` — por que o lint de agente nasce aqui e não na `20`
- Benchmark medido em 2026-08-26 nos 34 agentes de `~/.claude/plugins/marketplaces/`: `name` e
  `description` em 34, `model` em 26, `tools` em 25, `color` em 22, `effort` em 7, e **`skills:` em
  nenhum**
