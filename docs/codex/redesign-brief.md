---
# about
name: redesign-brief
type: doc
project: ""
description: Brief do redesign que substitui a norma modelo-dev-units.md por um codex — ideias consolidadas, decisões em aberto, peças essenciais do DC, Clean Architecture e onde cada conteúdo mora segundo a documentação do Claude Code
tags: [codex, redesign, foundation, clean-architecture, decode-and-code]

# history
author: Bortoli
created: 2026-11-24
status: draft
version: 1.17.0
updated: ""

# system
scope: project
source: ""
auto_load: false
checksum: ""
dependencies: []
---

# Redesign — da norma ao codex

**Estado:** congelado em 2026-11-25. O brief registra o contexto e as decisões até essa data. O que
mudou depois está no [inventário atômico](atomic-inventory.md) e, desde 2026-11-26, no codex, que
passou a ser a fonte da verdade do método; onde divergem, vale o codex.

Este brief consolida as ideias do redesign que substitui a norma
([`modelo-dev-units.md`](../plan/system/modelo-dev-units.md)) por um **codex**. Registra as ideias,
as decisões em aberto, as peças do DC que o redesign precisa levar e o que a documentação do Claude
Code diz sobre onde cada conteúdo mora. A seção 1 registra o que já foi acordado, e a seção
*Decisões em aberto*, o que ainda falta decidir.

A reescrita **não passa pelo próprio método**: nem intake, nem plano em `docs/plan/_inbox/`. A norma
que está sendo substituída não pode reger a própria substituição. Remendos item a item também foram
descartados.

## Ponto de partida

O diagnóstico de 2026-11-23 classificou as 1.112 linhas de conteúdo da norma:

| Classe | Linhas | % |
|---|---|---|
| Regra | 658 | 59% |
| Descrição de mecanismo (o que um script ou skill faz) | 301 | 27% |
| Evidência e história | 153 | 14% |

Dessas, 115 linhas (10%) só servem a quem mantém o plugin e mesmo assim viajam para todo projeto
que instala. Dos 18 problemas encontrados na leitura completa, 7 vêm do mesmo fato escrito em dois
lugares, 5 de resto do AmFlow ou de história, 4 de citação esquecida quando o conteúdo saiu da
norma, e 2 de estrutura e frontmatter. A norma também é lida por código: o `dc.py` extrai 11 seções
dela pelo título.

## 1. As ideias, consolidadas

**Missão.** Substituir a norma por um **codex** objetivo, eficiente e estável. O codex é o cérebro
do Decode and Code.

**Objetivo do DC.** Decodificar o pedido do usuário (entender, validar, planejar) e escrever código
correto e compatível com o projeto, como se o autor fizesse parte do time desde o início.

### Duas camadas

| Camada | O que guarda | Onde mora | Quem altera |
|---|---|---|---|
| Codex | o método: workflows por tipo, artefatos, contratos, gates e referências de produto | só no plugin, versionado com ele; nunca é copiado para o projeto | só quem mantém o plugin, a cada versão |
| Foundation | o padrão de código do projeto e o mapa dos recursos do projeto pelo nome | em `<plan_root>/system/`, lida pelo decode e pelo derive quando precisam | o projeto, pelas portas do DC (setup, rethink e plano), sempre com aprovação |

Princípios, guidelines, guardrails, perfil, decisões, planos e huddle continuam funcionando onde
estão hoje. A foundation, no máximo, os menciona.

Os **recursos do projeto** (skills, commands, MCP e o `CLAUDE.md`) ficam fora das duas camadas. Eles
são do projeto: o DC os cita pelo nome e nunca os copia nem edita (decisão 12).

A norma é substituída por completo pelo codex, inclusive nos projetos que já usam o DC (decisão 13).

### Workflow

O tipo do plano escolhe o workflow. Por enquanto são dois: o de correção, para `fix`, e o de produto,
para os demais tipos. Outros tipos podem ganhar workflow próprio depois.

#### Entrada, comum aos dois workflows

| # | Etapa | Quem | O que sai |
|---|---|---|---|
| 1 | Entrada: um pedido, blocos de texto para juntar ou um insight para discutir | usuário e Claude | um pedido único, ou uma conversa que termina sem plano |
| 2 | Tipo do plano, pela lista de tipos que o próprio DC mantém | Claude identifica, com as perguntas que precisar, e declara com o motivo; o usuário pode corrigir | o objetivo do plano claro para os dois, e o workflow que ele segue |

