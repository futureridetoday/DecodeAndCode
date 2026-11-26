---
# about
name: codex-artifacts
type: knowledge
project: ""
description: Codex do decode-and-code, capítulo dos artefatos — o pedido, o plano e as suas partes, a entrega, o handoff, a foundation e os registros de recursos, com o que contêm, quem os cria e as regras que valem para eles
tags: [codex, artefato]

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

# Artefatos

## Pedido

**O que é:** o que o usuário traz ao DC e que dá início a um plano; é o objeto que o DC decodifica.

- **Contém:** o que o usuário quer, nas palavras dele, juntado num pedido único quando chega em
  blocos de texto.
- **Quem cria:** o usuário, na entrada.
- **Regras:** decodificar o pedido é entender, validar e planejar.

**Ver também:** Insight, Usuário, Workflow, Tipo, Objetivo do plano, Decode, Paralelo com produto
digital.

## Objetivo do plano

**O que é:** o que o plano quer atingir, claro para o usuário e para Claude.

- **Contém:** uma frase.
- **Quem cria:** Claude a propõe ao identificar o tipo, na entrada; o usuário a confirma.
- **Regras:** é do plano, e não se confunde com o objetivo do DC, que é decodificar o pedido.

**Ver também:** Pedido, Tipo, Plano, Workflow.

## Plano

**O que é:** o registro do que vai ser feito para atender a um pedido.

- **Contém:** o tipo, o objetivo, a versão do formato, a parte do sistema a que se refere, a tabela
  de recursos do plano e, conforme o porte, tarefas ou unidades.
- **Quem cria:** Claude, a partir do pedido. No workflow de produto, começa como proposta e vira
  plano técnico na revisão.
- **Regras:**
  - O tipo escolhe o workflow que o plano segue.
  - O plano recebe número na aprovação do plano técnico (P4).
  - Todo plano novo declara a versão do formato.
  - Todo plano fecha com a aprovação final.

**Ver também:** Pedido, Tipo, Objetivo do plano, Porte, Workflow, Proposta, Plano técnico, Tarefa,
Unidade, Tabela de recursos do plano, Aprovação, Numeração e nomenclatura, Raiz dos planos, Plano
anterior ao redesign.

## Proposta

**O que é:** a solução conceitual para o pedido, escrita para o usuário.

- **Contém:** o problema e de quem ele é, a hipótese e o MVP, a solução conceitual com as referências
  técnicas, o apetite, os riscos e o que fica de fora, como no Shape Up.
- **Quem cria:** Claude, no decode (P1).
- **Regras:**
  - É escrita para o usuário, não para quem executa.
  - O usuário a aprova (P2), e só então vem a revisão, que a transforma em plano técnico.

**Ver também:** Decode, Revisão, Plano técnico, Hipótese, MVP, Os quatro riscos, Referência de
produto, Aprovação.

## Plano técnico

**O que é:** o plano pronto para ser executado, com tarefas ou unidades conforme o porte.

- **Contém:** as histórias com os critérios de aceite, o porte, e as tarefas ou unidades que o porte
  pede.
- **Quem cria:** Claude, na revisão (P3), a partir da proposta aprovada.
- **Regras:** o usuário o aprova em P4; o derive, no médio e no grande, só vem depois.

**Ver também:** Proposta, Revisão, Derive, Porte, História, Critério de aceite, Tarefa, Unidade,
Aprovação.

## Tarefa

**O que é:** a menor ação do trabalho, que o code executa de uma vez e cujo resultado se consegue
conferir.

- **Contém:** uma ação e o resultado que a confere.
- **Quem cria:** Claude, na revisão, ao quebrar o trabalho.
- **Regras:** no pequeno, as tarefas compõem o plano; no médio e no grande, compõem as unidades.

**Ver também:** Unidade, Plano técnico, Revisão, Code, Porte.

## Unidade

**O que é:** uma lista de tarefas que, no fim, produz uma entrega.

- **Contém:** as tarefas necessárias para produzir a entrega, sem limite de número, e o que o derive
  lhe dá para bastar sozinha.
- **Quem cria:** Claude; a revisão a define no plano técnico e o derive a prepara (P5).
- **Regras:**
  - Só existe no médio e no grande.
  - Corresponde a uma história.
  - Só começa com o critério de aceite declarado, e só fecha com o teste e a aprovação da entrega.
  - Basta sozinha e roda sem o histórico da conversa.

