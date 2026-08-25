---
# about
name: guideline-manifest
type: unit
project: DecodeAndCode
description: O que é uma guideline — manifesto com campos exigidos, semântica de paths: e a fronteira contra skill —, mais a primeira guideline que ativa de verdade neste repositório
tags: [decode-and-code, guideline, rules, camada-normativa, fase-3]

# alvo
core: model
module: decode-and-code
block: ""
owner: model
unit_id: 0001-09
unit_type: dev

# verificação
state: spec
test: .claude/skills/decode-and-code/scripts/tests/test_guideline.py
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

# 0001-09 — guideline-manifest

**Responsabilidade:** dar forma verificável à segunda camada — o que uma guideline **é**, o que a
separa de skill, e uma instância que **ativa de verdade aqui**, não apenas valida.

## Contrato

| Campo | Detalhe |
|---|---|
| **Entrada** | `rules.lint_guideline(path)` — o caminho de uma rule que declara `paths:` |
| **Saída** | Lista de problemas; vazia quando o arquivo é uma guideline válida |
| **Auth** | — |
| **Efeito** | A primeira guideline passa a existir em `.claude/rules/` e a ativar na leitura de arquivo que casa o glob |
| **Erro** | Sem `paths:` devolve problema — é princípio, não guideline; `paths:` presente e vazio idem |

**O que `lint_guideline` verifica além do que `lint_rule` já faz:**

| Invariante | Por quê |
|---|---|
| `paths:` presente e não vazio | Guideline sem escopo é princípio mal rotulado, e rótulo errado é o defeito que o plano persegue |
| Cada entrada compila como glob | Já coberto por `lint_rule`; aqui é pré-requisito, não repetição |
| **Ao menos uma entrada casa arquivo que existe no repositório** | Guideline que não casa nada nunca ativa, e falha **silenciosa e indistinguível de sucesso** — é o modo de falha que a `05` existe para expor |
| `description` diz **quando** vale, não o que ensina | É o texto que decide relevância; descrição de conteúdo não ajuda a decidir escopo |

> **O terceiro invariante é o que esta unidade acrescenta de verdade.** Validar frontmatter a `03` já
> faz. Afirmar que o escopo **alcança alguma coisa** é o que separa guideline viva de arquivo bem
> formado e inerte.

## Sequência

1. Estender `rules.py` com `lint_guideline(path)` — compõe `lint_rule` e acrescenta os invariantes da tabela. Casamento de glob contra o disco usa `Path.glob`, resolvido a partir de `lib.repo_root()`.
2. Escrever a seção **Guideline** na norma, dentro de *Camada normativa* — campos exigidos, semântica de `paths:`, e a regra de que **guideline é instância e nunca viaja no plugin** (invariante 2). Estender a seção que já existe, nunca criar documento paralelo.
3. Escrever a fronteira **skill × guideline** na mesma seção, com o teste que a decide: *skill é invocada; guideline é ativada*. O material medido é a `AmFlow:hub-front` — 547 linhas, §1–7 e §9 normativas, §8 procedimento —, citada como **caso**, sem copiar conteúdo dela para cá.
4. Escrever a primeira guideline real em `.claude/rules/`, com `paths:` que **casa arquivo existente neste repositório** — ver *A instância de prova* abaixo.
5. Escrever `tests/test_guideline.py` cobrindo o critério de aceite: a guideline real aprova, e cada invariante reprova isoladamente contra fixture sintética em `tempfile.TemporaryDirectory()`.
6. Acrescentar a `fixtures.py` o parâmetro que faz `rule()` emitir `paths:` — o construtor já existe desde a `03`, e é onde artefato de teste nasce (`L-21`).
7. Rodar o gate e relatar. **Nenhuma escrita no AmFlow:** extrair a `hub-front` de lá é consequência reportada, item do backlog daquele repositório, nunca gate desta unidade.

**A instância de prova — e por que ela não é a `hub-front`:**

O plano previa usar o conteúdo da `hub-front` como material da instância. **Como guideline viva aqui
ela não serve, e a razão é mecânica:** o escopo dela é `hub/app/**`, que não existe neste
repositório. Ela validaria e nunca ativaria — exatamente o modo de falha que o terceiro invariante
acima recusa, entregue pela própria unidade que o define.

