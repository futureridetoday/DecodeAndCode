---
# about
name: atomic-inventory
type: doc
project: ""
description: Inventário das menores partes do codex, no espírito do Atomic design — primeiro a lista de átomos tirada do brief, depois a definição, o funcionamento e as relações de cada um
tags: [codex, redesign, atomic-design, inventario]

# history
author: Bortoli
created: 2026-11-24
status: draft
version: 0.19.0
updated: ""

# system
scope: project
source: ""
auto_load: false
checksum: ""
dependencies: [redesign-brief]
---

# Inventário atômico do codex

Base de conceitos para o redesign do codex. A fonte dos itens é o
[brief do redesign](redesign-brief.md), que este documento não altera.

O trabalho tem duas fases:

1. **Identificar os átomos:** nome e origem no brief, sem definição.
2. **Definir cada átomo:** o que é, como funciona e com quais outros itens se relaciona. A
   classificação em moléculas e organismos vem nesta fase, quando as relações estiverem definidas.

Ficam de fora os nomes de mecanismo (scripts, subcomandos, hooks), porque o codex não os cita
(brief, seção 4).

## Fase 1 — Itens

Fechada em 2026-11-24, com 65 itens, depois de esgotar o brief. Na fase 2, seis itens saíram
(I-10, I-17, I-20, I-25, I-40 e I-57), e o I-66 (MVP) nasceu da separação do I-63; os IDs não são
reaproveitados.

A classificação em átomo, propriedade ou composto não serviu de filtro no primeiro lote: todos os
itens precisam de descrição. Entra na lista o que a pessoa seleciona; a classificação fica para a
fase 2.

| # | Item | Nota |
|---|---|---|
| I-01 | Pedido | junto com a entrada, etapa comum aos dois workflows |
| I-02 | Insight | entrada para discutir, que pode terminar sem plano |
| I-03 | Tipo | escolhe o workflow |
| I-04 | Workflow | |
| I-05 | Etapa | |
| I-06 | Decode | substitui o `intake` |
| I-07 | Revisão | |
| I-08 | Derive | |
| I-09 | Code | substitui o `implement` |
| I-11 | Plano | |
| I-12 | Plano técnico | |
| I-13 | Plano mínimo | da correção |
| I-14 | Porte | |
| I-15 | Unidade | sempre tem tarefas |
| I-16 | Tarefa | combinada com passo |
| I-18 | Aprovação | |
| I-19 | Teste |  |
| I-21 | Huddle |  |
| I-22 | Princípio | do projeto |
| I-23 | Guideline | do projeto |
| I-24 | Guardrail | do projeto |
| I-26 | Foundation |  |
| I-27 | Codex |  |
| I-28 | Padrão de código | conteúdo da foundation |
| I-29 | Mapa de recursos do projeto | conteúdo da foundation |
| I-30 | Recurso do projeto |  |
| I-31 | Papel | PM, Designer e Tech Lead |
| I-32 | Referência de produto |  |
| I-33 | Mindset de produto |  |
| I-34 | Módulo | junto com o manifesto do módulo |
| I-35 | Usuário | ator: pede, aprova e testa |
| I-36 | Claude | ator: decodifica, revisa, deriva e coda |
| I-37 | História | escrita na revisão; relação com a unidade a definir |
| I-38 | Definition of Ready | o que o derive garante |
| I-39 | Correção | workflow e tipo `fix` |
| I-41 | Plano anterior ao redesign | só se atualiza quando o usuário pede |
| I-42 | Migração | da norma para o codex nos projetos que já usam o DC |
| I-43 | Raiz dos planos | `<plan_root>` |
| I-44 | Cold-start | a unidade basta sozinha |
| I-45 | Handoff | orquestra as unidades entre sessões |
| I-46 | Independência entre planos | checagem de concorrência na revisão |
| I-47 | Registro de uso | log e feedback ao método |
| I-48 | Setup |  |
| I-49 | Rethink |  |
| I-50 | Fluxo de decodificação | Clarificar, Evitar, Reduzir |
| I-51 | Paralelo com produto digital | orientação, ainda não regra |
| I-52 | Camada | codex e foundation |
| I-53 | Clean Architecture |  |
| I-54 | Regra de dependência |  |
| I-55 | Invariante | uma fonte por fato; nada do projeto viaja no plugin |
| I-56 | Restrição fundamental | o projeto não altera o codex |
| I-58 | Núcleo | nunca importa um módulo |
| I-59 | Tabela de recursos do plano | skills do projeto pelo nome |
| I-60 | Objetivo do plano |  |
| I-61 | Quem mantém o plugin | único ator que altera o codex e inclui ou remove módulos |
| I-62 | Os quatro riscos | valor, usabilidade, viabilidade técnica e de negócio |
| I-63 | Hipótese | |
| I-64 | Teste do plano inteiro | P8 |
| I-65 | Teste que reproduz o defeito | C4 |
| I-66 | MVP | separado da hipótese na fase 2 |

## Fase 2 — Definições

Cada item traz o que é, como funciona, as relações com outros itens pelo ID e a origem. A fonte é
o brief; quando a informação vem do projeto, o item marca **[projeto]**; sem fonte, o campo fica
com "—".

### Piloto

#### I-11 Plano

- **O que é:** o registro do que vai ser feito para atender a um pedido. No paralelo com produto
  digital, corresponde à proposta.
- **Como funciona:**
  - Tem um tipo, que escolhe o workflow.
  - No workflow de produto, começa como proposta conceitual no decode (P1), é aprovado (P2) e vira
    plano técnico na revisão (P3), com tarefas ou unidades conforme o porte.
  - Recebe número na aprovação do plano técnico (P4, decisão 2).
  - O plano com mais de uma unidade é testado inteiro no fim (P8).
  - Todos os planos ficam juntos em `<plan_root>/`. O pequeno é um arquivo; o médio e o grande são
    uma pasta com o plano e as unidades.
  - O campo `core:` diz a que parte do sistema o plano se refere.
  - Todo plano novo declara a versão do formato (decisão 3).
- **Relações:** nasce de um pedido (I-01); tem um tipo (I-03) e um porte (I-14); segue um workflow
  (I-04); passa por proposta e plano técnico (I-12), ou é plano mínimo na correção (I-13); é
  feito de tarefas (I-16) ou unidades (I-15); é aprovado (I-18); é testado inteiro (I-64); mora na
  raiz dos planos (I-43); registra os recursos do projeto na tabela de recursos (I-59); os planos
  antigos seguem regra própria (I-41).
- **Origem:** seção 1 (*Workflow*, *Porte*, *Organização dos planos*); decisões 2, 3 e 7.

#### I-15 Unidade

- **O que é:** uma lista de tarefas que, no fim, entrega um pacote concreto e documentado, que
  agrega valor ao todo e é minimamente mensurável e testável, pelo Claude ou pelo usuário.
- **Como funciona:**
  - Tem as tarefas necessárias para entregar um pacote testável que agrega valor ao produto; não
    há limite de tarefas (decidido em 2026-11-24).
  - O médio tem 1 unidade, e o grande, 2 ou mais.
  - O derive dá a cada unidade o contexto, a memória e o padrão de código do projeto (P5).
  - O code executa uma unidade por vez (P6).
  - Só começa com um oráculo e só fecha com teste e aprovação do usuário, registrada em
    `approved_by` e `approved_at`.
  - A próxima unidade só começa depois que a anterior é aprovada (P7).
  - Basta sozinha e roda sem o histórico da conversa (seção 3, cold-start).
  - Se a execução mostrar que estava insuficiente, a correção é da unidade, registrada como lacuna
    (seção 3).
- **Relações:** é feita de tarefas (I-16); produz uma entrega; pertence a um plano médio ou
  grande (I-11, I-14); é preparada no derive (I-08) e executada no code (I-09); começa com um
  critério de aceite; fecha com teste (I-19) e aprovação (I-18); corresponde a uma história
  (I-37); obedece ao cold-start (I-44); é orquestrada pelo handoff (I-45).
- **Origem:** seção 1 (*Porte*, *Unidade*, *O que muda*, P5 a P7); seção 3; decisão 3.

#### I-16 Tarefa

