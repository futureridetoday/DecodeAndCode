---
# about
name: codex-guide
type: doc
project: ""
description: Guia do codex — quem o lê e quando, como ele se organiza, que tipos de conteúdo tem, como se escreve e como se muda sem virar colcha de retalhos; entrega da parte 1.1 do plano do redesign
tags: [codex, redesign, arquitetura-da-informacao]

# history
author: Bortoli
created: 2026-11-25
status: stable
version: 1.5.0
updated: ""

# system
scope: project
source: ""
auto_load: false
checksum: ""
dependencies: [atomic-inventory, redesign-brief, redesign-plan]
---

# Guia do codex

Entrega da parte 1.1 do [plano do redesign](../codex/redesign-plan.md): as decisões de arquitetura
da informação e de estratégia de conteúdo do codex. O conteúdo vem do
[inventário atômico](../codex/atomic-inventory.md); este guia diz como ele se organiza. "Item NN" é o
item NN do inventário.

**Estado:** aprovado em 2026-11-25, o que fecha a parte 1.1; o mapa recebeu as decisões da 1.2 no
mesmo dia.

## Leitores e leitura

Decidido em 2026-11-25. Cada etapa lê o trecho de que precisa, quando roda (item 27); quem mantém o
plugin o altera (item 61).

| Momento de leitura | Quem lê | Itens que ancoram o momento |
|---|---|---|
| Entrada: pedido, tipo e objetivo | Claude | 01, 02, 03, 60 |
| Decode (P1) | Claude, como PM, Designer e Tech Lead | 06 |
| Revisão (P3) | Claude, como PM e Tech Lead | 07 |
| Derive (P5) | Claude | 08 |
| Code e teste (P6 a P8) | Claude | 09, 19, 64 |
| Correção (C1 a C4) | Claude | 13, 39, 65 |
| Setup, rethink e huddle | Claude, com a pessoa | 21, 48, 49 |
| Manutenção | quem mantém o plugin | todo o codex |

## Organização

### Por conceito

Decidido em 2026-11-25: cada conceito é uma seção com título estável, e cada etapa lê só as seções de
que precisa, por título. A lista de seções que cada etapa lê fica na skill, não no codex: a skill cita
o codex, nunca o contrário (item 54).

**Medição que sustenta a escolha** (2026-11-25). Um item pertence a um momento de leitura se é âncora
dele, se uma âncora o cita em *Relações*, ou se ele cita uma âncora. O tamanho de um item é o número
de linhas não vazias da sua seção no inventário (818 no total).

| Momento | Itens que lê | Linhas, por conceito | Linhas, em camadas (núcleo inteiro e etapa) |
|---|---|---|---|
| Entrada | 12 | 158 | 503 |
| Decode | 24 | 362 | 593 |
| Revisão | 17 | 235 | 499 |
| Derive | 18 | 255 | 498 |
| Code | 25 | 349 | 498 |
| Correção | 11 | 172 | 502 |
| Setup, rethink e huddle | 14 | 191 | 562 |
| **Total** | | **1.722** | **3.655** |

- **Por etapa**, um arquivo completo por momento: descartada. Os 35 itens usados por dois momentos ou
  mais virariam 69 cópias e 1.007 linhas duplicadas, mais que o inventário inteiro (item 55).
- **Em camadas**, núcleo com os itens compartilhados e um arquivo por etapa: lê mais que o dobro, e
  só empata lendo o núcleo por seção, quando a camada deixa de trazer ganho de leitura.
- **Por conceito** lê o mínimo sem repetir nada. Depende de a leitura por seção funcionar, o que já
  existe hoje na extração por título.
- **Limites:** o tamanho é o do inventário, não o do codex; a matriz segue as relações declaradas; a
  manutenção ficou fora da conta.

### Lugar, arquivos e nomes

Decidido em 2026-11-25.

- **Lugar:** `.claude/skills/decode-and-code/codex/`, na pasta compartilhada das skills
  (`redesign-brief.md:436`), que o pacote já leva (`empacotar.py:114`).
