---
# about
name: config-and-paths
type: unit
project: DecodeAndCode
description: Os scripts deixam de assumir caminhos e cores do AmFlow — tudo resolve por config.json com defaults embutidos, e a norma perde as menções que são sobre a mesma coisa
tags: [decode-and-code, config, desacoplamento, fase-1]

# alvo
core: model
module: decode-and-code
block: ""
owner: model
unit_id: 0001-01
unit_type: dev

# verificação
state: spec
test: .claude/skills/decode-and-code/scripts/tests/test_config.py
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

# 0001-01 — config-and-paths

**Responsabilidade:** tirar dos scripts a suposição de que o projeto é o AmFlow — caminhos, cores e
runner de teste passam a vir de `config.json`, com defaults embutidos que fazem este repositório
funcionar sem configurar nada.

## Contrato

| Campo | Detalhe |
|---|---|
| **Entrada** | `config.json` em `.claude/skills/decode-and-code/config.json` — opcional |
| **Saída** | `lib.config()` devolve um dict resolvido: arquivo do disco sobreposto aos defaults embutidos |
| **Auth** | — |
| **Efeito** | `lib.plan_root()`, `lib.core_dir()`, `scaffold` e `verificacao` passam a ler dali; nenhuma assinatura pública muda |
| **Erro** | `config.json` malformado levanta `ValueError` nomeando o arquivo e o campo. Ausente **não é erro** — cai nos defaults |

**Chaves e defaults embutidos:**

| Chave | Default | Quem usa |
|---|---|---|
| `plan_root` | `"docs/plan"` | `lib.plan_root()` |
| `root_markers` | `[".claude", "docs"]` | `lib._find_repo_root()` |
| `move_script` | `"scripts/move-md.py"` | `scaffold` |
| `runners` | `{".py": "scripts/test-python.sh"}` | `verificacao._comando()` |

## Sequência

1. Escrever `config.json` com as quatro chaves acima e `lib.config()` — leitura com `json.loads`, sobreposição sobre os defaults embutidos, cache em módulo. Ausente cai no default; malformado levanta.
2. `lib.py`: `plan_root()` e `_find_repo_root()` passam a ler `config()`. As docstrings perdem "AmFlow" e a citação de `estudo-runtime-e-dependencias.md`, que não existe neste repositório.
3. `scaffold.py`: o caminho de `move-md.py` vem de `config()["move_script"]` em vez da constante da linha 38.
4. `verificacao.py`: `_comando()` resolve a extensão pelo mapa `runners`, e extensão fora do mapa levanta `ValueError` como hoje. **Sai `_comando_typescript`** (linhas 155-160) e com ela a classe `TestComandoTypescript` — é instância do AmFlow, e o mapa a substitui. **Fica `_VITEST_SKIPPED_RE`** (linha 117): é leitura de saída de runner, não instância, e um projeto que declare um runner `.ts` no `runners` continua precisando dela.
5. `verificacao.py`: `SENTINELA_REENTRANCIA` passa a `"DECODE_AND_CODE_VERIFICACAO_EM_CURSO"`.
6. Retirar de `backlog.py`, `lint_skill.py` e `lint_unidade.py` as citações de docstring a `docs/plan/hub/` e `docs/plan/builder/` — são links mortos neste repositório. O racional que elas carregam fica; some só o ponteiro.
7. Retirar da norma as linhas que citam cores, caminhos e serviços do AmFlow, e a nota de migração que anuncia esta unidade. O `project:` do frontmatter passa a `DecodeAndCode`.
8. Escrever `tests/test_config.py` cobrindo o critério de aceite.

## Arquivos

| Caminho | O que muda |
|---|---|
| `.claude/skills/decode-and-code/config.json` | **novo** — as quatro chaves |
| `.claude/skills/decode-and-code/scripts/lib.py` | `config()`; `plan_root()` e `_find_repo_root()` leem dela |
| `.claude/skills/decode-and-code/scripts/scaffold.py` | `move_script` vem do config (hoje linha 38) |
| `.claude/skills/decode-and-code/scripts/verificacao.py` | mapa `runners`; sai `_comando_typescript` (linhas 155-160); **fica** `_VITEST_SKIPPED_RE` (linha 117); sentinela renomeada (linha 43) |
| `.claude/skills/decode-and-code/scripts/tests/test_verificacao.py` | sai a classe `TestComandoTypescript` (linhas 330-351), que cobre a função removida e **passa hoje**. Os quatro `test_vitest_*` de `TestExecucaoIncompleta` (linhas 241-262) **ficam** — cobrem a regex, não o runner |
| `.claude/skills/decode-and-code/scripts/backlog.py` | docstring linha 19 |
| `.claude/skills/decode-and-code/scripts/lint_skill.py` | docstring linhas 10 e 140 |
| `.claude/skills/decode-and-code/scripts/lint_unidade.py` | docstring linha 15 |
| `docs/plan/system/modelo-dev-units.md` | frontmatter `project:`; nota de migração (linhas 27-36); as menções ao AmFlow |
| `.claude/skills/decode-and-code/scripts/tests/test_config.py` | **novo** — o teste declarado |

## Dependências

Nenhuma. É a primeira unidade do plano.

## Normas aplicáveis

| Norma | Onde |
|---|---|
| Fronteira skill / script | [`modelo-dev-units.md`](../../system/modelo-dev-units.md), seção *Fronteira skill / script* |
| Regiões — quem escreve o quê | [`modelo-dev-units.md`](../../system/modelo-dev-units.md), seção *Regiões* |
| `D-11` — config em arquivo declarativo | [`0001-decode-and-code-foundation.md`](0001-decode-and-code-foundation.md), seção *Decisões* |
| Nada específico de projeto viaja no plugin | `.claude/CLAUDE.md`, invariante 2 |
| Simplicidade primeiro | `.claude/CLAUDE.md` — sem configurabilidade além das quatro chaves |

## Critério de aceite

Com `config.json` ausente, os scripts resolvem exatamente os mesmos caminhos de hoje. Com um
`config.json` declarando `plan_root` diferente, `lib.plan_root()` acompanha e `scaffold` grava no
alvo novo. Nenhum `.py` da skill contém as strings `AmFlow`, `AMFLOW`, `docs/plan/hub` ou
`docs/plan/builder`. A norma não contém `Supabase` nem os quatro cores do AmFlow.

**Nenhum teste verde vira vermelho.** A única remoção permitida na suíte é `TestComandoTypescript`,
porque a função que ela cobre deixou de existir — a suíte cai de 158 para 157 rodados, e os 25
vermelhos herdados continuam sendo os mesmos 25. Os quatro `test_vitest_*` de `TestExecucaoIncompleta`
continuam verdes: se caírem, a regex foi removida junto com o runner, e isso é erro.

## Verificação

```
./scripts/test-python.sh .claude/skills/decode-and-code/scripts/tests/test_config.py
```

Último resultado: não executado.

## Fonte

- [`0001-decode-and-code-foundation.md`](0001-decode-and-code-foundation.md), *Escopo* → Fase 1, e `D-11`
- Acoplamento medido em 2026-08-23: 6 scripts citam caminho ou nome do AmFlow — `lib.py` (8
  ocorrências), `verificacao.py` (16), `lint_skill.py` (3), `lint_unidade.py` (2), `scaffold.py` (2),
  `backlog.py` (1). Executável em `lib.py:23,47`, `scaffold.py:38` e `verificacao.py:43,153,159-160`;
  o restante é docstring
