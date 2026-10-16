# intake

Versão 1.0.0 · skill

[← Como usar o Decode And Code](../../README.md#como-usar-o-decode-and-code)

## O que é

A skill que decide o menor mecanismo do Claude Code que resolve um pedido — instrução, hook,
command, skill ou agent — antes de qualquer plano nascer em `_inbox/`. Quando o pedido não é
automação, mas um esboço de plano, um problema de produto ou uma feature, aplica os gates de mínimo
viável e grava o esboço em `_inbox/` para a skill [`review-plan`](decode-and-code.md) revisar. Roda
em Opus, em fork (`context: fork`): um subagent sem o histórico da conversa.

## Problema que resolve

Dois problemas do mesmo ponto do ciclo, a etapa 1 (*o plano nasce*):

- Qualquer pedido de skill, agent ou hook virava plano, mesmo quando três linhas de instrução ou
  um hook resolveriam sozinhos.
- Um esboço de plano nascia sem crivo contra o problema real. A *Avaliação de escopo* do
  `review-plan` testa acoplamento entre planos, nunca se um plano sozinho é maior do que o problema
  pede (`modelo-dev-units.md`, seção *O que a avaliação não faz*): um esboço superficial pode levar
  o humano a aprovar dez unidades onde uma bastava, e depois disso não há outro checkpoint.

## Como funciona

Classifica o pedido e, se as duas leituras cabem, pergunta em vez de escolher.

Para **recurso do Claude Code**: lê o que o projeto já tem em `.claude/` e sobe a escada — nada,
instrução, hook, skill ou command, agent —, parando no primeiro degrau que resolve, mesmo contra o
tipo pedido. Entrega o recurso ou a recomendação.

Para **plano, feature ou problema**: lê os arquivos relacionados e aplica Clarificar → Evitar →
Reduzir e os gates A e B da norma (*Antes do plano — fluxo de decodificação*). Faltando informação, para numa única rodada e lista o
que falta. Com os gates respondidos, grava o esboço em `<plan_root>/_inbox/<nome>.md`, valida o nome
(`validar-nome`) e roda `lint-plano` pelo `dc.py`, e recomenda `review-plan <caminho>`. O nome do
esboço não leva número: ele vem na aprovação (norma, seção *Nomenclatura*).

## Como usar

| Plugin instalado | Checkout deste repositório |
|---|---|
| `/decode-and-code:intake <pedido>` | `/intake <pedido>` |

> /decode-and-code:intake os usuários estão abandonando o checkout no passo de pagamento

O modelo também a invoca por pedido em linguagem natural. Use antes de abrir um plano à mão, quando
não está decidido qual mecanismo resolve, ou quando só existe um problema ou uma ideia de feature.

## Exemplos de uso

**Pedido nomeia o recurso errado.** Pede-se uma skill para rodar o linter a cada edição de `.py`. O
comportamento precisa ser garantido, não sugerido: o `intake` recomenda um hook `PostToolUse` e diz
que ignorou o tipo pedido.

**Problema de produto, sem esboço prévio.** O pedido descreve um sintoma, não um recurso. O `intake`
lê os arquivos relacionados, aplica os gates e grava um esboço mínimo em `_inbox/`.

**Esboço maior do que o problema pede.** O gate B reprova o escopo como está: o `intake` reduz ao que
resolve agora, registra o que cortou no esboço e só então grava.

## Fundamentação

A escada de menor intervenção e o fluxo de decodificação da norma operam o mesmo princípio de
[`.claude/rules/principles.md`](../../.claude/rules/principles.md): *código é custo*, *subtração
antes de adição* (`remover > reduzir > reaproveitar > criar`). A skill o aplica duas vezes — a qual
mecanismo construir, e a que tamanho de plano propor.

Era o agent `ai-builder`, com 14 KB. A conversão em skill (`D-03` do plano `apply-plugin-review`)
mantém o isolamento de contexto por `context: fork` e reduz o prompt a cerca de 4 KB, o teto que um
teste confere; o que saiu era persona e repetição do que o Claude Code já faz (achado `P-06`).

## Base de conhecimento

`plan_root` vem do `config.json` da pasta compartilhada `decode-and-code/` (`docs/plan` é só o
default). Os scripts são chamados pelo `dc.py`, e o `allowed-tools` libera só ele, mais `Read`,
`Write`, `Edit`, `Glob`, `Grep` e `WebFetch` restrito a `code.claude.com`, para confirmar schema na
documentação oficial. O formato do esboço é o da norma, seção *O que cada porte carrega*.

## Limites

- **Não deriva nem implementa.** Plano aprovado é da skill `derive`; unidade derivada, da skill
  `implement` ([decode-and-code.md](decode-and-code.md)).
- **Não aprova.** Aprovação de plano é sempre do humano.
- **Uma rodada só.** Falta de informação para fechar um gate para a análise e lista o que falta; não
  itera pedindo confirmação no meio dela.
