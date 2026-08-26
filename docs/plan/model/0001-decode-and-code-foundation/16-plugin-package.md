---
# about
name: plugin-package
type: unit
project: DecodeAndCode
description: O método vira plugin instalável — build reproduzível a partir das fontes, com o guarda que recusa levar junto qualquer instância do projeto que o produziu
tags: [decode-and-code, plugin, empacotamento, distribuicao, guideline]

# alvo
core: model
module: decode-and-code
block: ""
owner: model
unit_id: 0001-16
unit_type: dev

# verificação
state: verified
test: .claude/skills/decode-and-code/scripts/tests/test_empacotamento.py
verified_at: 2026-08-26

# history
author: Bortoli
created: 2026-08-26
status: draft
version: 1.0.0
updated: ""

# system
scope: project
auto_load: false
dependencies: []
---

# 0001-16 — plugin-package

**Responsabilidade:** transformar o que este repositório desenvolveu em um plugin que outro projeto
instala — e garantir, por teste, que nada específico daqui viaje junto (invariante 2 do
`CLAUDE.md`).

## Contrato

| Campo | Detalhe |
|---|---|
| **Entrada** | `empacotar.construir(destino)`, `empacotar.verificar(destino)` e `empacotar.materializar(origem, projeto)` |
| **Saída** | `construir` devolve a lista de caminhos escritos. `verificar` devolve a lista de problemas — vazia quando o pacote está limpo, no mesmo padrão de `lint_*`. `materializar` devolve o caminho escrito, ou levanta se já existir |
| **Auth** | — |
| **Efeito** | `construir` escreve a árvore do plugin em `destino`, **sempre do zero**. `verificar` só lê. `materializar` escreve **um** arquivo em `<projeto>/.claude/rules/` |
| **Erro** | Fonte ausente levanta `FileNotFoundError` antes de escrever qualquer coisa. `materializar` sobre destino existente levanta `FileExistsError` — nunca sobrescreve norma em silêncio |

**A árvore que `construir` produz**, medida em plugins reais instalados nesta máquina
(`~/.claude/plugins/marketplaces/`, 2026-08-26) — não é convenção suposta:

| Caminho no pacote | De onde vem |
|---|---|
| `.claude-plugin/plugin.json` | cópia do manifesto versionado na raiz deste repositório |
| `skills/decode-and-code/` | `.claude/skills/decode-and-code/`, **sem** `scripts/tests/` e sem `__pycache__` |
| `hooks/*.py` | os quatro hooks de `.claude/hooks/` |
| `hooks/hooks.json` | gerado do bloco `hooks` de `.claude/settings.json`, com `${CLAUDE_PROJECT_DIR}/.claude/hooks` reescrito para `${CLAUDE_PLUGIN_ROOT}/hooks` |

> **`${CLAUDE_PLUGIN_ROOT}` é o que separa pacote de cópia.** O `hooks.json` do
> `AmFlowPlugins:plugins/worker` usa exatamente essa variável, e o `settings.json` daqui usa
> `${CLAUDE_PROJECT_DIR}` — mesma estrutura, âncora diferente. Empacotar sem a troca produz um
> plugin que procura os hooks dentro do projeto de quem instalou, e falha em silêncio.

**O que deliberadamente não viaja, e por quê:**

| Não viaja | Razão |
|---|---|
| `.claude/guardrails.json` | é a instância — a regra `ddl-remoto` é sobre o Supabase do AmFlow. O **mecanismo** (`guardrail.py` e o hook) viaja; quem instala declara as próprias regras |
| `.claude/rules/*` | plugin não empacota rules (*Restrições conhecidas*). É o que `materializar` existe para resolver |
| `scripts/tests/` | os testes leem `docs/plan/system/` e o acervo deste repositório: são a prova **daqui**, não componente do método |
| `docs/` | plano, norma e estudo são o registro deste projeto. A norma é citada pela skill, não copiada para dentro dela |

> **`materializar` recebe a origem, e não carrega catálogo.** A operação copia **um** arquivo de
> guideline para `<projeto>/.claude/rules/`; o plugin não embarca guideline nenhuma, porque toda
> guideline que existe hoje aqui é instância deste repositório. Fecha o que a `L-23` deixou em
> aberto: o `estudo-runtime-e-dependencias.md` **não** viaja — é evidência citada, não mecanismo.

**O pacote não é versionado.** `destino` default é `dist/decode-and-code/`, que entra no
`.gitignore`. Árvore construída e commitada envelhece em silêncio a cada mudança da fonte, e é
exatamente a divergência de 2026-08-01 que o plano registra. Publicar é ato humano, e reconciliar
é a `0001-17`.

## Sequência

1. Escrever `.claude-plugin/plugin.json` na raiz do repositório — `name`, `description`, `version`, `author` —, que é a fonte única do nome e da versão do pacote.
2. Escrever `empacotar.construir(destino)`: apaga `destino` se existir, copia o manifesto, a skill sem `scripts/tests/` nem `__pycache__`, e os quatro hooks — reescrevendo o `project:` do `SKILL.md` copiado para o nome do plugin, que é a mesma classe da troca de âncora do passo seguinte.
3. Gerar `hooks/hooks.json` a partir do bloco `hooks` de `.claude/settings.json`, trocando a âncora `${CLAUDE_PROJECT_DIR}/.claude/hooks` por `${CLAUDE_PLUGIN_ROOT}/hooks`.
4. Escrever `empacotar.verificar(destino)` com **duas** checagens: o nome do repositório de origem em qualquer arquivo, e `CLAUDE_PROJECT_DIR` **dentro de `hooks/`**. Nome de arquivo que o mecanismo lê e caminho default que ele resolve são mecanismo, não instância, e não entram na lista.
5. Escrever `empacotar.materializar(origem, projeto)`: copia um arquivo de guideline para `<projeto>/.claude/rules/`, levantando `FileExistsError` se o destino já existir.
6. Acrescentar `dist/` ao `.gitignore`.
7. Escrever `tests/test_empacotamento.py` com as duas naturezas — fixture sintética para o mecanismo, e **um caso que constrói deste repositório** —, corrigindo na fonte o que o caso real acusar.
8. Rodar o gate e relatar.

