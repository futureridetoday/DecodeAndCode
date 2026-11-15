---
# about
name: setup-record
type: unit
project: DecodeAndCode
description: O registro do setup do projeto — setup.py e os subcomandos setup-* sobre <plan_root>/system/setup.md, com perfil, decisões em vocabulário fechado e a data de conclusão
tags: [decode-and-code, setup, registro, dc-py]

# alvo
core: model
module: onboard-new-project
block: ""
owner: model
unit_id: 0009-01
unit_type: dev

# verificação
state: spec
test: .claude/skills/decode-and-code/scripts/tests/test_setup.py
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

# 0009-01 — setup-record

**Responsabilidade:** guardar, num arquivo versionado do projeto, o que o setup confirmou com o
humano e o que ele decidiu sobre cada sugestão — para que um segundo setup não sugira de novo o que
já foi aceito ou rejeitado, e para que o aviso de abertura saiba quando parar.

## Contrato

| Campo | Detalhe |
|---|---|
| **Entrada** | `projeto: Path` explícito nas funções; nos subcomandos, `lib.repo_root()`. `setup-perfil` e `setup-registrar` leem JSON do stdin |
| **Saída** | `setup.caminho(projeto)` → `<projeto>/<plan_root>/system/setup.md`. `iniciar` → caminho criado ou `None`. `decididas` → lista de chaves. `lint` → lista de problemas, vazia quando são |
| **Auth** | — |
| **Efeito** | Escreve só `setup.md`. `iniciar` nunca sobrescreve |
| **Erro** | `ValueError` para valor fora do vocabulário, chave repetida, seção ausente ou campo faltando; nada é escrito nesse caso. Subcomandos: `1` para reprovação (lint, valor recusado), `2` para stdin vazio, JSON incompleto ou arquivo ausente |

**Funções de `setup.py`:**

| Função | O que faz |
|---|---|
| `caminho(projeto)` | `Path(projeto) / lib.config()["plan_root"] / "system" / "setup.md"` |
| `iniciar(projeto)` | Esqueleto em `_CONTEUDO_INICIAL` (mesmo padrão de `huddle._CONTEUDO_INICIAL`, sem arquivo de template): frontmatter com `project:` = nome do diretório de `projeto` e `completed_at: ""`; seções `## Perfil` e `## Decisões`, esta com a tabela vazia |
| `perfil(arquivo, objetivo, escopo, stack, confirmacao)` | Reescreve o corpo de `## Perfil` com quatro linhas `- **Objetivo:** …`, `- **Escopo:** …`, `- **Stack:** …`, `- **Confirmado:** …` |
| `registrar(arquivo, chave, tipo, origem, resultado, detalhe)` | Acrescenta uma linha no fim da tabela de `## Decisões`, antes do próximo `## `, com a data de hoje |
| `decididas(arquivo)` | As chaves da tabela, na ordem |
| `concluir(arquivo, data)` | Grava `completed_at` |
| `lint(arquivo)` | As duas seções presentes, cada linha da tabela com valores do vocabulário, chave única, `completed_at` vazio ou `AAAA-MM-DD` |

**Tabela de `## Decisões`:** `| chave | tipo | origem | resultado | destino ou motivo | data |`.
`chave` é o slug que a skill dá à sugestão (kebab-case ASCII). `tipo` ∈ {`guideline`, `guardrail`,
`princípio`}. `origem` ∈ {`stack`, `decisão do time`, `existente`} ou `arquivo <caminho>`. `resultado`
∈ {`aceita`, `rejeitada`, `existente`}. `|` dentro de `detalhe` é escapado como `\|`, como em
`huddle.fechar`.

**Subcomandos planos do `dc.py`** (`D-06` do `0007`): `setup-iniciar`, `setup-perfil` (stdin
`{objetivo, escopo, stack, confirmacao}`), `setup-registrar` (stdin
`{chave, tipo, origem, resultado, detalhe}`), `setup-decididas`, `setup-concluir [--data]` (padrão:
hoje) e `setup-lint`. A leitura do stdin segue `_ler_json_do_stdin` do próprio `dc.py`.

## Sequência

1. Escrever `tests/test_setup.py` com os casos do critério de aceite, contra um projeto em `tempfile` passado por parâmetro.
2. Escrever `setup.py`: `caminho`, `iniciar` e o esqueleto.
3. `perfil`, `registrar` e `decididas`, com a validação de vocabulário antes de qualquer escrita.
4. `concluir` (por `regioes.escrever_campos`) e `lint`.
5. Os seis subcomandos no `dc.py`, depois de `_huddle_migrar`, no padrão dos `huddle-*`.
6. Os seis nomes em `SUBCOMANDOS` de `tests/test_dc.py`, e uma classe `_ProjetoCase` com `bootstrap()` cobrindo cada um.
7. Rodar o teste declarado e a suíte inteira.

## Arquivos

| Caminho | O que muda |
|---|---|
| `.claude/skills/decode-and-code/scripts/setup.py` | **novo** |
| `.claude/skills/decode-and-code/scripts/tests/test_setup.py` | **novo** — o teste declarado |
| `.claude/skills/decode-and-code/scripts/dc.py` | seis handlers e seis entradas no `_parser`, depois dos `huddle-*` |
| `.claude/skills/decode-and-code/scripts/tests/test_dc.py` | `SUBCOMANDOS` e uma classe de teste |
| `.claude/skills/decode-and-code/scripts/huddle.py:259-330` | referência de padrão: `_fim_da_secao` e `fechar` (inserção no fim da tabela) |

## Dependências

Nenhuma unidade deste plano. Usa `lib`, `regioes` e o padrão de subcomando do `dc.py`.

## Normas aplicáveis

| Norma | Onde |
|---|---|
| Onde o estado do setup vive | [`0009-onboard-new-project.md`](0009-onboard-new-project.md), seção *Decisões* |
| O que a unidade 01 entrega | [`0009-onboard-new-project.md`](0009-onboard-new-project.md), seção *Escopo* |
| Determinismo em código | [`modelo-dev-units.md`](../../system/modelo-dev-units.md), seção *Fronteira skill / script* |

## Critério de aceite

Num projeto em `tempfile`: `setup.lint` aprova o arquivo depois de `iniciar`, `perfil`,
`registrar` e `concluir`; `decididas` devolve a chave logo depois de `registrar`; `tipo`, `origem` ou
`resultado` fora do vocabulário e chave repetida são recusados sem mudar o arquivo; uma segunda chamada
de `iniciar` devolve `None` e não toca no arquivo; e cada subcomando do `dc.py` sai com o código do
contrato. **A suíte inteira continua verde.**

## Verificação

```
./scripts/test-python.sh .claude/skills/decode-and-code/scripts/tests/test_setup.py
```

## Fonte

- [`0009-onboard-new-project.md`](0009-onboard-new-project.md), *Escopo* → *Fase 1*, unidade 01
