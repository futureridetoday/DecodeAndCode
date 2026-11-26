---
# about
name: atomic-inventory
type: doc
project: ""
description: Inventário dos conceitos do codex e fonte da verdade do redesign — o que é cada item, como funciona, o mecanismo de hoje, as relações e a origem; vale sobre o brief onde os dois divergem
tags: [codex, redesign, atomic-design, inventario]

# history
author: Bortoli
created: 2026-11-24
status: draft
version: 0.23.0
updated: ""

# system
scope: project
source: ""
auto_load: false
checksum: ""
dependencies: [redesign-brief]
---

# Inventário atômico do codex

**Estado:** registro desde 2026-11-26. O codex, em `.claude/skills/decode-and-code/codex/`, passou
a ser a fonte da verdade do método no fechamento da parte 1.3 do [plano do redesign](redesign-plan.md)
(D-10); onde o codex e este inventário divergem, vale o codex.

Os conceitos de que o codex é feito, um por item. Foi a fonte da verdade do redesign até o codex ser
escrito: o plano do redesign parte dele e do [brief](redesign-brief.md). Onde os dois divergem, vale
o inventário, porque a divergência vem de uma decisão da pessoa, registrada com a data.

## Como ler

- **Cada item** traz o que é, como funciona, o mecanismo de hoje, as relações com outros itens pelo
  número e a origem no brief.
- **Mecanismo hoje** guarda a implementação atual (script, hook, skill, arquivo), que o codex não
  cita (54).
- **Fontes**, nesta ordem: o brief, sem marca; a decisão da pessoa, com a data (*decidido em*); o
  projeto, marcado **[projeto]**; e a referência de produto citada, marcada **[referência]**. Sem
  fonte, o campo fica com "—".
- **Numeração:** os números não são reaproveitados. Saíram os itens 10, 17, 20, 25, 40 e 57, e o 66
  (MVP) nasceu da separação do 63. O 67 (Proposta), o 68 (Entrega) e o 69 (Critério de aceite)
  nasceram na parte 1.2 do plano do redesign, no lugar dos conceitos que o 10, o 17 e o 20 tinham;
  o 70 (Lacuna) e o 71 (Numeração e nomenclatura) também nasceram nela.

## Inventário atômico

### 01 - Pedido

- **O que é:** o que a pessoa traz para o DC e que dá início a um plano. É a primeira etapa dos dois
  workflows, a entrada (etapa 1), e o objeto que o DC decodifica.
- **Como funciona:**
  - A entrada pode ser um pedido, blocos de texto para juntar ou um insight para discutir.
  - Sai dela um pedido único, ou uma conversa que termina sem plano.
  - Quem participa são o usuário e Claude.
  - No paralelo com produto digital, corresponde ao pedido que stakeholders e squad escrevem.
  - O objetivo do DC é decodificar o pedido: entender, validar e planejar.
- **Relações:** pode ser um insight (02); depois dele vem a escolha do tipo (03); é a etapa
  inicial de todo workflow (04, 05); dele nasce o plano (11); é decodificado no decode (06);
  vem do usuário (35); o paralelo com produto digital o relaciona à entrada (51).
- **Origem:** seção 1 (*Missão*, *Objetivo do DC*, *Entrada, comum aos dois workflows*, *O
  paralelo*).

### 02 - Insight

- **O que é:** uma das formas de entrada: algo para discutir, sem ser ainda um pedido.
- **Como funciona:**
  - O DC conversa sobre ele e só abre plano se ele virar um pedido (decidido em 2026-11-24).
  - Pode terminar numa conversa sem plano.
- **Relações:** é uma forma de entrada (01); se virar pedido, segue para a escolha do tipo (03).
- **Origem:** seção 1 (*Entrada, comum aos dois workflows*, etapa 1).

### 03 - Tipo

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
- **Relações:** escolhe o workflow (04) e, com ele, a correção (39) ou o produto; vem de uma
  lista; é identificado por Claude (36) e pode ser corrigido pelo usuário (35); é declarado no
  plano (11); define o objetivo do plano junto com o pedido (60); vem depois do pedido (01) e
  antes do decode (06).
- **Origem:** seção 1 (*Entrada, comum aos dois workflows*, *O que muda*, *Restrições*); decisões 5
  e 6.

### 04 - Workflow

- **O que é:** a sequência de etapas que um plano segue, escolhida pelo tipo.
- **Como funciona:**
  - Por enquanto são dois: o de correção, para `fix`, e o de produto, para os demais tipos.
  - No código, os identificadores são `fix`, para o de correção, e `product`, para o de produto
    (decidido em 2026-11-24).
  - Os dois começam pela mesma entrada (etapas 1 e 2).
  - Outros tipos podem ganhar workflow próprio depois.
  - Na Clean Architecture do DC, os workflows e suas etapas são os casos de uso; mudam quando um
    workflow muda ou um tipo ganha workflow próprio.
  - O workflow de correção é o primeiro módulo.
- **Relações:** é escolhido pelo tipo (03); é feito de etapas (05); o de correção é o item 39 e o de
  produto passa por decode (06), revisão (07), derive (08) e code (09); é seguido pelo
  plano (11); o workflow de correção é o primeiro módulo (34); é caso de uso na Clean
  Architecture (53).
- **Origem:** seção 1 (*Workflow*, *Módulos*); seção 4; decisão 5.

### 05 - Etapa

- **O que é:** um passo de um workflow, descrito com quem a executa e o que sai dela.
- **Como funciona:**
  - Os workflows são tabelas de etapas: entrada (1 e 2), correção (C1 a C4) e produto (P1 a P8).
  - Cada etapa diz quem a faz (Claude, usuário ou os dois) e o que produz.
- **Relações:** compõe o workflow (04); as etapas nomeadas no codex são o decode (06), a revisão
  (07), o derive (08) e o code (09); algumas etapas são aprovações (18).
- **Origem:** seção 1 (*Entrada*, *Workflow de correção*, *Workflow de produto*).

### 06 - Decode

- **O que é:** a primeira etapa do workflow de produto (P1): a em que Claude entende o pedido e
  propõe uma solução conceitual. Substitui o `intake`.
- **Como funciona:**
  - Claude atua no papel de PM, Designer e Tech Lead.
  - Usa o mindset de produto, a foundation, os princípios, as guidelines e os guardrails, e as
    skills e os recursos do projeto.
  - Apoia-se nas referências de produto.
  - Sai uma proposta de solução conceitual, com referências técnicas, escrita para o usuário.
  - As skills do projeto são invocadas pelo nome, nunca lidas e copiadas; o nome vai para a tabela
    do plano.
  - O fluxo de decodificação de hoje (Clarificar, Evitar, Reduzir) é a semente do decode.
  - Gate de saída: a proposta só vai à aprovação (P2) se passa nos dois gates. A, necessidade real:
    o problema é de alguém agora, e a hipótese tem sinal mensurável (63). B, mínimo viável: é a menor
    versão que resolve, com o que fica de fora declarado (50, 67) (decidido em 2026-11-25).
  - Na correção, o decode é enxuto: identificar o problema e criar a correção.
- **Relações:** vem depois do tipo (03); produz a proposta, que o usuário aprova (18);
  segue-se a revisão (07); usa o mindset de produto (33), os papéis (31), as referências de
  produto (32), os quatro riscos (62), a foundation (26), princípios, guidelines e
  guardrails (22, 23, 24) e os recursos do projeto (30, 59); sua semente é o fluxo de
  decodificação (50).
