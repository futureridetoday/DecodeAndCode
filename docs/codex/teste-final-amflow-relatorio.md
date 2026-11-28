---
# about
name: teste-final-amflow-relatorio
type: doc
project: DecodeAndCode
description: Relatório do teste final do DC 3.0 numa cópia do AmFlow — veredito, erros, oportunidades, métricas, comparação com o gabarito 0028, limites e contornos
tags: [codex, redesign, teste, release]

# history
author: Bortoli
created: 2026-11-27
status: draft
version: 1.0.0
updated: ""

# system
scope: project
source: local
auto_load: false
checksum: ""
dependencies: [teste-final-amflow]
---

# Relatório do teste final do DC 3.0 no AmFlow

Plano: [`teste-final-amflow.md`](teste-final-amflow.md). Ambiente, logs e cópia:
`/Users/rafaelbortoli/Code/decode-and-code-experiments/dc3-amflow-final/` — `logs/NN-*.jsonl` (um por
chamada), `achados.md` (notas por etapa), `tools/` (runner, resumo e métricas), `gabarito-0028-*.md`
e a cópia em `amflow/`, com uma tag por etapa (`etapa-00` a `etapa-06`).

## 1. Veredito

**Pronto com ressalvas.** O workflow inteiro roda num projeto real e produz um plano tão bom quanto o
original, e melhor em quatro pontos. Nenhum dado se perdeu e o gate entre unidades segura. Mas a
migração de um projeto que já usa o método deixa restos e um aviso permanente (E-01, E-03), e o
handoff manda executar em paralelo o que o gate recusa (E-02). Corrigir E-01 a E-05 antes da release.

## 2. Erros

Severidade: **bloqueia** a release, **grave** ou **menor**. Nenhum bloqueia.

### E-01 — O aviso de migração não some e manda para um comando que não resolve (grave)

- **Etapa:** 1 e 4.
- **Evidência:** antes do setup, o aviso é só "Setup do decode-and-code pendente" para um projeto que
  usa o método há meses (`logs/01-primeira-sessao.jsonl`, evento `hook_response` do `SessionStart`).
  Depois do setup concluído e da migração aplicada, toda sessão nova abre com "este projeto ainda tem
  o que o método anterior gravou. Rode /decode-and-code:setup para migrar" (`logs/04a-decode.jsonl`,
  primeiro `hook_response`). O setup concluído encerra logo depois do `migrar`, e só restam os 6
  rascunhos do `_inbox` que citam a norma, que o próprio `migrar` diz que só se atualizam na
  revisão. O modelo repetiu o aviso ao usuário no fim da revisão (`logs/05a-review.jsonl`, texto
  final).
- **Causa provável:** `migracao.py:63` conta os planos abertos em `pendencias`, e
  `session_start.py:88-96` avisa sempre que `pendencias` não está vazia. Antes do setup,
  `session_start.py:118-119` devolve só o aviso de setup.
- **Correção sugerida:** o aviso de migração olha só `norma` e `huddles`; planos abertos ficam no
  `migrar`, ou ganham um aviso próprio que não manda ao setup. Antes do setup, num projeto com norma
  copiada, a mensagem diz "migração", não "setup pendente".

### E-02 — O handoff manda abrir em paralelo o que o gate recusa (grave)

- **Etapa:** 5, 6 e 7.
- **Evidência:** o plano (`## Unidades`, *Ordem*: "A 1 e a 3 abrem já… A 8 abre com a 2") e o
  `_handoff.md` (*A fila*: "`0028-03` — abre já, em paralelo com a 01"; ordem 01, 03, 02, 04, 08,
  05…). Conferido fora do modelo: `entrada-code` da 03 sai `1` com "a unidade anterior 0028-01 ainda
  não teve a entrega aprovada" e "…0028-02…". A 01 é medição em staging e com máquinas Windows
  (etapa 8): pelo gate, nenhuma outra unidade do plano anda até ela fechar. No original, a 01 e a 03
  correram em paralelo.
