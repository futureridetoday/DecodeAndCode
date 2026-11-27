---
# about
name: migration-map
type: doc
project: ""
description: Mapa da migração da norma para o codex — consumidores, regras seguidas sem citação, nomes que mudam, comportamento novo, destino de cada seção da norma, o que o DC grava no projeto, restrições do brief e a ordem das subpartes da 2.2
tags: [codex, redesign, migracao]

# history
author: Bortoli
created: 2026-11-27
status: draft
version: 0.1.0
updated: ""

# system
scope: project
source: ""
auto_load: false
checksum: ""
dependencies: [redesign-plan, codex-guide]
---

# Mapa da migração — da norma ao codex

Entrega da parte 2.1 do [plano do redesign](redesign-plan.md). Cada linha diz o que consome a norma
(`docs/plan/system/modelo-dev-units.md`), o trecho do codex que a substitui, a classificação pela
D-04 e como a migração se verifica. As subpartes da 2.2 nascem da lista 8.

**Estado:** levantado em 2026-11-27; aprovado pela pessoa em 2026-11-27, com as recomendações dos
casos K-01 a K-15 como decisão.

**Convenções**

- Caminhos partem da raiz. `scripts/` é `.claude/skills/decode-and-code/scripts/`; `codex/` é
  `.claude/skills/decode-and-code/codex/`; `skills/X` é `.claude/skills/X/SKILL.md`.
- **Sentido da palavra:** **M**, o método, que vai para o codex; **P**, a "norma do projeto", que vira
  princípios, guidelines e guardrails; **T**, o valor `norma` de `plan_type` e `unit_type`, que vira
  `rule`; **G**, o plural genérico "normas", as regras que valem para uma unidade.
- **Classificação (D-04):** **S**, simples, muda o consumidor; **C**, complexa, vai à pessoa com uma
  recomendação (seção *Casos complexos*, `K-NN`).
- **Verificação:** **teste**, automatizado; **prova**, execução num projeto de prova; **leitura**,
  conferida contra o codex.
- Seções do codex vão em itálico, pelo título.

## Como foi levantado

- **Busca por palavra inteira**, fora do registro que a 2.1 exclui: `norma` em 74 arquivos, `normas`
  em 16, `modelo-dev-units` em 35, `intake` em 12 e `implement` em 23 — 82 arquivos ao todo, todos
  nas listas 1 e 3 ou em *Falsos positivos*. A busca pelos títulos das 11 seções que o `dc.py` extrai
  e de mais 14 títulos citados nas skills não achou arquivo novo.
- **Leitura contra o codex:** os 30 scripts de `scripts/` (cabeçalho, constantes, funções públicas e
  cada trecho que aplica uma regra do método), os 4 hooks de `.claude/hooks/`, os 7 `SKILL.md` por
  inteiro e os 7 atalhos `dc.py` das skills, que são idênticos e só repassam ao `dc.py` compartilhado.
  Os testes acompanham o script que testam e não foram lidos linha a linha.
- **O codex já viaja no pacote:** `empacotar._copiar_skill` copia a pasta compartilhada inteira, e
  `codex/` está nela (`scripts/empacotar.py:164-186`).

## 1. Consumidores da norma

Um consumidor por arquivo; as linhas dizem cada ponto.

### Scripts e hooks

