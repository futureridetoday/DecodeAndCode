---
# about
name: method-brief
type: unit
project: DecodeAndCode
description: dc.py explicar imprime, da norma, as quatro seções que sustentam o princípio Decode → Code, para a skill explicar o método sem texto próprio que possa divergir
tags: [decode-and-code, setup, metodo, dc-py]

# alvo
core: model
module: onboard-new-project
block: ""
owner: model
unit_id: 0009-04
unit_type: dev

# verificação
state: verified
test: .claude/skills/decode-and-code/scripts/tests/test_explicar.py
verified_at: 2026-11-16

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

# 0009-04 — method-brief

**Responsabilidade:** entregar à skill `setup` o texto da norma que explica o método — uma fonte
por fato: a skill explica a partir do que a norma diz, nunca de prosa própria.

## Contrato

| Campo | Detalhe |
|---|---|
| **Entrada** | `normas.secoes(arquivo: Path, nomes: tuple[str, ...])`; no `dc.py explicar`, sem argumento |
| **Saída** | `secoes` → lista de `(titulo, trecho)`, na ordem de `nomes`. `explicar` imprime cada uma como `### <caminho relativo> § <título>` seguido do trecho, no padrão do `dc.py normas` |
| **Auth** | — |
| **Efeito** | Só leitura |
| **Erro** | Seção ausente: `ValueError` nomeando quais faltam, e `explicar` sai `2` |

**As quatro seções**, buscadas por prefixo de título com `normas._buscar` (`normas.py:110-138`),
numa constante do `dc.py` como `_SECOES_DO_FECHO`:

1. `Antes do plano` — Clarificar → Evitar → Reduzir e os gates A e B
2. `O que cada porte carrega` — o porte medido pelo tamanho do problema
3. `Cold-start é o critério de suficiência da unidade`
4. `Skills \`review-plan\`, \`derive\` e \`implement\`` — prefixo, para continuar resolvendo depois que a `0009-07` tirar o "— substituem `plan-dev-units`" do título

**Qual norma:** a de `bootstrap._fonte_norma()` (`bootstrap.py:83-107`) — o `reference/` do pacote
primeiro, depois a do `plan_root` deste checkout. É a norma do método, não a cópia materializada do
projeto, que pode ser anterior.

## Sequência

1. Escrever `tests/test_explicar.py`: a norma real devolve as quatro; uma norma sintética sem uma delas levanta `ValueError` que a nomeia.
2. `normas.secoes`, sobre `_buscar`, levantando com a lista do que faltou.
3. O subcomando `explicar` no `dc.py`, em `SUBCOMANDOS` de `tests/test_dc.py`, com um caso que confere os quatro títulos na saída.
4. Rodar o teste declarado e a suíte inteira.

## Arquivos

| Caminho | O que muda |
|---|---|
| `.claude/skills/decode-and-code/scripts/normas.py` | `secoes` |
| `.claude/skills/decode-and-code/scripts/tests/test_explicar.py` | **novo** — o teste declarado |
| `.claude/skills/decode-and-code/scripts/dc.py` | constante, handler e entrada no `_parser`; `_huddle_fecho` é o modelo |
| `.claude/skills/decode-and-code/scripts/tests/test_dc.py` | `SUBCOMANDOS` e um caso |

## Dependências

Nenhuma unidade deste plano. A `0009-07` muda o título da quarta seção e depende de o prefixo
continuar resolvendo.

## Normas aplicáveis

| Norma | Onde |
|---|---|
| Etapa 5 do fluxo: o que o Decode e o Code explicam | [`0009-onboard-new-project.md`](0009-onboard-new-project.md), seção *O fluxo* |
| A explicação descreve só o que existe | [`0009-onboard-new-project.md`](0009-onboard-new-project.md), seção *Decisões* |
| Uma fonte por fato | [`modelo-dev-units.md`](../../system/modelo-dev-units.md), seção *Camada normativa* |

## Critério de aceite

`dc.py explicar` imprime os quatro títulos e os trechos da norma do método; removida qualquer uma
das quatro seções de uma norma de teste, `normas.secoes` levanta `ValueError` que nomeia a que
faltou. **A suíte inteira continua verde.**

## Verificação

```
./scripts/test-python.sh .claude/skills/decode-and-code/scripts/tests/test_explicar.py
```

## Fonte

- [`0009-onboard-new-project.md`](0009-onboard-new-project.md), *Escopo* → *Fase 1*, unidade 04
