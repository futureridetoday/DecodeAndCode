---
# ── claude code — campos nativos ──────────────────────────────────────────────
name: rethink
description: |
  Repensa a norma do projeto — princípios, guidelines e guardrails — depois de uma mudança de rumo: revisa cada item existente (Manter, Editar ou Arquivar), sugere itens novos e registra cada decisão, com toda escrita aprovada na conversa. Não atualiza o plugin.

  Use when a pessoa diz que o projeto mudou de rumo — objetivo, marca, público ou estratégia — e quer revisar a norma do projeto.

  <example>
  Context: o app trocou a marca azul por laranja e o objetivo de economizar por consciência de compra
  user: "/decode-and-code:rethink marca laranja, design divertido, objetivo: consciência das escolhas de compra"
  commentary: abre o histórico com o que mudou, reescreve o perfil, revisa os itens existentes um a um e depois sugere os novos
  </example>

disable-model-invocation: true
user-invocable: true

allowed-tools: "Read Write Edit Glob Grep Bash(python3 \"${CLAUDE_SKILL_DIR}/dc.py\" *) Bash(python3 ${CLAUDE_SKILL_DIR}/dc.py *)"

argument-hint: "[o que mudou]"

model: opus
shell: bash

# ── amflow — rastreabilidade ───────────────────────────────────────────────────
type: skill
project: DecodeAndCode
author: Claude
created: 2026-11-22
status: draft
version: 1.0.0
updated: "2026-11-22"
scope: project
auto_load: false
tags: [decode-and-code, skill, rethink]
dependencies: []

hub_id: ""
source: local
---

# rethink

Esta skill conduz o `rethink`: depois de uma mudança de rumo, a revisão de princípios, guidelines e
guardrails do projeto, na conversa principal e com a ferramenta de perguntas. A norma é
`<plan_root>/system/modelo-dev-units.md`, seção *Rethink*; `plan_root` vem do `config.json` em
`${CLAUDE_SKILL_DIR}/../decode-and-code/`, e os scripts, de `${CLAUDE_SKILL_DIR}/../decode-and-code/scripts/`.

Antes de começar, rode `python3 "${CLAUDE_SKILL_DIR}/dc.py" explicar rethink` e
`python3 "${CLAUDE_SKILL_DIR}/dc.py" explicar conversa`: o primeiro é o fluxo, o segundo as opções de
cada sugestão, as duas edições e os formatos de entrada dos comandos. Para o que mais a norma diz, use
`explicar` com a seção — `camada-normativa` (o teste de princípio, o teto, *Editar e arquivar*) e
`setup` (o critério de sugestão) —; não leia o código do plugin nem a norma com `grep` ou `sed`.

Toda escrita passa pelos comandos do `dc.py` e só acontece depois do sim da pessoa. Nunca escreva no
`CLAUDE.md` nem no `AGENTS.md`. Fale no idioma da pessoa, e escreva nele também as rules. Comando que
sai `1` volta para a pessoa com o motivo, e o fluxo continua do item em que parou.

**Toda pergunta vai pela ferramenta de perguntas, inclusive a aberta**: exemplos como opções, e o texto
livre como saída. Não encerre o turno antes do passo 4. Pergunta em prosa encerra o turno, e no turno
seguinte a liberação do `allowed-tools` não vale mais: cada comando do `dc.py` volta a pedir permissão.

## Passos

**0 — Pré-condições e o que mudou.** Confirme que o `rethink` é desejado agora; se não for, encerre.
Leia `<plan_root>/system/setup.md`: sem ele, ou com `completed_at` vazio, diga que o setup vem antes —
`/decode-and-code:setup` — e encerre. O que mudou vem no argumento do comando; sem argumento, pergunte
uma vez. Grave o JSON `{mudanca}` e passe-o a `python3 "${CLAUDE_SKILL_DIR}/dc.py" rethink-start`.

**1 — Perfil.** Rode `python3 "${CLAUDE_SKILL_DIR}/dc.py" descobrir` e compare o `## Perfil` do
`setup.md` com o que mudou. Se o objetivo, o escopo ou a stack mudou, proponha o perfil novo, uma
pergunta por vez, e grave o JSON `{objetivo, escopo, stack, confirmacao}` com
`python3 "${CLAUDE_SKILL_DIR}/dc.py" setup-perfil`. Se o objetivo mudou, o north star é o primeiro
item do passo 2.

