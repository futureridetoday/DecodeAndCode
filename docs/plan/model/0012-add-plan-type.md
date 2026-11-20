---
# about
name: add-plan-type
type: plan
project: DecodeAndCode
description: O plano passa a declarar `plan_type` num vocabulário fechado de sete tipos, validado como `plan_size`, e a norma diz o que cada tipo muda no review, no derive e no implement — oráculo, porte provável e quem executa
tags: [decode-and-code, norma, plano, plan-type, lint]

# alvo
plan_id: "0012"
plan_size: médio
plan_type: feature
core: model
module: add-plan-type
block: ""

# history
author: Claude
created: 2026-11-19
status: done
version: 1.0.0
updated: ""
approved_by: "Bortoli Rafael"
approved_at: "2026-11-19"

# system
scope: project
auto_load: false
dependencies: []
---

# O plano declara o seu tipo, e o tipo diz o oráculo

> **Tipo proposto deste plano: `feature`** — capacidade nova do método, com código (`lint_plano`,
> `scaffold`) e norma. O humano confirma na aprovação, junto com o porte.

## Objetivo

**Clarificar.** Hoje nada no plano declara **que tipo de trabalho** ele é, e por isso nada diz, antes
da aprovação, qual é o oráculo dele nem que porte é provável. Métrica: planos novos que chegam à
aprovação com o tipo declarado e o oráculo do tipo verificável no próprio texto — hoje **0 de 11**;
alvo, todos a partir deste. Beneficiário: o humano que aprova (recebe tipo e porte propostos, com o
porquê, em vez de um porte escolhido para o lint passar — `L-04` do `0006`), e quem revisa e deriva.

**Evitar.**

| Alternativa | Por que não basta |
|---|---|
| Deduzir o tipo do prefixo do nome (`fix-`, `add-`, `wire-`) | O prefixo é intenção livre (*Nomenclatura → Plano*), e já errou: o `0011` chama-se `fix-norma-config-claims` e é `norma`. Dos 11 planos, 7 começam por palavra que não é tipo nenhum (`decode-`, `record-`, `derive-`, `installable-`, `plugin-`, `e2e-`, `onboard-`). Fechar o prefixo num vocabulário mudaria a regra de nome e renomearia nada do que existe |
| Só texto na norma, sem campo | O intake proporia o tipo em prosa, e nada conferiria a presença dele na aprovação — o mesmo buraco que `plan_size` fechou com o gate |
| Variar o `model:` da skill por tipo | `model:` é frontmatter estático da skill (norma, *Modelos*); não há como uma skill trocar de modelo por campo do plano. A alocação de modelo por tipo só existe como **quem executa**: o `implement` (Sonnet, em fork) ou a sessão que orquestra (Opus) |

**Reduzir.** Um campo, uma constante, duas checagens que copiam o padrão de `plan_size`, e uma
tabela na norma. O resto — o que cada tipo muda a jusante — é texto que as skills **citam**, não
copiam. `intake/SKILL.md` não é tocado: o passo 6 já manda o esboço para *O que cada porte carrega*,
e é dali que a norma aponta para a tabela de tipos.

### Uma fonte por fato — campo e prefixo

**O campo é o fato; o prefixo continua intenção livre.** A norma ganha uma frase em *Nomenclatura →
Plano*: a intenção no nome não declara o tipo, e não precisa coincidir com ele. Nenhum script
compara os dois. Com isso não há dois lugares dizendo a mesma coisa — o nome diz o que se faz, o
campo diz que oráculo vale.

### O que cada tipo muda a jusante

O que **não** varia por tipo, e vale dizer antes da tabela: o pequeno e o médio **nunca** passam pelo
`implement` — a sessão que orquestra executa (norma, *Fluxo completo*). As colunas *derive* e
*implement* abaixo agem só no **grande**; nos outros portes o tipo muda o review e o oráculo de
entrega.