| # | Consumidor | O que consome | Sentido | Trecho do codex | D-04 | Verificação |
|---|---|---|---|---|---|---|
| 1.01 | `scripts/bootstrap.py:19-26`, `:84-107`, `:116-145` | copia a norma para `<plan_root>/system/`; `_fonte_norma` serve o `explicar` e o `huddle-fecho` | M | *Restrição fundamental*: o codex nunca é copiado ao projeto | C (K-12) | teste |
| 1.02 | `scripts/empacotar.py:118`, `:151`, `:223-310` | leva a norma a `reference/`, reescreve os links dela e o `project:` | M | nenhum: o codex já viaja em `codex/` | S, na 2.3 | teste e build |
| 1.03 | `scripts/empacotar.py:18-23` (docstring) | cita *Validar a ativação* | M | manutenção (lista 5) | S | leitura |
| 1.04 | `scripts/dc.py:197-230` (`normas`) | entrega o conteúdo da tabela `## Normas aplicáveis` | G | *Definition of Ready* | S: só a linha que cita a norma muda | teste |
| 1.05 | `scripts/dc.py:410-411`, `:635-655` (`huddle-fecho`) | imprime *Despejo* e *Momento* da norma do projeto ou do pacote | M | *Huddle* | C (K-12) | teste |
| 1.06 | `scripts/dc.py:658-688` (`explicar`) | imprime 4 seções do método e 5 avulsas | M | *Workflow*, *Decode*, *Porte*, *Cold-start*, *Huddle*, *Princípio*, *Guideline*, *Guardrail*, *Setup*, *Rethink* | C (K-12, K-13) | teste |
| 1.07 | `scripts/dc.py:302`, `:1021`, `:1025`, `:1040` | comentário e textos de ajuda | M | *Rethink*, *Huddle* | S | teste |
| 1.08 | `scripts/normas.py:2-30`, `:181-196` | `secoes` acha seção por prefixo de título; o docstring explica a norma | M, G | o extrator serve o codex, de títulos únicos | S | teste |
| 1.09 | `scripts/lint_unidade.py:2-24`, `:46-47`, `:93-137`, `:192-202` | teto de 8 passos, `unit_type` com `norma`, gate do `implement` | M, T, G | *Definition of Ready*, *Tipo* | C (K-05) | teste |
| 1.10 | `scripts/verificacao.py:13-27`, `:71-137` | oráculo de `unit_type: norma` por aprovação | T | *Tipo* (`rule`: aceite pela aprovação), *Teste* | S, dentro de K-02 | teste |
| 1.11 | `scripts/lib.py:56-70` | `PLAN_TYPES_VALIDOS` com `norma`; `MODOS` e `SKILLS` com `implement` e `intake`; comentários | M, T | *Tipo*, *Workflow* | C (K-02) | teste |
| 1.12 | `scripts/lint_plano.py:2-12` | tabela *O que cada porte carrega* | M | *Porte* | C (K-03) | teste |
| 1.13 | `scripts/handoff.py:48`, `:64`, `:104`, `:186` | cita *Como revisar uma entrega* e o caminho da norma no prompt | M | *Handoff*, *Entrega*, *Teste* | C (K-05) | teste |
| 1.14 | `scripts/huddle.py:16`, `:210-234` | o esqueleto do huddle gravado no projeto cita a norma, seção *Huddle* | M, P | *Huddle* | C (K-09, lista 6) | teste |
| 1.15 | `scripts/backlog.py:9`, `scripts/numeracao.py:7`, `:16`, `:49`, `scripts/nomenclatura.py:4`, `scripts/regioes.py:8`, `scripts/scaffold.py:7`, `:29`, `:126`, `scripts/rethink.py:8`, `scripts/rules.py:10`, `:17`, `:285`, `:395`, `:552`, `scripts/guardrail.py:17`, `scripts/eventos.py:2`, `scripts/activation_notice.py:85`, `:115`, `:128`, `scripts/descoberta.py:5`, `scripts/move-md.py:97` | comentário ou docstring que cita uma decisão ou seção da norma | M, P | a seção equivalente do codex, ou a manutenção pela lista 5 | S | leitura e busca |
| 1.16 | `.claude/hooks/pre_tool_use.py:7`, `.claude/hooks/instructions_loaded.py:8` | citam *Restrições conhecidas*, que não existe na norma | M | nenhum: a frase diz o motivo sozinha | S | leitura |
| 1.17 | `scripts/lint_codex.py:23` | diz que o `dc.py` e o `verificacao.py` consomem a norma | M | some quando os dois migram | S | leitura |

### Skills

| # | Consumidor | O que consome | Sentido | Trecho do codex | D-04 | Verificação |
|---|---|---|---|---|---|---|
| 1.18 | `skills/intake:58`, `:60`, `:70` | *Antes do plano*, *O que cada porte carrega* | M | *Workflow* (entrada), *Decode*, *Fluxo de decodificação*, *Proposta* | C (K-04) | prova |
| 1.19 | `skills/review-plan:5`, `:45`, `:55`, `:59-64`, `:73` | o modo `review`, os seis checks, *Avaliação de escopo*, *Quando cada porte cabe*, *Tipo de plano* | M | *Revisão*, *Plano técnico*, *Porte*, *Independência entre planos*, *Tipo* | C (K-04) | prova |
| 1.20 | `skills/derive:47`, `:57`, `:61-62`, `:66-67`, `:75`, `:81` | *Fluxo completo*, *Tipo de plano* (coluna *derive*), *Formato do arquivo de unidade*, *Huddle* | M | *Derive*, *Definition of Ready*, *Handoff*, *Unidade* | C (K-05) | prova |
| 1.21 | `skills/implement:42`, `:50`, `:52`, `:54`, `:60`, `:89` | os dois gates, *Fluxo completo*, *Fronteira skill / script*, *Huddle* | M, G | *Code*, *Entrega*, *Lacuna*, *Teste* | C (K-06) | prova |
| 1.22 | `skills/huddle:45`, `:64`, `:71`, `:85`, `:88`, `:93` | *Huddle*, *JSON pelo stdin*, *Camada normativa*, *Formato e vocabulário fechado*; destino "a norma" | M, P | *Huddle*, *Rethink* (as portas) | C (K-09) | prova |
| 1.23 | `skills/setup:43`, `:55-56`, `:64`, `:87`, `:118` | a norma como pré-condição, `explicar`, a tabela de princípios do método | M | *Setup*, *Foundation*, *Princípio* | C (K-10) | prova |
| 1.24 | `skills/rethink:5`, `:7`, `:45-53`, `:80` | *Rethink*, `explicar`; "norma do projeto" | M, P | *Rethink* | C (K-11) | prova |

### Manifestos, documentação e instruções deste repositório