#### Workflow de correção (`fix`)

O decode da correção é enxuto: identificar o problema e criar a correção, sem gastar milhares de
tokens para corrigir uma palavra. Se o diagnóstico mostrar que a correção não é pequena, ela passa
para o workflow de produto.

| # | Etapa | Quem | O que sai |
|---|---|---|---|
| C1 | Diagnóstico: localizar e reproduzir o problema | Claude | plano mínimo registrado: o plano pequeno com uma única tarefa, que traz o problema e como reproduzi-lo, a correção e como verificar (decisão 9) |
| C2 | Aprovação | usuário | correção aprovada |
| C3 | **Code** (hoje `implement`), com as skills e os recursos do projeto | Claude | a correção |
| C4 | Teste: o teste que reproduz o defeito falha antes da correção e passa depois | Claude ou usuário | correção verificada |

#### Workflow de produto (demais tipos)

| # | Etapa | Quem | O que sai |
|---|---|---|---|
| P1 | **Decode** (hoje `intake`), com mindset de produto, a foundation, os princípios, as guidelines e os guardrails, e as skills e os recursos do projeto | Claude, no papel de PM, Designer e Tech Lead | proposta de solução conceitual, com referências técnicas, escrita para o usuário |
| P2 | Aprovação da proposta | usuário | proposta aprovada e revisão pedida |
| P3 | Revisão: escrever as histórias, refinar (viabilidade técnica, compatibilidade, infra, erros, lacunas e decisões em aberto) e quebrar em tarefas | Claude, no papel de PM e Tech Lead | plano técnico, com tarefas ou unidades conforme o porte |
| P4 | Aprovação do plano técnico | usuário | plano técnico aprovado; é aqui que o plano recebe número |
| P5 | Derive (só médio e grande) | Claude | cada unidade com contexto, memória e o padrão de código do projeto |
| P6 | **Code** (hoje `implement`), com as skills e os recursos do projeto | Claude | no pequeno, as tarefas na mesma sessão; no médio e no grande, uma unidade por vez, numa sessão nova |
| P7 | Teste e aprovação da entrega | Claude ou o usuário testa; o usuário aprova | a próxima unidade só começa depois que a anterior for aprovada |
| P8 | Teste do plano inteiro, quando ele tem mais de uma unidade | Claude ou o usuário | só roda depois que todas as unidades forem concluídas |

#### Porte, no workflow de produto

| Porte | Estrutura | Passa pelo derive? | Como executa |
|---|---|---|---|
| Pequeno | lista de tarefas | não | na mesma sessão, logo após a aprovação do plano técnico |
| Médio | 1 unidade | sim | a unidade, numa sessão nova, aprovada ao final |
| Grande | 2 ou mais unidades | sim | uma unidade por vez, numa sessão nova, cada uma depois da aprovação da anterior |

São três portes, e só três: o plano mínimo da correção é o pequeno com uma única tarefa, não um
quarto porte. No médio e no grande, o DC recomenda executar numa sessão nova: a unidade traz o que
precisa para o cold-start, e começar sem o histórico da conversa economiza tokens.

**Unidade.** Uma lista de tarefas que, no fim, entrega um pacote concreto e documentado, que agrega
valor ao todo e é minimamente mensurável e testável, pelo Claude ou pelo usuário. Tem as tarefas
necessárias para entregar esse pacote; não há limite de tarefas por unidade (decisão 3).

#### O paralelo com produto digital

| Produto digital | DC |
|---|---|
| Stakeholders e squad escrevem o pedido | entrada |
| PM, Designer e Tech Lead propõem a solução | decode |
| A proposta é aprovada | aprovação |
| PM e Tech Lead escrevem histórias, refinam e quebram em tarefas | revisão |
| A história fica pronta para desenvolver (Definition of Ready) | derive |
| Desenvolvimento | code |
| Demonstração e aceite da história | teste e aprovação da unidade |

Nesse paralelo, o plano corresponde à proposta, a unidade à história, e a tarefa continua sendo
tarefa.

O paralelo orienta, mas ainda não é regra: precisa de mais estudo e refinamento, e não é o foco
agora. O DC também serve para criar skills, agents, plugins e outros recursos que não são produto
digital. O que vale em todos os casos é o mindset de produto.

#### Referências de produto