- **Arquivos:** um por tipo de conteúdo, com nome em inglês e conteúdo em pt-BR:

  | Arquivo | Tipo |
  |---|---|
  | `stages.md` | Etapa |
  | `artifacts.md` | Artefato |
  | `rules.md` | Regra |
  | `product-references.md` | Referência de produto |
  | `invariants.md` | Invariante |
  | `concepts.md` | Conceito |
  | `fix.md` | Capítulo do workflow de correção (item 39); vai para a pasta do módulo quando ele existir, na fase 2 |

- **Títulos:** o título de cada seção é único no codex inteiro, porque a leitura é por título.

## Fronteira

Decidido em 2026-11-25.

**Codex e skill.** O codex diz o que o DC faz, em que ordem, com que artefatos e com que garantias
(item 27). A skill guarda o procedimento: os passos, os comandos e o mecanismo. Um trecho é do codex
quando passa nos dois testes:

1. Continuaria verdadeiro se a skill, o script ou a versão do Claude Code mudassem
   (`atomic-inventory.md:881-882`).
2. Uma etapa precisa dele para decidir certo, e não só para executar.

**Núcleo e módulo.** O workflow de correção é o primeiro módulo e traz o próprio capítulo do codex
(itens 34 e 39). O núcleo nunca depende desse capítulo (item 58). O que é do módulo sai do núcleo
mesmo quando o item do inventário mistura os dois: no piloto, o decode enxuto da correção (item 06) e
a etapa C3 (item 09) foram para `fix.md`.

**Codex e o que fala do codex.** Os 8 itens que nenhum momento de leitura usa têm destinos
diferentes:

| Destino | Itens | Por quê |
|---|---|---|
| Codex | 55 Invariante, 56 Restrição fundamental | Limitam o que o setup e o rethink gravam no projeto: nada ali repete ou contradiz o codex, e o codex não é copiado para o projeto |
| Este guia | 27 Codex, 52 Camada, 54 Regra de dependência | Dizem o que o codex é e como se escreve; a regra de dependência é regra de escrita |
| Documentação de manutenção | 42 Migração, 58 Núcleo, 61 Quem mantém o plugin | Transição de release e arquitetura do plugin, que só quem o mantém usa |

O codex fica só com o que alguma etapa usa para trabalhar; o retrato completo do método passa a
depender também deste guia e da documentação de manutenção.

## Tipos de conteúdo

Decidido em 2026-11-25. Cada conceito é uma seção, e o tipo do conceito dá o modelo da seção.

**Parte comum a toda seção:** o título é o nome do conceito, estável; a primeira linha é *O que é*,
numa frase; a última é *Ver também*, com os títulos de outras seções. *Mecanismo hoje* e *Origem*, do
inventário, não entram: são mecanismo e história (item 27) e ficam no inventário, como registro.

| Tipo | Exemplos | Campos, além da parte comum |
|---|---|---|
| Etapa | workflow, decode, revisão, derive, code, correção | quem faz e em que papel; o que entra; o que sai; o gate de entrada e o de saída; as regras da etapa |
| Artefato | plano, plano técnico, plano mínimo, unidade, tarefa, história, handoff, tabela de recursos | o que contém; quem o cria e em que etapa; as regras que valem para ele |
| Regra | porte, aprovação, teste, cold-start, independência entre planos, Definition of Ready | quando vale; o que exige; o que acontece quando falha |
| Referência de produto | JTBD, os quatro riscos, hipótese, MVP, User Story Mapping | a fonte, com autor e obra; o que traz ao DC; em que etapa entra |
| Invariante | uma fonte por fato, restrição fundamental | o enunciado; o que protege; como se verifica |
| Conceito | usuário, Claude, papel, princípio, guideline, guardrail, foundation | o que é para o DC e onde aparece no trabalho |

O tipo *Conceito* é o mais genérico; o *Mapa* confere item a item, e o que não se encaixa bem num
tipo volta à pessoa.

## Regras de escrita

Decidido em 2026-11-25.

1. **Dependência.** Nenhum trecho cita skill, script, hook, versão do Claude Code ou projeto; todo
   trecho passa no teste do item 54 (`atomic-inventory.md:881-882`).
2. **Uma fonte por fato.** Cada fato mora numa seção só; as outras a citam pelo título, no texto ou
   em *Ver também*, e nunca o repetem (item 55). Uma etapa pode listar, no gate, a condição que
   aplica; o que ela não pode é reescrever a regra com outras palavras.
