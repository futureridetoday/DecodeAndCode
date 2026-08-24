---
# about
name: incremental-derive
type: unit
project: DecodeAndCode
description: A derivação incremental ganha teste declarado e registro na norma — aprovar é idempotente sobre plano já movido, e o modo derive passa a ter caminho para plano aprovado sem tratar o caso em markdown
tags: [decode-and-code, derive, scaffold, correcao, l-17]

# alvo
core: model
module: decode-and-code
block: ""
owner: model
unit_id: 0001-06
unit_type: dev

# verificação
state: verified
test: .claude/skills/decode-and-code/scripts/tests/test_scaffold_idempotente.py
verified_at: 2026-08-24

# history
author: Bortoli
created: 2026-08-24
status: draft
version: 1.0.0
updated: ""

# system
scope: project
auto_load: false
dependencies: []
---

# 0001-06 — incremental-derive

**Responsabilidade:** dar teste declarado e registro normativo ao comportamento que hoje existe em
código sem nenhum dos dois — `scaffold.aprovar` idempotente sobre plano já aprovado.

## Contrato

| Campo | Detalhe |
|---|---|
| **Entrada** | `scaffold.aprovar(plano)` com um plano já movido do `_inbox` e com `plan_id` atribuído |
| **Saída** | O próprio caminho do plano, resolvido |
| **Auth** | — |
| **Efeito** | **Nenhum.** Nada é escrito: nem frontmatter, nem `_planos.md`, nem estrutura |
| **Erro** | Plano no `_inbox` segue o caminho de sempre, e todas as validações atuais continuam valendo |

**O estado em que esta unidade começa, e por que ela não escreve código do zero:**

O mecanismo foi corrigido em **2026-08-24**, fora de unidade, por decisão do humano — o impasse era
que a unidade que conserta o `derive` precisaria do `derive` para ser derivada. `scaffold._ja_aprovado`
existe e está commitado em `de4fc57`. **O que não existe é teste próprio:** hoje ele é coberto só de
lado, pelo fato de a derivação da Fase 2 ter funcionado.

> **Isto não é unidade de escrever código, é unidade de fechar a dívida que a correção abriu.** Se a
> execução concluir que o mecanismo está errado, a correção é do mecanismo e a divergência vira
> lacuna — mas o caminho esperado é teste e norma, não reescrita.

## Sequência

1. Ler `scaffold._ja_aprovado` e `scaffold.aprovar` como estão hoje, e conferir contra o contrato acima. Divergência entre o que o código faz e o que este contrato declara é achado, não coisa a ajustar em silêncio.
2. Escrever `tests/test_scaffold_idempotente.py` cobrindo o critério de aceite, com fixtures montados em `tempfile.TemporaryDirectory()` — nenhum teste toca o plano real do repositório.
3. Cobrir os dois lados da guarda: plano fora do `_inbox` **com** `plan_id` é no-op; plano fora do `_inbox` **sem** `plan_id` **não** é no-op e segue o caminho normal. O segundo é o que impede a guarda de engolir plano mal formado.
4. Cobrir que o no-op **não escreve**: comparar o conteúdo do plano e do `_planos.md` antes e depois, byte a byte.
5. Registrar o comportamento na norma, na seção *Fluxo completo*: a etapa 4 é reentrante, e derivar em lotes é o caminho previsto — não exceção. Uma frase, sem duplicar o que o docstring já diz.
6. Rodar o gate e relatar.

## Arquivos

| Caminho | O que muda |
|---|---|
| `.claude/skills/decode-and-code/scripts/tests/test_scaffold_idempotente.py` | **novo** — o teste declarado |
| `docs/plan/system/modelo-dev-units.md` | uma frase na seção *Fluxo completo*, sobre reentrância da etapa 4 |
| `.claude/skills/decode-and-code/scripts/scaffold.py` | **só se** o passo 1 achar divergência com o contrato |

## Dependências

Nenhuma unidade. O mecanismo que ela cobre está em disco desde `de4fc57`.

## Normas aplicáveis

| Norma | Onde |
|---|---|
| Fluxo completo — as nove etapas | [`modelo-dev-units.md`](../../system/modelo-dev-units.md), seção *Fluxo completo* |
| `D-12` — a derivação é incremental, fase a fase | [`0001-decode-and-code-foundation.md`](0001-decode-and-code-foundation.md), seção *Decisões* |
| `L-17` — o que a `D-12` supunha e não era verdade | [`0001-decode-and-code-foundation.md`](0001-decode-and-code-foundation.md), seção *Lacunas* |
| Código, não instrução em markdown | `.claude/CLAUDE.md` — a guarda fica no script, nunca no modo |

## Critério de aceite

`aprovar()` sobre plano já aprovado devolve o caminho e **não escreve nada** — plano e `_planos.md`
byte-idênticos antes e depois. Plano fora do `_inbox` **sem** `plan_id` não é tratado como aprovado e
segue o caminho normal. Plano no `_inbox` continua com todas as validações de hoje: `core` ausente
levanta, nome inválido levanta, alvo existente levanta.

A norma registra que a etapa 4 do *Fluxo completo* é reentrante, em uma frase, sem recopiar o
docstring.

**A suíte inteira continua verde.**

## Verificação

```
./scripts/test-python.sh .claude/skills/decode-and-code/scripts/tests/test_scaffold_idempotente.py
```

Último resultado: não executado.

## Fonte

- [`0001-decode-and-code-foundation.md`](0001-decode-and-code-foundation.md), *Escopo* → *Correções descobertas na execução*, e `L-17`
- Correção do mecanismo em `de4fc57`, de 2026-08-24 — commit que descreve o impasse e por que a correção veio antes da unidade
