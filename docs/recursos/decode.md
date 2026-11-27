# decode

Versão 2.0.0 · skill

[← Recursos](../../README.md#recursos)

## O que é

A skill da entrada e do decode — P1 e P2 do workflow de produto (codex, *Workflow* e *Decode*). Junta
o pedido, declara o tipo com o motivo, propõe o objetivo do plano, e escreve a **proposta** no
`_inbox/`: a solução conceitual, escrita para o usuário, com os gates A (necessidade real) e B (mínimo
viável) respondidos. Termina na aprovação da proposta, que libera a revisão.

## Problema que resolve

Construir antes de entender é o desperdício mais caro: o plano nasce grande, resolve o problema
errado, ou cria um recurso onde uma instrução bastava. O decode põe a pergunta antes da solução — de
quem é o problema, qual a hipótese, qual o menor MVP — e só depois de o usuário aprovar a proposta o
trabalho vira plano técnico.

## Como funciona

- **Na sessão, sem fork**: o tipo, o objetivo e a proposta pedem a confirmação do usuário, e a
  ferramenta de perguntas não existe em fork.
- **Lê o método pelo título**: `dc.py codex <título>` imprime as seções do codex; a skill nunca as
  copia.
- **Usa o que o projeto já tem**: a foundation (padrão de código e mapa de recursos), as rules e os
  guardrails. Recurso entra na tabela `## Recursos` do plano pelo nome.
- **Recurso do Claude Code**: o gate B sobe a escada nada → instrução → hook → skill ou command →
  agent, e para no primeiro degrau que resolve.
- **Tipo com workflow próprio**: `dc.py modulos` diz se há um módulo para o tipo, como o `fix`, e o
  decode segue pela skill dele (`diagnose`).

## Como usar

```bash
/decode-and-code:decode <pedido>
```

A proposta fica em `<plan_root>/_inbox/<nome>.md`, com `format_version: 2`. Aprovada, a skill
recomenda `/decode-and-code:review-plan <caminho>`.

## Exemplos de uso

- "quero que o test-python.sh rode a cada edição de .py" — tipo `chore`; o gate B escolhe um hook,
  não uma skill, porque o comportamento precisa ser garantido.
- "o catálogo precisa de busca por marca" — tipo `feature`; a proposta traz a hipótese, o MVP e o
  apetite, e a revisão define o porte.

## Fundamentação

Codex, seções *Workflow*, *Decode*, *Proposta*, *Fluxo de decodificação* e *Mindset de produto*.

## Base de conhecimento

As referências de produto do codex (`product-references.md`).

## Limites

Não escreve o plano técnico nem aprova: a revisão (`review-plan`) e o usuário fazem isso.
