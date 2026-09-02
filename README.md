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

### Para desenvolver ou testar sem instalar

```bash
claude --plugin-dir dist/decode-and-code
```

```bash
claude --plugin-url <url do asset do Release>
```

## O que vem junto

| Componente | O que faz |
|---|---|
| Skill `decode-and-code` | Os três modos — revisar um plano, derivar estrutura e unidades, implementar uma unidade em cold-start |
| Agent `planner` | Revisa um plano antes da aprovação, e deriva as unidades de um plano aprovado |
| Agent `developer` | Implementa uma unidade já derivada, em cold-start |
| Comando `/implement` | Dispara a implementação de uma unidade |
| Comando `/delegate` | Delega a unidade ao `developer` em sessão limpa |
| Hooks | Carregam a norma e as guidelines ativas na abertura da sessão e após compactação |

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

1. `empacotar_zip()` — constrói, roda `verificar()`/`validar()` sobre o staging, zipa e imprime o
   caminho do zip e o SHA-256
2. `gh release create v<versão> decode-and-code-<versão>.zip --title "Decode and Code <versão>" --notes "…"`
3. Copiar a URL do asset publicado e o SHA-256 para a entrada do plugin no `marketplace.json`
   (`url`, `sha256`, `version`)
4. Commit, push
5. `/plugin marketplace update future-ride-today`

## Desenvolvimento

```bash
bash scripts/test-python.sh
```

Exige Python 3.10 explícito — ver [`language-policy.md`](docs/plan/system/language-policy.md) para
a medição de ambientes que fixou o alvo.

A norma completa fica em [`modelo-dev-units.md`](docs/plan/system/modelo-dev-units.md).
