---
# ── claude code — campos nativos ──────────────────────────────────────────────
name: review-plan
description: |
  Revisa um plano antes da aprovação, com os seis checks da norma de Unidades de Desenvolvimento — parte por script, parte por julgamento.

  Use when o usuário pede para revisar um plano do _inbox antes da aprovação.

  <example>
  Context: plano novo escrito no _inbox, ainda não aprovado
  user: "revise o plano docs/plan/_inbox/catalogo.md"
  commentary: modo review — os seis checks, isolando o que o script cobre (concorrência, formato do plano) do que exige julgamento
  </example>

disable-model-invocation: false
user-invocable: true

allowed-tools: "Read Write Edit Glob Grep Bash(python3 \"${CLAUDE_SKILL_DIR}/dc.py\" *) Bash(python3 ${CLAUDE_SKILL_DIR}/dc.py *)"

argument-hint: "<plano>"
arguments: [target]

model: opus
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
   - **Formato** — `python3 "${CLAUDE_SKILL_DIR}/dc.py" lint-plano <plano>` confere as seções exigidas pelo porte e o `plan_type`. Cada problema apontado é achado `bloqueante`, origem `comando`.
   - Plano sem `core` no frontmatter: achado bloqueante — o `concorrencia` responde "não verificável" (código `1`), a concorrência fica registrada assim, e a revisão **não aborta**.
2. **Independência** — audita a seção `## Independência` do plano contra o teste da norma ("A e B passam isolados?"). A presença por porte é do `lint-plano`, no passo 1 (norma, *O que cada porte carrega*: exigida no grande, dispensada no médio, recusada no pequeno); aqui se audita o conteúdo quando a seção existe.
3. **Tamanho e porte como contexto** — unidades previstas, cores e módulos tocados, lidos da seção `## Escopo`. Depois, uma linha `porte recomendado: <porte> — <porquê>`, pelas perguntas da norma (*O que cada porte carrega → Quando cada porte cabe*): cite a pergunta que decidiu e a evidência do plano — a decomposição em `## Escopo` (grande) ou `## Tarefas` (médio) ou, sem nenhuma das duas, a `## Solução` que mostra se há passos. Diferente do `plan_size` do esboço, o achado é `aviso`, origem `julgamento`, nunca `bloqueante`: reestruturar o plano para outro porte é decisão do humano. Relatar, nunca reprovar.
4. **Julgamento restante** — erros conceituais, erros de arquitetura e as fontes citadas: abra cada uma, confira que existe e avalie se é a certa para o escopo. No check de padrões, o plano declara o oráculo do seu `plan_type`: o que conferir está na coluna *`review-plan` confere* da norma (*Tipo de plano*).
5. **Lacunas** — cada uma nova entra como `L-XX`, sem tentar resolvê-la.
6. **Relatório** — uma linha por achado: check, veredito (`bloqueante` | `aviso`) e origem (`comando` | `julgamento`). Sinalizar divisão não é reprovar — se o humano decide não dividir, o porquê fica registrado no plano, não neste relatório. Encerra sem aprovar — quem aprova é o humano.
7. **Fecho do huddle** — `python3 "${CLAUDE_SKILL_DIR}/dc.py" huddle-fecho` imprime os gatilhos e o momento da norma (*Huddle*). O que ficou aberto entra por `python3 "${CLAUDE_SKILL_DIR}/dc.py" huddle-abrir <tipo> --autor Claude`, com o texto no stdin, uma chamada por entrada. Antes de enviar, a mensagem final passa por `python3 "${CLAUDE_SKILL_DIR}/dc.py" huddle-lint-relatorio`, no stdin, e termina com `entradas novas no huddle: N (H-XX, …)` — `0`, sem parênteses, quando não houve nada.

Composição via `dc.py` — ponto de entrada único, o que o `allowed-tools` libera; rode-o do diretório do projeto. **Rode o comando exatamente como está escrito** — sem variável de shell, sem tirar as aspas e sem trocar o caminho —, porque a liberação de permissão casa o texto do comando. Subcomandos: `validar-nome`, `concorrencia`, `lint-plano`, `huddle-fecho`, `huddle-abrir` e `huddle-lint-relatorio`.

## Referências

- Norma: `<plan_root>/system/modelo-dev-units.md` — `plan_root` é o do `config.json`, e
  `docs/plan` é só o default. Vive no projeto que usa a skill, e é lá que a skill a lê.
