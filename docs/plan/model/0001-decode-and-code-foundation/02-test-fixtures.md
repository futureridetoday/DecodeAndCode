---
# about
name: test-fixtures
type: unit
project: DecodeAndCode
description: Os 25 testes que usam arquivos reais do AmFlow como fixture ganham fixtures próprios, construídos em tempdir — a suíte deixa de depender de um repositório que não está aqui
tags: [decode-and-code, testes, fixtures, fase-1]

# alvo
core: model
module: decode-and-code
block: ""
owner: model
unit_id: 0001-02
unit_type: dev

# verificação
state: spec
test: .claude/skills/decode-and-code/scripts/tests/test_fixtures.py
verified_at: ""

# history
author: Bortoli
created: 2026-08-23
status: draft
version: 1.0.0
updated: ""

# system
scope: project
auto_load: false
dependencies: []
---

# 0001-02 — test-fixtures

**Responsabilidade:** dar à suíte fixtures que ela mesma constrói, para que nenhum teste dependa de um
arquivo que só existe no AmFlow.

## Contrato

| Campo | Detalhe |
|---|---|
| **Entrada** | — |
| **Saída** | `tests/fixtures.py` expõe construtores que escrevem artefatos válidos num diretório dado: `plano()`, `unidade()`, `skill()`, `planos_md()` |
| **Auth** | — |
| **Efeito** | Os 11 arquivos de teste acoplados passam a montar o que precisam em `tempfile.TemporaryDirectory()`; nenhum lê caminho real do repositório |
| **Erro** | Construtor com argumento inválido levanta `ValueError` antes de escrever qualquer arquivo |

**Inventário do acoplamento, medido em 2026-08-23 com `./scripts/test-python.sh`** — 158 testes, 25
vermelhos (4 `FAIL` + 21 `ERROR`), 133 verdes.

**O total muda antes de esta unidade rodar, e é esperado:** a `0001-01` remove `TestComandoTypescript`
junto com a função que ela cobre, então a suíte chega aqui com **157** rodados. Os 25 vermelhos são os
mesmos — nenhum deles está nessa classe. Confira o total antes de usá-lo; o número abaixo é de antes
da `01`.

| Fixture que falta | Testes | Onde |
|---|---|---|
| `.claude/skills/dev-units/SKILL.md` | 10 | `test_modo_review`, `test_modo_derive`, `test_modo_implement` (3 cada), `test_skill_base` (1) |
| `docs/plan/hub/0001-mcp/01-handler-auth.md` | 7 | `test_regioes.TestCampoFrontmatter` (6), `test_lint_unidade.test_handler_auth_aprova` |
| `docs/plan/builder/0002-dev-units/{0002-dev-units,01-lib-base,08-verificacao}.md` | 3 | `test_backlog`, `test_lint_unidade`, `test_verificacao` |
| `.claude/skills/digital-twin-product/SKILL.md` | 1 | `test_deprecacao` |
| Suposições sobre a população do repositório | 4 | `test_lib` (core `builder`), `test_lint_skill` (skill `backlog`; ≥ 10 skills), `test_regioes` (plano `mcp`) |

**Os 4 da última linha não são fixture ausente — são asserção sobre um repositório que não é este.**
`test_lint_skill` exige 10 skills e aqui há 1; `test_lib` exige o core `builder`. Viram asserção sobre
o que o repositório declara, não sobre um número herdado.

## Sequência

1. Escrever `tests/fixtures.py` com os quatro construtores. `unidade()` reaproveita a forma de `UNIDADE_VALIDA`, hoje inline em `test_lint_unidade.py:23` — passa a ter uma fonte só.
2. Escrever `tests/test_fixtures.py`, o teste declarado: cada construtor produz artefato que passa no lint correspondente — `lint_unidade` para `unidade()`, `lint_skill` para `skill()`, `regioes.ler_regiao` para `planos_md()`.
3. Repontar `test_modo_review`, `test_modo_derive`, `test_modo_implement` e `test_skill_base` para o `SKILL.md` real desta skill. Já aprova hoje: `lint_skill.lint(SKILL, modos=[review, derive, implement])` devolve `[]`.
4. Repontar `test_regioes.TestCampoFrontmatter` e `test_lint_unidade.TestUnidadesReais` para `fixtures.unidade()`.
5. Repontar `test_backlog.TestCaminhoRelativo` e `test_verificacao.TestSentinelaReentrancia` para `fixtures.plano()` e `fixtures.unidade()`.
6. Trocar as 4 asserções de população: `test_lib` e `test_lint_skill` passam a derivar a expectativa do disco, no padrão que `test_numeracao` já usa; `test_regioes.test_le_regiao_existente` usa `fixtures.planos_md()`.
7. Remover `tests/test_deprecacao.py`. Ele verifica que `plan-dev-units` e `digital-twin-product` deixaram de se citar — nenhum dos dois existiu neste repositório, e não há o que reapontar.
8. Rodar `./scripts/test-python.sh` inteiro e registrar o resultado no relatório.

