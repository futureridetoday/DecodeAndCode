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
state: verified
test: .claude/skills/decode-and-code/scripts/tests/test_rules.py
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
3. Acrescentar ao mesmo arquivo o fluxo de decodificação e os dois gates, **conforme as tabelas abaixo** — que são transcrição da fonte, não derivação. Não inventar estágio nem gate, e não trazer os Gates 1–5: os limites numéricos vêm de outro domínio e o plano os recusou.
4. Acrescentar o protocolo de exceção — os cinco gatilhos e o registro mínimo, conforme *Protocolo de exceção* abaixo. **Sem a governança da fonte:** Architecture Council, SLA em horas, matriz de risco e pipeline de aprendizado são instância do CortexMachine, e o invariante 2 os mantém fora.
5. Escrever `tests/test_rules.py` cobrindo o critério de aceite: a rule real aprova, e cada invariante reprova isoladamente contra fixture sintética montada em `tempfile.TemporaryDirectory()`.
6. Acrescentar a `fixtures.py` o construtor `rule()`, no padrão dos quatro que a `0001-02` entregou — escreve só sob o diretório dado e levanta `ValueError` antes de escrever quando o argumento é inválido.
7. Rodar o gate e relatar. **Não** instalar nada no AmFlow: esta unidade entrega o artefato deste repositório.

**Os três princípios — as formulações da fonte, que são mais afiadas que a taquigrafia da `D-03`:**

| Princípio | Formulação |
|---|---|
| **Código é custo** | Só existe se eliminar dor real e mensurável |
| **Subtração primeiro** | `remover > reduzir > reaproveitar > criar` |
| **Evidência acima de opinião** | Decisão baseada em dado simples, não em estética |

> A fonte tem **quatro**; o quarto — *"solução mínima vence: se 50 linhas resolvem, 500 é erro"* —
> foi cortado pela `D-03` por redundância com *subtração primeiro*. Conferido contra a fonte em
> 2026-08-24: o corte procede, e a cadeia `remover > reduzir > reaproveitar > criar` já carrega o
> que o quarto dizia.

**Fluxo de decodificação — transcrito de `decode_code_foundation.md`:**

| Passo | Perguntas obrigatórias | Saída esperada |
|---|---|---|
| **Clarificar** | Problema + métrica + beneficiário em 1 frase | Frase clara e mensurável |
| **Evitar** | Posso resolver sem código — config, processo, doc ou reuso? | Lista de alternativas |
| **Reduzir** | Qual é a menor versão que resolve 80% agora? | Escopo mínimo viável |

| Gate | Critério |
|---|---|
| **A — necessidade real** | Há impacto mensurável **agora**? |
| **B — mínimo viável** | Há como reduzir linhas, arquivos ou dependências? |

> **Gate é critério, não posição no tempo.** A e B são as duas perguntas que barram avanço; não são
> "antes de escrever" e "antes de entregar". A formulação anterior desta unidade os descrevia como
> posições, e estava errada — corrigida contra a fonte em 2026-08-24 (`L-19`).

**Protocolo de exceção — os cinco gatilhos, sem a governança da fonte:**

Pede-se exceção quando, e só quando: a regra é **inviável** no contexto; há **trade-off crítico** não
coberto; é **edge case** com risco operacional ou de compliance; há **conflito** entre normas ativas;
ou há **exigência explícita** do humano. O registro mínimo nomeia a regra, o que já foi tentado, o
que se propõe no lugar, e quem aprovou.

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
- **Fonte primária, lida em 2026-08-24** em `CortexMachine`, clonado localmente: `guidelines/decode_code/decode_code_foundation.md` (fundamentação, fluxo em `:204-212`, Gates A/B em `:222-224`), `guidelines/decode_code/decode_code_essentials.md` (os quatro princípios operacionais, `:26-38`) e `guidelines/guidelines_ml.md` (protocolo HITL, `:10-28`) — os cinco gatilhos de exceção saem daí
- **Recusados por serem instância de outro domínio:** os Gates 1–5 com limites numéricos (≤120L, ≤3 componentes, ≤6-8 fases, ≤10 regras), o catálogo de padrões Python de ML/scheduler, e a governança do protocolo HITL — Architecture Council, SLA de 2h–72h, matriz de risco e pipeline de aprendizado
