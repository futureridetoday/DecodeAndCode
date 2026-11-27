---
# about
name: release
type: doc
project: ""
description: Como o repositório se relaciona com o pacote do plugin e o procedimento de release, de dev para main e para o GitHub Release
tags: [manutencao, release, empacotamento]

# history
author: Bortoli
created: 2026-11-27
status: stable
version: 1.0.0
updated: ""

# system
scope: project
source: ""
auto_load: false
checksum: ""
dependencies: [packaging]
---

# Release

Documentação de manutenção, vinda do README (guia do codex, *Documentação de manutenção*). O que o
pacote leva e como se audita está em [`packaging.md`](packaging.md).

## Como este repositório se relaciona com o pacote

`.claude/` é a **fonte** — as skills e a pasta compartilhada `decode-and-code/` (codex, procedimentos,
módulos e scripts), os hooks e o manifesto (`.claude/plugin.json`). `dist/decode-and-code/` é staging
**gitignorado**: `empacotar.construir()` o escreve do zero a cada build, e nada dali é commitado. O
que se distribui é o **zip** que `empacotar.empacotar_zip()` produz a partir dessa mesma árvore,
publicado como asset de um GitHub Release e referenciado por `source: archive` (`url` + `sha256`) no
`marketplace.json`.

```bash
python3 -c "import sys; sys.path.insert(0, '.claude/skills/decode-and-code/scripts'); import empacotar; empacotar.construir()"
```

Para testar sem instalar, depois do build:

```bash
claude --plugin-dir dist/decode-and-code
```

## Procedimento de release

Desenvolvimento acontece em **`dev`** (staging, branch default). O release promove `dev` → `main`
(produção) e publica dali — a instalação por comando fixa `@main`. O repositório precisa estar
**público**: `source: archive` baixa o asset por URL anônima, e um repo privado devolve `404` para
qualquer cliente sem token.

1. Em `dev`: bump de `version` em **`.claude/plugin.json` e na entrada do plugin no
   `marketplace.json`** — os dois têm que concordar (`claude plugin tag` valida isso)
2. Em `dev`: `empacotar_zip()` — constrói, roda `verificar()`/`validar()` sobre o staging, zipa e
   imprime o caminho do zip e o SHA-256
3. Em `dev`: preencher no `marketplace.json` a `url` (determinística —
   `…/releases/download/v<versão>/decode-and-code-<versão>.zip`) e o `sha256` do passo 2; commit
4. Promover `dev` → `main` (merge, sem force) e push
5. Em `main`: `gh release create v<versão> decode-and-code-<versão>.zip --target main --title "Decode and Code <versão>" --notes "…"`
6. `/plugin marketplace update future-ride-today` — e os usuários rodam a atualização do README