## Arquivos

| Caminho | O que muda |
|---|---|
| `.claude/skills/decode-and-code/scripts/tests/fixtures.py` | **novo** — os quatro construtores |
| `.claude/skills/decode-and-code/scripts/tests/test_fixtures.py` | **novo** — o teste declarado |
| `.claude/skills/decode-and-code/scripts/tests/test_modo_review.py` | `SKILL` (linha 22) |
| `.claude/skills/decode-and-code/scripts/tests/test_modo_derive.py` | `SKILL` |
| `.claude/skills/decode-and-code/scripts/tests/test_modo_implement.py` | `SKILL` |
| `.claude/skills/decode-and-code/scripts/tests/test_skill_base.py` | `skill` (linha 25) |
| `.claude/skills/decode-and-code/scripts/tests/test_regioes.py` | `TestCampoFrontmatter` (setUp) e `test_le_regiao_existente` (linha 114) |
| `.claude/skills/decode-and-code/scripts/tests/test_lint_unidade.py` | `TestUnidadesReais`; `UNIDADE_VALIDA` (linha 23) migra para `fixtures.py` |
| `.claude/skills/decode-and-code/scripts/tests/test_backlog.py` | linha 356 |
| `.claude/skills/decode-and-code/scripts/tests/test_verificacao.py` | linha 410 |
| `.claude/skills/decode-and-code/scripts/tests/test_lib.py` | linhas 74-75 |
| `.claude/skills/decode-and-code/scripts/tests/test_lint_skill.py` | linhas 70 e 107 |
| `.claude/skills/decode-and-code/scripts/tests/test_deprecacao.py` | **removido** |

## Dependências

A unidade `0001-01`. Ela renomeia a sentinela de reentrância e retira o ramo `.ts` de
`verificacao.py`; `test_verificacao` toca os dois.

## Normas aplicáveis

| Norma | Onde |
|---|---|
| Os dois gates | [`modelo-dev-units.md`](../../system/modelo-dev-units.md), seção *Os dois gates* |
| Ciclo quando o teste ainda não existe | [`modelo-dev-units.md`](../../system/modelo-dev-units.md), seção de mesmo nome |
| `L-11` — o que este gate prova, e o que não prova | [`0001-decode-and-code-foundation.md`](0001-decode-and-code-foundation.md), seção *Lacunas* |
| Guarda contra verde falso | `scripts/test-python.sh` — `Ran 0 tests` com arquivo de teste em disco é erro |

## Critério de aceite

`tests/fixtures.py` produz plano, unidade, skill e `_planos.md` que passam no lint correspondente sem
tocar em nenhum caminho real do repositório, e `tests/test_fixtures.py` prova isso. Nenhum arquivo em
`tests/` referencia `docs/plan/hub`, `docs/plan/builder`, `skills/dev-units` ou
`skills/digital-twin-product`.

**A suíte inteira verde é a condição de fechamento da Fase 1, não o gate desta unidade** — o campo
`test:` aceita um arquivo só, e a razão está na `L-11`.

## Verificação

```
./scripts/test-python.sh .claude/skills/decode-and-code/scripts/tests/test_fixtures.py
```

Fechamento da Fase 1, conferido pelo humano:

```
./scripts/test-python.sh
```

Último resultado: não executado.

## Fonte

- [`0001-decode-and-code-foundation.md`](0001-decode-and-code-foundation.md), *Escopo* → Fase 1, e `L-10`
- Inventário medido em 2026-08-23 com `./scripts/test-python.sh`, o oráculo que o gate de saída roda
