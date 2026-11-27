---
# about
name: codex-invariants
type: knowledge
project: ""
description: Codex do decode-and-code, capítulo dos invariantes — as regras que valem sempre e limitam o que o DC grava no projeto, com o enunciado, o que protegem e como se verificam
tags: [codex, invariante]

# history
author: Bortoli
created: 2026-11-26
status: draft
version: 0.2.0
updated: ""

# system
scope: project
source: ""
auto_load: false
checksum: ""
dependencies: []
---

# Invariantes

## Invariante

**O que é:** uma regra que vale sempre, em qualquer etapa e em qualquer projeto.

- **Enunciado:**
  - Uma fonte por fato: nenhum trecho do codex aparece repetido na foundation nem no passo a passo
    que conduz cada etapa. Vale para o trecho copiado, não para a ideia citada.
  - Nada do projeto no plugin: nenhum dado de projeto viaja no plugin.
  - Instruções em conflito não têm vencedor; por isso nada do projeto, nem guideline nem foundation,
    pode repetir ou contradizer o codex.
- **O que protege:** o codex, como fonte única do método, e a foundation, como fonte única do que é
  do projeto.
- **Como se verifica:** pela busca de trecho repetido entre o codex e o que o projeto e as etapas
  guardam, e pela auditoria do que o plugin leva, contra dado de qualquer projeto.

**Ver também:** Restrição fundamental, Foundation, Guideline, Setup, Rethink, Tipo.

## Restrição fundamental

**O que é:** o projeto não altera o codex.

- **Enunciado:** o codex só existe no plugin, e nada do DC o copia para o projeto. O tradeoff é
  aceito: fora das etapas do DC, Claude não vê o método.
- **O que protege:** o codex, que muda num lugar só; a foundation é a parte que o projeto altera.
- **Como se verifica:** nenhum arquivo do projeto traz o texto do codex.

**Ver também:** Invariante, Foundation, Setup, Rethink, Usuário.
