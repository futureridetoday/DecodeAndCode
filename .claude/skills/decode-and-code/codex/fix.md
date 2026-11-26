---
# about
name: codex-fix
type: knowledge
project: ""
description: Codex do decode-and-code, capítulo do workflow de correção — o workflow, o plano mínimo e o teste que reproduz o defeito; o núcleo não depende deste capítulo
tags: [codex, correcao, modulo]

# history
author: Bortoli
created: 2026-11-26
status: draft
version: 0.1.0
updated: ""

# system
scope: project
source: ""
auto_load: false
checksum: ""
dependencies: []
---

# Correção

## Correção

**O que é:** o workflow enxuto que o plano do tipo `fix` segue: localizar o defeito, corrigi-lo e
provar que foi corrigido.

- **Quem faz:** Claude; o usuário aprova e pode testar no lugar de Claude.
- **O que entra:** o pedido, com o tipo e o objetivo do plano, depois da entrada comum a todo
  workflow.
- **O que sai:** o defeito corrigido, provado pelo teste que reproduz o defeito, e o plano fechado.
- **Workflow de correção, depois da entrada:**
  - C1, diagnóstico: Claude localiza e reproduz o defeito e registra o plano mínimo.
  - C2, aprovação do plano mínimo.
  - C3, code, com o plano mínimo aprovado como entrada.
  - C4, teste que reproduz o defeito.
  - Aprovação final, depois do teste.
- **Regras:**
  - O decode é enxuto: identifica o defeito e o que muda para corrigi-lo, sem o custo de um plano de
    produto para mudar uma palavra.
  - A correção não tem proposta: o diagnóstico gera o plano mínimo.
  - Se o diagnóstico mostra que o ajuste não é pequeno, o plano passa para o workflow de produto.

**Ver também:** Plano mínimo, Teste que reproduz o defeito, Workflow, Tipo, Decode, Code, Aprovação,
Proposta.

## Plano mínimo

**O que é:** o plano pequeno com uma única tarefa, que a correção segue.

- **Contém:** o defeito e como reproduzi-lo, o que muda para corrigi-lo, e como verificar.
- **Quem cria:** Claude, no diagnóstico (C1).
- **Regras:**
  - É o plano de porte pequeno; muda só o conteúdo.
  - Toda correção gera plano registrado.
  - O usuário o aprova antes do code (C2), e é nessa aprovação que o plano recebe número. Se o plano
    passa para o workflow de produto, recebe número na aprovação do plano técnico (P4).

**Ver também:** Correção, Plano, Porte, Tarefa, Aprovação, Numeração e nomenclatura, Plano técnico,
Teste que reproduz o defeito.

## Teste que reproduz o defeito

**O que é:** o teste C4 da correção, que falha antes do ajuste e passa depois.

- **Quando vale:** em toda correção, depois do code.
- **O que exige:**
  - Claude ou o usuário o faz, a partir de como reproduzir o defeito, que o plano mínimo declara.
  - É o teste que verifica o critério de aceite da correção.
- **Quando falha:** sem ele, a correção não é verificada.

**Ver também:** Teste, Critério de aceite, Plano mínimo, Correção, Aprovação.
