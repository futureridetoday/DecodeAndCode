---
# about
name: redesign-handoff
type: doc
project: ""
description: Handoff para a sessão principal que vai criar o plano do redesign da norma para o codex — objetivo, fontes, o aviso de não usar o decode para planejar a própria substituição, o que pode ser absorvido dele e como trabalhar com a pessoa
tags: [codex, redesign, handoff]

# history
author: Bortoli
created: 2026-11-25
status: draft
version: 1.0.0
updated: ""

# system
scope: project
source: ""
auto_load: false
checksum: ""
dependencies: [atomic-inventory, redesign-brief]
---

# Handoff — plano do redesign da norma para o codex

Leia este arquivo inteiro antes de qualquer ação. Ele abre a sessão principal do redesign: esta
sessão conduz o plano e pode abrir sessões aninhadas para partes dele. Ela começa sem o histórico
das sessões anteriores; tudo o que precisa está aqui ou nos arquivos que este handoff aponta.

## Objetivo

Criar, com a pessoa, o plano de execução do redesign que substitui a norma do DC
([`modelo-dev-units.md`](../plan/system/modelo-dev-units.md)) pelo **codex**. O que o codex é e
contém já foi decidido; esta sessão decide **como** chegar lá: as partes, a ordem, o que cada
parte entrega e como cada uma é verificada.

## Fontes, em ordem de autoridade

1. **[`atomic-inventory.md`](atomic-inventory.md): a fonte da verdade.** Os 60 conceitos do codex,
   cada um com o que é, como funciona, o mecanismo de hoje, as relações e a origem. A seção *Como
   ler* explica os campos e as marcas de fonte. A seção *Termos e pontos em aberto* lista o que o
   redesign ainda precisa definir.
2. **[`redesign-brief.md`](redesign-brief.md): o contexto.** As ideias consolidadas, as 14 decisões
   com data, as peças essenciais do DC, a Clean Architecture aplicada ao método e onde cada
   conteúdo mora segundo a documentação do Claude Code. **Onde o brief e o inventário divergem,
   vale o inventário.**
3. **O projeto**, só como evidência do estado atual: o código, as skills e a norma de hoje. A norma
   atual não é fonte de regra para o codex: o diagnóstico de 2026-11-23 a mediu corrompida
   (brief, *Ponto de partida*).

Este handoff não repete o conteúdo das fontes, para não ter dois lugares com o mesmo fato.

## Aviso central: não usar o decode para planejar o redesign

**Usar o decode para planejar o redesign da norma do decode é um erro que pode comprometer todo o
plano.** A norma que está sendo substituída é a mesma que rege as skills, os scripts e os gates do
DC. Planejar com eles faria as regras velhas moldarem o plano novo: o teto de 8 passos, os portes
de hoje, uma aprovação só, o tipo `norma`, a numeração e o backlog projetado. A norma passaria a
reger a própria substituição.

Por isso, **neste trabalho não se usa:**

- as skills que planejam e executam no DC: `intake`, `review-plan`, `derive` e `implement`;
- plano em `docs/plan/_inbox/`, a aprovação e a numeração do `dc.py`, nem o backlog projetado;
- os lints do DC (`lint_plano`, `lint_unidade`) como gate do plano do redesign.

**O que pode ser absorvido**, à mão e como prática, porque funciona no planejamento, na revisão e
no desenvolvimento:

- **Decomposição em partes que bastam sozinhas:** cada parte entrega algo testável e traz o que
  precisa para rodar sem o histórico da conversa. É o que permite entregar uma parte a uma sessão
  aninhada.
- **Critério de aceite antes de começar:** cada parte diz, antes de começar, como se sabe que ficou
  pronta.
- **Revisão por checagens explícitas** antes de aprovar: duas partes não mexem no mesmo alvo ao
  mesmo tempo, uma parte não depende de outra sem dizer, e as lacunas ficam registradas.
- **Aprovação da pessoa antes de executar, e teste antes de fechar.**
- **Decisões com data e lacunas registradas no próprio plano.**
- **Handoff entre sessões,** como este.

Regra prática: quando um passo chamaria uma skill ou um script do DC, faça à mão o que ele faria de
útil e diga à pessoa que fez assim.

## O que já está decidido e ainda não está no código

As decisões estão no inventário e no brief. Duas pedem atenção no plano:

- **O teto de 8 passos por unidade** sai do código (`lint_unidade.py` e o teste dele) **só na
  execução do redesign**, junto com a troca da norma pelo codex, para os dois não divergirem
  (brief, decisão 3).
- **Três decisões do inventário ainda não foram levadas ao brief:** as aprovações novas (depois do
  derive e a aprovação final), a nova definição do huddle e o handoff no médio. A pessoa adiou
  esse ajuste. O plano decide se atualiza o brief ou se o inventário basta.

## Como trabalhar com a pessoa

- Toda a escrita é em pt-BR, objetiva.
- **Propor e aplicar só depois do sim.** Em revisão, item a item. Quando o pedido for ambíguo,
  declarar o entendimento numa frase e esperar.
- **Nada de commit sem pedido.** O trabalho entra por branch a partir de `dev` e PR para `dev`, com
  revisão manual da pessoa.
- Há dois huddles com nomes parecidos, `bortoli.md` e `bortoli-rafael.md`: são pessoas diferentes,
  e as entradas não se movem entre eles.
- A pessoa decide o que entra no plano. Quando houver opções, trazer uma recomendação e o tradeoff
  principal.

## Primeiro passo sugerido

1. Ler o inventário e o brief inteiros.
2. Propor à pessoa a estrutura do plano: onde ele mora (sugestão: `docs/codex/redesign-plan.md`,
   fora do `_inbox/`), as partes, a ordem e quais partes viram sessões aninhadas. Esperar o sim.
3. Começar pelos *Termos e pontos em aberto* que bloqueiam a escrita do codex, como proposta,
   entrega, critério de aceite e lacuna.
