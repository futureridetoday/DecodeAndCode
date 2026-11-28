---
# ── claude code — campos nativos ──────────────────────────────────────────────
name: rethink
description: |
  Revisa princípios, guidelines, guardrails e a foundation do projeto quando o rumo muda: cada item existente (Manter, Editar ou Arquivar), o mapa de recursos, itens novos e os planos abertos afetados, com toda escrita aprovada na conversa. Não atualiza o plugin.

  Use when a pessoa diz que o projeto mudou de rumo — objetivo, marca, público ou estratégia — e quer revisar o que o projeto definiu.

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

Esta skill conduz o `rethink`: quando o rumo do projeto muda, a revisão de princípios, guidelines,
guardrails e da foundation, na conversa principal e com a ferramenta de perguntas.
`plan_root` é o que `python3 "${CLAUDE_SKILL_DIR}/dc.py" raiz` imprime; os scripts ficam em `${CLAUDE_SKILL_DIR}/../decode-and-code/scripts/`, e nada dali se lê, só se roda pelo `dc.py`. O que vale está no codex; leia pelo título com
`python3 "${CLAUDE_SKILL_DIR}/dc.py" codex "<Título>"`, nunca de memória: `Rethink`, `Setup`,
`Princípio`, `Guideline`, `Guardrail`, `Foundation` e `Mapa de recursos do projeto`. Antes do passo 1,
rode `python3 "${CLAUDE_SKILL_DIR}/dc.py" explicar conversa`: as opções de cada sugestão, as duas
edições e os formatos de entrada dos comandos.

Toda escrita passa pelos comandos do `dc.py` e só acontece depois do sim da pessoa. Nunca escreva no
`CLAUDE.md` nem no `AGENTS.md`. Fale no idioma da pessoa, e escreva nele também as rules. Comando que
sai `1` volta para a pessoa com o motivo, e o fluxo continua do item em que parou.

**Toda pergunta vai pela ferramenta de perguntas, inclusive a aberta**: exemplos como opções, e o texto
livre como saída. Não encerre o turno antes do passo 5. Pergunta em prosa encerra o turno, e no turno
seguinte a liberação do `allowed-tools` não vale mais: cada comando do `dc.py` volta a pedir permissão.
Sem a ferramenta de perguntas, peça a resposta como `/decode-and-code:rethink <resposta>`, que carrega
a skill de novo.

## Passos

**0 — Pré-condições e o que mudou.** Confirme que o `rethink` é desejado agora; se não for, encerre.
Leia `<plan_root>/system/setup.md`: sem ele, ou com `completed_at` vazio, diga que o setup vem antes —
`/decode-and-code:setup` — e encerre. O que mudou vem no argumento do comando; sem argumento, pergunte
uma vez. Grave o JSON `{mudanca}` e passe-o a `python3 "${CLAUDE_SKILL_DIR}/dc.py" rethink-start`.

**1 — Perfil.** Rode `python3 "${CLAUDE_SKILL_DIR}/dc.py" descobrir` e compare o `## Perfil` do
`setup.md` com o que mudou. Se o objetivo, o escopo ou a stack mudou, proponha o perfil novo, uma
pergunta por vez, e grave o JSON `{objetivo, escopo, stack, confirmacao}` com
`python3 "${CLAUDE_SKILL_DIR}/dc.py" setup-perfil`. Se o objetivo mudou, o primeiro princípio é o
primeiro item do passo 2.

**2 — Os existentes.** Na ordem princípios → guidelines → guardrails, cada item que o `descobrir`
listou, um por vez, com o texto atual à vista e **Manter**, **Editar** ou **Arquivar**. Diga, para
cada um, o que o rumo novo muda nele, ou por que não muda.

- **Manter** não escreve nada.
- **Editar** segue a conversa de uma sugestão; a versão aprovada vai pelo mesmo comando da criação
  com `--replace`, que mantém nome e lugar: `python3 "${CLAUDE_SKILL_DIR}/dc.py" criar-principio --replace`,
  `python3 "${CLAUDE_SKILL_DIR}/dc.py" criar-guideline --replace` ou
  `python3 "${CLAUDE_SKILL_DIR}/dc.py" adicionar-guardrail --replace`. Trocar o nome não é editar: é
  arquivar o antigo e criar o novo no passo 4.
- **Arquivar** pede o motivo à pessoa. Grave-o, como texto, num arquivo fora do projeto e passe-o com
  `python3 "${CLAUDE_SKILL_DIR}/dc.py" archive <principle|guideline|guardrail> <nome> < <arquivo>`.
  Antes, rode `python3 "${CLAUDE_SKILL_DIR}/dc.py" planos-que-citam <nome>` e mostre os planos abertos
  que o citam: eles precisam de ajuste, que a pessoa decide.

