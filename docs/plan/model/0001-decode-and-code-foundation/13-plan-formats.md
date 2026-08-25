---
# about
name: plan-formats
type: unit
project: DecodeAndCode
description: Cada porte passa a ter um formato próprio e verificável, e a unidade de conteúdo normativo ganha o oráculo que faltava — estrutura válida somada à aprovação declarada
tags: [decode-and-code, plano, porte, unit-type, l-01, l-22]

# alvo
core: model
module: decode-and-code
block: ""
owner: model
unit_id: 0001-13
unit_type: dev

# verificação
state: verified
test: .claude/skills/decode-and-code/scripts/tests/test_lint_plano.py
verified_at: 2026-08-25

# history
author: Bortoli
created: 2026-08-25
status: draft
version: 1.0.0
updated: ""

# system
scope: project
auto_load: false
dependencies: []
---

# 0001-13 — plan-formats

**Responsabilidade:** dizer o que cada porte dispensa, e tornar isso verificável — hoje existe **um**
formato de plano e ele cobra de uma correção de oito linhas a mesma estrutura que cobra deste plano.
No mesmo movimento, fechar a `L-01`: um terceiro valor de `unit_type` para a unidade cujo entregável
é conteúdo normativo.

## Contrato

| Campo | Detalhe |
|---|---|
| **Entrada** | `lint_plano.lint(plano)` — caminho de um plano, já aprovado ou ainda no `_inbox` |
| **Saída** | Lista de problemas, vazia quando o plano está no formato do porte que declara |
| **Auth** | — |
| **Efeito** | Nenhum — `lint_plano` só lê, como todos os lints do repositório |
| **Erro** | Frontmatter ausente ou `plan_size` fora do vocabulário entra como problema na lista, nunca levanta — quem levanta é `scaffold.aprovar` (`0001-12`), que é o gate |

**O que cada porte carrega, e é isto que `lint_plano` verifica:**

| Porte | Decomposição | `## Independência` | Região de backlog |
|---|---|---|---|
| `pequeno` | nenhuma | **recusada** | **recusada** |
| `médio` | `## Tarefas` — lista de caixas | dispensada | exigida |
| `grande` | `## Escopo` — tabela numerada | exigida | exigida |

> **No pequeno os dois blocos são recusados, não apenas dispensados.** Região de backlog é promessa
> de projeção: se nenhum script escreve ali, ela mente para sempre — é a `L-22` de novo, num lugar
> novo. E `## Independência` num plano sem decomposição responde a uma pergunta que ninguém fez.

**O terceiro `unit_type`, e o oráculo que ele traz:**

| Tipo | Entrega | Oráculo | `test:` |
|---|---|---|---|
| `dev` | Código | O teste declarado passa | obrigatório |
| `plan` | Um plano | O plano consta em `_planos.md` | inalterado nesta unidade |
| `norma` | Markdown normativo | `lint_unidade` limpo **somado** a `approved_by`/`approved_at` preenchidos | **vazio** |

`verified_at` de uma unidade `norma` recebe o valor de `approved_at`, não a data de hoje: o oráculo é
a aprovação do humano, e rodar o gate de novo amanhã não pode mover a data de um fato que não mudou.

> **Isto não transforma julgamento em oráculo, e a `L-01` continua aberta no que importa.** O script
> passa a exigir que a aprovação **exista e esteja registrada**; ele continua sem saber se a prosa
> presta. O que muda é que uma etapa que hoje é implícita — alguém leu e aceitou — deixa de ser
> indistinguível de nunca ter acontecido. É o mesmo padrão do `plan_size`: recusa-se a ausência.

**A linha órfã sai (`L-22`).** As unidades trazem no corpo *"Último resultado: não executado."*
enquanto o frontmatter delas diz `verified` com data. Nenhum script escreve essa linha e a norma não
a menciona — ela sobreviveu por cópia. Sai do formato e sai das unidades `01` a `11`; `lint_unidade`
passa a recusá-la, para que não volte pela mesma porta. As unidades `12` a `15` já nasceram sem ela.

## Sequência