- **Origem:** seção 1 (P1, *Referências de produto*, *O que muda*, *Workflow de correção*); decisões
  7 e 12.

### 07 - Revisão

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
  - Confere se os recursos do projeto citados no plano existem.
- **Mecanismo hoje:** um lint cruza a tabela de recursos do plano com a descoberta de recursos do
  projeto.
- **Relações:** vem depois da aprovação da proposta (18); escreve histórias (37); quebra
  em tarefas (16); produz o plano técnico (12) e define o porte (14); confere a independência
  entre planos (46); usa as referências de produto
  (32); confere os recursos do projeto (59); os papéis (31).
- **Origem:** seção 1 (P3, *Referências de produto*); seção 3; decisões 2 e 12.

### 08 - Derive

- **O que é:** a etapa P5 do workflow de produto: prepara cada unidade para ser executada. Só existe
  no médio e no grande.
- **Como funciona:**
  - Entrega cada unidade com contexto, memória e o padrão de código do projeto. A memória são as
    decisões e lacunas que o plano já registrou e que a unidade precisa conhecer (decidido em
    2026-11-24).
  - Garante que a unidade baste sozinha (cold-start).
  - Termina com a aprovação das unidades derivadas pelo usuário (decidido em 2026-11-24).
  - No paralelo com produto digital, é o momento em que a história fica pronta para desenvolver.
  - No médio e no grande, produz o handoff, que leva a execução para uma sessão nova.
  - Cita na unidade as guidelines aplicáveis, que o code recebe.
  - Confere se os recursos do projeto citados ainda existem.
- **Mecanismo hoje:** um lint confere os nomes dos recursos do projeto.
- **Relações:** vem depois do plano técnico aprovado (12, 18) e termina numa aprovação (18);
  prepara a unidade (15); garante a Definition of Ready (38) e o cold-start (44); produz o
  handoff (45); usa o padrão de código (28) e a foundation (26); cita guidelines (23) e
  confere recursos do projeto (59); antecede o code (09).
- **Origem:** seção 1 (P5, *Porte*, *O paralelo*); seção 3; decisões 8 e 12.

### 09 - Code

- **O que é:** a etapa de execução (C3 na correção, P6 no produto): Claude escreve o que o plano
  pede. Substitui o `implement`.
- **Como funciona:**
  - Usa as skills e os recursos do projeto.
  - No pequeno, as tarefas rodam na mesma sessão. No médio e no grande, uma unidade por vez, e o
    plano recebe a recomendação de ser executado numa sessão nova (decidido em 2026-11-24): a
    unidade traz o que precisa para o cold-start, e começar sem o histórico economiza tokens.
  - Gate de entrada: não começa sem critério de aceite (69). Gate de saída: não fecha sem teste e sem a aprovação do
    usuário (P7).
  - A unidade roda sem o histórico da conversa.
  - Na entrada, confere se os recursos do projeto citados ainda existem; as guidelines que ligam
    caminhos a recursos do projeto continuam valendo.
  - Unidade insuficiente vira lacuna (70).
- **Mecanismo hoje:** a skill `implement` roda num subagente (fork); um lint confere os nomes dos
  recursos na entrada; a guideline-ponte liga caminhos a recursos do projeto.
- **Relações:** executa tarefas (16) ou uma unidade (15); vem depois do plano mínimo aprovado
  (13) ou do derive (08); é seguido do teste (19) e da aprovação (18); usa os recursos do
  projeto (30, 59) e as guidelines (23); obedece ao cold-start (44); executa o Claude
  (36).
- **Origem:** seção 1 (C3, P6, P7, *O que muda*); seção 3; decisão 12.

### 11 - Plano

- **O que é:** o registro do que vai ser feito para atender a um pedido. No paralelo com produto
  digital, corresponde à proposta.
- **Como funciona:**
  - Tem um tipo, que escolhe o workflow.
  - No workflow de produto, começa como proposta conceitual no decode (P1), é aprovado (P2) e vira
    plano técnico na revisão (P3), com tarefas ou unidades conforme o porte.
  - Recebe número na aprovação do plano que vai ser executado: o plano técnico, no produto (P4,
    decisão 2), ou o plano mínimo, na correção (C2). Uma correção que passa para o workflow de
    produto recebe número em P4 (decidido em 2026-11-25).
  - O plano grande é testado inteiro no fim (P8); todo plano fecha com a aprovação final.
  - Todos os planos ficam juntos em `<plan_root>/`. O pequeno é um arquivo; o médio e o grande são
    uma pasta com o plano e as unidades.
  - O campo `core:` diz a que parte do sistema o plano se refere.
  - Todo plano novo declara a versão do formato (decisão 3).
- **Relações:** nasce de um pedido (01); tem um tipo (03) e um porte (14); segue um workflow
  (04); passa por proposta e plano técnico (12), ou é plano mínimo na correção (13); é
  feito de tarefas (16) ou unidades (15); é aprovado (18); é testado inteiro (64); mora na
  raiz dos planos (43); registra os recursos do projeto na tabela de recursos (59); os planos
  antigos seguem regra própria (41).
- **Origem:** seção 1 (*Workflow*, *Porte*, *Organização dos planos*); decisões 2, 3 e 7.

### 12 - Plano técnico

- **O que é:** o que sai da revisão (P3): o plano, com tarefas ou unidades conforme o porte.
- **Como funciona:**
  - É aprovado pelo usuário em P4, e é nessa aprovação que o plano recebe número.
  - Só depois da aprovação vem o derive, no médio e no grande.
  - O porte só se define na revisão; plano sem porte não é aprovado.
- **Relações:** nasce da proposta pela revisão (07); é aprovado (18); contém tarefas
  (16) ou unidades (15), conforme o porte (14); é o plano que segue para o derive (08);
  registra os recursos do projeto na tabela (59); parte do plano (11).
- **Origem:** seção 1 (P3, P4); decisão 2.

### 13 - Plano mínimo

- **O que é:** o plano pequeno com uma única tarefa. É o mesmo plano que o pequeno; muda só o
  conteúdo (decidido em 2026-11-24).
- **Como funciona:**
  - As seções são: o problema e como reproduzi-lo, a correção, e como verificar.
  - É registrado no diagnóstico (C1) e aprovado pelo usuário antes do code (C2).
  - Se o diagnóstico mostrar que a correção não é pequena, ela passa para o workflow de produto.
  - A correção gera plano registrado (decisão 9).
- **Relações:** é o plano (11) do workflow de correção (39); tem o porte pequeno (14); é
  aprovado (18); é codado (09) e verificado pelo teste que reproduz o defeito (65).
- **Origem:** seção 1 (*Workflow de correção*, C1, C2); decisões 9 e 10.

### 14 - Porte

- **O que é:** o tamanho do plano: pequeno, médio ou grande, e só esses três. Vale nos dois
  workflows: a correção usa o pequeno com uma única tarefa, o plano mínimo.
- **Como funciona:**
  - Pequeno: lista de tarefas, sem derive, executada na mesma sessão logo após a aprovação do plano
    técnico.
  - Médio: 1 unidade, com derive, numa sessão nova, aprovada ao final.
  - Grande: 2 ou mais unidades, com derive, numa sessão nova, uma por vez, cada uma depois da
    aprovação da anterior.
  - Define-se na revisão.
  - Não há limite de tarefas por unidade: a unidade tem as tarefas necessárias para produzir a sua
    entrega (68) (decidido em 2026-11-24).
  - Um plano sem porte não é aprovado.