| # | Consumidor | O que consome | Sentido | Trecho do codex | D-04 | Verificação |
|---|---|---|---|---|---|---|
| 1.25 | `.claude/plugin.json:4`, `.claude-plugin/marketplace.json:18` | descrição: "A norma em camadas (princípio, guideline, guardrail)…" | P | *Princípio*, *Guideline*, *Guardrail* | S | leitura |
| 1.26 | `README.md:5`, `:13-15`, `:62`, `:107-128`, `:133-213`, `:256` | o método, a norma em camadas, as skills pelo nome antigo | M, P, G | o codex inteiro, por link | S; seções de manutenção para `docs/maintenance/` (guia) | leitura |
| 1.27 | `docs/recursos/decode-and-code.md:9-101` | as três skills que executam a norma | M | *Revisão*, *Derive*, *Code* | S, depois de K-04 a K-06 | leitura |
| 1.28 | `docs/recursos/intake.md` | o `intake`, *Antes do plano*, *Nomenclatura*, *O que a avaliação não faz* | M | *Decode* | S, depois de K-04 | leitura |
| 1.29 | `docs/recursos/create-guardrail.md:7-8`, `:92`; `create-guideline.md:7-8`, `:20`, `:40`, `:54`, `:76`; `create-principle.md:7-8`, `:16`, `:41`, `:51`, `:92-93` | definições na *Camada normativa*; princípio entra como unidade `norma` | M, P, T | *Princípio*, *Guideline*, *Guardrail*, *Rethink* | S | leitura |
| 1.30 | `docs/recursos/hooks.md:26`, `:45`, `:58`, `:61` | *Validar a ativação*, *Log de uso* | M, P | *Registro de uso*; manutenção | S | leitura |
| 1.31 | `docs/recursos/huddle.md:29`, `:64`, `:69`; `rethink.md:9-71`; `setup.md:20`, `:63` | *Huddle*, *Log de uso*, *Setup*, *Rethink*; "norma do projeto" | M, P | *Huddle*, *Setup*, *Rethink* | S, depois de K-09 a K-11 | leitura |
| 1.32 | `.claude/CLAUDE.md:6-7`, `:31`, `:42-48`, `:65` | descrição do plugin, `docs/plan/system/` como norma do método | M, P | *Etapa* (o DC), o codex | S | leitura |
| 1.33 | `.claude/rules/principles.md:8`, `:43-44`; `.claude/rules/voice-and-language.md:24-25` | *Camada normativa → Princípio*, *Antes do plano*, *Nomenclatura* | M | *Princípio*, *Fluxo de decodificação*, *Numeração e nomenclatura* | S | leitura |
| 1.34 | `docs/maintenance/codex-guide.md:205` | conteúdo da norma que só serve a quem mantém | M | este mapa, lista 5 | S, na 2.3 | leitura |

### Testes, com o script que testam

| Testes | Seguem |
|---|---|
| `test_bootstrap.py`, `test_ciclo_instalado.py:256`, `test_dc.py:297`, `:344`, `:1263` | 1.01 |
| `test_empacotamento.py:27`, `:144`, `:350-385`, `:610-624`, `test_normas_system.py` | 1.02 e a 2.3 |
| `test_explicar.py`, `test_dc.py` (`explicar`, `huddle-fecho`) | 1.05, 1.06 |
| `test_normas.py`, `test_guidelines_aplicaveis.py`, `test_auditoria.py`, `test_eventos.py`, `test_session_start.py` | 1.04, 1.08 — "normas" no sentido G |
| `test_lint_unidade.py`, `test_porte_e_aprovacao.py`, `test_lint_plano.py`, `test_scaffold.py`, `test_scaffold_idempotente.py` | 1.09, 1.11, 1.12, K-03 |
| `test_handoff.py:113` | 1.13 |
| `test_rules.py:64`, `test_arquivar_rules.py`, `test_arquivar_guardrail.py`, `test_guardrail.py`, `test_rethink.py`, `test_activation_notice.py` | 1.15, K-11 |
| `test_skill_base.py`, `test_fixtures.py`, `tests/fixtures.py`, `test_huddle_cycle.py`, `test_lint_codex.py`, `test_move_md.py`, `test_nomenclatura.py:37` | lista 3 e K-02 |

## 2. Regras da norma seguidas sem citá-la