O decode e a revisão se apoiam em referências consagradas de criação de produto digital. Essa
referência fica no próprio codex.

| Referência | O que traz | Etapa |
|---|---|---|
| Jobs to Be Done (Clayton Christensen) | descrever o problema pelo que a pessoa quer realizar, não pela feature | decode |
| Design Thinking e Double Diamond (Design Council) | entender o problema antes de escolher a solução | decode |
| Lean Startup (Eric Ries) | hipótese e MVP: aprender construindo o mínimo | decode |
| Os quatro riscos (Marty Cagan) | validar valor, usabilidade, viabilidade técnica e viabilidade de negócio; é a pauta do trio PM, Designer e Tech Lead | decode |
| Shape Up (Ryan Singer) | proposta com problema, apetite, solução, riscos e o que fica de fora | decode |
| Histórias de usuário e INVEST (Mike Cohn, Bill Wake) | histórias independentes, pequenas e testáveis, com critério de aceite | revisão |
| User Story Mapping (Jeff Patton) | fatiar a entrega em incrementos | revisão |

O DC atual já tem a semente disso. O fluxo de decodificação de hoje pergunta qual é o problema, a
métrica e o beneficiário (Clarificar), se dá para resolver sem código (Evitar) e qual é a menor
versão que resolve 80% (Reduzir).

#### O que muda em relação ao DC de hoje

- **O tipo vem antes do decode**, porque é ele que escolhe o workflow, e Claude pode fazer as perguntas
  necessárias para identificá-lo. Hoje o intake propõe o tipo junto com o plano.
- **A unidade fecha com a aprovação do usuário**, além do teste. O mecanismo já existe na unidade do
  tipo `norma` (`rule` no formato novo), que fecha pelos campos `approved_by` e `approved_at`.
- **O grande deixa de executar as unidades em sequência direta:** cada unidade espera a aprovação
  da anterior. O maior grande já fechado teve 21 unidades, o que daria 21 aprovações.
- **Usar as skills do projeto no decode e no code é essencial**, sem copiá-las para dentro do DC:
  a skill continua evoluindo no projeto depois de integrada. Hoje isso funciona em parte, só no
  code, pela guideline-ponte: skill comum é chamada sem permissão extra, e skill que declara
  `allowed-tools` pede permissão. Fazer funcionar nas duas etapas é a decisão 12.

### Organização dos planos

Todos os planos ficam juntos em `<plan_root>/`, sem pasta por core: a documentação não precisa
espelhar a arquitetura, e quem busca um plano é o Claude. O pequeno é um arquivo; o médio e o
grande são uma pasta com o plano e as unidades, porque o médio agora também tem unidade. O campo
`core:` continua no frontmatter e diz a que parte do sistema o plano se refere, como `worker` num
plano de publicação do plugin worker (decisão 7).

### Restrições

| Restrição | Como verificar |
|---|---|
| Renomear: norma vira codex, `intake` vira `decode`, `implement` vira `code` e o valor `norma` de `plan_type` e `unit_type` vira `rule` no formato novo | nenhum arquivo em uso (skills, rules, scripts, hooks, `docs/recursos/`) usa os nomes antigos para essas peças; planos anteriores ao redesign ficam como estão até o usuário levá-los a revisar, derivar ou codar |
| Não refazer o plugin: o que funciona hoje continua funcionando | a suíte atual continua passando; um teste só muda quando o que ele testa foi renomeado de propósito |
| O codex é à prova de futuro, sem reescrita a cada três meses | o codex não cita skill, script, hook, versão do Claude Code nem projeto (regra de dependência, seção 4), e um lint confere isso |
| O DC é otimizado para Claude | cada conteúdo fica no mecanismo indicado na seção 5, dentro dos limites da documentação: `SKILL.md` com menos de 500 linhas, e o mínimo possível carregado em toda sessão |
| **O projeto não altera o codex** — restrição fundamental | o codex só existe no plugin, e nenhum comando do DC o copia para o projeto |
| O decode segue Clean Architecture, sempre | a regra de dependência da seção 4 organiza o método; no código do plugin, a Clean Architecture entra onde um script estiver causando problema; no projeto, é guideline de quem a adota (decisão 7) |
| Uma fonte por fato | nenhum trecho do codex aparece repetido na foundation nem nas skills, e um lint confere a repetição literal |
| Nada específico de projeto viaja no plugin | `empacotar.verificar` audita o pacote, mas hoje só procura o nome deste repositório; dado de outro projeto, como o AmFlow, precisa entrar na mesma auditoria |
| Funcionalidade nova entra como módulo plug and play, começando pequeno e com suporte a crescer | remover um módulo não quebra a suíte nem os outros módulos, e incluir um não exige editar o núcleo (decisão 14) |