- **O que é:** a menor ação do trabalho, que o code executa de uma vez e cujo resultado
  se consegue conferir (decidido em 2026-11-24).
- **Como funciona:**
  - A revisão quebra o trabalho em tarefas (P3).
  - No pequeno, as tarefas são executadas na mesma sessão, logo após a aprovação do plano técnico.
- **Relações:** compõe a unidade (I-15) e o plano pequeno (I-11, I-14); é criada na revisão
  (I-07); é executada no code (I-09).
- **Origem:** seção 1 (P3, P6, *Porte*, *O paralelo*).
- **Nota [projeto]:** na norma atual, passo é a sequência numerada dentro da unidade, com teto de 8,
  e tarefa é a lista de caixas `## Tarefas` do plano médio. O brief e a junção unificam os dois.

#### I-18 Aprovação

- **O que é:** o momento em que o usuário aceita o resultado de uma etapa do workflow do plano; a
  etapa seguinte só começa depois dela.
- **Como funciona:**
  - No workflow de produto, na ordem:
    1. A proposta, no fim do decode (P2).
    2. O plano técnico, no fim da revisão; é nela que o plano recebe número (P4, decisão 2).
    3. As unidades derivadas, no fim do derive (decidido em 2026-11-24; o brief não tem esta
       aprovação).
    4. Cada entrega, no code: fecha a unidade junto com o teste, registrada em `approved_by` e
       `approved_at`; a próxima unidade só começa depois (P7).
    5. A aprovação final, depois do teste do plano inteiro (decidido em 2026-11-24; o brief só tem
       o teste, P8). No pequeno, que não tem unidade, é a única aprovação depois do code.
  - No workflow de correção, na ordem:
    1. O plano mínimo, antes do code (C2, decisão 10).
    2. A aprovação final, depois do teste que reproduz o defeito (decidido em 2026-11-24; o brief
       só tem o teste, C4).
  - Quem aprova é sempre o usuário.
  - As escritas do DC no projeto (foundation, regra `Skill(<nome>)`, migração) também pedem o sim
    da pessoa, mas não são aprovação do workflow; cada item as descreve.
- **Relações:** é dada pelo usuário (I-35); fecha o decode (I-06), a revisão (I-07), o derive (I-08)
  e o code (I-09); aprova o plano técnico (I-12), o plano mínimo (I-13) e a unidade (I-15); vem
  depois do teste (I-19, I-64, I-65); abre a numeração do plano (I-11).
- **Origem:** seção 1 (C2, P2, P4, P7, P8, *O que muda*); decisões 2, 4 e 10; decidido pela pessoa
  em 2026-11-24.

### Demais itens

#### I-01 Pedido

- **O que é:** o que a pessoa traz para o DC e que dá início a um plano. É a primeira etapa dos dois
  workflows, a entrada (etapa 1), e o objeto que o DC decodifica.
- **Como funciona:**
  - A entrada pode ser um pedido, blocos de texto para juntar ou um insight para discutir.
  - Sai dela um pedido único, ou uma conversa que termina sem plano.
  - Quem participa são o usuário e Claude.
  - No paralelo com produto digital, corresponde ao pedido que stakeholders e squad escrevem.
  - O objetivo do DC é decodificar o pedido: entender, validar e planejar.
- **Relações:** pode ser um insight (I-02); depois dele vem a escolha do tipo (I-03); é a etapa
  inicial de todo workflow (I-04, I-05); dele nasce o plano (I-11); é decodificado no decode (I-06);
  vem do usuário (I-35); o paralelo com produto digital o relaciona à entrada (I-51).
- **Origem:** seção 1 (*Missão*, *Objetivo do DC*, *Entrada, comum aos dois workflows*, *O paralelo*).

#### I-02 Insight

- **O que é:** uma das formas de entrada: algo para discutir, sem ser ainda um pedido.
- **Como funciona:**
  - Pode terminar numa conversa sem plano.
  - O brief não diz como um insight vira pedido.
- **Relações:** é uma forma de entrada (I-01); se virar pedido, segue para a escolha do tipo (I-03).
- **Origem:** seção 1 (*Entrada, comum aos dois workflows*, etapa 1).
- **Decidido em 2026-11-24:** uma entrada que ainda não é pedido. O DC conversa sobre ela e só abre plano se ela
  virar um pedido.

#### I-03 Tipo

- **O que é:** a classificação do plano que escolhe o workflow que ele segue.
- **Como funciona:**
  - Vem antes do decode, na etapa 2 da entrada.
  - Claude o identifica, com as perguntas que precisar, e o declara com o motivo; o usuário pode
    corrigir.
  - A identificação usa a lista de tipos que o próprio DC mantém; o codex não a repete.
  - `fix` segue o workflow de correção; os demais tipos seguem o de produto.
  - Outros tipos podem ganhar workflow próprio depois.
  - O valor `norma` de `plan_type` e `unit_type` vira `rule` no formato novo; os planos antigos
    continuam com `norma`.
  - Hoje o intake propõe o tipo junto com o plano; no redesign o tipo vem antes do decode.
- **Relações:** escolhe o workflow (I-04) e, com ele, a correção (I-39) ou o produto; vem de uma lista;
  é identificado por Claude (I-36) e pode ser corrigido pelo usuário (I-35); é declarado
  no plano (I-11); define o objetivo do plano junto com o pedido (I-60); vem depois do pedido
  (I-01) e antes do decode (I-06).
- **Origem:** seção 1 (*Entrada, comum aos dois workflows*, *O que muda*, *Restrições*); decisões 5
  e 6.

#### I-04 Workflow

- **O que é:** a sequência de etapas que um plano segue, escolhida pelo tipo.
- **Como funciona:**
  - Por enquanto são dois: o de correção, para `fix`, e o de produto, para os demais tipos.
  - No código, os identificadores são `fix`, para o de correção, e `product`, para o de produto
    (decidido em 2026-11-24).
  - Os dois começam pela mesma entrada (etapas 1 e 2).
  - Outros tipos podem ganhar workflow próprio depois.
  - Na Clean Architecture do DC, os workflows e suas etapas são os casos de uso; mudam quando um workflow
    muda ou um tipo ganha workflow próprio.
  - O workflow de correção é o primeiro módulo.
- **Relações:** é escolhido pelo tipo (I-03); é feito de etapas (I-05); o de correção é I-39 e o de
  produto passa por decode (I-06), revisão (I-07), derive (I-08) e code (I-09); é seguido pelo
  plano (I-11); o workflow de correção é o primeiro módulo (I-34); é caso de uso na Clean
  Architecture (I-53).
- **Origem:** seção 1 (*Workflow*, *Módulos*); seção 4; decisão 5.

#### I-05 Etapa

- **O que é:** um passo de um workflow, descrito com quem a executa e o que sai dela.
- **Como funciona:**
  - Os workflows são tabelas de etapas: entrada (1 e 2), correção (C1 a C4) e produto (P1 a P8).
  - Cada etapa diz quem a faz (Claude, usuário ou os dois) e o que produz.
- **Relações:** compõe o workflow (I-04); as etapas nomeadas no codex são o decode (I-06), a revisão
  (I-07), o derive (I-08) e o code (I-09); algumas etapas são aprovações (I-18).
- **Origem:** seção 1 (*Entrada*, *Workflow de correção*, *Workflow de produto*).

#### I-06 Decode

- **O que é:** a primeira etapa do workflow de produto (P1): a em que Claude entende o pedido e propõe
  uma solução conceitual. Substitui o `intake`.
- **Como funciona:**
  - Claude atua no papel de PM, Designer e Tech Lead.
  - Usa o mindset de produto, a foundation, os princípios, as guidelines e os guardrails, e as
    skills e os recursos do projeto.
  - Apoia-se nas referências de produto.
  - Sai uma proposta de solução conceitual, com referências técnicas, escrita para o usuário.
  - As skills do projeto são invocadas pelo nome, nunca lidas e copiadas; o nome vai para a tabela
    do plano.
  - Segue Clean Architecture, sempre.
  - O fluxo de decodificação de hoje (Clarificar, Evitar, Reduzir) é a semente do decode.
  - Na correção, o decode é enxuto: identificar o problema e criar a correção.
