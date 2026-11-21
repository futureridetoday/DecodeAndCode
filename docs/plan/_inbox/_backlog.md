---
# about
name: backlog
type: doc
project: DecodeAndCode
description: Onde problema, ideia e feature ficam registrados antes de virarem plano
tags: [backlog, decode-and-code, pre-plano]

# history
author: Bortoli
created: 2026-08-22
status: draft
version: 1.0.0
updated: 2026-09-03

# system
scope: project
auto_load: false
dependencies: []
---

# Backlog

Onde problema, ideia e feature ficam registrados **antes** de virarem plano.

O modelo começa no plano, e plano já é um compromisso: nome, alvo declarado, independência
argumentada, escopo em unidades. Muita coisa que vale registrar ainda não merece esse custo — ou
porque não está madura, ou porque ninguém decidiu se vai ser feita. Sem um lugar antes do plano,
essas coisas vivem em conversa e se perdem.

## O que isto não é

- **Não é plano.** Item daqui não tem `plan_id`, não recebe número, não entra em
  [`_planos.md`](../_planos.md) e não segue o formato de plano.
- **Não é projeção de script.** O arquivo é escrito à mão, inteiro. Em particular, **não usar os
  marcadores `<!-- backlog:start -->` / `<!-- backlog:end -->`** aqui: eles pertencem ao
  `backlog.py`, que projeta o backlog de *unidades* dentro do arquivo de um plano. Nome igual,
  mecanismo oposto — e o script sobrescreve o miolo sem perguntar.
- **Não é lista de tarefas.** Tarefa de execução vive na unidade, com contrato e critério de aceite.

## Problemas abertos

