---
# about
name: commands-travel
type: unit
project: DecodeAndCode
description: O pacote passa a levar .claude/commands/ — /implement e /delegate — e o esqueleto do handoff mais a norma-mecanismo passam a dizer que eles existem
tags: [decode-and-code, plugin, empacotamento, comandos, handoff]

# alvo
core: model
module: installable-method
block: ""
owner: model
unit_id: 0004-06
unit_type: dev

# verificação
state: verified
test: .claude/skills/decode-and-code/scripts/tests/test_empacotamento.py
verified_at: 2026-09-01

# history
author: Bortoli
created: 2026-09-01
status: draft
version: 1.0.0
updated: ""

# system
scope: project
auto_load: false
dependencies: []
---

# 0004-06 — commands-travel

**Responsabilidade:** fazer o pacote levar `.claude/commands/` — `/implement` e `/delegate`, os
dois comandos que disparam cold-start —, e fazer quem orquestra a execução de um plano ficar
sabendo que eles existem.

## Contrato

| Campo | Detalhe |
|---|---|
| **Entrada** | `empacotar.construir(destino)`, mesma assinatura de hoje |
| **Saída** | `construir` devolve os caminhos escritos, agora incluindo os dois arquivos de `.claude/commands/` |
| **Auth** | — |
| **Efeito** | `construir` reescreve a árvore do pacote; `handoff.gerar` passa a incluir uma seção nova no esqueleto |
| **Erro** | Fonte ausente levanta `FileNotFoundError` nomeando-a, antes de escrever — mesmo contrato das demais fontes de `construir` |

### Os comandos são mecanismo, e ainda não viajam

`empacotar._fontes()` leva manifesto, skill, hooks, settings, agents e a norma — não
`.claude/commands/`. Um projeto que instalar o plugin hoje não ganha `/implement` nem `/delegate`,
mesmo eles sendo mecanismo puro: nenhuma marca de instância, prosa que não cita este repositório.
É a mesma lacuna que abriu o plano — *"nenhum caminho para usar"* o que o pacote leva —, só que
num artefato que nasceu depois da derivação (`D-08`).

**`project: DecodeAndCode` no frontmatter dos dois comandos precisa da mesma reescrita que a
`04` já aplica à norma e ao `SKILL.md`.** Sem `_declarar_o_plugin`, a cópia distribuída carrega o
nome deste repositório, e `verificar` acusa — `_marcadores_instancia()` é literalmente
`lib.repo_root().name`.

### Quem orquestra também não sabe

Nem dentro deste repositório: `_handoff.md` — o prompt que `derive` grava para a sessão de
orquestração — não menciona nenhum dos dois comandos, porque `handoff.py` foi escrito antes de
eles existirem. A norma-mecanismo, na seção que descreve o `_handoff.md`, também não. Como os
comandos passam a viajar (Contrato acima), citá-los ali é seguro: os dois mecanismos viajam
juntos, e nenhum cita algo que fica para trás.

## Sequência

1. Acrescentar `"commands": raiz / ".claude" / "commands"` a `empacotar._fontes()`.
2. Escrever `_copiar_comandos`, no mesmo formato de `_copiar_agentes` (copia `*.md` de um
   diretório), com a reescrita de `project:` que `_copiar_norma` já faz por arquivo.
3. Chamar `_copiar_comandos` em `construir`, junto das demais fontes.
4. Acrescentar ao esqueleto de `handoff.py` (`_ESQUELETO`) uma seção curta nomeando os dois
   comandos e quando usar cada um.
5. Acrescentar a mesma informação à norma-mecanismo, na seção que descreve o `_handoff.md`.
6. Escrever os casos novos em `test_empacotamento.py` (comandos no pacote, `project:` reescrito,
   `verificar` continua `[]` contra o repositório real) e em `test_handoff.py` (esqueleto cita os
   dois comandos).
7. Rodar o gate, os dois validadores sobre o pacote real, e a suíte inteira; relatar.

## Arquivos

| Caminho | O que muda |
|---|---|
| `.claude/skills/decode-and-code/scripts/empacotar.py` | `construir` leva `.claude/commands/` |
| `.claude/skills/decode-and-code/scripts/handoff.py` | esqueleto ganha a seção sobre os comandos |
| `docs/plan/system/modelo-dev-units.md` | a seção do `_handoff.md` cita os dois comandos |
| `.claude/skills/decode-and-code/scripts/tests/test_empacotamento.py` | comandos no pacote |
| `.claude/skills/decode-and-code/scripts/tests/test_handoff.py` | esqueleto cita os comandos |

## Dependências

A `0004-04`, por `_declarar_o_plugin` e pelo padrão de `_copiar_norma` que esta unidade reaproveita.
A `0004-03`, porque a seção do `_handoff.md` que esta unidade edita já não carrega instância — citar
os comandos ali não reabre o que a `03` fechou.

## Normas aplicáveis

| Norma | Onde |
|---|---|
| Os comandos viajam como unidade nova, não lacuna adiada | [`0004-installable-method.md`](0004-installable-method.md), `D-08` |
| `project:` reescrito em arquivo copiado, mesmo padrão da norma e do `SKILL.md` | [`0004-installable-method.md`](0004-installable-method.md), Fase 3, unidade `04` |
| `_marcadores_instancia` é o nome do repositório, medido, não hardcoded | [`modelo-dev-units.md`](../../system/modelo-dev-units.md), *Empacotamento — o que o plugin leva, e o que fica* |
| Nada específico de projeto viaja no plugin | `.claude/CLAUDE.md`, *Invariantes não negociáveis*, item 2 |

## Critério de aceite

`empacotar.construir` sobre o **repositório real** produz um pacote que contém
`commands/implement.md` e `commands/delegate.md`, e `empacotar.verificar` sobre essa árvore
continua devolvendo `[]` — os dois arquivos declaram `project: decode-and-code`, nunca o nome deste
repositório.

`handoff.gerar` sobre um plano sintético produz um `_handoff.md` que cita `/implement` **e**
`/delegate` pelo nome.

`modelo-dev-units.md` cita os dois comandos na seção que descreve o `_handoff.md`, sem reabrir
nenhuma marca de instância que a `0004-03` fechou — o teste que a `03` escreveu
(`test_mecanismo_sem_marca_de_instancia_deste_projeto`) continua passando.

**A suíte inteira continua verde**, e `empacotar.validar` continua aprovando o pacote real.

## Verificação

```
./scripts/test-python.sh .claude/skills/decode-and-code/scripts/tests/test_empacotamento.py .claude/skills/decode-and-code/scripts/tests/test_handoff.py
```

## Fonte

- [`0004-installable-method.md`](0004-installable-method.md), *Escopo* → *Fase 3*, `D-08`
- *O que foi medido* — validação dos comandos `/implement` e `/delegate` contra unidades reais
  deste plano, 2026-08-28: nem o pacote nem o `_handoff.md` os mencionavam