- **Mecanismo hoje:** o porte medido continua onde está, aplicado por script.
- **Relações:** é definido na revisão (07); determina se o plano passa pelo derive (08); fixa a
  estrutura do plano (11) em tarefas (16) ou unidades (15); o médio e o grande têm handoff
  (45); só o grande tem teste do plano inteiro (64); o mínimo é o pequeno (13).
- **Origem:** seção 1 (*Porte, no workflow de produto*); seção 3 (*Porte medido*); decisões 2 e 3.

### 15 - Unidade

- **O que é:** uma lista de tarefas que, no fim, produz uma entrega (68).
- **Como funciona:**
  - Tem as tarefas necessárias para produzir a entrega; não há limite de tarefas (decidido em
    2026-11-24).
  - O médio tem 1 unidade, e o grande, 2 ou mais.
  - O derive dá a cada unidade o contexto, a memória e o padrão de código do projeto (P5).
  - O code executa uma unidade por vez (P6).
  - Só começa com critério de aceite (69) e só fecha com teste e aprovação do usuário.
  - A próxima unidade só começa depois que a anterior é aprovada (P7).
  - Basta sozinha e roda sem o histórico da conversa (seção 3, cold-start).
  - Unidade insuficiente vira lacuna (70).
- **Mecanismo hoje:** a aprovação fica nos campos `approved_by` e `approved_at` da unidade.
- **Relações:** é feita de tarefas (16); produz uma entrega (68); pertence a um plano médio ou
  grande (11, 14); é preparada no derive (08) e executada no code (09); começa com um
  critério de aceite; fecha com teste (19) e aprovação (18); corresponde a uma história
  (37); obedece ao cold-start (44); é orquestrada pelo handoff (45).
- **Origem:** seção 1 (*Porte*, *Unidade*, *O que muda*, P5 a P7); seção 3; decisão 3.

### 16 - Tarefa

- **O que é:** a menor ação do trabalho, que o code executa de uma vez e cujo resultado
  se consegue conferir (decidido em 2026-11-24).
- **Como funciona:**
  - A revisão quebra o trabalho em tarefas (P3).
  - No pequeno, as tarefas são executadas na mesma sessão, logo após a aprovação do plano técnico.
- **Relações:** compõe a unidade (15) e o plano pequeno (11, 14); é criada na revisão
  (07); é executada no code (09).
- **Origem:** seção 1 (P3, P6, *Porte*, *O paralelo*).
- **Nota [projeto]:** na norma atual, passo é a sequência numerada dentro da unidade, com teto de 8,
  e tarefa é a lista de caixas `## Tarefas` do plano médio. O brief e a junção unificam os dois.

### 18 - Aprovação

- **O que é:** o momento em que o usuário aceita o resultado de uma etapa do workflow do plano; a
  etapa seguinte só começa depois dela.
- **Como funciona:**
  - No workflow de produto, na ordem:
    1. A proposta, no fim do decode (P2).
    2. O plano técnico, no fim da revisão; é nela que o plano recebe número (P4, decisão 2).
    3. As unidades derivadas, no fim do derive (decidido em 2026-11-24; o brief não tem esta
       aprovação).
    4. Cada entrega, no code: fecha a unidade junto com o teste; a próxima unidade só começa
       depois (P7).
    5. A aprovação final, que fecha o plano (decidido em 2026-11-24). No grande, vem depois do
       teste do plano inteiro (P8). No pequeno, vem depois do teste da entrega, e é a única
       aprovação depois do code. No médio, a aprovação da única entrega é também a aprovação final
       (decidido em 2026-11-25).
  - No workflow de correção, na ordem:
    1. O plano mínimo, antes do code; é nela que o plano recebe número (C2, decisão 10).
    2. A aprovação final, depois do teste que reproduz o defeito (decidido em 2026-11-24; o brief
       só tem o teste, C4).
  - Quem aprova é sempre o usuário.
  - As escritas do DC no projeto (foundation, permissão de uso de skill, migração) também pedem o
    sim da pessoa, mas não são aprovação do workflow; cada item as descreve.
- **Mecanismo hoje:** a aprovação da unidade fica nos campos `approved_by` e `approved_at`; a
  permissão de uso de skill é uma regra `Skill(<nome>)` no `settings.json` do projeto.
- **Relações:** é dada pelo usuário (35); fecha o decode (06), a revisão (07), o derive (08)
  e o code (09); aprova o plano técnico (12), o plano mínimo (13) e a unidade (15); vem
  depois do teste (19, 64, 65); abre a numeração do plano (11).
- **Origem:** seção 1 (C2, P2, P4, P7, P8, *O que muda*); decisões 2, 4 e 10; decidido pela pessoa
  em 2026-11-24.

### 19 - Teste

- **O que é:** a verificação de que uma entrega, uma correção ou o plano inteiro funciona; é feita
  pelo Claude ou pelo usuário.
- **Como funciona:**
  - Acontece em três momentos: o teste que reproduz o defeito (C4), o teste da entrega, antes da
    aprovação (P7), e o teste do plano inteiro (P8).
  - A unidade não fecha sem teste e sem a aprovação do usuário.
  - O estado de uma unidade é derivado do teste, nunca editado à mão.
  - No pequeno e no médio, o teste da entrega é também o teste do plano (decidido em 2026-11-25).
- **Relações:** verifica a correção (39, 65), a entrega (68) e o plano inteiro (64); precede
  a aprovação (18); fecha a unidade (15) junto com ela; é feito pelo usuário (35) ou por
  Claude (36); confere o critério de aceite (69).
- **Origem:** seção 1 (C4, P7, P8, *Unidade*); seção 3; decisão 4.

### 21 - Huddle

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
- **Relações:** acontece entre Claude (36) e o usuário (35); o que se aprende vira guideline
  (23), guardrail (24) ou feedback ao método no registro de uso (47); mora na raiz dos planos
  (43); o setup o inicia (48).
- **Origem:** definição da pessoa em 2026-11-24; o funcionamento vem do projeto. O brief só diz
  onde o huddle mora (seção 3).

### 22 - Princípio

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
- **Relações:** é do projeto (26 só o menciona); o decode o usa (06); setup (48) e rethink
  (49) o criam e revisam; irmão da guideline (23) e do guardrail (24).
- **Origem:** seção 1 (*Duas camadas*, *Workflow de produto*); seção 5; decidido em 2026-11-24.

### 23 - Guideline

- **O que é:** uma diretriz técnica do projeto, que vale para os arquivos que casam com um
  padrão.
- **Como funciona:**
  - A guideline-ponte nomeia o recurso do projeto para os caminhos onde ele vale; o derive a cita
    na unidade e o code a recebe.
  - A Clean Architecture, no projeto, é guideline de quem a adota.
  - O decode a usa.
- **Mecanismo hoje:** rule com `paths` em `.claude/rules/`, que carrega quando Claude lê ou edita um
  arquivo que casa com o padrão; frontmatter inválido faz a guideline carregar sempre, e por isso o
  lint continua necessário; subdiretórios de `.claude/rules/` também carregam.
