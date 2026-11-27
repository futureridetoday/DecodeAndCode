---
# about
name: codex-product-references
type: knowledge
project: ""
description: Codex do decode-and-code, capítulo das referências de produto — as fontes de criação de produto digital em que o decode e a revisão se apoiam, com o que cada uma traz ao DC e em que etapa entra
tags: [codex, referencia-de-produto]

# history
author: Bortoli
created: 2026-11-26
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

# Referências de produto

## Referência de produto

**O que é:** uma referência consagrada de criação de produto digital em que o decode e a revisão se
apoiam.

- **Fonte:** as referências que não têm seção própria:
  - Jobs to Be Done, de Clayton Christensen (*Competing Against Luck*);
  - Design Thinking, de Tim Brown (*Change by Design*), e o Double Diamond, do Design Council;
  - Lean Startup, de Eric Ries (*The Lean Startup*);
  - Shape Up, de Ryan Singer (*Shape Up*);
  - o formato de história, de Mike Cohn (*User Stories Applied*);
  - INVEST, de Bill Wake (*INVEST in Good Stories, and SMART Tasks*);
  - User Story Mapping, de Jeff Patton (*User Story Mapping*).
- **O que traz:** no decode, as perguntas do mindset de produto; na revisão, a forma, a qualidade e
  a ordem das histórias.
- **Em que etapa entra:** no decode, JTBD, Design Thinking e Double Diamond, Lean Startup, os quatro
  riscos e Shape Up; na revisão, o formato de história, INVEST e User Story Mapping.

**Ver também:** Mindset de produto, Os quatro riscos, Hipótese, MVP, Fluxo de decodificação,
Decode, Revisão, Proposta, História.

## Mindset de produto

**O que é:** o modo de pensar com que o DC decodifica qualquer pedido: começar pelo problema e por
quem o tem, buscar o resultado e não a funcionalidade, e entregar o mínimo que gera valor e se
consegue verificar.

- **Fonte:** as referências de produto; "resultado e não funcionalidade" é de Marty Cagan
  (*Inspired*).
- **O que traz:** as perguntas que o decode sempre faz:
  - De quem é o problema, e o que a pessoa quer realizar? (Jobs to Be Done)
  - O problema foi entendido antes de escolher a solução? (Double Diamond)
  - Qual é a hipótese, e como saberemos que deu certo? (Lean Startup)
  - Valor, usabilidade, viabilidade técnica e viabilidade de negócio estão cobertos? (os quatro
    riscos)
  - Quanto vale gastar, e o que fica de fora? (Shape Up)
  - Dá para resolver sem código, e qual é a menor versão? (fluxo de decodificação)
- **Em que etapa entra:** no decode. Vale também para recursos que não são produto digital, e então
  "quem usa" é quem usa o recurso.

**Ver também:** Referência de produto, Os quatro riscos, Hipótese, MVP, Fluxo de decodificação,
Decode, Paralelo com produto digital.

## Fluxo de decodificação

**O que é:** os três estágios que o DC aplica a uma decisão antes de ela virar plano: Clarificar,
Evitar e Reduzir.

- **Fonte:** o próprio método.
- **O que traz:**
  - Clarificar pergunta qual é o problema, a métrica e o beneficiário.
  - Evitar pergunta se dá para resolver sem código.
  - Reduzir pergunta qual é a menor versão que resolve 80% do problema.
- **Em que etapa entra:** é a base do decode, e a semente das referências de produto.

**Ver também:** Decode, Referência de produto, Hipótese, MVP, Mindset de produto.

## Os quatro riscos

**O que é:** validar valor, usabilidade, viabilidade técnica e viabilidade de negócio.

- **Fonte:** Marty Cagan (*Inspired*).
- **O que traz:** a pauta do trio PM, Designer e Tech Lead. Segurança e privacidade entram como
  viabilidade técnica e de negócio.
- **Em que etapa entra:** no decode.

**Ver também:** Papel, Decode, Hipótese, Referência de produto.

