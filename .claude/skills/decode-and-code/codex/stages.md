---
# about
name: codex-stages
type: knowledge
project: ""
description: Codex do decode-and-code, capítulo das etapas — o workflow, a etapa e cada etapa do núcleo, com quem faz, o que entra, o que sai, os gates e as regras
tags: [codex, workflow, etapa]

# history
author: Bortoli
created: 2026-11-25
status: draft
version: 0.1.0
updated: ""

# system
scope: project
source: ""
auto_load: false
checksum: ""
dependencies: []
---

# Etapas

## Workflow

**O que é:** a sequência de etapas que um plano segue, escolhida pelo tipo do plano.

- **Quem faz:** Claude e o usuário, cada um nas etapas que lhe cabem.
- **Entrada, comum a todo workflow:**
  1. O usuário traz um pedido, blocos de texto para juntar ou um insight. Sai um pedido único, ou uma
     conversa que termina sem plano.
  2. Claude identifica o tipo do plano, com as perguntas que precisar, e o declara com o motivo; o
     usuário pode corrigi-lo. Saem o objetivo do plano, confirmado pelo usuário, e o workflow que o
     plano segue.
- **Workflow de produto, depois da entrada:**
  - P1, decode.
  - P2, aprovação da proposta.
  - P3, revisão.
  - P4, aprovação do plano técnico.
  - P5, derive, só no médio e no grande, que termina na aprovação das unidades derivadas.
  - P6, code.
  - P7, teste e aprovação de cada entrega.
  - P8, teste do plano inteiro, só no grande.
  - Aprovação final.
- **Regras:** o workflow de produto vale para todo tipo que não tem workflow próprio. Um workflow
  próprio tem capítulo próprio no codex e não muda este.

**Ver também:** Etapa, Tipo, Pedido, Insight, Objetivo do plano, Aprovação, Porte.

## Etapa

**O que é:** um passo de um workflow, com quem o faz e o que sai dele.

- **Regras:**
  - Cada etapa diz quem a faz — Claude, o usuário ou os dois —, o que entra, o que sai e os gates de
    entrada e de saída.
  - Algumas etapas são aprovações.

**Ver também:** Workflow, Aprovação, Usuário, Claude.

## Decode

**O que é:** a etapa P1 do workflow de produto, em que Claude entende o pedido e propõe uma solução
conceitual.

- **Quem faz:** Claude, nos papéis de PM, Designer e Tech Lead.
- **O que entra:** o pedido, o tipo e o objetivo do plano.
- **O que sai:** a proposta, escrita para o usuário.
- **Gate de saída:** a proposta só vai à aprovação (P2) se passa nos dois gates.
  - A, necessidade real: o problema é de alguém agora, e a hipótese tem sinal mensurável.
  - B, mínimo viável: é a menor versão que resolve, com o que fica de fora declarado.
- **Regras:**
  - Decodifica com o mindset de produto, apoiado nas referências de produto, e com o fluxo de
    decodificação como base.
  - Usa o que o projeto já tem: a foundation, os princípios, as guidelines, os guardrails e os
    recursos do projeto.
  - Um recurso do projeto é usado pelo nome, nunca copiado, e o nome vai para a tabela de recursos do
    plano.

**Ver também:** Proposta, Mindset de produto, Referência de produto, Os quatro riscos, Hipótese, MVP,
Fluxo de decodificação, Papel, Foundation, Recurso do projeto, Tabela de recursos do plano, Aprovação.

## Revisão

**O que é:** a etapa P3 do workflow de produto, que transforma a proposta aprovada em plano técnico.

- **Quem faz:** Claude, nos papéis de PM e Tech Lead.
- **O que entra:** a proposta aprovada.
- **O que sai:** o plano técnico, com o porte definido e as tarefas ou unidades que o porte pede.
- **Gate de saída:** o plano técnico só vai à aprovação (P4) com porte, sem depender de outro plano
  e citando só recursos do projeto que existem.
- **Regras:**
  - Escreve as histórias, com os critérios de aceite, apoiada em INVEST e em User Story Mapping.
  - Refina a viabilidade técnica, a compatibilidade, a infraestrutura, os erros, o que falta e as
    decisões em aberto.
  - Quebra o trabalho em tarefas e define o porte.

