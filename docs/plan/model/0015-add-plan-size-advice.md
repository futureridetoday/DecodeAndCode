---
# about
name: add-plan-size-advice
type: plan
project: DecodeAndCode
description: A revisão passa a recomendar o porte do plano, com o porquê, por um critério estrutural escrito numa seção só da norma — o que cada porte muda a jusante —, sempre como aviso e nunca como reprovação; o humano continua declarando plan_size na aprovação
tags: [decode-and-code, norma, review-plan, porte, plan_size]

# alvo
plan_id: "0015"
plan_size: pequeno
plan_type: norma
core: model
module: add-plan-size-advice
block: ""

# history
author: Claude
created: 2026-11-20
status: done
version: 1.0.0
updated: ""
approved_by: Bortoli
approved_at: 2026-11-20

# system
scope: project
auto_load: false
dependencies: []
---

# A revisão recomenda o porte

## Objetivo

**Clarificar.** O humano declara `plan_size` na aprovação sem receber uma recomendação
fundamentada: a norma define o que cada porte **carrega** (*O que cada porte carrega*), mas não
**quando** cada um cabe, e o passo 3 do `review-plan` só relata tamanho. Métrica: relatórios do
`review-plan` com uma linha de porte recomendado, o porquê e a evidência — hoje **zero**, a partir
deste plano **todos**. Beneficiário: o humano que aprova, que recebe a recomendação com o porquê
em vez de um porte escolhido "para o lint passar" (`L-04` do `0006`).

**Por que o critério não pode ser numérico** — medido em
[`porte-medido.md`](../system/porte-medido.md), 14 planos fechados:

| Porte | Unidades ou tarefas | Linhas alteradas |
|---|---|---|
| grande | 21, 6, 7 | 8740, 1426, 2113 |
| médio | 6, 9, 7, 7, 10, 8, 14 | `—` (não medido) |
| pequeno | `—` | `—` |

As contagens se sobrepõem: o `0013` (médio) fechou com 14 tarefas, o `0004` (grande) com 6
unidades. Contagem não separa os portes, e linhas só existem no grande. O `0008` é o caso
oposto: médio com cerca de 20 arquivos (`D-14`), executado numa sessão e fechado. O que separa os
portes é **estrutural** — o que cada um muda a jusante, já escrito na norma:

| Pergunta | Sim → | Onde a norma já diz isso |
|---|---|---|
| O trabalho é uma mudança só, sem passos que valha projetar? | `pequeno` | *O que cada porte carrega*: sem decomposição, sem backlog |
| Há passos, mas uma sessão os executa em sequência, sem cold-start? | `médio` | *Fluxo completo*: médio não deriva unidade, executa na sessão da aprovação |
| Alguma parte precisa de cold-start isolado — não cabe no contexto de uma sessão, ou precisa de teste próprio por unidade com gate de saída? | `grande` | *Fluxo completo*, etapas 6–8; *`_handoff.md`*: só o grande atravessa sessões |

**Evitar.**

| Alternativa | Por que não basta |
|---|---|
| Deixar só o *porte provável* de *Tipo de plano* | É por tipo, não por plano: `fix` e `remove` aceitam pequeno ou médio, `feature` médio ou grande — não decide entre os dois. E quem o usa é o `intake`; a revisão não o consulta |
| Limiar numérico (unidades, arquivos, linhas) | Os dados acima não o sustentam, e a norma já recusa: "um número sem base empírica competiria com o teste de independência" (*O que a avaliação não faz*) |
| Medir linhas no médio e no pequeno antes (estender `porte.registrar`) | Só alimentaria um limiar numérico, que o critério estrutural dispensa. Fica como lacuna (`L-01`), com gatilho |
| Subcomando no `dc.py` que calcula o porte | As três perguntas são julgamento sobre o conteúdo do plano; script daria número onde a norma pede leitura |
| Gate no `scaffold.aprovar` | A declaração é do humano, e o gate já diz que não julga o porte (*Aprovação*). Recusar tiraria do humano o que o pedido quer preservar |

**Reduzir.** Uma subseção nova na norma, duas linhas ajustadas nela, e o passo 3 do
`review-plan` reescrito. Nenhum código, nenhum teste novo, nenhum campo novo no frontmatter.

## Gates

| Gate | Resposta |
|---|---|
| **A — necessidade real** | **Sim, com base estreita, somada a exigência explícita do humano** (2026-11-20 — protocolo de exceção, *exigência explícita*). Medido: `L-04` do `0006` — o `intake` gravou `pequeno` para o lint passar e o humano descobriu na aprovação que outro porte exigia reestruturar o plano; `L-03` do `0012` deixou sem medição se o *porte provável* resolveu isso. **Não medido neste repositório:** `git log -p` sobre `_inbox/` e `model/` mostra **zero** trocas de `plan_size` entre esboço e aprovação nos 14 planos — a única troca é grafia (`medio` → `médio`, `a3b8481`). O caso de `L-04` é do teste ponta a ponta, não daqui |
| **B — mínimo viável** | Cortado: o limiar numérico; a medição de linhas no médio e no pequeno (`L-01`); qualquer subcomando ou mudança em `scaffold.aprovar`, `lint_plano` ou `porte.py`; mudança no `intake/SKILL.md` — o passo 6 já manda o esboço para *O que cada porte carrega*, onde o critério passa a morar, então o `intake` o recebe sem edição (uma fonte por fato) |