- **Causa provável:** `entrega.py:44-50` toma como anteriores todas as unidades de número menor, e
  `stages.md:143` diz "na ordem do handoff". O derive escreve a fila com julgamento (`derive/SKILL.md`,
  passo 7) e nada a confere contra o gate.
- **Correção sugerida:** escolher uma fonte. Ou o gate lê `## Depende de` da unidade (já existe em
  cada uma), ou o derive numera na ordem da fila e o `handoff` recusa fila fora da ordem numérica.

### E-03 — A migração do huddle deixa o corpo antigo e o link para a norma apagada (grave)

- **Etapa:** 2.
- **Evidência:** depois de `migrar --aplicar huddle`, só `description` e `tags` mudaram; o corpo
  continua com "sai — para a norma" e `[modelo-dev-units.md](modelo-dev-units.md)`
  (`amflow/docs/plan/system/huddle/bortoli.md`, linhas 24-29, tag `etapa-03`). O `migrar` seguinte já
  não lista o huddle. O modelo achou o link morto sozinho (`logs/03b-setup.jsonl`).
- **Causa provável:** o terceiro par de `huddle.ESQUELETO_ANTERIOR` (`huddle.py:256-266`) não casa
  com o texto real do AmFlow (link em vez de caminho, quebra de linha e "*Fechadas*" diferentes), e
  `migracao.py:51-53` considera o arquivo migrado quando nenhum par casa mais.
- **Correção sugerida:** detectar o resto pelo que importa (qualquer citação a `modelo-dev-units` no
  arquivo), não pelo texto exato; e, se a troca não for possível, listar o trecho para a pessoa.

### E-04 — Em toda skill com aprovação, a resposta da pessoa perde a liberação do `dc.py` (grave)

- **Etapa:** 2 a 6.
- **Evidência:** a resposta "sim" ao setup, por `--resume`, teve os dois `migrar --aplicar` negados
  ("This command requires approval", `logs/02b-setup-migracao.jsonl`, `permission_denials`). Toda
  aprovação seguinte (P2, P4, P5) só rodou porque a resposta foi mandada como
  `/decode-and-code:<skill> <resposta>` (contorno, seção 7). Em sessão interativa, o efeito é um
  pedido de permissão por comando `dc.py` no turno da aprovação, que é justamente quando rodam
  `aprovar`, `handoff` e o fecho do huddle.
- **Causa provável:** a liberação do `allowed-tools` vale só no turno em que a skill carrega. Só
  `setup/SKILL.md:37-39` e `rethink` avisam; `decode`, `review-plan` e `derive` terminam o turno na
  pergunta de aprovação.
- **Correção sugerida:** a pergunta de aprovação dessas skills orienta a resposta pela skill
  (`/decode-and-code:<skill> <resposta>`) — o próprio modelo chegou a essa orientação no setup
  (`logs/02c-setup-migracao.jsonl`) —, ou o setup propõe a regra de permissão do `dc.py` no
  `settings.local.json` uma vez por projeto.

### E-05 — O decode de um rascunho do formato 1 perde restrições, e o plano novo passa a depender de um commit (grave)

- **Etapa:** 4 e 5.
- **Evidência:** a proposta (`logs/04b-decode.jsonl`) trocou 662 linhas por 199 e deixou de fora a
  L-15 (alcance da aprovação no plugin Builder, restrição do plano) e o Oráculo inteiro. Só voltaram
  pela recusa do mantenedor (`logs/04c-decode.jsonl`). O plano aprovado diz "As decisões 1 a 8 e as
  lacunas L-01 a L-15 do rascunho `030e36b` valem como estão e não se repetem aqui", e cada unidade
  cita `git show 030e36b:…`. O modelo teve de perguntar como retomar o rascunho
  (`logs/04a-decode.jsonl`, texto final).
