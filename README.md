# decode-and-code

Plugin do Claude Code que empacota o método **decode-and-code**: a norma em camadas (princípio,
guideline, guardrail), o porte de plano, e o ciclo `plano → unidade → cold-start`.

O problema que ele resolve: uma sessão nova não sabe o que a anterior sabia. O método faz o plano
carregar essa diferença — cada unidade é escrita para ser executada por alguém que chega sem
contexto, e o critério de que ela está pronta é justamente esse.

## Instalação

### Por comando

```bash
/plugin marketplace add futureridetoday/DecodeAndCode
```

```bash
/plugin install decode-and-code@future-ride-today
```

Os dois comandos rodam dentro do Claude Code. O primeiro registra o marketplace deste repositório;
o segundo instala o plugin a partir dele.

### Por upload

Customize → Plugins → *upload a custom plugin file*, com o zip anexado ao
[Release](https://github.com/futureridetoday/DecodeAndCode/releases) mais recente
(`decode-and-code-1.0.0.zip`).

### Atualização

Quando sai uma versão nova do plugin:

```bash
/plugin marketplace update future-ride-today
```

```bash
/plugin update decode-and-code@future-ride-today
```

O primeiro refresca o metadado do marketplace (nova `version`, `url`, `sha256`); o segundo baixa o
zip do Release novo, confere o `sha256` e instala. **Reiniciar o Claude Code** para aplicar — ou
usar o painel `/plugin` → aba Installed, que sinaliza *update available*.

Mudança que fica só no repositório (`README.md`, `docs/`, `docs/plan/`) não entra no pacote e não
exige nada de quem instalou.

### Para desenvolver ou testar sem instalar

Depois de `empacotar.construir()` (ver *Como este repositório se relaciona com o pacote*), que
escreve o staging em `dist/decode-and-code/`:

```bash
claude --plugin-dir dist/decode-and-code
```

Ou direto do asset publicado, sem build local:

```bash
claude --plugin-url https://github.com/futureridetoday/DecodeAndCode/releases/download/v1.0.0/decode-and-code-1.0.0.zip
```

## Como usar o Decode And Code

Um documento por recurso, em [`docs/recursos/`](docs/recursos/), no formato *o que é · problema que
resolve · como funciona · como usar · exemplos · fundamentação · base de conhecimento · limites*.

| Tipo | Recurso | O que faz | Doc |
|---|---|---|---|
| skill | `decode-and-code` | Os três modos — `review` um plano, `derive` estrutura e unidades, `implement` uma unidade em cold-start | [decode-and-code.md](docs/recursos/decode-and-code.md) |
| agent | `planner` | Revisa um plano antes da aprovação, e deriva as unidades de um plano aprovado (Opus) | [planner.md](docs/recursos/planner.md) |
| agent | `developer` | Implementa uma unidade já derivada, em cold-start isolado (Sonnet) | [developer.md](docs/recursos/developer.md) |
| command | `/decode-and-code:implement` | Roda o modo `implement` na sessão atual — pensado para sessão nova | [implement.md](docs/recursos/implement.md) |
| command | `/decode-and-code:delegate` | Delega a unidade ao agent `developer` sem sair da sessão de orquestração | [delegate.md](docs/recursos/delegate.md) |
| hooks | 4 hooks | Guardrail do projeto (`PreToolUse`) e anúncio de norma/guidelines/subagente — no harness, sem custo de contexto | [hooks.md](docs/recursos/hooks.md) |

O plugin carrega o **mecanismo**. Guardrail e guideline são do projeto que instala — o método os
materializa lá, e nunca viaja com os deste repositório.

## O ciclo

| # | Etapa | Onde |
|---|---|---|
| 1 | O plano nasce | `docs/plan/_inbox/` |
| 2 | Revisão | modo `review` |
| 3 | **Aprovação** | humano |
| 4 | Derivação em unidades | modo `derive` |
| 5 | Implementação, uma unidade por vez | modo `implement`, em cold-start |

Quem executa uma unidade entrega arquivos e relatório, e não commita. O estado de cada unidade
(`spec` → `wip` → `verified`) é **projetado a partir do teste**, nunca editado à mão.

## Como este repositório se relaciona com o pacote

`.claude/` é a **fonte** — a skill, os hooks, os agentes, os comandos e o manifesto
(`.claude/plugin.json`). `dist/decode-and-code/` é staging **gitignorado**: `empacotar.construir()`
o escreve do zero a cada build, e nada dali é commitado. O que se distribui é o **zip** que
`empacotar.empacotar_zip()` produz a partir dessa mesma árvore, publicado como asset de um GitHub
Release e referenciado por `source: archive` (`url` + `sha256`) no `marketplace.json`.

```bash
python3 -c "import sys; sys.path.insert(0, '.claude/skills/decode-and-code/scripts'); import empacotar; empacotar.construir()"
```

### Procedimento de release

O repositório precisa estar **público**: `source: archive` baixa o asset por URL anônima, e um repo
privado devolve `404` para qualquer cliente sem token — inclusive `claude --plugin-url` e
`/plugin marketplace add`.

1. Bump de `version` em **`.claude/plugin.json` e na entrada do plugin no `marketplace.json`** — os
   dois têm que concordar (`claude plugin tag` valida isso)
2. `empacotar_zip()` — constrói, roda `verificar()`/`validar()` sobre o staging, zipa e imprime o
   caminho do zip e o SHA-256
3. `gh release create v<versão> decode-and-code-<versão>.zip --title "Decode and Code <versão>" --notes "…"`
4. Copiar a URL do asset publicado e o SHA-256 para a entrada do plugin no `marketplace.json`
   (`url`, `sha256`)
5. Commit, push
6. `/plugin marketplace update future-ride-today` — e os usuários rodam a *Atualização* acima

## Desenvolvimento

```bash
bash scripts/test-python.sh
```

Exige Python 3.10 explícito — ver [`language-policy.md`](docs/plan/system/language-policy.md) para
a medição de ambientes que fixou o alvo.

A norma completa fica em [`modelo-dev-units.md`](docs/plan/system/modelo-dev-units.md).
