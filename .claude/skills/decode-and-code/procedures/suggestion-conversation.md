---
# about
name: suggestion-conversation
type: knowledge
project: ""
description: Passo a passo da conversa de uma sugestão que o setup, o rethink e o huddle compartilham — as opções, o JSON pelo stdin, os padrões de paths e o formato do guardrail
tags: [procedimento, setup, rethink, huddle]

# history
author: Bortoli
created: 2026-11-27
status: stable
version: 1.0.0
updated: ""

# system
scope: project
source: ""
auto_load: false
checksum: ""
dependencies: []
---

# Conversa de uma sugestão

Procedimento, não método: o que princípio, guideline e guardrail são, e quem os grava, está no
codex (*Princípio*, *Guideline*, *Guardrail* e *Rethink*). Aqui fica o como da conversa que o setup e
o rethink conduzem, e de que o huddle usa o *JSON pelo stdin*. Cada skill o imprime por
`dc.py explicar conversa`.

## As opções

Uma sugestão por vez, cada uma com a proposta inteira à vista, pela ferramenta de perguntas. Item
novo tem três opções: **Aprovar**, **Editar** e **Rejeitar**. Item existente, no rethink, tem
**Manter**, **Editar** e **Arquivar**.

- **Aprovar** grava e registra; **Rejeitar** registra, com o motivo se a pessoa der um.
- **Editar** abre uma segunda pergunta: **Edição livre** (a pessoa diz o que mudar, pelo texto livre,
  e a skill aplica; só ajuda a redigir se ela pedir) ou **Edição guiada** (perguntas uma por vez,
  cada uma com sugestões derivadas das anteriores, até escopo, regra e exceção estarem definidos). A
  versão editada volta com as mesmas três opções.
- Nada se grava antes do sim, e comando que sai `1` volta para a pessoa com o motivo; a conversa
  continua da sugestão em que parou.

## JSON pelo stdin, por arquivo

O Claude Code recusa heredoc com JSON ("Contains brace with quote character"). Para os comandos que
leem JSON — `setup-perfil`, `setup-registrar`, `criar-principio`, `criar-guideline`,
`adicionar-guardrail`, `restore` de guardrail, `rethink-start` e `rethink-record` —, grave o JSON com a
ferramenta `Write` num arquivo temporário fora do projeto (o scratchpad da sessão) e passe-o com `<`,
na forma que o `allowed-tools` casa: `python3 "${CLAUDE_SKILL_DIR}/dc.py" setup-perfil < <arquivo>`. O
`huddle-abrir` e o `archive` leem texto, não JSON.

## Padrões de `paths`

O `criar-guideline` recusa duas formas: arquivo da raiz pelo nome e chaves. Arquivo da raiz entra
como `**/<arquivo>` (`**/tailwind.config.ts`, não `tailwind.config.ts`), e cada extensão vai num
padrão próprio (`src/**/*.ts` e `src/**/*.tsx`, não `src/**/*.{ts,tsx}`).

## Formato do guardrail

O JSON do `adicionar-guardrail` é `{regra, proibido, permitido}`:

- `regra` tem quatro campos, todos texto não vazio: `nome` (kebab-case), `ferramenta` (regex sobre o
  nome da ferramenta, ex.: `^(Write|Edit)$`), `detector` (regex) e `mensagem`.
- O `detector` casa o texto dos valores de `tool_input` que são texto, unidos por quebra de linha:
  num `Write`, o caminho e o conteúdo; num `Edit`, o caminho e o trecho novo — o antigo fica de fora,
  para que o `Edit` que remove o problema passe. Não há campo de caminho: a restrição de pasta vai
  dentro do próprio regex.
- Para "na pasta X, nunca Y", o detector casa o caminho absoluto e o relativo e atravessa linhas:
  `(?s)(^|/)X/.*Y`. Prove os dois no par: um `proibido` com caminho relativo e o `permitido` fora de
  `X`.
- `proibido` e `permitido` têm a forma do payload do hook, `{tool_name, tool_input}`; o comando recusa
  a regra que não nega o `proibido` ou que nega o `permitido`.
