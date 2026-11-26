---
# about
name: codex-concepts
type: knowledge
project: ""
description: Codex do decode-and-code, capítulo dos conceitos — os atores, o que é do projeto e o espaço de conversa, com o que cada um é para o DC e onde aparece no trabalho
tags: [codex, conceito]

# history
author: Bortoli
created: 2026-11-26
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

# Conceitos

## Usuário

**O que é:** a pessoa que usa o DC, um dos dois atores do workflow.

- **Para o DC:**
  - Traz o pedido, os blocos de texto ou o insight, e pode corrigir o tipo que Claude declara.
  - Dá as aprovações do workflow.
  - Testa, ou deixa o teste com Claude.
  - Dá o sim a cada escrita do DC no projeto; esse sim não é aprovação do workflow.
  - Não altera o codex nem liga ou desliga módulo.
- **Onde aparece:** na entrada, em toda aprovação, no teste, no setup e no rethink.

**Ver também:** Claude, Pedido, Insight, Tipo, Aprovação, Teste, Setup, Rethink.

## Claude

**O que é:** o outro ator do workflow, que decodifica, revisa, deriva e coda.

- **Para o DC:**
  - Identifica o tipo do plano.
  - Exerce os papéis que cada etapa pede.
  - Pode testar no lugar do usuário.
  - Executa as unidades em cold-start.
  - O DC é otimizado para Claude.
- **Onde aparece:** no decode, na revisão, no derive, no code e no teste.

**Ver também:** Usuário, Papel, Tipo, Decode, Revisão, Derive, Code, Teste, Cold-start.

## Papel

**O que é:** o chapéu que Claude veste numa etapa: PM, Designer ou Tech Lead.

- **Onde aparece:** no decode, Claude atua nos três papéis; na revisão, como PM e Tech Lead.

**Ver também:** Claude, Decode, Revisão, Os quatro riscos, Paralelo com produto digital.

## Insight

**O que é:** uma forma de entrada que traz algo para discutir, sem ser ainda um pedido.

- **Para o DC:** o DC conversa sobre o insight e só abre plano se ele virar um pedido; a conversa
  pode terminar sem plano.
- **Onde aparece:** na entrada, comum a todo workflow.

**Ver também:** Pedido, Workflow, Tipo.

## Princípio

**O que é:** o north star do projeto, a direção que aponta para o objetivo final dele e pela qual se
julga cada decisão.

- **Para o DC:**
  - O primeiro princípio sai do objetivo do projeto, com um enunciado, o objetivo numa frase curta,
    e um teste, a condição verificável que uma mudança mostra para se aproximar dele.
  - São no máximo 5 princípios, e o ideal é 3.
  - Vale desde o início de toda sessão.
  - Se uma equipe competente pode deixar o item de lado e ainda fazer bom trabalho, ele tende a ser
    guideline, não princípio. É uma orientação, e o usuário escolhe se a segue.
  - É do projeto, não do codex.
- **Onde aparece:** o setup o cria, o rethink o revisa e o decode o usa.

**Ver também:** Guideline, Guardrail, Setup, Rethink, Decode.

## Guideline

**O que é:** uma diretriz técnica do projeto, que vale para os arquivos que casam com um padrão de
caminho.

- **Para o DC:**
  - É do projeto, não do codex.
  - Uma guideline liga caminhos do projeto aos recursos do projeto que valem para eles.
  - Uma arquitetura que o projeto adota, como a Clean Architecture, entra como guideline.
- **Onde aparece:** o setup a cria e o rethink a revisa; o decode a usa, o derive a cita na unidade,
  e o code a recebe nos caminhos que toca.

**Ver também:** Princípio, Guardrail, Recurso do projeto, Unidade, Setup, Rethink, Decode, Derive,
Code.

## Guardrail

**O que é:** uma regra do projeto que não pode depender de Claude lembrar, e por isso é imposta.

- **Para o DC:**
  - Bloqueia a ação, qualquer que seja a decisão de Claude.
  - A regra é do projeto; o DC só a impõe.
- **Onde aparece:** o setup o cria, o rethink o revisa e o decode o usa.

**Ver também:** Princípio, Guideline, Setup, Rethink, Decode.

## Padrão de código

**O que é:** o estilo de código do time do projeto.

- **Para o DC:** faz parte da foundation.
- **Onde aparece:** o derive garante que cada unidade o siga.

**Ver também:** Foundation, Derive, Unidade.

## Recurso do projeto

**O que é:** o que o projeto já tem para Claude usar, como skills, commands, servidores MCP e as
instruções do projeto.

- **Para o DC:**
  - É do projeto, fora do codex e da foundation, que só o mapeia.
  - O DC chama o recurso pelo nome e nunca copia o conteúdo dele, porque o recurso continua
    evoluindo no projeto.
  - Cada plano registra, pelo nome, os recursos que usa.
- **Onde aparece:** no decode e no code, que o usam; o rethink é a única etapa que o cria ou remove.

**Ver também:** Foundation, Mapa de recursos do projeto, Tabela de recursos do plano, Guideline,
Decode, Code, Rethink.

## Huddle

**O que é:** o espaço de conversa entre Claude e o usuário para os dois aprenderem juntos sobre o
projeto.

- **Para o DC:**
  - Há um huddle por pessoa, identificada pelo nome no git. É registro, e nada nele vale como regra.
  - Quando o huddle está atrasado, o usuário é avisado no início da sessão.
  - A pauta traz o que aconteceu desde o último huddle e as entradas abertas.
  - Claude ou o usuário registra uma entrada, com um tipo de um vocabulário fechado.
  - As entradas são conversadas uma por vez. Cada uma termina em decisão, guideline, guardrail,
    feedback ao método ou descarte com motivo, ou continua aberta.
  - O que se aprende sai do huddle para o lugar certo.
- **Onde aparece:** o setup o inicia; mora na raiz dos planos.

**Ver também:** Usuário, Claude, Guideline, Guardrail, Registro de uso, Setup, Raiz dos planos.

## Registro de uso

**O que é:** o log de uso do DC e o feedback ao método, que fazem o codex evoluir por evidência, não
por reescrita.

- **Para o DC:**
  - O registro fica no projeto.
  - Uma entrada `E-XX` é um erro registrado; uma entrada `M-XX` é um feedback sobre o próprio
    método, escrito de forma genérica e aprovado pelo usuário.
  - O feedback ao método chega a quem mantém o plugin, o único que altera o codex.
- **Onde aparece:** no huddle, que leva o que se aprende ao feedback ao método.

**Ver também:** Huddle, Usuário.
