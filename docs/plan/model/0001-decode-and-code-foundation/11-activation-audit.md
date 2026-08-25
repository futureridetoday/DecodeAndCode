---
# about
name: activation-audit
type: unit
project: DecodeAndCode
description: O que a validação por sessão provou vira gate onde dá e procedimento onde não dá — a árvore de rules ganha check estrutural, e o log de ativação ganha relatório que diz o que carregou e por quê
tags: [decode-and-code, rules, validacao, observabilidade, l-27]

# alvo
core: model
module: decode-and-code
block: ""
owner: model
unit_id: 0001-11
unit_type: dev

# verificação
state: verified
test: .claude/skills/decode-and-code/scripts/tests/test_auditoria.py
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

# 0001-11 — activation-audit

**Responsabilidade:** impedir que o defeito da `L-26` volte, e tornar repetível a validação que o
encontrou — hoje ela existe como resultado, e o procedimento está só numa conversa.

## Contrato

| Campo | Detalhe |
|---|---|
| **Entrada** | `rules.auditar_arvore()` sem argumento; `activation_notice.relatorio(caminho_log)` |
| **Saída** | `auditar_arvore` devolve lista de problemas, vazia quando a árvore está sã. `relatorio` devolve uma linha por instrução carregada, com caminho, motivo e o veredito de cada uma |
| **Auth** | — |
| **Efeito** | Nenhum — as duas **só leem**. Auditoria que corrige sozinha esconde o defeito que deveria mostrar |
| **Erro** | Log inexistente levanta `FileNotFoundError`; linha ilegível no log entra no relatório marcada, nunca derruba a leitura |

**O que `auditar_arvore` recusa:**

| Problema | Por quê |
|---|---|
| `.md` em **qualquer subdiretório** de `.claude/rules/` | É a `L-26` inteira: o matcher recursa, então subdiretório não desliga nada e a norma segue ativa com `listar()` dizendo o contrário |
| `.md` em `.claude/rules/` que reprova em `lint_rule` | Rule malformada carrega e não diz nada |
| `.md` em `.claude/rules-off/` que reprova em `lint_guideline` | Guideline desligada volta a ser ligada um dia; se estiver quebrada, o defeito espera lá dentro |

**O que `relatorio` sinaliza sobre um log de sessão:**

| Sinal | Significa |
|---|---|
| Rule **com** `paths:` carregada por `session_start` | O escopo não está sendo respeitado — custo de contexto que `paths:` existe para evitar |
| Caminho carregado que está sob `.claude/rules-off/` | Desligar não desligou — a `L-26` de volta |
| Caminho carregado em **subdiretório** de `.claude/rules/` | A forma **histórica** da `L-26`. `auditar_arvore` a pega estruturalmente, mas só quando a suíte roda; em sessão quem vê é o relatório |
| Duas rules com `paths:` casando o mesmo arquivo | A condição de colisão da `L-05`, que hoje ninguém detecta |

> **A auditoria não abre sessão, e é por isso que ela não fecha o problema sozinha.** Abrir sessão e
> tocar um arquivo são atos humanos; o que esta unidade faz é tirar o julgamento de quem lê o log.

## Sequência

1. Estender `rules.py` com `auditar_arvore()` — varre `.claude/rules/` e `.claude/rules-off/`, aplica a tabela de recusas acima, devolve lista no padrão dos outros lints do repositório.
2. Estender `activation_notice.py` com `relatorio(caminho_log)` — lê o log por sessão que `instructions_loaded.py` escreve, e devolve uma linha por instrução com os sinais da segunda tabela. Só leitura, nada de escrita.
3. Escrever a seção **Validar a ativação** na norma, dentro de *Camada normativa*: os dois atos humanos — abrir sessão nova, tocar um arquivo do escopo — e o comando que roda o relatório. Curta, porque o julgamento saiu dela e foi para o código.
4. Registrar na mesma seção o **controle de três estados** que provou a `L-26`: guideline ligada produz entrada; em subdiretório produz entrada; em diretório irmão não produz. É o padrão que qualquer projeto instalando o plugin repete para validar a própria camada.
5. Escrever `tests/test_auditoria.py` cobrindo o critério de aceite: a árvore real aprova, e cada recusa dispara isoladamente contra árvore sintética montada em `tempfile.TemporaryDirectory()`. Logs sintéticos exercitam os três sinais do `relatorio`.
6. Acrescentar a `fixtures.py` o construtor `log_ativacao()`, que escreve um log sintético — artefato de teste nasce lá (`L-21`).
7. Rodar o gate e relatar, incluindo a saída de `auditar_arvore()` contra a árvore real deste repositório.

