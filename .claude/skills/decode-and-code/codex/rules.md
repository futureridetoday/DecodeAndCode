---
# about
name: codex-rules
type: knowledge
project: ""
description: Codex do decode-and-code, capítulo das regras — tipo, porte, aprovação, teste, prontidão da unidade, independência e organização dos planos, com quando cada regra vale, o que exige e o que acontece quando falha
tags: [codex, regra]

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

# Regras

## Tipo

**O que é:** a classificação do plano que escolhe o workflow que ele segue.

- **Quando vale:** na entrada, antes do decode.
- **O que exige:**
  - O tipo sai de uma lista que o DC mantém; o codex não a repete.
  - Cada tipo segue o workflow de produto, a menos que tenha workflow próprio.
- **Quando falha:** o usuário corrige o tipo declarado, e o plano segue o workflow do tipo corrigido.

**Ver também:** Workflow, Claude, Usuário, Objetivo do plano, Plano.

## Porte

**O que é:** o tamanho do plano: pequeno, médio ou grande, e só esses três.

- **Quando vale:** em todo plano; define-se na revisão.
- **O que exige:**
  - Pequeno: lista de tarefas, sem derive.
  - Médio: 1 unidade, com derive.
  - Grande: 2 ou mais unidades, com derive e teste do plano inteiro.
- **Quando falha:** plano sem porte não é aprovado.

**Ver também:** Revisão, Derive, Code, Tarefa, Unidade, Handoff, Teste do plano inteiro, Plano
técnico.

## Aprovação

**O que é:** o momento em que o usuário aceita o resultado de uma etapa do workflow.

- **Quando vale:** no workflow de produto, nesta ordem:
  1. A proposta, no fim do decode (P2).
  2. O plano técnico, no fim da revisão (P4), quando o plano recebe número.
  3. As unidades derivadas, no fim do derive.
  4. Cada entrega, no code, junto com o teste (P7).
  5. A aprovação final, que fecha o plano. No grande, vem depois do teste do plano inteiro (P8). No
     pequeno, vem depois do teste da entrega e é a única aprovação depois do code. No médio, a
     aprovação da única entrega é também a aprovação final.
- **O que exige:** quem aprova é sempre o usuário.
- **Quando falha:** sem a aprovação, a etapa seguinte não começa.

**Ver também:** Usuário, Workflow, Etapa, Proposta, Plano técnico, Unidade, Entrega, Teste, Teste do
plano inteiro, Plano.

## Critério de aceite

**O que é:** a frase verificável que diz quando a entrega está pronta.

- **Quando vale:** em toda entrega, declarado antes de começar.
- **O que exige:**
  - O critério vem junto com o teste que o verifica: o critério diz o que precisa ser verdade, e o
    teste é o que confere.
  - O teste da entrega confere o critério antes da aprovação (P7).
  - Na história, são os critérios de aceite.
- **Quando falha:** sem critério e sem o teste que o verifica, o code não começa.

**Ver também:** Entrega, Teste, História, Code, Unidade, Aprovação.

## Teste

**O que é:** a verificação de que uma entrega ou o plano inteiro funciona.

- **Quando vale:** antes da aprovação de cada entrega (P7) e, no grande, no teste do plano inteiro
  (P8).
- **O que exige:**
  - Claude ou o usuário o faz.
  - O teste da entrega confere o critério de aceite.
  - O estado de uma unidade é derivado do teste, nunca editado à mão.
- **Quando falha:** a unidade não fecha, e a entrega não vai à aprovação.

**Ver também:** Critério de aceite, Entrega, Unidade, Teste do plano inteiro, Aprovação, Claude,
Usuário.

## Teste do plano inteiro

**O que é:** o teste P8, feito sobre o plano como um todo.

- **Quando vale:** só no grande, depois que todas as unidades forem concluídas. No pequeno e no
  médio, o teste da entrega já cobre o plano inteiro.
- **O que exige:** Claude ou o usuário testa o plano inteiro antes da aprovação final.

**Ver também:** Teste, Porte, Aprovação, Entrega.

