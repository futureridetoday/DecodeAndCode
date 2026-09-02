# /implement

Versão 1.0.0 · command

[← Como usar o Decode And Code](../../README.md#como-usar-o-decode-and-code)

## O que é

O comando que executa o modo `implement` da skill [`decode-and-code`](decode-and-code.md) para uma
unidade, **na sessão atual**.

## Problema que resolve

Uma sessão nova já chega em cold-start por conta própria — sem contexto de conversas anteriores.
Nesse caso, isolar contexto com o agent `developer` é redundante: a própria sessão já é o
isolamento. O comando roda o modo `implement` direto, sem a camada de agent.

## Como funciona

Invoca a skill `decode-and-code` em modo `implement` com `$1` (o identificador da unidade) como
alvo, e segue o processo que ela define: gate de entrada, teste declarado, código, gate de saída,
projeção do backlog. Ao final, entrega arquivos e relatório e **não commita**.

## Como usar

Numa **sessão nova** do Claude Code, com o identificador da unidade:

> /decode-and-code:implement 0004-06

Use quando a sessão já está limpa e dedicada a essa unidade. Se você está numa sessão de
orquestração que precisa preservar o contexto do plano, use [`/decode-and-code:delegate`](delegate.md)
em vez deste. Vale só para unidades de plano **porte grande**.

## Exemplos de uso

**Sessão dedicada a uma unidade.** Você abre uma sessão nova só para a `0004-06`.
`/decode-and-code:implement 0004-06` roda o ciclo inteiro ali; ao terminar, você revisa os arquivos
e versiona.

## Fundamentação

O comando é um atalho de invocação da skill — a diferença para o [`/delegate`](delegate.md) é só o
canal: `implement` roda o modo na sessão corrente; `delegate` dispara o agent `developer` num
cold-start isolado. A norma manda que quem executa entregue arquivos e relatório, e não commite.

## Base de conhecimento

Nenhuma própria. `allowed-tools: Read Write Edit Bash Glob Grep`, `model: sonnet`. Depende da skill
`decode-and-code` (`dependencies: [decode-and-code]`).

## Limites

- **Não isola contexto.** Roda na sessão atual — se ela carrega contexto que não deve gastar, o
  recurso certo é `/delegate`.
- **Só porte grande.** Pequeno e médio não derivam unidade.
- **Não commita.** Entrega arquivos e relatório; quem orquestra revisa antes de versionar.
- **Um argumento.** O identificador da unidade; sem ele, não há o que executar.
