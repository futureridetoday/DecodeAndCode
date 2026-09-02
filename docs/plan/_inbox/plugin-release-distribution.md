---
# about
name: plugin-release-distribution
type: plan
project: DecodeAndCode
description: A distribuição do plugin migra de dist/ commitado para asset de GitHub Release (source archive), a identidade passa a future-ride-today / Decode and Code, e a norma para de se contradizer sobre empacotamento
tags: [decode-and-code, plugin, marketplace, distribuicao, release, github]

# alvo
plan_id: ""
plan_size: medio
core: model
module: plugin-release-distribution
block: ""

# history
author: Bortoli
created: 2026-09-01
status: approved
version: 1.0.0
updated: ""
approved_by: Bortoli
approved_at: 2026-09-01

# system
scope: project
auto_load: false
dependencies: []
---

# Decode and Code se distribui como plugin: marketplace + upload + release zip

> **Este plano é executado direto numa sessão, não derivado em unidades.** Decisão do humano em
> 2026-09-01: a correção é pequena, o escopo está fechado, e o limite de contexto da sessão de
> planejamento acabou. O `_inbox/` aqui é armazenamento durável para a sessão de execução em
> cold-start, não entrada no fluxo `review → aprovação → derivação`.

## O que foi medido

Sessão de 2026-09-01. O plano `0004` fechou como `concluído`, mas a forma de distribuição que ele
produziu tem três defeitos, e um deles é processo:

| Fato | Evidência |
|---|---|
| **`dist/decode-and-code/` está commitado no `main`** (35 arquivos) | `find dist -type f`; `.gitignore` não contém `dist/`. A `D-09` do `0004` removeu `dist/` do `.gitignore` **fora de unidade, em 2026-09-01, sem aprovação humana registrada** — revertendo a `D-21` do plano `0001`, que foi decisão fundacional. `D-09` diz *"a distribuição não deixa alternativa"* — mas deixa (ver *Fonte*, doc oficial) |
| **A norma se contradiz** | [`modelo-dev-units.md`](../system/modelo-dev-units.md), subseção `#### Empacotamento`: por volta da linha 320 diz *"`dist/decode-and-code/` saiu do `.gitignore`… a sincronia virou caso de teste"*; ~30 linhas depois diz *"O pacote não é versionado — `dist/` entra no `.gitignore`"*. Invariante nº 1 do `CLAUDE.md` (*uma fonte por fato*) quebrado no documento central do método |
| **O install nunca foi provado ponta a ponta** | `0004`, `L-01` segue aberta (*"não se sabe se `skills:` carrega de verdade"*); *Restrições conhecidas* do `0004`: *"A prova final de instalação é ato humano, reportado"*. O plano fechou `done` sem ninguém rodar `/plugin install decode-and-code@<marketplace>` de verdade |

**A doc oficial do Claude (consultada em 2026-09-01) resolve o primeiro fato.** `marketplace.json`
aceita `source` do tipo **`archive`**: `{ "source": "archive", "url": "<https>", "sha256": "<64 hex>" }`
— o Claude Code baixa o pacote de uma URL HTTPS e **não** exige árvore construída no repositório
clonado. Um GitHub Release com o zip anexado dá essa URL, estável, e o mesmo zip serve o caminho de
upload no app (Customize → Plugins → *upload a custom plugin file*).

## Objetivo

Decode and Code se instala por três vias, cada uma alimentada pelo mesmo pacote:

| Via | Mecanismo |
|---|---|
| Comando no Claude Code | `/plugin marketplace add futureridetoday/DecodeAndCode` → `/plugin install decode-and-code@future-ride-today` |
| App / browser | Customize → Plugins → *upload a custom plugin file*, com o zip do Release |
| Marketplace comunitário (futuro) | submissão do repo, já no formato válido; `claude plugin validate` limpo |

O pacote construído vira **asset de GitHub Release**, referenciado por `source: archive`. O
repositório deixa de versionar a árvore construída. A norma passa a afirmar uma coisa só. O install
é provado antes de fechar.

## Decisões travadas

Tomadas pelo humano na sessão de planejamento, 2026-09-01. Não reabrir na execução.