- **Relações:** vem depois do tipo (I-03); produz a proposta, que o usuário aprova (I-18);
  segue-se a revisão (I-07); usa o mindset de produto (I-33), os papéis (I-31), as referências de
  produto (I-32), os quatro riscos (I-62), a foundation (I-26), princípios, guidelines e
  guardrails (I-22, I-23, I-24) e os recursos do projeto (I-30, I-59); sua semente é o workflow de
  decodificação (I-50); segue a Clean Architecture (I-53).
- **Origem:** seção 1 (P1, *Referências de produto*, *O que muda*, *Workflow de correção*); decisões 7
  e 12.

#### I-07 Revisão

- **O que é:** a etapa P3 do workflow de produto: transformar a proposta aprovada em plano técnico.
- **Como funciona:**
  - Claude atua no papel de PM e Tech Lead.
  - Escreve as histórias.
  - Refina: viabilidade técnica, compatibilidade, infra, erros, lacunas e decisões em aberto.
  - Quebra o trabalho em tarefas.
  - Sai o plano técnico, com tarefas ou unidades conforme o porte; é na revisão que o porte se
    define.
  - Apoia-se em histórias de usuário e INVEST e em User Story Mapping.
  - A independência entre planos se confere nela.
  - O lint cruza a tabela de recursos do plano com os recursos do projeto na revisão.
- **Relações:** vem depois da aprovação da proposta (I-18); escreve histórias (I-37); quebra
  em tarefas (I-16); produz o plano técnico (I-12) e define o porte (I-14); confere a independência
  entre planos (I-46); usa as referências de produto
  (I-32); confere os recursos do projeto (I-59); papéis em I-31.
- **Origem:** seção 1 (P3, *Referências de produto*); seção 3; decisões 2 e 12.

#### I-08 Derive

- **O que é:** a etapa P5 do workflow de produto: prepara cada unidade para ser executada. Só existe no
  médio e no grande.
- **Como funciona:**
  - Entrega cada unidade com contexto, memória e o padrão de código do projeto.
  - Garante que a unidade baste sozinha (cold-start).
  - No paralelo com produto digital, é o momento em que a história fica pronta para desenvolver.
  - No grande, orquestra a execução entre sessões (handoff).
  - Cita na unidade as guidelines aplicáveis, que o code recebe.
  - O lint de nomes dos recursos do projeto roda no derive.
- **Relações:** vem depois do plano técnico aprovado (I-12, I-18); prepara a unidade (I-15); garante
  a Definition of Ready (I-38) e o cold-start (I-44); produz o handoff (I-45); usa o padrão de
  código (I-28) e a foundation (I-26); cita guidelines (I-23) e confere recursos do projeto
  (I-59); antecede o code (I-09).
- **Origem:** seção 1 (P5, *Porte*, *O paralelo*); seção 3; decisões 8 e 12.
- **Decidido em 2026-11-24:** a memória são as decisões e lacunas que o plano já registrou e que a unidade precisa
  conhecer, coerente com o cold-start.

#### I-09 Code

- **O que é:** a etapa de execução (C3 na correção, P6 no produto): Claude escreve o que o plano
  pede. Substitui o `implement`.
- **Como funciona:**
  - Usa as skills e os recursos do projeto.
  - No pequeno, as tarefas rodam na mesma sessão. No médio e no grande, uma unidade por vez, e o
    plano recebe a recomendação de ser executado numa sessão nova (decidido em 2026-11-24): a
    unidade traz o que precisa para o cold-start, e começar sem o histórico economiza tokens.
  - Gate de entrada: não começa sem oráculo. Gate de saída: não fecha sem teste e sem a aprovação do
    usuário (P7).
  - A unidade roda num subagente, sem o histórico da conversa.
  - A guideline-ponte continua valendo no code, e o lint de nomes dos recursos do projeto roda na
    entrada.
  - Se a execução mostrar que a unidade estava insuficiente, a correção é da unidade, registrada como
    lacuna.
- **Relações:** executa tarefas (I-16) ou uma unidade (I-15); vem depois do plano mínimo aprovado
  (I-13) ou do derive (I-08); é seguido do teste (I-19) e da aprovação (I-18); usa os recursos do
  projeto (I-30, I-59) e as guidelines (I-23); obedece ao cold-start (I-44); executa o Claude
  (I-36).
- **Origem:** seção 1 (C3, P6, P7, *O que muda*); seção 3; decisão 12.

#### I-12 Plano técnico

- **O que é:** o que sai da revisão (P3): o plano, com tarefas ou unidades conforme o porte.
- **Como funciona:**
  - É aprovado pelo usuário em P4, e é nessa aprovação que o plano recebe número.
  - Só depois da aprovação vem o derive, no médio e no grande.
  - O porte só se define na revisão; plano sem porte não é aprovado.
- **Relações:** nasce da proposta pela revisão (I-07); é aprovado (I-18); contém tarefas
  (I-16) ou unidades (I-15), conforme o porte (I-14); é o plano que segue para o derive (I-08);
  registra os recursos do projeto na tabela (I-59); parte do plano (I-11).
- **Origem:** seção 1 (P3, P4); decisão 2.

#### I-13 Plano mínimo

- **O que é:** o plano pequeno com uma única tarefa. É o mesmo plano que o pequeno; muda só o
  conteúdo (decidido em 2026-11-24).
- **Como funciona:**
  - As seções são: o problema e como reproduzi-lo, a correção, e como verificar.
  - É registrado no diagnóstico (C1) e aprovado pelo usuário antes do code (C2).
  - Se o diagnóstico mostrar que a correção não é pequena, ela passa para o workflow de produto.
  - A correção gera plano registrado (decisão 9).
- **Relações:** é o plano (I-11) do workflow de correção (I-39); tem o porte pequeno (I-14); é aprovado
  (I-18); é codado (I-09) e verificado pelo teste que reproduz o defeito (I-65).
- **Origem:** seção 1 (*Workflow de correção*, C1, C2); decisões 9 e 10.

#### I-14 Porte

- **O que é:** o tamanho do plano no workflow de produto: pequeno, médio ou grande.
- **Como funciona:**
  - Pequeno: lista de tarefas, sem derive, executada na mesma sessão logo após a aprovação do plano
    técnico.
  - Médio: 1 unidade, com derive, aprovada ao final.
  - Grande: 2 ou mais unidades, com derive, uma por vez, cada uma depois da aprovação da anterior.
  - Define-se na revisão.
  - Não há limite de tarefas por unidade: a unidade tem as tarefas necessárias para entregar um
    pacote testável que agrega valor ao produto (decidido em 2026-11-24).
  - O porte medido continua onde está, aplicado por script.
  - Um plano sem porte não é aprovado.
- **Relações:** é definido na revisão (I-07); determina se o plano passa pelo derive (I-08); fixa a
  estrutura do plano (I-11) em tarefas (I-16) ou unidades (I-15); o grande tem handoff (I-45) e
  teste do plano inteiro (I-64).
- **Origem:** seção 1 (*Porte, no workflow de produto*); seção 3 (*Porte medido*); decisões 2 e 3.

#### I-19 Teste

- **O que é:** a verificação de que uma entrega, uma correção ou o plano inteiro funciona; é feita
  pelo Claude ou pelo usuário.
- **Como funciona:**
  - Acontece em três momentos: o teste que reproduz o defeito (C4), o teste da entrega, antes da
    aprovação (P7), e o teste do plano inteiro (P8).
  - A unidade não fecha sem teste e sem a aprovação do usuário.
  - O estado de uma unidade é derivado do teste, nunca editado à mão.
  - O que se entrega precisa ser minimamente mensurável e testável.
- **Relações:** verifica a correção (I-39, I-65), a entrega e o plano inteiro (I-64); precede
  a aprovação (I-18); fecha a unidade (I-15) junto com ela; é feito pelo usuário (I-35) ou por
  Claude (I-36); cobre o critério de aceite.
- **Origem:** seção 1 (C4, P7, P8, *Unidade*); seção 3; decisão 4.

#### I-21 Huddle

- **O que é:** o espaço de conversa entre Claude e a pessoa para os dois aprenderem juntos sobre o
  projeto (decidido em 2026-11-24).