- **Relações:** é do projeto; usada no decode (06), citada no derive (08) e recebida no code
  (09); a ponte liga recursos do projeto (30); irmã do princípio (22) e do guardrail (24);
  Clean Architecture no projeto (53); criada e revisada pelo setup (48) e pelo rethink (49).
- **Origem:** seção 1 (*Duas camadas*); seção 3; seção 5; decisões 7 e 12.
- **Nota [projeto]:** a norma a descreve como "como técnico"
  (`docs/plan/system/modelo-dev-units.md:190-195`).

### 24 - Guardrail

- **O que é:** uma regra do projeto que não pode depender de Claude lembrar: é imposta.
- **Como funciona:**
  - Bloqueia a ação independentemente da decisão de Claude.
  - As regras são do projeto; o que as impõe é do plugin.
  - O decode o usa.
- **Mecanismo hoje:** o hook `PreToolUse`, que a documentação do Claude Code manda usar para
  bloquear; as regras ficam em `.claude/guardrails.json`.
- **Relações:** é do projeto; usado no decode (06); criado e revisado pelo setup (48) e pelo
  rethink (49); irmão do princípio (22) e da guideline (23).
- **Origem:** seção 3; seção 5.
- **Nota [projeto]:** a norma o descreve como "limite verificável"
  (`docs/plan/system/modelo-dev-units.md:190-195`).

### 26 - Foundation

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
- **Relações:** é uma camada (52), par do codex (27); contém o padrão de código (28) e o mapa
  de recursos (29); é lida pelo decode (06) e pelo derive (08); escrita pelo setup (48),
  pelo rethink (49) e pelo plano; mora na raiz dos planos (43); obedece à uma fonte por fato
  (55).
- **Origem:** seção 1 (*Duas camadas*); seção 5; decisão 8; decidido em 2026-11-24.

### 27 - Codex

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
  - É à prova de futuro pela regra de dependência.
  - Substitui a norma por completo, inclusive nos projetos que já usam o DC.
  - Na Clean Architecture, é a camada das entidades.
- **Mecanismo hoje:** um lint confere que o codex não cita mecanismo.
- **Relações:** é uma camada (52), par da foundation (26); é mantido por quem mantém o plugin
  (61); nenhum projeto o altera (56); obedece à regra de dependência (54) e aos invariantes
  (55); contém as referências de produto (32) e o fluxo de decodificação (50); evolui pelo
  registro de uso (47); substitui a norma na migração (42); é a camada das entidades na Clean
  Architecture (53).
- **Origem:** *Ponto de partida*; seção 1 (*Missão*, *Duas camadas*, *Restrições*); seções 3, 4 e
  5; decisões 1, 11 e 13.

### 28 - Padrão de código

- **O que é:** o estilo de código do time do projeto, que o derive garante que a unidade siga.
- **Como funciona:**
  - É conteúdo da foundation.
  - No redesign, a foundation só reserva o lugar.
  - Extrair o padrão do código existente, com o setup propondo e a pessoa aprovando, é módulo para
    depois da versão 1.
- **Relações:** faz parte da foundation (26); entra na unidade pelo derive (08); o setup propõe
  extraí-lo (48), com o sim da pessoa; a extração é módulo futuro (34).
- **Origem:** seção 1 (*Duas camadas*, P5); seção 3; decisões 8 e 14.

### 29 - Mapa de recursos do projeto

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
- **Relações:** faz parte da foundation (26); lista os recursos do projeto (30); orienta o
  decode (06), a revisão (07) e o code (09); alimenta a tabela de recursos do plano (59); é
  escrito pelo setup (48) e atualizado pelo rethink (49).
- **Origem:** seção 1 (*Duas camadas*); seção 5; decisões 8 e 12; decidido em 2026-11-24.

### 30 - Recurso do projeto

- **O que é:** o que o projeto já tem para o Claude usar: skills, commands, MCP e o `CLAUDE.md`. É
  do projeto, fora do codex e da foundation.
- **Como funciona:**
  - O DC chama o recurso pelo nome e nunca copia o conteúdo dele, porque o recurso continua
    evoluindo no projeto.
  - O DC só cria ou remove um recurso pelo rethink, com o sim da pessoa.
  - Cada plano registra, pelo nome, os recursos que usa.
- **Relações:** é do projeto, fora do codex (27) e da foundation (26), que só o mapeia (29);
  é usado no decode (06) e no code (09); é registrado na tabela de recursos do plano (59); é
  criado ou removido pelo rethink (49).
- **Origem:** seção 1 (*Duas camadas*, *O que muda*); seção 5; decisão 12; decidido em 2026-11-24.

### 31 - Papel

- **O que é:** o chapéu que Claude veste numa etapa: PM, Designer ou Tech Lead.
- **Como funciona:**
  - No decode, Claude atua como PM, Designer e Tech Lead.
  - Na revisão, como PM e Tech Lead.
  - O trio PM, Designer e Tech Lead é a pauta dos quatro riscos.
- **Relações:** exercido por Claude (36) no decode (06) e na revisão (07); o trio faz a pauta
  dos quatro riscos (62); corresponde, no paralelo, a quem propõe e refina (51).
- **Origem:** seção 1 (P1, P3, *Referências de produto*, *O paralelo*).

### 32 - Referência de produto

- **O que é:** uma referência consagrada de criação de produto digital em que o decode e a revisão
  se apoiam. Ficam no próprio codex.
- **Como funciona:**
  - No decode: Jobs to Be Done, Design Thinking e Double Diamond, Lean Startup, os quatro riscos de
    Cagan e Shape Up.
  - Na revisão: histórias de usuário e INVEST, e User Story Mapping.
  - Cada uma traz algo específico: por exemplo, o JTBD descreve o problema pelo que a pessoa quer
    realizar.
- **Relações:** moram no codex (27); apoiam o decode (06) e a revisão (07); incluem os quatro
  riscos (62), a hipótese (63), o MVP (66), a história (37) e a proposta (via Shape Up); a
  semente delas é o fluxo de decodificação (50); o mindset de produto as sustenta (33).
- **Origem:** seção 1 (*Referências de produto*); decisão 11.

### 33 - Mindset de produto

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
- **Relações:** orienta o decode (06); reúne as referências de produto (32), os quatro riscos
  (62), a hipótese (63) e o MVP (66); usa o fluxo de decodificação (50); o paralelo com
  produto digital é só orientação (51).
- **Origem:** seção 1 (P1, *Referências de produto*, *O paralelo*); decidido em 2026-11-24,
  substituindo a decisão anterior de que o mindset não ganha conteúdo próprio.

### 34 - Módulo

- **O que é:** a forma como funcionalidade nova entra no DC sem alterar o núcleo.
- **Como funciona:**
  - Incluir ou remover um módulo não quebra o DC nem os outros módulos.
  - Só quem mantém o plugin inclui ou remove módulos.
  - Um módulo pode trazer o trecho do codex da funcionalidade dele.
  - O primeiro módulo é o workflow de correção.
  - O contrato técnico (manifesto, descoberta, versão) é arquitetura do plugin, não do método: fica
    na documentação de manutenção, fora do codex (decidido em 2026-11-24).
- **Relações:** o núcleo (58) não depende dele; é incluído e removido por quem mantém o plugin
  (61); o primeiro é a correção (39); o padrão de código extraído do projeto é módulo futuro
  (28).
