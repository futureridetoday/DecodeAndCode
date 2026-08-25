---
# about
name: plan-size-field
type: unit
project: DecodeAndCode
description: O plano passa a declarar o porte e quem o aprovou, e a aprovação deixa de ser efeito colateral do derive — o gate recusa ausência, nunca julga o valor
tags: [decode-and-code, plano, porte, aprovacao, l-16]

# alvo
core: model
module: decode-and-code
block: ""
owner: model
unit_id: 0001-12
unit_type: dev

# verificação
state: verified
test: .claude/skills/decode-and-code/scripts/tests/test_porte_e_aprovacao.py
verified_at: 2026-08-25

# history
author: Bortoli
created: 2026-08-25
status: draft
version: 1.0.0
updated: ""

# system
scope: project
auto_load: false
dependencies: []
---

# 0001-12 — plan-size-field

**Responsabilidade:** dar ao plano os dois campos que só o humano pode preencher — o **porte** e o
**registro da aprovação** — e fazer `scaffold.aprovar` conferi-los antes de escrever qualquer coisa.
Hoje ele carimba `status: approved` sozinho, e nenhum arquivo distingue *o humano aprovou* de *o
derive rodou* (`L-16`).

## Contrato

| Campo | Detalhe |
|---|---|
| **Entrada** | `scaffold.aprovar(plano, dry_run=False)` — a mesma assinatura de hoje |
| **Saída** | O caminho final do plano, como hoje. Plano já aprovado continua devolvendo o próprio caminho sem escrever nada (`L-17`) |
| **Auth** | — |
| **Efeito** | Move o plano, registra a linha em `_planos.md` e grava `plan_id`. **Deixa de gravar `status: approved` por conta própria**: passa a projetá-lo a partir do que o humano declarou |
| **Erro** | `ValueError` nomeando o campo, antes de qualquer escrita — inclusive em `dry_run` |

**Os três campos que o plano passa a declarar,** todos no frontmatter e todos escritos pelo humano:

| Campo | Valor | O que o gate faz |
|---|---|---|
| `plan_size` | `pequeno` \| `médio` \| `grande` | Recusa ausente **e** recusa valor fora do vocabulário |
| `approved_by` | nome de quem aprovou | Recusa ausente |
| `approved_at` | `YYYY-MM-DD` | Recusa ausente, e recusa o que não for data ISO |

> **Recusar valor fora do vocabulário não é julgar o porte.** A norma proíbe teto de unidades por
> escrito, e o gate continua sem opinar se `grande` era a escolha certa para *este* plano — isso é
> julgamento e fica com o humano. O que ele recusa é `plan_size: enorme`, que não é escolha e sim
> erro de digitação, no mesmo padrão de `UNIT_TYPES_VALIDOS` em `lint_unidade.py:37`. A unidade
> `0001-14` ramifica por esse valor: um valor desconhecido chegando lá teria que falhar de algum
> jeito, e falhar na aprovação é mais barato e mais cedo.

**A coluna *Aprovado* de `_planos.md` passa a receber `approved_at`,** não `date.today()`
(`scaffold.py:80`). É a correção direta da `L-16`: hoje a coluna registra quando o **script** rodou,
e o `D-15` existe porque essas duas datas divergiram sem que nada percebesse.

**O que esta unidade deliberadamente não faz:** preencher `approved_by` e `approved_at` no plano
`0001`. Ele foi ratificado pelo humano em 2026-08-24 (`D-15`) e os campos estão vazios — mas quem
executa esta unidade **não é** quem aprova, e escrever ali reproduziria exatamente o defeito que a
`L-16` descreve. O executor **reporta** que faltam, e o humano os escreve.

## Sequência