- **Como funciona [projeto]** (`.claude/skills/huddle/SKILL.md`; `modelo-dev-units.md:1202-1230`):
  - Há um huddle por pessoa, identificada pelo nome no git. É registro versionado e nunca é
    carregado sozinho na sessão.
  - Quando o huddle está atrasado, a abertura da sessão avisa.
  - A pauta traz o que aconteceu desde o último huddle (commits, erros registrados, bloqueios de
    guardrail) e as entradas abertas.
  - Claude ou a pessoa registra uma entrada, com um tipo de um vocabulário fechado.
  - As entradas são conversadas uma por vez; cada uma termina em decisão, guideline, guardrail,
    feedback ao método ou descarte com motivo, ou continua aberta.
  - Nada ali vale como regra: o que se aprende sai do huddle para o lugar certo.
- **Relações:** acontece entre Claude (I-36) e o usuário (I-35); o que se aprende vira guideline
  (I-23), guardrail (I-24) ou feedback ao método no registro de uso (I-47); mora na raiz dos planos
  (I-43); o setup o inicia (I-48).
- **Origem:** definição da pessoa em 2026-11-24; o funcionamento vem do projeto. O brief só diz
  onde o huddle mora (seção 3).

#### I-22 Princípio

- **O que é:** o north star do projeto: a direção que aponta para o objetivo final do projeto e
  pela qual se julga cada decisão.
- **Como funciona:**
  - O primeiro princípio é o north star, tirado do objetivo do projeto: um *enunciado*, o objetivo
    numa frase curta, e um *teste*, a condição verificável que uma mudança mostra para se aproximar
    dele **[projeto]** (`.claude/skills/setup/SKILL.md:83`).
  - O teto é 5 princípios, e o ideal, 3 **[projeto]** (`.claude/skills/setup/SKILL.md:79`).
  - Carrega no início de toda sessão (seção 5).
  - Para distinguir princípio de guideline há uma orientação, não uma regra: se uma equipe
    competente pode deixar o item de lado e ainda fazer bom trabalho, ele tende a ser guideline. A
    pessoa escolhe se segue a orientação **[projeto]** (`.claude/rules/principles.md:3-6`).
  - É do projeto, não do codex: o setup cria os princípios, o rethink os revisa e o decode os usa.
- **Relações:** é do projeto (I-26 só o menciona); o decode o usa (I-06); setup (I-48) e rethink
  (I-49) o criam e revisam; irmão da guideline (I-23) e do guardrail (I-24).
- **Origem:** seção 1 (*Duas camadas*, *Workflow de produto*); seção 5; decidido em 2026-11-24.

#### I-23 Guideline

- **O que é:** uma regra do projeto que carrega quando Claude lê ou edita um arquivo que casa com
  um padrão.
- **Como funciona:**
  - Mecanismo: rule com `paths`, em `.claude/rules/`.
  - Frontmatter inválido faz a guideline carregar sempre; por isso o lint continua necessário.
  - Subdiretórios de `.claude/rules/` também carregam.
  - A guideline-ponte nomeia o recurso do projeto para os caminhos onde ele vale; o derive a cita
    na unidade e o code a recebe.
  - A Clean Architecture, no projeto, é guideline de quem a adota.
  - O decode a usa.
- **Relações:** é do projeto; usada no decode (I-06), citada no derive (I-08) e recebida no code
  (I-09); a ponte liga recursos do projeto (I-30); irmã do princípio (I-22) e do guardrail (I-24);
  Clean Architecture no projeto (I-53); criada e revisada pelo setup (I-48) e pelo rethink (I-49).
- **Origem:** seção 1 (*Duas camadas*); seção 3; seção 5; decisões 7 e 12.
- **Nota [projeto]:** a norma a descreve como "como técnico"
  (`docs/plan/system/modelo-dev-units.md:190-195`).

#### I-24 Guardrail

- **O que é:** uma regra do projeto que não pode depender de Claude lembrar: é imposta.
- **Como funciona:**
  - Mecanismo: o hook `PreToolUse`, que a documentação manda usar para bloquear
    independentemente da decisão de Claude.
  - As regras ficam no projeto, em `.claude/guardrails.json`; o hook é do plugin.
  - O decode o usa.
- **Relações:** é do projeto; usado no decode (I-06); criado e revisado pelo setup (I-48) e pelo
  rethink (I-49); irmão do princípio (I-22) e da guideline (I-23).
- **Origem:** seção 3; seção 5.
- **Nota [projeto]:** a norma o descreve como "limite verificável"
  (`docs/plan/system/modelo-dev-units.md:190-195`).

#### I-26 Foundation

- **O que é:** o que o projeto registra para o DC trabalhar como alguém do time e que não tem outro
  lugar. A foundation registra o padrão de código e o mapa dos recursos do projeto.
- **Como funciona:**
  - O codex diz como o DC trabalha; a foundation diz como é este projeto.
  - Não repete o que já tem lugar: princípios, guidelines, guardrails, decisões, planos e huddle
    continuam onde estão, e a foundation no máximo os menciona.
  - Não é instrução carregada: o decode e o derive a leem quando precisam.
  - Mora num arquivo em `<plan_root>/system/`.
  - Só muda pelas portas do DC (setup, rethink e plano), com o sim da pessoa.
  - Nada do codex aparece nela.
  - No redesign, o padrão de código só tem o lugar reservado.
- **Relações:** é uma camada (I-52), par do codex (I-27); contém o padrão de código (I-28) e o mapa
  de recursos (I-29); é lida pelo decode (I-06) e pelo derive (I-08); escrita pelo setup (I-48),
  pelo rethink (I-49) e pelo plano; mora na raiz dos planos (I-43); obedece à uma fonte por fato
  (I-55).
- **Origem:** seção 1 (*Duas camadas*); seção 5; decisão 8; decidido em 2026-11-24.

#### I-27 Codex

- **O que é:** o método do DC, escrito uma vez e igual para todo projeto: o que o DC faz, em que
  ordem, com que artefatos e com que garantias. Substitui a norma e é o cérebro do DC.
- **O que guarda:** os workflows e as etapas; os artefatos (plano, unidade, tarefa); os contratos e
  os gates; as referências de produto; os invariantes.
- **O que não guarda:** mecanismo (skill, script, hook, versão do Claude Code), nada de projeto,
  nem evidência e história. Foram esses três que corromperam a norma: 27% das linhas eram mecanismo
  e 14%, evidência e história (*Ponto de partida*).
- **Como funciona:**
  - Cada etapa lê o trecho de que precisa, quando roda; fora das skills do DC, Claude não o vê.
  - Mora só no plugin, versionado com ele, e nunca é copiado para o projeto.
  - Só quem mantém o plugin o altera, a cada versão.
  - Evolui por evidência, a partir do registro de uso, e não por reescrita (seção 3).
  - É à prova de futuro pela regra de dependência; um lint confere.
  - Substitui a norma por completo, inclusive nos projetos que já usam o DC.
  - Na Clean Architecture, é a camada das entidades.
- **Relações:** é uma camada (I-52), par da foundation (I-26); é mantido por quem mantém o plugin
  (I-61); nenhum projeto o altera (I-56); obedece à regra de dependência (I-54) e aos invariantes
  (I-55); contém as referências de produto (I-32) e o fluxo de decodificação (I-50); evolui pelo
  registro de uso (I-47); substitui a norma na migração (I-42); é a camada das entidades na Clean
  Architecture (I-53).
- **Origem:** *Ponto de partida*; seção 1 (*Missão*, *Duas camadas*, *Restrições*); seções 3, 4 e
  5; decisões 1, 11 e 13.

#### I-28 Padrão de código

- **O que é:** o estilo de código do time do projeto, que o derive garante que a unidade siga.
- **Como funciona:**
  - É conteúdo da foundation.
  - No redesign, a foundation só reserva o lugar.
  - Extrair o padrão do código existente, com o setup propondo e a pessoa aprovando, é módulo para
    depois da versão 1.
- **Relações:** faz parte da foundation (I-26); entra na unidade pelo derive (I-08); o setup propõe
  extraí-lo (I-48) com aprovação (I-18); a extração é módulo futuro (I-34).
- **Origem:** seção 1 (*Duas camadas*, P5); seção 3; decisões 8 e 14.

