# ai-builder

Versão 1.0.0 · agent

[← Como usar o Decode And Code](../../README.md#como-usar-o-decode-and-code)

## O que é

O agent que decide o menor mecanismo do Claude Code que resolve um pedido de automação —
instrução, hook, command, skill ou agent — antes de qualquer plano nascer em `_inbox/`. Quando o
pedido não é automação, mas um esboço de plano, um problema de produto ou uma feature, consulta os
arquivos do sistema, aplica os gates de mínimo viável, e grava o esboço em `_inbox/` para a skill
[`review-plan`](decode-and-code.md) revisar. Roda em Opus.

## Problema que resolve

Dois problemas do mesmo ponto do ciclo, a etapa 1 (*o plano nasce*):

- Qualquer pedido de skill, agent ou hook virava plano, mesmo quando três linhas de instrução ou
  um hook resolveriam sozinhos.
- Um esboço de plano nascia sem crivo contra o problema real — nada no ciclo audita se o plano é
  maior do que o necessário. A *Avaliação de escopo* do `review-plan` testa acoplamento entre
  planos, nunca se um plano sozinho é maior do que o problema pede (`modelo-dev-units.md`, seção *O
  que a avaliação não faz*). Um esboço superficial pode convencer o humano a aprovar dez unidades
  onde uma bastava, e depois disso não existe outro checkpoint.

O agent isola os dois: chega sem o contexto da conversa, aplica a escada ou os gates conforme o
tipo de pedido, e só deixa passar para o `review-plan` o que já foi reduzido ao mínimo que resolve
agora.

## Como funciona

Quando invocado, primeiro classifica o pedido — automação do Claude Code, ou esboço/problema/
feature de produto — e verifica se o comportamento já está disponível e falha por outro motivo.

Para **automação pontual**: lê os recursos já existentes no projeto, percorre a escada — nada,
instrução, hook, command, skill, agent — parando no primeiro degrau que resolve, mesmo contra um
tipo de recurso já pedido explicitamente. Escreve a descrição de ativação com três prompts
positivos e três negativos, e constrói a menor versão que resolve o caso real.

Para **esboço de plano, problema ou feature**: lê os arquivos do sistema relacionados ao pedido, e
aplica Clarificar → Evitar → Reduzir e os dois gates de `principles.md`. Sem impacto mensurável
agora (Gate A), para e reporta. Com impacto, reduz o escopo até a menor fatia que resolve 80% do
problema (Gate B), registra por escrito o que foi cortado, numera e nomeia o esboço reaproveitando
os scripts da pasta compartilhada `decode-and-code/`, grava em `docs/plan/_inbox/`, roda
`lint_plano.py` contra o próprio arquivo, e recomenda `review-plan <caminho>`. Faltando informação
para fechar qualquer um dos três estágios, para numa única rodada e lista exatamente o que falta —
nunca itera pedindo confirmação no meio da análise.

## Como usar

Invoque pelo nome, com o pedido descrito em linguagem natural:

> @decode-and-code:ai-builder cria algo que rode o lint toda vez que eu editar um .py

> @decode-and-code:ai-builder os usuários estão abandonando o checkout no passo de pagamento,
> preciso resolver isso

Use antes de abrir um plano à mão, sempre que não estiver decidido qual mecanismo resolve, quando
o pedido já nomeia um tipo de recurso mas vale checar se é o menor que resolve, ou quando só existe
um problema ou uma ideia de feature e falta transformar isso num esboço revisável.

## Exemplos de uso

**Pedido nomeia o recurso errado.** Usuário pede uma skill para rodar o linter a cada edição de
`.py`. `@decode-and-code:ai-builder` identifica que o comportamento precisa ser garantido, não
sugerido — constrói um hook `PostToolUse` em vez da skill pedida, e relata que ignorou o pedido
original.

**Problema de produto, sem esboço prévio.** O pedido descreve um sintoma, não um recurso do Claude
Code. `@decode-and-code:ai-builder` lê os arquivos relacionados, aplica os gates, e grava um
esboço mínimo em `docs/plan/_inbox/` para o `review-plan` revisar.

**Esboço maior do que o problema pede.** O usuário já chega com um rascunho de feature com múltiplas
partes. O Gate B reprova o escopo como está — o agent reduz para o que resolve agora, registra o
corte, e só então grava.

## Fundamentação

A escada de menor intervenção (nada → instrução → hook → command → skill → agent) e o Fluxo de
decodificação (Clarificar → Evitar → Reduzir, Gates A e B) operam o mesmo princípio de
[`.claude/rules/principles.md`](../../.claude/rules/principles.md): *código é custo*, *subtração
antes de adição* (`remover > reduzir > reaproveitar > criar`). O agent aplica esse princípio duas
vezes — a qual mecanismo construir, e a que tamanho de plano propor — antes mesmo de a norma de
Unidades de Desenvolvimento entrar em jogo.

## Base de conhecimento

Depende dos scripts da pasta compartilhada `decode-and-code/` para o que reaproveita ao gravar um
esboço — `numeracao.py` (próximo número de plano), `nomenclatura.py` (sintaxe e colisão do nome) e
`lint_plano.py` (formato do esboço antes de encerrar). A escada de mecanismo continua independente
deles: só o ramo de esboço os usa. O agent declara `tools: Glob, Grep, Read, Bash, Write, Edit,
WebFetch`, `model: opus` e `skills: [review-plan]`.

O `skills:` pré-carrega o `review-plan`, e é por ele que o agent acha os scripts fora do checkout:
medido em 2026-10-15 com `--plugin-dir`, o debug log mostra `Preloaded skill` e o agent recebe o
corpo da skill com o caminho absoluto dos scripts no plugin.

## Limites

- **Não deriva nem implementa.** Plano aprovado é trabalho da skill `derive`; unidade derivada, da
  skill `implement` ([decode-and-code.md](decode-and-code.md)).
- **Não aprova.** Aprovação de plano é sempre do humano.
- **Não publica.** Não interage com hub nem marketplace.
- **Uma mensagem só.** Falta de informação para fechar um gate para a análise numa única rodada —
  não itera pedindo confirmação no meio dela.