| Tipo | Oráculo de entrega | Porte provável | `review-plan` confere | `derive` (grande) | Quem executa |
|---|---|---|---|---|---|
| `fix` | O teste que reproduz o defeito, vermelho antes do código e verde depois | pequeno, médio | O defeito está medido e citado (`L-XX`, `H-XX`, incidente) e o teste que o reproduz está declarado | A mesma unidade leva o teste que reproduz e a correção — unidade só com o teste terminaria vermelha e o gate de saída nunca a marcaria `verified`; o critério de aceite exige a execução vermelha antes do código | `implement` (Sonnet); o relatório mostra a execução vermelha, e o gate de saída, a verde |
| `feature` | Teste declarado de cada unidade — o ciclo como é hoje | médio, grande | `## Independência` auditada com peso, como já pede o grande | Sem regra nova | `implement` (Sonnet) |
| `remove` | Suíte verde e diff com saldo **negativo** de linhas | pequeno, médio | A evidência de não uso está citada (busca, medição) | As unidades declaram em `test:` a suíte existente que cobre o que sai | `implement` (Sonnet); a revisão da entrega mede o saldo com `git diff --numstat` |
| `refactor` | Suíte verde **sem alterar teste existente** | médio | O gate A cita a dor medida | Nenhuma unidade lista teste existente em *Arquivos* | `implement` (Sonnet); a revisão da entrega confere `git diff --stat` vazio nos testes existentes |
| `norma` | Aprovação humana (`approved_by`/`approved_at`) | pequeno | Lista as seções da norma que mudam; nenhum arquivo de código | Só unidades `unit_type: norma` | No pequeno, a sessão que orquestra; no grande, o `implement`, como hoje — o gate de saída fecha a unidade `norma` pela aprovação humana (`verificacao._verificar_norma`), sem rodar teste |
| `chore` | O artefato produzido existe e funciona (zip, release, CI verde) | médio | O artefato e o modo de conferi-lo estão nomeados | Sem regra nova | `implement` (Sonnet) |
| `spike` | A medição ou a decisão registrada — huddle, `## Decisões` ou outro plano | pequeno | A pergunta está escrita e o destino da resposta, nomeado; nenhum código de produção | Não se deriva `spike` grande | A sessão que orquestra (Opus), sem `implement` |

O porte provável é **recomendação** para o intake propor, não regra: o lint não cruza tipo com porte.

No grande, todo tipo que passa pelo `implement` com `unit_type: dev` — `fix`, `feature`, `remove`,
`refactor` e `chore` — precisa de teste com runner declarado, hoje só `.py` e `.ts` (`H-14`). O
oráculo de um `chore` grande, como o zip que instala, entra embrulhado num teste desses.

## Gates

| Gate | Resposta |
|---|---|
| **A — necessidade real** | **Sim, com base estreita, e somada a exigência explícita do humano** (2026-11-19, vocabulário decidido — protocolo de exceção, *exigência explícita*). Medido: `L-04` do `0006` (o intake grava o porte para o lint passar, e o humano perde a recomendação); o `0011`, cujo prefixo `fix-` contradiz o tipo `norma` — o oráculo dele é aprovação humana, e nada no plano o declarava. **Não medido:** nenhum incidente de oráculo ou executor errado por falta de tipo; `remove`, `refactor` e `spike` não têm precedente nos 11 planos (`L-01`) |
| **B — mínimo viável** | Cortados, reabríveis: **checagem de tipo × porte** no `lint_plano` (o porte provável fica recomendação); **checagem de tipo × `unit_type`** no `lint_unidade` (plano `norma` com unidade `dev` — sem incidente); **scripts de oráculo** para `remove` (saldo negativo) e `refactor` (testes intocados) — viram passo da revisão da entrega até a primeira instância medir a necessidade; **coluna *Tipo*** em `porte-medido.md` e em `_planos.md` (reabre quando houver planos suficientes para calibrar porte por tipo); **retroativo** nos 11 planos aprovados (o `lint_plano` não roda sobre eles). Fora por restrição: `intake/SKILL.md` (4095/4096 bytes) |

## Tarefas

- [x] `lib.PLAN_TYPES_VALIDOS` com os sete tipos, ao lado de `PLAN_SIZES_VALIDOS`, uma cópia só
- [x] `lint_plano.lint`: `plan_type` ausente, vazio ou fora do vocabulário entra na lista de problemas, sem encerrar as demais checagens (o tipo não muda o schema do porte), com teste
- [x] `scaffold.aprovar`: recusa `plan_type` ausente ou fora do vocabulário, antes de mover e inclusive em `dry_run`, com teste
- [x] Norma, *Formato do plano*: seção *Tipo de plano* com a tabela acima; *Aprovação* passa a quatro campos; *O que cada porte carrega* aponta para a tabela; *Nomenclatura → Plano* ganha a frase do prefixo
- [x] `review-plan/SKILL.md`: uma linha no check de padrões — o plano declara o oráculo do seu tipo (cita a norma, não copia)
- [x] `derive/SKILL.md`: uma linha no passo de decisão das unidades — a coluna *derive* da tabela (cita a norma)
- [x] Declarar `plan_type` nos três esboços do `_inbox` — `apply-plugin-review`, `fix-setup-validation` e este, `add-plan-type` (`feature`) —, para que o `lint-plano` siga limpo
- [x] `scripts/test-python.sh` verde (a suíte inteira)

## Oráculo

