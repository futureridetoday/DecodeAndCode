# decode-and-code

Versão 1.0.0 · skills (3)

[← Como usar o Decode And Code](../../README.md#como-usar-o-decode-and-code)

## O que é

As três skills que executam a norma de Unidades de Desenvolvimento
([`modelo-dev-units.md`](../plan/system/modelo-dev-units.md)), uma por modo: `review-plan` (revisar
um plano antes da aprovação), `derive` (derivar a estrutura e as unidades de um plano aprovado) e
`implement` (implementar uma unidade já derivada, em cold-start). Todo determinismo — gates,
contagem, projeção de estado, validação de nome e colisão — fica nos scripts da pasta compartilhada
`decode-and-code/scripts/`; as skills cuidam do que exige julgamento.

## Problema que resolve

Uma sessão nova não sabe o que a anterior sabia. Sem um método que force o plano a carregar essa
diferença, cada retomada re-deriva o que já existe ou executa fora do que foi desenhado. As skills
dão o procedimento: o modo é o nome da skill, os gates barram avanço com teste empírico, e o estado
de cada unidade é projetado do teste, nunca escrito à mão.

## Como funciona

Cada skill compõe scripts via `python3` (mesmo import dos testes, `sys.path` até
`${CLAUDE_SKILL_DIR}/../decode-and-code/scripts`):

- **`review-plan <plano>`** (Opus) — roda os checks determinísticos primeiro (nome por
  `nomenclatura`, concorrência na região `planos` de `_planos.md`, links do corpo), depois reserva
  julgamento para erro conceitual, erro de arquitetura e adequação das fontes. Lacunas novas entram
  como `L-XX`. Encerra **sem aprovar** — quem aprova é o humano.
- **`derive <plano aprovado>`** (Opus) — `scaffold.aprovar` valida `core`, numera e move o plano do
  `_inbox`. No porte grande, decide a fatia de cada unidade, escreve, linta, projeta o backlog e
  grava o `_handoff.md`. **Só por invocação explícita** (`disable-model-invocation: true`): cria
  estrutura e move arquivos, e o Skill tool recusa que o modelo o dispare.
- **`implement <unidade>`** (Sonnet) — gate de entrada (`lint_unidade`), lê a unidade inteira,
  escreve o teste declarado e o código que o faz passar tocando só os arquivos que ela lista, gate
  de saída (`verificacao.verificar`), projeta o backlog. **Não commita.**

**O `implement` roda sempre em fork** (`context: fork`, `agent: general-purpose`): um subagent sem o
histórico da conversa, em qualquer sessão, inclusive a de orquestração, sem gastar o contexto dela.
Substitui o par de commands `/implement` e `/delegate` das versões anteriores. Daí duas
consequências de desenho: não é interativo — *se o executor precisou perguntar, a unidade falhou* —,
e o resultado volta como uma mensagem, que quem orquestra revisa antes de versionar.

**O modelo é declarado em cada skill** (`model:`), não herdado da sessão: `review-plan` numa sessão
Sonnet roda em Opus, e `implement` numa sessão Opus roda só em Sonnet (norma, seção *Modelos*).

## Como usar

| Plugin instalado | Checkout deste repositório |
|---|---|
| `/decode-and-code:review-plan <plano>` | `/review-plan <plano>` |
| `/decode-and-code:derive <plano>` | `/derive <plano>` |
| `/decode-and-code:implement <unidade>` | `/implement <unidade>` |

> /decode-and-code:review-plan docs/plan/_inbox/catalogo.md

O modelo também invoca `review-plan` e `implement` por pedido em linguagem natural; o `derive`,
só o usuário, pelo comando. O nome `review` ficou de fora porque `/review` é alias do
`/code-review` embutido.

## Exemplos de uso

**Revisar antes de aprovar.** Um plano novo está no `_inbox/`. `review-plan` roda os seis checks,
separa o que o script decidiu do que é julgamento, e devolve uma linha por achado — check, veredito
(`bloqueante` | `aviso`), origem (`comando` | `julgamento`).

**Derivar um plano grande.** Plano aprovado, ainda sem unidades. `derive` cria `<core>/<NNNN>-<nome>/`,
gera um arquivo por unidade do `## Escopo`, linta cada um e escreve o `_handoff.md` para a sessão de
execução.

**Implementar uma unidade.** Unidade `0004-06` derivada. `implement` roda o gate de entrada, escreve
o teste e o código, roda o gate de saída — e se o teste não passa, a unidade não vira `verified`.

## Fundamentação

A norma [`modelo-dev-units.md`](../plan/system/modelo-dev-units.md) — os modos, os dois gates, o
fluxo completo, o formato da unidade — é a fonte; as skills descrevem só o **como**, para não
duplicar o que ela diz (regra anti-drift). Origem medida: a skill `dev-units` do AmFlow — 15 de 15
unidades executadas por Sonnet em sessões novas, sem uma pergunta sobre conteúdo de unidade.

## Base de conhecimento

Nenhuma além dos próprios `SKILL.md`. A norma é lida do projeto que instala, em
`<plan_root>/system/modelo-dev-units.md` — `plan_root` vem do `config.json` da pasta compartilhada
(`docs/plan` é só o default). `bootstrap.iniciar` cria a estrutura num projeto recém-instalado. O
`ai-builder` pré-carrega o `review-plan` e, por ele, acha os scripts fora do checkout.

## Limites

- **Não aprova plano.** `review-plan` encerra com achados; a aprovação é ato humano.
- **`derive` completo só no porte grande.** Pequeno e médio movem o plano sem subpasta e não
  derivam unidade.
- **`implement` não commita e não pergunta.** Entrega arquivos e relatório; versionar é de quem
  orquestra.
- **Não resolve unidade insuficiente.** A correção volta para quem deriva, como lacuna.
- **Nada específico de projeto viaja nas skills.** Guardrail e guideline são do projeto que instala.
