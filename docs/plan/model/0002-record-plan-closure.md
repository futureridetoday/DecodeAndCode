---
# about
name: record-plan-closure
type: plan
project: DecodeAndCode
description: O arquivo do plano passa a registrar o próprio fechamento — hoje ele diz `status: approved` para sempre, e quem quer saber se terminou precisa abrir outro arquivo
tags: [decode-and-code, plano, fechamento, projecao]

# alvo
plan_id: "0002"
plan_size: pequeno
core: model
module: record-plan-closure
block: ""

# history
author: Bortoli
created: 2026-08-27
status: done
version: 1.0.0
updated: ""
approved_by: Bortoli
approved_at: 2026-08-27

# system
scope: project
auto_load: false
dependencies: []
---

# O arquivo do plano passa a dizer que fechou

## Objetivo

**Medido em 2026-08-27, no `0001` recém-concluído:** o plano fechou — `_planos.md` projeta
`concluído`, o backlog projeta `21 de 21 derivadas · 21 verificadas`, e `porte-medido.md` gravou a
linha — e o **arquivo do plano** continua com `status: approved` e `updated: 2026-08-22`, cinco
dias antes do fechamento.

Quem abrir `0001-decode-and-code-foundation.md` daqui a seis meses lê um campo que mente e precisa
ir a **outro arquivo** para saber que o trabalho terminou. É a classe da `L-22`: campo que ninguém
projeta e que envelhece como afirmação falsa.

A norma trata `status:` como oráculo **só no porte pequeno** — *"a etapa 9 fecha quando o humano
grava `status: done`, nunca um script"* ([`modelo-dev-units.md`](../system/modelo-dev-units.md),
*Fluxo completo*). No grande, a situação é projetada das unidades e vive em `_planos.md`; nada
nunca definiu o que acontece com o campo dentro do arquivo do plano.

## Solução

`backlog.projetar` grava `status: done` no arquivo do plano **na transição** para `concluído` — o
mesmo instante em que já chama `porte.registrar`, e pela mesma guarda: transição, nunca a cada
execução sobre um plano que já fechou.

**Isso estende a decisão 13, e a extensão precisa estar escrita.** A decisão diz que script escreve
apenas o bloco `# verificação` do frontmatter e nunca o corpo — regra formulada para a **unidade**.
O plano é outro artefato, e nele o campo projetado é `status`. A norma passa a dizer as duas coisas,
em vez de deixar a segunda por inferência.

**O que não muda:** no porte pequeno, `status: done` continua sendo ato do **humano** — lá não há
unidade para projetar situação nenhuma, e o campo é o oráculo, não a projeção dele. A escrita por
script vale para médio e grande, onde a situação já é derivada.

**Efeito retroativo, e é desejado:** com o mecanismo em pé, a primeira projeção sobre o `0001`
grava o campo que hoje falta. O plano fechado passa a se declarar sem ninguém editar à mão.

## Oráculo

`tests/test_situacao.py` — a transição para `concluído` grava `status: done` no arquivo do plano;
uma segunda projeção com a situação já `concluído` **não reescreve**; e projeção que devolve `em
desenvolvimento` nunca toca o campo. Três casos, um por ramo, no mesmo padrão da guarda que
`porte.registrar` já usa.

Mais o caso contra a instância: projetar o `0001` real deixa o arquivo com `status: done` — é o que
separa provar o mecanismo de provar que ele funciona no artefato que motivou o plano (`L-31`).

## Fonte

- Medição de 2026-08-27, na validação de conclusão do plano `0001`
- [`modelo-dev-units.md`](../system/modelo-dev-units.md), *Fluxo completo* (etapa 9) e decisão 13
- `0001`, `L-22` — a linha órfã que ninguém projetava e que sempre mentia