- **Origem:** seção 1 (*Restrições*, *Módulos*); decisão 14; decidido em 2026-11-24.

### 35 - Usuário

- **O que é:** a pessoa que usa o DC; é um dos dois atores do workflow.
- **Como funciona:**
  - Pede: traz o pedido, os blocos de texto ou o insight.
  - Pode corrigir o tipo que Claude declara.
  - Aprova, na ordem do workflow: a proposta, o plano técnico, as unidades derivadas, cada entrega
    e o plano no fim; na correção, o plano mínimo e o plano no fim (18).
  - Testa, ou deixa o teste com Claude, na correção, na entrega e no plano inteiro.
  - Dá o sim às escritas do DC no projeto, como a foundation e as permissões de uso de skill; esse
    sim não é aprovação do workflow.
  - O projeto que usa o DC não altera o codex nem liga ou desliga módulo.
- **Relações:** faz o pedido (01); corrige o tipo (03); dá as aprovações (18); testa (19);
  parceiro de Claude (36); não é o mantenedor do plugin (61).
- **Origem:** seção 1 (*Entrada*, *Workflow*, *Duas camadas*, *Módulos*); decisões 10 e 12.

### 36 - Claude

- **O que é:** o outro ator do workflow: decodifica, revisa, deriva e coda.
- **Como funciona:**
  - Identifica o tipo, com as perguntas que precisar, e o declara com o motivo.
  - Exerce os papéis de PM, Designer e Tech Lead.
  - Pode testar no lugar do usuário.
  - Executa as unidades em cold-start, sem o histórico da conversa.
  - O DC é otimizado para Claude.
- **Mecanismo hoje:** o modelo de cada etapa é declarado no frontmatter da skill: Opus decide,
  Sonnet executa.
- **Relações:** faz o decode (06), a revisão (07), o derive (08) e o code (09); identifica o
  tipo (03); exerce os papéis (31); testa (19); parceiro do usuário (35); obedece ao
  cold-start (44).
- **Origem:** seção 1 (*Entrada*, *Workflow*, *Restrições*); seção 3.

### 37 - História

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
- **Relações:** é escrita na revisão (07); corresponde à unidade (15); a Definition of Ready a
  qualifica (38); os critérios de aceite (69); o aceite é o teste (19) e a aprovação (18); as
  referências (32); o paralelo (51).
- **Origem:** seção 1 (P3, *Referências de produto*, *O paralelo*); decidido em 2026-11-24.

### 38 - Definition of Ready

- **O que é:** no paralelo com produto digital, o estado em que a história está pronta para ser
  desenvolvida. É o que o derive garante.
- **Como funciona:**
  - O derive entrega cada unidade com contexto, memória e padrão de código, e basta sozinha.
  - A correspondência é parte do paralelo, que orienta mas ainda não é regra.
- **Relações:** é garantida pelo derive (08); qualifica a história (37) e portanto a unidade
  (15); depende do cold-start (44); o paralelo (51).
- **Origem:** seção 1 (*O paralelo*, P5); seção 3.

### 39 - Correção

- **O que é:** o workflow enxuto que um plano do tipo `fix` segue: localizar o defeito, corrigi-lo e
  provar que foi corrigido. No código, o identificador é `fix`.
- **Como funciona:**
  - C1, diagnóstico: localiza e reproduz o problema e gera o plano mínimo, com uma tarefa.
  - C2, aprovação do plano mínimo.
  - C3, code.
  - C4, teste: o teste que reproduz o defeito falha antes da correção e passa depois.
  - Por fim, a aprovação final do plano (decidido em 2026-11-24).
  - O decode é enxuto: sem gastar milhares de tokens para corrigir uma palavra.
  - Se a correção não for pequena, o plano passa para o workflow de produto.
  - É o primeiro módulo.
- **Relações:** é o workflow (04) escolhido pelo tipo (03); gera o plano mínimo (13); passa
  por aprovação (18); é codada (09) e testada pelo teste que reproduz o defeito (65); é um
  módulo (34).
- **Origem:** seção 1 (*Workflow de correção*, *Módulos*); decisões 5, 9, 10 e 14; decidido em
  2026-11-24.

### 41 - Plano anterior ao redesign

- **O que é:** o plano sem versão do formato.
- **Como funciona:**
  - É lido pela regra antiga.
  - Fica onde está, mesmo dentro de uma pasta de core.
  - Só é atualizado quando o usuário quiser revisá-lo, derivá-lo ou codá-lo; revisar esses planos
    não faz parte do redesign.
  - Continua com `norma` em `plan_type` e `unit_type`.
  - Links de planos fechados para a norma ficam como registro.
  - Nenhum arquivo em uso usa os nomes antigos, mas esses planos ficam como estão.
- **Mecanismo hoje:** os scripts escolhem a regra pela versão do formato.
- **Relações:** é um plano (11) sem a versão do formato; mora na raiz dos planos (43) ou em
  pasta de core; só muda quando o usuário (35) o leva à revisão (07), ao derive (08) ou ao
  code (09); a migração (42).
- **Origem:** seção 1 (*Restrições*, *Compatibilidade e migração*); decisões 3 e 6.

### 42 - Migração

- **O que é:** o passo que substitui a norma pelo codex nos projetos que já usam o DC.
- **Como funciona:**
  - A primeira sessão com a versão nova avisa da migração.
  - Apaga a cópia da norma do projeto, só com aprovação.
  - O histórico do git a guarda, e os links de planos fechados para a norma ficam como registro.
  - A cópia é arquivo do projeto; remover e reinstalar o plugin não a apaga.
  - Todo plano novo declara a versão do formato.
  - O redesign termina no codex; depois vêm a propagação e a revisão geral, e só então a release
    3.0.
- **Mecanismo hoje:** o aviso vem do hook de abertura da sessão; a cópia foi gravada pelo bootstrap
  em `<plan_root>/system/`.
- **Relações:** substitui a norma pelo codex (27); pede o sim da pessoa; atua sobre a raiz dos
  planos (43); lida com planos antigos (41).
- **Origem:** seção 1 (*Compatibilidade e migração*); decisões 6 e 13.

### 43 - Raiz dos planos

- **O que é:** o diretório `<plan_root>/`, onde ficam todos os planos juntos.
- **Como funciona:**
  - Não há pasta por core: a documentação não precisa espelhar a arquitetura, e quem busca o plano é
    Claude.
  - O plano pequeno é um arquivo; o médio e o grande são uma pasta com o plano e as unidades.
  - O campo `core:` continua no frontmatter e diz a que parte do sistema o plano se refere.
  - Em `<plan_root>/system/` moram a foundation e o huddle.
  - Planos, unidades, huddle e histórico são registro versionado, não instrução carregada.
- **Relações:** guarda planos (11), unidades (15), a foundation (26) e o huddle (21); abriga
  planos antigos (41); a migração age sobre ela (42).
- **Origem:** seção 1 (*Organização dos planos*); seção 5; decisão 7.

### 44 - Cold-start

- **O que é:** a propriedade da unidade de bastar sozinha: roda sem o histórico da conversa.
- **Como funciona:**
  - É o que o derive precisa garantir.
  - Unidade insuficiente vira lacuna (70).
  - A memória de execução entre unidades ficou fora do redesign, porque o cold-start depende de a
    unidade bastar sozinha.
