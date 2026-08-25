---
# about
name: derive-by-size
type: unit
project: DecodeAndCode
description: O derive passa a ramificar pelo porte — não roda no pequeno, projeta tarefas no médio, e só o grande ganha diretório e um arquivo por unidade
tags: [decode-and-code, derive, porte, backlog, scaffold]

# alvo
core: model
module: decode-and-code
block: ""
owner: model
unit_id: 0001-14
unit_type: dev

# verificação
state: verified
test: .claude/skills/decode-and-code/scripts/tests/test_derive_por_porte.py
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

# 0001-14 — derive-by-size

**Responsabilidade:** fazer o porte declarado mudar o que o `derive` faz. A `0001-13` diz o que cada
porte carrega; esta faz o mecanismo obedecer — sem ela, os três formatos existem no lint e o script
continua tratando todo plano como grande.

## Contrato

| Campo | Detalhe |
|---|---|
| **Entrada** | `scaffold.aprovar(plano)` e `backlog.projetar(alvo)`, onde `alvo` passa a aceitar **diretório** (grande) ou **arquivo de plano** (pequeno e médio) |
| **Saída** | `aprovar` devolve o caminho final, que agora depende do porte. `projetar` devolve `(backlog, situacao)`, com `backlog` vazio no pequeno |
| **Auth** | — |
| **Efeito** | Cria estrutura, move o plano e projeta — cada um conforme a tabela abaixo |
| **Erro** | `ValueError` nomeando o campo quando o porte é ilegível. Região de backlog ausente **deixa de ser erro** no pequeno, onde ela é recusada por formato |

**O que o `derive` faz em cada porte:**

| Porte | Alvo | Região de backlog | Unidades | Situação projeta de |
|---|---|---|---|---|
| `pequeno` | `<core>/<NNNN>-<nome>.md` | não existe | **o derive não roda** | `status` do frontmatter |
| `médio` | `<core>/<NNNN>-<nome>.md` | as tarefas projetadas | nenhuma | as caixas de `## Tarefas` |
| `grande` | `<core>/<NNNN>-<nome>/<NNNN>-<nome>.md` | as unidades, como hoje | um arquivo por unidade | as unidades, como hoje |

> **Pequeno e médio não ganham diretório.** Pasta com um arquivo dentro é custo puro — e no pequeno
> ela seria pasta com um arquivo que nunca ganha companhia, porque o porte não decompõe nada.

**A situação projeta da fonte que o porte tem, e isso é deliberado.** No grande a fonte é o `state`
das unidades, projetado por teste. No médio são caixas que o **humano** marca, e no pequeno é o
`status` que o humano escreve. Não é exceção ao invariante 3: ele diz que `state` e `verified_at` de
uma **unidade** nunca se editam à mão, e no médio e no pequeno não existe unidade. Onde não há teste
para projetar, o humano é a fonte — e o alternativa seria exigir teste de uma correção de oito
linhas, que é exatamente o custo que o porte existe para remover.

**Onde o pequeno fecha:** `status: done` no frontmatter, escrito pelo humano. `aprovar` continua
gravando `approved`; o humano troca quando termina, e `projetar` lê. Nenhum script escreve `done`.

## Sequência

1. Ramificar o alvo em `scaffold.aprovar` pelo `plan_size` já validado pela `0001-12`: pequeno e médio vão para `<core>/<NNNN>-<nome>.md`, sem `mkdir`; grande segue como está.
2. Fazer `_garantir_secao_backlog` rodar apenas onde há projeção — médio e grande —, porque no pequeno a região é recusada pelo formato.
3. Aceitar arquivo de plano em `backlog.projetar` além de diretório, e ramificar a projeção: pequeno não escreve região nenhuma, médio projeta as tarefas de `## Tarefas`, grande segue como hoje.
4. Ramificar `_situacao` pela mesma fonte de cada porte — `status` no pequeno, caixas marcadas no médio, `state` das unidades no grande —, mantendo a regra da `0001-07`: fonte ilegível nunca projeta `concluído`.
5. Registrar a ramificação na norma, em *Fluxo completo*, e no modo `derive` da skill — incluindo que **no pequeno o derive não roda**, e que aprovar continua acontecendo.
6. Acrescentar a `fixtures.py` os planos pequeno e médio, e escrever `tests/test_derive_por_porte.py` cobrindo o critério de aceite.
7. Rodar o gate e relatar.

