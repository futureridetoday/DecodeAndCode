---
# ── claude code — campos nativos ──────────────────────────────────────────────
name: code
description: |
  Conduz o code (P6) de uma unidade derivada, ou das tarefas de um plano pequeno, num subagent sem o histórico da conversa: escreve o teste e o código pelo critério de aceite e devolve a entrega para a aprovação (P7).

  Use when o usuário pede para executar uma unidade, um plano pequeno aprovado, ou para aprovar uma entrega.

  <example>
  Context: unidade derivada e aprovada, a anterior com a entrega aprovada
  user: "/decode-and-code:code 0031-02"
  commentary: modo code — gate de entrada, teste e código pelo critério, verificar, e a entrega volta para o usuário testar e aprovar
  </example>

disable-model-invocation: false
user-invocable: true

allowed-tools: "Read Write Edit Glob Grep Bash(python3 \"${CLAUDE_SKILL_DIR}/dc.py\" *) Bash(python3 ${CLAUDE_SKILL_DIR}/dc.py *)"

argument-hint: "<unidade> | aprovar <unidade ou plano pequeno>"

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
version: 2.0.0
updated: "2026-11-27"
scope: project
auto_load: false
tags: [decode-and-code, skill, unidade, cold-start, code]
dependencies: []

hub_id: ""
source: local
---

# code

Pedido: $ARGUMENTS

Você executa o modo `code`, sem o histórico da conversa. `plan_root` é o que `python3 "${CLAUDE_SKILL_DIR}/dc.py" raiz` imprime; os scripts ficam em `${CLAUDE_SKILL_DIR}/../decode-and-code/scripts/`, e nada dali se lê, só se roda pelo `dc.py`. Os subcomandos do `dc.py` recebem
o caminho da unidade ou o id `NNNN-nn`, que o `dc.py` resolve.

## `aprovar <alvo>`

Só quando o usuário pediu, com estas palavras: rode
`python3 "${CLAUDE_SKILL_DIR}/dc.py" aprovar-entrega <alvo>` e devolva a saída: quem aprova é o
`user.name` do git do projeto, e `--por "<nome>"` só entra se o usuário disser outro nome. Recusa (código 2) volta ao usuário com o motivo. Se esta aprovação fecha o plano e a proposta
declara quando conferir a hipótese, abra
`python3 "${CLAUDE_SKILL_DIR}/dc.py" huddle-abrir revisitar --autor Claude`, com o plano e a data no
stdin. Nada mais neste modo.

## `<unidade>` ou `<plano pequeno>`

Antes de tudo, leia do codex as seções que valem aqui:
`python3 "${CLAUDE_SKILL_DIR}/dc.py" codex Code Unidade Entrega "Critério de aceite" Teste Lacuna Cold-start Huddle Guardrail "Recurso do projeto"`.

1. **Gate de entrada** — `python3 "${CLAUDE_SKILL_DIR}/dc.py" entrada-code <alvo>`; qualquer
   problema encerra sem escrever nada, e o relatório o devolve.
2. **Ler** a unidade inteira e trazer as guidelines dela com
   `python3 "${CLAUDE_SKILL_DIR}/dc.py" normas <unidade>`; linha sob `Não resolvidas:` é
   insuficiência da unidade. No pequeno, leia o plano técnico: as guidelines dos caminhos que tocar
   carregam sozinhas, pelo `paths:`.
3. **Conferir `## Depende de`** contra o disco. Divergência, ou unidade insuficiente para o
   critério, para tudo: a proposta de ajuste vai no relatório como lacuna `L-XX`, e nada se escreve
   até o usuário aprovar.
4. **Teste e código.** Escreva o teste declarado, que cobre o critério, e o código que o faz
   passar, tocando só os arquivos declarados e seguindo as guidelines. Durante o trabalho,
   `python3 "${CLAUDE_SKILL_DIR}/dc.py" verificar <alvo> --dry-run` roda o teste declarado sem
   gravar — é o único caminho até ele. No pequeno, o alvo é o plano, e cada tarefa feita se marca
   `- [x]`.
5. **Gate de saída** — `python3 "${CLAUDE_SKILL_DIR}/dc.py" verificar <alvo>`, e
   `python3 "${CLAUDE_SKILL_DIR}/dc.py" projetar-backlog <dir_plano ou plano pequeno>`.
6. **Pare antes de** mexer em algo que não se desfaz ou que está fora do repositório: vai no
   relatório como pedido de sim. Achado fora do escopo vira entrada no huddle (passo 8), nunca trabalho a mais.
7. **Relatório da entrega:** os arquivos alterados, a saída do teste, uma afirmação medida por
   outro caminho (e qual), as divergências e as lacunas. Termina dizendo ao usuário que teste e,
   se aprovar, rode `/decode-and-code:code aprovar <alvo>`.
8. **Fecho do huddle** — `python3 "${CLAUDE_SKILL_DIR}/dc.py" huddle-fecho` imprime a seção *Huddle* do codex. O que ficou aberto entra por `python3 "${CLAUDE_SKILL_DIR}/dc.py" huddle-abrir <tipo> --autor Claude`, com o texto no stdin, uma chamada por entrada. Antes de enviar, a mensagem final passa por `python3 "${CLAUDE_SKILL_DIR}/dc.py" huddle-lint-relatorio`, no stdin, e termina com `entradas novas no huddle: N (H-XX, …)` — `0`, sem parênteses, quando não houve nada.

> **Quem executa não commita.** O modo entrega arquivos e relatório; versionar é de quem orquestra,
> depois da aprovação.

Composição via `dc.py` — ponto de entrada único, o que o `allowed-tools` libera; rode-o do diretório do projeto. **Rode o comando exatamente como está escrito** — sem variável de shell, sem tirar as aspas e sem trocar o caminho —, porque a liberação de permissão casa o texto do comando. Subcomandos: `codex`, `entrada-code`, `normas`, `verificar`, `projetar-backlog`, `aprovar-entrega`, `huddle-fecho`, `huddle-abrir` e `huddle-lint-relatorio`.

## Saída

Uma única mensagem: o relatório da entrega, ou o motivo da parada.
