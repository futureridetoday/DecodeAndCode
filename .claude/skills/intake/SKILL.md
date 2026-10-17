---
# ── claude code — campos nativos ──────────────────────────────────────────────
name: intake
description: |
  Percorre a escada de menor intervenção antes de qualquer plano existir: resolve com um recurso isolado ou grava o esboço mínimo em _inbox para o review-plan.

  Use when o usuário quer criar ou automatizar algo no Claude Code, ou traz um problema, feature ou esboço de plano ainda sem escopo.

  <example>
  Context: quer lint automático depois de editar um .py
  user: "cria uma skill que roda o test-python.sh a cada edição de .py"
  commentary: o comportamento precisa ser garantido, então o degrau é hook, não skill
  </example>

disable-model-invocation: false
user-invocable: true

allowed-tools: "Read Write Edit Glob Grep WebFetch(domain:code.claude.com) Bash(python3 \"${CLAUDE_SKILL_DIR}/dc.py\" *) Bash(python3 ${CLAUDE_SKILL_DIR}/dc.py *)"

argument-hint: "<pedido>"

model: opus
context: fork
agent: general-purpose
background: false
shell: bash

# ── amflow — rastreabilidade ───────────────────────────────────────────────────
type: skill
project: DecodeAndCode
author: Bortoli
created: 2026-10-15
status: draft
version: 1.0.0
updated: "2026-10-15"
scope: project
auto_load: false
tags: [decode-and-code, skill, plano, intake]
dependencies: []

hub_id: ""
source: local
---

# intake

Resolva o pedido abaixo com a menor intervenção que funcione, antes de qualquer plano existir.

Pedido: $ARGUMENTS

`plan_root` vem do `config.json` em `${CLAUDE_SKILL_DIR}/../decode-and-code/`, nunca fixo; os scripts, de `${CLAUDE_SKILL_DIR}/../decode-and-code/scripts/`.

## Instruções

1. **Sempre:** `python3 "${CLAUDE_SKILL_DIR}/dc.py" bootstrap` (idempotente).
2. **Classifique o pedido:** recurso do Claude Code, ou plano, feature, problema. Se as duas leituras cabem, apresente ambas e pergunte.
3. **Recurso do Claude Code:** leia o que o projeto já tem em `.claude/` e suba a escada, parando no primeiro degrau que resolve: nada (já existe e falha por outro motivo) → instrução → hook (o comportamento precisa ser garantido) → skill ou command → agent (só com contexto isolado). Entregue o recurso ou a recomendação, com o degrau e o porquê, mesmo contra o tipo pedido. Schema em dúvida: confirme em code.claude.com, não por analogia.
4. **Plano, feature ou problema:** leia os arquivos relacionados e aplique Clarificar → Evitar → Reduzir e os gates A e B da norma `<plan_root>/system/modelo-dev-units.md` (*Antes do plano*). Comece pela objeção: ache o motivo para não construir. Se o gate A reprova (sem impacto mensurável agora), reporte e pare sem gravar.
5. **Falta informação** para responder os estágios: pare e liste o que falta, numa rodada só. Nunca grave esboço incompleto para resolver depois.
6. **Estágios e gates respondidos:** grave o esboço mínimo em `<plan_root>/_inbox/<nome>.md`, no formato da norma `<plan_root>/system/modelo-dev-units.md` (*O que cada porte carrega*). Nome semântico, sem número (vem na aprovação). Os gates A e B vão respondidos por escrito no esboço, com o que o B cortou. Depois:
   - `python3 "${CLAUDE_SKILL_DIR}/dc.py" validar-nome <nome>`
   - `python3 "${CLAUDE_SKILL_DIR}/dc.py" lint-plano <plano>`
7. Lint sem problemas: recomende `review-plan <caminho>` como próximo passo.

Composição via `dc.py`: rode-o do diretório do projeto. **Rode o comando exatamente como está escrito** — sem variável de shell, sem tirar as aspas e sem trocar o caminho —, porque a liberação de permissão casa o texto do comando.

## Fora do escopo

Derivar (`derive`), implementar (`implement`) e aprovar, que é do humano.

## Saída

Uma única mensagem, no idioma do pedido. Recurso: o degrau, o porquê e o que foi criado ou recomendado. Plano: o caminho do esboço, os gates A e B e `review-plan <caminho>`. Parada: o que falta, ou o gate que reprovou.
