---
name: principles
description: Os três princípios inegociáveis do decode-and-code — código é custo, subtração antes de adição, evidência acima de opinião — e o fluxo de decodificação que os aplica a uma decisão concreta. Carrega sempre, em toda sessão.
---

# Princípios

Carregados sempre — este arquivo não declara `paths:`. É o que os separa de guideline (norma,
seção *Princípio e guideline separam-se por um teste*): **uma equipe competente pode rejeitar isso
e ainda estar fazendo trabalho bom?** Não, para os três abaixo — por isso são princípio, não
escolha técnica.

## Código é custo

**Enunciado:** código não é ativo — é responsabilidade que se paga em manutenção, superfície de
bug e carga cognitiva, a cada linha que existe.

**Teste:** só existe se eliminar dor real e mensurável.

## Subtração antes de adição

**Enunciado:** toda solução se avalia nesta ordem, e a próxima opção só entra em consideração se a
anterior não resolver.

**Teste:** `remover > reduzir > reaproveitar > criar`.

**Na prática:** sem features além do pedido, sem abstração para uso único, sem configurabilidade
não solicitada. Ao editar código existente, tocar só o necessário e seguir o estilo que já está
lá — não refatorar o que não está quebrado. Código morto não relacionado ao trabalho em curso se
menciona, não se deleta.

## Evidência acima de opinião

**Enunciado:** decisão de projeto se sustenta em dado, não em preferência estética ou tendência de
mercado.

**Teste:** decisão baseada em dado simples — medição, citação ou caso registrado —, não em
estética.

## Fluxo de decodificação

Três estágios, cada um com pergunta obrigatória e saída esperada:

| Estágio | Perguntas obrigatórias | Saída esperada |
|---|---|---|
| **Clarificar** | Problema + métrica + beneficiário em 1 frase | Frase clara e mensurável |
| **Evitar** | Posso resolver sem código — config, processo, doc ou reuso? | Lista de alternativas |
| **Reduzir** | Qual é a menor versão que resolve 80% agora? | Escopo mínimo viável |

Dois gates, que barram avanço:

| Gate | Critério |
|---|---|
| **A — necessidade real** | Há impacto mensurável **agora**? |
| **B — mínimo viável** | Há como reduzir linhas, arquivos ou dependências? |

> **Gate é critério, não posição no tempo.** A e B são as duas perguntas que barram avanço; não são
> "antes de escrever" e "antes de entregar".

## Protocolo de exceção

Pede-se exceção quando, e só quando: a regra é **inviável** no contexto; há **trade-off crítico**
não coberto; é **edge case** com risco operacional ou de compliance; há **conflito** entre normas
ativas; ou há **exigência explícita** do humano.

O registro mínimo nomeia a regra, o que já foi tentado, o que se propõe no lugar, e quem aprovou.

## Fonte

Formulações da fonte primária, `CortexMachine:guidelines/decode_code/decode_code_essentials.md` e
`decode_code_foundation.md` — ver [`03-principles-rule.md`](../../docs/plan/model/0001-decode-and-code-foundation/03-principles-rule.md)
para a proveniência completa e o que foi deliberadamente deixado de fora.
