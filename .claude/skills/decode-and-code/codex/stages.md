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
status: stable
version: 1.0.0
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
  - Aprovação final. No pequeno e no médio, ela coincide com a aprovação da única entrega, no P7.
- **Regras:** o workflow de produto vale para todo tipo que não tem workflow próprio. Um workflow
  próprio tem capítulo próprio no codex e não muda este.

**Ver também:** Etapa, Tipo, Pedido, Insight, Objetivo do plano, Aprovação, Porte.

## Etapa

**O que é:** um passo de um workflow, com quem o faz e o que sai dele.

- **Regras:**
  - Cada etapa diz quem a faz — Claude, o usuário ou os dois —, o que entra, o que sai e os gates de
    entrada e de saída.
  - Algumas etapas são aprovações.
  - O DC é o método que este codex descreve. O codex diz o que vale em cada etapa; o passo a passo
    de cada uma fica fora dele.

**Ver também:** Workflow, Aprovação, Usuário, Claude.

## Decode

**O que é:** a etapa P1 do workflow de produto, em que Claude entende o pedido e propõe uma solução
conceitual.

- **Quem faz:** Claude, nos papéis de PM, Designer e Tech Lead.
- **O que entra:** o pedido, o tipo e o objetivo do plano.
- **O que sai:** a proposta, escrita para o usuário.
- **Gate de saída:** a proposta só vai à aprovação (P2) se passa nos dois gates. Se um falha, Claude
  refaz a proposta ou propõe ao usuário encerrar o plano.
  - A, necessidade real: o problema é de alguém agora, e a hipótese tem sinal mensurável. O pedido
    explícito do usuário conta como evidência de que o problema existe.
  - B, mínimo viável: é a menor versão que resolve, com o que fica de fora declarado.
- **Regras:**
  - A proposta tem o tamanho do pedido: num pedido pequeno, hipótese, MVP e riscos cabem numa linha
    cada.
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
- **O que sai:** o plano técnico.
- **Gate de saída:** o plano técnico só vai à aprovação (P4) com porte, com a independência
  declarada, sem decisão em aberto e citando só recursos do projeto que existem.
- **Regras:**
  - Escreve as histórias, com os critérios de aceite, apoiada em INVEST e em User Story Mapping.
  - Refina a viabilidade técnica, a compatibilidade, a infraestrutura e os erros, e registra no plano
    técnico as decisões e os riscos técnicos.
  - Fecha cada decisão em aberto, ou a declara fora de escopo.
  - Abre cada fonte técnica da proposta e confere que existe e serve.
  - Quando o porte diverge do apetite da proposta, mostra a diferença ao usuário na aprovação (P4).
  - Quebra o trabalho em tarefas e define o porte.

**Ver também:** Plano técnico, História, Critério de aceite, Tarefa, Unidade, Porte, Independência
entre planos, Tabela de recursos do plano, Proposta, Referência de produto, Papel, Aprovação.

## Derive

**O que é:** a etapa P5 do workflow de produto, que prepara cada unidade para ser executada sem o
histórico da conversa; só existe no médio e no grande.

- **Quem faz:** Claude.
- **O que entra:** o plano técnico aprovado.
- **O que sai:** cada unidade pronta para o code, e o handoff do plano.
- **Gate de saída:** cada unidade cumpre a Definition of Ready, e o usuário aprova as unidades
  derivadas.
- **Regras:**
  - Dá a cada unidade o que a Definition of Ready pede.
  - Declara em cada unidade o que ela espera das anteriores: nomes, contratos e arquivos.
  - Confere se os recursos do projeto citados ainda existem.