**Ver também:** Tarefa, Entrega, História, Porte, Derive, Code, Critério de aceite, Teste,
Aprovação, Cold-start, Definition of Ready, Handoff, Lacuna.

## História

**O que é:** a descrição de uma mudança do ponto de vista de quem se beneficia dela, com o critério
que diz quando está pronta.

- **Contém:** "Como <quem>, quero <o quê>, para <por quê>", com os critérios de aceite.
- **Quem cria:** Claude, na revisão (P3), no plano técnico.
- **Regras:**
  - Segue INVEST: independente, negociável, valiosa, estimável, pequena e testável.
  - As histórias se ordenam pelo caminho de quem usa e se cortam em incrementos que entregam valor,
    como no User Story Mapping.
  - Quando o recurso não é produto digital, o "quem" é quem usa o recurso.
  - O aceite da história é o teste e a aprovação da unidade que corresponde a ela.

**Ver também:** Plano técnico, Revisão, Unidade, Critério de aceite, Definition of Ready, Teste,
Aprovação, Referência de produto.

## Entrega

**O que é:** o pacote que uma unidade produz: concreto, documentado, que agrega valor ao todo e que
se consegue medir e testar, por Claude ou pelo usuário.

- **Contém:** o que a unidade produz, com o critério de aceite que diz quando está pronta.
- **Quem cria:** Claude, no code (P6).
- **Regras:**
  - Cada unidade tem uma entrega.
  - É testada e aprovada pelo usuário antes de a próxima unidade começar (P7).
  - No pequeno, que não tem unidade, a entrega é o resultado das tarefas, aprovado na aprovação
    final.

**Ver também:** Unidade, Tarefa, Critério de aceite, Teste, Aprovação, Code, Tabela de recursos do
plano.

## Handoff

**O que é:** o que leva o plano médio ou grande à sessão nova e conduz a execução das unidades.

- **Contém:** o necessário para a sessão nova executar as unidades na ordem, sem o histórico da
  conversa.
- **Quem cria:** Claude, no derive.
- **Regras:** vale no médio e no grande.

**Ver também:** Derive, Code, Unidade, Porte, Cold-start.

## Tabela de recursos do plano

**O que é:** a tabela no plano que registra, pelo nome, os recursos do projeto que o plano usa.

- **Contém:** para cada recurso, o nome pelo qual é invocado, o tipo e onde entra na entrega; nunca
  conteúdo, linha ou versão.
- **Quem cria:** Claude, no decode, a partir do mapa de recursos do projeto.
- **Regras:** todo recurso citado na tabela precisa existir no projeto.

**Ver também:** Plano, Recurso do projeto, Mapa de recursos do projeto, Entrega, Decode, Revisão,
Derive, Code.

## Foundation

**O que é:** o que o projeto registra para o DC trabalhar como alguém do time e que não tem outro
lugar.

- **Contém:** o padrão de código e o mapa de recursos do projeto.
- **Quem cria:** o setup a escreve; o rethink e os planos a mudam, sempre com o sim do usuário.
- **Regras:**
  - O codex diz como o DC trabalha; a foundation diz como é este projeto.
  - Não repete o que já tem lugar: princípios, guidelines, guardrails, decisões, planos e huddle
    continuam onde estão, e a foundation no máximo os menciona.
  - Não é instrução carregada: o decode e o derive a leem quando precisam.

**Ver também:** Padrão de código, Mapa de recursos do projeto, Setup, Rethink, Decode, Derive, Raiz
dos planos, Restrição fundamental, Invariante.

## Mapa de recursos do projeto

**O que é:** o índice, guardado na foundation, dos recursos do projeto que o DC pode usar.

- **Contém:** para cada recurso, o nome pelo qual é invocado; o tipo; a etapa em que entra (decode,
  revisão ou code); se só o usuário pode chamá-lo; se é do projeto ou pessoal; e se tem permissão de
  uso registrada.
- **Quem cria:** o setup o escreve e o rethink o atualiza, com o sim do usuário.
- **Regras:**
  - Nunca guarda conteúdo, linha nem versão: o recurso invocado pelo nome entra na versão atual.
  - É dele que o plano tira a sua tabela de recursos.

**Ver também:** Foundation, Recurso do projeto, Tabela de recursos do plano, Setup, Rethink.
