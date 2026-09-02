---
# about
name: huddle-command
type: plan
project: DecodeAndCode
description: O huddle ganha um comando /decode-and-code:huddle que resolve a data do último huddle, roda git log desde ela e monta a pauta de quatro partes da conversa recorrente — sem escrever no arquivo
tags: [decode-and-code, huddle, comando, plugin]

# alvo
plan_id: ""
plan_size: médio
core: model
module: huddle-command
block: ""

# history
author: Bortoli
created: 2026-09-02
status: draft
version: 1.0.0
updated: ""
approved_by: ""
approved_at: ""

# system
scope: project
auto_load: false
dependencies: []
---

# O huddle ganha um comando que monta a pauta da conversa recorrente

## Objetivo

**Clarificar.** Quem conduz o huddle semanal monta a pauta à mão toda vez: abrir `huddle.md`,
descobrir desde quando olhar, rodar `git log`, e montar o resumo de quatro partes que o *Prompt de
continuidade* pede — o que mudou desde o último huddle, o que espera decisão, o que ficou por
fazer, por onde começar. Beneficiário: quem conduz o projeto. Custo: fricção recorrente e execução
inconsistente do ritual.

**Evitar.** O *Prompt de continuidade* já existe dentro do `huddle.md` — é template colável. O que
um comando adiciona sobre ele: descoberta (não achar nem copiar o prompt) e as partes mecânicas já
resolvidas (data do último huddle, `git log` desde ela). **Se a revisão concluir que isso não paga
um comando novo, o plano fecha sem execução** — resultado válido.

**Reduzir.** A menor versão que resolve 80%: um comando `/decode-and-code:huddle` que lê o
`huddle.md`, resolve a data do último huddle pela última linha de `## Fechadas`, roda `git log
--oneline` desde ela, e devolve o resumo de quatro partes. **Não toca em arquivo, não abre
entrada** — abertura continua no fecho dos três modos, como a norma manda.

## Solução

| Quem | O quê |
|---|---|
| **Script** (`huddle.py`) | A data do último huddle — última linha de `## Fechadas`, ou o `created` do frontmatter se nada fechou — e a lista bruta de commits desde ela via `git log --oneline` |
| **Comando / julgamento** | Montar as quatro partes a partir dessa matéria-prima: o que mudou, o que espera decisão (as `H-XX` de `## Abertas`), o que ficou por fazer, e onde começar; conduzir a conversa com as condições de `## Como conversamos` |

O comando é arquivo em `.claude/commands/huddle.md`, mesmo formato de `implement.md`/`delegate.md`,
e viaja no pacote pelo glob de `_copiar_comandos`. O helper novo em `huddle.py` roda `git` de
verdade em pelo menos um caso (guideline `scripts.md`, *Comando externo*).

## Tarefas

- [ ] `huddle.py` ganha `ultima_data(caminho) -> date` — última data de `## Fechadas`, ou `created`
      do frontmatter se nada fechou. Fixture das duas condições.
- [ ] `huddle.py` ganha `commits_desde(data) -> list[str]` — `git log --oneline --since`, com um
      caso contra `git` real num repo `tempfile` (caracterizar antes de corrigir).
- [ ] `.claude/commands/huddle.md` — frontmatter (`description`, `argument-hint: ""`,
      `allowed-tools: "Read Bash"`, `model`, rastreabilidade amflow) + corpo: compõe
      `ultima_data`/`commits_desde`, lê `## Abertas` e `## Como conversamos`, devolve o resumo de
      quatro partes.
- [ ] Empacotamento — conferir que os testes de árvore real e `claude plugin validate` seguem
      limpos com o comando novo; nenhum ajuste esperado nos testes de fixture sintética.
- [ ] Docs — linha na tabela `## Como usar` do README, `docs/recursos/huddle-command.md`, menção na
      seção `## Huddle`.
- [ ] Norma — uma linha na seção *Huddle* (subseção *Prompt de continuidade*) reconhecendo o
      comando, sem duplicar o formato.
- [ ] Versão — bump em `.claude/plugin.json` e `.claude-plugin/marketplace.json`, executado no
      release.

## Independência

O helper de `huddle.py` e o arquivo de comando são independentes na entrega: o helper tem teste
próprio (fixture + `git` real) sem o comando existir; o comando referencia o helper, mas seu
"teste" é `claude plugin validate` sobre o pacote. Doc e norma dependem dos dois prontos.

## Oráculo

| Alvo | Como se sabe que funcionou |
|---|---|
| `ultima_data` | fixture com `## Fechadas` populado devolve a última data; fixture sem nenhuma linha devolve `created` |
| `commits_desde` | caso contra `git` real num repo `tempfile` com commits datados devolve só os posteriores à data |
| Comando | `claude plugin validate` limpo sobre o pacote; `unzip -l` mostra `commands/huddle.md` |
| Fluxo | numa sessão real, `/decode-and-code:huddle` devolve as quatro partes com commits reais desde o último huddle |
| Norma | `test_normas_system` continua verde; a seção *Huddle* cita o comando uma vez |

## Decisões

| # | Decisão | Estado |
|---|---|---|
| D-01 | **O comando não escreve nada** | Abertura de entrada é no fecho dos três modos, por desenho (norma, *Momento*). Um comando que abrisse entrada sob demanda criaria entrada natimorta — o que a norma já rejeita |
| D-02 | **A "data do último huddle" sai de `## Fechadas`, não de marcador guardado** | Menos estado. A última linha fechada é o sinal mais próximo de "quando algo se resolveu pela última vez"; imperfeito quando um huddle acontece sem fechar nada, e o plano diz isso |

## Lacunas

| # | Lacuna | Por que fica registrada |
|---|---|---|
| L-01 | **Um comando sob demanda tensiona o "preenchido na sexta, com estado fresco"** | A norma (*Prompt de continuidade*) diz que o prompt se preenche no fecho do trabalho, não na retomada; o comando o monta na retomada. As duas coisas podem coexistir, mas a norma precisa dizer qual é o caminho recomendado. Decisão de aprovação |
| L-02 | **Não há medição de quantos huddles deixaram de acontecer pela fricção** | A justificativa é fricção observada, não taxa medida — o Gate A do fluxo de decodificação fica só parcialmente satisfeito. Base estreita, e vale dizer |
| L-03 | **`commits_desde` assume que o repo do huddle é o repo git** | Verdadeiro neste projeto; um projeto com `plan_root` fora do repo git veria lista vazia. Fora do escopo desta versão |

## Backlog

<!-- backlog:start -->
<!-- backlog:end -->

## Fonte

- [`huddle.md`](../system/huddle.md) — o arquivo, o *Prompt de continuidade*, `## Como conversamos`
- [`modelo-dev-units.md`](../system/modelo-dev-units.md), seção *Huddle* — formato, gatilhos,
  *Momento*, regra de despejo
- `.claude/commands/implement.md` e `.claude/commands/delegate.md` — formato de comando de
  referência
- `.claude/skills/decode-and-code/scripts/huddle.py` — `lint_arquivo`, `lint_relatorio`,
  `iniciar`; onde `ultima_data` e `commits_desde` entram