## Solução

**Norma** (`docs/plan/system/modelo-dev-units.md`):

1. *O que cada porte carrega*: subseção nova **Quando cada porte cabe**, com as três perguntas da
   tabela acima, a ordem em que se respondem (a primeira que responde sim decide), a frase de que
   contagem de unidades, tarefas ou arquivos é contexto e não critério (com a sobreposição medida
   em `porte-medido.md`), e a de que o *porte provável* de *Tipo de plano* é ponto de partida que
   as perguntas confirmam ou corrigem.
2. *Modo `review` — os seis checks*, linha "dividido": o julgamento passa a relatar também o porte
   recomendado contra o declarado, pelo critério de *Quando cada porte cabe*.
3. *Avaliação de escopo → O que a avaliação não faz*, primeiro item: acrescentar que a
   recomendação de porte é **aviso**, nunca bloqueante; a declaração continua do humano na
   aprovação (*Aprovação*).

**Skill** (`.claude/skills/review-plan/SKILL.md`):

4. Passo 3 passa a **Tamanho e porte como contexto**: relata o tamanho como hoje e acrescenta uma
   linha `porte recomendado: <porte> — <porquê>`, citando a pergunta de *Quando cada porte cabe*
   que decidiu e a evidência do plano: a decomposição em `## Escopo` (grande) ou `## Tarefas`
   (médio), ou, sem nenhuma das duas, a `## Solução` que mostra se há passos (`L-04`). Quando
   difere do `plan_size` do esboço, o achado é `aviso`, origem `julgamento` — e reestruturar o
   formato para o outro porte é decisão do humano, não da revisão.

## Oráculo

- `grep -n "Quando cada porte cabe" docs/plan/system/modelo-dev-units.md` acha a subseção e a
  citação na linha "dividido" de *Modo `review`*.
- `grep -n "porte recomendado" .claude/skills/review-plan/SKILL.md` acha o passo 3, e o passo diz
  `aviso` e nunca `bloqueante`.
- *Aprovação* e `scaffold.aprovar` intocados: `git diff --stat` não lista `scaffold.py` nem a
  seção *Aprovação* muda.
- `lint_skill.lint` sobre `.claude/skills/review-plan/SKILL.md` devolve lista vazia (roda pelo
  `test-python.sh`).

Critério de saída: os itens acima, conferidos pelo humano no diff, e a aprovação humana do texto
(oráculo do tipo `norma`).

## Lacunas

| # | Lacuna | Detalhe |
|---|---|---|
| L-01 | **Linhas alteradas não se medem fora do grande** | `porte.registrar` mede só arquivos declarados em unidades (`D-19` do `0001`); médio e pequeno saem `—`. Sem isso, não há como conferir depois se a recomendação acertou em custo. Gatilho para plano próprio: a primeira recomendação de porte que o humano rejeitar na aprovação, ou o primeiro médio que precise virar grande no meio da execução |
| L-02 | **A métrica mede preenchimento, não acerto** | Mesmo caso do `L-03` do `0012`. O acerto se observaria em trocas de `plan_size` entre revisão e aprovação, cujo baseline neste repositório já é zero |
| L-03 | **A correção chega a quem já instalou só no próximo release** | Mesmo caso do `L-02` do `0014`: o `bootstrap` nunca sobrescreve a cópia da norma no projeto |
| L-04 | **O passo 3 lê só `## Escopo`, que só o grande tem** | Hoje o passo 3 do `review-plan` tira o tamanho de `## Escopo`. O item 4 não diz de onde vem a evidência da recomendação num médio (`## Tarefas`) ou num pequeno (nenhuma decomposição) — justamente os casos em que a recomendação mais importa. Levantada na revisão de 2026-11-20. **Fechada no item 4 da *Solução*, com o sim do humano em 2026-11-20** |

## Fonte

- [`modelo-dev-units.md`](../system/modelo-dev-units.md), seções *Aprovação*, *O que cada porte
  carrega*, *Tipo de plano*, *Porte medido*, *Avaliação de escopo → O que a avaliação não faz*,
  *Modo `review`*, *Fluxo completo*
- [`porte-medido.md`](../system/porte-medido.md)
- [`review-plan/SKILL.md`](../../../.claude/skills/review-plan/SKILL.md), passo 3
- [`0006-e2e-fixes.md`](0006-e2e-fixes.md), `L-04`;
  [`0012-add-plan-type.md`](0012-add-plan-type.md), `L-03`;
  [`0008-wire-huddle-cycle.md`](0008-wire-huddle-cycle.md), `D-14`