1. Escrever `lint_plano.py` com `lint(plano)`, ramificando pela tabela de portes acima e devolvendo lista no padrão dos outros lints do repositório.
2. Estender `lint_unidade.py`: `norma` entra em `UNIT_TYPES_VALIDOS`; `test:` passa a ser exigido em `dev` e exigido **vazio** em `norma`; `norma` sem `approved_by`/`approved_at` é problema; e a linha `Último resultado` no corpo passa a ser recusada.
3. Ramificar `verificacao.verificar` por `unit_type`: `norma` fecha por lint limpo somado à aprovação declarada, com `verified_at` recebendo `approved_at`, e **sem executar comando nenhum**.
4. Escrever na norma: *Formato do plano* ganha a tabela do que cada porte carrega; *Tipo de unidade* ganha `norma` e seu oráculo; e *Formato do arquivo de unidade* passa a dizer que `## Verificação` carrega o comando e mais nada.
5. Retirar a linha `Último resultado` das unidades `01` a `11` — só a linha, nada mais dos arquivos.
6. Acrescentar a `fixtures.py` os construtores que faltam: `plano()` nos três portes, e `unidade()` com `unit_type: norma`.
7. Escrever `tests/test_lint_plano.py` cobrindo o critério de aceite — os três portes válidos, cada recusa isolada, e o ciclo do `unit_type: norma` em `verificar`.
8. Rodar o gate e relatar.

## Arquivos

| Caminho | O que muda |
|---|---|
| `.claude/skills/decode-and-code/scripts/lint_plano.py` | **novo** — o formato por porte |
| `.claude/skills/decode-and-code/scripts/lint_unidade.py` | `norma`, `test:` por tipo, aprovação exigida, e a recusa da linha órfã |
| `.claude/skills/decode-and-code/scripts/verificacao.py` | `verificar` ramifica por `unit_type` |
| `docs/plan/system/modelo-dev-units.md` | *Formato do plano*, *Tipo de unidade* e *Formato do arquivo de unidade* |
| `docs/plan/model/0001-decode-and-code-foundation/01-config-and-paths.md` … `11-activation-audit.md` | a linha `Último resultado` sai das onze |
| `.claude/skills/decode-and-code/scripts/tests/fixtures.py` | `plano()` por porte, `unidade()` com `unit_type: norma` |
| `.claude/skills/decode-and-code/scripts/tests/test_lint_plano.py` | **novo** — o teste declarado |

## Dependências

A `0001-12`, por duas razões: o vocabulário de `plan_size` que esta unidade ramifica, e os campos
`approved_by`/`approved_at`, que nascem lá e são reusados aqui como oráculo do `unit_type: norma`.

## Normas aplicáveis

| Norma | Onde |
|---|---|
| *Formato do plano*, *Tipo de unidade* e *Formato do arquivo de unidade* | [`modelo-dev-units.md`](../../system/modelo-dev-units.md) |
| `L-01` — unidade de conteúdo normativo não tem oráculo natural | [`0001-decode-and-code-foundation.md`](0001-decode-and-code-foundation.md), seção *Lacunas* |
| `L-22` — a linha órfã que sempre mente | [`0001-decode-and-code-foundation.md`](0001-decode-and-code-foundation.md), seção *Lacunas* |
| Os campos declarados pelo humano, e por que o gate recusa ausência | [`12-plan-size-field.md`](12-plan-size-field.md) |
| Código, não instrução em markdown | `.claude/CLAUDE.md` |

## Critério de aceite

`lint_plano.lint` devolve `[]` para um plano bem formado em cada um dos três portes, e **recusa
isoladamente** cada linha da tabela de portes: pequeno com `## Independência`, pequeno com região de
backlog, médio sem `## Tarefas`, médio sem região de backlog, grande sem `## Escopo`, grande sem
`## Independência`, grande sem região de backlog. `plan_size` ausente ou fora do vocabulário entra
como problema na lista — `lint_plano` **não levanta**.

`lint_plano.lint` devolve `[]` contra o plano real `0001` deste repositório, que é `grande`.

`lint_unidade` aceita `unit_type: norma`, recusa `norma` sem `approved_by` ou sem `approved_at`,
recusa `norma` com `test:` preenchido, recusa `dev` com `test:` vazio, e recusa qualquer unidade que
traga a linha `Último resultado` no corpo. As onze unidades existentes passam no lint depois do passo
5 — **é isso que prova que a linha saiu de todas**, e não uma contagem.

`verificacao.verificar` sobre uma unidade `norma` com aprovação declarada devolve `verified` **sem
executar comando nenhum** — o teste prova a não-execução mockando `subprocess.run` e afirmando que
ele não foi chamado — e grava `verified_at` igual a `approved_at`. Sem a aprovação, devolve `spec`.

**A suíte inteira continua verde.**

## Verificação

```
./scripts/test-python.sh .claude/skills/decode-and-code/scripts/tests/test_lint_plano.py
```

## Fonte

- [`0001-decode-and-code-foundation.md`](0001-decode-and-code-foundation.md), *Escopo* → *Fase 4*
- `L-01` e `L-22`, e o `B-01` do backlog do AmFlow que originou o porte de plano
- `lint_unidade.py:37` — o vocabulário fechado que esta unidade estende