| # | Consumidor | A regra de hoje | O que o codex diz | D-04 | Verificação |
|---|---|---|---|---|---|
| 2.01 | `scripts/porte.py:4-5`, `:82-134` | porte declarado contra real por arquivos e tarefas; "ausente cai no grande" | *Porte*: conta entregas; na dúvida, o menor | C (K-03) | teste |
| 2.02 | `scripts/backlog.py:154-170` | médio projeta `## Tarefas`; pequeno lê `status` | *Porte*: o médio tem 1 unidade | C (K-03) | teste |
| 2.03 | `scripts/handoff.py:6-8` | `_handoff.md` só no grande | *Handoff*: um por plano, no médio e no grande, com as seções do codex pelo título | C (K-05) | teste |
| 2.04 | `scripts/scaffold.py:1-40`, `:161-251` | plano vai para `<core>/<NNNN>-<nome>`; pequeno e médio sem subpasta; o número sai no `derive` | *Raiz dos planos*: sem pasta por parte do sistema; médio e grande são pasta. *Aprovação*: número em P4 | C (K-03, K-04) | teste |
| 2.05 | `scripts/scaffold.py:121-158` (`concorrentes`), `dc.py concorrencia` | concorrência = mesmo `core` ou `module` em desenvolvimento | *Independência entre planos*: concorrem os que mudam o mesmo comportamento; a revisão avisa e registra | C (K-07) | teste |
| 2.06 | `scripts/nomenclatura.py:90-112` | colisão de nome procurada no alvo por `core` e `module` | *Raiz dos planos*: todos os planos juntos | S, dentro de K-03 | teste |
| 2.07 | `scripts/lint_plano.py:88-106` | `## Independência` exigida no grande, dispensada no médio, recusada no pequeno | *Revisão*: todo plano declara a independência | C (K-03) | teste |
| 2.08 | `scripts/lint_unidade.py:34-46` | blocos do corpo e teto de 8 passos | *Definition of Ready*; o teto sai (D-06) | C (K-05) | teste |
| 2.09 | `scripts/reconciliar.py:2` | reconcilia "duas cópias do método" entre repositórios | *Restrição fundamental* | C (K-14) | leitura |
| 2.10 | `skills/huddle` (*Promover*) | o huddle grava guideline e guardrail | *Rethink*: só o setup, o rethink e um plano `rule` gravam; o huddle propõe | C (K-09) | prova |
| 2.11 | `skills/setup` (etapas 2 e 5) | huddle na etapa 5; princípios do método oferecidos | *Setup*: huddle primeiro; princípios só do objetivo e do que nunca pode ser violado | C (K-10) | prova |
| 2.12 | `skills/derive` (passo 1) | o `derive` aprova e numera | *Aprovação*: o número sai em P4, no fim da revisão | C (K-04) | prova |
| 2.13 | `skills/implement` | quem executa não pergunta; insuficiência volta como relatório | *Lacuna*: Claude para, propõe o ajuste e segue com a aprovação | C (K-06) | prova |
| 2.14 | `skills/intake:57` | escada de menor intervenção para recurso do Claude Code | não está no codex; o gate B (*Decode*) é o equivalente | C (K-04) | prova |
| 2.15 | `scripts/descoberta.py:21-84` | inventaria rules, guidelines e guardrails existentes | *Setup*: também o mapa de recursos e o padrão de código | S, dentro de K-10 | teste |
| 2.16 | `.claude/hooks/session_start.py` | propõe o setup pendente; lembra o huddle atrasado | *Setup* ("proposto quando falta"), *Huddle* | nenhuma: já cumpre | — |

## 3. Nomes que mudam

| Nome | Para | Ocorrências fora do registro | Onde muda |
|---|---|---|---|
| `intake` | `decode` | `skills/intake/` (pasta e `SKILL.md`), `scripts/lib.py:66-70`, `.claude/CLAUDE.md:42`, `README.md:111`, `docs/recursos/intake.md`, `docs/recursos/decode-and-code.md:94`, `docs/recursos/huddle.md:29`; testes `test_dc.py`, `test_empacotamento.py`, `test_handoff.py`, `test_huddle_cycle.py`, `test_skill_base.py` | K-04 |
| `implement` | `code` | `skills/implement/`, `scripts/lib.py:64`, `scripts/handoff.py:48`, `scripts/lint_unidade.py:2`, `scripts/verificacao.py:27`, `:115`, `scripts/normas.py:4`, `scripts/dc.py:663`, `skills/derive:73`, `skills/intake:70`, `skills/setup:111`, `:134`, `.claude/CLAUDE.md:42`, `README.md:107`, `:128`, `docs/recursos/decode-and-code.md`, `docs/recursos/huddle.md:29`, `docs/recursos/intake.md:84`; testes `test_ciclo_instalado.py`, `test_dc.py`, `test_empacotamento.py`, `test_fixtures.py`, `test_handoff.py`, `test_lint_codex.py`, `test_lint_plano.py`, `test_skill_base.py` | K-06 |
| norma (o método) | codex | todo consumidor da lista 1 com sentido M | cada subparte, pela linha |
| norma (do projeto) | princípios, guidelines e guardrails | os da lista 1 com sentido P | cada subparte, pela linha |
| `norma` em `plan_type` e `unit_type` | `rule` | `scripts/lib.py:61`, `scripts/lint_unidade.py:47`, `:93-137`, `scripts/verificacao.py:19`, `:71-137`, `docs/recursos/create-principle.md:41`, `README.md:161` | K-02 |

Os comandos de barra mudam junto: `/decode-and-code:intake` vira `/decode-and-code:decode`, e
`/decode-and-code:implement` vira `/decode-and-code:code`.

## 4. O que o codex descreve e nenhum consumidor faz hoje

