# /delegate

Versão 1.0.0 · command

[← Como usar o Decode And Code](../../README.md#como-usar-o-decode-and-code)

## O que é

O comando que delega a implementação de uma unidade ao agent [`developer`](developer.md), **sem
sair da sessão atual**.

## Problema que resolve

A sessão de orquestração guarda o contexto do plano — ordem das unidades, dependências, pendências
do humano — e não deve gastá-lo executando uma unidade. O comando dispara o `developer` num
cold-start próprio, isolado desta conversa, e devolve o controle para a orquestração quando o agent
termina.

## Como funciona

Invoca o Agent tool com `subagent_type: "developer"`, pedindo para implementar a unidade `$1`.
Quando o agent retorna, o pedido é revisar a entrega — medir, não reler o relatório — antes de
registrar ou versionar.

## Como usar

Na **sessão de orquestração**, com o identificador da unidade:

> /decode-and-code:delegate 0004-06

Use quando você está conduzindo o plano e quer executar uma unidade sem perder o fio. Se a sessão
já está limpa e dedicada a essa unidade, [`/decode-and-code:implement`](implement.md) roda direto,
sem a camada de agent. Vale só para unidades de plano **porte grande**.

## Exemplos de uso

**Fila de unidades a partir do handoff.** A sessão de orquestração recebeu o `_handoff.md` e vai
executar a fila. Para cada unidade, `/decode-and-code:delegate <id>` dispara o `developer`
isolado; ao voltar, a orquestração revisa a entrega e segue para a próxima.

## Fundamentação

O comando é um atalho para a invocação do agent `developer` — a diferença para
[`/implement`](implement.md) é o canal: `delegate` isola a execução num agent com contexto próprio;
`implement` roda o modo na sessão corrente. A revisão da entrega segue a norma, seção *Como revisar
uma entrega*.

## Base de conhecimento

Nenhuma própria. `allowed-tools: Agent`, `model: sonnet`. Depende da skill `decode-and-code`
(`dependencies: [decode-and-code]`) e do agent `developer`.

## Limites

- **Precisa do agent `developer`.** É ele quem executa; o comando só o invoca.
- **Só porte grande.** Pequeno e médio não derivam unidade.
- **Não commita.** O agent entrega arquivos e relatório; a sessão de orquestração revisa e
  versiona.
- **Um argumento.** O identificador da unidade.
