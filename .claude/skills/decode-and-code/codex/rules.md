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

# Regras

## Tipo

**O que é:** a classificação do plano que escolhe o workflow que ele segue e o que a revisão e o
aceite da entrega exigem.

- **Quando vale:** na entrada, antes do decode.
- **O que exige:** o tipo é um destes, e cada um muda o que se confere:

  | Tipo | O trabalho | O aceite da entrega | A revisão confere |
  |---|---|---|---|
  | `fix` | corrigir um defeito | o teste que reproduz o defeito, vermelho antes e verde depois | o diagnóstico reproduz o defeito |
  | `feature` | capacidade nova | o teste de cada entrega, que verifica os critérios das histórias | a independência, com peso |
  | `remove` | tirar o que não se usa | os testes passam, e o código diminui | a evidência de que não se usa |
  | `refactor` | mudar a forma sem mudar o comportamento | os testes passam sem alterar teste existente | a dor medida que justifica |
  | `rule` | mudar princípio, guideline ou guardrail | a aprovação do usuário | os itens que mudam; nenhum código |
  | `chore` | produzir um artefato de apoio | o artefato existe e funciona | o artefato e como conferi-lo |
  | `spike` | responder a uma pergunta | a resposta registrada, sem código de produção; nunca grande | a pergunta e o destino da resposta |

  Um defeito é um comportamento especificado que não se cumpre; o que nunca foi especificado não é
  `fix`. A especificação pode ser implícita: o que o usuário descreve como esperado e o sistema
  claramente deveria fazer. Na dúvida entre `fix` e outro tipo, o plano começa como `fix`, e o
  diagnóstico confirma; nas demais dúvidas, Claude pergunta.
- **Quando falha:** o usuário corrige o tipo declarado; depois da entrada, só uma troca aprovada por
  ele muda o tipo.

**Ver também:** Workflow, Claude, Usuário, Objetivo do plano, Plano, Teste, Aprovação.

## Porte

**O que é:** o tamanho do plano: pequeno, médio ou grande, e só esses três.

- **Quando vale:** em todo plano; define-se na revisão.
- **O que exige:**
  - Pequeno: uma entrega que cabe na mesma sessão, sem perder o contexto; lista de tarefas, sem
    derive. Pode ter mais de uma história.
  - Médio: uma entrega que pede sessão nova; 1 unidade, com derive.
  - Grande: duas ou mais entregas, em sequência; uma unidade por entrega, com derive e teste do plano
    inteiro. A proposta carrega as três seções do grande (*Proposta*) e o lint confere que cada
    `R-NN` tem dono.
  - Primeiro se contam as entregas; depois, se a entrega única cabe na sessão. Na dúvida, vale o
    menor.
- **Quando falha:** plano sem porte não é aprovado.

**Ver também:** Revisão, Derive, Code, Tarefa, Unidade, História, Handoff, Teste do plano inteiro,
Plano técnico.

## Aprovação

**O que é:** o momento em que o usuário aceita o resultado de uma etapa do workflow.

- **Quando vale:** no workflow de produto, nesta ordem:
  1. A proposta, no fim do decode (P2).
  2. O plano técnico, no fim da revisão (P4), quando o plano recebe número.
  3. As unidades derivadas, juntas, no fim do derive.
  4. Cada entrega, no code, junto com o teste (P7).
  5. A aprovação final, que fecha o plano. No grande, vem depois do teste do plano inteiro (P8). No
     pequeno e no médio, é a própria aprovação da única entrega (P7).
- **O que exige:** quem aprova é sempre o usuário.
- **Quando falha:** sem a aprovação, a etapa seguinte não começa. Uma recusa volta à etapa que
  produziu o resultado, com a objeção do usuário como entrada, ou encerra o plano como descartado.

**Ver também:** Usuário, Workflow, Etapa, Proposta, Plano técnico, Unidade, Entrega, Teste, Teste do
plano inteiro, Plano.

## Critério de aceite

**O que é:** a frase verificável que diz quando a entrega está pronta.

- **Quando vale:** em toda entrega, declarado antes de começar.
- **O que exige:**
  - O critério vem junto com o teste que o verifica: o critério diz o que precisa ser verdade, e o
    teste é o que confere.
  - A revisão escreve o critério, na história; o derive declara o teste na unidade; no pequeno, a
    revisão declara os dois.
  - O teste da entrega confere o critério antes da aprovação (P7).
- **Quando falha:** sem critério e sem o teste que o verifica, o code não começa.

**Ver também:** Entrega, Teste, História, Revisão, Derive, Code, Unidade, Aprovação.

## Teste

**O que é:** a verificação de que uma entrega ou o plano inteiro funciona.

- **Quando vale:** antes da aprovação de cada entrega (P7) e, no grande, no teste do plano inteiro
  (P8).
- **O que exige:**
  - Claude ou o usuário o faz; o usuário escolhe, e Claude faz quando ele não escolhe.
  - O teste da entrega confere o critério de aceite e o aceite que o tipo exige. Pode ser a soma dos
    testes das tarefas, quando eles cobrem o critério.
  - Todo número que o relatório afirma é alegação até ser medido: Claude mede ao menos uma afirmação
    por outro caminho e declara qual, e o usuário pode medir outra.
  - Um teste que decide algo falha quando o código que ele prova é desligado; verde sozinho não é
    evidência.
  - A situação de uma unidade — por fazer, em teste, verificada — é derivada do teste, nunca editada
    à mão.