- **Relações:** vale para a unidade (15); é garantido pelo derive (08) e obedecido pelo code
  (09); sustenta a Definition of Ready (38); o handoff conduz as unidades entre sessões (45).
- **Origem:** seção 3; seção 5 (*Memória de execução*).

### 45 - Handoff

- **O que é:** o que leva o plano médio ou grande para a sessão nova e conduz a execução das
  unidades (decidido em 2026-11-24).
- **Como funciona:**
  - É produzido no derive.
  - O brief e o projeto o previam só no grande; com a sessão nova no médio, vale para os dois.
- **Mecanismo hoje:** faz parte da skill derive.
- **Relações:** é produzido pelo derive (08); conduz as unidades (15) de um plano médio ou
  grande (14); leva à sessão nova (09).
- **Origem:** seção 3.
- **Nota [projeto]:** a norma o descreve como `_handoff.md`, o prompt que conduz a execução, gravado
  só no grande (`docs/plan/system/modelo-dev-units.md:762`, `1626`).

### 46 - Independência entre planos

- **O que é:** a condição de que um plano não dependa de outro; é evitar planos que dependem um do
  outro.
- **Como funciona:**
  - A checagem de independência e concorrência vai para o codex, na etapa de revisão.
  - Vale a regra atual **[projeto]** (`modelo-dev-units.md:790`): todo plano diz por que é um
    plano e não dois, e a revisão barra dois planos concorrentes no mesmo alvo (decidido em
    2026-11-24).
- **Relações:** é conferida na revisão (07); vale entre planos (11).
- **Origem:** seção 3.

### 47 - Registro de uso

- **O que é:** o log de uso do DC e o feedback ao método, que fazem o codex evoluir por evidência,
  não por reescrita.
- **Como funciona:**
  - O registro fica no projeto.
  - O destino do feedback é o registro do método.
  - As entradas usam as marcas `E-XX` e `M-XX` **[projeto]** (`modelo-dev-units.md:1252`): `E-XX`
    é um erro registrado; `M-XX` é um feedback sobre o próprio método, escrito de forma genérica
    e aprovado pela pessoa (decidido em 2026-11-24).
- **Mecanismo hoje:** o log fica em `.claude/log/`.
- **Relações:** é do projeto; alimenta a evolução do codex (27), cuja alteração cabe só ao
  mantenedor (61).
- **Origem:** seção 3.

### 48 - Setup

- **O que é:** o primeiro uso do DC no projeto: cria princípios, guidelines e guardrails.
- **Como funciona:**
  - A abertura da sessão propõe o setup quando ele falta.
  - É uma das portas pelas quais o projeto escreve a foundation, sempre com aprovação.
  - Propõe, com a pessoa aprovando, a extração do padrão de código; isso é módulo para depois da
    versão 1.
  - Registra a permissão de cada skill do projeto que o DC pode usar, com o sim da pessoa.
  - A guideline-ponte é criada no setup.
- **Mecanismo hoje:** o aviso vem do hook de abertura da sessão; a permissão é uma regra
  `Skill(<nome>)` no `settings.json` do projeto.
- **Relações:** cria e revisa princípios, guidelines e guardrails (22, 23, 24); escreve a
  foundation (26); irmão do rethink (49); escreve o mapa de recursos (29); avisa também do
  huddle (21).
- **Origem:** seção 3; seção 1 (*Duas camadas*); seção 5; decisões 8 e 12.
- **Nota [projeto]:** a skill o define como o primeiro uso: pré-condições, perfil, princípios,
  guidelines, guardrails, huddle e o princípio Decode → Code, uma sugestão por vez, com toda
  escrita aprovada na conversa (`.claude/skills/setup/SKILL.md:5`).

### 49 - Rethink

- **O que é:** a revisão de princípios, guidelines e guardrails depois de uma mudança de rumo
  do projeto.
- **Como funciona:**
  - É uma das portas pelas quais o projeto escreve a foundation, sempre com o sim da pessoa.
  - Hoje chama esse conjunto de "norma do projeto"; a renomeação troca a expressão pelo nome das
    três coisas.
  - Vai ganhar a capacidade de adicionar e remover recursos do projeto, como skills **[projeto]**
    (huddle, H-25).
- **Relações:** revisa princípios, guidelines e guardrails (22, 23, 24); escreve a foundation
  (26) e atualiza o mapa de recursos (29); vai adicionar e remover recursos do projeto (30);
  irmão do setup (48).
- **Origem:** seção 3; seção 1 (*Duas camadas*); decisão 6; huddle, H-25.
- **Nota [projeto]:** a norma a descreve como a revisão depois de mudança de rumo, item por item,
  com Manter, Editar ou Arquivar, depois do setup concluído
  (`docs/plan/system/modelo-dev-units.md:1567-1585`).

### 50 - Fluxo de decodificação

- **O que é:** os três estágios que o DC de hoje aplica a uma decisão antes de virar plano:
  Clarificar, Evitar e Reduzir.
- **Como funciona:**
  - Clarificar pergunta qual é o problema, a métrica e o beneficiário.
  - Evitar pergunta se dá para resolver sem código.
  - Reduzir pergunta qual é a menor versão que resolve 80%.
  - O brief o trata como a semente das referências de produto.
  - Entra como base do decode, com Clarificar, Evitar e Reduzir; os gates A e B, revistos à luz das
    referências de produto, são o gate de saída do decode (06) (decidido em 2026-11-25).
- **Relações:** semente do decode (06) e das referências de produto (32); o Clarificar pergunta
  a métrica que dá o sinal da hipótese (63); o Reduzir difere do MVP (66).
- **Origem:** seção 1 (*Referências de produto*).
- **Nota [projeto]:** a norma acrescenta dois gates, A (necessidade real) e B (mínimo viável)
  (`docs/plan/system/modelo-dev-units.md:671-690`); o princípio da subtração antes da adição está em
  `.claude/rules/principles.md`.

### 51 - Paralelo com produto digital

- **O que é:** a correspondência entre o workflow do DC e o processo de criação de produto digital.
- **Como funciona:**
  - Stakeholders e squad escrevem o pedido (entrada); PM, Designer e Tech Lead propõem a solução
    (decode); a proposta é aprovada (aprovação); PM e Tech Lead escrevem histórias, refinam e
    quebram em tarefas (revisão); a história fica pronta (derive, Definition of Ready);
    desenvolvimento (code); demonstração e aceite da história (teste e aprovação da unidade).
  - O plano corresponde à proposta, a unidade à história e a tarefa continua tarefa.
  - Orienta, mas ainda não é regra: precisa de mais estudo e refinamento, e não é o foco agora.
  - O DC também serve para criar recursos que não são produto digital.
- **Relações:** relaciona pedido (01), decode (06), revisão (07), derive (08), code (09),
  plano (11), unidade (15), tarefa (16), história (37), Definition of Ready (38) e papéis
  (31); o mindset de produto vale além dele (33).
- **Origem:** seção 1 (*O paralelo com produto digital*).

### 52 - Camada

- **O que é:** cada uma das duas partes em que o DC organiza o que sabe: o método, no codex, e o
  projeto, na foundation.
- **Como funciona:**
  - Codex: o método, só no plugin, alterado só por quem o mantém.
  - Foundation: o padrão de código do projeto e o mapa de recursos, em `<plan_root>/system/`,
    alterada pelo projeto com aprovação.
  - Os recursos do projeto ficam fora das duas camadas.
  - A seção 4 usa "camada" noutro sentido, o das camadas da Clean Architecture.