- **Causa provável:** o codex não diz o que o decode faz com um rascunho do formato 1 que já está no
  `_inbox` e já foi além da proposta: *Plano anterior ao redesign* (`rules.md:229-240`) cobre revisão,
  derive e code, e o `decode/SKILL.md` não o menciona.
- **Correção sugerida:** uma regra no codex para esse caso: as decisões, as lacunas decididas e o
  oráculo do rascunho passam para a proposta (ou para um anexo no `_inbox`), e nada do plano aprovado
  fica só no histórico do git.

### E-06 — `setup-escopo --aplicar` sobrescreve um `false` deliberado (menor)

- **Etapa:** 2.
- **Evidência:** com `"decode-and-code@future-ride-today": false` no `settings.json`, a saída foi
  `habilitado: false`, e o modelo disse que o plugin "não está em enabledPlugins". `--aplicar` grava
  `true`, o que na cópia reativaria a 2.0 instalada ao lado da 3.0. Respondido "não".
- **Causa provável:** `escopo.py:50` não distingue chave ausente de `false`; `escopo.py:66` grava
  `True` por cima.
- **Correção sugerida:** três estados na saída (`ausente`, `false`, `true`), e `--aplicar` só
  acrescenta chave ausente, como a skill promete.

### E-07 — `criar-principio` grava depois de `## Fonte` e sem o formato dos outros (menor)

- **Etapa:** 3.
- **Evidência:** `amflow/.claude/rules/principles.md`, fim do arquivo (tag `etapa-03`): a seção
  `## instalado-e-revisado` entrou depois de `## Fonte`, só com *Enunciado* e *Teste*. O modelo abriu
  H-13 sobre isso.
- **Causa provável:** `criar-principio` acrescenta ao fim do arquivo.
- **Correção sugerida:** inserir antes de `## Fonte` quando existir.

### E-08 — O `descobrir` chama de princípio toda rule sem `paths:` (menor)

- **Etapa:** 3.
- **Evidência:** *Já existe* listou 6 princípios (`code-vs-prose`, `execution-protocol`,
  `grounding-and-verification`, `principles`, `tools`, `voice-and-language`); só `principles.md` passa
  no teste da equipe competente. O modelo corrigiu na conversa (`logs/03b-setup.jsonl`).
- **Correção sugerida:** listar como "rules que carregam sempre", sem classificar.

### E-09 — `code aprovar` pede o nome do git sem poder lê-lo (menor)

- **Etapa:** 9.
- **Evidência:** `git config user.name` negado duas vezes; o modelo usou o nome do snapshot da sessão
  (`logs/09-aprovar.jsonl`).
- **Causa provável:** `code/SKILL.md` manda passar `--por "<nome dele no git>"`, e o `allowed-tools`
  só libera o `dc.py`.
- **Correção sugerida:** `aprovar-entrega` com `--por` opcional, caindo em `huddle.usuario`, que já
  lê o git.

### E-10 — A skill `code` manda usar Glob, que a sessão não tem (menor)

- **Etapa:** 8.
- **Evidência:** "No such tool available: Glob" no fork (`logs/08-code-01.jsonl`); o modelo caiu
  para `find`.
- **Causa provável:** `code/SKILL.md` ("ache o arquivo com Glob") e o `allowed-tools` de todas as
  skills citam `Glob`, ausente no Claude Code 2.1.330 desta máquina.
- **Correção sugerida:** o `dc.py` resolve `NNNN-nn` para o caminho, e a skill não depende de
  ferramenta de busca.

### E-11 — O modelo mudou um guardrail aprovado sem pedir novo sim (menor)

- **Etapa:** 3.
- **Evidência:** o guardrail existente do AmFlow `escrita-arquivo-env` (`(?i)\.env\b`) negou a
  escrita do JSON do guardrail novo, porque o texto tinha `process.env`. O modelo trocou detector,
  exemplo e mensagem e gravou, avisando depois e abrindo H-12 (`logs/03e-setup.jsonl`). Desvia de
  "grave só depois do Aprovar" (`setup/SKILL.md`, etapas 5 e 6). O detector antigo é do AmFlow, e o
  hook se comporta igual ao do 2.0 (diff só no registro do bloqueio).