3. **Por quê sim, história não.** Uma regra pode trazer o porquê em uma frase, quando ele ajuda a
   aplicá-la num caso de fronteira. Data, medição, número de planos e caso passado ficam fora: são
   evidência e história (item 27).
4. **Um termo por conceito.** O nome dos itens do inventário é o glossário; o mesmo conceito nunca
   aparece com outro nome. Identificadores ficam em código: `fix`, `product`, `rule`. Uma palavra
   comum que coincide com um termo do glossário, usada em outro sentido, é trocada: na revisão,
   "lacunas" virou "o que falta", porque Lacuna é o item 70.
5. **Referências de produto.** Toda referência cita autor e obra e é descrita com palavras próprias,
   sem citação longa da fonte. Autor e obra ficam só na seção da referência, em
   `product-references.md`; as outras seções nomeiam a referência e a citam em *Ver também*.
6. **Idioma e voz.** Segue a rule `voice-and-language` do projeto, que esta regra cita e não repete.
   O texto é no presente, impessoal, e diz o que é e o que vale — não o passo a passo, que é
   procedimento da skill.
7. **Seção curta.** Teto de 40 linhas por seção; acima disso, a seção provavelmente tem dois
   conceitos. A média por item no inventário é 13,6 linhas (818 em 60). O teto é escolhido, não
   medido; o piloto da 1.3 o manteve, com a maior seção de `stages.md` em 23 linhas.

As regras 1 e 7 se conferem por script, com o `lint_codex.py`; a 2, por script fora do codex e por
leitura dentro dele; as 3 a 6, por leitura.

## Como mudar o codex depois

Decidido em 2026-11-25. Vale para os ajustes da fase 2 (D-04 do plano) e para as versões seguintes do
plugin.

1. **Reescrever no lugar.** O ajuste reescreve a seção afetada no modelo do seu tipo; nunca acrescenta
   exceção, nota, ressalva ou "a partir de".
2. **Mudar o conceito por inteiro.** Se o ajuste muda o que um conceito é, as seções que o citam são
   revistas na mesma mudança.
3. **Conceito novo vira seção própria.** Só entra se passa nos dois testes da *Fronteira*, com seção do
   seu tipo; nunca como subseção de outro conceito.
4. **Conceito que sai, sai inteiro.** A seção sai com as citações a ela nas outras seções.
5. **Sem histórico no codex.** O porquê e a data de cada ajuste ficam no plano, como decisão datada; o
   codex tem só a versão do plugin (item 27).
6. **Sinais de colcha.** Seção acima do teto de 40 linhas, campo fora do modelo do tipo ou regra que
   contradiz outra seção pedem reescrita antes de o ajuste fechar.

## Documentação de manutenção

Decidido em 2026-11-25.

- **Onde:** `docs/maintenance/`, fora do pacote. O nome da pasta e dos arquivos é em inglês e o
  conteúdo, em pt-BR, pela rule `voice-and-language` do projeto.
- **O que guarda:** este guia; o contrato de módulo e o núcleo
  (itens 34 e 58); o empacotamento, a release e quem mantém o plugin (item 61); a migração (item 42);
  e o conteúdo da norma que só serve a quem mantém o plugin, conforme o mapa da 2.1.
- **README:** as seções de manutenção — *Como este repositório se relaciona com o pacote* e
  *Procedimento de release* (`README.md:215`, `:228`) — passam para lá na fase 2, como um consumidor
  do mapa da 2.1, e o README fica com um link.

## Mapa

Decidido em 2026-11-25.

### Itens do inventário

