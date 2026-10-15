---
# ── claude code — campos nativos ──────────────────────────────────────────────
name: review-plan
description: |
  Revisa um plano antes da aprovação, com os seis checks da norma de Unidades de Desenvolvimento — parte por script, parte por julgamento.

  Use when o usuário pede para revisar um plano do _inbox antes da aprovação.

  <example>
  Context: plano novo escrito no _inbox, ainda não aprovado
  user: "revise o plano docs/plan/_inbox/catalogo.md"
  commentary: modo review — os seis checks, isolando o que o script cobre (concorrência, fontes citadas) do que exige julgamento
  </example>

disable-model-invocation: false
user-invocable: true

allowed-tools: "Read Write Edit Glob Grep Bash(python3 \"${CLAUDE_SKILL_DIR}/dc.py\" *) Bash(python3 ${CLAUDE_SKILL_DIR}/dc.py *)"

argument-hint: "<plano>"
arguments: [target]

model: opus
effort: ""
context: ""
shell: bash

# ── amflow — rastreabilidade ───────────────────────────────────────────────────
type: skill
project: DecodeAndCode
author: Bortoli
created: 2026-10-15
status: draft
version: 1.0.0
updated: "2026-10-15"
scope: project
auto_load: false
tags: [decode-and-code, skill, plano, review]
dependencies: []

hub_id: ""
source: local
---

# review-plan

Esta skill executa o modo `review` da norma `<plan_root>/system/modelo-dev-units.md` — `plan_root` resolvido pelo `config.json` em `${CLAUDE_SKILL_DIR}/../decode-and-code/`. Todo determinismo (gates, contagem, projeção de estado) fica nos scripts em `${CLAUDE_SKILL_DIR}/../decode-and-code/scripts/` (norma, seção *Fronteira skill / script*); a skill cuida do que exige julgamento.

## Argumentos

- `$target` — caminho do plano a revisar

## Instruções

### `review <plano>`

Os seis checks são os da norma (*Modo `review` — os seis checks*) — esta seção descreve só o **como**, para não duplicar o que já está lá (regra anti-drift, norma, seção *Camada normativa*).

1. **Determinístico, roda primeiro:**
   - **Nome** — `python3 "${CLAUDE_SKILL_DIR}/dc.py" validar-nome <nome>`, com o stem do arquivo (`_inbox/<nome>.md` → `nome`).
   - **Concorrência** — `python3 "${CLAUDE_SKILL_DIR}/dc.py" concorrencia <plano>` lê `core`/`module` do frontmatter do plano e varre a região `planos` de `_planos.md` por uma linha `em desenvolvimento` no mesmo core **ou** módulo (norma, *Avaliação de escopo*). Encontrada (código `1`), a linha inteira é a evidência citada no achado.
   - **Fontes citadas** — cada link relativo do corpo do plano resolve em disco.
   - Plano sem `core` no frontmatter: achado bloqueante — o `concorrencia` responde "não verificável" (código `1`), a concorrência fica registrada assim, e a revisão **não aborta**.
2. **Independência** — audita a seção `## Independência` do plano contra o teste da norma ("A e B passam isolados?"). Seção ausente é achado bloqueante, não silêncio.
3. **Tamanho como contexto** — unidades previstas, cores e módulos tocados, lidos da seção `## Escopo`. Relatar, nunca reprovar (decisão 26).
4. **Julgamento restante** — erros conceituais, erros de arquitetura, adequação das fontes ao escopo.
5. **Lacunas** — cada uma nova entra como `L-XX`, sem tentar resolvê-la.
6. **Relatório** — uma linha por achado: check, veredito (`bloqueante` | `aviso`) e origem (`comando` | `julgamento`). Sinalizar divisão não é reprovar — se o humano decide não dividir, o porquê fica registrado no plano, não neste relatório. Encerra sem aprovar — quem aprova é o humano.

Composição via `dc.py` — ponto de entrada único, o que o `allowed-tools` libera; rode-o do diretório do projeto. **Rode o comando exatamente como está escrito** — sem variável de shell, sem tirar as aspas e sem trocar o caminho —, porque a liberação de permissão casa o texto do comando. Subcomandos: `validar-nome` e `concorrencia`.

## Referências

- Norma: `<plan_root>/system/modelo-dev-units.md` — `plan_root` é o do `config.json`, e
  `docs/plan` é só o default. Vive no projeto que usa a skill, e é lá que a skill a lê.

## Começando um projeto do zero

Um projeto que acabou de instalar o plugin não tem estrutura nenhuma sob `plan_root` — nem
`_planos.md`, nem `_inbox/`, nem a norma que as skills do método citam. `python3 "${CLAUDE_SKILL_DIR}/dc.py" bootstrap [<projeto>]`
cria o que falta (o padrão é o diretório atual), item a item e sem sobrescrever o que já existir:

| Cria | Onde |
|---|---|
| `_planos.md`, com os marcadores e o cabeçalho da tabela | `<plan_root>/` |
| `_inbox/` | `<plan_root>/` |
| A norma-mecanismo, materializada de `reference/` (na pasta compartilhada `decode-and-code/`) ou do checkout | `<plan_root>/system/modelo-dev-units.md` |
| `.claude/` | raiz do projeto |

**Idempotente:** rodar de novo sobre um projeto que já tem parte disso não toca no que já está lá —
inclusive a norma, se o projeto já a tiver editado.

Composição via `dc.py` — ponto de entrada único, o que o `allowed-tools` libera; rode-o do diretório do projeto: `bootstrap`.