#### I-29 Mapa de recursos do projeto

- **O que é:** o índice dos recursos do projeto que o DC pode usar, pelo nome, guardado na
  foundation.
- **Para cada recurso, registra:** o nome pelo qual é invocado; o tipo; a fase do DC em que entra
  (decode, revisão ou code); se só a pessoa pode chamá-lo; se é do projeto ou pessoal; e se tem
  permissão registrada (decisão 12).
- **Como funciona:**
  - Nunca guarda conteúdo, linha nem versão: o recurso invocado pelo nome entra na versão atual.
  - O setup o escreve e o rethink o atualiza, com o sim da pessoa. Recurso criado depois do setup
    só entra quando o rethink roda **[projeto]** (huddle, H-25).
  - É dele que o plano tira a sua tabela de recursos.
- **Relações:** faz parte da foundation (I-26); lista os recursos do projeto (I-30); orienta o
  decode (I-06), a revisão (I-07) e o code (I-09); alimenta a tabela de recursos do plano (I-59); é
  escrito pelo setup (I-48) e atualizado pelo rethink (I-49).
- **Origem:** seção 1 (*Duas camadas*); seção 5; decisões 8 e 12; decidido em 2026-11-24.

#### I-30 Recurso do projeto

- **O que é:** o que o projeto já tem para o Claude usar: skills, commands, MCP e o `CLAUDE.md`. É
  do projeto, fora do codex e da foundation.
- **Como funciona:**
  - O DC chama o recurso pelo nome e nunca copia o conteúdo dele, porque o recurso continua
    evoluindo no projeto.
  - O DC só cria ou remove um recurso pelo rethink, com o sim da pessoa.
  - Cada plano registra, pelo nome, os recursos que usa.
- **Relações:** é do projeto, fora do codex (I-27) e da foundation (I-26), que só o mapeia (I-29);
  é usado no decode (I-06) e no code (I-09); é registrado na tabela de recursos do plano (I-59); é
  criado ou removido pelo rethink (I-49).
- **Origem:** seção 1 (*Duas camadas*, *O que muda*); seção 5; decisão 12; decidido em 2026-11-24.

#### I-31 Papel

- **O que é:** o chapéu que Claude veste numa etapa: PM, Designer ou Tech Lead.
- **Como funciona:**
  - No decode, Claude atua como PM, Designer e Tech Lead.
  - Na revisão, como PM e Tech Lead.
  - O trio PM, Designer e Tech Lead é a pauta dos quatro riscos.
- **Relações:** exercido por Claude (I-36) no decode (I-06) e na revisão (I-07); o trio faz a pauta
  dos quatro riscos (I-62); corresponde, no paralelo, a quem propõe e refina (I-51).
- **Origem:** seção 1 (P1, P3, *Referências de produto*, *O paralelo*).

#### I-32 Referência de produto

- **O que é:** uma referência consagrada de criação de produto digital em que o decode e a revisão se
  apoiam. Ficam no próprio codex.
- **Como funciona:**
  - No decode: Jobs to Be Done, Design Thinking e Double Diamond, Lean Startup, os quatro riscos de
    Cagan e Shape Up.
  - Na revisão: histórias de usuário e INVEST, e User Story Mapping.
  - Cada uma traz algo específico: por exemplo, o JTBD descreve o problema pelo que a pessoa quer
    realizar.
- **Relações:** moram no codex (I-27); apoiam o decode (I-06) e a revisão (I-07); incluem os quatro
  riscos (I-62), hipótese e MVP (I-63), a história (I-37) e a proposta (via Shape Up); a
  semente delas é o fluxo de decodificação (I-50); o mindset de produto as sustenta (I-33).
- **Origem:** seção 1 (*Referências de produto*); decisão 11.

#### I-33 Mindset de produto

- **O que é:** o modo de pensar com que o DC decodifica qualquer pedido: começar pelo problema e por
  quem o tem, buscar o resultado e não a funcionalidade, e entregar o mínimo que gera valor e se
  consegue verificar.
- **Como funciona:** o decode sempre faz estas perguntas:
  - De quem é o problema, e o que a pessoa quer realizar? (Jobs to Be Done)
  - O problema foi entendido antes de escolher a solução? (Double Diamond)
  - Qual é a hipótese, e como saberemos que deu certo? (Lean Startup)
  - Valor, usabilidade, viabilidade técnica e viabilidade de negócio estão cobertos? (os quatro
    riscos)
  - Quanto vale gastar, e o que fica de fora? (Shape Up)
  - Dá para resolver sem código, e qual é a menor versão? (Clarificar, Evitar e Reduzir;
    **[projeto]** os princípios *Código é custo* e *Subtração antes de adição*,
    `.claude/rules/principles.md`)
  - Vale também para skills, agents e plugins: nesses casos, o "usuário" é quem usa o recurso.
  - "Resultado e não funcionalidade" (outcome em vez de output) é **[referência]** (Marty Cagan).
- **Relações:** orienta o decode (I-06); reúne as referências de produto (I-32), os quatro riscos
  (I-62), a hipótese (I-63) e o MVP (I-66); usa o fluxo de decodificação (I-50); o paralelo com
  produto digital é só orientação (I-51).
- **Origem:** seção 1 (P1, *Referências de produto*, *O paralelo*); decidido em 2026-11-24,
  substituindo a decisão anterior de que o mindset não ganha conteúdo próprio.

#### I-34 Módulo

- **O que é:** a forma como funcionalidade nova entra no DC sem alterar o núcleo.
- **Como funciona:**
  - Incluir ou remover um módulo não quebra o DC nem os outros módulos.
  - Só quem mantém o plugin inclui ou remove módulos.
  - Um módulo pode trazer o trecho do codex da funcionalidade dele.
  - O primeiro módulo é o workflow de correção.
  - O contrato técnico (manifesto, descoberta, versão) é arquitetura do plugin, não do método: fica
    na documentação de manutenção, fora do codex (decidido em 2026-11-24).
- **Relações:** o núcleo (I-58) não depende dele; é incluído e removido por quem mantém o plugin
  (I-61); o primeiro é a correção (I-39); o padrão de código extraído do projeto é módulo futuro
  (I-28).
- **Origem:** seção 1 (*Restrições*, *Módulos*); decisão 14; decidido em 2026-11-24.

#### I-35 Usuário

- **O que é:** a pessoa que usa o DC; é um dos dois atores do workflow.
- **Como funciona:**
  - Pede: traz o pedido, os blocos de texto ou o insight.
  - Pode corrigir o tipo que Claude declara.
  - Aprova: a correção (C2), a proposta (P2), o plano técnico (P4) e cada entrega (P7).
  - Testa, ou deixa o teste com Claude, na correção, na entrega e no plano inteiro.
  - Aprova as escritas do DC no projeto, como a foundation e as regras de permissão.
  - O projeto que usa o DC não altera o codex nem liga ou desliga módulo.
- **Relações:** faz o pedido (I-01); corrige o tipo (I-03); dá as aprovações (I-18); testa (I-19);
  parceiro de Claude (I-36); não é o mantenedor do plugin (I-61).
- **Origem:** seção 1 (*Entrada*, *Workflow*, *Duas camadas*, *Módulos*); decisões 10 e 12.

#### I-36 Claude

- **O que é:** o outro ator do workflow: decodifica, revisa, deriva e coda.
- **Como funciona:**
  - Identifica o tipo, com as perguntas que precisar, e o declara com o motivo.
  - Exerce os papéis de PM, Designer e Tech Lead.
  - Pode testar no lugar do usuário.
  - Executa as unidades em cold-start, sem o histórico da conversa.
  - O DC é otimizado para Claude.
  - Modelo por etapa: Opus decide, Sonnet executa (frontmatter das skills).
- **Relações:** faz o decode (I-06), a revisão (I-07), o derive (I-08) e o code (I-09); identifica o
  tipo (I-03); exerce os papéis (I-31); testa (I-19); parceiro do usuário (I-35); obedece ao
  cold-start (I-44).
- **Origem:** seção 1 (*Entrada*, *Workflow*, *Restrições*); seção 3.

#### I-37 História

- **O que é:** a descrição de uma mudança do ponto de vista de quem se beneficia dela: quem, o que
  quer e para quê, com o critério que diz quando está pronta.