**3 — A foundation.** Rode `python3 "${CLAUDE_SKILL_DIR}/dc.py" foundation`. Proponha, uma coisa por
vez, o padrão de código novo, se o rumo o muda (`foundation-padrao`, texto no stdin), e cada recurso
que entra, muda ou sai do mapa: entra e muda pelo JSON `{nome, tipo, etapa, so_usuario, escopo, permissao}`
para `python3 "${CLAUDE_SKILL_DIR}/dc.py" foundation-recurso`; sai por
`python3 "${CLAUDE_SKILL_DIR}/dc.py" foundation-retirar <nome>`, depois de mostrar o que
`planos-que-citam <nome>` devolve.

**4 — Os novos.** Leia os arquivos do projeto e o que o `descobrir` trouxe, considere o que foi
mantido, editado e arquivado, e sugira itens novos para as três camadas, com o critério do setup e
as opções **Aprovar**, **Editar** e **Rejeitar**, uma sugestão por vez. Princípio respeita o teto,
contando os que ficaram. Grave o aprovado pelo comando da criação, sem `--replace`.

- **O rejeitado volta.** Ao contrário do setup, não pule o que está em `setup-decididas`: o que foi
  rejeitado e ainda vale pode voltar. Mostre quando e por que foi rejeitado, das linhas `rejeitada` do
  `setup.md` e das `rejeitado` do `<plan_root>/system/rethink.md`.
- **O arquivado volta.** Item em `.claude/archive/` que o rumo novo faz valer de novo é sugerido com
  quando e por que foi arquivado. Volta com o mesmo nome por
  `python3 "${CLAUDE_SKILL_DIR}/dc.py" restore <principle|guideline|guardrail> <nome>`; o guardrail
  pede um par novo, o JSON `{proibido, permitido}`, porque o arquivado não guarda o antigo.

Cada decisão dos passos 2 a 4 vai para o histórico na hora, com o JSON `{camada, nome, decisao, motivo}`
para `python3 "${CLAUDE_SKILL_DIR}/dc.py" rethink-record`: `camada` é `princípio`, `guideline`,
`guardrail`, `recurso` ou `padrão de código`; `decisao` é `mantido`, `editado`, `arquivado`, `criado`,
`restaurado`, `rejeitado` ou `retirado` (do mapa); o motivo é obrigatório em `arquivado` e `retirado`.

**5 — Concluir.** Leia o `CLAUDE.md`, o `.claude/CLAUDE.md` e o `AGENTS.md`, se existirem, e aponte à
pessoa cada trecho que contradiz o rumo novo; quem os edita é ela. Resuma o que ficou, o que mudou e o
que foi arquivado, e os planos abertos que pedem ajuste. Diga o que vai para o git: `.claude/rules/`,
`.claude/archive/`, `.claude/guardrails.json`, a foundation, o `setup.md`, se o perfil mudou, e o
`rethink.md`. Depois, o fecho do huddle como nas outras skills:
`python3 "${CLAUDE_SKILL_DIR}/dc.py" huddle-fecho` imprime a seção *Huddle* do codex; o que ficou
aberto entra por `python3 "${CLAUDE_SKILL_DIR}/dc.py" huddle-abrir <tipo> --autor Claude`, com o texto
no stdin, uma chamada por entrada. A mensagem final passa por
`python3 "${CLAUDE_SKILL_DIR}/dc.py" huddle-lint-relatorio`, no stdin, e termina com
`entradas novas no huddle: N (H-XX, …)` — `0`, sem parênteses, quando não houve nada.

## Referência

`huddle-abrir` aceita `pergunta`, `divergência`, `padrão`, `revisitar` e `observação`; outro tipo sai
`1`.

Composição via `dc.py` — ponto de entrada único, o que o `allowed-tools` libera; rode-o do diretório do
projeto. **Rode o comando exatamente como está escrito** — sem variável de shell, sem tirar as aspas e sem
trocar o caminho —, porque a liberação de permissão casa o texto do comando. Subcomandos: `codex`,
`explicar`, `descobrir`, `setup-perfil`, `setup-decididas`, `rethink-start`, `rethink-record`,
`criar-principio`, `criar-guideline`, `adicionar-guardrail`, `archive`, `restore`, `planos-que-citam`,
`foundation`, `foundation-padrao`, `foundation-recurso`, `foundation-retirar`, `huddle-fecho`,
`huddle-abrir` e `huddle-lint-relatorio`.