| # | Item | Tipo | Prioridade | Autor | Core | Data de inclusão | Onde vive |
|---|---|---|---|---|---|---|---|
| B-01 | **Checagem de consistência entre normas.** A doc do Claude Code afirma que instruções contraditórias fazem o modelo escolher arbitrariamente. Com `CLAUDE.md` + norma + princípios + N guidelines ativas, a superfície de contradição cresce e nada a mede. **Gatilho, e é mecânico:** escrever quando **duas rules ativas casarem o mesmo path** — condição observável, não impressão. A unidade `05` (`activation-notice`) já vê todo carregamento e é o detector natural, sem construir nada. É a `L-05` do plano em curso | problema | — | Claude | model | 2026-08-22 | `.claude/rules/` |
| B-02 | **Verificador de invariantes de guideline.** Nasce como instrução em markdown e sem oráculo. **Quando escrever:** na primeira divergência observada entre duas instalações, não numa data. É a exclusão declarada no *Escopo* do plano em curso | feature | — | Claude | model | 2026-08-22 | Guideline (Fase 3) |
| B-05 | **Auditar as tabelas `## Arquivos` contra o disco, distinguindo criado de removido.** Nenhum gate confere se o que uma unidade declarou tocar corresponde ao que existe: o gate de unidade roda o teste declarado, e `lint_unidade` só exige que a tabela tenha **algum** caminho concreto. As duas ocorrências medidas apontam para o mesmo buraco em direções opostas — a `L-29`, onde a `0001-15` declarou `fixtures.py` e **não o tocou**, e a auditoria de 2026-08-27, onde eu li a `0001-02` como defeituosa por declarar `test_deprecacao.py` que não existe em disco, quando a tabela dizia corretamente `**removido**`. **O invariante é de par, não de existência:** caminho marcado `novo` ou alterado existe; caminho marcado `removido` **não** existe; e o que a tabela não classifica não é verificável. Escrever quando houver terceira ocorrência, ou junto do plano que dividir a norma — não numa data. **Cuidado que a segunda ocorrência ensina:** auditoria montada na hora reprova artefato correto, então este item nasce com a exigência de um caso para cada um dos três estados | feature | — | Claude | model | 2026-08-27 | `lint_plano` / `lint_unidade` |
| B-03 | **Migrar as seis skills normativas restantes do AmFlow.** `hub-env`, `security-testing`, `data-architecture`, `data-privacy-lgpd`, `digital-twin-product` e `user-modeling` são norma com escopo, vestidas de skill. A unidade `06` migra **uma** — a `hub-front` — de propósito: migrar sete de uma vez é o over-engineering que o plano combate, e migrar uma **mede o custo real** da migração. Este item é o que sobra depois dessa medição | feature | — | Claude | model | 2026-08-22 | Guideline (Fase 3) |
| B-07 | **A premissa que tornou `planner` e `developer` agents, e não skill, contradiz a doc oficial atual — e o vocabulário de `lint_agente` ficou para trás.** **Skill:** a norma ([`modelo-dev-units.md`](../system/modelo-dev-units.md), *Modelos*) afirma *"A troca não é declarável na skill"*, verificado em 2026-07-19 **por inferência de uso** (as skills do projeto deixavam `model:` vazio), não pela doc. Relida em 2026-09-13, [skills](https://code.claude.com/docs/en/skills) lista no frontmatter `model` (*"Model to use when this skill is active"*), `effort`, `context` (*"Set to `fork` to run in a forked subagent context"*) e `agent` (*"Which subagent type to use when `context: fork` is set"*), e diz que *"Custom commands have been merged into skills"*. Duas ressalvas impedem a decisão de se inverter sozinha: sem `fork`, o override dura só o turno (*"The session model resumes when you send your next prompt"*); com `fork`, define o modelo do subagente. E `model` é **por skill, não por modo**, então trocar de modelo automaticamente numa skill de três modos exigiria separar os modos. **Agent:** [sub-agents](https://code.claude.com/docs/en/sub-agents) aceita em `model` *"`sonnet`, `opus`, `haiku`, `fable`, a full model ID such as `claude-opus-5`, or `inherit`"* e lista ainda `disallowedTools`, `permissionMode`, `maxTurns`, `mcpServers`, `hooks`, `memory`, `background`, `effort`, `isolation`, `initialPrompt` e `experimental`. `CAMPOS_NATIVOS` e `MODELOS_VALIDOS` foram **medidos em uso** (34 agentes, 2026-08-26, unidade `0001-19`), não restringidos por decisão. A única recusa deliberada é `memory` (`D-06`, `CAMPOS_RECUSADOS`). O próprio benchmark da `19` contou `effort` em 7 dos 34 agentes e o deixou fora; `haiku` entrou *"por completar a família"*, sem medição, e `fable` não entrou. Hoje o lint reprova `model: fable`, `model: claude-opus-5` e `effort: high`, e chama esses campos de *"não-nativo"*, o que a doc desmente. `permissionMode`, `mcpServers` e `hooks` ficam fora com razão, porque a doc os marca *"Ignored for plugin subagents"*. **De passagem:** a mesma página diz que `skills:` injeta *"The full skill content"*, carregamento que a norma registra como nunca medido. **Impacto:** a justificativa de agents em vez de skill pode não valer mais, e o lint recusa configuração válida. Revisar isso é decisão arquitetural: pede plano e aprovação, não edição direta da norma. **Quando escrever:** antes do próximo agent ou da próxima mudança em `planner`/`developer`, e com medição, porque doc não é observação: uma sessão que confirme que `model:` numa skill com `context: fork` de fato troca o modelo | problema | — | Claude | model | 2026-09-13 | `modelo-dev-units.md` (*Modelos*, *Agente — o que o lint exige*) + `lint_agente.py` |
| B-08 | **"Não neste projeto" para o aviso de setup.** Com o plugin no escopo de usuário, o aviso de `SessionStart` aparece em todo projeto aberto, inclusive nos que nunca vão adotar o método — consequência da `D-09` do [`0009`](../model/0009-onboard-new-project/0009-onboard-new-project.md), registrada lá como `L-10`. A ideia é a pessoa recusar o setup por projeto. **O que trava:** a recusa precisa ficar fora do repositório, porque o aviso nunca escreve no projeto (`0001`, *Materializar não pode ser automático*) e a `D-05` do `0009` limita onde o setup escreve. Nasceu como M8 do esboço `fix-setup-validation`, que o deixou de fora por ser desenho próprio. **Quando escrever:** quando alguém relatar o aviso como incômodo num projeto que não adota o método — até hoje, nenhum relato | feature | — | Claude | model | 2026-11-19 | `session_start.py` |

## Solução planejada

| # | Item | Tipo | Prioridade | Autor | Core | Data de inclusão | Onde vive | Plano |
|---|---|---|---|---|---|---|---|---|

## Problemas resolvidos

| # | Item | Tipo | Prioridade | Autor | Core | Data de inclusão | Onde vive | Plano | Data de conclusão |
|---|---|---|---|---|---|---|---|---|---|
| B-04 | **Isolar o `git` real de `scripts/move-md.py` nos testes.** Medido em 2026-08-25 com um shim de `git` no `PATH`: a suíte executava **16** `git ls-files --error-unmatch` de verdade, todas de [`move-md.py:196`](../../../scripts/move-md.py), que confere se a origem está versionada antes de usar `git mv`. Não quebrava nada e era pré-existente — o registro existiu porque foi essa suposição não conferida que tornou falsa a afirmação *"nenhum teste executa `git` de verdade"* da unidade `0001-15` (`L-28`). **Resolvido mockando `esta_versionado` nos quatro arquivos que movem plano** — `test_scaffold` (9), `test_derive_por_porte` (5), `test_config` (1) e `test_porte_e_aprovacao` (1). O mock devolve `False`, que é o que o git já respondia para arquivo em `tempfile`: nenhum comportamento muda, só a chamada some. **Remedido com o mesmo shim: 16 → 0**, e as 22 invocações que restam são as do `TestComandoContraGitReal`, deliberadas. **A primeira tentativa foi outra e falhou:** uma guarda em `esta_versionado` para não perguntar por caminho fora do `REPO_ROOT` não removeu nenhuma das 16 — os testes patcham `move_md.REPO_ROOT` para o próprio `tempfile`, então o caminho está *dentro* do repo do ponto de vista do script. Descartada | problema | — | Claude | model | 2026-08-25 | `scripts/move-md.py` | — (correção direta, fora de unidade) | 2026-08-25 |
| B-06 | **O primeiro uso do plugin direciona o instalador a configurar a própria norma.** O plugin carrega só o **mecanismo** — `.claude/rules/*` e `.claude/guardrails.json` são do projeto que instala e **não viajam** com ele (README, *O que viaja no plugin*). Hoje nada diz isso a quem instala: para descobrir que precisa escrever os próprios princípios, guidelines e guardrails, o instalador tem que achar a seção *Como usar* do README e os três guias [`create-principle.md`](../../recursos/create-principle.md) / [`create-guideline.md`](../../recursos/create-guideline.md) / [`create-guardrail.md`](../../recursos/create-guardrail.md) por conta própria. A ideia é o **primeiro uso** detectar a ausência de norma de projeto e apontar para os três guias — provável forma: hook de sessão que vê `.claude/rules/` sem guideline de projeto e `guardrails.json` sem regra, ou um comando `/decode-and-code:setup`. **Cuidado:** o hook `InstructionsLoaded` já anuncia norma e guidelines a cada carregamento — este item é *onboarding único*, não mais um anúncio recorrente. **Quando escrever:** junto do primeiro onboarding real de terceiro — a primeira instalação fora de `DecodeAndCode` e `AmFlow`. Até lá não há "primeiro uso" real para calibrar, e o único instalador (AmFlow) já passou sem ele | feature | — | Bortoli | model | 2026-09-03 | hook de sessão + `docs/recursos/create-*.md` | [0009-onboard-new-project](../model/0009-onboard-new-project/0009-onboard-new-project.md) | 2026-11-17 |
