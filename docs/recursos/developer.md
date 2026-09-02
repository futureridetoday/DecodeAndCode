# developer

Versão 1.0.0 · agent

[← Como usar o Decode And Code](../../README.md#como-usar-o-decode-and-code)

## O que é

O agent que implementa uma unidade já derivada, sempre em cold-start — sem contexto de conversas
anteriores e sem memória entre execuções. Escreve o teste declarado e o código que o faz passar,
tocando só os arquivos que a unidade lista. Roda em Sonnet.

## Problema que resolve

A sessão que orquestra um plano guarda contexto caro — a ordem das unidades, as dependências, o que
ficou pendente do humano. Executar a unidade ali gasta esse contexto. O agent isola a execução:
chega limpo, implementa uma unidade, devolve arquivos e relatório, e a sessão de orquestração
segue intacta.

## Como funciona

Quando invocado, carrega a skill declarada em `skills: [decode-and-code]` e segue o modo
`implement`: gate de entrada antes de tocar qualquer arquivo, lê a unidade inteira, abre as normas
citadas na tabela dela, escreve o teste do critério de aceite, escreve o código que faz o teste
passar, roda o gate de saída (teste falhando, a unidade não vira `verified`), projeta o backlog e
relata.

## Como usar

Invoque pelo nome, com a unidade como alvo:

> @decode-and-code:developer implemente a unidade 0004-06

Ou, sem sair da sessão atual, pelo comando [`/decode-and-code:delegate`](delegate.md), que faz
exatamente essa invocação. Use quando a unidade **já está derivada** e você quer executá-la sem
gastar o contexto da conversa de orquestração. Vale só para unidades de plano **porte grande** —
são as únicas que o modelo deriva.

## Exemplos de uso

**Delegação da sessão de orquestração.** A sessão que derivou o plano precisa implementar a
`0004-06` sem perder o fio. `/decode-and-code:delegate 0004-06` dispara o `developer` em cold-start
próprio; ao retornar, a sessão revisa a entrega (medir, não reler o relatório) antes de versionar.

**Fila de unidades.** Várias unidades derivadas e independentes. Cada uma vai para uma invocação do
`developer`, e o resultado de cada uma é arquivos + relatório, nunca um commit.

## Fundamentação

O agent é um invólucro fino sobre o modo `implement` da skill. A norma separa os papéis: quem
executa uma unidade **entrega arquivos e relatório, não commita**; e **se o executor precisou
perguntar, a unidade falhou** — a correção volta para quem deriva, registrada como lacuna, nunca
resolvida em execução.

## Base de conhecimento

Nenhuma própria. Tudo vem da skill `decode-and-code` e das normas que a unidade referencia — que
são referência, nunca cópia dentro da unidade. O agent declara `tools: Glob, Grep, Read, Bash,
Write, Edit` e `model: sonnet`.

## Limites

- **Só implementa.** Não deriva nem revisa planos — decidir a fatia de uma unidade não é trabalho
  dele.
- **Não commita.** Entrega arquivos e relatório; versionar é de quem orquestra.
- **Não conserta unidade insuficiente.** Se a unidade não basta sozinha, a correção volta para
  quem deriva.
- **Só porte grande.** Pequeno e médio não derivam unidade, então não há o que este agent execute.
- **Cold-start sempre.** Não herda contexto e não guarda memória entre execuções.