**Ver também:** Unidade, Definition of Ready, Cold-start, Handoff, Lacuna, Padrão de código,
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
  - No médio e no grande, cada unidade roda na sua sessão nova, na ordem do handoff, e a próxima só
    começa depois da aprovação da anterior.
  - Se a entrega anterior divergiu do que a unidade espera, a unidade é ajustada antes de rodar; o
    ajuste que muda o critério ou o escopo segue a Lacuna.
  - Usa os recursos do projeto, o padrão de código e as guidelines dos caminhos que toca.
  - Quando a unidade e o código divergem, o critério de aceite manda: Claude entrega pelo critério,
    registra a divergência no relatório da entrega e nunca reduz o escopo em silêncio.
  - Se o critério não se cumpre com o que a unidade ou a tarefa diz, ela é insuficiente e vira
    lacuna.
  - Ação irreversível ou fora do repositório, como mudar um banco remoto ou publicar, pede o sim do
    usuário na hora, mesmo com o plano aprovado.
  - Achado fora do escopo não entra no plano: vira um pedido novo ou uma entrada no huddle.

**Ver também:** Entrega, Critério de aceite, Teste, Unidade, Tarefa, Handoff, Cold-start, Lacuna,
Padrão de código, Recurso do projeto, Guideline, Huddle, Aprovação.

## Setup

**O que é:** o primeiro uso do DC num projeto, em que o projeto ganha os seus princípios, guidelines
e guardrails.

- **Quem faz:** Claude propõe; o usuário aprova cada escrita.
- **O que entra:** um projeto que ainda não fez o setup, e o objetivo do projeto, que o usuário
  declara.
- **O que sai, nesta ordem:**
  1. o huddle iniciado, que recebe o que surgir no resto do setup;
  2. os princípios: o primeiro tirado do objetivo do projeto, os demais do que o usuário diz que
     nunca pode ser violado;
  3. a foundation, com o padrão de código e o mapa de recursos do projeto, e a permissão de uso de
     cada recurso que o DC pode chamar;
  4. as guidelines, que podem nomear os recursos já mapeados;
  5. os guardrails.
- **Regras:**
  - É proposto quando falta, e cada escrita no projeto pede o sim do usuário, uma sugestão por vez.
  - Nada do que grava no projeto repete ou contradiz o codex, e o codex não é copiado para o projeto.
  - Nunca escreve nas instruções que o time mantém, e nada do que grava repete o que elas já dizem.
    Os princípios ficam num lugar próprio, que vale em toda sessão.

**Ver também:** Rethink, Princípio, Guideline, Guardrail, Foundation, Padrão de código, Mapa de
recursos do projeto, Recurso do projeto, Huddle, Invariante, Restrição fundamental.

## Rethink

**O que é:** a revisão dos princípios, das guidelines e dos guardrails do projeto depois de uma
mudança de rumo.

- **Quem faz:** Claude propõe; o usuário aprova cada escrita.
- **O que entra:** um projeto com o setup feito e uma mudança de rumo que o usuário declara: um
  objetivo, uma tecnologia ou uma forma de trabalhar que deixa de valer.
- **O que sai:** cada item mantido, editado, arquivado ou criado; a foundation e o mapa de recursos
  do projeto atualizados; os planos abertos que citam um item retirado, listados para ajuste.
- **Regras:**
  - Princípios, guidelines e guardrails só mudam por três portas: o setup, o rethink e um plano do
    tipo `rule`. O huddle propõe a mudança, e uma dessas portas a grava.
  - Só o rethink inclui um recurso no mapa de recursos depois do setup, ou o retira dele.
  - O rethink revê o conjunto depois de uma mudança de rumo; um plano do tipo `rule` muda um item.
  - Editar é mudar o texto ou o caminho de um item que continua valendo; o que deixa de valer é
    arquivado. Arquivar nunca apaga: o item guarda o motivo, e o nome fica reservado.
  - As instruções do time que contradizem a mudança são apontadas ao usuário, que as edita.
  - Valem as mesmas regras do setup para escrever no projeto.

**Ver também:** Setup, Princípio, Guideline, Guardrail, Foundation, Mapa de recursos do projeto,
Recurso do projeto, Huddle, Tipo.