### Módulos

Funcionalidade nova do DC entra como módulo. O contrato começa mínimo, na versão 1, e cresce depois
(decisão 14):

| Cláusula | Na versão 1 |
|---|---|
| O que é | uma funcionalidade do DC numa pasta só: as skills, os scripts, o capítulo do codex e os testes dela |
| Manifesto | um `module.json` na raiz da pasta, com `name`, `version`, `description` e `requires` (a versão do núcleo e os módulos de que depende); fica fora do `SKILL.md`, porque um módulo pode ter nenhuma ou várias skills |
| Descoberta | o núcleo procura as pastas que têm `module.json`, e só elas viajam no pacote; sem lista central, e a garantia de não vazar skill de desenvolvimento continua |
| Fronteira | o núcleo nunca importa um módulo; o módulo usa o núcleo e só os módulos que declara em `requires`, e um lint confere os imports |
| O que um módulo acrescenta | skills, subcomandos do `dc.py` registrados pelo próprio módulo e o capítulo do codex; hooks e tipos de plano com workflow próprio ficam para depois |
| Quem inclui e remove | só quem mantém o plugin; o projeto que usa o DC não liga nem desliga módulo |
| Remover | apagar a pasta; a suíte do núcleo continua passando, e nenhum outro módulo o importa sem declarar |
| Versão | o núcleo recusa um módulo que exige outra versão dele, e diz por quê |

O primeiro módulo é o workflow de correção: funcionalidade nova do redesign, pequena e separada do
resto, que testa o contrato sem mexer no que já funciona.

### Compatibilidade e migração

- Todo plano novo declara a versão do formato. Plano sem versão é anterior ao redesign, e os
  scripts o leem pela regra antiga (decisão 3).
- Planos anteriores ao redesign ficam onde estão, mesmo dentro de uma pasta de core, e só são
  atualizados quando o usuário quiser revisá-los, derivá-los ou codá-los. Revisar esses planos não
  faz parte do redesign (decisão 6).
- Na primeira sessão com a versão nova, o hook de abertura avisa da migração. A migração apaga a
  cópia da norma do projeto, só com aprovação; o histórico do git a guarda, e os links de planos
  fechados para a norma ficam como registro (decisão 13).
- O redesign termina no codex. Depois vem um trabalho de propagação e revisão geral do DC, e só
  então a release 3.0 (decisão 6).

## 2. Decisões em aberto

Cada item traz o conflito, a evidência e uma recomendação. Quando um item é decidido, ele fica com a
data e aponta para a seção 1, onde a decisão passa a valer; o número não muda. Quando só parte foi
decidida, o item diz qual.

### 1. Codex na pasta de regras ou codex que o projeto não altera

- **Decidido em 2026-11-24:** o codex mora só no plugin, como arquivos de apoio das skills, e nunca
  é copiado para o projeto (seção 1, *Duas camadas*). Consequência: o bootstrap deixa de copiar a
  norma. O tradeoff aceito: fora de uma skill do DC, Claude não vê o método.

### 2. Uma aprovação ou duas

- **Decidido em 2026-11-24:** o plano técnico também passa por aprovação, antes do derive, e é nela
  que o plano recebe número (seção 1, P4). O `scaffold.aprovar` continua como está e passa a rodar
  nessa aprovação, porque recusa plano sem porte, e o porte só se define na revisão.

### 3. O médio muda de significado

- **Decidido em 2026-11-24:** todo plano novo declara a versão do formato, e o limite de 8 passos por
  unidade continua (seção 1, *Porte, no workflow de produto* e *Compatibilidade e migração*). Com o
  limite, 4 dos 12 médios já fechados teriam virado grandes. `lint_plano`, `scaffold.aprovar` e
  `backlog.projetar` passam a ler a versão do formato.
- **Revisto em 2026-11-24:** o limite de 8 passos sai. A unidade tem as tarefas necessárias para
  entregar um pacote testável que agrega valor ao produto (seção 1, *Unidade*). O plugin ainda
  aplica o teto, no lint da unidade e no teste dele; o teto sai do código na execução do redesign,
  junto com a troca da norma pelo codex, para os dois não divergirem.