- **Relações:** são o codex (27) e a foundation (26); os recursos do projeto ficam fora (30);
  as camadas da Clean Architecture são outra divisão (53).
- **Origem:** seção 1 (*Duas camadas*); seção 4.

### 53 - Clean Architecture

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

  - A regra de dependência: as dependências só apontam para dentro (54).
  - O ganho **[referência]**: o centro fica independente de detalhe, testável e durável. No DC, é
    isso que torna o codex à prova de futuro.
  - Onde vale (decisão 7): no método, sempre; no código do plugin, onde um script estiver causando
    problema; no projeto, é guideline de quem a adota.
  - A Clean Architecture organiza o método, não as soluções que o decode propõe; no projeto, ela
    entra só como guideline de quem a adota (23) (decidido em 2026-11-25).
- **Relações:** as entidades são o codex (27); os casos de uso são os workflows (04); a regra é
  a regra de dependência (54); no projeto, é guideline (23).
- **Origem:** seção 1 (*Restrições*); seção 4; decisão 7; decidido em 2026-11-24.

### 54 - Regra de dependência

- **O que é:** a regra central da Clean Architecture **[referência]**: as dependências só apontam
  para dentro, e o que está dentro não sabe nada do que está fora.
- **Como funciona:**
  - O codex não cita skill, script, hook, versão do Claude Code nem projeto.
  - As skills citam o codex, e os scripts o implementam.
  - O núcleo nunca importa um módulo.
  - O que envelhece rápido fica na borda; é isso que torna o codex à prova de futuro.
  - Teste para cada trecho do codex: ele continuaria verdadeiro se o script, a skill ou a versão do
    Claude Code mudassem? Se não, não é codex.
  - A norma atual a quebra nos 27% das linhas que descrevem mecanismo.
- **Mecanismo hoje:** um lint confere que o codex não cita mecanismo.
- **Relações:** vale para o codex (27); é a regra da Clean Architecture (53); no nível dos
  módulos, o núcleo nunca importa um módulo (58).
- **Origem:** seção 1 (*Restrições*); seção 4; decidido em 2026-11-24.

### 55 - Invariante

- **O que é:** uma regra que vale sempre: uma fonte por fato; nada específico de projeto viaja no
  plugin.
- **Como funciona:**
  - Uma fonte por fato: nenhum trecho do codex aparece repetido na foundation nem nas skills.
  - Nada do projeto no plugin: nenhum dado de projeto pode viajar no plugin.
  - Instruções em conflito não têm vencedor; por isso nada do projeto, nem rules nem foundation,
    pode repetir ou contradizer o codex.
- **Mecanismo hoje:** um lint confere a repetição literal; a auditoria do pacote hoje só procura o
  nome deste repositório, e dado de outro projeto precisa entrar na mesma auditoria.
- **Relações:** protege o codex (27) e a foundation (26); a lista de tipos fica fora do codex
  por causa dela; o projeto não altera o codex (56).
- **Origem:** seção 1 (*Restrições*); seção 3; seção 5.

### 56 - Restrição fundamental

- **O que é:** o projeto não altera o codex.
- **Como funciona:**
  - O codex só existe no plugin, e nenhum comando do DC o copia para o projeto.
  - Consequência: nada copia o método para o projeto.
  - Tradeoff aceito: fora de uma skill do DC, Claude não vê o método.
- **Mecanismo hoje:** o bootstrap deixa de copiar a norma.
- **Relações:** protege o codex (27); a foundation, que o projeto altera, é a outra camada (26);
  a migração remove a cópia antiga (42); só o mantenedor altera o codex (61).
- **Origem:** seção 1 (*Restrições*, *Duas camadas*); decisão 1.

### 58 - Núcleo

- **O que é:** a parte do DC que funciona sem nenhum módulo.
- **Como funciona:**
  - Nunca depende de um módulo.
  - Incluir ou remover um módulo não exige alterá-lo.
  - O contrato técnico com os módulos é arquitetura do plugin, não do método: fica na
    documentação de manutenção, fora do codex (decidido em 2026-11-24).
- **Mecanismo hoje:** o núcleo procura as pastas que têm `module.json`, e só elas viajam no pacote;
  recusa um módulo que exige outra versão dele; a suíte do núcleo passa sem qualquer módulo; o
  núcleo do codex fica na pasta compartilhada das skills.
- **Relações:** não depende dos módulos (34), que o usam; o núcleo do codex (27); mantido
  por quem mantém o plugin (61); a regra de dependência vale entre núcleo e módulo (54).
- **Origem:** seção 1 (*Restrições*, *Módulos*); seção 5; decisão 14.

### 59 - Tabela de recursos do plano

- **O que é:** a tabela no plano que registra, pelo nome, os recursos do projeto que o plano usa.
- **Como funciona:**
  - Registra só o nome pelo qual o recurso é invocado, o tipo e onde entra na entrega; sem
    conteúdo, linha ou versão.
  - É conferida na revisão, no derive e na entrada do code: o recurso citado precisa existir.
  - No decode, o nome vai para a tabela.
- **Mecanismo hoje:** um script lê a tabela, e um lint a cruza com a descoberta de recursos do
  projeto.
- **Relações:** faz parte do plano (11); registra recursos do projeto (30); orienta-se pelo mapa
  de recursos (29); é preenchida no decode (06) e conferida na revisão (07), no derive
  (08) e no code (09); diz onde cada recurso entra na entrega.
- **Origem:** seção 1 (*Organização dos planos*); seção 3; decisão 12.

### 60 - Objetivo do plano

- **O que é:** o que o plano quer atingir, claro para o usuário e para Claude.
- **Como funciona:**
  - É uma frase que o usuário confirma na etapa de tipo, distinta do objetivo do DC (decidido em
    2026-11-24).
  - É uma das saídas da etapa 2 da entrada, ao lado do workflow que o plano segue.
- **Relações:** sai da etapa de tipo (03); é do plano (11); parte do pedido (01).
- **Origem:** seção 1 (*Entrada, comum aos dois workflows*, etapa 2).

### 61 - Quem mantém o plugin

- **O que é:** o único ator que altera o codex e inclui ou remove módulos.
- **Como funciona:**
  - Altera o codex a cada versão do plugin.
  - Inclui e remove módulos; o projeto que usa o DC não liga nem desliga módulo.
  - Empacotamento e release ficam fora do codex, como documentação de manutenção.
- **Relações:** altera o codex (27) e os módulos (34); o projeto e o usuário não o fazem (35,
  56).
- **Origem:** seção 1 (*Duas camadas*, *Módulos*); seção 3; seção 5.

### 62 - Os quatro riscos

- **O que é:** a referência de Marty Cagan: validar valor, usabilidade, viabilidade técnica e
  viabilidade de negócio.
- **Como funciona:**
  - É a pauta do trio PM, Designer e Tech Lead.
  - Apoia o decode.
- **Relações:** referência de produto (32) do decode (06); a pauta é dos papéis (31).
- **Origem:** seção 1 (*Referências de produto*).

### 63 - Hipótese

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
- **Relações:** é testada pelo MVP (66); a hipótese de valor é o primeiro dos quatro riscos
  (62); o sinal se liga ao *Clarificar* (50); é declarada no decode (06); faz parte do
  mindset de produto (33); referência de produto (32).