## Arquivos

| Caminho | O que muda |
|---|---|
| `.claude/skills/decode-and-code/scripts/scaffold.py` | alvo por porte, e `_garantir_secao_backlog` condicionado |
| `.claude/skills/decode-and-code/scripts/backlog.py` | `projetar` aceita arquivo, projeta tarefas, e `_situacao` ramifica |
| `docs/plan/system/modelo-dev-units.md` | *Fluxo completo* ramifica por porte |
| `.claude/skills/decode-and-code/SKILL.md` | o modo `derive` diz o que faz em cada porte |
| `.claude/skills/decode-and-code/scripts/tests/fixtures.py` | `plano()` produz pequeno e médio de verdade — sem diretório |
| `.claude/skills/decode-and-code/scripts/tests/test_derive_por_porte.py` | **novo** — o teste declarado |

## Dependências

A `0001-12`, pelo `plan_size` validado — sem ele a ramificação recebe valor que ninguém conferiu. A
`0001-13`, pelo formato de cada porte, que é o que esta unidade materializa. A `0001-07`, pela regra
de que fonte ilegível falha fechado, que continua valendo nos três portes.

## Normas aplicáveis

| Norma | Onde |
|---|---|
| *Fluxo completo*, e a reentrância da etapa 4 | [`modelo-dev-units.md`](../../system/modelo-dev-units.md) |
| *Backlog — região delimitada por marcadores* | [`modelo-dev-units.md`](../../system/modelo-dev-units.md), seção *Formato do plano* |
| O formato de cada porte, e o que cada um recusa | [`13-plan-formats.md`](13-plan-formats.md) |
| `L-18` — situação que projeta `concluído` sem poder contar | [`0001-decode-and-code-foundation.md`](0001-decode-and-code-foundation.md), seção *Lacunas* |
| Invariante 3 — `state` e `verified_at` nunca se editam à mão | `.claude/CLAUDE.md` |

## Critério de aceite

`scaffold.aprovar` sobre plano `pequeno` e sobre plano `médio` produz `<core>/<NNNN>-<nome>.md` e
**nenhum diretório novo** — o teste afirma a ausência da pasta, não só a presença do arquivo. Sobre
plano `grande`, produz o diretório e o arquivo dentro dele, como hoje.

`backlog.projetar` aceita arquivo de plano e diretório. No pequeno **não escreve região nenhuma** e
não levanta por marcador ausente; a situação vem de `status` — `approved` projeta `em
desenvolvimento`, `done` projeta `concluído`. No médio, a região recebe as tarefas de `## Tarefas` e
a situação é `concluído` só com **ao menos uma** tarefa e todas marcadas. No grande, backlog e
situação saem idênticos aos de hoje — o teste do plano real `0001` prova a não-regressão.

Fonte ilegível continua falhando fechado nos três portes: pequeno sem `status`, médio sem
`## Tarefas` e grande sem `## Escopo` projetam `em desenvolvimento`, nunca `concluído`.

**A suíte inteira continua verde**, incluindo `test_backlog.py` e `test_situacao.py`.

## Verificação

```
./scripts/test-python.sh .claude/skills/decode-and-code/scripts/tests/test_derive_por_porte.py
```

## Fonte

- [`0001-decode-and-code-foundation.md`](0001-decode-and-code-foundation.md), *Escopo* → *Fase 4*
- `B-01` do backlog do AmFlow — correção de oito linhas não paga estrutura de quinze unidades
- `backlog.py:188` — a regra de falhar fechado que a `0001-07` estabeleceu