### 4. "O plano precisa ser testado"

- **Decidido em 2026-11-24:** cada entrega é testada e aprovada antes da próxima (P7), e o plano com
  mais de uma unidade é testado inteiro depois que todas forem concluídas (P8).

### 5. Correção ou feature, contra os sete tipos de hoje

- **Decidido em 2026-11-24:** a identificação do tipo continua como o DC já faz, e a lista de tipos
  é a que o próprio DC mantém; o codex não a repete. O tipo escolhe o workflow: `fix` segue o de
  correção, os demais seguem o de produto (seção 1, *Entrada, comum aos dois workflows*).
- **Para depois:** dos 10 planos que declaram `plan_type`, só `feature` (6), `fix` (2) e `norma` (2)
  apareceram; `remove`, `refactor`, `chore` e `spike` nunca foram usados.

### 6. As renomeações quebram quem já usa o plugin

- **Decidido em 2026-11-24:** todos os nomes mudam (seção 1, *Restrições*). Planos anteriores ao
  redesign só são atualizados quando o usuário quiser revisá-los, derivá-los ou codá-los, e revisar
  esses planos não faz parte do redesign (seção 1, *Compatibilidade e migração*).
- **Impacto medido** (arquivos que citam a palavra, com algum falso positivo): `intake` em 24, 6
  deles Python; `implement` em 43, 13 deles Python; `norma` em 138, 50 deles Python.
- **Decidido em 2026-11-24:** a release 3.0 sai depois do redesign e de um trabalho de propagação e
  revisão geral do DC (seção 1, *Compatibilidade e migração*).
- **Decidido em 2026-11-24:** o valor `norma` de `plan_type` e `unit_type` vira `rule` no formato
  novo (seção 1, *Restrições*). É o único identificador em português da lista, contra a regra de identificador em inglês, e o nome
  confunde com a norma que o codex substitui. Os planos antigos continuam com `norma`, pela versão
  do formato (decisão 3).
- **Decidido em 2026-11-24:** nenhuma skill redireciona os nomes antigos; o redirecionamento seria
  código mantido só para a transição.

### 7. Clean Architecture aplicada a quê

- **Decidido em 2026-11-24:** a Clean Architecture vale sempre. Ela organiza o método desde agora
  (seção 4); no código do plugin, entra onde um script estiver causando problema; no projeto, é
  guideline de quem a adota, fora do codex, porque escolha técnica que um time competente pode
  rejeitar não viaja no plugin.
- **Decidido em 2026-11-24, sobre "core":** o nível de pasta `core` sai, e todos os planos ficam
  juntos em `<plan_root>/`; o campo `core:` continua no frontmatter (seção 1, *Organização dos
  planos*). A organização por pasta de core veio do tempo em que o dev-units fazia parte do AmFlow e
  não se mostrou eficaz.

### 8. A foundation que "registra tudo" pode virar a próxima norma

- **Decidido em 2026-11-24:** a foundation guarda só o que hoje não tem lugar: o padrão de código do
  projeto e o mapa dos recursos do projeto pelo nome. Mora num arquivo em `<plan_root>/system/`, que
  o decode e o derive leem quando precisam, sem carregar em toda sessão. O resto continua onde está,
  e a foundation no máximo o menciona (seção 1, *Duas camadas*).

### 9. A correção gera plano registrado?

- **Decidido em 2026-11-24:** sim. O plano mínimo é o plano pequeno de hoje, com três seções fixas,
  e a correção que não for pequena passa para o workflow de produto (seção 1, *Workflow de correção*).
- **Revisto em 2026-11-24:** o plano mínimo é o plano pequeno com uma única tarefa. O DC tem só três
  portes, e o mínimo não é um quarto (seção 1, *Porte*).

### 10. A correção pede aprovação?

- **Decidido em 2026-11-24:** sim, toda correção passa por aprovação antes do code (C2).

### 11. Onde fica a referência de produto

- **Decidido em 2026-11-24:** no próprio codex, que mora no plugin (seção 1, *Referências de
  produto*, e decisão 1).

### 12. Como o DC usa as skills do projeto sem copiá-las

- **Decidido em 2026-11-24:** abrir um spike para descobrir como fazer; a funcionalidade é muito
  importante para o decode. O spike terminou no mesmo dia, medido com `claude -p` (Claude Code
  2.1.330) num projeto de prova, sem implementar nada; a resposta está abaixo.
