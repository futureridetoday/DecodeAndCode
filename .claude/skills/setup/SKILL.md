---
# ── claude code — campos nativos ──────────────────────────────────────────────
name: setup
description: |
  Conduz o primeiro uso do método no projeto: pré-condições, perfil, guidelines, guardrails, huddle e o princípio Decode → Code, uma sugestão por vez, com toda escrita aprovada na conversa.

  Use when a pessoa instala o método num projeto, ou quando o aviso de abertura diz que o setup está pendente.

  <example>
  Context: o aviso de abertura disse que o setup do projeto está pendente
  user: "/decode-and-code:setup"
  commentary: confirma que o setup é desejado agora e percorre as etapas 0 a 6, gravando cada decisão pelo dc.py
  </example>

disable-model-invocation: false
user-invocable: true

allowed-tools: "Read Write Edit Glob Grep Bash(python3 \"${CLAUDE_SKILL_DIR}/dc.py\" *) Bash(python3 ${CLAUDE_SKILL_DIR}/dc.py *)"

model: opus
shell: bash

# ── amflow — rastreabilidade ───────────────────────────────────────────────────
type: skill
project: DecodeAndCode
author: Claude
created: 2026-11-16
status: draft
version: 1.0.0
updated: "2026-11-16"
scope: project
auto_load: false
tags: [decode-and-code, skill, setup]
dependencies: []

hub_id: ""
source: local
---

# setup

Esta skill conduz o modo `setup`: o primeiro uso do método no projeto, na conversa principal e com a
ferramenta de perguntas. A norma é `<plan_root>/system/modelo-dev-units.md`; `plan_root` vem do
`config.json` em `${CLAUDE_SKILL_DIR}/../decode-and-code/`, e os scripts, de
`${CLAUDE_SKILL_DIR}/../decode-and-code/scripts/`.

Toda escrita passa pelos comandos do `dc.py` e só acontece depois do sim da pessoa. Nunca escreva no
`CLAUDE.md` nem no `AGENTS.md`. Fale no idioma da pessoa, e escreva nele também as rules geradas. Comando
que sai `1` volta para a pessoa com o motivo, e o fluxo continua da sugestão em que parou.

## Etapas

**0 — Pré-condições.** Confirme que o setup é desejado agora; se não for, encerre. Sem `.claude/` e
`docs/`, proponha `python3 "${CLAUDE_SKILL_DIR}/dc.py" bootstrap`. Depois rode
`python3 "${CLAUDE_SKILL_DIR}/dc.py" setup-escopo`, que mostra se o plugin está habilitado no projeto; se
não estiver, proponha `python3 "${CLAUDE_SKILL_DIR}/dc.py" setup-escopo --aplicar` e, com o sim, aplique.
Explique que cada colega instala o plugin uma vez por clone.

**1 — Perfil.** Rode `python3 "${CLAUDE_SKILL_DIR}/dc.py" setup-iniciar` e
`python3 "${CLAUDE_SKILL_DIR}/dc.py" descobrir`. Confirme objetivo, escopo e stack, uma pergunta por vez,
com sugestões tiradas do inventário e o texto livre como saída. Grave o JSON
`{objetivo, escopo, stack, confirmacao}` em arquivo, como descrito em *JSON pelo stdin*, e passe-o a
`python3 "${CLAUDE_SKILL_DIR}/dc.py" setup-perfil`.

**2 e 3 — Guidelines, depois guardrails.** Antes de sugerir, rode
`python3 "${CLAUDE_SKILL_DIR}/dc.py" setup-decididas`: o que já está lá não volta, e o que está em
`existentes` no `descobrir` se registra como `existente`. Todas as guidelines antes dos guardrails, uma
por vez, com três opções: **Aprovar**, **Editar** e **Rejeitar**.

- **Aprovar** grava e registra; **Rejeitar** registra, com o motivo se a pessoa der um.
- **Editar** abre uma segunda pergunta: **Edição livre** (a pessoa diz o que mudar, pelo texto livre, e
  você aplica; só ajuda a redigir se ela pedir) ou **Edição guiada** (perguntas uma por vez, cada uma com
  sugestões derivadas das anteriores, até escopo, regra e exceção estarem definidos). A versão editada
  volta com **Aprovar**, **Editar** ou **Rejeitar**.

