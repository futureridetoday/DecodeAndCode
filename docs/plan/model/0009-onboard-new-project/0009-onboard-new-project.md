---
# about
name: onboard-new-project
type: plan
project: DecodeAndCode
description: O primeiro uso do plugin num projeto vira um setup guiado — põe o plugin no escopo do projeto, entende objetivo e stack, sugere guidelines e guardrails uma por vez com aprovar, editar ou rejeitar, grava pelos comandos, inicia o huddle da pessoa e explica o método
tags: [decode-and-code, onboarding, setup, guideline, guardrail, huddle]

# alvo
plan_id: "0009"
plan_size: grande
core: model
module: onboard-new-project
block: ""

# history
author: Claude
created: 2026-11-10
status: done
version: 1.0.0
updated: "2026-11-15"
approved_by: Bortoli
approved_at: 2026-11-15

# system
scope: project
auto_load: false
dependencies: [add-norm-writers, wire-huddle-cycle]
---

# Setup guiado no primeiro uso do plugin

## Objetivo

**Clarificar.** Quem instala o plugin recebe o mecanismo, mas não a norma: `.claude/rules/` e
`guardrails.json` são do projeto, e hoje nada diz isso a ele — os guias de criação moram em `docs/`,
que não viaja no pacote, e são texto estático. E num time, cada pessoa pode ter o plugin num escopo
diferente, ou nenhum, e trabalhar com normas diferentes. Métrica de entrega: um projeto sai do setup
com o plugin no escopo do projeto, as guidelines e os guardrails aprovados gravados e passando nos
lints, e o huddle da pessoa criado — sem ninguém abrir um guia. Beneficiário: o time de um projeto
que adota o método.

**Evitar.**