## Arquivos

| Caminho | O que muda |
|---|---|
| `.claude/skills/decode-and-code/scripts/rules.py` | acrescenta `auditar_arvore()` |
| `.claude/skills/decode-and-code/scripts/activation_notice.py` | acrescenta `relatorio(caminho_log)` |
| `docs/plan/system/modelo-dev-units.md` | seção *Validar a ativação*, dentro de *Camada normativa* |
| `.claude/skills/decode-and-code/scripts/tests/test_auditoria.py` | **novo** — o teste declarado |
| `.claude/skills/decode-and-code/scripts/tests/fixtures.py` | acrescenta `log_ativacao()` |

## Dependências

A `0001-05`, pelo formato do log e pelo `activation_notice`. A `0001-09` e a `0001-10`, pelos lints
de rule e pela árvore que a auditoria varre.

## Normas aplicáveis

| Norma | Onde |
|---|---|
| Camada normativa, manifesto de guideline e a operação de ligar/desligar | [`modelo-dev-units.md`](../../system/modelo-dev-units.md), seção *Camada normativa* |
| `L-26` — o subdiretório que não desligava, e como apareceu | [`0001-decode-and-code-foundation.md`](0001-decode-and-code-foundation.md), seção *Lacunas* |
| `L-05` — a colisão só existe com duas rules com escopo | [`0001-decode-and-code-foundation.md`](0001-decode-and-code-foundation.md), seção *Lacunas* |
| As seis medições, e o que cada uma provou | [`0001-decode-and-code-foundation.md`](0001-decode-and-code-foundation.md), seção *Validação de ponta a ponta* |
| Código, não instrução em markdown | `.claude/CLAUDE.md` — o julgamento sai do procedimento e vira função |

## Critério de aceite

`rules.auditar_arvore()` devolve `[]` contra a árvore real deste repositório, e **recusa
isoladamente** cada caso da tabela: um `.md` num subdiretório de `.claude/rules/`, uma rule
malformada em `.claude/rules/`, e uma guideline quebrada em `.claude/rules-off/`.

**O caso do subdiretório é o que esta unidade existe para gatear**, e o teste o monta reproduzindo a
forma exata da `L-26` — `rules/_off/<guideline>.md`.

`activation_notice.relatorio()` sinaliza os três casos da segunda tabela contra logs sintéticos, e
devolve linha marcada — nunca levanta — para linha ilegível. Log inexistente levanta
`FileNotFoundError`.

A norma ganha *Validar a ativação* com os dois atos humanos, o comando do relatório, e o controle de
três estados. **Nenhuma das seis medições é recopiada** — a seção aponta para *Validação de ponta a
ponta*, que é onde os resultados vivem.

**A suíte inteira continua verde.**

## Verificação

```
./scripts/test-python.sh .claude/skills/decode-and-code/scripts/tests/test_auditoria.py
```

Último resultado: não executado.

## Fonte

- [`0001-decode-and-code-foundation.md`](0001-decode-and-code-foundation.md), *Escopo* → *Correções descobertas na execução*, e `L-27`
- `L-26`, medida em 2026-08-24 e reteste em 2026-08-25: o subdiretório carregava, o diretório irmão não
- As seis medições de *Validação de ponta a ponta*, cujo procedimento esta unidade transforma em artefato
