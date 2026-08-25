---
# about
name: size-instrumentation
type: unit
project: DecodeAndCode
description: No fechamento, o porte declarado passa a ficar registrado ao lado do resultado real — é o que separa vocabulário calibrável de palpite que envelhece
tags: [decode-and-code, porte, medicao, instrumentacao]

# alvo
core: model
module: decode-and-code
block: ""
owner: model
unit_id: 0001-15
unit_type: dev

# verificação
state: spec
test: .claude/skills/decode-and-code/scripts/tests/test_porte_medido.py
verified_at: ""

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

# 0001-15 — size-instrumentation

**Responsabilidade:** gravar, quando um plano fecha, o porte que o humano **declarou** ao lado do que
o trabalho **foi**. Sem isso o vocabulário de três palavras da `0001-12` nunca se corrige: ninguém
descobre que o que se chama de médio aqui vem custando o que se chamava de grande.

## Contrato

| Campo | Detalhe |
|---|---|
| **Entrada** | `porte.medir(alvo)` e `porte.registrar(alvo)` — o mesmo `alvo` que `backlog.projetar` aceita: diretório no grande, arquivo nos demais |
| **Saída** | `medir` devolve o dicionário da medição. `registrar` devolve a linha acrescentada, ou `None` quando o plano já tem linha |
| **Auth** | — |
| **Efeito** | `medir` só lê. `registrar` **acrescenta** uma linha a `docs/plan/system/porte-medido.md` e nunca reescreve nenhuma |
| **Erro** | Plano ilegível levanta `ValueError` antes de escrever. Git indisponível **não** levanta: a coluna sai como `não medido`, com o motivo |

**O que a medição carrega:**

| Coluna | De onde sai | Quando não sai |
|---|---|---|
| Porte declarado | `plan_size` do frontmatter | nunca — a `0001-12` o torna obrigatório |
| Unidades ou tarefas | `state` das unidades no grande; as caixas de `## Tarefas` no médio | `—` no pequeno, que não decompõe |
| Arquivos declarados | caminhos distintos das tabelas `## Arquivos` das unidades | `não declarado` fora do grande, onde não existem unidades |
| Linhas alteradas | `git diff --numstat` do commit que criou o plano até `HEAD`, **restrito aos arquivos declarados** | `não medido`, com o motivo, quando git falha ou o plano não tem commit |
| Fechado em | a data em que a situação virou `concluído` | nunca |

> **A restrição aos arquivos declarados é o que faz o número significar alguma coisa.** O churn do
> repositório inteiro no intervalo mediria todo trabalho paralelo e chamaria isso de custo do plano.
> Só é atribuível o que a unidade declarou tocar — e é por isso que a coluna fica vazia no pequeno e
> no médio, em vez de receber um número maior e errado.

**A tabela é append-only, e não é projeção.** Toda outra escrita de script neste repositório é
projeção — recalculada, sobrescrita, sempre igual à fonte. Esta é o contrário: a medição vale pelo
instante em que foi tirada, e recalculá-la meses depois daria outro número sobre o mesmo fato.
`registrar` acrescenta, confere se o plano já tem linha, e não toca em nenhuma existente.

**Quando dispara:** dentro de `backlog.projetar`, na transição da situação para `concluído` — o
momento em que ela **passa** a ser `concluído`, não toda vez que já é. A projeção roda a cada
unidade fechada, e sem a guarda a tabela ganharia uma linha por execução.

## Sequência

1. Escrever `porte.py` com `medir(alvo)` e `registrar(alvo)`, lendo o plano pelo mesmo caminho que `backlog` já usa — `regioes.ler_campo` e as tabelas do corpo.
2. Compor o real: unidades ou tarefas conforme o porte; caminhos distintos das tabelas `## Arquivos`; e as linhas alteradas por `git diff --numstat` restrito a esses caminhos, do commit que criou o plano até `HEAD` — com `não medido` e o motivo quando o git não responde, nunca um zero.
3. Chamar `registrar` em `backlog.projetar` **na transição** para `concluído`, comparando a situação lida com a projetada antes de escrever.
4. Criar `docs/plan/system/porte-medido.md` com frontmatter, cabeçalho da tabela e a nota de que a tabela é acrescentada, nunca reescrita — e que não há marcadores de projeção ali de propósito.
5. Escrever na norma a seção curta que diz onde o dado vive, o que cada coluna significa e para que ele serve: recalibrar o vocabulário de porte com dado, não com impressão.
6. Acrescentar a `fixtures.py` o que falta para montar um plano fechado, e escrever `tests/test_porte_medido.py` cobrindo o critério de aceite, com `subprocess.run` mockado.
7. Rodar o gate e relatar.

## Arquivos

| Caminho | O que muda |
|---|---|
| `.claude/skills/decode-and-code/scripts/porte.py` | **novo** — `medir` e `registrar` |
| `.claude/skills/decode-and-code/scripts/backlog.py` | `projetar` chama `registrar` na transição para `concluído` |
| `docs/plan/system/porte-medido.md` | **novo** — a tabela append-only |
| `docs/plan/system/modelo-dev-units.md` | a seção que diz onde o dado vive e para que serve |
| `.claude/skills/decode-and-code/scripts/tests/fixtures.py` | plano fechado nos portes que a medição cobre |
| `.claude/skills/decode-and-code/scripts/tests/test_porte_medido.py` | **novo** — o teste declarado |

## Dependências

A `0001-12`, pelo `plan_size` que a medição compara. A `0001-14`, pela ramificação de `_situacao` —
é a transição dela que dispara o registro, e o que conta como fonte muda com o porte.

## Normas aplicáveis

| Norma | Onde |
|---|---|
| *Backlog — região delimitada por marcadores*, e por que esta tabela **não** é uma região | [`modelo-dev-units.md`](../../system/modelo-dev-units.md), seção *Formato do plano* |
| A ramificação da situação por porte | [`14-derive-by-size.md`](14-derive-by-size.md) |
| Evidência acima de opinião | [`principles.md`](../../../../.claude/rules/principles.md) |
| Mockar `subprocess.run` em teste, em vez de executar de verdade | `.claude/skills/decode-and-code/scripts/verificacao.py:92` |

## Critério de aceite

`porte.medir` devolve o porte declarado e o real para um plano grande fechado, com as unidades
contadas, os caminhos distintos das tabelas `## Arquivos` deduplicados, e as linhas vindas do
`git diff --numstat` mockado. Caminho declarado duas vezes por duas unidades conta **uma**.

`porte.medir` devolve `não medido` **com motivo** — nunca zero, nunca exceção — quando `git` falha,
quando o comando não existe, e quando o plano não tem commit de criação. Cada um é um caso do teste.

`porte.registrar` acrescenta exatamente uma linha ao fim da tabela, preserva integralmente o que já
estava lá, e devolve `None` sem escrever quando o plano já tem linha. O teste roda `registrar` duas
vezes e afirma que o arquivo não mudou na segunda.

`backlog.projetar` registra **na transição**: a projeção que leva a situação de `em desenvolvimento`
para `concluído` grava a linha; uma segunda projeção com a situação já `concluído` não grava nada; e
projeção que devolve `em desenvolvimento` nunca grava.

**A suíte inteira continua verde**, e nenhum teste executa `git` de verdade.

## Verificação

```
./scripts/test-python.sh .claude/skills/decode-and-code/scripts/tests/test_porte_medido.py
```

## Fonte

- [`0001-decode-and-code-foundation.md`](0001-decode-and-code-foundation.md), *Escopo* → *Fase 4*
- `D-19` — por que a medição usa git e por que ela é restrita aos arquivos declarados
