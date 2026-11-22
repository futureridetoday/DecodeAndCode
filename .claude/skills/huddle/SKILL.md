---
# ── claude code — campos nativos ──────────────────────────────────────────────
name: huddle
description: |
  Conduz o huddle da pessoa da sessão: percorre as entradas abertas uma a uma e decide, promove a guideline ou guardrail, descarta ou mantém cada uma. Com `registrar <texto>`, abre uma entrada nova.

  Use when a pessoa quer fazer o huddle, ou registrar algo que ainda não foi decidido.

  <example>
  Context: o aviso de abertura disse que o huddle está atrasado
  user: "/decode-and-code:huddle"
  commentary: roda a pauta e conduz as abertas uma por vez, gravando cada decisão pelo dc.py
  </example>

disable-model-invocation: true
user-invocable: true

allowed-tools: "Read Write Edit Glob Grep Bash(python3 \"${CLAUDE_SKILL_DIR}/dc.py\" *) Bash(python3 ${CLAUDE_SKILL_DIR}/dc.py *)"

argument-hint: "[registrar <texto>]"

model: opus
shell: bash

# ── amflow — rastreabilidade ───────────────────────────────────────────────────
type: skill
project: DecodeAndCode
author: Bortoli
created: 2026-11-15
status: draft
version: 1.2.0
updated: "2026-11-22"
scope: project
auto_load: false
tags: [decode-and-code, skill, huddle]
dependencies: []

hub_id: ""
source: local
---

# huddle

Esta skill conduz o modo `huddle` da pessoa que está na sessão — a fila do que ainda não foi
decidido, na norma `<plan_root>/system/modelo-dev-units.md`, seção *Huddle*. `plan_root` vem do
`config.json` em `${CLAUDE_SKILL_DIR}/../decode-and-code/`; os scripts, de
`${CLAUDE_SKILL_DIR}/../decode-and-code/scripts/`. Cada pessoa tem o próprio arquivo, e o `dc.py`
resolve qual é pelo `git config user.name`: aqui só se lê e se escreve o da pessoa da sessão.

Argumentos: $ARGUMENTS

## Sem argumento — conduzir o huddle

1. **Pauta** — `python3 "${CLAUDE_SKILL_DIR}/dc.py" huddle-pauta`. Mostre as abertas e um resumo
   dos commits desde o último huddle: é o que a conversa percorre. Se houver `## Log`, resuma-o
   também — comandos que reprovaram ou falharam, bloqueios de guardrail e os `E-XX` abertos. Um
   `E-XX` se resolve com `python3 "${CLAUDE_SKILL_DIR}/dc.py" log-resolver <E-XX> "<destino>"`, com
   destino `H-XX`, `L-XX`, `método` (defeito do próprio método: vira `M-XX`) ou
   `descartado: <motivo>`. Os `M-XX` pendentes aparecem no `## Log`: mostre-os com
   `python3 "${CLAUDE_SKILL_DIR}/dc.py" metodo-listar` e lembre a pessoa de levá-los ao repositório
   do método; quando ela disser onde os levou, rode
   `python3 "${CLAUDE_SKILL_DIR}/dc.py" metodo-levado <M-XX> "<onde>"`.
2. **Uma entrada por vez**, pela ferramenta de perguntas, com cinco saídas:
   - **Decidir** — o destino em texto livre (a norma, o `## Decisões` de um plano, uma resposta).
     Grave com `python3 "${CLAUDE_SKILL_DIR}/dc.py" huddle-fechar <H-XX> "<destino>"`.
   - **Promover** — a guideline ou o guardrail. Monte a proposta com a pessoa e mostre-a inteira;
     **só grave depois de ela aprovar na conversa**. Guideline: o JSON
     `{nome, descricao, paths, corpo}` (e `aguardando: true` se o caminho ainda não existe) para
     `python3 "${CLAUDE_SKILL_DIR}/dc.py" criar-guideline`. Guardrail: o JSON
     `{regra, proibido, permitido}` para `python3 "${CLAUDE_SKILL_DIR}/dc.py" adicionar-guardrail`.
     O JSON vai por arquivo, como diz *JSON pelo stdin* na norma
     (`python3 "${CLAUDE_SKILL_DIR}/dc.py" explicar conversa`, que traz também os padrões de `paths`
     e o formato do guardrail): `python3 "${CLAUDE_SKILL_DIR}/dc.py" criar-guideline < <arquivo>`.
     Código `1` traz o motivo da recusa: ajuste com a pessoa e tente de novo. Gravado, feche com
     `python3 "${CLAUDE_SKILL_DIR}/dc.py" huddle-fechar <H-XX> "<guideline ou guardrail>: <caminho>"`.
   - **Levar ao método** — quando a entrada é sobre o próprio método, não sobre o projeto. Redija
     com a pessoa um texto genérico, sem nome de plano, módulo ou trecho do projeto; mostre-o
     inteiro e **só grave depois de ela aprovar na conversa**, com o texto no stdin:
     `python3 "${CLAUDE_SKILL_DIR}/dc.py" huddle-fechar <H-XX> método < <arquivo>`, o arquivo
     escrito com `Write` fora do projeto. Código `1` não fecha a entrada: traga o motivo à pessoa.
   - **Descartar** — com o motivo escrito: `huddle-fechar <H-XX> "descartada: <motivo>"`.
   - **Manter** — continua aberta; nada a gravar.
3. **Concluir** — `python3 "${CLAUDE_SKILL_DIR}/dc.py" huddle-concluir`, que grava a data do huddle
   e apaga do log os eventos que a pauta mostrou.
4. **Relatar** o que fechou, o que virou norma (com o caminho), o que foi descartado e o que ficou.

Os critérios para guideline e guardrail — guideline nasce da stack e do objetivo, guardrail de
uma decisão explícita do time — estão na norma, seção *Camada normativa*.

## `registrar <texto>`

Abra uma entrada com a pessoa como autora. Pergunte o tipo pela ferramenta de perguntas, dentro
do vocabulário fechado da norma (*Formato e vocabulário fechado*), e se a entrada tem origem — um
`E-XX`, um `L-XX`, um bloqueio, um gate ou uma revisão. A origem é opcional; com ela, grave com
`python3 "${CLAUDE_SKILL_DIR}/dc.py" huddle-abrir <tipo> --evidencia "<origem>"`, sem ela, com
`python3 "${CLAUDE_SKILL_DIR}/dc.py" huddle-abrir <tipo>` — o texto no stdin nos dois. Responda com
o `H-XX`.

Se o `dc.py` recusar porque o arquivo único de projeto ainda existe, não migre por conta própria:
diga à pessoa que a migração é `python3 "${CLAUDE_SKILL_DIR}/dc.py" huddle-migrar`, e que é ela
quem decide rodar.

Composição via `dc.py` — ponto de entrada único, o que o `allowed-tools` libera; rode-o do
diretório do projeto. **Rode o comando exatamente como está escrito** — sem variável de shell, sem
tirar as aspas e sem trocar o caminho —, porque a liberação de permissão casa o texto do comando.
Subcomandos: `huddle-pauta`, `huddle-fechar`, `huddle-concluir`, `huddle-abrir`, `huddle-migrar`,
`log-resolver`, `metodo-listar`, `metodo-levado`, `criar-guideline`, `adicionar-guardrail` e `explicar`.