- **Hoje:** o vínculo existe só do derive para o code. A guideline-ponte, criada no setup, nomeia o
  recurso do projeto para os caminhos onde ele vale; o derive a cita na unidade
  (`guidelines-aplicaveis`), e o code a recebe (`dc.py normas`). Ela referencia a skill, sem
  copiá-la. O `SKILL.md` do intake não menciona recursos do projeto; na prática, o intake os lê por
  conta própria e copia o conteúdo (ver *Achado*).
- **Lacuna:** a ponte depende de `paths`, e no decode ainda não existe arquivo para casar. O vínculo
  por caminho não serve para essa etapa.
- **Resposta do spike:**
  1. *De onde vem a lista.* O fork do decode recebe a listagem de skills do Claude Code, igual à da
     conversa principal. Mesmo assim, o que o plano cita vem do `descobrir`: a listagem mistura as
     skills do projeto com as pessoais, sem marcar a origem, corta descrições quando passa do
     orçamento (125 de 206 só com o nome, na medição) e não é legível por script. O `descobrir`
     precisa de quatro correções: ler a descrição inteira e o `when_to_use` (hoje corta no primeiro
     parágrafo); marcar as skills com `disable-model-invocation: true`, que só a pessoa chama; filtrar
     as skills do DC pela origem, não pelo nome da pasta (hoje uma skill do projeto chamada `setup`
     some da lista); e ter uma saída só com os recursos.
  2. *Permissão.* Skill comum do projeto é chamada do fork sem permissão extra. Skill que declara
     `allowed-tools`, `disallowed-tools` ou `hooks` pede permissão, e isso vale também para o
     `implement` de hoje. Pôr `Skill` no `allowed-tools` da skill do DC resolve, medido.
  3. *Registro no plano.* Só o nome pelo qual a skill é invocada, numa tabela que um script lê
     (recurso, tipo e onde entra na entrega). Sem conteúdo, linha ou versão: invocada pelo nome, a
     skill entra na versão atual. Um lint cruza a tabela com o `descobrir` na revisão, no `derive` e na
     entrada do `code`: reprova o nome que sumiu, avisa a skill que só a pessoa pode chamar e avisa a
     skill pessoal de mesmo nome, que passa na frente da do projeto.
- **Achado:** na execução real, o `intake` de hoje não chamou a skill. Achou os `SKILL.md` por
  `find`, leu-os com `Read` e copiou as regras citando linha. É a cópia que esta decisão quer evitar,
  e o `Read` ainda contorna o `allowed-tools` da skill.
- **Decidido em 2026-11-24, a recomendação do spike:** no decode, a lista vem do `descobrir` corrigido, e o `SKILL.md` manda
  invocar as skills pela ferramenta `Skill`, nunca lê-las com `Read`; o nome vai para a tabela do
  plano. No code, a ponte continua, e o lint de nomes roda na entrada. A regra "cita pelo nome, não
  copia, não cita linha" fica no codex.
- **Decidido em 2026-11-24, sobre a permissão:** regra por skill. Cada skill do projeto que o DC
  pode usar ganha uma regra `Skill(<nome>)` no `settings.json` do projeto, com a aprovação da pessoa.
  `Skill` solto no `allowed-tools` do decode e do code fica descartado, porque liberaria toda skill do
  projeto e as ferramentas que ela se concede.
- **Fase de cada skill:** o mapa de recursos da foundation (decisão 8) diz em que fase do DC cada
  skill do projeto entra: decode, revisão ou code.

### 13. Migração da norma nos projetos que já usam o DC

- **Decidido em 2026-11-24:** a norma é substituída por completo pelo codex, por um passo de
  migração que o hook de abertura avisa na primeira sessão com a versão nova, e que só apaga a cópia
  com aprovação (seção 1, *Compatibilidade e migração*).
- **Fato:** a cópia da norma é arquivo do projeto, gravada pelo bootstrap em `<plan_root>/system/`.
  Remover e reinstalar o plugin não a apaga, porque o plugin mora em `~/.claude/plugins/cache/`,
  fora do projeto.

### 14. O que é um módulo plug and play

- **Já definido:** funcionalidade nova do DC entra como módulo plug and play: incluir ou remover não
  quebra o plugin. Começar pequeno, com suporte a crescer (seção 1, *Restrições*).