**Ver também:** Plano técnico, História, Critério de aceite, Tarefa, Unidade, Porte, Independência
entre planos, Tabela de recursos do plano, Referência de produto, Papel, Aprovação.

## Derive

**O que é:** a etapa P5 do workflow de produto, que prepara cada unidade para ser executada sem o
histórico da conversa; só existe no médio e no grande.

- **Quem faz:** Claude.
- **O que entra:** o plano técnico aprovado.
- **O que sai:** cada unidade pronta para o code, e o handoff que leva a execução a uma sessão nova.
- **Gate de saída:** a aprovação das unidades derivadas pelo usuário.
- **Regras:**
  - Dá a cada unidade o contexto, a memória e o padrão de código do projeto. A memória são as
    decisões e as lacunas que o plano registrou e que a unidade precisa conhecer.
  - Garante que cada unidade cumpre a Definition of Ready e basta sozinha.
  - Cita na unidade as guidelines que valem para ela.
  - Confere se os recursos do projeto citados ainda existem.

**Ver também:** Unidade, Cold-start, Definition of Ready, Handoff, Lacuna, Padrão de código,
Guideline, Tabela de recursos do plano, Aprovação.

## Code

**O que é:** a etapa P6 do workflow de produto, em que Claude produz o que o plano pede.

- **Quem faz:** Claude.
- **O que entra:** no pequeno, o plano técnico aprovado; no médio e no grande, uma unidade derivada e
  aprovada.
- **O que sai:** a entrega.
- **Gate de entrada:** o critério de aceite está declarado, com o teste que o verifica, e os
  recursos do projeto citados existem.
- **Gate de saída:** o teste da entrega e a aprovação do usuário (P7).
- **Regras:**
  - No pequeno, as tarefas rodam na mesma sessão.
  - No médio e no grande, roda uma unidade por vez, de preferência numa sessão nova: a unidade basta
    sozinha, e começar sem o histórico custa menos.
  - A próxima unidade só começa depois da aprovação da anterior.
  - Usa os recursos do projeto e as guidelines que valem para os caminhos que toca.
  - Unidade insuficiente vira lacuna.

**Ver também:** Entrega, Critério de aceite, Teste, Unidade, Tarefa, Cold-start, Lacuna, Recurso do
projeto, Guideline, Aprovação.

## Setup

**O que é:** o primeiro uso do DC num projeto, em que o projeto ganha os seus princípios, guidelines
e guardrails.

- **Quem faz:** Claude propõe; o usuário aprova cada escrita.
- **O que entra:** um projeto que ainda não fez o setup.
- **O que sai:**
  - os princípios, as guidelines e os guardrails do projeto, com a guideline que liga caminhos do
    projeto aos recursos que valem para eles;
  - a foundation, com o mapa de recursos do projeto;
  - a permissão de uso de cada recurso do projeto que o DC pode usar;
  - o huddle iniciado.
- **Regras:**
  - É proposto quando falta, e cada escrita no projeto pede o sim do usuário, uma sugestão por vez.
  - Nada do que grava no projeto repete ou contradiz o codex, e o codex não é copiado para o projeto.

**Ver também:** Rethink, Princípio, Guideline, Guardrail, Foundation, Mapa de recursos do projeto,
Recurso do projeto, Huddle, Invariante, Restrição fundamental.

## Rethink

**O que é:** a revisão dos princípios, das guidelines e dos guardrails do projeto depois de uma
mudança de rumo.

- **Quem faz:** Claude propõe; o usuário aprova cada escrita.
- **O que entra:** um projeto com o setup feito e uma mudança de rumo.
- **O que sai:** cada item mantido, editado ou arquivado; a foundation e o mapa de recursos do
  projeto atualizados; os recursos do projeto que a mudança pede criados ou removidos.
- **Regras:**
  - Só o rethink cria ou remove um recurso do projeto, e um recurso criado depois do setup só entra
    no mapa de recursos por ele.
  - Valem as mesmas regras do setup para escrever no projeto.

**Ver também:** Setup, Princípio, Guideline, Guardrail, Foundation, Mapa de recursos do projeto,
Recurso do projeto.
