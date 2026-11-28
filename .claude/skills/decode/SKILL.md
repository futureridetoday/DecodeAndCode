---
# ── claude code — campos nativos ──────────────────────────────────────────────
name: decode
description: |
  Conduz a entrada e o decode (P1 e P2): identifica o tipo e o objetivo do pedido, escreve a proposta para o usuário no _inbox e a leva à aprovação.

  Use when o usuário traz um pedido, um problema, uma feature ou um insight, ainda sem plano.

  <example>
  Context: quer lint automático depois de editar um .py
  user: "quero que o test-python.sh rode a cada edição de .py"
  commentary: entrada, tipo e objetivo confirmados; a proposta mira o mínimo viável, um hook
  </example>

disable-model-invocation: false
user-invocable: true

allowed-tools: "Read Write Edit Glob Grep WebFetch(domain:code.claude.com) Bash(python3 \"${CLAUDE_SKILL_DIR}/dc.py\" *) Bash(python3 ${CLAUDE_SKILL_DIR}/dc.py *)"

argument-hint: "<pedido>"

model: opus
background: false
shell: bash

# ── amflow — rastreabilidade ───────────────────────────────────────────────────
type: skill
project: DecodeAndCode
author: Bortoli
created: 2026-10-15
status: draft
version: 2.0.0
updated: "2026-11-27"
scope: project
auto_load: false
tags: [decode-and-code, skill, plano, decode]
dependencies: []

hub_id: ""
source: local
---

# decode

Pedido: $ARGUMENTS

`plan_root` é o que `python3 "${CLAUDE_SKILL_DIR}/dc.py" raiz` imprime; os scripts ficam em `${CLAUDE_SKILL_DIR}/../decode-and-code/scripts/`, e nada dali se lê, só se roda pelo `dc.py`.

O que vale em cada passo está no codex; leia as seções pelo título com
`python3 "${CLAUDE_SKILL_DIR}/dc.py" codex "<Título>"`, nunca de memória. Comece por
`Workflow`, `Tipo`, `Objetivo do plano`, `Decode`, `Proposta` e `Fluxo de decodificação`.

## Instruções

1. **Chão:** `python3 "${CLAUDE_SKILL_DIR}/dc.py" bootstrap` (idempotente).
2. **Entrada.** Junte os blocos num pedido único. Declare o tipo com o motivo e proponha o objetivo
   numa frase; pergunte o que faltar, numa rodada só, e espere a confirmação dos dois. Um insight
   sem plano termina aqui, registrado no huddle se o usuário quiser. Se o tipo tem workflow próprio
   (`python3 "${CLAUDE_SKILL_DIR}/dc.py" modulos` lista os tipos e a skill de cada um), siga por ela.
3. **Contexto do projeto.** Leia a foundation (`<plan_root>/system/foundation.md`, se existir), as
   rules em `.claude/rules/`, `.claude/guardrails.json` e o mapa de recursos. Recurso entra pelo
   nome, nunca copiado.
4. **Proposta (P1).** Se o pedido retoma um rascunho sem `format_version` no `_inbox`, leia antes
   `Plano anterior ao redesign`. Rode o fluxo de decodificação nos três papéis e escreva
   `<plan_root>/_inbox/<nome>.md`: nome pela regra de `Numeração e nomenclatura`, conferido com
   `python3 "${CLAUDE_SKILL_DIR}/dc.py" validar-nome <nome>`. Frontmatter: `plan_id: ""`,
   `status: draft`, `plan_type`, `format_version: 2`, `plan_size: ""`, `approved_by: ""`,
   `approved_at: ""` e, se o pedido for de uma parte do sistema, `core`. Corpo: `## Objetivo`,
   `## Proposta`, com as partes que a seção `Proposta` do codex lista, e `## Recursos`, a tabela `| Recurso | Tipo | Onde entra |` ou a frase de
   que não há nenhum.
5. **Gate B para recurso do Claude Code.** Quando o pedido é criar ou automatizar algo no Claude
   Code, o mínimo viável é o primeiro degrau que resolve: nada (o que existe falha por outro
   motivo) → instrução → hook (o comportamento precisa ser garantido) → skill ou command → agent
   (só com contexto isolado). Schema em dúvida se confere em code.claude.com.
6. **Gates.** Escreva em `## Gates` a resposta ao A e ao B, com o que o B cortou. Se um falha,
   refaça a proposta ou proponha encerrar o plano.
7. **Aprovação (P2).** Mostre a proposta e pergunte. Peça a resposta como `/decode-and-code:decode <resposta>`: a liberação do
   `allowed-tools` só vale no turno em que a skill carrega, e o sim roda comandos do `dc.py`. No sim, acrescente `## Aprovação da proposta`
   com quem aprovou e a data, e recomende a revisão: `/decode-and-code:review-plan <caminho>`. Na
   recusa, refaça com a objeção ou encerre.
8. **Fecho:** `python3 "${CLAUDE_SKILL_DIR}/dc.py" huddle-fecho`; o que ficou aberto vai por
   `python3 "${CLAUDE_SKILL_DIR}/dc.py" huddle-abrir <tipo> --autor Claude`, texto no stdin; a
   mensagem final passa por `python3 "${CLAUDE_SKILL_DIR}/dc.py" huddle-lint-relatorio` antes de
   enviar.

Rode o `dc.py` do diretório do projeto, **exatamente como está escrito** — sem variável de shell,
sem tirar as aspas e sem trocar o caminho —, porque a liberação de permissão casa o texto do
comando.

## Fora do escopo

O plano técnico (`review-plan`), o derive, o code e as aprovações, que são do usuário.

## Saída

No idioma do pedido: o tipo, o objetivo, o caminho da proposta, os gates e a pergunta de aprovação;
ou o que falta, ou o gate que reprovou. Termina com `entradas novas no huddle: N (H-XX, …)`.
