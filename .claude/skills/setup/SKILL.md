---
# ── claude code — campos nativos ──────────────────────────────────────────────
name: setup
description: |
  Conduz o primeiro uso do método no projeto: pré-condições, perfil, princípios, guidelines, guardrails, huddle e o princípio Decode → Code, uma sugestão por vez, com toda escrita aprovada na conversa.

  Use when a pessoa instala o método num projeto, ou quando o aviso de abertura diz que o setup está pendente.

  <example>
  Context: o aviso de abertura disse que o setup do projeto está pendente
  user: "/decode-and-code:setup"
  commentary: confirma que o setup é desejado agora e percorre as etapas 0 a 7, gravando cada decisão pelo dc.py
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
version: 1.1.0
updated: "2026-11-22"
scope: project
auto_load: false
tags: [decode-and-code, skill, setup]
dependencies: []

hub_id: ""
source: local
---

# setup

Esta skill conduz o modo `setup`: o primeiro uso do método no projeto, na conversa principal e com a
ferramenta de perguntas. `plan_root` vem do `config.json` ao lado de
`${CLAUDE_SKILL_DIR}/../decode-and-code/scripts/`, nunca fixo. O que vale está no codex; leia pelo
título com `python3 "${CLAUDE_SKILL_DIR}/dc.py" codex "<Título>"`, nunca de memória: `Setup`,
`Princípio`, `Guideline`, `Guardrail`, `Foundation`, `Padrão de código`, `Huddle`,
`Recurso do projeto` e, por fim, `Mapa de recursos do projeto`.

Toda escrita passa pelos comandos do `dc.py` e só acontece depois do sim da pessoa. Nunca escreva no
`CLAUDE.md` nem no `AGENTS.md`, e não grave o que eles já dizem. Fale no idioma da pessoa, e escreva
nele também o que gravar. Comando que sai `1` volta para a pessoa com o motivo, e o fluxo continua da
sugestão em que parou.

**Toda pergunta vai pela ferramenta de perguntas, inclusive a aberta**: exemplos como opções, e o texto
livre como saída. Não encerre o turno antes da etapa 7. Pergunta em prosa encerra o turno, e no turno
seguinte a liberação do `allowed-tools` não vale mais: cada comando do `dc.py` volta a pedir permissão.

Antes da etapa 1, rode `python3 "${CLAUDE_SKILL_DIR}/dc.py" explicar conversa`: as opções de cada
sugestão, as duas edições e os formatos de entrada dos comandos — *JSON pelo stdin*, *Padrões de
`paths`* e *Formato do guardrail* — estão lá, e esta skill não os repete.

## Etapas

**0 — Pré-condições.** Confirme que o setup é desejado agora; se não for, encerre. Proponha
`python3 "${CLAUDE_SKILL_DIR}/dc.py" bootstrap`: ele cria só o que falta e nunca sobrescreve. Depois rode
`python3 "${CLAUDE_SKILL_DIR}/dc.py" setup-escopo`. A saída tem duas linhas: `habilitado` diz se o plugin
está em `enabledPlugins` do `.claude/settings.json`, e `marketplace`, se o marketplace está em
`extraKnownMarketplaces`. Com alguma `false`, proponha
`python3 "${CLAUDE_SKILL_DIR}/dc.py" setup-escopo --aplicar`, que acrescenta só o que falta, e aplique com
o sim. Explique que a habilitação commitada não baixa o plugin: cada pessoa o instala uma vez por clone.

**1 — Perfil.** Rode `python3 "${CLAUDE_SKILL_DIR}/dc.py" setup-iniciar` e
`python3 "${CLAUDE_SKILL_DIR}/dc.py" descobrir`. O `descobrir` já traz o começo de cada arquivo, dentro de
uma cerca; não os releia. Confirme objetivo, escopo e stack, uma pergunta por vez, com sugestões tiradas
do inventário e o texto livre como saída. Grave o JSON `{objetivo, escopo, stack, confirmacao}` em
arquivo, como descrito em *JSON pelo stdin*, e passe-o a `python3 "${CLAUDE_SKILL_DIR}/dc.py" setup-perfil`.

**2 — Huddle.** Se o projeto ainda tem o arquivo único antigo, proponha
`python3 "${CLAUDE_SKILL_DIR}/dc.py" huddle-migrar` e rode-o com o sim; senão rode
`python3 "${CLAUDE_SKILL_DIR}/dc.py" huddle-iniciar`, ou apenas explique se o arquivo da pessoa já existe.
Explique o huddle a partir da seção do codex, em poucas frases, e diga que as dúvidas que aparecerem
daqui em diante vão para ele.

**3 — Princípios.** Rode `python3 "${CLAUDE_SKILL_DIR}/dc.py" setup-decididas` e conte os princípios que
já existem; o teto da seção `Princípio` conta com eles. Sugira, uma por vez, com as opções de item novo:

1. O **primeiro**, do objetivo declarado no perfil: enunciado curto e um teste que só este objetivo
   produz, como "adicionar uma marca muda só tokens". Origem `proposto`.
2. Os **demais**: pergunte o que, neste projeto, não se viola de jeito nenhum. O que o `CLAUDE.md` ou o
   `.claude/CLAUDE.md` já afirma carrega sozinho: registre como `existente`, sem gravar.

Cada sugestão mostra o teste de equipe competente da seção `Princípio` e por que passou; se não passa,
leve-a à etapa 5 como guideline. Grave o aprovado com o JSON `{nome, enunciado, teste}` para
`python3 "${CLAUDE_SKILL_DIR}/dc.py" criar-principio` e registre com `tipo: princípio`, como na etapa 5.