- **Correção sugerida:** na skill, "proposta alterada volta à pessoa antes de gravar", explícito para
  o caso de bloqueio por guardrail.

## 3. Oportunidades de melhoria

| # | Oportunidade | Evidência | Custo |
|---|---|---|---|
| O-01 | `setup-registrar` e `foundation-recurso` aceitam lista | 03d: 68 turnos, 183 s, 35 Bash e 32 Write para 13 recursos; 03c: 3 recusas tentando gerar os JSON por script | Baixo |
| O-02 | Toda skill lê as seções do codex num comando só, `codex "A" "B" …`, como o `code` já faz | Loop `for` negado em 04a, 05a e 06a; compostos negados em quase toda etapa (31 recusas no total) | Baixo |
| O-03 | `huddle-fecho` imprime os tipos aceitos | O modelo sondou `huddle-abrir tipo-invalido` em 04d, 05a e 06a para descobrir o vocabulário | Baixo |
| O-04 | `migrar` lista, como informação, as citações à norma e às skills do 2.0 em `CLAUDE.md`/`AGENTS.md` | O `.claude/CLAUDE.md` do AmFlow cita `modelo-dev-units.md` três vezes e `/decode-and-code:intake` e `:implement`, que não existem no 3.0; o setup não edita o arquivo, e o aviso dependeu do modelo | Baixo |
| O-05 | `huddle-migrar` com `--dry-run`, ou o `explicar` descreve o efeito | O modelo propôs a migração do huddle dizendo "não sei o que acontece com H-01 a H-10" (03b) | Baixo |
| O-06 | O `lint-plano`/`lint-unidade` avisa frontmatter do projeto ausente, ou a skill preserva os campos existentes | Proposta, plano e unidades nasceram só com os campos do DC; os campos do padrão do AmFlow caíram. `setup.md` e `foundation.md` com `project: amflow`, `author: ""`, `created: ""` | Médio |
| O-07 | O derive confere "unidade remove ou muda algo que outro arquivo lê" por busca | Nenhum dos dois planos antecipou L-25, L-27, L-29 e L-30 do original, todas achadas depois por `grep` | Médio |
| O-08 | O huddle migrado ganha `last_huddle` da migração | Primeira sessão depois do setup: "último huddle há 97 dias" (conta desde `created` 2026-08-22) | Baixo |

## 4. Métricas por etapa

Custo por chamada: o `total_cost_usd` do `result` é cumulativo na sessão retomada por `--resume`; a
tabela usa a diferença. `num_turns` 0 nas chamadas do `code`: o trabalho roda no fork.

| Etapa | Chamadas | Duração (s) | Turnos | Custo (USD) | Recusas | Modelo |
|---|---|---|---|---|---|---|
| 0 Preparar | — | — | — | — | — | — |
| 1 Primeira sessão | 1 | 19 | 5 | 0,29 | 2 | sonnet |
| 2 Migração | 3 | 48 | 13 | 0,83 | 2 | opus |
| 3 Setup | 5 | 479 | 138 | 4,42 | 7 | opus |
| 4 Decode (P1, recusa, P2) | 4 | 193 | 39 | 2,02 | 1 | opus |
| 5 Review-plan (P3, P4) | 2 | 259 | 47 | 2,88 | 6 | opus + haiku |
| 6 Derive (P5) | 2 | 485 | 72 | 4,29 | 3 | opus |
| 7 Gate entre unidades | 1 | 19 | fork | 0,28 | 1 | sonnet |
| 8 Code parcial da 0028-01 | 1 | 78 | fork | 0,52 | 7 | sonnet |
| 9 Aprovação P7 | 1 | 10 | fork | 0,19 | 2 | sonnet |
| **Total** | **20** | **1592** | **314** | **15,72** | **31** | |

