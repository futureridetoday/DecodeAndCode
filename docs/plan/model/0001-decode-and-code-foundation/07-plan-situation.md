---
# about
name: plan-situation
type: unit
project: DecodeAndCode
description: A situação projetada em _planos.md passa a medir o plano, não só as unidades derivadas — plano com unidade prevista e não derivada nunca projeta concluído, e o check de concorrência volta a enxergar
tags: [decode-and-code, backlog, projecao, concorrencia, l-18]

# alvo
core: model
module: decode-and-code
block: ""
owner: model
unit_id: 0001-07
unit_type: dev

# verificação
state: verified
test: .claude/skills/decode-and-code/scripts/tests/test_situacao.py
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

# 0001-07 — plan-situation

**Responsabilidade:** impedir que um plano com trabalho previsto e não derivado seja projetado como
`concluído` — e, com isso, devolver visão ao check de concorrência, que hoje fica cego exatamente
nesse estado.

## Contrato

| Campo | Detalhe |
|---|---|
| **Entrada** | `backlog.projetar(dir_plano)` — mesma assinatura de hoje |
| **Saída** | A tupla `(miolo, situacao)` de hoje, com `situacao` passando a considerar o escopo declarado do plano |
| **Auth** | — |
| **Efeito** | A linha do plano em `_planos.md` só recebe `concluído` quando **não há unidade prevista fora de `verified`** |
| **Erro** | Plano sem escopo declarado legível: `situacao` cai no comportamento de hoje e o rodapé diz que o total é desconhecido — **nunca** levanta, e nunca projeta `concluído` por não saber |

**O defeito, medido em 2026-08-24:**

Ao fechar a `0001-02`, `projetar` levou a situação a `concluído` com quinze unidades por derivar. A
região `planos` ficou **sem nenhuma linha `em desenvolvimento`** — que é o que o check de concorrência
do modo `review` varre para decidir se há trabalho concorrente no mesmo core ou módulo. Um plano novo
em `model`/`decode-and-code` teria passado num check que deveria sinalizá-lo.

> **Não é ocorrência única.** Repete a cada fronteira em que todas as unidades derivadas estão
> verificadas e ainda há trabalho previsto — que é o estado normal da derivação incremental que a
> `D-12` adotou.

## Sequência

1. Ler a tabela `## Escopo` do plano e contar as unidades **previstas** — as linhas que declaram número e responsabilidade, em todas as tabelas da seção, incluindo as de correções fora de fase.
2. `projetar` passa a comparar previstas com derivadas: `concluído` só quando as duas coincidem **e** todas as derivadas estão `verified`. Qualquer outro estado é `em desenvolvimento`.
3. O rodapé do backlog passa a dizer **"N de M derivadas"**, com `M` vindo do escopo — hoje ele diz "N de N" e é o mesmo defeito por outro ângulo, registrado como custo aceito na `D-12`.
4. Escopo ilegível ou ausente **não** é erro: o rodapé diz que o total é desconhecido, e a situação nunca é `concluído`. Falhar fechado aqui é correto — projetar `concluído` por não conseguir contar é a falha que a unidade existe para impedir.
5. Escrever `tests/test_situacao.py` cobrindo o critério de aceite, com planos sintéticos montados por `fixtures.plano()` em `tempfile.TemporaryDirectory()`.
6. Rodar o gate, reprojetar o plano `0001` e conferir que a linha dele volta a `em desenvolvimento` com o total correto. Relatar.

## Arquivos

| Caminho | O que muda |
|---|---|
| `.claude/skills/decode-and-code/scripts/backlog.py` | contagem do escopo; `situacao`; rodapé "N de M" |
| `.claude/skills/decode-and-code/scripts/tests/test_situacao.py` | **novo** — o teste declarado |
| `.claude/skills/decode-and-code/scripts/tests/fixtures.py` | `plano()` passa a aceitar um escopo com unidades previstas |
| `.claude/skills/decode-and-code/scripts/tests/test_backlog.py` | os testes de rodapé que assumem "N de N" |

## Dependências

A unidade `0001-02`, pelo `fixtures.py`.

## Normas aplicáveis

| Norma | Onde |
|---|---|
| A situação é projetada, nunca digitada | [`modelo-dev-units.md`](../../system/modelo-dev-units.md), seção *Tabela de planos* |
| Regiões — quem escreve o quê | [`modelo-dev-units.md`](../../system/modelo-dev-units.md), seção *Regiões* |
| O check de concorrência do `review`, e o que ele varre | [`modelo-dev-units.md`](../../system/modelo-dev-units.md), seção *Modo `review`* |
| `D-12` — o custo do rodapé "N de N", aceito e agora pago | [`0001-decode-and-code-foundation.md`](0001-decode-and-code-foundation.md), seção *Decisões* |
| `state` e `verified_at` nunca se editam à mão | `.claude/CLAUDE.md`, invariante 3 |

## Critério de aceite

Plano com unidade prevista e não derivada projeta **`em desenvolvimento`**, mesmo com todas as
derivadas em `verified`. Plano com todas as previstas derivadas e verificadas projeta `concluído`.
Plano sem escopo legível projeta `em desenvolvimento` e diz no rodapé que o total é desconhecido —
**nunca** `concluído`.

O rodapé diz "N de M derivadas" com `M` vindo do escopo declarado.

Reprojetado o plano `0001` real, a linha dele em `_planos.md` diz `em desenvolvimento`, e a região
volta a ter linha que o check de concorrência enxerga.

**A suíte inteira continua verde**, e os testes de rodapé existentes são atualizados, não removidos.

## Verificação

```
./scripts/test-python.sh .claude/skills/decode-and-code/scripts/tests/test_situacao.py
```

## Fonte

- [`0001-decode-and-code-foundation.md`](0001-decode-and-code-foundation.md), *Escopo* → *Correções descobertas na execução*, e `L-18`
- Defeito medido em 2026-08-24, ao fechar a `0001-02`: situação `concluído` com quinze unidades por derivar, e zero linhas `em desenvolvimento` na região `planos`
