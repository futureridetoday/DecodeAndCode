---
# about
name: codex-fix
type: knowledge
project: ""
description: Codex do decode-and-code, capítulo do workflow de correção — o workflow, a passagem para o workflow de produto, o plano mínimo e o teste que reproduz o defeito; o núcleo não depende deste capítulo
tags: [codex, correcao, modulo]

# history
author: Bortoli
created: 2026-11-26
status: stable
version: 1.0.0
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
  - C1, diagnóstico: Claude localiza e reproduz o defeito, à mão se preciso, e registra o plano
    mínimo.
  - C2, aprovação do plano mínimo.
  - C3, code, com o plano mínimo aprovado como entrada: começa pelo teste que reproduz o defeito,
    que roda e falha antes do ajuste.
  - C4, o mesmo teste passa depois do ajuste.
  - Aprovação final, depois do teste.
- **Regras:**
  - O diagnóstico é um decode enxuto: identifica o defeito e o que muda para corrigi-lo, lendo do
    projeto só o que o defeito toca, sem o custo de um plano de produto para mudar uma palavra.
  - A correção não tem proposta: o diagnóstico gera o plano mínimo.
  - Valem no C3 os gates do code, e nas aprovações as regras de Aprovação, recusa inclusive.

**Ver também:** Passagem para o workflow de produto, Plano mínimo, Teste que reproduz o defeito,
Workflow, Tipo, Decode, Code, Aprovação, Proposta.

## Passagem para o workflow de produto

**O que é:** o que acontece quando o diagnóstico mostra que o pedido não cabe na correção.

- **Quem faz:** Claude propõe; o usuário aprova a troca.
- **Quando vale:** quando o ajuste não é pequeno, ou quando não há defeito, porque o comportamento
  pedido nunca foi especificado nem construído.
- **Regras:**
  - Claude propõe o novo tipo, com o motivo, e o usuário aprova a troca.
  - O plano continua, ainda sem número: o conteúdo do plano mínimo dá lugar ao do workflow de
    produto, o que o diagnóstico achou entra na proposta como contexto, e o nome pode ser refeito.
  - O plano volta à confirmação do objetivo, na entrada, e segue o workflow de produto desde o P1.

**Ver também:** Correção, Plano mínimo, Tipo, Objetivo do plano, Workflow, Decode, Plano.

## Plano mínimo

**O que é:** o plano pequeno com uma única tarefa, que a correção segue.

- **Contém:** o que todo plano contém, e, no lugar das histórias, o defeito e como reproduzi-lo, o
  que muda para corrigi-lo, e como verificar, que é o critério de aceite.
- **Quem cria:** Claude, no diagnóstico (C1).
- **Regras:**
  - É o plano de porte pequeno, com uma tarefa que inclui o teste.
  - Toda correção gera plano registrado.
  - O usuário o aprova antes do code (C2), e é nessa aprovação que o plano recebe número.

**Ver também:** Correção, Passagem para o workflow de produto, Plano, Porte, Tarefa, Critério de
aceite, Aprovação, Numeração e nomenclatura, Teste que reproduz o defeito.

## Teste que reproduz o defeito

**O que é:** o teste da correção, que falha antes do ajuste e passa depois.

- **Quando vale:** em toda correção; é escrito e roda vermelho no início do C3, e roda verde no C4.
- **O que exige:**
  - Claude ou o usuário o faz, a partir de como reproduzir o defeito, que o plano mínimo declara.
  - É o teste que verifica o critério de aceite da correção.
  - A execução vermelha, antes do ajuste, fica registrada no relatório da entrega.
- **Quando falha:** se não falha antes do ajuste, não reproduz o defeito e é refeito; se não passa
  depois, o C3 continua.

**Ver também:** Teste, Critério de aceite, Plano mínimo, Correção, Entrega, Aprovação.