| # | Comportamento | Codex | Quem o traz |
|---|---|---|---|
| 4.01 | Entrada: tipo declarado com o motivo, objetivo do plano confirmado, insight sem plano | *Workflow*, *Objetivo do plano*, *Insight* | K-04 |
| 4.02 | Proposta escrita para o usuário, com papéis, hipótese, MVP, apetite e os quatro riscos; aprovação P2 | *Decode*, *Proposta*, *Papel*, referências de produto | K-04 |
| 4.03 | Tabela de recursos do plano, tirada do mapa; conferida na revisão, no derive e no code | *Tabela de recursos do plano* | K-04, K-05 |
| 4.04 | Revisão que escreve o plano técnico: histórias INVEST, critérios, tarefas, decisões e riscos; fontes técnicas abertas; porte contra apetite | *Revisão*, *Plano técnico*, *História* | K-04 |
| 4.05 | Número na aprovação do plano técnico (P4); estados rascunho, aprovado, fechado e descartado | *Aprovação*, *Plano* | K-03, K-04 |
| 4.06 | Versão do formato no plano e leitura pela regra anterior quando falta | *Plano*, *Plano anterior ao redesign* | K-01 |
| 4.07 | Médio com 1 unidade, derive e handoff; aprovação das unidades derivadas juntas | *Porte*, *Derive*, *Handoff*, *Aprovação* | K-03, K-05 |
| 4.08 | Definition of Ready como lista: história, critério com teste, tarefas, arquivos, guidelines, padrão de código, recursos, decisões, lacunas, o que espera das anteriores | *Definition of Ready* | K-05 |
| 4.09 | Code: unidade ajustada quando a anterior divergiu; ação irreversível pede o sim na hora; achado fora do escopo vira pedido ou huddle; pequeno também passa pelo code | *Code* | K-06 |
| 4.10 | Lacuna com parada, proposta de ajuste e aprovação; vale também para a tarefa do pequeno | *Lacuna* | K-06 |
| 4.11 | Teste do plano inteiro (P8) no grande, contra um critério do plano técnico; falha vira lacuna | *Teste do plano inteiro* | K-06 |
| 4.12 | Workflow de correção: diagnóstico, plano mínimo, teste vermelho registrado no relatório, passagem para produto | `fix.md` inteiro | K-08 |
| 4.13 | Foundation com o padrão de código e o mapa de recursos; permissão de uso por recurso | *Foundation*, *Mapa de recursos do projeto*, *Recurso do projeto* | K-10 |
| 4.14 | Rethink atualiza a foundation e o mapa; lista os planos abertos que citam item retirado; aponta instruções do time que contradizem | *Rethink* | K-11 |
| 4.15 | Huddle: ponto de verificação da hipótese como entrada com data; gatilhos de quando Claude registra | *Huddle* | K-09 |
| 4.16 | Auditoria do pacote contra dado de outro projeto | restrição do brief, `redesign-brief.md:203` | K-15 |

## 5. Destino de cada seção da norma