| Alternativa | Por que não basta |
|---|---|
| Apontar os três guias no README | É o estado atual; o README e `docs/recursos/` não estão no pacote instalado |
| O `intake` fazer o setup | Roda em fork, e a ferramenta de perguntas não existe em subagente ([sub-agents](https://code.claude.com/docs/en/sub-agents)) |
| Copiar o survey do `new-project` do Builder | Criaria uma terceira cópia editável do mesmo texto, em repositório público diferente. O **padrão** das perguntas é reaproveitado, os arquivos não |

**Reduzir.** Uma skill na conversa principal que entende o projeto, conduz as sugestões e grava
pelos comandos do `add-norm-writers` e do `wire-huddle-cycle`; quatro funções determinísticas novas
(registro do setup, inventário, escopo do plugin, resumo do método); e um aviso ao abrir a sessão.

## Gates

| Gate | Resposta |
|---|---|
| **A — necessidade real** | **Parcial.** O vazio é medido: nada no pacote cria `rules/` ou `guardrails.json`. O `B-06` condicionava este trabalho ao primeiro onboarding real de terceiro, que ainda não aconteceu; o humano decidiu antecipá-lo (`D-10`). A métrica é de entrega, não de impacto observado (`L-01`) |
| **B — mínimo viável** | Cortado: sugerir princípio (`D-04`); editar `CLAUDE.md` ou `AGENTS.md` (`D-05`); corrigir o lint de `paths` (fica no `add-norm-writers`, `L-01` de lá); a seção *Como conversamos* no huddle (`D-12`); agentes especialistas e revisão por QA independente (`D-06`); descoberta por agente ou por hook `type: agent` |

## O fluxo

O pedido do humano, na ordem dele, com a etapa 0 que a plataforma exige.

**0 — Pré-condições.** A skill confirma que o setup é desejado agora. Sem `.claude/` e `docs/`, propõe
o `dc.py bootstrap` — sem ele, todo comando do método falha (`lib.py:36`, `lib.py:141-148`). Depois,
confere se o plugin está habilitado no `.claude/settings.json` do projeto; se não, propõe habilitar,
com o marketplace, para que quem clonar trabalhe com as mesmas normas (`D-09`).

**1 — Entender o projeto.** `dc.py descobrir` inventaria as fontes; a skill confirma com o humano
objetivo, escopo e stack, uma pergunta por vez, com sugestões tiradas do inventário e o "Outro" para
texto livre — o padrão do `new-project` do Builder. O perfil confirmado fica em `setup.md`.

**2 — Guidelines.** Cada sugestão é um padrão de como codar na stack identificada, para o objetivo
do projeto, escopado pelos caminhos onde vale. Exemplo: num design system com shadcn e Tailwind,
"variantes de componente com `cva`", "classes combinadas com `cn()`", "valores vindos dos tokens do
Tailwind". A rule carrega sempre que uma sessão, um plano ou um agente toca um arquivo do escopo. O
que o `CLAUDE.md` ou o `AGENTS.md` já carregam não é repetido; regra que um linter já impõe não vira
guideline. Guideline para um caminho que ainda não existe — `components/**/*.tsx` antes do primeiro
componente — é gravada já, com `paths_pending: true` (`D-08` do `add-norm-writers`), e passa a
carregar no primeiro arquivo criado ali (`D-13`).

**3 — Guardrails.** Cada sugestão protege uma decisão do time que desvia do padrão da stack.
Exemplo: o time separou cada componente do shadcn em dois arquivos, estilo e funcionamento; o
guardrail recusa escrever em `components/**` um arquivo de componente que contenha definição de
estilo. O guardrail barra o que **uma** escrita contém, por regex — não confere o conjunto de
arquivos (`D-11`). O detector recebe o caminho e o conteúdo da escrita juntos, separados por
quebra de linha (`guardrail.py:36-38`), então a restrição a `components/**` vive no próprio regex;
no exemplo, o par permitido é escrever o arquivo de estilo, que também contém `cva`. A skill
pergunta pelas decisões do time e também as procura no inventário.

Nas etapas 2 e 3, uma sugestão por vez, todas as guidelines antes dos guardrails:

| Opção | O que acontece |
|---|---|
| **Aprovar** | Grava pelo comando, registra como aceita e mostra a próxima |
| **Editar** | Segunda pergunta: **Edição livre** ou **Edição guiada** |
| **Rejeitar** | Registra como rejeitada, com motivo opcional, e mostra a próxima |

- **Edição livre:** a skill pede que o humano informe o que quer editar, pela linha de texto livre da
  própria pergunta, e aplica. Ajuda a redigir só se ele pedir.
- **Edição guiada:** perguntas uma por vez, cada uma com sugestões derivadas das anteriores, até
  escopo, regra e exceção estarem definidos — o padrão *Refinar* do `build-resource` do Builder.
  Apresenta a versão editada com **Aprovar**, **Editar** (o ciclo recomeça) ou **Rejeitar**.

**4 — Huddle.** `dc.py huddle-iniciar` cria o arquivo da pessoa. Se o projeto ainda tem o arquivo
único antigo, `<plan_root>/system/huddle.md`, a skill propõe `dc.py huddle-migrar` antes — sem isso,
o `huddle-abrir` do `wire-huddle-cycle` recusa registros. A skill explica o que é, o que
dispara uma entrada, que cada pessoa tem o seu, que os dois registram, o lembrete semanal e como
ajustar `reminder_days`, e que um item pode ser promovido a guideline ou guardrail.

**5 — O método.** `dc.py explicar` imprime, da norma, as seções que sustentam o princípio, e a skill
explica a partir delas, sem texto próprio que possa divergir:

- **Decode:** Clarificar → Evitar → Reduzir e os gates A e B — pensar antes de construir, e o porte
  do plano medido pelo tamanho do problema, para que um caractere errado não vire plano de vinte
  tarefas nem uma feature transversal vire lista solta.
- **Code:** o que o plugin faz hoje — `derive` decompõe e `implement` executa cada unidade em
  cold-start, sem o histórico da conversa, contra as normas que a unidade cita; quem orquestra
  revisa a entrega antes de versionar (`D-06`).

**6 — Concluir.** `dc.py setup-concluir` grava a data, e o aviso deixa de aparecer.

## Restrições da plataforma

Lidas na documentação oficial em 2026-11-10.

| Restrição | Consequência no desenho | Fonte |
|---|---|---|
| Não existe evento de instalação ou de habilitação de plugin | O gatilho é um aviso no `SessionStart` | [hooks](https://code.claude.com/docs/en/hooks) |
| Hook síncrono não abre o turno; o contexto entra antes do primeiro prompt. `asyncRewake` com saída 2 acorda o Claude mesmo ocioso, mas não há registro dele em `SessionStart` | O setup começa na primeira mensagem do usuário; `asyncRewake` é a alternativa a medir (`L-02`) | [hooks](https://code.claude.com/docs/en/hooks) |
| A ferramenta de perguntas não existe em subagente, e skill com `context: fork` roda em subagente | A skill `setup` roda na conversa principal | [sub-agents](https://code.claude.com/docs/en/sub-agents), [skills](https://code.claude.com/docs/en/skills) |
| De 2 a 4 opções por pergunta, mais o texto livre | Aprovar / Editar / Rejeitar numa pergunta; Livre / Guiada na seguinte | [user-input](https://code.claude.com/docs/en/agent-sdk/user-input) |
| Plugin não declara o próprio escopo. `--scope project` grava `enabledPlugins` no `.claude/settings.json`, que vai para o git, mas não baixa nada: cada pessoa instala uma vez por clone; exigir em toda máquina é da administração da organização | O setup grava a habilitação no projeto e explica o passo de cada colega (`D-09`, `L-07`) | [discover-plugins](https://code.claude.com/docs/en/discover-plugins), [plugins-reference](https://code.claude.com/docs/en/plugins-reference) |
| A pré-aprovação de `allowed-tools` vale no turno da skill | O fluxo inteiro corre pela ferramenta de perguntas, dentro do turno (`L-06`) | [skills](https://code.claude.com/docs/en/skills) |
| Decisão do `0001`: hook que escreve no projeto é efeito colateral silencioso | O aviso nunca escreve; toda escrita passa por aprovação na skill | `0001`, *Materializar não pode ser automático* |

## Escopo

As unidades seguem a ordem de dependência. A validação ponta a ponta não é unidade (seção própria).

### Fase 1 — Fundação determinística

| # | Unidade | Responsabilidade |
|---|---|---|
| 01 | `setup-record` | `setup.py` e os subcomandos planos `setup-iniciar`, `setup-perfil`, `setup-registrar`, `setup-decididas`, `setup-concluir` e `setup-lint` (`D-06` do `add-norm-writers`), sobre `<plan_root>/system/setup.md`, com esqueleto em `_CONTEUDO_INICIAL`: `completed_at` no frontmatter, `## Perfil` (objetivo, escopo, stack, como o humano confirmou) e `## Decisões`, tabela `chave \| tipo \| origem \| resultado \| destino ou motivo \| data`. `tipo` ∈ {guideline, guardrail, princípio}; `origem` ∈ {stack, decisão do time, arquivo `<caminho>`, existente}; `resultado` ∈ {aceita, rejeitada, existente}; `chave` é o slug da sugestão, dado pela skill. `decididas` lista as chaves já registradas. Entrada por stdin em JSON |
| 02 | `project-scan` | `descoberta.py` e `dc.py descobrir`: o inventário por uma tupla literal de globs — `CLAUDE.md`, `.claude/CLAUDE.md`, `CLAUDE.local.md`, `AGENTS.md`, `README*`, `CONTRIBUTING*`, `package.json`, `pyproject.toml` (texto bruto), `tsconfig.json`, `components.json`, `tailwind.config.*`, configs de ESLint, Prettier, Biome e Ruff, `.editorconfig`, `.pre-commit-config.yaml`, `.github/workflows/*.yml`, `.gitlab-ci.yml`, `.cursor/rules/**`, `.cursorrules`, `.windsurfrules`, `.clinerules` — com caminho e as primeiras 60 linhas; e, à parte, as rules, os princípios e as regras de `guardrails.json` que já existem. Não classifica |
| 03 | `project-scope` | `dc.py setup-escopo`: lê o `.claude/settings.json` do projeto e, se pedido, acrescenta `enabledPlugins` e `extraKnownMarketplaces` do plugin, preservando o resto do arquivo; idempotente; recusa JSON inválido sem tocar nele. O nome e a origem do marketplace vêm de uma chave nova `marketplace` no `config.json` do pacote — o pacote só leva `.claude-plugin/plugin.json`, e o `marketplace.json` fica na raiz do repositório, com `source: archive` —, o que exige a chave nos padrões de `lib.py:33-39`, porque chave desconhecida levanta erro (`lib.py:84-85`) (`D-14`) |
| 04 | `method-brief` | `dc.py explicar`: imprime, da norma resolvida como em `bootstrap._fonte_norma` (pacote primeiro), as seções *Antes do plano — fluxo de decodificação*, *O que cada porte carrega*, *Cold-start é o critério de suficiência da unidade* e *Skills `review-plan`, `derive` e `implement`*. O teste falha se alguma delas sumir |

### Fase 2 — Fluxo

| # | Unidade | Responsabilidade |
|---|---|---|
| 05 | `setup-notice` | O `session_start.py` do `wire-huddle-cycle` ganha o caso do setup, resolvido por `CLAUDE_PROJECT_DIR`: sem `setup.md` com `completed_at`, devolve `systemMessage` e `additionalContext` propondo o setup — inclusive com o plugin só no escopo de usuário, porque a primeira etapa é pô-lo no do projeto (`D-09`). Enquanto o setup não conclui, o aviso de huddle não aparece. Nunca escreve |
| 06 | `setup-skill` | Skill `setup`, linha da `TOPOLOGIA`: `modo: setup`, `model: opus`, `disable-model-invocation: false` — o modelo pode propor e iniciar depois de ver o aviso, e o primeiro passo é a confirmação —, sem `context`, `allowed-tools` igual a `ALLOWED_TOOLS`. Atalho `skills/setup/dc.py`; corpo cita a pasta de scripts compartilhada e nenhum nome de projeto. Conduz as etapas 0 a 6 de *O fluxo*. Em projeto que já tem rules, princípios ou guardrails, registra cada um como `existente` e segue só com o que é novo; com o arquivo de huddle da pessoa já presente, só explica; com o arquivo único antigo, propõe `huddle-migrar`. Achado com cara de princípio vira entrada `observação` no huddle da pessoa (`D-04`). Termina com o gate de fecho do huddle |

### Fase 3 — Documentação

| # | Unidade | Responsabilidade |
|---|---|---|
| 07 | `setup-docs` | Norma: seção *Setup — o primeiro uso* entre *Bootstrap* e *Fluxo completo*, e as contagens de skills em *Empacotamento* e *Camada de execução*; as seções que o `explicar` imprime perdem as marcas deste repositório — o `B-01` em *O que cada porte carrega* e o "— substituem `plan-dev-units`" do título da seção de skills (a busca por prefixo continua resolvendo quem cita o título curto); README: *Como começar*, com o passo de instalar no escopo do projeto; `create-guideline.md` e `create-guardrail.md` ganham *No primeiro uso* (`D-03`); `.claude/CLAUDE.md` e comentário de `lib.SKILLS`; `B-06` vai para *Solução planejada* na aprovação e para *Problemas resolvidos* no fechamento |

## Validação ponta a ponta

Não é unidade: sessão real é medição reportada, não gate automático (norma, *Ciclo instalado*). O
resultado fica registrado aqui.

- Pacote construído por `empacotar.construir` num diretório fora de qualquer repositório com
  `.claude/` e `docs/` — dentro do checkout, `lib.repo_root()` acharia este repositório (`L-03` do
  `0006`).
- Projeto de exemplo sem `.claude/` e sem `docs/`, com `package.json`, `components.json` do shadcn e
  `tailwind.config.ts`, e ainda sem `components/`. Medir: onde o aviso aparece; a etapa 0 roda o
  bootstrap e o escopo; as sugestões de guideline citam a stack; a guideline para
  `components/**/*.tsx` é gravada com `paths_pending` e carrega quando o primeiro componente é
  criado; um guardrail é gravado com o par proibido/permitido; a segunda sessão não traz aviso.
- Rodar o setup num projeto com o `huddle.md` antigo: a etapa 4 propõe `huddle-migrar`.
- Rodar o setup neste repositório: `scripts.md`, `principles.md` e `ddl-remoto` aparecem como
  existentes e não são sugeridos de novo.
- Ao fim, `git status` deste repositório sem mudança.

### Resultado — 2026-11-16 e 2026-11-17

Conduzida por `claude -p` (Claude Code 2.1.325, `claude-opus-5-5`), em turnos encadeados por
`--resume`, com o pacote construído por `empacotar.construir` fora de qualquer repositório e carregado
por `--plugin-dir`. Os logs em stream-json ficaram no scratchpad da sessão que orquestrou.

**Desvio do roteiro:** em `-p` não existe a ferramenta de perguntas, então a skill perguntou em texto
e cada resposta foi um turno novo. A permissão que a pessoa daria a cada pedido foi simulada com
`--allowedTools` (o atalho `dc.py` da skill), `--add-dir` (leitura do pacote) e
`--permission-mode acceptEdits` (escrita do componente), turno a turno.

| Medida | Resultado |
|---|---|
| Aviso de setup | Chega ao modelo como `additionalContext`; ele propõe `/decode-and-code:setup` e espera o sim. Onde o `systemMessage` aparece para a pessoa não se mede em `-p` (`L-04` segue aberta) |
| Início do setup | Não começa sozinho (`L-02` confirmada). Invocada pelo modelo, a skill pede permissão `Skill(...)`; digitada pela pessoa, roda |
| Etapa 0 | `bootstrap` e `setup-escopo --aplicar` propostos e rodados com o sim; `settings.json` com só as duas chaves |
| Etapa 1 | Uma pergunta por vez, com sugestões tiradas do inventário; perfil gravado e `setup-lint` aprovado |
| Guidelines citam a stack | Sim: par `*.styles.ts`/`*.tsx` com `cva`, `cn()`, `forwardRef`/`Slot`, e tokens do tema |
| `paths_pending` | As duas guidelines saíram com `paths_pending: true`. Numa sessão nova, ler `components/ui/button.tsx` carregou as duas rules no contexto sem abrir `.claude/`. A marca não sai sozinha (`L-05` do `0007`) |
| Editar → Edição livre | Aplicou a mudança, apontou a tensão que ela criou com o corpo e voltou com Aprovar/Editar/Rejeitar |
| Guardrail com o par | `cva-so-no-styles` gravado, provado pelo `adicionar-guardrail`; numa segunda sessão barrou o `button.tsx` com `cva` e deixou passar o par separado |
| Segunda sessão | Sem aviso de setup |
| `huddle.md` antigo | A etapa 4 propôs o `huddle-migrar`; o `git mv` funcionou e os lints aprovaram |
| Este repositório (num clone) | `scripts`, `principles` e `ddl-remoto` registrados como `existente` e não sugeridos de novo. O aviso apareceu duas vezes: o hook do repositório e o do pacote |
| `git status` daqui | Igual ao de antes da validação |
| Etapas 5 e 6 | `explicar`, `setup-concluir` e o fecho do huddle rodaram nos dois projetos; o modelo abriu entradas no huddle da pessoa sozinho |

**Achados que viram lacuna:** `L-15` (heredoc barrado), `L-16` (formato do guardrail fora do
pacote), `L-17` (a pré-aprovação não atravessa o turno, medida) e `L-18` (arquivo da raiz em
`paths`). Achados menores, sem lacuna: o modelo disse que o colega "recebe a oferta de instalação"
ao abrir o projeto, o que a doc não afirma (`L-07`); a skill não lista os tipos do huddle, e o
modelo tentou `contorno` antes de `observação`; no projeto com `.claude/` e `docs/` mas sem a norma,
a etapa 0 não propôs o `bootstrap`.

**Remedição depois da correção de `L-15` e `L-16`, 2026-11-17.** Pacote reconstruído (`verificar` e
`validar` limpos), projeto novo `api-mini` (FastAPI, sem `.claude/` nem `docs/`) e um turno só, com
todas as respostas no pedido e **sem nenhuma permissão simulada**. Medido: o JSON foi por arquivo e
`<` nas quatro chamadas, nenhum heredoc; o guardrail `rotas-sem-sqlalchemy` saiu certo na primeira
tentativa, com o par provado; as etapas 0 a 6 rodaram só com a pré-aprovação da skill. A única
recusa foi um `; echo "exit $?"` que o modelo acrescentou a um comando, fora do texto da skill.

**Sessão interativa com o plugin instalado, 2026-11-17.** O humano rodou o setup num projeto novo
(`teste-setup`: React, shadcn e Tailwind, sem `components/`) com o 2.3.1 instalado pelo marketplace,
na ferramenta de perguntas. Relato dele: tudo como planejado, sem erro. Conferido nos arquivos, com
o `dc.py` do plugin instalado: `setup-lint`, `huddle-lint`, `lint-guardrails` e o lint das duas
guidelines aprovam; o escopo está habilitado; as quatro decisões estão no vocabulário (uma guideline
aceita depois da edição guiada, uma aceita sem edição, um guardrail aceito e um rejeitado); as duas
guidelines têm `paths_pending`; o hook não avisa mais; e o guardrail `cva-fora-do-tsx`, avaliado por
`guardrail.decidir`, barra o `cva` no `.tsx` e libera o par separado. O relato não detalha onde o
`systemMessage` apareceu nem quantas permissões foram pedidas, então a `L-04` segue aberta e a
`L-17` não tem contagem; "sem erro" indica que nenhum pedido atrapalhou o fluxo.

## Independência

**Um plano, em três fases, e não três planos.** A Fase 2 compõe as funções da Fase 1, e a Fase 3
documenta a Fase 2. Entregar só a Fase 1 deixa funções testadas sem ninguém que as chame.

**Guidelines e guardrails não viram dois planos** por decisão do humano: um fluxo só, em sequência
(`D-08`). Separados, os dois passariam no teste de independência; a norma aceita não dividir quando
o plano registra o porquê (*O que a avaliação não faz*).

**Dependência de outros planos.** As etapas 2 e 3 usam os comandos do `add-norm-writers`; a 4 e a
unidade 05 usam o `wire-huddle-cycle`. **Este plano só se aprova depois que os dois estiverem
`concluído` em `_planos.md`**, rodando `dc.py concorrencia` de novo na aprovação — nenhum script lê
`dependencies:` do frontmatter (`L-08`).

## Oráculo

| Alvo | Como se sabe que funcionou |
|---|---|
| Registro | `setup-lint` aprova o arquivo depois de `setup-perfil`, `setup-registrar` e `setup-concluir`; `setup-decididas` devolve a chave logo depois de `setup-registrar`; valor fora do vocabulário é recusado |
| Inventário | Num `tempfile` com `.claude/CLAUDE.md`, `components.json` e uma rule existente, `descobrir` lista os dois primeiros como fonte e a rule como existente, e nada fora da tupla |
| Escopo | `setup-escopo` sobre um `settings.json` com outras chaves preserva todas e acrescenta só as do plugin, com o marketplace lido do `config.json`; segunda chamada não muda nada; JSON inválido fica intacto |
| Método | `explicar` imprime as quatro seções; removida uma delas da norma de teste, o teste falha |
| Aviso | Teste por subprocesso com `CLAUDE_PROJECT_DIR` num `tempfile`: sem `setup.md`, JSON com a proposta; com `completed_at`, saída vazia; com setup pendente e huddle atrasado, só o aviso de setup |
| Skill | `lint_skill` e `TOPOLOGIA` aprovam; `claude plugin validate --strict` limpo; o zip tem `skills/setup/SKILL.md` |
| Fluxo | *Validação ponta a ponta*, registrada neste plano |

## Decisões

| # | Decisão | Estado |
|---|---|---|
| D-01 | **Gatilho: aviso no `SessionStart` mais a skill na conversa principal.** Imposto pela plataforma (*Restrições*) | Decorre da documentação |
| D-02 | **O estado do setup fica em `<plan_root>/system/setup.md`, versionado** | Decidida pelo humano em 2026-11-10 |
| D-03 | **O critério de sugestão no primeiro uso: guideline nasce da stack e do objetivo do projeto; guardrail, de decisão explícita do time que desvia do padrão da stack.** Os guias pedem falha observada ou incidente, que projeto novo não tem; ganham o parágrafo *No primeiro uso* | Decidida pelo humano em 2026-11-10 |
| D-04 | **O setup não sugere princípio.** Princípio entra por plano com unidade de tipo `norma`; achado com essa cara vira entrada `observação` no huddle | Decidida pelo humano em 2026-11-15 |
| D-05 | **O setup só escreve no que o bootstrap cria, no `.claude/settings.json` (escopo), em `.claude/rules/`, no `guardrails.json`, no `setup.md` e no arquivo de huddle da pessoa.** Nunca no `CLAUDE.md` nem no `AGENTS.md`; o que eles carregam não se repete em guideline | Decidida pelo humano em 2026-11-15 |
| D-06 | **A explicação do Code descreve só o que existe.** Agentes especialistas e revisão por QA independente ficam para plano próprio | Decidida pelo humano em 2026-11-10 |
| D-07 | **A skill conversa e gera as rules no idioma do usuário**, como o `intake` já responde no idioma do pedido | Decidida pelo humano em 2026-11-15 |
| D-08 | **Todas as guidelines antes, depois todos os guardrails, uma sugestão por vez, num fluxo só** | Pedido do humano em 2026-11-10 |
| D-09 | **O plugin trabalha no escopo do projeto.** O setup propõe habilitá-lo no `.claude/settings.json` e o aviso aparece mesmo com o plugin só no escopo de usuário, para que todo o time use as mesmas guidelines e guardrails | Decidida pelo humano em 2026-11-10 |
| D-10 | **O `B-06` é antecipado**, sem esperar a primeira instalação de terceiro | Decidida pelo humano em 2026-11-10 |
| D-11 | **Guardrail barra o que uma escrita contém**, pelo mecanismo atual de regex; verificar o conjunto de arquivos seria mecanismo novo | Decidida pelo humano em 2026-11-10 |
| D-12 | **Sem *Como conversamos* no setup.** A norma define o arquivo de huddle com `## Abertas` e `## Fechadas`, nada autoritativo; um contrato de conversa ali contradiz isso | Decidida pelo humano em 2026-11-15 |
| D-13 | **Guideline para caminho que ainda não existe é gravada já**, com `paths_pending: true`, pelo mecanismo da `D-08` do `add-norm-writers` — o padrão vale desde o primeiro arquivo, que é o que o setup promete | Decidida pelo humano em 2026-11-15 |
| D-14 | **O marketplace que `setup-escopo` grava vem de uma chave `marketplace` no `config.json` do pacote**, porque o pacote não leva o `marketplace.json`. É identidade do próprio plugin, não instância de projeto | Decidida pelo humano em 2026-11-15 |

## Decisões da derivação

Tomadas no `derive` de 2026-11-15; a forma está nas unidades.

| # | Decisão | Por quê |
|---|---|---|
| DD-01 | **`setup-escopo` mora em `escopo.py`, não em `setup.py`** (`0009-03`) | `setup.py` guarda o registro; ler e escrever o `settings.json` é outro arquivo e outro erro. As duas unidades ficam sem arquivo de código em comum além do `dc.py` |
| DD-02 | **A chave `marketplace` do `config.json` leva também `plugin`** (`0009-03`) | `enabledPlugins` usa `plugin@marketplace`, e o nome do plugin não está em nenhum lugar que o `config.json` já tenha |
| DD-03 | **`normas.secoes(arquivo, nomes)` é a função do `explicar`** (`0009-04`) | `normas._buscar` já resolve seção por prefixo; a função nova só junta as quatro e levanta com as que faltam |
| DD-04 | **A `0009-07` é unidade `norma`** | Entrega só prosa; o oráculo é a aprovação humana, e o `lint-unidade` exige `approved_by` e `approved_at` antes do `implement` |
| DD-05 | **A checagem do setup vem antes de `huddle.usuario` no hook** (`0009-05`) | Projeto recém-aberto pode não ter `user.name`; o aviso de setup não pode depender do que o setup resolve |
| DD-06 | **`empacotar.verificar` tira do texto o `marketplace.source.repo` do `config.json` antes de procurar o nome do projeto** (`0009-03`, `L-13`) | Decidida pelo humano em 2026-11-16. É identidade do plugin, como o `plugin.json`, que o verificador já deixa de fora; o nome solto em qualquer outro lugar continua acusado. Gravar o `repo` em minúsculas passava só porque a comparação diferencia caixa: um clone numa pasta `decodeandcode` voltava a reprovar |

## Lacunas

| # | Lacuna | Por que fica registrada |
|---|---|---|
| L-01 | **O gate A está satisfeito só em parte** | A prova usa projeto de exemplo, não terceiro real; a métrica é de entrega. A antecipação é decisão humana (`D-10`) |
| L-02 | **O setup não começa sozinho** | Hook síncrono não abre o turno. `asyncRewake` acorda o Claude com saída 2, mas a doc não o mostra em `SessionStart` e trata a saída 2 como erro; medir na validação ponta a ponta antes de adotar |
| L-03 | **A pertinência da sugestão não tem oráculo** | O lint garante estrutura, nunca que a guideline sugerida era boa. Só a sessão real e o uso medem |
| L-04 | **Onde o `systemMessage` de `SessionStart` aparece não está na doc** | Mesma `L-02` do `wire-huddle-cycle` |
| L-05 | **Edição guiada sem teto de perguntas** | O pedido é "a quantidade necessária". O critério de parada — escopo, regra e exceção definidos — é julgamento, como o "dois exemplos claros" do `build-resource` |
| L-06 | **A pré-aprovação vale no turno da skill** | Se o humano sair da ferramenta de perguntas para mensagem livre, os comandos seguintes pedem permissão. Se responder à ferramenta conta como "next message" não está na doc |
| L-07 | **Escopo de projeto não instala nada nas outras máquinas** | Pela [doc](https://code.claude.com/docs/en/discover-plugins), commitar a habilitação "doesn't download it": cada colega instala uma vez por clone. Exigir em toda máquina é configuração da organização, fora do plugin. Se o Claude Code pede a instalação ao confiar na pasta não está na doc |
| L-08 | **`dependencies:` não é lido por script** | A espera pelos dois planos depende de quem aprova rodar `concorrencia` |
| L-09 | **Rule escopada em subagente** | A doc confirma para subagente customizado e para Explore e Plan; para skill em fork, não. "Qualquer agente" fica a medir |
| L-10 | **O aviso aparece em todo projeto aberto com o plugin no escopo de usuário** | Consequência de `D-09`, inclusive em repositórios que nunca vão adotar o método. Se incomodar, uma opção "não neste projeto" exige onde guardar a recusa sem escrever no repositório |
| L-11 | **Guideline com `paths_pending` pode ter o caminho errado sem que nada acuse** | Herdada da `L-05` do `add-norm-writers`: a sessão real da validação ponta a ponta mede o caso feliz, não o erro de digitação |
| L-12 | **O `### <caminho>` do `descobrir` colide com os títulos dos trechos** | Medido na revisão da `0009-02` neste repositório: o `README.md` traz `### Por comando`, que na saída parece uma fonte. A `0009-02` fixou o formato sem cerca em volta do trecho; quem lê é a skill da `0009-06`, e a validação ponta a ponta mede se ela confunde |
| L-13 | **A `0009-03` fixou um `repo` que o empacotador recusa** | Medido na primeira execução da `0009-03`: `empacotar.verificar` acusa o nome do diretório de origem em todo arquivo do pacote, e `config.json` e `lib.py` viajam nele. A unidade não listava `empacotar.py`; o executor gravou o `repo` em minúsculas (`H-12`). Corrigida pela `DD-06`, com a unidade refeita |
| L-14 | **A `0009-06` não dava à skill o vocabulário do `setup-registrar`** | Medido na revisão da primeira execução: o `SKILL.md` listava `editada` entre os resultados, e o `setup.py` recusa esse valor com saída `1`. A unidade também não dizia como registrar o achado com cara de princípio, nem o que fazer quando o `huddle-abrir` recusa por causa do arquivo único antigo. Corrigida na unidade, refeita |
| L-15 | **O heredoc que a skill `setup` manda usar é barrado pelo Claude Code** | Medido na validação ponta a ponta: `<<'FIM'` com JSON recusado por "Contains brace with quote character" em toda chamada que lê do stdin (perfil, registro, guideline, guardrail). O modelo contornou gravando o JSON num arquivo e passando por `<`, o que o `allowed-tools` casa. Corrigida na `0009-06`, refeita. O `huddle/SKILL.md` do `0008` tem o mesmo heredoc com JSON no `criar-guideline` da promoção, e fica fora deste plano |
| L-16 | **O formato da regra de guardrail não chega à skill** | Medido na validação: a skill manda à norma, *Camada normativa*, que não traz os campos; o `create-guardrail.md` fica em `docs/recursos/`, fora do pacote. O modelo errou duas vezes e só acertou lendo o `guardrail.py`, com permissão para ler fora do projeto. Corrigida na `0009-06`: o corpo traz os campos e o que o detector lê |
| L-17 | **A pré-aprovação do `allowed-tools` vale só no turno da invocação — medida** | Fecha a dúvida da `L-06`: na mensagem seguinte da pessoa, todo `dc.py` volta a pedir permissão. Com a ferramenta de perguntas o fluxo fica num turno só; em `-p` ou com resposta por texto livre, cada comando pede aprovação |
| L-18 | **Arquivo da raiz não entra em `paths` pelo nome** | Medido na validação: `criar-guideline` recusou `tailwind.config.ts`; a skill trocou por `**/tailwind.config.ts` com o sim da pessoa. É o lint de `paths` que este plano deixou de fora (`L-01` do `add-norm-writers`), agora com um caso real |

## Backlog

<!-- backlog:start -->
| Unidade | Título | Estado |
|---|---|---|
| [0009-01](01-setup-record.md) | setup-record | `verified` |
| [0009-02](02-project-scan.md) | project-scan | `verified` |
| [0009-03](03-project-scope.md) | project-scope | `verified` |
| [0009-04](04-method-brief.md) | method-brief | `verified` |
| [0009-05](05-setup-notice.md) | setup-notice | `verified` |
| [0009-06](06-setup-skill.md) | setup-skill | `verified` |
| [0009-07](07-setup-docs.md) | setup-docs | `verified` |

7 de 7 derivadas · 7 verificadas · atualizado em 2026-11-17
<!-- backlog:end -->

## Fonte

- [`modelo-dev-units.md`](../../system/modelo-dev-units.md) — seções *Camada normativa*, *Antes do
  plano — fluxo de decodificação*, *O que cada porte carrega*, *Bootstrap*, *Ciclo instalado*,
  *Avaliação de escopo* e *Huddle*
- [`_backlog.md`](../../_inbox/_backlog.md) — `B-06`, que este plano resolve
- [`add-norm-writers.md`](../0007-add-norm-writers.md) e [`wire-huddle-cycle.md`](../0008-wire-huddle-cycle.md) —
  os planos de que este depende
- [`0001-decode-and-code-foundation`](../0001-decode-and-code-foundation/0001-decode-and-code-foundation.md)
  — *Materializar não pode ser automático*
- [`0006-e2e-fixes`](../0006-e2e-fixes.md) — `L-03`, o pacote dentro do checkout
- [`create-guideline.md`](../../../recursos/create-guideline.md),
  [`create-guardrail.md`](../../../recursos/create-guardrail.md),
  [`create-principle.md`](../../../recursos/create-principle.md)
- Builder do AmFlow, `skills/build-resource/SKILL.md` (*Refinar*) e `commands/new-project.md` (uma
  pergunta por vez) — o padrão das perguntas, não o texto
- Documentação oficial do Claude Code, lida em 2026-11-10:
  [hooks](https://code.claude.com/docs/en/hooks),
  [skills](https://code.claude.com/docs/en/skills),
  [sub-agents](https://code.claude.com/docs/en/sub-agents),
  [memory](https://code.claude.com/docs/en/memory),
  [plugins-reference](https://code.claude.com/docs/en/plugins-reference),
  [discover-plugins](https://code.claude.com/docs/en/discover-plugins),
  [user-input](https://code.claude.com/docs/en/agent-sdk/user-input)