| # | Decisão | Nota |
|---|---|---|
| T-1 | marketplace `name` = `future-ride-today`; `owner` = `{ "name": "Future Ride Today", "url": "https://github.com/futureridetoday" }` | kebab-case obrigatório no `name` (spec + `nomenclatura.validar_nome`); não colide com `amflow` |
| T-2 | plugin `name` = `decode-and-code` **inalterado** (é o namespace `decode-and-code:*`); `displayName` = `Decode and Code` | `displayName` é válido no `plugin.json` **e** na entrada do plugin dentro do `marketplace.json` (verificado no catálogo oficial) |
| T-3 | `source` do plugin = `{ "source": "archive", "url": "<asset do Release>", "sha256": "<digest>" }` | doc oficial `plugin-marketplaces`, *Zip Archive source*. `http://` é recusado; `sha256` é conferido a cada download |
| T-4 | pacote = zip anexado a **GitHub Release**, **não commitado**. Tag `v1.0.0`, asset `decode-and-code-1.0.0.zip` | reverte a `D-09`; restaura a intenção da `D-21` |
| T-5 | a `D-10` do `0004` **permanece** — raiz só `marketplace.json`, manifesto-fonte em `.claude/plugin.json` | está certa e alinhada ao spec |
| T-6 | licença = **MIT**, copyright `Future Ride Today`, 2026 | campo `license: "MIT"` no `plugin.json` **e** arquivo `LICENSE` na raiz com o texto |

## Escopo — os passos

Ordem sugerida. Passos 1–8 são locais: **não commitar, não fazer push**. Passo 9 é ato humano.

### 1 — Manifestos e licença

- **`.claude/plugin.json`** (fonte; `empacotar.construir` copia para `<pacote>/.claude-plugin/plugin.json`):
  - adiciona `"displayName": "Decode and Code"`
  - `author.name`: `Bortoli` → `Future Ride Today`
  - adiciona `"homepage"` e `"repository"` = `https://github.com/futureridetoday/DecodeAndCode`
  - adiciona `"license": "MIT"`
  - `name` (`decode-and-code`) e `version` (`1.0.0`) inalterados
- **`LICENSE`** na raiz do repositório: texto MIT padrão, `Copyright (c) 2026 Future Ride Today`
- **`.claude-plugin/marketplace.json`**:
  - `name`: `bortoli` → `future-ride-today`
  - `owner`: `{ "name": "Future Ride Today", "url": "https://github.com/futureridetoday" }`
  - entrada do plugin: adiciona `"displayName": "Decode and Code"`; `author.name` → `Future Ride Today`;
    `source` → objeto `archive`. No commit local, `url` e `sha256` ficam com placeholder explícito
    (`"url": "PENDENTE-RELEASE-v1.0.0"`, sem `sha256`) — o passo 9 preenche
  - `version` da entrada acompanha o `plugin.json` (`1.0.0`); bump conjunto a cada Release
  - `$schema` pode alinhar ao do catálogo oficial (`https://anthropic.com/claude-code/marketplace.schema.json`) — cosmético, ignorado em runtime

### 2 — Build passa a produzir zip (`empacotar.py`)

- `construir(destino)` volta a escrever numa área de staging **gitignorada** (mantém o default
  `dist/decode-and-code/`), como antes da `D-09`
- nova função `empacotar_zip(staging=None) -> (Path, str)`: constrói se `staging` for `None`, zipa a
  raiz do plugin, calcula SHA-256, devolve `(caminho_do_zip, sha256_hex)` e imprime os dois. Nome do
  zip: `decode-and-code-<version>.zip`, lendo `version` do `plugin.json`
- **Layout do zip — verificar, não supor**: primeira tentativa com a raiz do plugin no topo do
  archive (`.claude-plugin/plugin.json` no nível 0 do zip). Se o passo 9 mostrar que `--plugin-url`
  recusa, reempacotar com um único diretório-raiz `decode-and-code/` e re-testar. Registrar qual
  funcionou, no docstring da função e na norma
- `verificar()` (vazamento de instância) e `validar()` (`claude plugin validate`) rodam sobre o
  staging **antes** de zipar; zip só é escrito se os dois devolverem `[]`
- `.gitignore`: readiciona `dist/` e `*.zip`

### 3 — Testes (`.claude/skills/decode-and-code/scripts/tests/test_empacotamento.py`)

- **remove** `TestPacoteCommitadoEstaSincronizado` — não há mais pacote commitado para sincronizar
- **adiciona** (`TestEmpacotarZip` ou equivalente):
  - o zip contém a árvore esperada e `.claude-plugin/plugin.json` parseável no caminho previsto
  - `verificar()` e `validar()` limpos sobre o staging usado para o zip
  - `sha256` devolvido tem 64 hex e é idêntico para duas construções da mesma fonte
- mantém `TestPacoteRealEstaLimpo`, `TestValidarPelaFerramentaOficial`, `TestScaffoldImportaDoPacote`,
  `TestMaterializar`