| Seção (linha) | Destino |
|---|---|
| Cabeçalho e *O gargalo que o modelo precisa resolver* (22, 39) | descarte: evidência e história, já em `registro-dev-units.md` |
| *Plano e módulo são eixos diferentes* (57) | descarte: o codex tem *Raiz dos planos*, sem pasta por parte do sistema |
| *Cold-start é o critério de suficiência da unidade* (69) | codex, *Cold-start* |
| *1. Hierarquia estrutural* (97) | codex, *Plano*, *Unidade*, *Raiz dos planos*; core, módulo e bloco como pasta saem |
| *2. Estado derivado de verificação* (155) | codex, *Teste*; mecanismo em `verificacao.py` e `backlog.py` |
| *3. Camada normativa* (186) | codex, *Princípio*, *Guideline*, *Guardrail*; a *Referência* sai, porque o codex não a tem como camada |
| *Guardrail fundador — regra de dependência entre cores* (202) | descarte: arquitetura do projeto entra como guideline (*Guideline*) |
| *Princípio* (221) e a tabela dos princípios do método (251) | codex, *Princípio*; a tabela sai (K-10) |
| *Guideline* (263) | codex, *Guideline*; o formato de `paths:` na skill do setup |
| *Editar e arquivar* (285) | codex, *Rethink*; mecanismo em `rules.py` e `guardrail.py` |
| *Validar a ativação* (339) | manutenção, `docs/maintenance/activation.md` (novo) |
| *Empacotamento* (390) | manutenção, `docs/maintenance/packaging.md` (novo, item 61) |
| *Reconciliação* (472) | manutenção, com o `reconciliar.py` (K-14) |
| *4. Norma de lote e decomposição* (492) | descarte: o teto sai (D-06), e a decomposição está em *Porte* |
| *5. Preservação do que funciona* (516) | descarte: história; as lacunas estão em *Lacuna* |
| *Regiões — quem escreve o quê* (532) | script, `regioes.py`; a regra "não editar à mão" no codex, *Teste* |
| *Blocos do corpo* (553) e *Precedência entre os blocos* (574) | codex, *Definition of Ready* e *Code* ("o critério de aceite manda"); o formato na skill do derive |
| *Identificador* (595) | codex, *Numeração e nomenclatura* |
| *Tipo de unidade* (606) e *`norma`* (627) | codex, *Tipo* (`rule`); mecanismo em `lint_unidade.py` e `verificacao.py` |
| *Ciclo quando o teste ainda não existe* (657) | codex, *Critério de aceite*; mecanismo em `verificacao.py` |
| *Antes do plano — fluxo de decodificação* (671) | codex, *Fluxo de decodificação* e *Decode* |
| *Alvo* (697), *Backlog* (739) | script (`scaffold.py`, `backlog.py`) e skill da revisão |
| *Aprovação — quatro campos* (719) | codex, *Aprovação* (quem e quando); os campos no script |
| *`_handoff.md`* (762) | codex, *Handoff*; formato em `handoff.py` e na skill do derive |
| *Bloco obrigatório — Independência* (790) | codex, *Independência entre planos* |
| *O que cada porte carrega* (799), *Quando cada porte cabe* (823) | codex, *Porte* |
| *Tipo de plano* (843) | codex, *Tipo* |
| *Porte medido* (877) | script, `porte.py`; manutenção para o porquê |
| *Avaliação de escopo* (904), *O teste* (918), *A checagem* (926), *Quando não dividir* (933), *O que a avaliação não faz* (945) | codex, *Independência entre planos*; *O caso que originou a regra* (909) é descarte |
| *Nomenclatura* (962), *Plano* (967), *Unidade* (1010) | codex, *Numeração e nomenclatura*; mecanismo em `nomenclatura.py` e `numeracao.py` |
| *Tabela de planos* (1033) | script: `_planos.md` é projeção (guia, *Pontos em aberto*) |
| *Divisão de responsabilidade* (1053), *Fronteira skill / script* (1137), *Modelos* (1166) | manutenção, `docs/maintenance/skills-and-scripts.md` (novo) |
| *Camada de execução* (1066), *Skills `review-plan`, `derive` e `implement`* (1074) | skill de cada etapa |
| *Modo `review` — os seis checks* (1087) | codex, *Revisão*; o como na skill |
| *Os dois gates* (1103) | codex, *Code* (gates de entrada e de saída) |
| *Como revisar uma entrega* (1111) | codex, *Entrega* e *Teste*; o como na skill do code |
| *Huddle* (1202), *Despejo* (1276), *Momento* (1290), *Quem registra* (1313) | codex, *Huddle* |
| *Formato e vocabulário fechado* (1225), *H-XX* (1230) | script `huddle.py` e skill do huddle |
| *Sem arquivo de template* (1334) | manutenção, `skills-and-scripts.md` |
| *Log de uso* (1348) | codex, *Registro de uso*; mecanismo em `eventos.py`, porquê na manutenção |
| *Bootstrap* (1412) e subseções | script `bootstrap.py`; porquê na manutenção, `packaging.md` |
| *Setup — o primeiro uso* (1465) | codex, *Setup*; o como na skill |
| *Conversa de uma sugestão* (1514) e subseções: *As opções*, *JSON pelo stdin*, *Padrões de `paths`*, *Formato do guardrail* | procedimento compartilhado por setup, rethink e huddle (K-13) |
| *Rethink* (1567) | codex, *Rethink*; o como na skill |
| *Fluxo completo* (1614) | codex, *Workflow* |
| *Ciclo instalado* (1648), *O que prova* (1656) | manutenção, `packaging.md` |

## 6. O que o DC grava num projeto a partir da norma

| # | O que | Quem grava | O que a 2.4 faz |
|---|---|---|---|
| 6.01 | A cópia `<plan_root>/system/modelo-dev-units.md` | `bootstrap.iniciar` | apaga, com aprovação (item 42) |
| 6.02 | Os princípios do método em `.claude/rules/principles.md`, com origem `arquivo <plan_root>/system/modelo-dev-units.md` no `setup.md` | skill `setup`, etapa 2 | nada: o projeto que os aceitou os tem como seus; a linha de origem fica como registro |
| 6.03 | O esqueleto do huddle, que cita a norma, seção *Huddle*, e a tag `pre-norma` | `huddle.iniciar`, `huddle.py:204-248` | troca o parágrafo e a tag pelo texto novo, com aprovação |
| 6.04 | Unidades de planos abertos com `## Normas aplicáveis` apontando para seções da norma | skill `derive` | lista os planos abertos ao usuário: depois de 6.01, essas linhas vão para `Não resolvidas:`; o plano é atualizado quando ele o leva à revisão, ao derive ou ao code (*Plano anterior ao redesign*) |
| 6.05 | `_handoff.md` de planos abertos, que cita o caminho da norma | `handoff.gerar` | o mesmo de 6.04: regerado quando o plano volta ao derive |

## 7. Restrições do brief

| Restrição (`redesign-brief.md`) | Quem a cumpre |
|---|---|
| Renomear: norma, `intake`, `implement`, `norma` em `plan_type` e `unit_type` (:196) | K-02, K-04, K-06 e a subparte de documentação (lista 3) |
| Não refazer o plugin: a suíte continua passando (:197) | toda subparte, pelo critério de aceite da 2.2 |
| Codex à prova de futuro, com lint (:198) | 1.4, feita; a ligação do `lint_codex.py` ao CI entra na subparte 2.2.01 |
| DC otimizado para Claude: `SKILL.md` abaixo de 500 linhas e o mínimo carregado (:199) | cada subparte de skill confere o próprio `SKILL.md` |
| O projeto não altera o codex (:200) | K-12 e a 2.4 |
| O decode segue Clean Architecture (:201) | o guia, feito na 1.1; no projeto, como guideline; nenhuma subparte |
| Uma fonte por fato (:202) | lint de repetição em cada subparte; os 3 trechos conhecidos somem em K-04, K-10 e K-11 |
| Nada específico de projeto viaja (:203) | K-15 |
| Módulo plug and play (:204) | K-08: o módulo de correção sai sem quebrar a suíte |

