---
# about
name: project-scan
type: unit
project: DecodeAndCode
description: O inventário do projeto para o setup — descoberta.py e dc.py descobrir listam as fontes por uma tupla literal de globs, com as primeiras 60 linhas, e à parte a norma que já existe; não classifica nada
tags: [decode-and-code, setup, inventario, dc-py]

# alvo
core: model
module: onboard-new-project
block: ""
owner: model
unit_id: 0009-02
unit_type: dev

# verificação
state: spec
test: .claude/skills/decode-and-code/scripts/tests/test_descoberta.py
verified_at: ""

# history
author: Claude
created: 2026-11-15
status: draft
version: 1.0.0
updated: ""

# system
scope: project
auto_load: false
dependencies: []
---

# 0009-02 — project-scan

**Responsabilidade:** dar à skill `setup` o material para sugerir guidelines e guardrails —
os arquivos que dizem a stack, o objetivo e as convenções do projeto, e a norma que ele já tem —
sem julgar nada: classificar é da skill.

## Contrato

| Campo | Detalhe |
|---|---|
| **Entrada** | `descoberta.descobrir(projeto: Path)`; no `dc.py descobrir`, `lib.repo_root()` |
| **Saída** | `{"fontes": [{"caminho", "trecho"}], "existentes": {"guidelines": [...], "principios": [...], "guardrails": [...], "aviso": str \| None}}`. `caminho` relativo ao projeto, em ordem; `trecho` são as primeiras 60 linhas |
| **Auth** | — |
| **Efeito** | Só leitura |
| **Erro** | Arquivo ilegível (binário, permissão) vira entrada com `trecho` vazio, nunca exceção. `guardrails.json` que não passa em `guardrail.lint_arquivo` deixa `guardrails` vazio e preenche `aviso` |

**`FONTES` é uma tupla literal de globs relativos à raiz**, e nada fora dela entra:
`CLAUDE.md`, `.claude/CLAUDE.md`, `CLAUDE.local.md`, `AGENTS.md`, `README*`, `CONTRIBUTING*`,
`package.json`, `pyproject.toml` (texto bruto, sem `tomllib`), `tsconfig.json`, `components.json`,
`tailwind.config.*`, `.eslintrc*`, `eslint.config.*`, `.prettierrc*`, `prettier.config.*`,
`biome.json`, `biome.jsonc`, `ruff.toml`, `.ruff.toml`, `.editorconfig`, `.pre-commit-config.yaml`,
`.github/workflows/*.yml`, `.gitlab-ci.yml`, `.cursor/rules/**/*`, `.cursorrules`, `.windsurfrules` e
`.clinerules`. Só arquivos; sem duplicata quando dois globs casam o mesmo caminho.

**`existentes`:** `guidelines` são os nomes dos `.md` diretos em `.claude/rules/` com `paths:`;
`principios`, os sem `paths:` (o mesmo corte de `registry._e_guideline`, que já tolera `.md` sem
frontmatter); `guardrails`, os `nome` das regras de `.claude/guardrails.json`.

**`dc.py descobrir`** imprime um bloco `### <caminho>` com o trecho por fonte e, no fim,
`## Já existe`, com as três listas e o aviso, se houver. Sai `0`.

## Sequência

1. Escrever `tests/test_descoberta.py` contra um projeto em `tempfile`.
2. Escrever `descoberta.py` com `FONTES` e `descobrir`.
3. A parte de `existentes`, reaproveitando `registry._e_guideline` e `guardrail.lint_arquivo`.
4. O subcomando `descobrir` no `dc.py`, `"descobrir"` em `SUBCOMANDOS` de `tests/test_dc.py` e um caso.
5. Rodar o teste declarado e a suíte inteira.

## Arquivos

| Caminho | O que muda |
|---|---|
| `.claude/skills/decode-and-code/scripts/descoberta.py` | **novo** |
| `.claude/skills/decode-and-code/scripts/tests/test_descoberta.py` | **novo** — o teste declarado |
| `.claude/skills/decode-and-code/scripts/dc.py` | handler e entrada no `_parser` |
| `.claude/skills/decode-and-code/scripts/tests/test_dc.py` | `SUBCOMANDOS` e um caso |
| `.claude/skills/decode-and-code/scripts/registry.py:49-60` | `_e_guideline`, reaproveitado |
| `.claude/skills/decode-and-code/scripts/guardrail.py:63` | `lint_arquivo`, reaproveitado |

## Dependências

Nenhuma unidade deste plano.

## Normas aplicáveis

| Norma | Onde |
|---|---|
| O que a unidade 02 entrega, e que ela não classifica | [`0009-onboard-new-project.md`](0009-onboard-new-project.md), seção *Escopo* |
| Etapa 1 do fluxo, que consome o inventário | [`0009-onboard-new-project.md`](0009-onboard-new-project.md), seção *O fluxo* |
| Princípio e guideline: o corte por `paths:` | [`modelo-dev-units.md`](../../system/modelo-dev-units.md), seção *Camada normativa* |

## Critério de aceite

Num `tempfile` com `.claude/CLAUDE.md`, `components.json`, um `src/app.ts`, uma guideline e um
princípio em `.claude/rules/` e um `guardrails.json` válido, `descobrir` lista os dois primeiros como
fonte, com trecho de no máximo 60 linhas, **não** lista `src/app.ts`, e devolve a guideline, o
princípio e o nome da regra em `existentes`; com `guardrails.json` malformado, `guardrails` vem vazio
e `aviso` preenchido, sem exceção. **A suíte inteira continua verde.**

## Verificação

```
./scripts/test-python.sh .claude/skills/decode-and-code/scripts/tests/test_descoberta.py
```

## Fonte

- [`0009-onboard-new-project.md`](0009-onboard-new-project.md), *Escopo* → *Fase 1*, unidade 02
