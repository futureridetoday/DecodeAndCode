# ai-builder

Versão 1.0.0 · agent

[← Como usar o Decode And Code](../../README.md#como-usar-o-decode-and-code)

## O que é

O agent que decide o menor mecanismo do Claude Code que resolve um pedido — instrução, hook,
command, skill ou agent — antes de qualquer plano nascer em `_inbox/`. Percorre a escada de menor
intervenção e só recomenda abrir um plano quando o pedido excede o que um recurso isolado resolve.
Roda em Opus.

## Problema que resolve

A etapa 1 do ciclo (*o plano nasce*) hoje roda solta na conversa principal, sem crivo — qualquer
pedido de skill, agent ou hook vira plano, mesmo quando três linhas de instrução ou um hook
resolveriam sozinhos. O agent isola esse crivo: chega sem o contexto da conversa, aplica a escada,
e só deixa passar para o ciclo `plano → unidade → cold-start` o que de fato precisa dele.

## Como funciona

Quando invocado, primeiro verifica se o comportamento pedido já está disponível e falha por outro
motivo. Em seguida lê os recursos já existentes no projeto para descartar sobreposição, e percorre
a escada — nada, instrução, hook, command, skill, agent, plano — parando no primeiro degrau que
resolve, mesmo contra um tipo de recurso já pedido explicitamente. Se o degrau for um recurso
isolado, escreve a descrição de ativação com três prompts positivos e três negativos, e constrói a
menor versão que resolve o caso real. Se o degrau for `plano`, para e recomenda abrir
`docs/plan/_inbox/` — nunca escreve o plano.

## Como usar

Invoque pelo nome, com o pedido descrito em linguagem natural:

> @decode-and-code:ai-builder cria algo que rode o lint toda vez que eu editar um .py

> @decode-and-code:ai-builder preciso que o Claude pare de esquecer de rodar o teste antes
> de eu commitar

Use antes de abrir um plano, sempre que não estiver decidido qual mecanismo resolve, ou quando o
pedido já nomeia um tipo de recurso mas vale checar se é o menor que resolve. Se a análise concluir
que o trabalho é grande, o agent recomenda o plano — escrevê-lo continua sendo trabalho da sessão
principal, nunca deste agent.

## Exemplos de uso

**Pedido nomeia o recurso errado.** Usuário pede uma skill para rodar o linter a cada edição de
`.py`. `@decode-and-code:ai-builder` identifica que o comportamento precisa ser garantido,
não sugerido — constrói um hook `PostToolUse` em vez da skill pedida, e relata que ignorou o pedido
original.

**Escopo grande demais para um recurso isolado.** O pedido toca múltiplos scripts e a camada
normativa do projeto. `@decode-and-code:ai-builder` para na escada, não constrói nada, e
recomenda abrir um plano em `docs/plan/_inbox/` — cabe ao humano decidir se abre, e à sessão
principal escrevê-lo.

## Fundamentação

A escada de menor intervenção (nada → instrução → hook → command → skill → agent → plano) opera o
mesmo princípio de [`.claude/rules/principles.md`](../../.claude/rules/principles.md): *código é
custo*, *subtração antes de adição* (`remover > reduzir > reaproveitar > criar`). O agent aplica
esse princípio à decisão de **qual mecanismo construir**, antes mesmo de a norma de Unidades de
Desenvolvimento entrar em jogo.

## Base de conhecimento

Nenhuma própria — a escada e os critérios de construção estão no corpo do agent, não numa skill
carregada à parte. Não depende da skill `decode-and-code`: sua decisão é anterior a ela, e só a
aciona indiretamente ao recomendar abrir um plano. O agent declara
`tools: Glob, Grep, Read, Bash, Write, Edit` e `model: opus`.

## Limites

- **Não escreve plano.** Quando a escada aponta para esse tamanho, recomenda abrir `_inbox/` e
  para — escrever plano do zero pede vaivém que não cabe num agent cold-start.
- **Não revisa nem deriva.** Plano já escrito é trabalho do agent [`planner`](planner.md).
- **Não implementa.** Unidade já derivada é trabalho do agent [`developer`](developer.md).
- **Não publica.** Não interage com hub nem marketplace.
- **Uma mensagem só.** Não itera pedindo confirmação no meio da análise.