## Casos complexos (D-04)

Cada um com a recomendação; a pessoa decide.

| # | Caso | Recomendação |
|---|---|---|
| K-01 | **Versão do formato.** Todo comportamento novo depende de saber se o plano é do formato novo. | Subparte própria, primeiro: campo `format_version` no frontmatter; sem ele, os scripts seguem a regra de hoje. Sem isso, cada subparte quebraria os 23 planos fechados e os rascunhos do `_inbox/`. |
| K-02 | **`norma` vira `rule`** em `plan_type` e `unit_type`. | Junto da K-01: `rule` no formato novo, `norma` aceito só sem versão. |
| K-03 | **Porte por entregas e raiz dos planos**: `porte.py`, `backlog.py`, `lint_plano.py`, `scaffold.py`, `nomenclatura.py`. | Subparte própria, depois da K-01: médio vira pasta com 1 unidade, sem pasta por `core`, independência em todo porte; o `core:` fica como campo. |
| K-04 | **Decode e revisão.** O `intake` vira `decode` e passa a escrever a proposta; o `review-plan` passa a escrever o plano técnico; o número vai do `derive` para o P4. A escada de recursos do Claude Code não está no codex. | Duas subpartes, decode e depois revisão. A escada fica como passo a passo do gate B no `decode`, porque é o mínimo viável aplicado a recurso do Claude Code. |
| K-05 | **Derive**: Definition of Ready no lugar dos blocos, teto sai (D-06), médio com unidade, handoff no médio e no grande citando o codex pelo título. | Subparte própria, depois da K-03 e da K-04. |
| K-06 | **Code**: `implement` vira `code`; lacuna com parada e aprovação; P8; ação irreversível; pequeno também passa pela skill. | Subparte própria, depois da K-05. O subagent em fork conta como sessão nova: roda sem o histórico. |
| K-07 | **Concorrência por `core` e `module`.** O codex define concorrência por comportamento, que script não mede. | Remover o comando `concorrencia` e deixar a checagem como julgamento da revisão, que avisa e registra. Alternativa: manter como aviso. |
| K-08 | **Workflow de correção.** Nenhum consumidor o faz. | Subparte própria, depois da K-06, como módulo que sai sem quebrar a suíte. |
| K-09 | **Huddle grava guideline e guardrail** (*Promover*), contra as três portas do *Rethink*. | Manter o codex: *Promover* vira "propor", que fecha a entrada com destino `rethink` ou um pedido de plano `rule`. Alternativa: acrescentar o huddle como quarta porta no codex. |
| K-10 | **Setup**: huddle primeiro, foundation com padrão de código e mapa de recursos com permissão, sem os princípios do método. | Subparte própria; a foundation mora em `<plan_root>/system/foundation.md` (*Raiz dos planos*), escrita por script, com o sim a cada escrita. |
| K-11 | **Rethink**: foundation e mapa, planos abertos que citam item retirado, instruções do time. | Subparte própria, depois da K-10. |
| K-12 | **Fonte do `explicar` e do `huddle-fecho`**: hoje leem a norma copiada no projeto; o codex não é copiado. | Os dois passam a ler `codex/` do pacote, pelo título da seção. É a condição para a 2.3 tirar a cópia. |
| K-13 | **Procedimento compartilhado** (*Conversa de uma sugestão*, *JSON pelo stdin*, *Padrões de `paths`*, *Formato do guardrail*): é passo a passo, não codex, e três skills o usam. | Um arquivo de referência na pasta compartilhada, fora de `codex/`, impresso por `explicar conversa`. É lugar novo: o guia só prevê codex, skill, script e manutenção. |
| K-14 | **`reconciliar.py`** compara duas cópias do método entre repositórios. | Fica fora da migração: é ferramenta de manutenção, não viaja e não copia nada a um projeto. A seção da norma vai para a manutenção. |
| K-15 | **Auditoria contra dado de outro projeto**: nenhum consumidor a faz. | Subparte pequena em `empacotar.verificar`, com a lista de marcas de outros projetos no `config.json`. |

## Falsos positivos

| Ocorrência | Por quê |
|---|---|
| `docs/plan/system/language-policy.md:7-105` | a política chama a si mesma de "norma": regra deste repositório, não do método |
| `docs/plan/system/porte-medido.md:41-42` | nome de plano fechado (`0010-fix-norma-entry-gate`), registro |
| `scripts/tests/test_harness.py:5` | "o interpretador atende à norma": a versão mínima do Python |
| `scripts/move-md.py:35` | "read-only por norma", no sentido comum |
| `.claude/rules/principles.md:50` | "conflito entre normas ativas", no sentido comum do protocolo de exceção |
| `codex/rules.md:237` | o codex dizendo que o tipo `norma` vira `rule` |