- **Como funciona:**
  - Formato **[referência]** (Mike Cohn): "Como <quem>, quero <o quê>, para <por quê>", com os
    critérios de aceite.
  - INVEST **[referência]** (Bill Wake): independente, negociável, valiosa, estimável, pequena e
    testável.
  - É escrita na revisão (P3), no plano técnico, e cada unidade corresponde a uma história.
  - User Story Mapping **[referência]** (Jeff Patton): ordena as histórias pelo caminho de quem usa
    e as corta em incrementos que entregam valor.
  - O derive garante a Definition of Ready; o aceite da história é o teste e a aprovação da
    unidade.
  - Para recursos que não são produto digital, o "quem" é quem usa o recurso.
- **Relações:** é escrita na revisão (I-07); corresponde à unidade (I-15); a Definition of Ready a
  qualifica (I-38); o aceite é o teste (I-19) e a aprovação (I-18); referências em I-32; o paralelo
  em I-51.
- **Origem:** seção 1 (P3, *Referências de produto*, *O paralelo*); decidido em 2026-11-24.

#### I-38 Definition of Ready

- **O que é:** no paralelo com produto digital, o estado em que a história está pronta para ser
  desenvolvida. É o que o derive garante.
- **Como funciona:**
  - O derive entrega cada unidade com contexto, memória e padrão de código, e basta sozinha.
  - A correspondência é parte do paralelo, que orienta mas ainda não é regra.
- **Relações:** é garantida pelo derive (I-08); qualifica a história (I-37) e portanto a unidade
  (I-15); depende do cold-start (I-44); paralelo em I-51.
- **Origem:** seção 1 (*O paralelo*, P5); seção 3.

#### I-39 Correção

- **O que é:** o workflow enxuto que um plano do tipo `fix` segue: localizar o defeito, corrigi-lo e
  provar que foi corrigido. No código, o identificador é `fix`.
- **Como funciona:**
  - C1, diagnóstico: localiza e reproduz o problema e gera o plano mínimo, com uma tarefa.
  - C2, aprovação do plano mínimo.
  - C3, code.
  - C4, teste: o teste que reproduz o defeito falha antes da correção e passa depois.
  - O decode é enxuto: sem gastar milhares de tokens para corrigir uma palavra.
  - Se a correção não for pequena, o plano passa para o workflow de produto.
  - É o primeiro módulo.
- **Relações:** é o workflow (I-04) escolhido pelo tipo (I-03); gera o plano mínimo (I-13); passa
  por aprovação (I-18); é codada (I-09) e testada pelo teste que reproduz o defeito (I-65); é um
  módulo (I-34).
- **Origem:** seção 1 (*Workflow de correção*, *Módulos*); decisões 5, 9, 10 e 14; decidido em
  2026-11-24.

#### I-41 Plano anterior ao redesign

- **O que é:** o plano sem versão do formato.
- **Como funciona:**
  - Os scripts o leem pela regra antiga.
  - Fica onde está, mesmo dentro de uma pasta de core.
  - Só é atualizado quando o usuário quiser revisá-lo, derivá-lo ou codá-lo; revisar esses planos
    não faz parte do redesign.
  - Continua com `norma` em `plan_type` e `unit_type`.
  - Links de planos fechados para a norma ficam como registro.
  - Nenhum arquivo em uso usa os nomes antigos, mas esses planos ficam como estão.
- **Relações:** é um plano (I-11) sem a versão do formato; mora na raiz dos planos (I-43) ou em pasta
  de core; só muda quando o usuário (I-35) o leva à revisão (I-07), ao derive (I-08) ou ao code
  (I-09); migração em I-42.
- **Origem:** seção 1 (*Restrições*, *Compatibilidade e migração*); decisões 3 e 6.

#### I-42 Migração

- **O que é:** o passo que substitui a norma pelo codex nos projetos que já usam o DC.
- **Como funciona:**
  - O hook de abertura avisa na primeira sessão com a versão nova.
  - Apaga a cópia da norma do projeto, só com aprovação.
  - O histórico do git a guarda, e os links de planos fechados para a norma ficam como registro.
  - A cópia é arquivo do projeto, gravado pelo bootstrap em `<plan_root>/system/`; remover e
    reinstalar o plugin não a apaga.
  - Todo plano novo declara a versão do formato.
  - O redesign termina no codex; depois vêm a propagação e a revisão geral, e só então a release 3.0.
- **Relações:** substitui a norma pelo codex (I-27); exige aprovação (I-18); atua sobre a raiz dos
  planos (I-43); lida com planos antigos (I-41).
- **Origem:** seção 1 (*Compatibilidade e migração*); decisões 6 e 13.

#### I-43 Raiz dos planos

- **O que é:** o diretório `<plan_root>/`, onde ficam todos os planos juntos.
- **Como funciona:**
  - Não há pasta por core: a documentação não precisa espelhar a arquitetura, e quem busca o plano é
    Claude.
  - O plano pequeno é um arquivo; o médio e o grande são uma pasta com o plano e as unidades.
  - O campo `core:` continua no frontmatter e diz a que parte do sistema o plano se refere.
  - Em `<plan_root>/system/` moram a foundation e o huddle.
  - Planos, unidades, huddle e histórico são registro versionado, não instrução carregada.
- **Relações:** guarda planos (I-11), unidades (I-15), a foundation (I-26) e o huddle (I-21); abriga
  planos antigos (I-41); a migração age sobre ela (I-42).
- **Origem:** seção 1 (*Organização dos planos*); seção 5; decisão 7.

#### I-44 Cold-start

- **O que é:** a propriedade da unidade de bastar sozinha: roda num subagente sem o histórico da
  conversa.
- **Como funciona:**
  - É o que o derive precisa garantir.
  - Se a execução mostrar que a unidade estava insuficiente, a correção é da unidade, registrada
    como lacuna.
  - A memória de execução entre unidades ficou fora do redesign, porque o cold-start depende de a
    unidade bastar sozinha.
- **Relações:** vale para a unidade (I-15); é garantido pelo derive (I-08) e obedecido pelo code
  (I-09); sustenta a Definition of Ready (I-38); o handoff conduz as unidades entre sessões (I-45).
- **Origem:** seção 3; seção 5 (*Memória de execução*).

#### I-45 Handoff

- **O que é:** a orquestração da execução entre sessões, no plano grande.
- **Como funciona:**
  - Faz parte da skill derive.
- **Relações:** é produzido pelo derive (I-08); conduz as unidades (I-15) de um plano grande (I-14).
- **Origem:** seção 3.
- **Nota [projeto]:** a norma o descreve como `_handoff.md`, o prompt que conduz a execução, gravado
  só no grande (`docs/plan/system/modelo-dev-units.md:762`, `1626`).

#### I-46 Independência entre planos

- **O que é:** a condição de que um plano não dependa de outro; é evitar planos que dependem um do
  outro.
- **Como funciona:**
  - A checagem de independência e concorrência vai para o codex, na etapa de revisão.
- **Relações:** é conferida na revisão (I-07); vale entre planos (I-11).
- **Origem:** seção 3.
- **Decidido em 2026-11-24:** vale a regra atual **[projeto]**: todo plano diz por que é um plano e não dois
  (`modelo-dev-units.md:790`), e a revisão barra dois planos concorrentes no mesmo alvo.

#### I-47 Registro de uso

- **O que é:** o log de uso do DC e o feedback ao método, que fazem o codex evoluir por evidência, não
  por reescrita.
- **Como funciona:**
  - O log fica no projeto, em `.claude/log/`.
  - O destino do feedback é o registro do método.
  - As entradas usam as marcas `E-XX` e `M-XX`.
- **Relações:** é do projeto; alimenta a evolução do codex (I-27), cuja alteração cabe só ao
  mantenedor (I-61).
- **Origem:** seção 3.
- **Decidido em 2026-11-24:** **[projeto]** `E-XX` é um erro registrado no log; `M-XX` é um feedback sobre o próprio
  método, escrito de forma genérica e aprovado pela pessoa (`modelo-dev-units.md:1252`).

#### I-48 Setup

