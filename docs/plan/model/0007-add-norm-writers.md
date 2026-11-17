---
# about
name: add-norm-writers
type: plan
project: DecodeAndCode
description: Guideline e guardrail passam a ser gravados por comando, com frontmatter que o Claude Code consegue ler e regra que só entra provada pelo par proibido/permitido — base da promoção no huddle e do setup
tags: [decode-and-code, guideline, guardrail, normas, dc-py]

# alvo
plan_id: "0007"
plan_size: médio
core: model
module: add-norm-writers
block: ""

# history
author: Claude
created: 2026-11-10
status: done
version: 1.0.0
updated: "2026-11-15"
approved_by: Bortoli
approved_at: 2026-11-15

# system
scope: project
auto_load: false
dependencies: []
---

# Guideline e guardrail gravados por comando

## Objetivo

**Clarificar.** Hoje toda guideline e todo guardrail são escritos à mão, sem nada que garanta duas
falhas que não aparecem até alguém tropeçar nelas: um frontmatter que o lint aprova e o Claude Code
não consegue ler vira rule carregada sempre, sem aviso, e uma regra malformada no `guardrails.json`
desliga ela mesma e todas as seguintes. Métrica: toda rule e todo guardrail criados pelos comandos
passam nos lints, e todo guardrail novo nega o caso proibido e libera o permitido declarados.
Beneficiários: a promoção de item no huddle (`wire-huddle-cycle`) e o setup (`onboard-new-project`),
que dependem destes comandos, e quem cria norma à mão hoje.

**Evitar.**

| Alternativa | Por que não basta |
|---|---|
| Os guias `create-guideline.md` e `create-guardrail.md` | É o estado atual: passos manuais, e `docs/` não viaja no pacote |
| `empacotar.materializar` | Copia uma guideline existente, não cria; e é script de desenvolvimento, fora do pacote |
| O modelo escrever o arquivo com Write | Funciona hoje e é exatamente o que produz os dois defeitos abaixo |

**Reduzir.** Duas funções de escrita, um lint de `guardrails.json` e o registro no `registry.json`,
expostos pelo `dc.py`. Nada de interface: quem conversa com o humano são as skills dos dois planos
seguintes.

## Gates

