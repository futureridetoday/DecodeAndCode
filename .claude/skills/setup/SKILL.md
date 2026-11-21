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
version: 1.0.0
updated: "2026-11-20"
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

**Toda pergunta vai pela ferramenta de perguntas, inclusive a aberta**: exemplos como opções, e o texto
livre como saída. Não encerre o turno antes da etapa 7. Pergunta em prosa encerra o turno, e no turno
seguinte a liberação do `allowed-tools` não vale mais: cada comando do `dc.py` volta a pedir permissão.

Para o que a norma diz, use `python3 "${CLAUDE_SKILL_DIR}/dc.py" explicar`, com ou sem seção; não leia o
código do plugin nem a norma com `grep` ou `sed`.

## Etapas

**0 — Pré-condições.** Confirme que o setup é desejado agora; se não for, encerre. Se faltar `.claude/`,
`docs/` ou a norma em `<plan_root>/system/modelo-dev-units.md`, proponha
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

**2 — Princípios.** Rode `python3 "${CLAUDE_SKILL_DIR}/dc.py" explicar camada-normativa`: a subseção
*Princípio* traz o teste, o formato, o teto e os princípios do método — não os reescreva de memória. O
teto é 5, ideal 3, contando os que já existem; atingido, siga para a etapa 3. Sugira nesta ordem, uma
por vez, com as opções da etapa 3:

1. O **north star**, do objetivo do perfil: *Enunciado*, o objetivo numa frase curta; *Teste*, a
   condição verificável que só este objetivo produz — o que uma mudança precisa mostrar para
   aproximá-lo, como "adicionar uma marca muda só tokens" —, nunca "a mudança aproxima o projeto do
   objetivo". Origem `proposto`.
2. Os **princípios do método**, da tabela da norma. Origem `arquivo <plan_root>/system/modelo-dev-units.md`.
3. Em projeto em andamento, os **extraídos**: o que o projeto já afirma, com o arquivo citado e origem
   `arquivo <caminho>`. O que o `CLAUDE.md` ou o `.claude/CLAUDE.md` afirma já carrega: registre como
   `existente`, sem gravar.
4. Em projeto em andamento, os **propostos**: inferidos e ligados ao objetivo. Origem `proposto`.

Em projeto novo, só os passos 1 e 2: os demais nascem pelo huddle. Cada sugestão mostra a origem e o
teste aplicado — uma equipe competente, trabalhando neste projeto, pode rejeitá-lo? — e por que passou.
Se não passa, diga por que e leve-a à etapa 3 como guideline. Grave o aprovado com o JSON
`{nome, enunciado, teste}`, cada campo numa linha, para
`python3 "${CLAUDE_SKILL_DIR}/dc.py" criar-principio`, e registre com `tipo: princípio`, como na etapa 3.

**3 e 4 — Guidelines, depois guardrails.** Antes de sugerir, rode
`python3 "${CLAUDE_SKILL_DIR}/dc.py" setup-decididas`: o que já está lá não volta, e o que está em
`existentes` no `descobrir` se registra como `existente`. Todas as guidelines antes dos guardrails, uma
por vez, com três opções: **Aprovar**, **Editar** e **Rejeitar**.

- **Aprovar** grava e registra; **Rejeitar** registra, com o motivo se a pessoa der um.
- **Editar** abre uma segunda pergunta: **Edição livre** (a pessoa diz o que mudar, pelo texto livre, e
  você aplica; só ajuda a redigir se ela pedir) ou **Edição guiada** (perguntas uma por vez, cada uma com
  sugestões derivadas das anteriores, até escopo, regra e exceção estarem definidos). A versão editada
  volta com **Aprovar**, **Editar** ou **Rejeitar**.

Guideline nasce da stack e do objetivo do projeto, escopada pelos caminhos onde vale; o que o `CLAUDE.md`
ou um linter já impõe não vira guideline. Recurso do projeto ligado a caminhos — skill, command ou MCP
listado em *Recursos do projeto* no `descobrir` — vira **guideline-ponte**: `paths` onde ele vale, e corpo
que começa por um título e diz qual recurso usar, como `# Interface` e "Componente novo em
`src/components/` passa pela skill `ui-builder` do projeto". O título é o que o `derive` cita na unidade;
a origem é `arquivo <caminho do recurso>`.
Agent não entra em ponte: o `implement` roda em subagente, que não cria outro. Guardrail nasce de decisão explícita do time que desvia do
padrão da stack, e barra o que uma escrita contém, por regex — pergunte pelas decisões e procure-as no
inventário. Mostre a proposta inteira e grave só depois do **Aprovar**: guideline, o JSON
`{nome, descricao, paths, corpo}` para `python3 "${CLAUDE_SKILL_DIR}/dc.py" criar-guideline` (com
`aguardando: true` se o caminho ainda não existe), em `paths` como diz *Padrões de `paths`*; guardrail, o
JSON `{regra, proibido, permitido}` para `python3 "${CLAUDE_SKILL_DIR}/dc.py" adicionar-guardrail`, no
formato de *Formato do guardrail*. `python3 "${CLAUDE_SKILL_DIR}/dc.py" explicar camada-normativa` imprime
o que a norma diz da guideline. Cada resultado vai para `python3 "${CLAUDE_SKILL_DIR}/dc.py" setup-registrar`, com o JSON
`{chave, tipo, origem, resultado, detalhe}`. O `setup-registrar` aceita só um vocabulário fechado, e valor
fora dele sai `1`: `tipo` é `guideline`, `guardrail` ou `princípio`; `origem` é `stack`, `decisão do time`,
`existente`, `proposto` ou `arquivo <caminho>`; `resultado` é `aceita`, `rejeitada` ou `existente`.
Sugestão editada e depois aprovada é `aceita` — não existe `editada`.