- **O que é:** a skill do primeiro uso do DC no projeto: cria princípios, guidelines e guardrails.
- **Como funciona:**
  - Um aviso na abertura da sessão, por hook, propõe o setup quando falta.
  - É uma das portas pelas quais o projeto escreve a foundation, sempre com aprovação.
  - Propõe, com a pessoa aprovando, a extração do padrão de código; isso é módulo para depois da
    versão 1.
  - Cada skill do projeto que o DC pode usar ganha uma regra `Skill(<nome>)` gravada com aprovação.
  - A guideline-ponte é criada no setup.
- **Relações:** cria e revisa princípios, guidelines e guardrails (I-22, I-23, I-24); escreve a
  foundation (I-26); irmão do rethink (I-49); aprovações (I-18); avisa também do huddle (I-21).
- **Origem:** seção 3; seção 1 (*Duas camadas*); seção 5; decisões 8 e 12.
- **Nota [projeto]:** a skill o define como o primeiro uso: pré-condições, perfil, princípios,
  guidelines, guardrails, huddle e o princípio Decode → Code, uma sugestão por vez, com toda
  escrita aprovada na conversa (`.claude/skills/setup/SKILL.md:5`).

#### I-49 Rethink

- **O que é:** a skill que revisa princípios, guidelines e guardrails depois de uma mudança de rumo
  do projeto.
- **Como funciona:**
  - É uma das portas pelas quais o projeto escreve a foundation, sempre com o sim da pessoa.
  - Hoje chama esse conjunto de "norma do projeto"; a renomeação troca a expressão pelo nome das
    três coisas.
  - Vai ganhar a capacidade de adicionar e remover recursos do projeto, como skills **[projeto]**
    (huddle, H-25).
- **Relações:** revisa princípios, guidelines e guardrails (I-22, I-23, I-24); escreve a foundation
  (I-26) e atualiza o mapa de recursos (I-29); vai adicionar e remover recursos do projeto (I-30);
  irmão do setup (I-48).
- **Origem:** seção 3; seção 1 (*Duas camadas*); decisão 6; huddle, H-25.
- **Nota [projeto]:** a norma a descreve como a revisão depois de mudança de rumo, item por item,
  com Manter, Editar ou Arquivar, depois do setup concluído
  (`docs/plan/system/modelo-dev-units.md:1567-1585`).

#### I-50 Fluxo de decodificação

- **O que é:** os três estágios que o DC de hoje aplica a uma decisão antes de virar plano: Clarificar,
  Evitar e Reduzir.
- **Como funciona:**
  - Clarificar pergunta qual é o problema, a métrica e o beneficiário.
  - Evitar pergunta se dá para resolver sem código.
  - Reduzir pergunta qual é a menor versão que resolve 80%.
  - O brief o trata como a semente das referências de produto.
- **Relações:** semente do decode (I-06) e das referências de produto (I-32); Reduzir tem relação com
  hipótese e MVP (I-63).
- **Origem:** seção 1 (*Referências de produto*).
- **Nota [projeto]:** a norma acrescenta dois gates, A (necessidade real) e B (mínimo viável)
  (`docs/plan/system/modelo-dev-units.md:671-690`); o princípio da subtração antes da adição está em
  `.claude/rules/principles.md`.
- **Decidido em 2026-11-24:** entra como base do decode, com Clarificar, Evitar e Reduzir; os gates A e B só entram
  depois de revistos à luz das referências de produto.

#### I-51 Paralelo com produto digital

- **O que é:** a correspondência entre o workflow do DC e o workflow de produto digital.
- **Como funciona:**
  - Stakeholders e squad escrevem o pedido (entrada); PM, Designer e Tech Lead propõem a solução
    (decode); a proposta é aprovada (aprovação); PM e Tech Lead escrevem histórias, refinam e quebram
    em tarefas (revisão); a história fica pronta (derive, Definition of Ready); desenvolvimento
    (code); demonstração e aceite da história (teste e aprovação da unidade).
  - O plano corresponde à proposta, a unidade à história e a tarefa continua tarefa.
  - Orienta, mas ainda não é regra: precisa de mais estudo e refinamento, e não é o foco agora.
  - O DC também serve para criar recursos que não são produto digital.
- **Relações:** relaciona pedido (I-01), decode (I-06), revisão (I-07), derive (I-08), code (I-09),
  plano (I-11), unidade (I-15), tarefa (I-16), história (I-37), Definition of Ready (I-38) e papéis
  (I-31); o mindset de produto vale além dele (I-33).
- **Origem:** seção 1 (*O paralelo com produto digital*).

#### I-52 Camada

- **O que é:** cada uma das duas partes que guardam o método: o codex e a foundation.
- **Como funciona:**
  - Codex: o método, só no plugin, alterado só por quem o mantém.
  - Foundation: o padrão de código do projeto e o mapa de recursos, em `<plan_root>/system/`,
    alterada pelo projeto com aprovação.
  - Os recursos do projeto ficam fora das duas camadas.
  - A seção 4 usa "camada" noutro sentido, o das camadas da Clean Architecture.
- **Relações:** são o codex (I-27) e a foundation (I-26); os recursos do projeto ficam fora (I-30);
  as camadas da Clean Architecture são outra divisão (I-53).
- **Origem:** seção 1 (*Duas camadas*); seção 4.

#### I-53 Clean Architecture

- **O que é:** a arquitetura de Robert C. Martin **[referência]** que organiza um sistema em
  círculos concêntricos, do mais estável, no centro, ao mais volátil, na borda. O DC a adota para
  organizar o método.
- **Como funciona:**
  - As camadas, do centro para a borda, e o que cada uma é no DC (seção 4):

    | Camada | No DC | Muda quando |
    |---|---|---|
    | Entidades | o codex: conceitos, contratos e gates | o método muda |
    | Casos de uso | os workflows e as etapas | um workflow muda |
    | Adaptadores | scripts, hooks e formatos de arquivo | o formato ou o Claude Code muda |
    | Frameworks | Claude Code, git e runners de teste | fora do controle do DC |

  - A regra de dependência: as dependências só apontam para dentro (I-54).
  - O ganho **[referência]**: o centro fica independente de detalhe, testável e durável. No DC, é
    isso que torna o codex à prova de futuro.
  - Onde vale (decisão 7): no método, sempre; no código do plugin, onde um script estiver causando
    problema; no projeto, é guideline de quem a adota.
  - O que "o decode a segue" significa na prática: —
- **Relações:** as entidades são o codex (I-27); os casos de uso são os workflows (I-04); a regra é
  a regra de dependência (I-54); no projeto, é guideline (I-23); o decode a segue (I-06).
- **Origem:** seção 1 (*Restrições*); seção 4; decisão 7; decidido em 2026-11-24.

#### I-54 Regra de dependência

- **O que é:** a regra central da Clean Architecture **[referência]**: as dependências só apontam
  para dentro, e o que está dentro não sabe nada do que está fora.
- **Como funciona:**
  - O codex não cita skill, script, hook, versão do Claude Code nem projeto.
  - As skills citam o codex, e os scripts o implementam.
  - O núcleo nunca importa um módulo.
  - O que envelhece rápido fica na borda; é isso que torna o codex à prova de futuro.
  - Um lint confere que o codex não cita mecanismo.
  - Teste para cada trecho do codex: ele continuaria verdadeiro se o script, a skill ou a versão do
    Claude Code mudassem? Se não, não é codex.
  - A norma atual a quebra nos 27% das linhas que descrevem mecanismo.
- **Relações:** vale para o codex (I-27); é a regra da Clean Architecture (I-53); no nível dos
  módulos, o núcleo nunca importa um módulo (I-58).
- **Origem:** seção 1 (*Restrições*); seção 4; decidido em 2026-11-24.

#### I-55 Invariante

- **O que é:** uma regra que vale sempre: uma fonte por fato; nada específico de projeto viaja no
  plugin.
- **Como funciona:**
  - Uma fonte por fato: nenhum trecho do codex aparece repetido na foundation nem nas skills; um
    lint confere a repetição literal.
  - Nada do projeto no plugin: a auditoria do pacote hoje só procura o nome deste repositório; dado de
    outro projeto precisa entrar na mesma auditoria.
  - Instruções em conflito não têm vencedor; por isso nada do projeto, nem rules nem foundation, pode
    repetir ou contradizer o codex.
