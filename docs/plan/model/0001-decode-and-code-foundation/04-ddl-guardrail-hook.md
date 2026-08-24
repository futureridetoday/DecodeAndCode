---
# about
name: ddl-guardrail-hook
type: unit
project: DecodeAndCode
description: O mecanismo de guardrail passa a existir — hook PreToolUse que casa a ferramenta por regex e inspeciona o conteúdo do comando, recusando DDL em ambiente remoto e deixando passar SELECT diagnóstico
tags: [decode-and-code, guardrail, hook, pre-tool-use, fase-2]

# alvo
core: model
module: decode-and-code
block: ""
owner: model
unit_id: 0001-04
unit_type: dev

# verificação
state: spec
test: .claude/skills/decode-and-code/scripts/tests/test_guardrail.py
verified_at: ""

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

# 0001-04 — ddl-guardrail-hook

**Responsabilidade:** provar que a camada de guardrail impõe de verdade — um hook que lê o payload
de `PreToolUse`, casa a ferramenta por regex, **inspeciona o conteúdo** do comando e recusa o caso
proibido, deixando passar o diagnóstico.

## Contrato

| Campo | Detalhe |
|---|---|
| **Entrada** | Payload JSON de `PreToolUse` em stdin — `tool_name` e `tool_input`, conforme a referência de hooks |
| **Saída** | JSON em stdout com a decisão. Recusa nomeia **qual regra** recusou e **por quê**; liberação é silenciosa |
| **Auth** | — |
| **Efeito** | Comando que casa a regra não chega a executar |
| **Erro** | **Falha aberta.** Payload ilegível, regra que levanta, ou qualquer exceção interna ⇒ libera e reporta em stderr. Guardrail que trava o trabalho por defeito próprio é o obstáculo que a norma manda evitar |

**A fronteira mecanismo / instância, que é o que decide o desenho:**

| Camada | O que é | Onde vive |
|---|---|---|
| **Mecanismo** | Ler payload, casar ferramenta por regex, aplicar uma lista de regras ao conteúdo, montar a decisão | `guardrail.py` — viaja no plugin |
| **Instância** | *"DDL em ambiente remoto é recusado"*, e o statement que a prova | Arquivo de regras do projeto — **não** viaja (invariante 2) |

> **Nenhum projeto que instale o plugin herda uma regra sobre banco de dados.** A Fase 5 empacota o
> mecanismo; esta unidade escreve a instância porque ela é o **campo de prova**, e prova mais que
> qualquer página de norma sobre hooks.

## Sequência

1. Escrever `guardrail.py`: lê o payload de stdin, resolve `tool_name` contra o regex de cada regra declarada e aplica as que casarem ao conteúdo de `tool_input`. Devolve decisão estruturada; **nunca** levanta para fora — exceção interna vira liberação com aviso em stderr.
2. Declarar as regras em arquivo próprio do projeto, carregado por `guardrail.py` — não embutidas no código do mecanismo. Uma regra é: regex de ferramenta, detector de conteúdo, e a mensagem de recusa.
3. Escrever o detector de DDL **ancorado no statement**, nunca em substring: casa o verbo no início de statement (após `;` ou início do texto, ignorando espaço e comentário), nunca a palavra solta no meio de uma string ou de um `SELECT`.
4. Escrever `.claude/hooks/pre_tool_use.py` como o ponto de entrada que o `settings.json` invoca, delegando a `guardrail.py`. O ponto de entrada não decide nada — só liga stdin e stdout ao mecanismo.
5. Registrar o hook em `.claude/settings.json`, no evento `PreToolUse`. **Barato por construção:** ele roda em toda chamada de ferramenta, então nada de I/O além da leitura do arquivo de regras, e nada de import pesado.
6. Escrever `tests/test_guardrail.py` cobrindo o critério de aceite, com os três casos que separam mecanismo de acidente: o DDL real recusado, o `SELECT` diagnóstico liberado, e o `SELECT` que **contém a palavra** do verbo liberado.
7. Rodar o gate e relatar. **Não instalar no AmFlow** — instalar lá é consequência reportada, item do backlog daquele repositório, nunca gate desta unidade.

## Arquivos

| Caminho | O que muda |
|---|---|
| `.claude/skills/decode-and-code/scripts/guardrail.py` | **novo** — o mecanismo |
| `.claude/hooks/pre_tool_use.py` | **novo** — ponto de entrada, sem lógica de decisão |
| `.claude/guardrails.json` | **novo** — as regras deste projeto; é instância, não viaja no plugin |
| `.claude/settings.json` | acrescenta o bloco `hooks` com `PreToolUse` |
| `.claude/skills/decode-and-code/scripts/tests/test_guardrail.py` | **novo** — o teste declarado |

## Dependências

Nenhuma unidade. Depende de `.claude/settings.json`, que já existe e hoje só declara `permissions`.

## Normas aplicáveis

| Norma | Onde |
|---|---|
| O pipeline princípio → guideline → guardrail | [`0001-decode-and-code-foundation.md`](0001-decode-and-code-foundation.md), seção *O pipeline completo, na instância que tem incidente registrado* |
| Ancorar no statement, nunca em substring | mesma seção — e a `L-02` do `AmFlow:0006`, que registra o defeito da mesma classe |
| `PreToolUse` roda em toda chamada: barato, e falha fechada trava o trabalho | [`0001-decode-and-code-foundation.md`](0001-decode-and-code-foundation.md), seção *Restrições conhecidas* |
| `D-07` — guardrail fica no projeto, não no frontmatter do agente | [`0001-decode-and-code-foundation.md`](0001-decode-and-code-foundation.md), seção *Decisões* |
| Nada específico de projeto viaja no plugin | `.claude/CLAUDE.md`, invariante 2 |
| Guardrail fundador — o que é guardrail, e por que é verificável | [`modelo-dev-units.md`](../../system/modelo-dev-units.md), seção *Guardrail fundador* |

## Critério de aceite

O hook recusa o statement de DDL do incidente e libera o `SELECT` diagnóstico. **O terceiro caso é o
que prova o mecanismo, e não pode faltar:** um `SELECT` cujo texto contém o verbo do DDL — em nome de
coluna, em literal, ou em comentário — é **liberado**. Casar substring reprovaria os três, e passaria
por guardrail funcionando.

Payload malformado, arquivo de regras ausente e regra que levanta exceção **liberam**, cada um com
aviso em stderr. Nenhum desses casos bloqueia, e nenhum levanta para fora do hook.

`guardrail.py` não contém o nome de nenhum serviço, tabela ou projeto: o que ele conhece é a forma de
uma regra. Toda instância está em `.claude/guardrails.json`.

**A suíte inteira continua verde**, e nenhum teste existente é alterado.

## Verificação

```
./scripts/test-python.sh .claude/skills/decode-and-code/scripts/tests/test_guardrail.py
```

Último resultado: não executado.

## Fonte

- [`0001-decode-and-code-foundation.md`](0001-decode-and-code-foundation.md), *Escopo* → Fase 2, e `D-02`
- **O statement do incidente está no AmFlow, e é somente leitura daqui.** Registrado em
  `AmFlow:docs/plan/_inbox/notification-fk.md` e em
  `AmFlow:docs/plan/hub/0004-close-surface-split/gate-encerramento-2026-08-12.md`, localizados em
  2026-08-24. Copiar o statement para o fixture é leitura de lá, nunca escrita — e a `L-20` registra
  que o fixture depende de um repositório externo
- Catálogo de eventos de hook e canais de saída, medido em 2026-08-22 sobre a doc do Claude Code