- **Fato:** hoje as skills são registradas numa lista central, `lib.SKILLS`, em
  `.claude/skills/decode-and-code/scripts/lib.py`; incluir ou remover uma skill pede editar o
  núcleo.
- **Decidido em 2026-11-24:** o contrato da versão 1 (seção 1, *Módulos*). Módulo é uma pasta com
  `module.json`, descoberta pelo núcleo sem lista central; o núcleo nunca importa módulo. Só quem
  mantém o plugin inclui e remove módulos. Hooks ficam para depois, porque o build gera
  `hooks/hooks.json` a partir do `settings.json`, e juntar os hooks de cada módulo pede um passo
  novo. O primeiro módulo é o workflow de correção.

## 3. Peças essenciais que o texto original não cita

| Peça do DC hoje | Para que serve | Destino sugerido |
|---|---|---|
| Estado derivado do teste (`spec` → `verified`, nunca editado à mão) | a documentação não mente sobre o que está pronto | regra no codex, aplicada por script |
| Cold-start: a unidade basta sozinha e roda num subagente sem o histórico da conversa | é o que o derive precisa garantir | codex |
| Gates de entrada e de saída do `code` | não começar sem oráculo, não fechar sem teste e sem a aprovação do usuário (P7) | regra no codex, aplicada por script; a unidade fecha pelos campos `approved_by` e `approved_at`, que hoje só a unidade `norma` usa |
| Modelo por etapa (Opus decide, Sonnet executa) | custo e qualidade | frontmatter das skills |
| Numeração, `_planos.md` e nomenclatura | rastrear cada plano | regra no codex, aplicada por script; o número sai na aprovação do plano técnico (decisão 2), sem pasta por core (decisão 7) |
| Independência e concorrência entre planos | evitar planos que dependem um do outro | codex, na etapa de revisão |
| Huddle | lugar das decisões em aberto que a revisão encontra | continua onde está, em `<plan_root>/system/huddle/` |
| Log de uso e feedback ao método (`E-XX`, `M-XX`) | o codex evolui por evidência, não por reescrita | log no projeto, em `.claude/log/`; destino no registro do método |
| Setup e rethink | criar e revisar princípios, guidelines e guardrails | skills; o rethink hoje chama esse conjunto de "norma do projeto", e a renomeação (decisão 6) troca a expressão pelo nome das três coisas |
| Hook de guardrail (`PreToolUse`) | impor o que não pode depender de Claude lembrar | mecanismo no plugin, regras no projeto |
| `descobrir`, guideline-ponte, `guidelines-aplicaveis` e `normas` | ligar o plano às skills e recursos do projeto | no decode, o `descobrir` corrigido, com as skills invocadas pela ferramenta `Skill` e o nome registrado numa tabela do plano; no code, a ponte e o lint de nomes (decisão 12) |
| Padrão de código do projeto | o derive garante que o código segue o estilo do time | foundation (decisão 8), que no redesign só reserva o lugar; extrair o padrão do código existente, com o setup propondo e a pessoa aprovando, é módulo para depois da versão 1 (decisão 14) |
| Handoff entre sessões (grande) | orquestrar a execução | skill derive |
| Porte medido | calibrar o porte com dado | continua onde está, aplicado por script |
| Empacotamento e release | distribuir o plugin | fora do codex: documentação de manutenção |
| Invariantes: uma fonte por fato; nada do projeto dentro do plugin | evitar desatualização e vazamento | codex |
| Lacuna `L-XX` | quando a execução mostra que a unidade estava insuficiente, a correção é da unidade e fica registrada no plano | regra no codex; o registro fica no plano |

## 4. Clean Architecture aplicada ao DC

| Camada | No DC | Muda quando |
|---|---|---|
| Entidades | codex: conceitos (pedido, plano, porte, unidade, tarefa, teste), contratos e gates | o método muda |
| Casos de uso | os workflows por tipo de plano e suas etapas (decode, revisão, derive, code), que são as skills | um workflow muda, ou um tipo ganha workflow próprio |
| Adaptadores | `dc.py`, scripts, hooks e formatos de arquivo | o formato ou o Claude Code muda |
| Frameworks | Claude Code, git e runners de teste | fora do controle do DC |