- suíte inteira verde — somar as **duas** linhas `Ran` (`bash scripts/test-python.sh`), o total é a soma

### 4 — Remove a árvore construída do git

`git rm -r dist/decode-and-code/` (35 arquivos). Agora é staging gitignorado, substituído pelo asset
do Release. **Não commitar ainda** — deixar como remoção staged para o humano revisar no passo 9.

### 5 — Reconcilia a norma (`docs/plan/system/modelo-dev-units.md`)

- reescreve a subseção `#### Empacotamento — o que o plugin leva, e o que fica` para afirmar **uma
  coisa só**: build reproduzível; saída **não commitada**; distribuída como **zip de GitHub Release**
  referenciado por `source: archive` no `marketplace.json`; a raiz do repo carrega só
  `marketplace.json`; `.claude/plugin.json` é o manifesto-fonte, copiado pelo build para
  `<pacote>/.claude-plugin/plugin.json`
- **apaga** o parágrafo contraditório — o antigo *"O pacote não é versionado… `dist/` entra no
  `.gitignore`… Publicar é ato humano"* e o mais recente *"`dist/` saiu do `.gitignore`… sincronia
  virou caso de teste"* viram um só parágrafo coerente
- confere `docs/plan/system/registro-dev-units.md` — não pode reintroduzir a contradição nem citar
  `dist/` como versionado
- roda `test_normas_system.py` (invariante de instância na norma) — continua verde

### 6 — README.md

- **Instalação por comando**:
  ```
  /plugin marketplace add futureridetoday/DecodeAndCode
  /plugin install decode-and-code@future-ride-today
  ```
- **Instalação por upload**: Customize → Plugins → *upload a custom plugin file*, com
  `decode-and-code-1.0.0.zip` do Release
- **Dev/teste**: `claude --plugin-dir dist/decode-and-code` ou `claude --plugin-url <asset do Release>`
- **Procedimento de release** (novo bloco): build → `empacotar_zip()` → `gh release create v<x> …`
  + upload do asset → copiar a URL do asset e o `sha256` para a entrada do plugin no
  `marketplace.json` (`url`, `sha256`, `version`) → commit → push → `/plugin marketplace update future-ride-today`
- remove a instrução antiga que fala em `dist/` versionado / `@bortoli`

### 7 — CLAUDE.md (seção Arquitetura)

- `dist/decode-and-code/` volta a ser staging gitignorado — **não** pacote versionado; some a menção
  a `D-09`/pacote versionado
- pacote distribuído como asset de GitHub Release; `marketplace.json` com `source: archive`
- marketplace identificado como `future-ride-today`, owner `Future Ride Today`
- mantém a menção à `D-10` (raiz só marketplace, manifesto em `.claude/plugin.json`)

### 8 — Registro em `docs/plan/`

- `0004-installable-method.md`: a `D-11` **já foi adicionada** na sessão de planejamento (aponta para
  este plano). Conferir que o link resolve depois que este arquivo existir; nada mais a fazer lá
- **não** tocar `_planos.md` nem regiões entre `<!-- planos:start -->` / `<!-- backlog:start -->` —
  são projeção de script

### 9 — Primeiro Release + verificação ponta a ponta — **ato humano**

O executor **prepara e apresenta**; o humano autoriza o que sai do repositório.

1. Executor: roda `empacotar_zip()`, produz `decode-and-code-1.0.0.zip` + `sha256`, e mostra os dois
2. Executor: monta o comando `gh release create v1.0.0 <zip> --title "Decode and Code 1.0.0" --notes "…"`
   e a versão final do `marketplace.json` com `url`/`sha256` preenchidos — **apresenta, não roda**
3. Humano (ou executor com autorização explícita): `git push`, cria o Release, sobe o asset
4. Verificação, e **fecha a `L-01` do `0004`**:
   - `claude --plugin-url <URL do asset>` — carrega sem erro na aba `/plugin` → *Errors*?
     (se recusar, é o layout do zip — voltar ao passo 2, reempacotar com diretório-raiz, novo Release ou novo asset)
   - numa sessão real: `/plugin marketplace add futureridetoday/DecodeAndCode` →
     `/plugin install decode-and-code@future-ride-today`
   - confirmar: skill `decode-and-code` disponível; `/decode-and-code:implement` e `/decode-and-code:delegate` listados; `@decode-and-code:planner` e `@decode-and-code:developer` presentes; invocar `@decode-and-code:planner` e reler o log de ativação para saber se `skills:` traz a skill junto
5. Relatar o resultado — e, se algo falhar, é defeito **deste plano**, corrigido aqui

