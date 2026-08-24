---
# about
name: principles-rule
type: unit
project: DecodeAndCode
description: Os três princípios fechados na D-03 e o fluxo de decodificação viram regra sempre carregada em .claude/rules/, sem paths: — e nasce o verificador de invariantes de rule que as unidades de guideline reusam
tags: [decode-and-code, principios, rules, camada-normativa, fase-2]

# alvo
core: model
module: decode-and-code
block: ""
owner: model
unit_id: 0001-03
unit_type: dev

# verificação
state: spec
test: .claude/skills/decode-and-code/scripts/tests/test_rules.py
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

# 0001-03 — principles-rule

**Responsabilidade:** fazer a camada de princípio existir como artefato carregado pelo mecanismo
nativo — `.claude/rules/` sem `paths:` —, e dar a ela um oráculo estrutural que não julgue prosa.

## Contrato

| Campo | Detalhe |
|---|---|
| **Entrada** | `rules.lint_rule(path)` recebe o caminho de um arquivo de `.claude/rules/` |
| **Saída** | Lista de problemas — vazia quando o arquivo é uma rule válida, no mesmo padrão de `lint_unidade.lint` e `lint_skill.lint` |
| **Auth** | — |
| **Efeito** | `.claude/rules/principles.md` passa a existir e a carregar em toda sessão, por não declarar `paths:` |
| **Erro** | Caminho inexistente levanta `FileNotFoundError`; arquivo sem frontmatter devolve problema, nunca exceção |

**Invariantes que `lint_rule` verifica** — são de forma, nunca de conteúdo:

| Invariante | Por quê |
|---|---|
| Frontmatter delimitado por `---` e legível por `regioes.ler_campo` | Sem isso o Claude Code não lê o arquivo como rule |
| `name` e `description` presentes e não vazios | `description` é o que o modelo usa para decidir relevância |
| `paths:` **ausente** ⇒ princípio; **presente** ⇒ toda entrada compila como glob | É a única diferença mecânica entre princípio e guideline (plano, *Não inventar ativação*) |
| Corpo não vazio abaixo do frontmatter | Rule vazia carrega e não diz nada — falha silenciosa |

> **O lint não lê o mérito.** Ele afirma que o arquivo é uma rule bem formada e que o `paths:`
> declara o que promete. Se os três princípios são os certos é julgamento humano, e a `L-01` já
> registra que nenhum campo transforma isso em oráculo.

## Sequência

1. Escrever `rules.py` com `lint_rule(path)` — compõe `regioes.ler_campo` para o frontmatter e `fnmatch.translate` + `re.compile` para validar cada entrada de `paths:`. Sem classe, sem estado: uma função e as auxiliares privadas que ela precisar, no estilo de `lint_unidade.py`.
2. Escrever `.claude/rules/principles.md` **sem `paths:`**, com os três princípios da `D-03` — *código é custo*, *subtração antes de adição*, *evidência acima de opinião* —, cada um em uma seção com o enunciado e o teste que o torna aplicável.
3. Acrescentar ao mesmo arquivo o fluxo de decodificação em três estágios — `Clarificar → Evitar → Reduzir` — e os dois gates, conforme a tabela em *Fluxo de decodificação* abaixo. O texto está aqui porque a fonte original não está neste repositório (`L-19`); não inventar estágio nem gate além dos declarados.
4. Escrever `tests/test_rules.py` cobrindo o critério de aceite: a rule real aprova, e cada invariante reprova isoladamente contra fixture sintética montada em `tempfile.TemporaryDirectory()`.
5. Acrescentar a `fixtures.py` o construtor `rule()`, no padrão dos quatro que a `0001-02` entregou — escreve só sob o diretório dado e levanta `ValueError` antes de escrever quando o argumento é inválido.
6. Rodar o gate e relatar. **Não** instalar nada no AmFlow: esta unidade entrega o artefato deste repositório.