- **Relações:** protege o codex (I-27) e a foundation (I-26); a lista de tipos fica fora do codex por
  causa dela; o projeto não altera o codex (I-56).
- **Origem:** seção 1 (*Restrições*); seção 3; seção 5.

#### I-56 Restrição fundamental

- **O que é:** o projeto não altera o codex.
- **Como funciona:**
  - O codex só existe no plugin, e nenhum comando do DC o copia para o projeto.
  - Consequência: o bootstrap deixa de copiar a norma.
  - Tradeoff aceito: fora de uma skill do DC, Claude não vê o método.
- **Relações:** protege o codex (I-27); a foundation, que o projeto altera, é a outra camada (I-26);
  a migração remove a cópia antiga (I-42); só o mantenedor altera o codex (I-61).
- **Origem:** seção 1 (*Restrições*, *Duas camadas*); decisão 1.

#### I-58 Núcleo

- **O que é:** o DC sem módulos.
- **Como funciona:**
  - Nunca importa um módulo.
  - Procura as pastas que têm `module.json` e só elas viajam no pacote; não há lista central.
  - Recusa um módulo que exige outra versão dele, e diz por quê.
  - A suíte do núcleo continua passando sem qualquer módulo; incluir um módulo não exige editar o
    núcleo.
  - O núcleo do codex fica na pasta compartilhada das skills.
- **Relações:** descobre os módulos (I-34); o módulo o usa; o núcleo do codex (I-27); mantido
  por I-61; a regra de dependência vale entre núcleo e módulo (I-54).
- **Origem:** seção 1 (*Restrições*, *Módulos*); seção 5; decisão 14.

#### I-59 Tabela de recursos do plano

- **O que é:** a tabela no plano que registra as skills do projeto pelo nome.
- **Como funciona:**
  - Registra só o nome pelo qual a skill é invocada, o tipo e onde entra na entrega; sem conteúdo,
    linha ou versão.
  - Um script a lê.
  - Um lint cruza a tabela com a descoberta de recursos na revisão, no derive e na entrada do code.
  - No decode, o nome vai para a tabela.
- **Relações:** faz parte do plano (I-11); registra recursos do projeto (I-30); orienta-se pelo mapa
  de recursos (I-29); é preenchida no decode (I-06) e conferida na revisão (I-07), no derive
  (I-08) e no code (I-09); diz onde cada recurso entra na entrega.
- **Origem:** seção 1 (*Organização dos planos*); seção 3; decisão 12.

#### I-60 Objetivo do plano

- **O que é:** o que o plano quer atingir, claro para o usuário e para Claude.
- **Como funciona:**
  - É uma das saídas da etapa 2 da entrada, ao lado do workflow que o plano segue.
- **Relações:** sai da etapa de tipo (I-03); é do plano (I-11); parte do pedido (I-01).
- **Origem:** seção 1 (*Entrada, comum aos dois workflows*, etapa 2).
- **Decidido em 2026-11-24:** uma frase que o usuário confirma na etapa de tipo, distinta do objetivo do DC.

#### I-61 Quem mantém o plugin

- **O que é:** o único ator que altera o codex e inclui ou remove módulos.
- **Como funciona:**
  - Altera o codex a cada versão do plugin.
  - Inclui e remove módulos; o projeto que usa o DC não liga nem desliga módulo.
  - Empacotamento e release ficam fora do codex, como documentação de manutenção.
- **Relações:** altera o codex (I-27) e os módulos (I-34); o projeto e o usuário não o fazem (I-35,
  I-56).
- **Origem:** seção 1 (*Duas camadas*, *Módulos*); seção 3; seção 5.

#### I-62 Os quatro riscos

- **O que é:** a referência de Marty Cagan: validar valor, usabilidade, viabilidade técnica e
  viabilidade de negócio.
- **Como funciona:**
  - É a pauta do trio PM, Designer e Tech Lead.
  - Apoia o decode.
- **Relações:** referência de produto (I-32) do decode (I-06); a pauta é dos papéis (I-31).
- **Origem:** seção 1 (*Referências de produto*).

#### I-63 Hipótese

- **O que é:** uma suposição explícita sobre o efeito de uma mudança, escrita de forma que possa se
  provar errada, com o sinal que vai confirmá-la ou refutá-la.
- **Modelo básico [referência]** (Barry O'Reilly, *Hypothesis-Driven Development*):

  > Acreditamos que **<mudança>**, para **<quem>**, vai resultar em **<resultado>**.
  > Teremos confiança para seguir quando **<sinal mensurável>**, até **<prazo ou ponto de
  > verificação>**.

- **Como funciona:**
  - Cada hipótese tem um resultado só.
  - O sinal é definido antes de construir.
  - A hipótese pode ser refutada: se nenhum resultado a contradiz, não é hipótese.
  - **[referência]** (Eric Ries, Lean Startup): há duas hipóteses de partida, a de valor (a pessoa
    ganha algo ao usar) e a de crescimento (como novas pessoas chegam). O ciclo é construir, medir e
    aprender.
  - No DC, a proposta declara a hipótese, e o sinal se liga à métrica que o *Clarificar* pergunta.
    Para uma skill ou um plugin, o "quem" é quem usa o recurso.
  - Exemplo: "Acreditamos que executar médio e grande numa sessão nova, para quem usa o DC, vai
    reduzir o consumo de tokens por unidade. Teremos confiança para seguir quando o consumo médio
    cair nos próximos 5 planos."
- **Relações:** é testada pelo MVP (I-66); a hipótese de valor é o primeiro dos quatro riscos
  (I-62); o sinal se liga ao *Clarificar* (I-50); é declarada no decode (I-06); faz parte do
  mindset de produto (I-33); referência de produto (I-32).
- **Origem:** seção 1 (*Referências de produto*); decidido em 2026-11-24.

#### I-64 Teste do plano inteiro

- **O que é:** o teste P8, feito sobre o plano como um todo.
- **Como funciona:**
  - Só vale quando o plano tem mais de uma unidade.
  - Só roda depois que todas as unidades forem concluídas.
  - Claude ou o usuário o faz.
- **Relações:** é um teste (I-19); testa o plano (I-11) do porte grande (I-14); vem depois das
  entregas aprovadas (I-18).
- **Origem:** seção 1 (P8); decisão 4.

#### I-65 Teste que reproduz o defeito

- **O que é:** o teste C4 da correção: falha antes da correção e passa depois.
- **Como funciona:**
  - Verifica a correção; sem ele a correção não é verificada.
  - Claude ou o usuário o faz.
- **Relações:** é um teste (I-19); verifica a correção (I-39); o plano mínimo diz como reproduzir o
  defeito (I-13).
- **Origem:** seção 1 (C4, *Workflow de correção*).

#### I-66 MVP

- **O que é [referência]** (Eric Ries): a menor versão que testa uma hipótese com o mínimo de
  esforço, feita para aprender e não para ser o produto final.
- **Como funciona:**
  - Parte de uma hipótese: o MVP é o mínimo que produz o sinal que ela define. Sem hipótese, não é
    MVP, é só uma versão menor.
  - O "mínimo" se mede pelo aprendizado, e não pelo escopo: precisa ser bom o bastante para gerar
    um sinal real.
  - Formas comuns **[referência]**: protótipo; concierge, o serviço feito à mão; Mágico de Oz, que
    parece automático mas é manual; teste de demanda.
  - Depois de medir **[referência]**: perseverar, pivotar ou parar.
  - Não é o *Reduzir*, que mira o escopo (a menor versão que resolve 80%), e não é o porte pequeno,
    que é tamanho do plano.
  - No DC (proposta, sem fonte): a proposta declara o MVP junto com a hipótese, e a aprovação da
    entrega é o ponto em que se mede.
- **Relações:** testa a hipótese (I-63); difere do *Reduzir* (I-50) e do porte (I-14); é declarado
  no decode (I-06); a medição acontece na aprovação (I-18); faz parte do mindset de produto (I-33);
  referência de produto (I-32).
- **Origem:** seção 1 (*Referências de produto*); criado na fase 2, ao separar hipótese e MVP;
  decidido em 2026-11-24.