## Oráculo

| Alvo | Como se sabe que funcionou |
|---|---|
| Manifestos | `python3 -c "import json,sys; [json.load(open(p)) for p in ['.claude/plugin.json','.claude-plugin/marketplace.json']]"` sem erro; `displayName`/`owner`/`name` conforme T-1/T-2 |
| Build → zip | `empacotar_zip()` devolve `(zip, sha256)`; `unzip -l` mostra `.claude-plugin/plugin.json` + `skills/` + `agents/` + `commands/` + `hooks/hooks.json`; `verificar()`/`validar()` = `[]` |
| Repo limpo | `git status` mostra `dist/decode-and-code/` como deleção staged; `dist/` e `*.zip` no `.gitignore`; nenhum `.zip` rastreado |
| Norma | `grep -n "gitignore\|versionad\|não é versionado\|archive\|Release" docs/plan/system/modelo-dev-units.md` — uma narrativa só, sem contradição; `test_normas_system.py` verde |
| Suíte | `bash scripts/test-python.sh` — soma das duas linhas `Ran`, zero `FAILED` |
| Install real | passo 9.4 — skill + comandos + agentes carregam de um pacote instalado por `@future-ride-today` |

## Restrições

| Restrição | Origem |
|---|---|
| Português brasileiro na documentação; identificadores em inglês | `CLAUDE.md`, Invariantes |
| Nunca editar entre `<!-- backlog:start -->` / `<!-- planos:start -->` — é projeção | `CLAUDE.md` |
| `state` e `verified_at` nunca à mão | `CLAUDE.md` |
| PRs para `main` exigem revisão manual; nunca force push em `main` | `CLAUDE.md`, Git |
| Passos 1–8 não commitam nem fazem push; passo 9 é ato humano | este plano |
| Nada específico deste repositório pode vazar no pacote — `empacotar.verificar` é o guarda | `CLAUDE.md`, Invariante 2 |

## Notas de execução

Achado durante a execução dos passos 1–8, em 2026-09-01. Não reabre nenhuma decisão travada.

| Achado | Correção |
|---|---|
| `empacotar.verificar()` acusava falso positivo em `.claude-plugin/plugin.json`: os campos `repository`/`homepage` novos (`T-2`) apontam para o GitHub deste método, e o nome do repositório aparece ali sempre que o diretório local se chama como o repositório real — o caso comum, não vazamento do checkout que construiu o pacote | `verificar()` passou a excluir o manifesto do escaneamento de instância; ele é copiado verbatim (nunca passa por `_declarar_o_plugin`) e sua função é justamente declarar essa identidade fixa. Documentado no docstring de `verificar()` |

Zip real gerado e inspecionado nesta sessão: `.claude-plugin/plugin.json` no nível 0 do archive
(primeira tentativa do passo 2, layout confirmado contra a doc oficial — ver docstring de
`empacotar_zip`), `claude plugin validate` aprova sobre o zip extraído. A prova que falta é
`--plugin-url` contra um asset publicado de verdade — passo 9.

## Fonte

- Doc oficial do Claude, consultada em 2026-09-01:
  - [Plugins reference](https://code.claude.com/docs/en/plugins-reference) — estrutura da raiz de plugin, schema do `plugin.json`, `displayName`, `${CLAUDE_PLUGIN_ROOT}`, `claude plugin validate`
  - [Create and distribute a plugin marketplace](https://code.claude.com/docs/en/plugin-marketplaces) — schema do `marketplace.json`, formatos de `source` (incl. **`archive`** com `url` + `sha256`), repo como marketplace + plugin
  - [Discover and install plugins](https://code.claude.com/docs/en/discover-plugins) — `/plugin marketplace add`, `/plugin install nome@marketplace`, `--plugin-dir`, `--plugin-url`, múltiplos marketplaces
  - [Create plugins](https://code.claude.com/docs/en/plugins) — layout mínimo, teste local, submissão ao marketplace comunitário
  - [Use plugins in Claude (app/browser)](https://support.claude.com/en/articles/13837440-use-plugins-in-claude) — Customize → Plugins → upload de arquivo de plugin
- Catálogos reais conferidos no disco: `~/.claude/plugins/marketplaces/{amflow,claude-plugins-official}/.claude-plugin/marketplace.json` — `displayName` em entrada de plugin, ausência de `displayName` no nível do marketplace, múltiplos marketplaces coexistindo
- `0004-installable-method.md` — `D-09`, `D-10`, `D-11`, `L-01`; `0001`, `D-21`/`D-22` — o que o pacote leva e por quê