**2 — Os existentes.** Na ordem princípios → guidelines → guardrails, cada item que o `descobrir`
listou, um por vez, com o texto atual à vista e **Manter**, **Editar** ou **Arquivar**. Diga, para
cada um, o que o rumo novo muda nele, ou por que não muda.

- **Manter** não escreve na norma.
- **Editar** segue a conversa de uma sugestão; a versão aprovada vai pelo mesmo comando da criação
  com `--replace`, que mantém nome e lugar: `python3 "${CLAUDE_SKILL_DIR}/dc.py" criar-principio --replace`,
  `python3 "${CLAUDE_SKILL_DIR}/dc.py" criar-guideline --replace` ou
  `python3 "${CLAUDE_SKILL_DIR}/dc.py" adicionar-guardrail --replace`. Trocar o nome não é editar: é
  arquivar o antigo e criar o novo no passo 3.
- **Arquivar** pede o motivo à pessoa. Grave-o, como texto, num arquivo fora do projeto e passe-o com
  `python3 "${CLAUDE_SKILL_DIR}/dc.py" archive <principle|guideline|guardrail> <nome> < <arquivo>`.
  Antes, procure com `Grep` as unidades em `<plan_root>/` que citam o item e mostre-as: elas passam a
  listá-lo em `Não resolvidas:`.

Cada decisão vai para o histórico na hora, com o JSON `{camada, nome, decisao, motivo}` para
`python3 "${CLAUDE_SKILL_DIR}/dc.py" rethink-record`: `camada` é `princípio`, `guideline` ou
`guardrail`; `decisao` é `mantido`, `editado` ou `arquivado`; o motivo é obrigatório em `arquivado`.

**3 — Os novos.** Leia os arquivos do projeto e o que o `descobrir` trouxe, considere o que foi
mantido, editado e arquivado, e sugira itens novos para as três camadas, com o critério do setup e
as opções **Aprovar**, **Editar** e **Rejeitar**, uma sugestão por vez. Princípio respeita o teto de 5,
contando os que ficaram. Grave o aprovado pelo comando da criação, sem `--replace`.

- **O rejeitado volta.** Ao contrário do setup, não pule o que está em `setup-decididas`: o que foi
  rejeitado e ainda vale pode voltar. Mostre quando e por que foi rejeitado, das linhas `rejeitada` do
  `setup.md` e das `rejeitado` do `<plan_root>/system/rethink.md`.
- **O arquivado volta.** Item em `.claude/archive/` que o rumo novo faz valer de novo é sugerido com
  quando e por que foi arquivado. Volta com o mesmo nome por
  `python3 "${CLAUDE_SKILL_DIR}/dc.py" restore <principle|guideline|guardrail> <nome>`; o guardrail
  pede um par novo, o JSON `{proibido, permitido}`, porque o arquivado não guarda o antigo.

Registre cada resultado por `rethink-record`, com `decisao` `criado`, `restaurado` ou `rejeitado`.

**4 — Concluir.** Resuma o que ficou, o que mudou e o que foi arquivado. Diga o que vai para o git:
`.claude/rules/`, `.claude/archive/`, `.claude/guardrails.json`, o `setup.md`, se o perfil mudou, e o
`rethink.md`. Depois, o fecho do huddle como nas outras skills:
`python3 "${CLAUDE_SKILL_DIR}/dc.py" huddle-fecho` imprime os gatilhos; o que ficou aberto entra por
`python3 "${CLAUDE_SKILL_DIR}/dc.py" huddle-abrir <tipo> --autor Claude`, com o texto no stdin, uma
chamada por entrada. A mensagem final passa por
`python3 "${CLAUDE_SKILL_DIR}/dc.py" huddle-lint-relatorio`, no stdin, e termina com
`entradas novas no huddle: N (H-XX, …)` — `0`, sem parênteses, quando não houve nada.

## Referência

`huddle-abrir` aceita `pergunta`, `divergência`, `padrão`, `revisitar` e `observação`; outro tipo sai
`1`.

Composição via `dc.py` — ponto de entrada único, o que o `allowed-tools` libera; rode-o do diretório do
projeto. **Rode o comando exatamente como está escrito** — sem variável de shell, sem tirar as aspas e sem
trocar o caminho —, porque a liberação de permissão casa o texto do comando. Subcomandos: `explicar`,
`descobrir`, `setup-perfil`, `setup-decididas`, `rethink-start`, `rethink-record`, `criar-principio`,
`criar-guideline`, `adicionar-guardrail`, `archive`, `restore`, `huddle-fecho`, `huddle-abrir` e
`huddle-lint-relatorio`.