Guideline nasce da stack e do objetivo do projeto, escopada pelos caminhos onde vale; o que o `CLAUDE.md`
ou um linter já impõe não vira guideline. Guardrail nasce de decisão explícita do time que desvia do
padrão da stack, e barra o que uma escrita contém, por regex — pergunte pelas decisões e procure-as no
inventário. Mostre a proposta inteira e grave só depois do **Aprovar**: guideline, o JSON
`{nome, descricao, paths, corpo}` para `python3 "${CLAUDE_SKILL_DIR}/dc.py" criar-guideline` (com
`aguardando: true` se o caminho ainda não existe); guardrail, o JSON `{regra, proibido, permitido}` para
`python3 "${CLAUDE_SKILL_DIR}/dc.py" adicionar-guardrail`, no formato de *Formato do guardrail*. A norma,
seção *Camada normativa*, cobre a guideline. Cada resultado vai para `python3 "${CLAUDE_SKILL_DIR}/dc.py" setup-registrar`, com o JSON
`{chave, tipo, origem, resultado, detalhe}`. O `setup-registrar` aceita só um vocabulário fechado, e valor
fora dele sai `1`: `tipo` é `guideline`, `guardrail` ou `princípio`; `origem` é `stack`, `decisão do time`,
`existente` ou `arquivo <caminho>`; `resultado` é `aceita`, `rejeitada` ou `existente`. Sugestão editada e
depois aprovada é `aceita` — não existe `editada`. Achado com cara de princípio, e não de guideline ou
guardrail, vira entrada `observação` no huddle e se registra com `tipo: princípio`, `resultado: rejeitada`
e o id `H-XX` no `detalhe`; se o projeto ainda tem o arquivo único antigo, o `huddle-abrir` recusa, e você
propõe o `huddle-migrar` da etapa 4 antes de registrar.

### JSON pelo stdin, por arquivo

O Claude Code recusa heredoc com JSON ("Contains brace with quote character"). Para `setup-perfil`,
`setup-registrar`, `criar-guideline` e `adicionar-guardrail`, grave o JSON com a ferramenta `Write` num
arquivo temporário fora do projeto (o scratchpad da sessão) e passe-o com `<`, na forma que o
`allowed-tools` casa: `python3 "${CLAUDE_SKILL_DIR}/dc.py" setup-perfil < <arquivo>`. O `huddle-abrir`
lê texto, não JSON, e segue como nas outras skills.

### Formato do guardrail

O JSON do `adicionar-guardrail` é `{regra, proibido, permitido}`:

- `regra` tem quatro campos, todos texto não vazio: `nome` (kebab-case), `ferramenta` (regex sobre o nome
  da ferramenta, ex.: `^(Write|Edit)$`), `detector` (regex) e `mensagem`.
- O `detector` casa o texto de todos os valores de `tool_input` que são texto, unidos por quebra de
  linha: num `Write`, o caminho e o conteúdo; num `Edit`, o caminho, o trecho antigo e o novo. Não há
  campo de caminho — a restrição de pasta vai dentro do próprio regex.
- `proibido` e `permitido` têm a forma do payload do hook, `{tool_name, tool_input}`; o comando recusa a
  regra que não nega o `proibido` ou que nega o `permitido`.

### Tipos do huddle

`huddle-abrir` aceita `pergunta`, `divergência`, `padrão`, `revisitar` e `observação`; outro tipo
(`contorno`, por exemplo) sai `1`.

**4 — Huddle.** Se o projeto ainda tem o arquivo único antigo, proponha
`python3 "${CLAUDE_SKILL_DIR}/dc.py" huddle-migrar` e rode-o com o sim; senão rode
`python3 "${CLAUDE_SKILL_DIR}/dc.py" huddle-iniciar`, ou apenas explique se o arquivo da pessoa já existe.
Explique o que é o huddle, o que dispara uma entrada, que cada pessoa tem o seu, que a pessoa e o Claude
registram nele, o lembrete semanal e como ajustar `reminder_days`, e que um item pode ser promovido a
guideline ou guardrail.

**5 — O método.** Rode `python3 "${CLAUDE_SKILL_DIR}/dc.py" explicar` e explique Decode e Code a partir
do que ele imprime, sem texto próprio que possa divergir: Decode é pensar antes de construir (Clarificar,
Evitar, Reduzir, os gates A e B e o porte do plano); Code é o que o plugin faz hoje, com `derive`
decompondo e `implement` executando cada unidade em cold-start, e quem orquestra revisando a entrega
antes de versionar.

**6 — Concluir.** Rode `python3 "${CLAUDE_SKILL_DIR}/dc.py" setup-concluir`. Depois, o fecho do huddle
como nas outras skills: `python3 "${CLAUDE_SKILL_DIR}/dc.py" huddle-fecho` imprime os gatilhos; o que
ficou aberto entra por `python3 "${CLAUDE_SKILL_DIR}/dc.py" huddle-abrir <tipo> --autor Claude`, com o
texto no stdin, uma chamada por entrada. A mensagem final passa por
`python3 "${CLAUDE_SKILL_DIR}/dc.py" huddle-lint-relatorio`, no stdin, e termina com
`entradas novas no huddle: N (H-XX, …)` — `0`, sem parênteses, quando não houve nada.

Composição via `dc.py` — ponto de entrada único, o que o `allowed-tools` libera; rode-o do diretório do
projeto. **Rode o comando exatamente como está escrito** — sem variável de shell, sem tirar as aspas e sem
trocar o caminho —, porque a liberação de permissão casa o texto do comando. Subcomandos: `bootstrap`,
`setup-escopo`, `setup-iniciar`, `descobrir`, `setup-perfil`, `setup-decididas`, `setup-registrar`,
`criar-guideline`, `adicionar-guardrail`, `huddle-migrar`, `huddle-iniciar`, `explicar`, `setup-concluir`,
`huddle-fecho`, `huddle-abrir` e `huddle-lint-relatorio`.