A `hub-front` fica onde é útil: como **caso medido** da fronteira do passo 3, que é o papel para o
qual o plano a nomeou — *"norma com escopo, vestida de skill"*.

A guideline viva carrega a **norma operativa de escrita de script**, com `paths:` casando os `.py`
deste repositório. E o corte segue o padrão que a `03` já estabeleceu: **a rule carrega o operativo,
o documento de `docs/plan/system/` carrega evidência e racional**, citado — nunca as duas coisas nos
dois lugares (invariante 1). O `language-policy.md` mantém a medição de ambientes e o porquê; a
guideline diz o que vale ao escrever um `.py`, e é o que entra em contexto quando alguém abre um.

## Arquivos

| Caminho | O que muda |
|---|---|
| `.claude/skills/decode-and-code/scripts/rules.py` | acrescenta `lint_guideline(path)` |
| `.claude/rules/scripts.md` | **novo** — a primeira guideline, com `paths:` casando os `.py` daqui |
| `docs/plan/system/modelo-dev-units.md` | a seção *Camada normativa* ganha o manifesto de guideline e a fronteira contra skill |
| `docs/plan/system/language-policy.md` | perde o que virou operativo na guideline; mantém medição e racional, e passa a citá-la |
| `.claude/skills/decode-and-code/scripts/tests/test_guideline.py` | **novo** — o teste declarado |
| `.claude/skills/decode-and-code/scripts/tests/fixtures.py` | `rule()` passa a emitir `paths:` |

## Dependências

A unidade `0001-03`, pelo `rules.py` e pelo `fixtures.rule()`. A `0001-08`, pelo `language-policy.md`
que esta unidade divide entre operativo e evidência.

## Normas aplicáveis

| Norma | Onde |
|---|---|
| Camada normativa — os quatro elementos | [`modelo-dev-units.md`](../../system/modelo-dev-units.md), seção *Camada normativa* |
| Skill é invocada; guideline é ativada | [`0001-decode-and-code-foundation.md`](0001-decode-and-code-foundation.md), seção *Skill e guideline separam-se por outro teste* |
| Ativação silenciosa é o modo de falha da própria camada | [`0001-decode-and-code-foundation.md`](0001-decode-and-code-foundation.md), seção de mesmo nome |
| `L-02` — cópia versionada, não symlink | [`0001-decode-and-code-foundation.md`](0001-decode-and-code-foundation.md), seção *Lacunas* |
| Uma fonte por fato | `.claude/CLAUDE.md`, invariante 1 — o corte operativo × evidência é como esta unidade o respeita |
| Nada específico de projeto viaja no plugin | `.claude/CLAUDE.md`, invariante 2 — guideline é instância por definição |

## Critério de aceite

`rules.lint_guideline()` devolve `[]` sobre a guideline entregue, e **reprova isoladamente** cada
invariante: sem `paths:`, com `paths:` vazio, com glob que não compila, e — o que esta unidade
acrescenta — com glob sintaticamente válido que **não casa arquivo nenhum** do repositório.

A guideline entregue **ativa**: ao menos uma entrada de `paths:` casa arquivo que existe aqui,
verificado contra o disco e não contra fixture.

A norma define guideline numa seção só, dentro de *Camada normativa*, e a fronteira contra skill
está escrita com o teste que a decide. Nenhum conteúdo da `hub-front` foi copiado — ela é citada
como caso.

**Nenhum fato aparece nos dois lugares:** o que virou operativo na guideline saiu do
`language-policy.md`, que passa a citá-la.

**A suíte inteira continua verde.**

## Verificação

```
./scripts/test-python.sh .claude/skills/decode-and-code/scripts/tests/test_guideline.py
```

Último resultado: não executado.

## Fonte

- [`0001-decode-and-code-foundation.md`](0001-decode-and-code-foundation.md), *Escopo* → Fase 3, e as seções *Não inventar ativação* e *Skill e guideline separam-se por outro teste*
- `AmFlow:.claude/skills/hub-front/SKILL.md`, medido em 2026-08-24: 547 linhas, seções 1–7 e 9 normativas, seção 8 mapeando unidades. Leitura apenas
- Medição de 2026-08-24 registrada em *Validação de ponta a ponta*: três fontes normativas carregam por sessão, e **nenhuma declara `paths:`** — esta unidade entrega a primeira
