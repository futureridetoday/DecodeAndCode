# planner

Versão 1.0.0 · agent

[← Como usar o Decode And Code](../../README.md#como-usar-o-decode-and-code)

## O que é

O agent que revisa planos no `_inbox/` e deriva a estrutura e as unidades de planos já aprovados,
aplicando a norma de Unidades de Desenvolvimento pela skill [`decode-and-code`](decode-and-code.md).
Roda em Opus e escreve apenas sob `<plan_root>/**`.

## Problema que resolve

`review` e `derive` pedem julgamento denso — erro conceitual num plano, a fatia de cada unidade — e
gastam contexto. Rodar isso na conversa principal mistura o trabalho de planejamento com o resto da
sessão. O agent isola: chega sem o contexto da conversa, faz só review ou derive, e devolve uma
mensagem só.

## Como funciona

Quando invocado, identifica o modo pedido (`review` ou `derive`) a partir do pedido explícito,
carrega a skill declarada em `skills: [decode-and-code]` e segue o que ela define para esse modo.
Em `review`, roda os checks determinísticos primeiro e reserva julgamento só para o que a skill
marca como tal. Em `derive`, decide a fatia de cada unidade — o único passo que pede julgamento
seu; o resto é mecânico. Encerra com o relatório que o modo pede.

## Como usar

Invoque pelo nome, com o modo e o alvo explícitos:

> @decode-and-code:planner revise o plano docs/plan/_inbox/catalogo.md

> @decode-and-code:planner derive o plano docs/plan/model/0005-catalogo/0005-catalogo.md

Use quando quiser review ou derive **isolados da conversa atual** — o agent não herda o contexto e
não deve ser usado para escrever um plano do zero (isso pede vaivém extenso e cabe a um `fork`).
Para implementar uma unidade, o recurso é o agent [`developer`](developer.md), nunca este.

## Exemplos de uso

**Revisão antes da aprovação.** Um plano acabou de ser escrito no `_inbox/`. `@decode-and-code:planner`
em modo `review` devolve os seis checks — o que o script decidiu (nome, concorrência, fontes) e o
que é julgamento (arquitetura, adequação) — mais as lacunas novas como `L-XX`. O humano decide a
aprovação a partir disso.

**Derivação de um plano grande.** Plano aprovado por um humano, ainda sem unidades.
`@decode-and-code:planner` em modo `derive` cria a subpasta do plano, gera um arquivo por unidade,
linta cada um, projeta o backlog e grava o handoff para a sessão de execução.

## Fundamentação

O agent é um invólucro fino sobre os modos `review` e `derive` da skill. A separação entre agent e
skill segue a norma: o `.md` do agent diz **quando e com que escopo** rodar; a skill diz **como**.
O escopo de escrita `<plan_root>/**` é declaração no corpo do agent, não imposição — impor de
verdade é guardrail do projeto que instala.

## Base de conhecimento

Nenhuma própria. Tudo o que aplica vem da skill `decode-and-code` e da norma que ela lê. O agent
declara `tools: Glob, Grep, Read, Bash, Write, Edit` e `model: opus`.

## Limites

- **Só `review` e `derive`.** Não implementa unidade — isso é do agent `developer`.
- **Não escreve plano do zero.** Começa cada invocação sem o contexto da conversa; escrever plano
  pede um `fork`.
- **Não aprova.** `review` encerra com achados; a aprovação continua sendo ato humano.
- **Escreve só sob `<plan_root>/**`.** Nunca toca código de produção — e isso é declaração, não
  barreira técnica.
- **Uma mensagem só.** Não itera pedindo confirmação no meio do relatório.
