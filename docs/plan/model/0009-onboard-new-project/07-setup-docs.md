---
# about
name: setup-docs
type: unit
project: DecodeAndCode
description: A documentação do setup — a seção Setup na norma, as contagens de skills, as seções que o explicar imprime sem as marcas deste repositório, o Como começar do README, o No primeiro uso dos guias e o B-06
tags: [decode-and-code, setup, documentacao, norma]

# alvo
core: model
module: onboard-new-project
block: ""
owner: model
unit_id: 0009-07
unit_type: norma
approved_by: ""
approved_at: ""

# verificação
state: spec
test: ""
verified_at: ""

# history
author: Claude
created: 2026-11-15
status: draft
version: 1.0.0
updated: ""

# system
scope: project
auto_load: false
dependencies: []
---

# 0009-07 — setup-docs

**Responsabilidade:** fazer a documentação dizer o que o método passou a fazer no primeiro uso, e
tirar das seções que o `dc.py explicar` mostra a quem instala o que só faz sentido neste repositório.

## Contrato

| Campo | Detalhe |
|---|---|
| **Entrada** | O que as unidades `0009-01` a `0009-06` entregaram |
| **Saída** | Markdown normativo e de uso, nos arquivos da tabela *Arquivos* |
| **Auth** | — |
| **Efeito** | Só texto. Nenhum código muda |
| **Erro** | — |

**O que entra:**

| Onde | O quê |
|---|---|
| Norma, nova seção *Setup — o primeiro uso*, entre *Bootstrap* e *Fluxo completo* | O aviso, a skill, as etapas, o `setup.md` e o que o setup escreve e não escreve. Referencia o plano para o detalhe do fluxo |
| Norma, *Empacotamento* e *Camada de execução* | Seis skills, com o `setup` |
| Norma, *O que cada porte carrega* | Sem a menção ao `B-01`, que é backlog deste repositório |
| Norma, título *Skills `review-plan`, `derive` e `implement` — substituem `plan-dev-units`* | Sem o "— substituem `plan-dev-units`". A busca por prefixo da `0009-04` continua resolvendo; `lint-unidade` sobre as unidades que citam o título confirma |
| README, *Como começar* | O passo de instalar no escopo do projeto e o setup como primeira coisa a fazer |
| `docs/recursos/create-guideline.md` e `create-guardrail.md` | Parágrafo *No primeiro uso*: guideline nasce da stack e do objetivo; guardrail, de decisão explícita do time (`D-03`) |
| `docs/recursos/setup.md` | **novo** — o guia da skill, no formato de `docs/recursos/huddle.md` |
| `.claude/CLAUDE.md`, *Arquitetura* e *Recursos Instalados* | Seis skills; a linha da skill `setup` |
| `docs/plan/_inbox/_backlog.md` | O `B-06` vai de *Solução planejada* para *Problemas resolvidos* quando o plano fechar, com a data |

## Sequência

1. Escrever a seção *Setup — o primeiro uso* na norma.
2. Corrigir as contagens de skills e as duas marcas deste repositório nas seções que o `explicar` imprime.
3. Rodar `dc.py explicar` e `dc.py lint-unidade` sobre as unidades que citam o título da seção de skills.
4. README, guias, `docs/recursos/setup.md` e `.claude/CLAUDE.md`.
5. Rodar a suíte inteira e `git grep -n "quatro skills\|cinco skills"` para achar contagem que ficou para trás.
6. Entregar para aprovação humana: `approved_by` e `approved_at` desta unidade.

## Arquivos

| Caminho | O que muda |
|---|---|
| `docs/plan/system/modelo-dev-units.md` | seção nova, contagens e as duas marcas |
| `README.md` | *Como começar* |
| `docs/recursos/create-guideline.md` | *No primeiro uso* |
| `docs/recursos/create-guardrail.md` | *No primeiro uso* |
| `docs/recursos/setup.md` | **novo** |
| `.claude/CLAUDE.md` | *Arquitetura* e *Recursos Instalados* |
| `docs/plan/_inbox/_backlog.md` | `B-06`, no fechamento do plano |

## Dependências

`0009-06`: a documentação descreve a skill como ela ficou.

## Normas aplicáveis

| Norma | Onde |
|---|---|
| O que a unidade 07 entrega | [`0009-onboard-new-project.md`](0009-onboard-new-project.md), seção *Escopo* |
| O critério de sugestão no primeiro uso | [`0009-onboard-new-project.md`](0009-onboard-new-project.md), seção *Decisões* |
| Unidade que entrega prosa | [`modelo-dev-units.md`](../../system/modelo-dev-units.md), seção *Tipo de unidade* |

## Critério de aceite

A norma tem a seção *Setup — o primeiro uso* e conta seis skills; `dc.py explicar` imprime as quatro
seções sem `B-01` e sem `plan-dev-units`; nenhuma contagem antiga de skills sobra no repositório; a
suíte inteira continua verde; e o humano grava `approved_by` e `approved_at`.

## Verificação

```
python3 .claude/skills/derive/dc.py lint-unidade docs/plan/model/0009-onboard-new-project/07-setup-docs.md
```

## Fonte

- [`0009-onboard-new-project.md`](0009-onboard-new-project.md), *Escopo* → *Fase 3*, unidade 07
