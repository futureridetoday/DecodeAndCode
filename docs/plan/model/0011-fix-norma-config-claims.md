---
# about
name: fix-norma-config-claims
type: plan
project: DecodeAndCode
description: A norma promete que o projeto que instala declara runner e core no `config.json`, mas o código lê o `config.json` de dentro do plugin e não tem chave de core — as duas frases passam a dizer o que o código faz, e o desenho da config de projeto fica registrado para quando houver consumidor
tags: [decode-and-code, norma, config, runner, verificacao]

# alvo
plan_id: "0011"
plan_size: pequeno
core: model
module: fix-norma-config-claims
block: ""

# history
author: Claude
created: 2026-11-19
status: done
version: 1.0.0
updated: ""
approved_by: Bortoli
approved_at: 2026-11-19

# system
scope: project
auto_load: false
dependencies: []
---

# A norma para de prometer config de projeto que o código não lê

## Objetivo

**Clarificar.** Duas frases da norma afirmam um comportamento que o código não tem, e quem as segue
erra sem aviso. Métrica: **zero** afirmações na norma de que o projeto que instala declara algo no
`config.json` (hoje: duas). Beneficiário: quem lê a norma para configurar um projeto consumidor, e o
modelo que a recebe por `dc.py normas` ou `explicar`.

| Linha | A norma diz | O código faz |
|---|---|---|
| 101 | Core: *"declarada por projeto, em `config.json`"* | `lib._DEFAULTS` não tem chave de core; `config()` recusa campo desconhecido |
| 1198 | *"o projeto declara o seu runner em `runners`, no `config.json`"* | `lib._config_path()` lê o `config.json` **do plugin** (irmão de `scripts/`). Instalado, ele mora em `~/.claude/plugins/cache/future-ride-today/decode-and-code/<versão>/` — pasta nova a cada versão, então editar ali se perde no update |

O que o projeto **consegue** hoje: fornecer o script em `scripts/test-python.sh` ou
`scripts/test-ts.sh` na própria raiz (o caminho do runner resolve contra a raiz do projeto). O que
**não** consegue: declarar extensão nova (`.swift`, `.go`, …), nem trocar o caminho do script.

**Evitar.**

| Alternativa | Por que não basta |
|---|---|
| Implementar a config de projeto agora | Reprovada pelo gate A: não há consumidor fora de `.py`/`.ts` no porte grande (resposta do humano, 2026-11-19). O desenho decidido fica abaixo, para não ser refeito |
| Deixar o `H-14` aberto e a norma como está | A norma continua mandando fazer o que não funciona; é a falha que o invariante *uma fonte por fato* existe para impedir |

**Reduzir.** Só texto da norma, duas frases. Nenhum código, nenhum teste novo.

## Gates

| Gate | Resposta |
|---|---|
| **A — necessidade real** | **Sim, para a correção de texto:** a divergência existe hoje e foi medida lendo `lib.py` e a cópia instalada do 2.3.1. **Não, para o código** (config de projeto e detecção de skip fora de `unittest`/`vitest`): nenhum projeto consumidor fora de `.py`/`.ts` usa o porte grande agora |
| **B — mínimo viável** | Cortado: a chave de core (não existe mecanismo, só a frase sai); a config de projeto e o contrato do runner (vão como desenho registrado, não como entrega) |

## Solução

1. **Linha 101** — `Core → fronteira de ownership: declarada pelo plano, no frontmatter (`core:`)`.
   É onde o core é declarado de fato: `scaffold.aprovar` o lê do plano para criar a estrutura.
2. **Linha 1198** — trocar a promessa pelo estado real: o mapa `runners` (extensão → script) vem do
   `config.json` do plugin, hoje `.py` e `.ts`; o **script** é do projeto, no caminho que o mapa
   declara, relativo à raiz; extensão fora do mapa é recusada pelo gate de saída (*"extensão de
   teste sem runner declarado"*). Uma linha apontando para *Desenho adiado*, abaixo, enquanto o
   plano não for aprovado; depois, para este plano.

Toca só `docs/plan/system/modelo-dev-units.md`.

## Desenho adiado — config de projeto

Decidido pelo humano em 2026-11-19, para quando o gate A passar (gatilho: o primeiro projeto fora de
`.py`/`.ts` que derive unidades no porte grande):

| # | Decisão | Motivo |
|---|---|---|
| D-01 | A config de projeto mora em `<projeto>/.claude/decode-and-code.json`, sobreposta à do plugin | Ao lado do `guardrails.json`, que já é instância em `.claude/`; achada pela raiz, sem depender de `plan_root` |
| D-02 | O projeto sobrepõe **só** `runners` | Única chave com dor medida. `root_markers` seria circular (a raiz é achada por ele antes de a config do projeto ser lida); `move_script` e `marketplace` são do plugin; `plan_root` não tem incidente |
| D-03 | Execução incompleta fora de `unittest`/`vitest` é **contrato do runner**: o script do projeto sai com código diferente de zero em skip ou zero teste. Os regex atuais de `verificacao._execucao_incompleta` ficam | O runner já é código do projeto; nenhum parser novo no plugin |

## Oráculo

- `grep -n "config.json" docs/plan/system/modelo-dev-units.md`: nenhuma ocorrência diz que o
  **projeto** declara algo no `config.json`.
- A linha do core cita o campo `core:` do frontmatter do plano.
- A linha do runner nomeia as extensões do mapa atual e a mensagem de recusa do gate de saída.

Critério de saída: os três itens acima, conferidos pelo humano no diff.

## Lacunas

Registradas no `review-plan` de 2026-11-19, sem resolver.

| # | Lacuna | Detalhe |
|---|---|---|
| L-01 | **A correção não chega sozinha a quem já instalou** | A norma viaja em `reference/` e o `bootstrap` nunca sobrescreve a cópia do projeto: chega ao pacote só no próximo release, e projetos existentes mantêm o texto errado — o AmFlow tem a linha do core idêntica. O plano não diz se pede release nem se o AmFlow recebe a correção |
| L-02 | **O gatilho do desenho adiado não tem quem o lembre** | `D-01` a `D-03` ficam num plano que fecha `done`; nada os traz de volta quando o primeiro projeto fora de `.py`/`.ts` derivar unidades. Candidato: entrada `revisitar` no huddle |
| L-03 | **As frases são localizadas por número de linha** | "Linha 101" e "linha 1198" mudam com qualquer edição da norma; citar seção e frase em vez de número |

## Fonte

- `H-14` do huddle `bortoli-rafael`, aberto em 2026-11-19
- `lib.py` — `_DEFAULTS`, `_config_path`, `config`; `verificacao.py` — `_comando`, `_execucao_incompleta`
- [`modelo-dev-units.md`](../system/modelo-dev-units.md), *Hierarquia estrutural* e *Bootstrap → O que não cria*
- Cópia instalada: `~/.claude/plugins/cache/future-ride-today/decode-and-code/2.3.1/skills/decode-and-code/config.json`