## Arquivos

| Caminho | O que muda |
|---|---|
| `.claude-plugin/plugin.json` | **novo** — o manifesto, fonte única de nome e versão |
| `.claude/skills/decode-and-code/scripts/empacotar.py` | **novo** — `construir`, `verificar` e `materializar` |
| `.claude/skills/decode-and-code/SKILL.md` | a norma passa a ser citada por `<plan_root>`, sai o ponteiro para um plano que já não está no `_inbox`, e a nota de migração provisória dá lugar à dependência que o pacote não resolve |
| `.claude/skills/decode-and-code/scripts/porte.py` | `_CONTEUDO_INICIAL` deixa de gravar o nome deste repositório no arquivo do projeto que instalar |
| `.gitignore` | passa a ignorar `dist/` |
| `.claude/skills/decode-and-code/scripts/tests/test_empacotamento.py` | **novo** — o teste declarado |
| `docs/plan/system/modelo-dev-units.md` | a seção curta que diz o que o pacote leva, o que não leva, e por quê |

## Dependências

A `0001-01`, pelo `config.json` que já tirou caminho fixo dos scripts — o pacote depende de a skill
resolver caminho por configuração, não por suposição. A `0001-10`, pelo `registry.py`: `materializar`
entrega o arquivo em `.claude/rules/`, e é o registry que o liga e desliga depois.

## Normas aplicáveis

| Norma | Onde |
|---|---|
| Invariante 2 — nada específico de projeto viaja no plugin | [`CLAUDE.md`](../../../../.claude/CLAUDE.md) |
| Guideline é instância e nunca viaja no plugin; o mecanismo é o que o plugin empacota | [`modelo-dev-units.md`](../../system/modelo-dev-units.md), seção *Camada normativa* |
| Materializar é cópia versionada, não symlink — e não pode ser automático | [`0001-decode-and-code-foundation.md`](0001-decode-and-code-foundation.md), *O plugin não pode enviar regras* |
| Ligar e desligar guideline é operação, não edição de arquivo | `.claude/skills/decode-and-code/scripts/registry.py` |

## Critério de aceite

`empacotar.construir` produz, em `tempfile`, uma árvore com `.claude-plugin/plugin.json`,
`skills/decode-and-code/SKILL.md`, os scripts da skill e os quatro hooks — e **sem**
`scripts/tests/`, sem `__pycache__`, sem `guardrails.json` e sem `docs/`. Cada ausência é um caso do
teste, não uma afirmação da prosa.

O `hooks/hooks.json` gerado declara os mesmos quatro eventos do `settings.json` e **nenhuma**
ocorrência de `CLAUDE_PROJECT_DIR`: os quatro comandos ancoram em `${CLAUDE_PLUGIN_ROOT}`. O teste
compara o conjunto de eventos dos dois arquivos, em vez de reescrever a lista.

`empacotar.verificar` devolve `[]` sobre a árvore recém-construída, **e devolve problema** sobre uma
árvore em que o nome do projeto de origem foi plantado de propósito. Os dois casos andam juntos: sem
o segundo, `verificar` poderia devolver `[]` sempre e o teste não veria.

A âncora `CLAUDE_PROJECT_DIR` conta **dentro de `hooks/`** e não conta fora: o teste planta a string
nos dois lugares e afirma que só a de dentro vira problema. Fora dela é dado — a constante que
orienta a própria troca —; dentro é hook que vai procurar o próprio código na árvore de quem
instalou.

**Um caso constrói deste repositório e exige `verificar() == []`.** Fixture prova o mecanismo,
nunca a instância: sem esse caso, `verificar` responde `[]` sobre uma árvore montada para não ter
marcador nenhum, enquanto o pacote real sai com o nome do projeto dentro. Foi o que aconteceu na
primeira entrega, e foi esse caso que o expôs.

`empacotar.materializar` escreve a guideline em `<projeto>/.claude/rules/` com conteúdo idêntico ao
da origem, e levanta `FileExistsError` sem tocar no arquivo quando o destino já existe — o teste
confere o conteúdo preservado depois da recusa.

**A suíte inteira continua verde**, e nenhum teste desta unidade escreve fora do `tempfile`.

## Verificação

```
./scripts/test-python.sh .claude/skills/decode-and-code/scripts/tests/test_empacotamento.py
```

## Fonte

- [`0001-decode-and-code-foundation.md`](0001-decode-and-code-foundation.md), *Escopo* → *Fase 5*
- `D-21` e `D-22` — a forma do pacote e o que ele não leva
- Estrutura medida em 2026-08-26 nos plugins instalados em `~/.claude/plugins/marketplaces/`:
  `.claude-plugin/plugin.json`, `hooks/hooks.json` com `${CLAUDE_PLUGIN_ROOT}`, componentes na raiz