## Definition of Ready

**O que é:** o estado em que a unidade está pronta para ser desenvolvida, como a história no produto
digital.

- **Quando vale:** no derive, para cada unidade.
- **O que exige:** a unidade tem o que o derive lhe dá e basta sozinha.

**Ver também:** Derive, Unidade, História, Cold-start, Paralelo com produto digital.

## Cold-start

**O que é:** a propriedade da unidade de bastar sozinha, rodando sem o histórico da conversa.

- **Quando vale:** em toda unidade, no médio e no grande.
- **O que exige:** não há memória de execução entre unidades; o que a unidade precisa está nela.
- **Quando falha:** a unidade insuficiente vira lacuna.

**Ver também:** Unidade, Derive, Code, Definition of Ready, Handoff, Lacuna.

## Lacuna

**O que é:** o registro, no plano, de que uma unidade se mostrou insuficiente na execução.

- **Quando vale:** quando a execução mostra que faltava algo na unidade.
- **O que exige:**
  - O ajuste é feito na unidade, não deixado a cargo de quem a executa.
  - A lacuna fica no plano, marcada `L-XX`, com o que faltou e o ajuste feito.

**Ver também:** Unidade, Plano, Code, Derive, Cold-start.

## Independência entre planos

**O que é:** a condição de que um plano não dependa de outro.

- **Quando vale:** na revisão.
- **O que exige:** todo plano diz por que é um plano e não dois.
- **Quando falha:** a revisão barra o plano que depende de outro, e dois planos concorrentes no mesmo
  alvo.

**Ver também:** Revisão, Plano.

## Numeração e nomenclatura

**O que é:** como planos e unidades são nomeados e numerados, para que cada um seja rastreável.

- **Quando vale:** em todo plano e em toda unidade.
- **O que exige:**
  - O plano nasce com um nome semântico, em inglês e em kebab-case, no formato
    `<intenção>-<alvo>[-<qualificador>]`. O nome é identificador, e a prosa do plano segue em pt-BR.
    O nome não declara o tipo.
  - Na aprovação, o plano recebe um número de 4 dígitos, sequencial em todo o projeto, atribuído uma
    vez e nunca reaproveitado. Passa a se chamar `NNNN-nome`, e o nome não muda mais.
  - Cada unidade tem um identificador `NNNN-nn`, formado pelo número do plano e pela ordem dela no
    plano. Ele nunca muda, e é ele que o código, os testes e as outras unidades citam. O nome do
    arquivo da unidade, `nn-slug`, pode mudar sem quebrar nenhuma referência.
  - Os planos aprovados ficam num índice, e a situação de cada um é derivada, nunca digitada.

**Ver também:** Plano, Unidade, Tipo, Aprovação, Raiz dos planos, Teste.

## Raiz dos planos

**O que é:** o diretório `<plan_root>/`, onde ficam todos os planos juntos.

- **Quando vale:** em todo plano.
- **O que exige:**
  - Não há pasta por parte do sistema: quem busca o plano é Claude, e a documentação não precisa
    espelhar a arquitetura.
  - O pequeno é um arquivo; o médio e o grande são uma pasta com o plano e as unidades.
  - Em `<plan_root>/system/` moram a foundation e o huddle.
  - Planos, unidades, huddle e histórico são registro versionado, não instrução carregada.

**Ver também:** Plano, Unidade, Foundation, Huddle, Plano anterior ao redesign.

## Plano anterior ao redesign

**O que é:** o plano sem versão do formato.

- **Quando vale:** em todo plano que não declara a versão do formato.
- **O que exige:**
  - É lido pela regra anterior e fica onde está, mesmo dentro de uma pasta por parte do sistema.
  - Só é atualizado quando o usuário quer revisá-lo, derivá-lo ou codá-lo.
  - Continua com o tipo `norma`, que no formato novo se chama `rule`.
  - Os links de planos fechados para a regra anterior ficam como registro.

**Ver também:** Plano, Raiz dos planos, Tipo, Usuário, Revisão, Derive, Code.