- **Origem:** seção 1 (*Referências de produto*); decidido em 2026-11-24.

### 64 - Teste do plano inteiro

- **O que é:** o teste P8, feito sobre o plano como um todo.
- **Como funciona:**
  - Só existe no plano grande (decidido em 2026-11-24): no pequeno e no médio, o teste da entrega já
    cobre o plano inteiro.
  - Só roda depois que todas as unidades forem concluídas.
  - Claude ou o usuário o faz.
- **Relações:** é um teste (19); testa o plano (11) do porte grande (14); vem depois das
  entregas aprovadas (18).
- **Origem:** seção 1 (P8); decisão 4.

### 65 - Teste que reproduz o defeito

- **O que é:** o teste C4 da correção: falha antes da correção e passa depois.
- **Como funciona:**
  - Verifica a correção; sem ele a correção não é verificada.
  - Claude ou o usuário o faz.
- **Relações:** é um teste (19); verifica a correção (39); o plano mínimo diz como reproduzir o
  defeito (13).
- **Origem:** seção 1 (C4, *Workflow de correção*).

### 66 - MVP

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
  - No DC, a proposta declara o MVP junto com a hipótese (67). O sinal se mede no ponto de
    verificação que a hipótese declara (63), que pode vir depois de o plano fechar: a aprovação da
    entrega confere o critério de aceite (69), não a hipótese (decidido em 2026-11-25).
- **Relações:** testa a hipótese (63); difere do *Reduzir* (50) e do porte (14); é declarado
  no decode (06) e na proposta (67); o sinal se mede no ponto que a hipótese declara (63); faz parte do mindset de produto (33);
  referência de produto (32).
- **Origem:** seção 1 (*Referências de produto*); criado ao separar hipótese e MVP;
  decidido em 2026-11-24.

### 67 - Proposta

- **O que é:** o que sai do decode (P1): a solução conceitual para o pedido, escrita para o usuário,
  que ele aprova em P2.
- **Como funciona:**
  - Traz o problema e de quem ele é, a hipótese (63) e o MVP (66), a solução conceitual com as
    referências técnicas, o apetite, os riscos e o que fica de fora, como no Shape Up.
  - É escrita para o usuário, não para quem executa.
  - Só depois da aprovação vem a revisão, que a transforma em plano técnico.
  - A correção não tem proposta: o diagnóstico gera o plano mínimo.
- **Relações:** sai do decode (06); é aprovada pelo usuário (18, 35); vira plano técnico na revisão
  (07, 12); declara a hipótese (63); segue o Shape Up entre as referências de produto (32); não
  existe na correção (13, 39).
- **Origem:** seção 1 (P1, P2, *Referências de produto*); decidido em 2026-11-25, depois da remoção
  do item 10.

### 68 - Entrega

- **O que é:** o pacote que uma unidade produz: concreto, documentado, que agrega valor ao todo e que
  se consegue medir e testar, por Claude ou pelo usuário.
- **Como funciona:**
  - Cada unidade tem uma entrega e as tarefas necessárias para produzi-la (15).
  - É testada e aprovada pelo usuário antes de a próxima unidade começar (P7).
  - No pequeno, que não tem unidade, a entrega é o resultado das tarefas, aprovado na aprovação
    final.
  - A tabela de recursos do plano diz onde cada recurso do projeto entra nela (59).
- **Relações:** é produzida pela unidade (15) ou pelas tarefas do pequeno (16); passa pelo teste
  (19) e pela aprovação (18); a tabela de recursos aponta onde cada recurso entra nela (59).
- **Origem:** seção 1 (*Unidade*, P7); decidido em 2026-11-25, depois da remoção do item 17.

### 69 - Critério de aceite

- **O que é:** a frase verificável que diz quando a entrega (68) está pronta, declarada antes de
  começar, junto com o teste que a verifica (19).
- **Como funciona:**
  - Toda entrega tem critério de aceite, e ele é o gate de entrada do code: sem ele e sem o teste
    que o verifica, o trabalho não começa.
  - O teste da entrega confere o critério antes da aprovação (P7).
  - Na história, são os critérios de aceite do formato de Mike Cohn (37).
  - Na correção, o teste que verifica o critério é o que reproduz o defeito (65).
  - O termo "oráculo", da norma, não é usado: o critério diz o que precisa ser verdade, e o teste é
    o que confere.
- **Relações:** é da entrega (68); é verificado pelo teste (19, 65); é o gate de entrada do code
  (09) e da unidade (15); vem da história (37).
- **Origem:** seção 3 (*Gates de entrada e de saída do code*); decidido em 2026-11-25, depois da
  remoção do item 20.

### 70 - Lacuna

- **O que é:** o registro, no plano, de que uma unidade se mostrou insuficiente na execução.
- **Como funciona:**
  - Quando a execução mostra que faltava algo na unidade, a correção é feita na unidade, não deixada
    a cargo de quem a executa.
  - A lacuna fica no plano, marcada `L-XX`, com o que faltou e a correção feita.
  - O derive leva à unidade as lacunas que ela precisa conhecer, como parte da memória (08).
- **Relações:** é registrada no plano (11) sobre uma unidade (15); nasce da execução no code (09);
  entra na memória que o derive passa à unidade (08); protege o cold-start (44).
- **Origem:** seção 3 (*Lacuna `L-XX`*); decidido em 2026-11-25.

### 71 - Numeração e nomenclatura

- **O que é:** como planos e unidades são nomeados e numerados, para que cada um seja rastreável.
- **Como funciona:**
  - O plano nasce com um nome semântico, em inglês e em kebab-case, no formato
    `<intenção>-<alvo>[-<qualificador>]`. O nome é identificador, e a prosa do plano segue em pt-BR.
    O nome não declara o tipo (03).
  - Na aprovação, o plano recebe um número de 4 dígitos, sequencial em todo o projeto, atribuído uma
    vez e nunca reaproveitado (11). Passa a se chamar `NNNN-nome`, e o nome não muda mais.
  - Cada unidade tem um identificador `NNNN-nn`, formado pelo número do plano e pela ordem dela no
    plano. Ele nunca muda, e é ele que o código, os testes e as outras unidades citam. O nome do
    arquivo da unidade, `nn-slug`, pode mudar sem quebrar nenhuma referência.
  - Os planos aprovados ficam num índice, e a situação de cada um é derivada, nunca digitada.
- **Mecanismo hoje:** a validação sintática do nome (tamanho, caracteres e conectivos) e a checagem
  de colisão são feitas por script; o índice é `<plan_root>/_planos.md`, projetado por script entre
  marcadores; a sugestão de nomes vem da skill.
- **Relações:** o número sai na aprovação (11, 18); o nome não declara o tipo (03); os planos moram
  juntos na raiz (43); a unidade (15) tem identificador próprio; a situação vem do estado derivado do
  teste (19).
- **Origem:** seção 3 (*Numeração, `_planos.md` e nomenclatura*); norma, seção *Nomenclatura*
  **[projeto]** (`modelo-dev-units.md:962-1059`); decidido em 2026-11-25.

## Termos e pontos em aberto

Nenhum. A parte 1.2 do plano do redesign decidiu todos em 2026-11-25; cada decisão está no item que
ela muda, com a data, e o lugar de cada uma no codex está no mapa do guia do codex.
