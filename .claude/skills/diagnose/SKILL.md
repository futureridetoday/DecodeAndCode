---
# ── claude code — campos nativos ──────────────────────────────────────────────
name: diagnose
description: |
  Conduz o workflow de correção de um plano do tipo fix: diagnóstico (C1), plano mínimo no _inbox e a aprovação dele (C2), que dá o número; o code faz o resto.

  Use when a entrada declarou o tipo fix, ou o usuário relata um defeito.

  <example>
  Context: o decode confirmou tipo fix e o objetivo
  user: "o lint-plano aceita médio com duas unidades"
  commentary: modo diagnose — reproduz o defeito, escreve o plano mínimo e o leva à aprovação C2
  </example>

disable-model-invocation: false
user-invocable: true

allowed-tools: "Read Write Edit Glob Grep Bash(python3 \"${CLAUDE_SKILL_DIR}/dc.py\" *) Bash(python3 ${CLAUDE_SKILL_DIR}/dc.py *)"

argument-hint: "<defeito>"

model: opus
shell: bash

# ── amflow — rastreabilidade ───────────────────────────────────────────────────
type: skill
project: DecodeAndCode
author: Bortoli
created: 2026-11-27
status: draft
version: 1.0.0
updated: "2026-11-27"
scope: project
auto_load: false
tags: [decode-and-code, skill, correcao, diagnose]
dependencies: []

hub_id: ""
source: local
---

# diagnose

Defeito: $ARGUMENTS

Esta skill executa o modo `diagnose`, do módulo de correção. `plan_root` vem do `config.json` ao
lado de `${CLAUDE_SKILL_DIR}/../decode-and-code/scripts/`, nunca fixo. O que vale está no codex;
leia pelo título com `python3 "${CLAUDE_SKILL_DIR}/dc.py" codex "<Título>"`, nunca de memória:
`Correção`, `Plano mínimo`, `Passagem para o workflow de produto` e, por último,
`Teste que reproduz o defeito`.

## Instruções

1. **Entrada.** O tipo `fix` e o objetivo vêm confirmados da entrada (`/decode-and-code:decode`);
   sem eles, faça a entrada primeiro. `python3 "${CLAUDE_SKILL_DIR}/dc.py" bootstrap` (idempotente).
2. **Diagnóstico (C1).** Localize e reproduza o defeito, lendo do projeto o mínimo. Se não há
   defeito, ou o ajuste não é pequeno, siga a `Passagem para o workflow de produto`: proponha a troca
   de tipo e, no sim, mande ao `decode`.
3. **Plano mínimo.** Escreva `<plan_root>/_inbox/<nome>.md` (nome conferido com
   `python3 "${CLAUDE_SKILL_DIR}/dc.py" validar-nome <nome>`), com o frontmatter `plan_id: ""`,
   `status: draft`, `plan_type: fix`, `format_version: 2`, `plan_size: pequeno`,
   `approved_by: ""`, `approved_at: ""`, e as seções `## Objetivo`, `## Defeito` (como reproduzir),
   `## Correção` (o que muda), `## Como verificar` (o critério e o teste), `## Recursos` e
   `## Tarefas` com uma tarefa: escrever o teste, rodá-lo vermelho e guardar a saída para o
   relatório, corrigir, rodá-lo verde. Rode `python3 "${CLAUDE_SKILL_DIR}/dc.py" lint-plano <plano>`.
4. **Aprovação (C2).** Mostre o plano mínimo. No sim, preencha `approved_by` e `approved_at` e rode
   `python3 "${CLAUDE_SKILL_DIR}/dc.py" aprovar <plano>`: o plano recebe o número. Recomende
   `/decode-and-code:code <caminho>` (C3 e C4) e, depois do teste, `/decode-and-code:code aprovar
   <caminho>`, a aprovação final. Na recusa, refaça com a objeção ou encerre.
5. **Fecho do huddle** — `python3 "${CLAUDE_SKILL_DIR}/dc.py" huddle-fecho`; o que ficou aberto vai por `python3 "${CLAUDE_SKILL_DIR}/dc.py" huddle-abrir <tipo> --autor Claude`, texto no stdin; a mensagem final passa por `python3 "${CLAUDE_SKILL_DIR}/dc.py" huddle-lint-relatorio` e termina com `entradas novas no huddle: N (H-XX, …)`.

Rode o `dc.py` do diretório do projeto, **exatamente como está escrito** — sem variável de shell,
sem tirar as aspas e sem trocar o caminho —, porque a liberação de permissão casa o texto do
comando. Subcomandos: `codex`, `bootstrap`, `validar-nome`, `lint-plano`, `aprovar`, `huddle-fecho`,
`huddle-abrir` e `huddle-lint-relatorio`.

## Fora do escopo

O code (C3 e C4), que é do `code`, e as aprovações, que são do usuário.