**Fluxo de decodificação — o conteúdo normativo, para não ser derivado em cold-start:**

| Estágio | Pergunta que ele faz | Sai daqui quando |
|---|---|---|
| **Clarificar** | O que exatamente foi pedido, e o que foi suposto? | A suposição está declarada ou eliminada |
| **Evitar** | Isto precisa existir? Existe algo que já resolve? | A resposta é sim e nada existente resolve |
| **Reduzir** | Qual é a menor forma que resolve o que sobrou? | Nada mais pode sair sem quebrar o pedido |

| Gate | Onde | Recusa quando |
|---|---|---|
| **A** | Antes de escrever a primeira linha | O estágio *Evitar* não foi respondido — código a caminho sem justificativa de existência |
| **B** | Antes de entregar | O estágio *Reduzir* não foi respondido — há parte da entrega que sai sem quebrar o pedido |

## Arquivos

| Caminho | O que muda |
|---|---|
| `.claude/skills/decode-and-code/scripts/rules.py` | **novo** — `lint_rule(path)` e as auxiliares privadas |
| `.claude/rules/principles.md` | **novo** — os três princípios e o fluxo, sem `paths:` |
| `.claude/skills/decode-and-code/scripts/tests/test_rules.py` | **novo** — o teste declarado |
| `.claude/skills/decode-and-code/scripts/tests/fixtures.py` | acrescenta o construtor `rule()` |

## Dependências

A unidade `0001-02`, pelo `fixtures.py` que ela criou. Não depende da `01` além do que já está em
disco.

## Normas aplicáveis

| Norma | Onde |
|---|---|
| Camada normativa — princípio, guideline, guardrail, referência | [`modelo-dev-units.md`](../../system/modelo-dev-units.md), seção *Camada normativa* |
| O teste que separa princípio de guideline | [`0001-decode-and-code-foundation.md`](0001-decode-and-code-foundation.md), seção *Princípio e guideline separam-se por um teste* |
| `D-03` — a lista de três está fechada | [`0001-decode-and-code-foundation.md`](0001-decode-and-code-foundation.md), seção *Decisões* |
| `L-01` — o que oráculo estrutural prova, e o que não prova | [`0001-decode-and-code-foundation.md`](0001-decode-and-code-foundation.md), seção *Lacunas* |
| Nada específico de projeto viaja no plugin | `.claude/CLAUDE.md`, invariante 2 |
| Simplicidade primeiro | `.claude/CLAUDE.md` — uma função, sem abstração para uso único |

## Critério de aceite

`.claude/rules/principles.md` existe, **não declara `paths:`**, e `rules.lint_rule()` devolve `[]`
sobre ele. Os três princípios da `D-03` estão presentes, nenhum a mais — quatro princípios é a
formulação que a `D-03` rejeitou. O fluxo tem exatamente três estágios e dois gates.

Cada invariante reprova isoladamente: rule sem `description` devolve problema, rule com `paths:`
declarando glob inválido devolve problema, rule com corpo vazio devolve problema. Nenhum desses
casos levanta exceção — o lint devolve lista, como os outros dois do repositório.

**A suíte inteira continua verde**, e nenhum teste existente é alterado: esta unidade só acrescenta.

## Verificação

```
./scripts/test-python.sh .claude/skills/decode-and-code/scripts/tests/test_rules.py
```

Último resultado: não executado.

## Fonte

- [`0001-decode-and-code-foundation.md`](0001-decode-and-code-foundation.md), *Escopo* → Fase 2, `D-03` e a seção *Não inventar ativação*
- Mecanismo nativo confirmado na medição de 2026-08-22 sobre a doc do Claude Code: `.claude/rules/` com frontmatter `paths:`, e sem `paths:` a rule carrega sempre
- O fluxo de decodificação vem da guideline `decode_code` de `futureridetoday/CortexMachine`, **que não está em disco** — o texto acima é derivação a partir do que o plano descreve, e a `L-19` registra isso
