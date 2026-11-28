---
# ── claude code — campos nativos ──────────────────────────────────────────────
name: review-plan
description: |
  Conduz a revisão (P3 e P4): transforma a proposta aprovada em plano técnico, com histórias, porte, independência e tarefas ou unidades, e o leva à aprovação, que dá o número ao plano.

  Use when há uma proposta aprovada no _inbox, ou o usuário pede para revisar um plano.

  <example>
  Context: proposta aprovada no _inbox
  user: "revise o plano docs/plan/_inbox/add-catalog.md"
  commentary: modo review — escreve o plano técnico, roda os comandos de formato e leva à aprovação P4
  </example>

disable-model-invocation: false
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
tags: [decode-and-code, skill, plano, review]
dependencies: []

hub_id: ""
source: local
---

# review-plan

Esta skill executa o modo `review`: a revisão do workflow de produto. `plan_root` é o que `python3 "${CLAUDE_SKILL_DIR}/dc.py" raiz` imprime; os scripts ficam em `${CLAUDE_SKILL_DIR}/../decode-and-code/scripts/`, e nada dali se lê, só se roda pelo `dc.py`. O que vale
está no codex; leia pelo título com `python3 "${CLAUDE_SKILL_DIR}/dc.py" codex "<Título>"`, nunca de
memória. Comece por `Revisão`, `Plano técnico`, `História`, `Critério de aceite`, `Tarefa`, `Unidade`,
`Porte`, `Independência entre planos`, `Tipo` e `Aprovação`.

## Argumentos

- `$target` — caminho do plano no `_inbox`

## Instruções

### `review <plano>`

1. **Entrada.** O plano precisa de `## Aprovação da proposta` (P2); sem ela, pare e mande ao
   `decode`. Plano sem `format_version` é anterior ao redesign: revisá-lo é atualizá-lo para o
   formato 2 (`Plano anterior ao redesign`), e isso se diz ao usuário antes.
2. **Plano técnico (P3).** No mesmo arquivo, abaixo da proposta, escreva:
   - `## Histórias` — cada história e o seu critério;
   - `## Independência` — a resposta ao teste da seção `Independência entre planos`;
   - `## Decisões e riscos` — as decisões técnicas e os riscos; nenhuma em aberto;
   - pelo porte: `## Tarefas`, como checklist `- [ ]`, no pequeno; `## Unidades`, tabela
     `| # | Unidade | Entrega | Histórias |`, uma linha numerada por unidade, nos portes com unidade.
   No grande, siga `Plano técnico` e `Revisão` quanto à fase das histórias, ao teste do plano
   inteiro e ao acréscimo à proposta.
   Preencha `plan_size`. No pequeno, sem unidade para levar o teste, a revisão o declara no plano: acrescente
   ao frontmatter `test: <caminho do teste>` (vazio no tipo `rule`), `state: spec` e
   `verified_at: ""`. O que o tipo pede que a revisão confira está em `Tipo`.
3. **Fontes e recursos.** Abra as fontes técnicas citadas na proposta; confira que existem e servem. Cada
   recurso de `## Recursos` precisa existir no projeto: confira pelo nome.
4. **Concorrência.** Leia `_planos.md`: um plano em desenvolvimento que muda o mesmo comportamento
   concorre com este. Avise; se o usuário segue, o porquê vai para `## Independência`.
5. **Comandos:**
   - `python3 "${CLAUDE_SKILL_DIR}/dc.py" validar-nome <nome>`, com o stem do arquivo;
   - `python3 "${CLAUDE_SKILL_DIR}/dc.py" lint-plano <plano>` — cada problema se corrige antes do P4.
6. **Aprovação (P4).** Mostre ao usuário o plano técnico e, quando porte e apetite não batem, a
   diferença. Peça a resposta como `/decode-and-code:review-plan <resposta>`: a liberação do
   `allowed-tools` só vale no turno em que a skill carrega, e o sim roda comandos do `dc.py`. No sim, preencha `approved_by` (o nome dele) e `approved_at` (a data) e
   rode `python3 "${CLAUDE_SKILL_DIR}/dc.py" aprovar <plano>`: o plano recebe o número e vai para a
   raiz dos planos. Recomende o próximo passo: `/decode-and-code:derive <caminho>` no médio e no
   grande; o code no pequeno. Na recusa, volte ao passo 2 com a objeção, ou encerre.
7. **Lacunas** — cada uma nova entra como `L-XX`, sem tentar resolvê-la.
8. **Fecho do huddle** — `python3 "${CLAUDE_SKILL_DIR}/dc.py" huddle-fecho` imprime a seção *Huddle* do codex. O que ficou aberto entra por `python3 "${CLAUDE_SKILL_DIR}/dc.py" huddle-abrir <tipo> --autor Claude`, com o texto no stdin, uma chamada por entrada. Antes de enviar, a mensagem final passa por `python3 "${CLAUDE_SKILL_DIR}/dc.py" huddle-lint-relatorio`, no stdin, e termina com `entradas novas no huddle: N (H-XX, …)` — `0`, sem parênteses, quando não houve nada.

Composição via `dc.py` — ponto de entrada único, o que o `allowed-tools` libera; rode-o do diretório do projeto. **Rode o comando exatamente como está escrito** — sem variável de shell, sem tirar as aspas e sem trocar o caminho —, porque a liberação de permissão casa o texto do comando. Subcomandos: `codex`, `validar-nome`, `lint-plano`, `aprovar`, `huddle-fecho`, `huddle-abrir` e `huddle-lint-relatorio`.

## Fora do escopo

A proposta (`decode`), o derive, o code e as aprovações, que são do usuário.