1. Estender `scaffold.aprovar` com a checagem de `plan_size`, reusando `_campo_vazio` e uma constante `PLAN_SIZES_VALIDOS` no padrão de `lint_unidade.UNIT_TYPES_VALIDOS`. Roda junto com a checagem de `core`, antes de qualquer escrita e antes do `dry_run` retornar.
2. Estender a mesma função com `approved_by` e `approved_at`; `_linha_planos_md` passa a receber `approved_at` no lugar de `date.today()`, e `escrever_campos` grava `status: approved` como projeção do que foi declarado, nunca como afirmação própria.
3. Escrever na norma, em *Formato do plano*, a subseção dos três campos declarados pelo humano; e em *Fluxo completo*, fazer a etapa 3 deixar registro — hoje ela é gate sem artefato nenhum.
4. Acrescentar os três campos a `fixtures._PLANO_TEMPLATE` e os parâmetros correspondentes a `fixtures.plano()`, com default válido, para que os testes existentes que constroem plano continuem construindo plano válido.
5. Escrever `tests/test_porte_e_aprovacao.py` cobrindo o critério de aceite, e conferir que os quatro arquivos de teste que já chamam `aprovar` continuam verdes — `test_config.py`, `test_lint_unidade.py`, `test_scaffold.py` e `test_scaffold_idempotente.py`.
6. Rodar o gate e relatar, incluindo a lista dos campos que faltam no plano `0001` — sem preenchê-los.

## Arquivos

| Caminho | O que muda |
|---|---|
| `.claude/skills/decode-and-code/scripts/scaffold.py` | `PLAN_SIZES_VALIDOS`, as três checagens em `aprovar`, e `_linha_planos_md` lendo `approved_at` |
| `docs/plan/system/modelo-dev-units.md` | *Formato do plano* ganha os campos declarados; *Fluxo completo* ganha o registro da etapa 3 |
| `.claude/skills/decode-and-code/scripts/tests/fixtures.py` | `_PLANO_TEMPLATE` e `plano()` carregam os três campos |
| `.claude/skills/decode-and-code/scripts/tests/test_porte_e_aprovacao.py` | **novo** — o teste declarado |

## Dependências

Nenhuma unidade anterior. Depende do mecanismo que a `0001-06` formalizou — `aprovar` idempotente —,
porque a guarda de plano já aprovado precisa continuar retornando **antes** das checagens novas: um
plano aprovado sob o formato antigo não pode passar a falhar por campo que não existia quando ele
entrou.

## Normas aplicáveis

| Norma | Onde |
|---|---|
| *Formato do plano* e *Fluxo completo*, etapas 3 e 4 | [`modelo-dev-units.md`](../../system/modelo-dev-units.md) |
| `L-16` — a etapa 3 não deixa registro, e o `derive` a carimba sozinho | [`0001-decode-and-code-foundation.md`](0001-decode-and-code-foundation.md), seção *Lacunas* |
| `D-15` — a ratificação de 2026-08-24, e por que a data da coluna continua sendo a do script | [`0001-decode-and-code-foundation.md`](0001-decode-and-code-foundation.md), seção *Decisões* |
| `D-18` — por que o gate recusa valor fora do vocabulário | [`0001-decode-and-code-foundation.md`](0001-decode-and-code-foundation.md), seção *Decisões* |
| Vocabulário fechado validado por constante | `.claude/skills/decode-and-code/scripts/lint_unidade.py:37` |

## Critério de aceite

`scaffold.aprovar` levanta `ValueError` nomeando o campo, **sem escrever nada**, para cada um destes
casos isoladamente: `plan_size` ausente, `plan_size: ""`, `plan_size` fora do vocabulário,
`approved_by` ausente, `approved_at` ausente, e `approved_at` que não é data ISO. O teste confere a
ausência de escrita em disco, não só a exceção — é o mesmo cuidado que a checagem de `core` já tem.

Plano com os três campos válidos é aprovado, e a linha em `_planos.md` traz na coluna *Aprovado* o
valor de `approved_at` — **não** a data em que o teste rodou. O teste prova isso com uma data
declarada que não é a de hoje.

Plano **já aprovado** — `plan_id` preenchido e fora do `_inbox` — continua devolvendo o próprio
caminho sem escrever nada, **mesmo sem os campos novos**. É o caso do plano `0001`, e é o que impede
a unidade de quebrar o repositório em que ela roda.

**A suíte inteira continua verde**, incluindo os quatro arquivos que já chamam `aprovar`.

## Verificação

```
./scripts/test-python.sh .claude/skills/decode-and-code/scripts/tests/test_porte_e_aprovacao.py
```

## Fonte

- [`0001-decode-and-code-foundation.md`](0001-decode-and-code-foundation.md), *Escopo* → *Fase 4*
- `L-16`, e a `D-15` que a originou
- `scaffold.py:80` e `scaffold.py:111` — a data de hoje na coluna e o carimbo de `status`
