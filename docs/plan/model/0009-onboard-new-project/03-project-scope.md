---
# about
name: project-scope
type: unit
project: DecodeAndCode
description: dc.py setup-escopo lê e, se pedido, habilita o plugin no .claude/settings.json do projeto — enabledPlugins e extraKnownMarketplaces, com o marketplace vindo de uma chave nova do config.json do pacote — preservando o resto do arquivo
tags: [decode-and-code, setup, escopo, settings, dc-py]

# alvo
core: model
module: onboard-new-project
block: ""
owner: model
unit_id: 0009-03
unit_type: dev

# verificação
state: verified
test: .claude/skills/decode-and-code/scripts/tests/test_escopo.py
verified_at: 2026-11-16

# history
author: Claude
created: 2026-11-15
status: draft
version: 1.0.0
updated: ""

# system
scope: project
auto_load: false
dependencies: []
---

# 0009-03 — project-scope

**Responsabilidade:** pôr o plugin no escopo do projeto (`D-09`), para que quem clonar trabalhe
com as mesmas guidelines e guardrails, sem estragar nada que o `.claude/settings.json` já tenha.

## Contrato

| Campo | Detalhe |
|---|---|
| **Entrada** | `escopo.estado(projeto)` e `escopo.habilitar(projeto)`; no `dc.py`, `setup-escopo [--aplicar]` com `lib.repo_root()` |
| **Saída** | `estado` → `{"habilitado": bool, "marketplace": bool}`. `habilitar` → `True` se escreveu, `False` se já estava tudo lá |
| **Auth** | — |
| **Efeito** | `habilitar` escreve só `<projeto>/.claude/settings.json`, criando-o se faltar; acrescenta `enabledPlugins["<plugin>@<marketplace>"] = true` e `extraKnownMarketplaces["<marketplace>"] = {"source": <source>}`; toda outra chave fica como estava |
| **Erro** | JSON inválido, ou raiz que não é objeto: `ValueError` e o arquivo intacto. `setup-escopo` sai `2` nesse caso; sem `--aplicar`, imprime o estado e sai `0` |

**O marketplace vem do `config.json` do pacote, chave nova `marketplace`** (`D-14`): o pacote não
leva o `.claude-plugin/marketplace.json`, que fica na raiz deste repositório. Valor, em
`.claude/skills/decode-and-code/config.json` e nos padrões de `lib._DEFAULTS`
(`lib.py:33-39`) — sem a chave nos padrões, `lib.config()` recusa o arquivo (`lib.py:84-85`):

```json
"marketplace": {
  "name": "future-ride-today",
  "plugin": "decode-and-code",
  "source": {"source": "github", "repo": "futureridetoday/DecodeAndCode"}
}
```