Tabela por chamada: `tools/metricas.py` no ambiente.

**Conferência independente** (rodada pela sessão do teste, fora do modelo):

| Comando | Resultado |
|---|---|
| `verificar` e `validar` do staging | limpos; zip com 61 arquivos, sem `reference/`, `version` 3.0.0 |
| `migrar` antes / depois | norma, huddle e 6 planos / só os 6 planos |
| `lint-plano` do 0028 aprovado | ok |
| `lint-unidade` das 11 unidades | ok |
| `entrada-code` 01 / 02 / 03 | ok / recusa / recusa (E-02) |
| `verificar --dry-run` 01 e 04 | `spec`, "teste declarado não existe no disco" |
| Guardrail novo pelo hook | barra `process["env"]` em `hub/app`; `process.env` já é barrado pelo guardrail antigo do AmFlow |
| `./scripts/test-ts.sh` na cópia | 4 de 4 verdes depois do `npm ci` (A-1) |

**Por etapa, o que o teste validou:**

- **1:** só a 3.0.0 carrega (`decode-and-code@inline`); as 8 skills e os hooks presentes.
- **2:** a norma copiada foi apagada com o sim; o huddle único foi para `huddle/bortoli.md` com
  H-01 a H-10 preservadas; os 6 planos só foram listados. O aviso não some (E-01) e o corpo do huddle
  ficou antigo (E-03).
- **3:** setup até a etapa 7 em `-p`, sem a ferramenta de perguntas: perfil, 1 princípio novo, 6
  regras como existentes, foundation com 13 recursos, 1 guideline (`interface-hub`), 1 guardrail;
  `setup-concluir` gravou `completed_at`.
- **4:** decode sem fork, tipo e objetivo confirmados antes de escrever, Gates A e B, uma recusa
  real e a aprovação P2.
- **5:** plano `format_version: 2` na raiz dos planos, número 0028, `_planos.md` "em
  desenvolvimento", links do `_inbox` corrigidos pelo `aprovar`.
- **6:** 11 unidades com os 8 blocos da Definition of Ready, `## Aprovação das unidades`, backlog e
  handoff.
- **7:** o gate recusa a 02 antes da 01.
- **8:** o fork Sonnet passou o gate, leu a unidade, rodou `normas` e parou antes de escrever,
  propondo a lacuna L-16 (pré-condições de staging e MCP ausentes). Nada escrito.
- **9:** `aprovar-entrega` sai `2`: "a entrega só se aprova com o teste verde".

## 5. Comparação com o gabarito 0028

Gabarito: o plano aprovado em `8be45e5` e o plano final em `origin/dev` (`gabarito-0028-*.md` no
ambiente).

| Aspecto | Original (DC 2.0) | Refeito (DC 3.0) |
|---|---|---|
| Porte | grande, 11 unidades | grande, 11 unidades, mesma divisão e mesmos nomes |
| Tipos | 01, 02, 03 `norma`; 04-11 `dev` | 01, 02 `plan` com teste declarado; 03 `rule`; 04-11 `dev` |
| Histórias | não havia | 4 histórias com critério, uma por papel, mais o teste do plano inteiro (P8) |
| Decisões | 1 a 8, L-01 a L-15, "a fixar na 02" | as mesmas, por referência ao `030e36b`, mais R1-R12 fechando o que o original deixava "a fixar" |
| Ordem | 01 e 03 em paralelo | a mesma no texto, mas o gate a impede (E-02) |
| Tamanho | plano 697 linhas + 11 unidades (1366 linhas no commit) | plano 379 linhas + 11 unidades + handoff (1570 linhas) |

**Lacunas que a execução original só achou depois (L-16 a L-32):**

