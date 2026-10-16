---
# ── claude code — campos nativos ──────────────────────────────────────────────
name: implement
description: |
  Implementa uma unidade já derivada em cold-start, num subagent isolado — escreve o teste declarado e o código que o faz passar, tocando só os arquivos que a unidade lista.

  Use when o usuário pede para implementar ou executar uma unidade já derivada do modelo de dev-units.

  <example>
  Context: unidade já derivada, pronta para execução
  user: "implemente a unidade 0001-03"
  commentary: modo implement — executa em cold-start, com gate de entrada (critério de aceite e teste declarados) e gate de saída (teste precisa passar antes de marcar verified)
  </example>

disable-model-invocation: false
user-invocable: true

allowed-tools: "Read Write Edit Glob Grep Bash(python3 \"${CLAUDE_SKILL_DIR}/dc.py\" *) Bash(python3 ${CLAUDE_SKILL_DIR}/dc.py *)"

argument-hint: "<unidade>"
arguments: [target]

model: sonnet
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
tags: [decode-and-code, skill, unidade, cold-start, implement]
dependencies: []

hub_id: ""
source: local
---

# implement

Implemente a unidade `$target` do método decode-and-code, em cold-start. Você executa o modo `implement` da norma `<plan_root>/system/modelo-dev-units.md` — `plan_root` resolvido pelo `config.json` em `${CLAUDE_SKILL_DIR}/../decode-and-code/`. Todo determinismo (gates, contagem, projeção de estado) fica nos scripts em `${CLAUDE_SKILL_DIR}/../decode-and-code/scripts/` (norma, seção *Fronteira skill / script*); a skill cuida do que exige julgamento.

## Argumentos

- `$target` — identificador da unidade a implementar

## Instruções

### `implement <unidade>`

Os dois gates são os da norma (*Os dois gates*, decisão 15) — esta seção descreve só o **como**, para não duplicar o que já está lá.

1. **Gate de entrada** — `python3 "${CLAUDE_SKILL_DIR}/dc.py" lint-unidade <unidade>`; qualquer problema recusa e encerra sem escrever nada, e a correção volta ao `derive`.
2. **Ler a unidade inteira** — contrato, sequência, arquivos, normas referenciadas e critério de aceite.
3. **Abrir as normas citadas** na tabela — são referências, o conteúdo delas não está copiado na unidade.
4. **Escrever o teste declarado**, cobrindo o critério de aceite — teste e código são entregáveis da mesma unidade (decisão 15); exigir teste preexistente tornaria impossível começar unidade nova.
5. **Escrever o código** que faz o teste passar, tocando apenas os arquivos que a unidade declara.
6. **Gate de saída** — `python3 "${CLAUDE_SKILL_DIR}/dc.py" verificar <unidade>`; teste falhando, a unidade não transiciona para `verified`.
7. **Projetar o backlog** do plano com `python3 "${CLAUDE_SKILL_DIR}/dc.py" projetar-backlog <dir_plano>`.
8. **Relatar** o que foi feito — se algo da unidade estava insuficiente, dizer o quê; a correção é da unidade, nunca do executor.

> **Se o executor precisou perguntar, a unidade falhou.** O teste é empírico e barato, e a
> insuficiência volta para quem deriva — nunca é resolvida por conta própria em execução.

> **O executor não commita.** O modo entrega arquivos e relatório; versionar é de quem orquestra, que
> revisa a entrega antes de registrá-la.

Para rodar o teste durante o trabalho (passos 4 e 5), use `python3 "${CLAUDE_SKILL_DIR}/dc.py" verificar <unidade> --dry-run`, que roda sem gravar estado. Teste que falha vem com a saída dele (as últimas 80 linhas): é dela que sai o que corrigir.

Composição via `dc.py` — ponto de entrada único, o que o `allowed-tools` libera; rode-o do diretório do projeto. **Rode o comando exatamente como está escrito** — sem variável de shell, sem tirar as aspas e sem trocar o caminho —, porque a liberação de permissão casa o texto do comando. Subcomandos: `lint-unidade`, `verificar` e `projetar-backlog`.

> **O executor nunca deriva nem revisa planos.** Decidir a fatia de uma unidade não é trabalho de quem executa.

## Saída

Uma única mensagem: o que foi escrito, o resultado do gate de saída, e o que ficou insuficiente na unidade, se algo ficou.

## Referências

- Norma: `<plan_root>/system/modelo-dev-units.md` — `plan_root` é o do `config.json`, e
  `docs/plan` é só o default. Vive no projeto que usa a skill, e é lá que a skill a lê.
