---
# ── claude code — campos nativos ──────────────────────────────────────────────
name: derive
description: |
  Deriva a estrutura e as unidades de um plano já aprovado — cria a estrutura do alvo, move o plano do _inbox, gera um arquivo por unidade e projeta o backlog.

  Use when o usuário pede, de forma explícita, para derivar um plano já aprovado.

  <example>
  Context: plano aprovado, ainda sem estrutura nem unidades
  user: "derive o plano docs/plan/_inbox/catalogo.md"
  commentary: modo derive — cria a estrutura do alvo, move o plano do _inbox, gera um arquivo por unidade e projeta o backlog
  </example>

disable-model-invocation: true
user-invocable: true

allowed-tools: "Read Write Edit Bash Glob Grep"

argument-hint: "<plano>"
arguments: [target]

model: opus
effort: ""
context: ""
shell: bash

# ── amflow — rastreabilidade ───────────────────────────────────────────────────
type: skill
project: DecodeAndCode
author: Bortoli
created: 2026-10-15
status: draft
version: 1.0.0
updated: "2026-10-15"
scope: project
auto_load: false
tags: [decode-and-code, skill, plano, unidade, derive]
dependencies: []

hub_id: ""
source: local
---

# derive

> Invocação só explícita (`disable-model-invocation: true`): um `derive` disparado por engano cria estrutura e move arquivos.

Esta skill executa o modo `derive` da norma `<plan_root>/system/modelo-dev-units.md` — `plan_root` resolvido pelo `config.json` em `${CLAUDE_SKILL_DIR}/../decode-and-code/`. Todo determinismo (gates, contagem, projeção de estado) fica nos scripts em `${CLAUDE_SKILL_DIR}/../decode-and-code/scripts/` (norma, seção *Fronteira skill / script*); a skill cuida do que exige julgamento.

## Argumentos

- `$target` — caminho do plano aprovado a derivar

## Instruções

### `derive <plano>`

A Sequência é a da norma (*Fluxo completo*, etapas 4 a 7) — esta seção descreve só o **como**, para não duplicar o que já está lá.

1. **Aprovar** — `scaffold.aprovar(plano)` valida `core`, atribui o número do plano, valida o nome, move o arquivo do `_inbox` (compondo `move-md.py`) e registra a linha em `_planos.md`. Qualquer validação que falhar impede toda escrita.
2. **Ler o escopo** — a tabela `## Escopo` do plano já movido: uma linha por unidade prevista, com número e responsabilidade.
3. **Decidir a fatia** — para cada unidade, o contrato, a sequência e os arquivos que ela toca. **É aqui que está o julgamento**, e por isso o modo pede Opus, nunca Sonnet.
4. **Numerar e escrever** — `numeracao.proxima_unidade(dir_plano)` dá o próximo `nn`; cada arquivo carrega todos os blocos do corpo (norma, *Formato do arquivo de unidade*) e declara `test:` mesmo antes de o arquivo existir (decisão 15).
5. **Lint antes de seguir** — `lint_unidade.lint(arquivo)` em cada unidade recém-escrita; qualquer problema apontado é corrigido ali, antes de passar para a próxima.
6. **Projetar o backlog** — `backlog.projetar(dir_plano)`, que atualiza também a situação da linha em `_planos.md`.
7. **Gravar o handoff** — `handoff.gerar(dir_plano, fila=…, pendencias=…, sugestao=…)` escreve `_handoff.md` no diretório do plano. **Só no grande.** O script mede o que não pede opinião — commit, derivadas, verificadas, próximo número livre — e os três argumentos são **julgamento seu**: a ordem das unidades com suas dependências, o que ficou pendente do humano, e por onde você começaria.
8. **Registrar e relatar** — decisões tomadas durante a derivação vão para uma seção própria do plano, nunca para a norma; lacunas novas entram como `L-XX`, sem tentar resolvê-las; o que ficou pendente é reportado ao humano. **E dizer o que fazer com o handoff:** ele é para uma **sessão nova**, colado inteiro, e quem o receber orquestra a execução — não implementa unidade.

> **O handoff é projeção, não documento.** Cada `derive` incremental o regera com os números
> daquele instante, e edição à mão se perde na próxima execução. O prefixo `_` o mantém fora do
> padrão `NN-*.md` que conta unidades.

> **O lint roda antes de entregar** (passo 5). Sem isso, o `derive` produz unidades que o gate de entrada do `implement` recusa depois, e o retrabalho só aparece na próxima sessão.

> **Os passos 2 a 6 valem só para o grande** (norma, *Fluxo completo* e *O que cada porte carrega*, unidade 0001-14). **No pequeno, esta sequência não roda** — o passo 1 (`aprovar`) move o plano direto para `<core>/<NNNN>-<nome>.md`, sem subpasta, e para aí: sem `## Escopo`, sem unidade para decidir, numerar ou lintar. `backlog.projetar` ainda roda sobre esse arquivo, mas não escreve região nenhuma — só projeta a situação a partir de `status`, escrito pelo humano (fecha quando ele grava `status: done`). **No médio**, `aprovar` também move sem subpasta e os passos 2 a 5 seguem sem rodar — médio não deriva unidade —, mas o passo 6 projeta as caixas de `## Tarefas` em vez do backlog de unidades.

Composição via `python3` (mesmo import dos testes, `sys.path` até `${CLAUDE_SKILL_DIR}/../decode-and-code/scripts`): `${CLAUDE_SKILL_DIR}/../decode-and-code/scripts/scaffold.py`, `${CLAUDE_SKILL_DIR}/../decode-and-code/scripts/numeracao.py`, `${CLAUDE_SKILL_DIR}/../decode-and-code/scripts/lint_unidade.py`, `${CLAUDE_SKILL_DIR}/../decode-and-code/scripts/backlog.py` e `${CLAUDE_SKILL_DIR}/../decode-and-code/scripts/handoff.py`.

## Referências

- Norma: `<plan_root>/system/modelo-dev-units.md` — `plan_root` é o do `config.json`, e
  `docs/plan` é só o default. Vive no projeto que usa a skill, e é lá que a skill a lê.