A forma das duas chaves do `settings.json` é a da [referência de settings](https://code.claude.com/docs/en/settings-reference):
`enabledPlugins` mapeia `plugin@marketplace` para booleano; `extraKnownMarketplaces` mapeia o nome do
marketplace para `{"source": {...}}`, e `github` com `repo` é uma das formas aceitas — o
`marketplace.json` na raiz do repositório é o caminho padrão. A mesma página diz que o
`extraKnownMarketplaces` do repositório só vale depois de a pessoa confiar na pasta, e o
[`discover-plugins`](https://code.claude.com/docs/en/discover-plugins) diz que habilitar no projeto
não baixa nada (`L-07` do plano): a skill explica isso, esta unidade só escreve.

**Escrita:** `json.dumps(dados, ensure_ascii=False, indent=2)` com quebra de linha final; a ordem das
chaves existentes é mantida e as novas entram no fim.

**O empacotador não acusa a identidade do plugin** (`DD-06` do plano, `L-13`).
`empacotar.verificar` procura em todo arquivo do pacote o nome do diretório que o construiu
(`_marcadores_instancia`), e o `repo` acima contém esse nome no checkout deste repositório. Antes de
procurar os marcadores, `verificar` tira do texto de cada arquivo a string exata
`lib.config()["marketplace"]["source"]["repo"]`. O marcador solto, fora dessa string, continua sendo
acusado em qualquer arquivo. O `repo` fica com a grafia do `marketplace.json` da raiz,
`futureridetoday/DecodeAndCode`, em `config.json` e em `lib._DEFAULTS`, sem contorno de caixa.

> **Refeita em 2026-11-16.** A primeira execução entregou `escopo.py`, `test_escopo.py`, o
> `setup-escopo` e a chave `marketplace` com o `repo` em minúsculas, para escapar do verificador.
> O que falta é o valor com a grafia acima, a isenção em `empacotar.verificar` e o teste dela.

## Sequência

1. Escrever `tests/test_escopo.py` contra um projeto em `tempfile`.
2. Acrescentar `marketplace` ao `config.json` e a `lib._DEFAULTS`, e ajustar `tests/test_config.py` se ele enumerar as chaves.
3. Escrever `escopo.py` com `estado` e `habilitar`, lendo o marketplace de `lib.config()["marketplace"]`.
4. O subcomando `setup-escopo` no `dc.py`, em `SUBCOMANDOS` de `tests/test_dc.py`, com um caso para cada saída.
5. A isenção em `empacotar.verificar`, com dois casos em `test_empacotamento.py`: o `repo` do `config.json` num arquivo do pacote não é acusado; o nome do projeto solto no mesmo arquivo é.
6. Rodar o teste declarado e a suíte inteira, inclusive `test_empacotamento.py`, que constrói o pacote a partir deste repositório.

## Arquivos

| Caminho | O que muda |
|---|---|
| `.claude/skills/decode-and-code/scripts/escopo.py` | **novo** |
| `.claude/skills/decode-and-code/scripts/tests/test_escopo.py` | **novo** — o teste declarado |
| `.claude/skills/decode-and-code/config.json` | chave `marketplace` |
| `.claude/skills/decode-and-code/scripts/lib.py:33-39` | `marketplace` em `_DEFAULTS` |
| `.claude/skills/decode-and-code/scripts/tests/test_config.py:42-60` | se enumerar as chaves |
| `.claude/skills/decode-and-code/scripts/dc.py` | handler e entrada no `_parser` |
| `.claude/skills/decode-and-code/scripts/tests/test_dc.py` | `SUBCOMANDOS` e os casos |
| `.claude/skills/decode-and-code/scripts/empacotar.py:338-366` | `verificar` tira o `repo` do marketplace antes de procurar os marcadores |
| `.claude/skills/decode-and-code/scripts/tests/test_empacotamento.py` | os dois casos da isenção, na classe que testa `verificar` |

## Dependências

Nenhuma unidade deste plano.

## Normas aplicáveis

| Norma | Onde |
|---|---|
| Por que o plugin vai para o escopo do projeto, e de onde vem o marketplace | [`0009-onboard-new-project.md`](0009-onboard-new-project.md), seção *Decisões* |
| O que a plataforma permite e o que não faz | [`0009-onboard-new-project.md`](0009-onboard-new-project.md), seção *Restrições da plataforma* |
| Escopo de projeto não instala nas outras máquinas | [`0009-onboard-new-project.md`](0009-onboard-new-project.md), seção *Lacunas* |
| Por que o verificador deixa passar o `repo` do marketplace | [`0009-onboard-new-project.md`](0009-onboard-new-project.md), seção *Decisões da derivação* |

## Critério de aceite

`habilitar` sobre um `settings.json` com `hooks` e `permissions` preserva as duas chaves byte a byte
no conteúdo serializado e acrescenta só `enabledPlugins` e `extraKnownMarketplaces`, com os valores
lidos de `lib.config()["marketplace"]`; uma segunda chamada devolve `False` e não muda o arquivo; sem
`settings.json`, cria um com só as duas chaves; com JSON inválido, levanta `ValueError` e o arquivo
fica idêntico. `lib.config()["marketplace"]["source"]["repo"]` é `futureridetoday/DecodeAndCode`, e
`empacotar.verificar` não o acusa, mas acusa o nome do projeto solto no mesmo arquivo. **A suíte
inteira continua verde.**

## Verificação

```
./scripts/test-python.sh .claude/skills/decode-and-code/scripts/tests/test_escopo.py
```

## Fonte

- [`0009-onboard-new-project.md`](0009-onboard-new-project.md), *Escopo* → *Fase 1*, unidade 03
- [settings-reference](https://code.claude.com/docs/en/settings-reference), `enabledPlugins` e `extraKnownMarketplaces`, lida em 2026-11-15