## 8. Ordem e lotes

Uma subparte por PR, salvo onde diz. Nenhuma corre junto de outra: quase todas tocam o `dc.py` ou os
testes dele.

| Subparte | Conteúdo | Depende de | Lote |
|---|---|---|---|
| 2.2.01 | Comentários e docstrings (1.15, 1.16, 1.17) e o `lint_codex.py` no CI | — | 1 PR |
| 2.2.02 | Conteúdo de manutenção da norma para `docs/maintenance/` (lista 5) | — | 1 PR |
| 2.2.03 | Versão do formato e `rule` (K-01, K-02) | 2.2.01 | 1 PR |
| 2.2.04 | Fonte do `explicar` e do `huddle-fecho`, e o procedimento compartilhado (K-12, K-13) | 2.2.03 | 1 PR |
| 2.2.05 | Porte e raiz dos planos (K-03, K-07) | 2.2.03 | 1 PR |
| 2.2.06 | Decode (K-04, primeira parte) | 2.2.05 | 1 PR |
| 2.2.07 | Revisão (K-04, segunda parte) | 2.2.06 | 1 PR |
| 2.2.08 | Derive (K-05) | 2.2.07 | 1 PR |
| 2.2.09 | Code (K-06) | 2.2.08 | 1 PR |
| 2.2.10 | Correção (K-08) | 2.2.09 | 1 PR |
| 2.2.11 | Setup e foundation (K-10, 2.15) | 2.2.04 | 1 PR |
| 2.2.12 | Rethink (K-11) | 2.2.11 | 1 PR |
| 2.2.13 | Huddle (K-09, 1.14, 4.15) | 2.2.12 | 1 PR |
| 2.2.14 | Auditoria do pacote (K-15) | 2.2.01 | 1 PR |
| 2.2.15 | Documentação, manifestos e instruções deste repositório (1.25 a 1.34), com as seções de manutenção do README | todas as anteriores | 1 PR |

Cada subparte é detalhada e aprovada antes de começar (2.2), com as linhas deste mapa que cobre, e
marca aqui as linhas migradas.

## Registro da migração

Uma linha por subparte fechada: as linhas do mapa que ela migrou, o PR e o que ficou para outra.

| Subparte | Linhas migradas | PR | Notas |
|---|---|---|---|
| 2.2.01 | 1.15 (menos 8 pontos), 1.16, 1.17; lint de repetição na suíte | #70 | Ficam para a 2.2.02, com o destino na manutenção: `rules.py:10`, `:17`, `:552`, `activation_notice.py:85`, `:115`. Ficam para a 2.2.05, porque descrevem core e módulo, que saem em K-03: `scaffold.py:7`, `:29`, `:126`. O trecho repetido do `setup` mudou desde a 1.4: hoje é "a mudança aproxima o projeto do objetivo" (`setup:85`, contra *Princípio*). |
| 2.2.02 | 1.03; da lista 5, *Validar a ativação*, *Empacotamento*, *Reconciliação*, *Porte medido* (o porquê), *Divisão de responsabilidade*, *Fronteira skill / script*, *Modelos*, *Sem arquivo de template*, *Log de uso* (o porquê), *Bootstrap* (o porquê) e *Ciclo instalado*; os 5 pontos de 1.15 adiados da 2.2.01 | #71 | Três arquivos novos em `docs/maintenance/`: `activation.md`, `packaging.md`, `skills-and-scripts.md`, listados no guia. A norma fica intacta até a 2.3 (D-05). Os nomes `intake` e `implement` nesses arquivos mudam na 2.2.06 e na 2.2.09. As seções *Não inventar ativação* e *Ativação silenciosa*, citadas em `rules.py`, não existiam na norma; o comentário passou a dizer o motivo. |
| 2.2.03 | K-01, K-02; 1.10, 1.11 (tipos), sentido T de lista 3 no código | #72 | `lib.formato` lê `format_version` do plano (a unidade herda); sem o campo, formato 1, a regra de antes. `lib.PLAN_TYPES_POR_FORMATO` e `UNIT_TYPES_POR_FORMATO`: `rule` no 2, `norma` no 1; `lint_plano`, `scaffold.aprovar`, `lint_unidade` e `verificacao` leem pelo formato. Quem passa a escrever `format_version: 2` é o decode e a revisão (2.2.06, 2.2.07). As menções em documentação ficam para a 2.2.15. Teste: `test_formato.py`. |
| 2.2.04 | K-12, K-13; 1.05, 1.06, 1.08 (o extrator) | — | `normas.secao_do_codex` acha a seção pelo título exato, no `codex/` do pacote; `explicar` e `huddle-fecho` deixam de ler a norma. `camada-normativa` imprime *Princípio*, *Guideline* e *Guardrail*. O procedimento compartilhado mora em `decode-and-code/procedures/suggestion-conversation.md`, impresso por `explicar conversa`, e viaja no pacote. As skills que diziam "momento da norma (*Huddle*)" passaram a citar a seção do codex. `bootstrap._fonte_norma` continua só para a cópia, que sai na 2.3. |
