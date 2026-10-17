---
# about
name: e2e-fixes
type: plan
project: DecodeAndCode
description: Correções dos oito defeitos que o teste ponta a ponta do plugin encontrou antes do release 2.0 — runner, aprovação, bootstrap, normas das unidades e textos das skills — com o mesmo teste como critério de saída
tags: [decode-and-code, plugin, e2e, release]

# alvo
plan_id: "0006"
plan_size: médio
core: model
module: e2e-fixes
block: ""

# history
author: Claude
created: 2026-10-16
status: approved
version: 1.0.0
updated: ""
approved_by: bortolirafael
approved_at: 2026-10-16

# system
scope: project
auto_load: false
dependencies: []
---

# Correções do teste ponta a ponta — antes do release 2.0

## Contexto

Antes de promover `dev` para `main` como 2.0.0, o plugin rodou como um usuário novo usaria: pacote
construído de `dev` (`9e47e50`), projeto Python vazio, `--plugin-dir`, e o ciclo inteiro
`intake → review-plan → aprovação → derive → implement`.

O pacote passou em `verificar`, `validar` e `claude plugin validate --strict`, e o ciclo fechou com
a unidade `verified` e os testes do projeto passando, a cerca de US$ 3. **Mas só fechou com três
intervenções manuais:** bootstrap rodado à mão, plano corrigido à mão e runner de teste criado à
mão. Os defeitos abaixo são o que um usuário novo encontraria.

A evidência bruta (streams) ficou fora do repositório; o resumo por etapa fica aqui:

| Etapa | Resultado | Tempo / custo | Desvio |
|---|---|---|---|
| `intake`, sem bootstrap | parou, sem esboço | 31 s / US$ 0,30 | pediu a norma e fez 4 perguntas |
| `intake`, após bootstrap manual | esboço no `_inbox` | 55 s / US$ 0,43 | resposta final em inglês |
| `review-plan` | 0 bloqueantes, 4 avisos | 53 s / US$ 0,57 | — |
| aprovação (humano) | campos preenchidos | — | — |
| `derive` | falhou | 46 s / US$ 0,38 | `aprovar` moveu o plano e falhou por falta de `plan_id` |
| `derive`, porte pequeno | ok, sem unidade | 24 s / US$ 0,13 | após devolver o plano ao `_inbox` e acrescentar `plan_id` |
| `implement` sobre o pequeno | recusou | 14 s / US$ 0,11 | mandou rodar o `derive` de novo |
| `derive`, porte grande | ok, unidade `01-divide` | 83 s / US$ 0,81 | — |
| `implement` | falhou no gate de saída | 54 s / US$ 0,13 | `FileNotFoundError` em `scripts/test-python.sh` |
| `implement`, após criar o runner | `verified`, 3 testes passando | 25 s / US$ 0,05 | — |

## Defeitos

| # | Defeito | Efeito | Responsável |
|---|---|---|---|
| D1 | O runner `.py` do `config.json` é `scripts/test-python.sh`, resolvido a partir da raiz do projeto, e o bootstrap não o cria | O gate de saída quebra em todo projeto novo: nenhuma unidade chega a `verified` sem ajuste manual | `config.json`, `verificacao.py` |
| D2 | O esboço do `intake` sai sem `plan_id`, e o `aprovar` falha **depois** de mover o arquivo — `escrever_campos` não cria campo ausente | O `derive` quebra e deixa o plano movido e meio aprovado | `scaffold.aprovar`, `lint_plano.py` |
| D3 | O `intake` não roda o bootstrap e para pedindo a norma | O primeiro uso num projeto novo trava | `intake/SKILL.md` |
| D4 | No porte pequeno, o `derive` diz "implemente direto", e o `implement` exige unidade | O porte pequeno não tem caminho até a execução — e a norma (*Fluxo completo*) não diz quem executa o pequeno | norma, `derive/SKILL.md`, `implement/SKILL.md` |
| D5 | O `derive` escreve *Normas aplicáveis* sem link, e `dc.py normas` não resolve nenhuma linha | A correção da `L-08` não alcança as unidades que o próprio `derive` produz | `derive/SKILL.md`, `lint_unidade.py` |
| D6 | Sem `.claude/`, os scripts não acham a raiz do projeto | Mesmo efeito de D3 | coberto por D3 |
| D7 | O `review-plan` diz que `## Independência` ausente é bloqueante; a norma a **recusa** no porte pequeno | Texto contradiz a norma; o modelo acertou mesmo assim | `review-plan/SKILL.md` |
| D8 | A resposta final do `intake` saiu em inglês num projeto em português | Atrito para o usuário | `intake/SKILL.md` |

