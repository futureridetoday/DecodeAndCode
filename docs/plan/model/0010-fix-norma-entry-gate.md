---
# about
name: fix-norma-entry-gate
type: plan
project: DecodeAndCode
description: A `implement` recusa toda unidade `unit_type: norma` no gate de entrada, porque o `lint_unidade` exige a aprovação que o humano só declara depois da entrega — a exigência sai do lint e fica só no gate de saída
tags: [decode-and-code, implement, norma, gate, lint]

# alvo
plan_id: "0010"
plan_size: pequeno
core: model
module: fix-norma-entry-gate
block: ""

# history
author: Claude
created: 2026-11-17
status: approved
version: 1.0.0
updated: ""
approved_by: Bortoli
approved_at: 2026-11-17

# system
scope: project
auto_load: false
dependencies: []
---

# O gate de entrada para de exigir a aprovação da `norma`

## Objetivo

**Medido no AmFlow, plano `0028-decouple-resource-transport`, com o plugin 2.0.0:** o
`dc.py lint-unidade` reprova as três unidades `norma` recém-derivadas — `rc=1`, com duas linhas só:
`unit_type 'norma' exige 'approved_by' preenchido` e o mesmo para `approved_at`. As oito unidades
`dev` do mesmo plano passam. Como o passo 1 da `implement` é esse lint, e *"qualquer problema recusa
e encerra sem escrever nada"*, nenhuma unidade `norma` consegue começar.

A causa é um lint com dois papéis. `lint_unidade.lint` é o gate de **entrada** — da `implement` e do
passo 5 do `derive` — e é também metade do gate de **saída** da `norma`
(`verificacao._verificar_norma`). A norma diz que `approved_by`/`approved_at` são preenchidos pelo
humano **depois** de revisar a entrega
([`modelo-dev-units.md`](../system/modelo-dev-units.md), *`norma` — quando a unidade entrega prosa*).
Exigidos no lint, a unidade só passaria na entrada depois de entregue.

## Solução

**Subtração:** a checagem de aprovação sai de `lint_unidade.lint` e passa a `verificacao`, que é o
único lugar onde ela é oráculo. Nenhum modo novo, nenhum flag: o lint volta a conferir só estrutura —
o que vale para os três tipos —, e `_verificar_norma` fecha `verified` com lint limpo **e** os dois
campos preenchidos, com o campo que falta na saída quando não fecha. `verified_at` continua copiando
`approved_at`.

Descartado: um modo `--entrada` no `lint-unidade`. Manteria no lint uma exigência que nenhum chamador
de entrada quer, e o `derive` precisaria passar o mesmo flag — dois chamadores para o mesmo desvio.

**Detalhe do mesmo caminho — o argumento da `implement`.** `lint-unidade`, `normas` e `verificar`
recebem caminho; com o id (`0028-01`) caem em `FileNotFoundError`, e a `implement` documentava
`<unidade>` como "identificador". Entra aqui só como texto: a `SKILL.md` diz que o `$target` pode ser
caminho ou `unit_id`, e que o id se resolve para o caminho com Glob antes do passo 1. Resolver id em
script seria código para um caso que a skill já resolve com a ferramenta que tem.

Toca: `lint_unidade.py`, `verificacao.py`, `implement/SKILL.md`, a norma (*`norma` — quando a
unidade entrega prosa*), e os testes `test_lint_plano.py`, `test_dc.py` e o docstring de
`fixtures.unidade`.

## Oráculo

`tests/test_lint_plano.py`:

- `test_norma_recem_derivada_sem_aprovacao_aprova_no_gate_de_entrada` — `lint_unidade.lint` de uma
  `norma` sem `approved_by`/`approved_at` devolve `[]`. **Falha contra o código anterior** (medido:
  1 falha em 140, só este caso).
- `test_cada_campo_de_aprovacao_ausente_fecha_spec_e_aparece_na_saida` — sem qualquer um dos dois,
  `verificar` fecha `spec`, sem `subprocess`, e nomeia o campo na saída.

`tests/test_dc.py`: `test_norma_sem_aprovacao_devolve_o_que_falta`; e
`test_norma_devolve_os_problemas_do_lint` passa a usar um problema de lint real (`test:` preenchido),
já que a aprovação deixou de ser um.

Critério de saída: suíte inteira verde.

## Fonte

- Medição no AmFlow, plano `0028`, plugin 2.0.0 — relatada pela sessão que orquestra aquele plano
- [`modelo-dev-units.md`](../system/modelo-dev-units.md), *Tipo de unidade*, *`norma` — quando a
  unidade entrega prosa* e *Os dois gates*
- `0001-13` — a unidade que introduziu `unit_type: norma` e pôs a aprovação no lint