**4 — Foundation.** Mostre e grave com o sim, uma coisa por vez:

- o **padrão de código**: tirado dos linters e da configuração que o `descobrir` mostrou, em poucas
  linhas; quando um recurso do projeto já o guarda, a frase que nomeia esse recurso. Texto no stdin de
  `python3 "${CLAUDE_SKILL_DIR}/dc.py" foundation-padrao`; registre com `tipo: padrão de código`.
- cada **recurso** de *Recursos do projeto* do `descobrir`, com a etapa em que entra, se só a pessoa o
  chama, o escopo (projeto ou pessoal) e se Claude pode chamá-lo sem perguntar (a permissão de uso, que
  só a pessoa dá). O JSON `{nome, tipo, etapa, so_usuario, escopo, permissao}` vai para
  `python3 "${CLAUDE_SKILL_DIR}/dc.py" foundation-recurso`; `tipo` é `skill`, `command`, `agent`,
  `mcp`, `instrução` ou `outro`; `etapa`, `decode`, `revisão`, `derive`, `code` ou `fora do workflow`;
  `escopo`, `projeto` ou `pessoal`; os outros dois, `sim` ou `não`. Registre com `tipo: recurso`.

**5 e 6 — Guidelines, depois guardrails.** O que já está em `setup-decididas` não volta, e o que está em
`existentes` no `descobrir` se registra como `existente`. Todas as guidelines antes dos guardrails, uma
por vez, com as opções de item novo.

Guideline nasce da stack e do objetivo do projeto, escopada pelos caminhos onde vale; o que o `CLAUDE.md`
ou um linter já impõe não vira guideline. Um recurso do mapa ligado a caminhos pode ser nomeado pela
guideline daqueles caminhos: `paths` onde ele vale, e corpo que começa por um título e diz qual recurso
usar, como `# Interface` e "Componente novo em `src/components/` passa pela skill `ui-builder` do
projeto". O título é o que o `derive` cita na unidade. Agent não entra: o `code` roda em subagente, que
não cria outro. Guardrail nasce de decisão explícita do time que desvia do padrão da stack, e barra o
que uma escrita contém, por regex — pergunte pelas decisões e procure-as no inventário. Mostre a
proposta inteira e grave só depois do **Aprovar**: guideline, o JSON `{nome, descricao, paths, corpo}`
para `python3 "${CLAUDE_SKILL_DIR}/dc.py" criar-guideline` (com `aguardando: true` se o caminho ainda
não existe); guardrail, o JSON `{regra, proibido, permitido}` para
`python3 "${CLAUDE_SKILL_DIR}/dc.py" adicionar-guardrail`.

Cada resultado das etapas 3 a 6 vai para `python3 "${CLAUDE_SKILL_DIR}/dc.py" setup-registrar`, com o
JSON `{chave, tipo, origem, resultado, detalhe}`, em vocabulário fechado — valor fora dele sai `1`:
`tipo` é `guideline`, `guardrail`, `princípio`, `padrão de código` ou `recurso`; `origem` é `stack`,
`decisão do time`, `existente`, `proposto` ou `arquivo <caminho>`; `resultado` é `aceita`, `rejeitada`
ou `existente`. Sugestão editada e depois aprovada é `aceita`.

**7 — Concluir.** Explique o método em poucas frases a partir de
`python3 "${CLAUDE_SKILL_DIR}/dc.py" explicar`, sem texto próprio que possa divergir, e rode
`python3 "${CLAUDE_SKILL_DIR}/dc.py" setup-concluir`. Diga o que vai para o git:
`.claude/settings.json`, `.claude/rules/`, `.claude/guardrails.json`, o que o bootstrap criou em
`<plan_root>/`, a foundation, o `setup.md` e o arquivo de huddle da pessoa. E diga o que é pessoal:
`.claude/settings.local.json` guarda as permissões que a pessoa concedeu e não vai para o git — o setup
não escreve no `.gitignore`, então cabe a ela. Depois, o fecho do huddle como nas outras skills:
`python3 "${CLAUDE_SKILL_DIR}/dc.py" huddle-fecho` imprime a seção *Huddle* do codex; o que ficou aberto
entra por `python3 "${CLAUDE_SKILL_DIR}/dc.py" huddle-abrir <tipo> --autor Claude`, com o texto no
stdin, uma chamada por entrada. A mensagem final passa por
`python3 "${CLAUDE_SKILL_DIR}/dc.py" huddle-lint-relatorio`, no stdin, e termina com
`entradas novas no huddle: N (H-XX, …)` — `0`, sem parênteses, quando não houve nada.

## Referência

### Tipos do huddle

`huddle-abrir` aceita `pergunta`, `divergência`, `padrão`, `revisitar` e `observação`; outro tipo
(`contorno`, por exemplo) sai `1`.

Composição via `dc.py` — ponto de entrada único, o que o `allowed-tools` libera; rode-o do diretório do
projeto. **Rode o comando exatamente como está escrito** — sem variável de shell, sem tirar as aspas e sem
trocar o caminho —, porque a liberação de permissão casa o texto do comando. Subcomandos: `codex`,
`bootstrap`, `setup-escopo`, `setup-iniciar`, `descobrir`, `setup-perfil`, `setup-decididas`,
`setup-registrar`, `criar-principio`, `foundation-padrao`, `foundation-recurso`, `criar-guideline`,
`adicionar-guardrail`, `huddle-migrar`, `huddle-iniciar`, `explicar`, `setup-concluir`, `huddle-fecho`,
`huddle-abrir` e `huddle-lint-relatorio`.