| Destino | Itens | Total |
|---|---|---|
| `stages.md` | 04 Workflow, 05 Etapa, 06 Decode, 07 Revisão, 08 Derive, 09 Code, 48 Setup, 49 Rethink | 8 |
| `fix.md` | 13 Plano mínimo, 39 Correção, 65 Teste que reproduz o defeito | 3 |
| `artifacts.md` | 01 Pedido, 11 Plano, 12 Plano técnico, 15 Unidade, 16 Tarefa, 26 Foundation, 29 Mapa de recursos do projeto, 37 História, 45 Handoff, 59 Tabela de recursos do plano, 60 Objetivo do plano, 67 Proposta, 68 Entrega | 13 |
| `rules.md` | 03 Tipo, 14 Porte, 18 Aprovação, 19 Teste, 38 Definition of Ready, 41 Plano anterior ao redesign, 43 Raiz dos planos, 44 Cold-start, 46 Independência entre planos, 64 Teste do plano inteiro, 69 Critério de aceite, 70 Lacuna, 71 Numeração e nomenclatura | 13 |
| `product-references.md` | 32 Referência de produto, 33 Mindset de produto, 50 Fluxo de decodificação, 51 Paralelo com produto digital, 62 Os quatro riscos, 63 Hipótese, 66 MVP | 7 |
| `invariants.md` | 55 Invariante, 56 Restrição fundamental | 2 |
| `concepts.md` | 02 Insight, 21 Huddle, 22 Princípio, 23 Guideline, 24 Guardrail, 28 Padrão de código, 30 Recurso do projeto, 31 Papel, 35 Usuário, 36 Claude, 47 Registro de uso | 11 |
| Este guia | 27 Codex, 52 Camada, 53 Clean Architecture, 54 Regra de dependência | 4 |
| `docs/maintenance/` | 34 Módulo, 42 Migração, 58 Núcleo, 61 Quem mantém o plugin | 4 |

- **48 Setup e 49 Rethink** ficam em `stages.md`: não fazem parte dos workflows, mas cabem no modelo
  do tipo Etapa.
- **53 Clean Architecture** vem para este guia (decidido em 2026-11-25, na 1.2): ela organiza o
  método, não as soluções que o decode propõe, e nenhuma etapa decide algo por ela; no projeto, entra
  como guideline de quem a adota (23).
- **34 Módulo** vai para a manutenção, contra a matriz de leitura, que o ligou à correção: o contrato
  do módulo é de quem mantém o plugin, e nenhuma etapa decide algo por ele.

### Mecanismo hoje

Nenhum *Mecanismo hoje* vai para o codex. Cada um fica onde está e entra no mapa da 2.1:

| Onde fica | Itens |
|---|---|
| Skill da etapa | 09, 36, 45 |
| Script ou lint | 07, 08, 14, 15, 41, 55, 59, e o lint dos itens 27 e 54 |
| Hook | 24, 42, 48 |
| Configuração do projeto | 18 (regra `Skill(<nome>)`), 23 (rule com `paths`) |
| `.claude/log/` | 47 |
| Documentação de manutenção | 56, 58 |

### Pontos em aberto da 1.2

| Ponto | Lugar provável |
|---|---|
| Proposta | 67 Proposta, em `artifacts.md` (decidido em 2026-11-25) |
| Entrega | 68 Entrega, em `artifacts.md` (decidido em 2026-11-25) |
| Critério de aceite ou oráculo | 69 Critério de aceite, em `rules.md`; o termo "oráculo" sai (decidido em 2026-11-25) |
| Lacuna | 70 Lacuna, em `rules.md` (decidido em 2026-11-25) |
| O decode segue a Clean Architecture | 53 Clean Architecture, neste guia: organiza o método, não as soluções (decidido em 2026-11-25) |
| Teste antes da aprovação final no pequeno e no médio | 18, 19 e 64: o teste da entrega vale como teste do plano; no médio, uma aprovação só (decidido em 2026-11-25) |
| Divergências com o brief | fora do codex: o brief foi congelado, e vale o inventário (decidido em 2026-11-25) |
| Número do plano de correção | 11 Plano, com menção no 18: o número sai na aprovação do plano mínimo, C2 (decidido em 2026-11-25) |
| Numeração, `_planos.md` e nomenclatura | 71 Numeração e nomenclatura, em `rules.md`; o `_planos.md` é projeção por script e fica fora (decidido em 2026-11-25) |
| Gates A e B | 06 Decode, como gate de saída, e 50 Fluxo de decodificação (decidido em 2026-11-25) |
| MVP no DC | 66 MVP e 67 Proposta: declarado na proposta, medido no ponto que a hipótese declara (decidido em 2026-11-25) |