## Hipótese

**O que é:** uma suposição explícita sobre o efeito de uma mudança, escrita de forma que possa se
provar errada, com o sinal que vai confirmá-la ou refutá-la.

- **Fonte:** Barry O'Reilly (*Hypothesis-Driven Development*), para o modelo; Eric Ries (*The Lean
  Startup*), para as hipóteses de partida e o ciclo.
- **O que traz:**
  - O modelo: "Acreditamos que <mudança>, para <quem>, vai resultar em <resultado>. Teremos
    confiança para seguir quando <sinal mensurável>, até <prazo ou ponto de verificação>."
  - Cada hipótese tem um resultado só, e o sinal é definido antes de construir. O sinal pode vir de
    uma consulta ao que o sistema já guarda ou de uma observação do usuário, com data; não exige
    instrumentação nova.
  - Se nenhum resultado pode contradizê-la, não é hipótese.
  - Há duas hipóteses de partida: a de valor, que é o primeiro dos quatro riscos, e a de crescimento.
    O ciclo é construir, medir e aprender.
  - Para um recurso que não é produto digital, o "quem" é quem usa o recurso.
  - Exemplo: "Acreditamos que executar o médio e o grande numa sessão nova, para quem usa o DC, vai
    reduzir o consumo de tokens por unidade. Teremos confiança para seguir quando o consumo médio
    cair nos próximos 5 planos."
- **Em que etapa entra:** no decode, declarada na proposta; o sinal se liga à métrica que o
  Clarificar pergunta. Um ponto de verificação depois de o plano fechar fica no huddle.

**Ver também:** MVP, Proposta, Decode, Os quatro riscos, Fluxo de decodificação, Mindset de produto,
Huddle.

## MVP

**O que é:** a menor versão que testa uma hipótese com o mínimo de esforço, feita para aprender e
não para ser o produto final.

- **Fonte:** Eric Ries (*The Lean Startup*).
- **O que traz:**
  - Sem hipótese, não é MVP, é só uma versão menor: o MVP é o mínimo que produz o sinal que ela
    define.
  - O mínimo se mede pelo aprendizado, não pelo escopo: o MVP precisa ser bom o bastante para gerar
    um sinal real.
  - Formas comuns: protótipo; concierge, o serviço feito à mão; Mágico de Oz, que parece automático
    mas é manual; teste de demanda.
  - Depois de medir: perseverar, pivotar ou parar.
  - Não é o Reduzir, que mira o escopo, nem o porte pequeno, que é o tamanho do plano.
- **Em que etapa entra:** no decode, declarado na proposta junto com a hipótese. O sinal se mede no
  ponto de verificação que a hipótese declara, que pode vir depois de o plano fechar: a aprovação da
  entrega confere o critério de aceite, não a hipótese.

**Ver também:** Hipótese, Proposta, Decode, Fluxo de decodificação, Porte, Critério de aceite,
Aprovação.

## Paralelo com produto digital

**O que é:** a correspondência entre o workflow do DC e o processo de criação de produto digital.

- **Fonte:** o processo de criação de produto digital.
- **O que traz:**
  - Stakeholders e squad escrevem o pedido (entrada); PM, Designer e Tech Lead propõem a solução
    (decode); a proposta é aprovada (aprovação); PM e Tech Lead escrevem histórias, refinam e
    quebram em tarefas (revisão); a história fica pronta (derive, Definition of Ready); o
    desenvolvimento (code); a demonstração e o aceite da história (teste e aprovação da entrega).
  - O plano corresponde à proposta, a unidade à história, e a tarefa continua tarefa.
  - Orienta, mas não é regra.
  - O DC também serve para criar recursos que não são produto digital.
- **Em que etapa entra:** em nenhuma como regra; orienta a leitura do workflow inteiro.

**Ver também:** Workflow, Papel, Pedido, Proposta, História, Unidade, Tarefa, Definition of Ready,
Mindset de produto.
