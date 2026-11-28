# decode-and-code

Versão 2.0.0 · skills `review-plan`, `derive`, `code` e `diagnose`

[← Recursos](../../README.md#recursos)

## O que é

As skills que levam a proposta aprovada até a entrega, no workflow do codex (*Workflow*):
`review-plan` (P3 e P4, o plano técnico e a aprovação que dá o número), `derive` (P5, as unidades
prontas para rodar sem a conversa), `code` (P6 e P7, a entrega e a aprovação dela), e `diagnose`, do
módulo de correção. Todo determinismo — gates, contagem, projeção de estado, validação de nome — fica
nos scripts da pasta compartilhada `decode-and-code/scripts/`; as skills cuidam do que exige
julgamento.

## Problema que resolve

Uma sessão nova não sabe o que a anterior sabia. Sem um método que force o plano a carregar essa
diferença, cada retomada re-deriva o que já existe ou executa fora do que foi desenhado. As skills
dão o procedimento; os gates barram o avanço por teste; e a situação de cada unidade é projetada do
teste, nunca escrita à mão.

## Como funciona

Cada skill chama os scripts por um ponto de entrada só, o `dc.py`
(`python3 "${CLAUDE_SKILL_DIR}/dc.py" <subcomando> …`, do diretório do projeto), e o `allowed-tools`
libera só ele. Saída em texto simples; código `0` ok, `1` problema ou reprovação, `2` erro de uso ou
exceção. Cada skill lê do codex, pelo título, as seções que valem para ela (`dc.py codex`).

- **`review-plan <plano>`** (Opus) — escreve, abaixo da proposta aprovada, as histórias, a
  independência, as decisões e os riscos, e as tarefas (pequeno) ou a tabela de unidades (médio e
  grande); no grande, também a fase de cada história e o `## Teste do plano inteiro`; confere fontes,
  recursos e concorrência; roda `validar-nome` e `lint-plano`. Na
  aprovação do usuário (P4), roda `aprovar`: o plano recebe número e vai para a raiz dos planos.
- **`derive <plano>`** (Opus, só por invocação explícita) — no médio e no grande, escreve uma
  unidade por linha de `## Unidades`, com os blocos da Definition of Ready, cita as guidelines dos
  caminhos (`guidelines-aplicaveis`), linta (`lint-unidade`, e `lint-plano` no grande, que confere o dono de cada `R-NN`), projeta o backlog e grava o
  `_handoff.md`. O usuário aprova as unidades juntas.
- **`code <unidade>`** (Sonnet, em fork, sem o histórico) — `entrada-code` confere a unidade e a
  aprovação das unidades que ela cita em `## Depende de`; escreve o teste e o código pelo critério de aceite; `verificar` projeta o
  estado. Para e propõe o ajuste (lacuna) quando a unidade não basta, e antes de ação irreversível.
  No pequeno, executa as tarefas do plano. `code aprovar <alvo>` grava a aprovação do usuário (P7)
  por `aprovar-entrega`.
- **`diagnose <defeito>`** (Opus) — do módulo `fix`: reproduz o defeito, escreve o plano mínimo e o
  leva à aprovação (C2); o `code` faz o teste vermelho, o ajuste e o teste verde.

## Como usar

```bash
/decode-and-code:review-plan docs/plan/_inbox/add-catalog.md
```

```bash
/decode-and-code:derive docs/plan/0031-add-catalog
```

```bash
/decode-and-code:code 0031-01
```

```bash
/decode-and-code:code aprovar 0031-01
```

O handoff do médio e do grande vai para uma sessão nova, que roda o `code` de cada unidade na ordem
dele.

## Exemplos de uso

- Plano pequeno: `review-plan` → aprovação P4 → `code <plano>` → `code aprovar <plano>`, que fecha o
  plano.
- Plano grande: `review-plan` → P4 → `derive` → aprovação das unidades → `code` e `code aprovar` por
  unidade, na ordem do handoff → teste do plano inteiro (P8).

## Fundamentação

Codex, seções *Revisão*, *Plano técnico*, *Derive*, *Definition of Ready*, *Handoff*, *Code*,
*Entrega*, *Lacuna* e *Aprovação*; no módulo de correção, *Correção* e *Plano mínimo*.

## Base de conhecimento

A fronteira entre skill e script e o modelo de cada skill:
[`skills-and-scripts.md`](../maintenance/skills-and-scripts.md).

## Limites

Nenhuma skill aprova pelo usuário: P2, P4, a aprovação das unidades e P7 são dele. Quem executa uma
unidade não commita. Plano anterior ao redesign (sem `format_version`) passa pela revisão antes de
derive e code.