**5 — Huddle.** Se o projeto ainda tem o arquivo único antigo, proponha
`python3 "${CLAUDE_SKILL_DIR}/dc.py" huddle-migrar` e rode-o com o sim; senão rode
`python3 "${CLAUDE_SKILL_DIR}/dc.py" huddle-iniciar`, ou apenas explique se o arquivo da pessoa já existe.
A partir do que `python3 "${CLAUDE_SKILL_DIR}/dc.py" explicar huddle` imprime, explique o que é o huddle,
o que dispara uma entrada, que cada pessoa tem o seu, que a pessoa e o Claude registram nele, o lembrete
semanal e como ajustar `reminder_days`, e que um item pode ser promovido a guideline ou guardrail.

**6 — O método.** Rode `python3 "${CLAUDE_SKILL_DIR}/dc.py" explicar` e explique Decode e Code a partir
do que ele imprime, sem texto próprio que possa divergir: Decode é pensar antes de construir (Clarificar,
Evitar, Reduzir, os gates A e B e o porte do plano); Code é o que o plugin faz hoje, com `derive`
decompondo e `implement` executando cada unidade em cold-start, e quem orquestra revisando a entrega
antes de versionar.

**7 — Concluir.** Rode `python3 "${CLAUDE_SKILL_DIR}/dc.py" setup-concluir`. Diga o que vai para o git:
`.claude/settings.json`, `.claude/rules/`, `.claude/guardrails.json`, o que o bootstrap criou em
`<plan_root>/`, o `setup.md` e o arquivo de huddle da pessoa. E diga o que é pessoal:
`.claude/settings.local.json` guarda as permissões que a pessoa concedeu e não vai para o git — o setup
não escreve no `.gitignore`, então cabe a ela. Depois, o fecho do huddle como nas outras skills:
`python3 "${CLAUDE_SKILL_DIR}/dc.py" huddle-fecho` imprime os gatilhos; o que ficou aberto entra por
`python3 "${CLAUDE_SKILL_DIR}/dc.py" huddle-abrir <tipo> --autor Claude`, com o texto no stdin, uma
chamada por entrada. A mensagem final passa por
`python3 "${CLAUDE_SKILL_DIR}/dc.py" huddle-lint-relatorio`, no stdin, e termina com
`entradas novas no huddle: N (H-XX, …)` — `0`, sem parênteses, quando não houve nada.

## Referência

### JSON pelo stdin, por arquivo

O Claude Code recusa heredoc com JSON ("Contains brace with quote character"). Para `setup-perfil`,
`setup-registrar`, `criar-principio`, `criar-guideline` e `adicionar-guardrail`, grave o JSON com a ferramenta `Write` num
arquivo temporário fora do projeto (o scratchpad da sessão) e passe-o com `<`, na forma que o
`allowed-tools` casa: `python3 "${CLAUDE_SKILL_DIR}/dc.py" setup-perfil < <arquivo>`. O `huddle-abrir`
lê texto, não JSON, e segue como nas outras skills.

### Padrões de `paths`

O `criar-guideline` recusa duas formas: arquivo da raiz pelo nome e chaves. Arquivo da raiz entra como
`**/<arquivo>` (`**/tailwind.config.ts`, não `tailwind.config.ts`), e cada extensão vai num padrão próprio
(`src/**/*.ts` e `src/**/*.tsx`, não `src/**/*.{ts,tsx}`).

### Formato do guardrail

O JSON do `adicionar-guardrail` é `{regra, proibido, permitido}`:

- `regra` tem quatro campos, todos texto não vazio: `nome` (kebab-case), `ferramenta` (regex sobre o nome
  da ferramenta, ex.: `^(Write|Edit)$`), `detector` (regex) e `mensagem`.
- O `detector` casa o texto dos valores de `tool_input` que são texto, unidos por quebra de linha: num
  `Write`, o caminho e o conteúdo; num `Edit`, o caminho e o trecho novo — o antigo fica de fora, para
  que o `Edit` que remove o problema passe. Não há campo de caminho: a restrição de pasta vai dentro do
  próprio regex.
- Para "na pasta X, nunca Y", o detector casa o caminho absoluto e o relativo e atravessa linhas:
  `(?s)(^|/)X/.*Y`. Prove os dois no par: um `proibido` com caminho relativo e o `permitido` fora de `X`.
- `proibido` e `permitido` têm a forma do payload do hook, `{tool_name, tool_input}`; o comando recusa a
  regra que não nega o `proibido` ou que nega o `permitido`.

### Tipos do huddle

`huddle-abrir` aceita `pergunta`, `divergência`, `padrão`, `revisitar` e `observação`; outro tipo
(`contorno`, por exemplo) sai `1`.

Composição via `dc.py` — ponto de entrada único, o que o `allowed-tools` libera; rode-o do diretório do
projeto. **Rode o comando exatamente como está escrito** — sem variável de shell, sem tirar as aspas e sem
trocar o caminho —, porque a liberação de permissão casa o texto do comando. Subcomandos: `bootstrap`,
`setup-escopo`, `setup-iniciar`, `descobrir`, `setup-perfil`, `setup-decididas`, `setup-registrar`,
`criar-principio`, `criar-guideline`, `adicionar-guardrail`, `huddle-migrar`, `huddle-iniciar`, `explicar`, `setup-concluir`,
`huddle-fecho`, `huddle-abrir` e `huddle-lint-relatorio`.