| Lacuna original | O plano novo antecipou? |
|---|---|
| L-16 — os scripts nascem em `scripts/` e descem por `vendor.py` | **Sim** (R6) |
| L-17 — guarda dos scripts dos plugins | Em parte: teste de imports na 08 |
| L-18 — fonte única dos limites sem dono | Em parte: `hub/lib/package-limits.json` fixado no derive |
| L-19 — 06 e 07 precisam de migration e não declaram | **Sim**: as duas declaram migration em *Arquivos* |
| L-20 — medições que a especificação assume | Não se aplica (nasce da 02) |
| L-21 — Python no Windows | Em parte: R7 decide o tratamento antes |
| L-22 — ESLint não acusa import relativo | Não |
| L-23 — segredo da limpeza e arquivo de limites | Em parte: segredo em `env.schema.ts` declarado na 05 |
| L-24 — sessão presa ao recurso sem teste | Não |
| L-25, L-27, L-29, L-30 — a unidade muda algo que outro teste ou rota lê | Não (O-07) |
| L-26 — teto do lint desce no mesmo commit | Não |
| L-28 — `agent-description.md` fora da L-15 | Não |
| L-31 — 25 arquivos, não 23 | Não (só medível em staging) |
| L-32 — apagamento no cancelamento da M10 | Não |

**Conclusão:** o DC 3.0 planeja **igual ou um pouco melhor** que o 2.0 neste caso. Igual na divisão,
melhor em histórias, decisões fechadas e duas lacunas inteiras antecipadas (L-16, L-19), além de três
em parte. Pior em dois pontos de forma: a ordem do handoff que o gate não aceita (E-02) e a
dependência do histórico do git (E-05). As lacunas que nem o original previu, achadas na revisão de
entrega, continuam fora do alcance do derive.

## 6. Limites do teste

- **Workspace não confiado.** Toda chamada avisou "Ignoring 17 permissions.allow entries": as
  permissões do `.claude/settings.json` do AmFlow não valeram. O `~/.claude.json` não foi tocado
  (salvaguarda). Parte das 31 recusas não aconteceria no AmFlow real.
- **Modo `-p`.** Sem a ferramenta de perguntas (A-3 não pedida): o setup perguntou em texto e juntou
  perguntas por etapa. Sem pedido de permissão interativo: o que pediria aprovação foi negado.
- **Caminho do plugin por processo.** `--plugin-dir <zip>` extrai o plugin num diretório novo a cada
  processo; numa resposta por `--resume`, o modelo repetiu o caminho do turno anterior
  (`logs/02b-setup-migracao.jsonl`). Com o plugin instalado, o caminho é estável.
- **Sem staging nem MCP.** `amflow-builder` e `amflow-worker` falharam com 402; sem Docker liberado
  nem Supabase. A 0028-01 não é executável aqui.
- **Caminho verde do code e do P7 não exercido.** O gate só libera a 01, que depende de staging; o
  teste vermelho, o `verificar` com runner `.ts`, o fecho e a projeção depois da aprovação não
  rodaram. O runner `.ts` do AmFlow foi conferido à parte (4 de 4 verdes).
- **AmFlowPlugins ausente.** A revisão e o derive não leram a prosa dos plugins e declararam.
- **Ambiente global da máquina.** O `CLAUDE.md` global, 20 plugins e hooks de outros plugins
  carregam em toda sessão; a sessão sem skill rodou em Sonnet por padrão.
- **Uma rodada.** Cada etapa rodou uma vez; não há variância medida.

## 7. Contornos

- **No pacote: nenhum.** O zip testado é o construído do `dev` (`7325ba1`), sha256
  `54ea35d05b5d00bf4e6f74908865cd4dea744d9c55807ef0608a02a8274d6cf2`, com só a `version` trocada no
  staging.
- **Na orquestração:** a partir da etapa 2c, cada resposta da pessoa foi enviada como
  `/decode-and-code:<skill> Continuação desta conversa. <resposta>`, com `--resume`, para recarregar a
  liberação do `allowed-tools` (E-04).
- **Na cópia:** `enabledPlugins` do DC 2.0 em `false` (etapa 0) e a recusa ao `setup-escopo --aplicar`
  para mantê-lo assim (E-06).