| Alvo | Como se sabe que funcionou |
|---|---|
| `lint_plano` | Teste: plano sem `plan_type`, com `plan_type: perf` e com `plan_type: fix` — os dois primeiros com um problema que nomeia o vocabulário, o terceiro sem |
| `scaffold.aprovar` | Teste: `ValueError` para `plan_type` ausente e fora do vocabulário, nada movido, inclusive em `dry_run` |
| Norma | `grep -c "plan_type"` acha a tabela em *Tipo de plano*, e a tabela só existe ali (as skills citam a seção) |
| Esboços do `_inbox` | `dc.py lint-plano` sem problema nos três esboços |
| Intake | Próximo intake real grava `plan_type` com o porquê, sem edição na `intake/SKILL.md` — medido no primeiro uso, não neste plano |

## Decisões

Decididas pelo humano em 2026-11-19, a partir das propostas da revisão.

| # | Decisão |
|---|---|
| D-01 | **`feature` fica no vocabulário**, como o caso comum (7 dos 11 planos) contra o qual os outros tipos diferem |
| D-02 | **`scaffold.aprovar` recusa `plan_type` ausente ou fora do vocabulário**, no mesmo padrão de `plan_size` — é na aprovação que o humano confirma o tipo |
| D-03 | **A classificação dos 11 planos confere**, para registro, sem retroativo no frontmatter: `feature` 0001–0004 e 0007–0009; `fix` 0006 e 0010; `chore` 0005; `norma` 0011 |

## Lacunas

| # | Lacuna | Detalhe |
|---|---|---|
| L-01 | **`remove`, `refactor` e `spike` não têm precedente** | Nenhum dos 11 planos é de um desses tipos; as linhas deles na tabela são desenho, não medição. O primeiro plano de cada um é onde a linha se prova — ou se corrige |
| L-02 | **O tipo não troca o modelo do pequeno e do médio** | Quem executa no pequeno e no médio é sempre a sessão que orquestra, no modelo dela; *Opus* e *Sonnet* da tabela só se aplicam ao grande. Se o pedido pressupunha troca de modelo em todo porte, isso não se faz por campo do plano |
| L-03 | **A métrica mede preenchimento, não benefício** | Com o gate, "planos com tipo declarado" vai a 100% sozinha. O que o tipo deveria melhorar — oráculo e executor certos, porte recomendado sem reestruturação na aprovação (`L-04` do `0006`) — não tem medição definida aqui; os primeiros planos com tipo são onde se observa |
| L-04 | **O `lint_plano` roda, sim, sobre um plano aprovado** | O gate B cortou o retroativo dizendo que o `lint_plano` não roda sobre os 11 planos aprovados; `test_lint_plano.TestPlanoRealDoRepositorio` o roda sobre o `0001`. Na execução, o teste passou a esperar exatamente o problema de `plan_type` ausente, sem tocar o frontmatter do `0001` (`D-03`). Se o retroativo for reaberto, o teste volta a esperar `[]` |

## Fonte

- [`modelo-dev-units.md`](../system/modelo-dev-units.md), *Tipo de unidade*, *Aprovação — três campos declarados pelo humano*, *O que cada porte carrega*, *Nomenclatura → Plano*, *Modelos*, *Fluxo completo*
- [`0006-e2e-fixes.md`](0006-e2e-fixes.md), `L-04`
- [`0011-fix-norma-config-claims.md`](0011-fix-norma-config-claims.md)
- [`_planos.md`](../_planos.md) — os 11 nomes de plano

## Backlog

<!-- backlog:start -->
- [x] `lib.PLAN_TYPES_VALIDOS` com os sete tipos, ao lado de `PLAN_SIZES_VALIDOS`, uma cópia só
- [x] `lint_plano.lint`: `plan_type` ausente, vazio ou fora do vocabulário entra na lista de problemas, sem encerrar as demais checagens (o tipo não muda o schema do porte), com teste
- [x] `scaffold.aprovar`: recusa `plan_type` ausente ou fora do vocabulário, antes de mover e inclusive em `dry_run`, com teste
- [x] Norma, *Formato do plano*: seção *Tipo de plano* com a tabela acima; *Aprovação* passa a quatro campos; *O que cada porte carrega* aponta para a tabela; *Nomenclatura → Plano* ganha a frase do prefixo
- [x] `review-plan/SKILL.md`: uma linha no check de padrões — o plano declara o oráculo do seu tipo (cita a norma, não copia)
- [x] `derive/SKILL.md`: uma linha no passo de decisão das unidades — a coluna *derive* da tabela (cita a norma)
- [x] Declarar `plan_type` nos três esboços do `_inbox` — `apply-plugin-review`, `fix-setup-validation` e este, `add-plan-type` (`feature`) —, para que o `lint-plano` siga limpo
- [x] `scripts/test-python.sh` verde (a suíte inteira)

8 de 8 tarefas concluídas · atualizado em 2026-11-19
<!-- backlog:end -->