- **Quando falha:** a unidade não fecha, a entrega não vai à aprovação, e o trabalho volta ao code da
  mesma entrega.

**Ver também:** Critério de aceite, Entrega, Unidade, Tipo, Teste do plano inteiro, Aprovação,
Claude, Usuário.

## Teste do plano inteiro

**O que é:** o teste P8, feito sobre o plano como um todo.

- **Quando vale:** só no grande, depois que todas as unidades forem concluídas. No pequeno e no
  médio, o teste da entrega já cobre o plano inteiro.
- **O que exige:** Claude ou o usuário testa o plano inteiro antes da aprovação final, contra um
  critério que o plano técnico declara em `## Teste do plano inteiro`. O critério sai das fases de
  entrega e dos `R-NN` que nenhuma unidade cobre.
- **Quando falha:** o que falhou vira lacuna da unidade que o causa, e o trabalho volta ao code dela.

**Ver também:** Teste, Porte, Aprovação, Entrega, Plano técnico, Lacuna.

## Definition of Ready

**O que é:** o estado em que a unidade está pronta para ser desenvolvida, como a história no produto
digital.

- **Quando vale:** no derive, para cada unidade.
- **O que exige:** a unidade traz, sem depender da conversa:
  - a história que realiza, e o critério de aceite com o teste que o verifica;
  - as tarefas e os arquivos que toca;
  - as guidelines desses caminhos e o padrão de código, citados pelo nome;
  - os recursos do projeto que usa, pelo nome;
  - as decisões e as lacunas do plano que valem para ela;
  - as unidades de que depende, pelo identificador, e o que espera delas.
- **Quando falha:** a unidade não vai à aprovação das unidades derivadas.

**Ver também:** Derive, Unidade, História, Critério de aceite, Cold-start, Guideline, Padrão de
código, Lacuna, Paralelo com produto digital.

## Cold-start

**O que é:** a propriedade da unidade de bastar sozinha, rodando sem o histórico da conversa.

- **Quando vale:** em toda unidade, no médio e no grande.
- **O que exige:** não há memória de execução entre unidades; o que a unidade precisa está nela.
- **Quando falha:** a unidade insuficiente vira lacuna.

**Ver também:** Unidade, Derive, Code, Definition of Ready, Handoff, Lacuna.

## Lacuna

**O que é:** o registro, no plano, de que uma unidade ou uma tarefa se mostrou insuficiente na
execução.

- **Quando vale:** quando a execução mostra que faltava algo na unidade, ou na tarefa do pequeno.
- **O que exige:**
  - Claude para, propõe o ajuste da unidade ou da tarefa, e só segue com a aprovação do usuário.
  - O ajuste é feito na unidade, não deixado a cargo de quem a executa, e chega às unidades
    seguintes que dependem do mesmo ponto.
  - A lacuna fica no plano, marcada `L-XX`, numerada por plano, com o que faltou e o ajuste feito.

**Ver também:** Unidade, Tarefa, Plano, Code, Derive, Cold-start, Aprovação.

## Independência entre planos

**O que é:** a condição de que um plano não dependa de outro.

- **Quando vale:** na revisão, em todo plano.
- **O que exige:**
  - Todo plano diz por que é um plano e não dois, pelo teste: entregando só a parte A e parando, o
    sistema fica válido e útil? Se sim para A e para B, são dois planos.
  - Partes com dependência em sequência e objetivo único ficam no mesmo plano, como quando só A é
    útil e B depende de A: dividi-las cria dependência entre planos.
  - Dois planos concorrem quando, abertos ao mesmo tempo, mudam o mesmo comportamento.
- **Quando falha:** a revisão avisa o usuário, que decide; quando ele decide não dividir, ou seguir
  com um plano concorrente, o plano registra o porquê.

**Ver também:** Revisão, Plano, Plano técnico, Aprovação.

## Numeração e nomenclatura

**O que é:** como planos e unidades são nomeados e numerados, para que cada um seja rastreável.

- **Quando vale:** em todo plano e em toda unidade.
- **O que exige:**
  - O plano nasce com um nome semântico, em inglês e em kebab-case, no formato
    `<intenção>-<alvo>[-<qualificador>]`. O nome é identificador, e a prosa do plano segue em pt-BR.
    O nome não declara o tipo.
  - Na aprovação que o Plano define, o plano recebe um número de 4 dígitos, sequencial em todo o
    projeto, atribuído uma vez e nunca reaproveitado. Passa a se chamar `NNNN-nome`, e o nome não
    muda mais.
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
  - O rascunho no `_inbox` que já foi além da proposta volta pelo decode: as decisões, as lacunas
    decididas, as restrições e o oráculo dele passam para a proposta, e nada do que vale fica só no
    histórico do git.
  - Continua com o tipo `norma`, que no formato novo se chama `rule`.
  - Os links de planos fechados para a regra anterior ficam como registro.

**Ver também:** Plano, Raiz dos planos, Tipo, Usuário, Decode, Revisão, Derive, Code.
