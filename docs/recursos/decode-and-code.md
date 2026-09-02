# decode-and-code

Versão 1.0.0 · skill

[← Como usar o Decode And Code](../../README.md#como-usar-o-decode-and-code)

## O que é

A skill que executa a norma de Unidades de Desenvolvimento
([`modelo-dev-units.md`](../plan/system/modelo-dev-units.md)) em três modos: `review` (revisar um
plano antes da aprovação), `derive` (derivar a estrutura e as unidades de um plano aprovado) e
`implement` (implementar uma unidade já derivada, em cold-start). Todo determinismo — gates,
contagem, projeção de estado, validação de nome e colisão — fica nos scripts em `scripts/`; a skill
cuida do que exige julgamento.

## Problema que resolve

Uma sessão nova não sabe o que a anterior sabia. Sem um método que force o plano a carregar essa
diferença, cada retomada re-deriva o que já existe ou executa fora do que foi desenhado. A skill dá
o procedimento único: o modo é sempre explícito, os gates barram avanço com teste empírico, e o
estado de cada unidade é projetado do teste, nunca escrito à mão.

## Como funciona

O primeiro argumento é o modo — nunca inferido do texto livre. Cada modo compõe scripts via
`python3` (mesmo import dos testes, `sys.path` até `scripts/`):

- `review <plano>` — roda os checks determinísticos primeiro (nome por `nomenclatura`, concorrência
  na região `planos` de `_planos.md`, links do corpo resolvem em disco), depois reserva julgamento
  para erro conceitual, erro de arquitetura e adequação das fontes. Lacunas novas entram como
  `L-XX`, sem tentar resolvê-las. Encerra **sem aprovar** — quem aprova é o humano.
- `derive <plano aprovado>` — `scaffold.aprovar` valida `core`, atribui o número, move o plano do
  `_inbox` e registra a linha em `_planos.md`. No porte grande, decide a fatia de cada unidade
  (contrato, sequência, arquivos que toca), numera com `numeracao`, escreve, linta com
  `lint_unidade`, projeta o backlog e grava o `_handoff.md`.
- `implement <unidade>` — gate de entrada (`lint_unidade`), lê a unidade inteira, escreve o teste
  declarado cobrindo o critério de aceite e o código que o faz passar tocando só os arquivos que a
  unidade lista, gate de saída (`verificacao.verificar`), projeta o backlog. O executor **não
  commita**.

## Como usar

Sempre com o modo explícito no primeiro argumento:

> revise o plano docs/plan/_inbox/catalogo.md → modo `review`

> derive o plano docs/plan/_inbox/catalogo.md → modo `derive`

> implemente a unidade 0001-03 → modo `implement`

Sem modo, ou com modo fora dos três, a skill recusa e lista as opções — não escolhe por conta
própria.

`review` e `derive` pedem julgamento denso e rodam melhor em Opus; `implement` roda por padrão em
Sonnet, com override do usuário conforme o escopo. A skill **herda o modelo de quem a invoca** — a
troca por modo não é declarável nela.

Para rodar `implement` numa sessão limpa sem gastar o contexto da conversa atual, use o comando
[`/decode-and-code:implement`](implement.md) (sessão nova) ou
[`/decode-and-code:delegate`](delegate.md) (delega ao agent `developer`). Para `review`/`derive`
isolados, invoque o agent [`@decode-and-code:planner`](planner.md).

## Exemplos de uso

**Revisar antes de aprovar.** Um plano novo está no `_inbox/`. `review` roda os seis checks, separa
o que o script decidiu do que é julgamento, registra lacunas como `L-XX` sem resolvê-las, e devolve
uma linha por achado — check, veredito (`bloqueante` | `aviso`), origem (`comando` | `julgamento`).

**Derivar um plano grande.** Plano aprovado, ainda sem unidades. `derive` cria
`<core>/<NNNN>-<nome>/`, gera um arquivo por unidade prevista no `## Escopo`, linta cada um, projeta
o backlog e escreve o `_handoff.md` para a sessão de execução.

**Implementar uma unidade.** Unidade `0004-06` derivada. `implement` roda o gate de entrada,
escreve o teste do critério de aceite e o código, roda o gate de saída — e se o teste não passa, a
unidade não transiciona para `verified`.

## Fundamentação

A norma [`modelo-dev-units.md`](../plan/system/modelo-dev-units.md) — os três modos, os dois gates,
o fluxo completo, o formato do arquivo de unidade — é a fonte. A skill descreve só o **como** de
cada modo, para não duplicar o que a norma já diz (regra anti-drift). Origem medida: a skill
`dev-units` do AmFlow — 15 de 15 unidades executadas por Sonnet em sessões novas, sem uma pergunta
sobre conteúdo de unidade.

## Base de conhecimento

Nenhuma embutida além do próprio `SKILL.md`. A norma é lida do projeto que instala, em
`<plan_root>/system/modelo-dev-units.md` — `plan_root` resolvido pelo `config.json` da skill
(`docs/plan` é só o default). Os scripts em `scripts/` carregam toda a lógica determinística;
`bootstrap.iniciar` cria a estrutura (`_planos.md`, `_inbox/`, a norma) num projeto que acabou de
instalar o plugin.

## Limites

- **Não infere o modo.** Sem modo explícito, recusa e lista as opções.
- **Não aprova plano.** `review` encerra com achados; a aprovação é ato humano.
- **`derive` completo só no porte grande.** Pequeno e médio movem o plano sem subpasta e não
  derivam unidade — médio projeta as caixas de `## Tarefas`, pequeno fecha quando o humano grava
  `status: done`.
- **`implement` não commita.** Entrega arquivos e relatório; versionar é de quem orquestra.
- **Não resolve unidade insuficiente.** Se o executor precisou perguntar, a unidade falhou — a
  correção volta para quem deriva, como lacuna.
- **Nada específico de projeto viaja na skill.** Guardrail e guideline são do projeto que instala.