| Gate | Resposta |
|---|---|
| **A — necessidade real** | Sim, com a ressalva abaixo. Medido em 2026-11-15: `paths: [**/*.md]` passa em `lint_rule` e `lint_guideline` e não é YAML válido (Ruby Psych: "scanning an alias") — pela [doc](https://code.claude.com/docs/en/memory), o Claude Code então "loads the rule as if it had no `paths`"; `["src/**/*.{ts,tsx}", "docs/**/*.md"]` também passa, com a primeira entrada cortada na vírgula. Um erro numa regra do `guardrails.json` libera a chamada e pula as regras seguintes (`guardrail.py:51-56`). Nenhuma função cria guideline, registra no `registry.json` ou escreve guardrail (`registry.py` expõe só `listar`, `ligar`, `desligar`). **Ressalva:** o defeito é latente — `auditar_arvore` devolve `[]` neste repositório e no AmFlow, e nenhuma rule quebrada existe hoje. A maior parte do valor vem dos dois planos seguintes, que dependem destes comandos (`D-01`); aprovado sozinho, sem eles, o plano previne um defeito que ainda não aconteceu |
| **B — mínimo viável** | Cortado: corrigir o lint de `paths` para a semântica da doc (`L-01`); escrever princípio, que entra por plano de tipo `norma`; qualquer interface ou pergunta ao humano |

## Solução

| Quem | O quê |
|---|---|
| **`rules.criar_guideline`** | Grava `.claude/rules/<nome>.md` com frontmatter seguro, valida antes de mover para o lugar, e registra no `registry.json` |
| **`registry.registrar`** | Cria ou atualiza a entrada de uma guideline que já está no disco, reaproveitando `_reprojetar` |
| **`guardrail.lint_arquivo`** | Recusa `guardrails.json` que desligaria regras em silêncio |
| **`guardrail.adicionar`** | Só grava a regra que, avaliada sozinha, nega o proibido e libera o permitido |
| **`dc.py`** | `criar-guideline`, `adicionar-guardrail` e `lint-guardrails` — nomes planos em kebab-case, como os subcomandos existentes (`D-06`) —, com a entrada em JSON pelo stdin, no padrão do `handoff` (`dc.py:166-173`), porque regex e markdown não sobrevivem às aspas do argv |

Todas as funções novas recebem a raiz do projeto como parâmetro explícito; o `dc.py` passa
`lib.repo_root()`, como os outros subcomandos (`D-07`).

## Tarefas

- [x] **T1 — `rules.criar_guideline(raiz, nome, descricao, paths, corpo) -> Path`.** O nome casa
      `^[a-z0-9]+(-[a-z0-9]+)*$` — kebab-case ASCII; não se usa o `nomenclatura`, que é de plano e
      exige de 2 a 5 tokens — e é recusado se já existir em `rules/` ou em `rules-off/`. `name` e
      `description` são escritos entre aspas duplas com escape JSON (`json.dumps`), que é YAML válido.
      Cada entrada de `paths` vai entre aspas duplas, e o padrão é recusado se tiver `{`, `,` ou `/`
      inicial, se não começar por diretório ou por `**/`, ou se terminar em `/**` — a forma de
      diretório inteiro é `dir/**/*`, a que a [doc](https://code.claude.com/docs/en/memory)
      exemplifica; no Python 3.10, `Path.glob("dir/**")` casa o próprio diretório e o lint aprovaria
      sem nenhum arquivo. É o subconjunto em que lint e Claude Code concordam (`D-02`). Grava num
      arquivo temporário, roda `lint_guideline` contra `raiz` e só então move para `rules/`;
      reprovado, nada fica no disco. `lint_guideline` ganha um parâmetro opcional `raiz`, com o padrão
      atual (`lib.repo_root()`), para o casamento de `paths`. **Caminho que ainda não existe**
      (`D-08`): com `aguardando=True`, `criar_guideline` grava também `paths_pending: true` no
      frontmatter — campo que o Claude Code ignora, como todo campo que não é `paths` —, e
      `lint_guideline` passa a aceitar `paths` sem casamento no disco quando esse campo está
      presente; as demais checagens continuam. Casos de teste: `description` com `: ` e `#`;
      `**/*.tsx`; chave recusada; `docs/**` recusado e `docs/**/*` aceito; nome existente em
      `rules-off/`; nome com acento ou maiúscula; reprovação sem resíduo; caminho inexistente recusado
      sem `aguardando` e aceito com ele.
- [x] **T2 — `registry.registrar(raiz, nome)`**, chamado por T1 depois da gravação: reaproveita
      `_reprojetar(raiz / ".claude" / "rules", nome)`. `_e_guideline` passa a tratar `.md` sem
      frontmatter como "não é guideline", em vez de levantar. O motivo não é que o arquivo esteja
      certo — `lint_rule` continua recusando rule sem frontmatter, e `auditar_arvore` continua
      apontando —, e sim que hoje um único `.md` assim faz `_reprojetar` levantar e trava o registro de
      **toda** guideline do diretório, o que acontece num projeto de terceiro com rules escritas à mão.
      Teste com um `.md` sem frontmatter ao lado de uma guideline. **Efeito declarado:** num projeto com
      guidelines e sem `registry.json` — o AmFlow hoje —, o primeiro `registrar` cria o registro com
      todas elas, datadas do dia (`registry.py:96-114`); o registro é projeção, não fonte.
- [x] **T3 — `guardrail.lint_arquivo(caminho) -> list[str]`**: JSON válido, `regras` como lista,
      as quatro chaves com string não vazia, `ferramenta` e `detector` que compilam, `nome` único.
      Lista vazia quando são. Testes para cada recusa, e contra o `guardrails.json` deste repositório.
- [x] **T4 — `guardrail.adicionar(raiz, regra, proibido, permitido) -> Path`.** Avalia a regra
      candidata sozinha, num arquivo temporário: `decidir` precisa negar `proibido` com a própria
      regra (`regra == nome`) e liberar `permitido`. Só então acrescenta a regra ao
      `.claude/guardrails.json` do projeto, criando o arquivo se faltar, e roda `lint_arquivo` no
      resultado. Recusa `nome` repetido. `proibido` e `permitido` têm a forma do payload do hook
      (`tool_name`, `tool_input`).
- [x] **T5 — `dc.py criar-guideline`, `dc.py adicionar-guardrail` e `dc.py lint-guardrails`.** Os
      dois primeiros leem JSON do stdin — `{nome, descricao, paths, corpo}` e
      `{regra: {nome, ferramenta, detector, mensagem}, proibido: {tool_name, tool_input}, permitido: {…}}`
      — e recusam stdin vazio, como o `handoff`. Todos passam `lib.repo_root()` como `raiz`. Os três
      entram em `SUBCOMANDOS` (`tests/test_dc.py:44-56`), com um caso cada.
- [x] **T6 — documentação.** Norma, *Camada normativa*: os comandos de escrita, citados uma vez.
      `create-guideline.md` e `create-guardrail.md`: os passos de escrita e registro passam a ser os
      comandos; *Quando criar* não muda aqui (o primeiro uso é do `onboard-new-project`).
- [x] **T7 — versão**: o número é decisão humana no release; bump em `.claude/plugin.json` e
      `.claude-plugin/marketplace.json`.

## Oráculo

| Alvo | Como se sabe que funcionou |
|---|---|
| Frontmatter | O arquivo gravado por T1 passa em `lint_guideline`, e o valor de cada campo do frontmatter (`name`, `description`, `paths` e, quando houver, `paths_pending`) passa em `json.loads` — todo JSON é YAML válido, e a stdlib não tem parser de YAML. Controle que precisa falhar no mesmo teste: o frontmatter com `paths: [**/*.md]` sem aspas |
| Sem resíduo | Toda reprovação de T1 deixa `rules/` e `registry.json` como estavam |
| Registro | Depois de T1, `registry.listar()` traz o nome como `ligada`, sem `divergente`; com um `.md` sem frontmatter no mesmo diretório, também |
| Guardrail | Avaliada sozinha, a regra nova nega o `proibido` com `regra == nome` e libera o `permitido`; uma regra cujo `detector` não casa o `proibido` é recusada, mesmo que outra regra do arquivo já o negue (`D-03`). Depois de T4, `decidir` sobre o `guardrails.json` gravado continua negando o `proibido` — pela regra nova ou por uma anterior, já que vale a primeira que casa |
| Lint | `lint_arquivo` recusa regex que não compila, chave faltando e nome repetido; aprova o arquivo deste repositório |

## Decisões

| # | Decisão | Estado |
|---|---|---|
| D-01 | **Três planos, nesta ordem:** este, `wire-huddle-cycle` (que usa estes comandos para promover item) e `onboard-new-project` | Decidida pelo humano em 2026-11-10 |
| D-02 | **O gerador escreve `paths` só no subconjunto em que lint e Claude Code concordam**, em vez de corrigir o lint agora | Decidida pelo humano em 2026-11-15 |
| D-03 | **A regra candidata é avaliada sozinha.** Avaliada junto das existentes, uma regra anterior que já negasse o caso faria o teste passar sem a regra nova casar nada | Decidida pelo humano em 2026-11-15 |
| D-04 | **Entrada pelo stdin em JSON**, como o `handoff` já faz | Decidida pelo humano em 2026-11-15 |
| D-05 | **Um plano, não dois.** A parte de guideline (T1, T2) e a de guardrail (T3, T4) passam sozinhas no teste de independência. Ficam juntas porque os dois consumidores — a promoção no huddle e o setup — usam as duas, a superfície no `dc.py` é a mesma, e separar criaria dois planos pequenos com a mesma dependência a jusante (norma, *O que a avaliação não faz*: o plano registra o porquê) | Decidida pelo humano em 2026-11-15 |
| D-06 | **Subcomandos planos em kebab-case** (`criar-guideline`, `adicionar-guardrail`, `lint-guardrails`), como todos os do `dc.py` hoje; o teste de drift das skills lê um token só depois de `dc.py"` (`tests/test_dc.py:197-202`). O `wire-huddle-cycle` segue a mesma forma | Decidida pelo humano em 2026-11-15 |
| D-07 | **A raiz do projeto é parâmetro explícito** das funções novas, e o `dc.py` a resolve por `lib.repo_root()`, como os outros subcomandos | Decidida pelo humano em 2026-11-15 |
| D-08 | **Guideline para caminho que ainda não existe é gravada já**, marcada com `paths_pending: true` no próprio frontmatter, e vale desde o primeiro arquivo criado no escopo. A marca fica na rule, não no `setup.md` do `onboard-new-project`, para este plano não depender daquele | Decidida pelo humano em 2026-11-15 |

## Lacunas

| # | Lacuna | Por que fica registrada |
|---|---|---|
| L-01 | **O lint de `paths` diverge da doc oficial** | Divide padrões com chaves na vírgula interna, trata `*.md` como só da raiz e recusa lista YAML em bloco; e a norma diz que o modelo lê a `description` da rule, o que a [doc](https://code.claude.com/docs/en/memory) nega ("`paths` is the only field Claude Code reads"). Anterior a este plano; `D-02` só evita o problema na escrita |
| L-02 | **"Invariante já respeitado" não é verificável por script** | O guia de guardrail exige que o trabalho já respeite o invariante. O par proibido/permitido prova o detector, não o histórico do projeto |
| L-03 | **O projeto é resolvido por `lib.repo_root()`** | Herda a `L-03` do `0006`: com o pacote dentro de um checkout, `lib.repo_root()` acha o checkout primeiro |
| L-04 | **Guideline para caminho que ainda não existe é recusada** | `lint_guideline` exige que `paths` case ao menos um arquivo no disco. Num projeto novo, uma guideline para `components/**/*.tsx` seria recusada antes da pasta existir — o que atinge diretamente o setup do `onboard-new-project`. **Fechada em 2026-11-15** pela `D-08` |
| L-05 | **Glob errado com `paths_pending` não é pego** | Com a marca, o lint deixa de exigir casamento, então um erro de digitação no caminho só aparece quando alguém nota que a rule nunca carrega. A marca também não sai sozinha depois que a pasta existe |

## Backlog

<!-- backlog:start -->
- [x] **T1 — `rules.criar_guideline(raiz, nome, descricao, paths, corpo) -> Path`.** O nome casa
- [x] **T2 — `registry.registrar(raiz, nome)`**, chamado por T1 depois da gravação: reaproveita
- [x] **T3 — `guardrail.lint_arquivo(caminho) -> list[str]`**: JSON válido, `regras` como lista,
- [x] **T4 — `guardrail.adicionar(raiz, regra, proibido, permitido) -> Path`.** Avalia a regra
- [x] **T5 — `dc.py criar-guideline`, `dc.py adicionar-guardrail` e `dc.py lint-guardrails`.** Os
- [x] **T6 — documentação.** Norma, *Camada normativa*: os comandos de escrita, citados uma vez.
- [x] **T7 — versão**: o número é decisão humana no release; bump em `.claude/plugin.json` e

7 de 7 tarefas concluídas · atualizado em 2026-11-15
<!-- backlog:end -->

## Fonte

- [`modelo-dev-units.md`](../system/modelo-dev-units.md) — seção *Camada normativa*
- [`create-guideline.md`](../../recursos/create-guideline.md) e
  [`create-guardrail.md`](../../recursos/create-guardrail.md) — os passos manuais que viram comando
- `.claude/skills/decode-and-code/scripts/rules.py`, `registry.py`, `guardrail.py`, `dc.py`
- Documentação oficial do Claude Code, lida em 2026-11-10 e conferida em 2026-11-15 (semântica de
  `paths`): [memory](https://code.claude.com/docs/en/memory), [hooks](https://code.claude.com/docs/en/hooks)
