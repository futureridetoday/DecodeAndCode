---
# ── claude code — campos nativos ──────────────────────────────────────────────
name: derive
description: |
  Conduz o derive (P5) de um plano médio ou grande já aprovado: escreve cada unidade pronta para o code, projeta o backlog, grava o handoff e leva as unidades à aprovação.

  Use when o usuário pede, de forma explícita, para derivar um plano aprovado.

  <example>
  Context: plano técnico aprovado no P4, porte grande
  user: "derive o plano docs/plan/0031-add-catalog"
  commentary: modo derive — uma unidade por linha de ## Unidades, cada uma com a Definition of Ready, o handoff e a aprovação das unidades
  </example>

disable-model-invocation: true
user-invocable: true

allowed-tools: "Read Write Edit Glob Grep Bash(python3 \"${CLAUDE_SKILL_DIR}/dc.py\" *) Bash(python3 ${CLAUDE_SKILL_DIR}/dc.py *)"

argument-hint: "<plano>"
arguments: [target]

model: opus
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
tags: [decode-and-code, skill, plano, unidade, derive]
dependencies: []

hub_id: ""
source: local
---

# derive

> Invocação só explícita (`disable-model-invocation: true`): o `derive` cria arquivos no plano.

Esta skill executa o modo `derive`. `plan_root` vem do `config.json` ao lado de
`${CLAUDE_SKILL_DIR}/../decode-and-code/scripts/`, nunca fixo. O que vale está no codex; leia pelo
título com `python3 "${CLAUDE_SKILL_DIR}/dc.py" codex "<Título>"`, nunca de memória. Comece por
`Derive`, `Definition of Ready`, `Unidade`, `Cold-start`, `Handoff`, `Critério de aceite` e `Tipo`.

## Argumentos

- `$target` — o diretório do plano aprovado, ou o arquivo dele

## Instruções

### `derive <plano>`

1. **Entrada.** O plano tem número (`plan_id`), `format_version: 2` e porte médio ou grande. Sem
   número, mande à revisão (`/decode-and-code:review-plan`); sem `format_version`, também: a revisão
   o atualiza. O pequeno não tem derive.
2. **Uma unidade por linha de `## Unidades`.** `python3 "${CLAUDE_SKILL_DIR}/dc.py" proxima-unidade <dir_plano>`
   dá o `nn`; o arquivo é `<dir_plano>/<nn>-<slug>.md`, com o frontmatter `unit_id: <NNNN>-<nn>`,
   `unit_type` (`dev`, `plan` ou `rule`), `state: spec`, `test: <caminho do teste>` (vazio no
   `rule`), `verified_at: ""`, `approved_by: ""` e `approved_at: ""`, e o corpo com um `##` para cada bloco: `História`,
   `Critério de aceite`, `Tarefas` (lista), `Arquivos` (tabela com os caminhos entre crases),
   `Guidelines`, `Recursos`, `Decisões e lacunas` e `Depende de` — nomes, contratos e arquivos que
   ela espera das anteriores, ou `nada`. O `test:` aponta o arquivo do teste mesmo antes de ele
   existir. O que o tipo do plano pede no aceite está em `Tipo`.
3. **Guidelines.** Com a tabela `Arquivos` escrita, rode
   `python3 "${CLAUDE_SKILL_DIR}/dc.py" guidelines-aplicaveis <unidade>` e ponha cada linha que ele
   devolver na tabela `| Guideline | Onde |` de `## Guidelines`, mais o padrão de código da
   foundation pelo nome, se houver; sem nenhuma, escreva `nenhuma`. O que sair em `Avisos:` vai
   para o relatório.
4. **Recursos.** Confira que cada recurso de `## Recursos` do plano ainda existe no projeto; um que
   sumiu é lacuna do plano.
5. **Lint.** `python3 "${CLAUDE_SKILL_DIR}/dc.py" lint-unidade <unidade>...` em cada unidade; corrija
   ali o que ele apontar.
6. **Backlog.** `python3 "${CLAUDE_SKILL_DIR}/dc.py" projetar-backlog <dir_plano>`.
7. **Handoff.** `python3 "${CLAUDE_SKILL_DIR}/dc.py" handoff <dir_plano>` grava `_handoff.md`,
   lendo do stdin as seções `## Fila`, `## Pendências` e `## Sugestão` (seção ausente é erro), por
   heredoc com o delimitador entre aspas, `<<'FIM'`. As três são julgamento seu: a ordem com as
   dependências, o que espera do usuário e por onde começar.
8. **Aprovação das unidades.** Mostre as unidades ao usuário. No sim, acrescente ao plano
   `## Aprovação das unidades` com quem aprovou e a data, e diga que o handoff vai para uma sessão
   nova. Na recusa, ajuste as unidades com a objeção.
9. **Fecho do huddle** — `python3 "${CLAUDE_SKILL_DIR}/dc.py" huddle-fecho` imprime a seção *Huddle* do codex. O que ficou aberto entra por `python3 "${CLAUDE_SKILL_DIR}/dc.py" huddle-abrir <tipo> --autor Claude`, com o texto no stdin, uma chamada por entrada. Antes de enviar, a mensagem final passa por `python3 "${CLAUDE_SKILL_DIR}/dc.py" huddle-lint-relatorio`, no stdin, e termina com `entradas novas no huddle: N (H-XX, …)` — `0`, sem parênteses, quando não houve nada.

> **O handoff e o backlog são projeção.** Cada `derive` os regera, e edição à mão se perde. O
> prefixo `_` mantém o handoff fora do padrão `NN-*.md` que conta unidades.

Composição via `dc.py` — ponto de entrada único, o que o `allowed-tools` libera; rode-o do diretório do projeto. **Rode o comando exatamente como está escrito** — sem variável de shell, sem tirar as aspas e sem trocar o caminho —, porque a liberação de permissão casa o texto do comando. Subcomandos: `codex`, `proxima-unidade`, `guidelines-aplicaveis`, `lint-unidade`, `projetar-backlog`, `handoff`, `huddle-fecho`, `huddle-abrir` e `huddle-lint-relatorio`.

## Fora do escopo

A proposta, o plano técnico, o code e as aprovações, que são do usuário.
