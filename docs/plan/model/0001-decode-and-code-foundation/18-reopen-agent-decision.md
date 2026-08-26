---
# about
name: reopen-agent-decision
type: unit
project: DecodeAndCode
description: A norma registra que o próprio gate dela abriu — as duas condições que ela exigia para agent existir foram cumpridas, e a decisão 18 e a pendência 2 fecham com o registro de quando e por quê
tags: [decode-and-code, norma, agent, decisao, gate]

# alvo
core: model
module: decode-and-code
block: ""
owner: model
unit_id: 0001-18
unit_type: dev

# verificação
state: verified
test: .claude/skills/decode-and-code/scripts/tests/test_normas_system.py
verified_at: 2026-08-26

# history
author: Bortoli
created: 2026-08-26
status: draft
version: 1.0.0
updated: ""

# system
scope: project
auto_load: false
dependencies: []
---

# 0001-18 — reopen-agent-decision

**Responsabilidade:** tirar da norma a frase que proíbe agent, registrando **por que ela sai** — as
duas condições que a própria norma exigia foram cumpridas, e é isso que a `19` e a `20` precisam ter
por escrito antes de existirem.

## Contrato

| Campo | Detalhe |
|---|---|
| **Entrada** | Nenhuma — a unidade edita `modelo-dev-units.md` |
| **Saída** | Três pontos da norma reescritos: a seção *Modelos*, a decisão 18 e a pendência 2 |
| **Auth** | — |
| **Efeito** | Escrita em `docs/plan/system/modelo-dev-units.md` e no teste que a verifica |
| **Erro** | — |

**Os três pontos, e o que cada um passa a dizer:**

| Onde | Hoje | Passa a |
|---|---|---|
| *Modelos*, [`:897`](../../system/modelo-dev-units.md) | *"**Fora do escopo desta fase:** qualquer agent. Agent só se justifica onde há julgamento somado a pesquisa ampla, e só depois de a skill existir"* | registrar que **as duas condições foram cumpridas** — a skill existe desde 2026-07-26, e o requisito foi declarado pelo humano em 2026-08-22 a partir de uso diário — e dizer o que um agente é aqui: **papel e processo, nunca a norma** |
| Decisão 18, [`:983`](../../system/modelo-dev-units.md) | *"Não declarável em skill — política operacional; automatizar exigiria agent"* | ganhar linha de **revisão**, no mesmo padrão da decisão 32 sobre a 20: o que ela afirmou continua verdadeiro para a skill, e o que mudou é que o agent deixou de estar fora de escopo |
| Pendência 2, [`:1030`](../../system/modelo-dev-units.md) | *"Troca automática de modelo por modo... hoje fora de escopo"* | sair da lista de pendentes, com o destino nomeado — `model:` por agente, entregue pela `19` e pela `20` |

> **A ordem dentro da fase é o conteúdo da unidade, não organização.** Escrever unidade de agente
> enquanto a norma diz por escrito que agent está fora de escopo produziria duas fontes em
> contradição direta — e a doc do Claude Code registra que instruções contraditórias fazem o modelo
> *"pick one arbitrarily"*. Por isso esta unidade vem primeiro, e por isso ela é pequena.

**O que esta unidade não faz:** não escreve agente nenhum, não decide `model:` nem `tools:`, e não
reverte julgamento — o gate da norma tinha duas condições, e a unidade registra que ambas foram
cumpridas, com data e origem.

## Sequência

1. Reescrever o fecho da seção *Modelos* — as duas condições cumpridas, com data e origem de cada uma, e a forma que o agente adota aqui: papel e processo, com a norma continuando na norma.
2. Acrescentar a linha de revisão à decisão 18, preservando o que ela afirmou sobre a skill.
3. Retirar a pendência 2 da lista, nomeando onde a troca por modo passa a viver.
4. Escrever, em `tests/test_normas_system.py`, os casos que verificam os três pontos — cada um por conteúdo, nunca por contagem de linha.
5. Rodar o gate e relatar.

## Arquivos

| Caminho | O que muda |
|---|---|
| `docs/plan/system/modelo-dev-units.md` | seção *Modelos*, decisão 18 e a lista de pendentes |
| `.claude/skills/decode-and-code/scripts/tests/test_normas_system.py` | classe nova com os casos dos três pontos |

## Dependências

Nenhuma unidade. Depende da `D-05`, da `D-06` e da `D-07` do plano, que já decidiram a forma dos
agentes — esta unidade só abre o caminho normativo para elas.

## Normas aplicáveis

| Norma | Onde |
|---|---|
| O gate de agent e o seu desbloqueio, com as duas condições | [`modelo-dev-units.md`](../../system/modelo-dev-units.md), seção *Modelos* |
| Agente carrega papel e processo; a norma continua na norma | [`0001-decode-and-code-foundation.md`](0001-decode-and-code-foundation.md), *Agente: papel e processo, nunca a norma* |
| Uma fonte por fato | [`CLAUDE.md`](../../../../.claude/CLAUDE.md), invariante 1 |

## Critério de aceite

A norma **não contém mais** a frase que põe agent fora de escopo, e **contém** o registro das duas
condições cumpridas com as datas — skill desde 2026-07-26, requisito declarado em 2026-08-22. Um
caso do teste procura a frase antiga e falha se ela voltar; outro procura o registro novo.

A decisão 18 continua na tabela — decisão resolvida não se apaga — e carrega a linha de revisão. O
teste afirma as duas coisas: a linha existe, e ela cita a revisão.

A lista de pendentes **não contém** mais a troca automática de modelo por modo, e o destino está
nomeado no corpo. O teste procura pelos dois.

Cada um dos três pontos é um caso, verificado por **conteúdo**: nenhum caso compara número de linha,
que muda a cada edição da norma e transformaria o teste em falso alarme.

**A suíte inteira continua verde.**

## Verificação

```
./scripts/test-python.sh .claude/skills/decode-and-code/scripts/tests/test_normas_system.py
```

## Fonte

- [`0001-decode-and-code-foundation.md`](0001-decode-and-code-foundation.md), *Escopo* → *Fase 6*
- `D-24` — por que esta unidade é `dev` e não `norma`, e o que isso revela sobre o terceiro tipo