> **Correção registrada.** No PR da `L-08` (#22) o orquestrador afirmou que citação sem link "não é
> o formato que o `derive` produz". O teste mostrou o contrário — é a origem de D5.

## Solução recomendada

**D1 — runner de teste num projeto novo.** O pacote leva um runner `.py` próprio, que roda
`python3 -m unittest` sobre o caminho declarado; `verificacao` procura primeiro o runner do projeto
e, na falta, usa o do pacote. O `.ts` continua exigindo runner no projeto, com mensagem que diz o
que falta. Não escreve nada no projeto do usuário e não muda quem já tem runner (este repositório,
o AmFlow).

**D2 — aprovação não atômica.** Duas camadas: o `lint-plano`, que o `intake` já roda, passa a
exigir os campos que o `aprovar` vai escrever (`plan_id`, `status`) — o esboço defeituoso é barrado
na origem; e o `aprovar` confere esses campos **antes** de mover, falhando sem tocar em nada.

**D3 e D6 — primeiro uso sem bootstrap.** O primeiro passo do `intake` vira `dc.py bootstrap`:
idempotente, nunca sobrescreve, então roda sempre. O bootstrap já cria `.claude/`, o que fecha D6
**quando a entrada é o `intake`**. Quem começa por um plano escrito à mão e vai direto ao
`review-plan` ou ao `derive` não passa por ele: para esse caminho, a mensagem de "raiz do
repositório não localizada" passa a nomear `dc.py bootstrap` como o que falta.

**D5 — normas das unidades.** O `lint-unidade`, que o `derive` roda antes de entregar e o
`implement` roda no gate de entrada, passa a usar `normas.resolver` e reprova citação que não
resolve. O passo de escrita do `derive` passa a nomear o formato: link relativo e "seção *X*". Uma
regra, aplicada por script. As unidades antigas do plano `0001` (40 citações sem resolução) já
estão `verified` e não passam mais pelo gate; se algum teste as lintar, ajusta-se o teste.

**D4, D7 e D8 — textos das skills.**
- D4: pela norma, o pequeno não tem unidade — não se estende o `implement`. A regra nasce na
  norma: *Fluxo completo* passa a dizer que o plano pequeno aprovado é executado pela sessão que
  orquestra, sem `implement`, e fecha quando o humano grava `status: done`. O `derive` e a recusa
  do `implement` passam a citar essa seção, sem repetir a regra.
- D7: a regra de *Independência* no `review-plan` passa a depender do porte, como a norma manda.
- D8: a resposta final do `intake` sai no idioma do pedido do usuário — não fixa português, porque
  o plugin serve a qualquer projeto.

## Tarefas

- [x] T1 — uma linha em `apply-plugin-review.md` apontando para este plano como continuação — os defeitos ficam só aqui (uma fonte por fato)
- [x] T2 — D1: runner `.py` no pacote e resolução projeto → pacote em `verificacao` (PR próprio)
- [x] T3 — D2: `lint-plano` exige `plan_id` e `status`; `aprovar` confere antes de mover (PR próprio)
- [x] T4 — D3 e D6: `intake` roda `bootstrap` no primeiro passo; a mensagem de raiz não localizada nomeia `dc.py bootstrap`; prova em sessão real (PR próprio)
- [ ] T5 — D5: `lint-unidade` resolve as normas citadas; `derive` nomeia o formato (PR próprio)
- [ ] T6 — D4, D7 e D8: regra do pequeno em *Fluxo completo* da norma; ajustes de texto em `derive`, `implement`, `review-plan` e `intake` (PR próprio, ou três, a critério do humano)
- [ ] T7 — repetir o teste ponta a ponta, sem nenhuma intervenção manual

T2 e T3 não tocam os mesmos arquivos e podem rodar em paralelo. T4 a T6 tocam `SKILL.md`
diferentes, mas T5 e T6 dividem o `derive` — em sequência.

## Critério de saída

T7 passa: projeto vazio, plugin por `--plugin-dir`, ciclo completo do `intake` ao `implement` com a
unidade `verified` e os testes do projeto passando, **sem intervenção manual** e sem erro de
script. Preencher os três campos de aprovação é etapa humana do roteiro, não intervenção. Passando, o próximo passo é a promoção de `dev` para `main` como 2.0.0 — decisão do humano,
fora deste plano.

## Lacunas

| # | Lacuna | Por que fica registrada |
|---|---|---|
| L-01 | **O runner `.py` do pacote usa `python3 -m unittest <caminho>`, que exige o teste importável a partir da raiz** | Pode falhar com teste fora de pacote ou layout `src/`. O comportamento do `scripts/test-python.sh` deste repositório não foi comparado — T2 confere antes de escolher a forma |
| L-02 | **Não está decidido quem executa as caixas de `## Tarefas` no porte médio** | Mesma pergunta de D4, num porte que o teste não exercitou. Fica fora deste plano |

## Execução

Um PR por correção, para `dev`, cada um implementado por um agente Sonnet num worktree a partir de
`dev` e revisado pelo orquestrador, com a suíte, `validar --strict` e o CI verdes antes do PR. O PR
só abre com aprovação do humano.

## Backlog

<!-- backlog:start -->
- [x] T1 — uma linha em `apply-plugin-review.md` apontando para este plano como continuação — os defeitos ficam só aqui (uma fonte por fato)
- [x] T2 — D1: runner `.py` no pacote e resolução projeto → pacote em `verificacao` (PR próprio)
- [x] T3 — D2: `lint-plano` exige `plan_id` e `status`; `aprovar` confere antes de mover (PR próprio)
- [x] T4 — D3 e D6: `intake` roda `bootstrap` no primeiro passo; a mensagem de raiz não localizada nomeia `dc.py bootstrap`; prova em sessão real (PR próprio)
- [ ] T5 — D5: `lint-unidade` resolve as normas citadas; `derive` nomeia o formato (PR próprio)
- [ ] T6 — D4, D7 e D8: regra do pequeno em *Fluxo completo* da norma; ajustes de texto em `derive`, `implement`, `review-plan` e `intake` (PR próprio, ou três, a critério do humano)
- [ ] T7 — repetir o teste ponta a ponta, sem nenhuma intervenção manual

4 de 7 tarefas concluídas · atualizado em 2026-10-17
<!-- backlog:end -->

## Fonte

- Teste ponta a ponta de 2026-10-16, sobre `dev` em `9e47e50`
- Norma: [`modelo-dev-units.md`](../system/modelo-dev-units.md), seções *O que cada porte carrega*,
  *Aprovação — três campos declarados pelo humano* e *Os dois gates*
- Plano de origem dos achados: [`apply-plugin-review.md`](../_inbox/apply-plugin-review.md)
