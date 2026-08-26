---
# about
name: developer-agent
type: unit
project: DecodeAndCode
description: O agente de execução nasce sem memória entre execuções — porque agente que lembra corrói o cold-start em silêncio, e a unidade passa a funcionar por memória em vez de por estar completa
tags: [decode-and-code, agent, execucao, sonnet, cold-start]

# alvo
core: model
module: decode-and-code
block: ""
owner: model
unit_id: 0001-20
unit_type: dev

# verificação
state: verified
test: .claude/skills/decode-and-code/scripts/tests/test_agentes.py
verified_at: 2026-08-26

# history
author: Bortoli
created: 2026-08-26
status: draft
version: 1.0.0
updated: ""

# system
scope: project
auto_load: false
dependencies: []
---

# 0001-20 — developer-agent

**Responsabilidade:** entregar o agente que implementa uma unidade em cold-start — `model: sonnet`,
escrita em código e teste — e **sem `memory:`**, que é o campo cuja ausência preserva o critério de
suficiência da unidade.

## Contrato

| Campo | Detalhe |
|---|---|
| **Entrada** | Nenhuma — a unidade entrega uma definição de agente, validada por `lint_agente` |
| **Saída** | `.claude/agents/developer.md` |
| **Auth** | — |
| **Efeito** | Escrita do arquivo do agente e dos casos novos no teste que a `19` criou |
| **Erro** | — |

**O que o agente declara, e o que ele deliberadamente não declara:**

| Campo | Valor | Por quê |
|---|---|---|
| `model` | `sonnet` | É o padrão do `implement` na norma, com override do usuário conforme o escopo |
| `skills` | `[decode-and-code]` | O agente chega sabendo operar o método; a norma continua na norma |
| `tools` | leitura ampla, mais `Write`, `Edit` e `Bash` | Implementar é escrever teste e código, e rodar o gate — sem `Bash` não há `./scripts/test-python.sh` |
| **`memory`** | **ausente** | `D-06`: memória entre execuções faz a unidade funcionar **por lembrança**, e não por estar completa. A insuficiência então só aparece quando outra pessoa a executa |

> **A ausência de `memory:` é o invariante, e ausência não se prova lendo o arquivo com os olhos.**
> Por isso ela vira caso de teste: o campo não pode aparecer no frontmatter, hoje nem depois. É a
> mesma classe da linha órfã `Último resultado`, que a `L-22` tirou do formato e o `lint_unidade`
> passou a recusar para que não voltasse pela mesma porta.

**O executor não commita**, e o agente precisa dizer isso no corpo: quem executa entrega arquivos e
relatório, e versionar é de quem orquestra. É contrato de processo, não preferência.

## Sequência

1. Escrever `.claude/agents/developer.md` — `model: sonnet`, `skills: [decode-and-code]`, `tools` com leitura, escrita e `Bash`.
2. Escrever o corpo na forma medida: papel → processo numerado, espelhando os oito passos do modo `implement` da skill por **referência**, nunca copiando-os.
3. Declarar no corpo os dois contratos de processo: o executor não commita, e unidade insuficiente volta para quem deriva em vez de ser resolvida por conta própria.
4. Acrescentar a `tests/test_agentes.py` os casos do `developer.md`: `lint_agente` limpo, `model: sonnet`, `skills` existente em disco.
5. Acrescentar o caso da ausência de `memory:` — e o caso contrário, com um fixture que **declara** `memory:` e é recusado.
6. Rodar o gate e relatar.

## Arquivos

| Caminho | O que muda |
|---|---|
| `.claude/agents/developer.md` | **novo** — o agente de execução |
| `.claude/skills/decode-and-code/scripts/lint_agente.py` | `memory` entra na lista de campos recusados |
| `.claude/skills/decode-and-code/scripts/tests/test_agentes.py` | casos do `developer.md` e do `memory:` recusado |

## Dependências

A `0001-19`, pelo `lint_agente` e pelo arquivo de teste que ela cria — esta unidade acrescenta
casos a ele em vez de abrir outro. A `0001-18`, pela norma que deixou de pôr agent fora de escopo.

## Normas aplicáveis

| Norma | Onde |
|---|---|
| O agente de desenvolvimento não declara `memory:`, e o porquê | [`0001-decode-and-code-foundation.md`](0001-decode-and-code-foundation.md), `D-06` |
| Cold-start é o critério de suficiência da unidade | [`modelo-dev-units.md`](../../system/modelo-dev-units.md), *Conceitos estruturantes* |
| Sonnet é o padrão no `implement`, com override do usuário | [`modelo-dev-units.md`](../../system/modelo-dev-units.md), seção *Modelos* |
| O executor entrega arquivos e relatório, e não commita | [`CLAUDE.md`](../../../../.claude/CLAUDE.md), *Trabalho novo passa pelo modelo* |

## Critério de aceite

`lint_agente.lint(".claude/agents/developer.md")` devolve `[]`, e o arquivo declara `model: sonnet`
e `skills: [decode-and-code]` — com o teste conferindo que a skill nomeada **existe em disco**.

**`memory:` não aparece no frontmatter do `developer.md`**, e `lint_agente` passa a recusá-lo em
qualquer agente. Os dois casos andam juntos: um afirma a ausência no arquivo real, outro planta
`memory:` num fixture e exige que o lint acuse. Sem o segundo, a recusa poderia nunca ter sido
implementada e o primeiro passaria igual.

O corpo declara os dois contratos de processo — não commitar, e devolver unidade insuficiente a
quem deriva. Cada um é um caso que procura a declaração no corpo.

**A suíte inteira continua verde.**

## Verificação

```
./scripts/test-python.sh .claude/skills/decode-and-code/scripts/tests/test_agentes.py
```

## Fonte

- [`0001-decode-and-code-foundation.md`](0001-decode-and-code-foundation.md), *Escopo* → *Fase 6*
- `D-06` — por que não há `memory:`, e o que ele corroeria