**Regra de dependência.** O codex não cita skill, script, hook, versão do Claude Code nem projeto.
As skills citam o codex, e os scripts o implementam. O que envelhece rápido fica na borda, e é isso
que torna o codex à prova de futuro. A norma atual quebra essa regra nos 27% das linhas que
descrevem mecanismo.

## 5. Onde cada conteúdo mora, segundo a documentação do Claude Code

| Conteúdo | Mecanismo, segundo a documentação | Lugar | Camada ou dono |
|---|---|---|---|
| Princípios do projeto | rule sem `paths`: carrega no início de toda sessão | `.claude/rules/` | do projeto |
| Guidelines | rule com `paths`: carrega quando Claude lê ou edita um arquivo que casa com o padrão | `.claude/rules/` | do projeto |
| Guardrails | hook `PreToolUse`: a documentação manda usar hook para bloquear independentemente da decisão de Claude | regras em `.claude/guardrails.json`, hook no plugin | regras do projeto, hook do plugin |
| Convenções curtas e estáveis | `CLAUDE.md`, com menos de 200 linhas | raiz ou `.claude/` | do projeto, fora do DC |
| Procedimento de cada etapa | skill: carrega só quando usada; `SKILL.md` com menos de 500 linhas | plugin | casos de uso |
| Codex | arquivos de apoio das skills, lidos quando a skill precisa | plugin: o núcleo na pasta compartilhada `skills/decode-and-code/`, onde a norma já viaja hoje, lido por `${CLAUDE_SKILL_DIR}/../decode-and-code/`; o capítulo de cada módulo, na pasta do módulo (decisão 14) | entidades |
| Foundation: padrão de código e mapa dos recursos do projeto | não é instrução sempre carregada; o decode e o derive a leem quando precisam | `<plan_root>/system/` | do projeto |
| Aviso na abertura da sessão (setup, huddle) | hook `SessionStart` com `additionalContext` | plugin | adaptador |
| Memória de execução | subagente com `memory: project` grava em `.claude/agent-memory/<agente>/` | `.claude/` | fora do redesign: sem dor medida, e o cold-start depende de a unidade bastar sozinha; se surgir dor, entra como módulo |
| Planos, unidades, huddle e histórico | não são instrução carregada; são registro versionado | `<plan_root>/` | do projeto |
| Plugin habilitado para o time, e uma regra `Skill(<nome>)` por skill do projeto que o DC pode usar, gravada com a aprovação da pessoa (decisão 12) | `settings.json` do projeto, versionado | `.claude/` | do projeto |
| Módulo | pasta com `module.json`, descoberta pelo núcleo; só as pastas com manifesto viajam no pacote | plugin | só quem mantém o plugin (decisão 14) |
| Estado do plugin entre versões | `${CLAUDE_PLUGIN_DATA}`; já `${CLAUDE_PLUGIN_ROOT}` muda a cada versão | fora do projeto | adaptador |

Três pontos da documentação pesam no desenho:

- **Instruções em conflito não têm vencedor:** Claude pode seguir qualquer uma. Por isso nada do
  projeto, nem rules nem foundation, pode repetir ou contradizer o codex.
- **Frontmatter inválido** faz uma guideline carregar como se não tivesse `paths`, ou seja, sempre.
  O lint das guidelines continua necessário.
- **Subdiretórios de `.claude/rules/` também carregam**, porque a busca é recursiva.

## Fontes

- Documentação do Claude Code, consultada em 2026-11-23:
  [memory](https://code.claude.com/docs/en/memory),
  [plugins-reference](https://code.claude.com/docs/en/plugins-reference),
  [skills](https://code.claude.com/docs/en/skills),
  [hooks](https://code.claude.com/docs/en/hooks) e
  [claude-directory](https://code.claude.com/docs/en/claude-directory).
- Porte e tipo dos planos: frontmatter dos 21 planos aprovados em `docs/plan/model/` e
  [`porte-medido.md`](../plan/system/porte-medido.md), medidos em 2026-11-23.
- Impacto das renomeações: arquivos que citam cada palavra, contados em 2026-11-23 sem `.git/`,
  `dist/` e `.claude/log/`.
- Diagnóstico da norma: classificação por parágrafo em 2026-11-23. A classificação é julgamento; a
  contagem foi feita por script, que não foi versionado.
- Spike da decisão 12: medição com `claude -p` (Claude Code 2.1.330) em 2026-11-24, com o pacote do
  DC carregado num projeto de prova. O relatório completo ficou nas notas da sessão do spike, fora do
  repositório.
