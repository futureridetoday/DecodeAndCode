---
# about
name: fix-review-plan-claims
type: plan
project: DecodeAndCode
description: A norma e a skill review-plan prometem script onde não há (fontes citadas, grafo de cores, guardrails do CLAUDE.md), contam cinco checks onde há seis, e a skill não roda o lint-plano a que delega o formato — o texto passa a dizer o que existe, a revisão ganha o lint-plano que já existe, e a seção de bootstrap duplicada sai
tags: [decode-and-code, norma, review-plan, lint-plano, guardrail]

# alvo
plan_id: "0014"
plan_size: pequeno
plan_type: norma
core: model
module: fix-review-plan-claims
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

# A revisão para de prometer script que não existe

## Objetivo

**Clarificar.** A norma e a skill `review-plan` descrevem como determinístico o que hoje é feito à
mão, e quem segue o texto espera um oráculo que não roda. Métrica: **zero** afirmações, na norma e
na skill, de verificação por script sem subcomando correspondente no `dc.py` (hoje: três), e
**zero** contagens divergentes dos checks (hoje: uma). Beneficiário: o modelo que executa a
revisão e o humano que aprova confiando no relatório dela.

| # | Onde | O texto diz | O que existe |
|---|---|---|---|
| 1 | Norma, *Modo `review`*, linha "documentação oficial"; skill, passo 1 | "Script confere se as fontes citadas existem", no bloco determinístico | Nenhum subcomando; o modelo confere à mão |
| 2 | Norma, *Modo `review`*, linha "arquitetura"; *Guardrail fundador*, o blockquote final | Misto quando há grafo; "o mecanismo — declarar o grafo e verificá-lo por contagem — viaja" | Nem código nem campo no `config.json` para declarar grafo |
| 3 | Skill, passo 2 | "A presença por porte é do `lint-plano`" | A skill nunca roda `lint-plano`; só o `intake` roda. Plano escrito à mão chega ao `aprovar`, que confere só `plan_size`/`plan_type`, sem lint de formato |
| 4 | Norma, *Fluxo completo*, etapa 2 | "Cinco checks" | *Modo `review`* lista seis |
| 5 | Norma, *Modo `review`*, linha "padrões" | "Guardrails do `CLAUDE.md` são verificáveis" | Guardrails moram em `.claude/guardrails.json` e são regras do hook `PreToolUse` (ferramenta + regex sobre a chamada): barram em execução, não leem plano. `lint-guardrails` valida o arquivo de regras, não o plano |
| 6 | Skill, seção *Começando um projeto do zero* | Tabela do que o `bootstrap` cria | Duplica *Bootstrap → O que cria* da norma; nenhuma outra skill tem a seção, e ela só documenta — não manda rodar |

**Evitar.**

| Alternativa | Por que não basta |
|---|---|
| Subcomando de links no `dc.py`, reaproveitando `lint_skill._checar_links` dentro do `lint_plano` | Reprovado no gate A: varredura de `docs/plan/**` em 2026-11-19 achou **zero** links quebrados em arquivo de plano; os quebrados estão numa unidade (`0001/19`), no `_backlog.md` e no huddle — nenhum chegou a uma revisão. Fica como desenho adiado, abaixo |
| Grafo de cores declarável (campo + contagem) | Reprovado no gate A: nenhum projeto consumidor declara grafo |
| Fazer a revisão rodar `lint-guardrails` | Não verifica plano nenhum — confere o schema de `guardrails.json`. Rodá-lo na revisão seria oráculo do arquivo errado |
| Deixar como está | A revisão continua relatando como "comando" o que é leitura, e o humano aprova sobre essa origem |

**Reduzir.** Texto da norma em três seções e da skill `review-plan`; uma linha de comando que já
existe (`lint-plano`) entra no passo determinístico. Nenhum código, nenhum teste novo.

## Gates

| Gate | Resposta |
|---|---|
| **A — necessidade real** | **Sim, para o texto:** as seis divergências existem hoje, medidas lendo a norma, a skill e o `dc.py` (subcomandos `_validar_nome` a `_descobrir`, nenhum de links nem de grafo). **Sim, para o `lint-plano` na revisão:** a skill delega o formato a um comando que não roda, e o `aprovar` não o substitui. **Não, para código novo:** zero links quebrados em plano, zero grafo declarado |
| **B — mínimo viável** | Cortado: o checador de links (vira desenho adiado, gatilho abaixo); o mecanismo de grafo (sai a promessa, fica a frase de que é julgamento até existir consumidor); `lint-guardrails` na revisão (oráculo errado); a seção de bootstrap inteira, sem linha substituta — o `bootstrap` é da etapa 0 do `setup`, que o propõe com o sim da pessoa (`L-03`) |

## Solução

**Norma** (`docs/plan/system/modelo-dev-units.md`):

1. *Modo `review` — os seis checks*:
   - "dividido" → nomeia o subcomando: "`concorrencia` checa `_planos.md`".
   - "documentação oficial" → **Julgamento**: o modelo abre cada fonte citada, confere que existe e
     avalia se é a certa.
   - "arquitetura" → **Julgamento**, com uma frase: o check por contagem de *Guardrail fundador* não
     tem mecanismo ainda.
   - "padrões" → **Misto**: `lint-plano` confere formato por porte e `plan_type`; guardrails de
     `.claude/guardrails.json` se impõem em execução pelo hook, e a revisão confere por julgamento
     que o plano não depende de violá-los, nem as guidelines de `.claude/rules/`.
   - "Quatro dos seis têm parte automatizável" → **dois** (divisão e padrões).
2. *Guardrail fundador*, blockquote final: o mecanismo **ainda não existe**; nenhum projeto declara
   grafo (gate A deste plano); até existir, arquitetura é julgamento.
3. *Fluxo completo*, etapa 2: "Cinco checks" → "Seis checks".

**Skill** (`.claude/skills/review-plan/SKILL.md`):

4. Passo 1: sai "Fontes citadas" do bloco determinístico (vai ao passo 4, julgamento); entra
   `lint-plano <plano>`, cujos problemas viram achado `bloqueante`, origem `comando`.
5. Passo 2: a delegação ao `lint-plano` passa a apontar para o passo 1.
6. Sai a seção *Começando um projeto do zero*, inteira; a linha *Subcomandos* passa a listar
   `validar-nome`, `concorrencia`, `lint-plano` e os três `huddle-*`.
7. `description`, exemplo: "(concorrência, fontes citadas)" → "(concorrência, formato do plano)".

## Desenho adiado — checador de links

Para quando o gate A passar (gatilho: o primeiro link relativo quebrado num plano que chegue à
revisão ou à aprovação): `lint_plano.lint` passa a chamar `lint_skill._checar_links` com o próprio
plano como âncora — a função já resolve a partir de `skill.parent`, então serve sem mudança. O
`move-md.py` reescreve os links quando o `aprovar` move o plano um nível abaixo, então o lint no
`_inbox` e depois do movimento continua válido.

## Oráculo

- `grep -n "Cinco checks" docs/plan/system/modelo-dev-units.md`: nenhuma ocorrência.
- `grep -n "CLAUDE.md\` são verificáveis" docs/plan/system/modelo-dev-units.md`: nenhuma ocorrência.
- Na tabela *Modo `review`*, cada linha **Misto** nomeia um subcomando que aparece em
  `python3 dc.py --help`.
- `grep -n "lint-plano" .claude/skills/review-plan/SKILL.md` acha o passo 1;
  `grep -n "Começando um projeto do zero" .claude/skills/review-plan/SKILL.md`: nenhuma ocorrência.
- `lint_skill.lint` sobre `.claude/skills/review-plan/SKILL.md` devolve lista vazia (sem subcomando
  no `dc.py`; roda pelo `test-python.sh`, que já cobre as skills do repositório).

Critério de saída: os itens acima, conferidos pelo humano no diff.

## Lacunas

| # | Lacuna | Detalhe |
|---|---|---|
| L-01 | **Concorrência com o `0013`** | Mesmo core (`model`), em desenvolvimento; o `concorrencia` vai acusar. Os arquivos não se cruzam (o `0013` toca o setup), mas a decisão de esperar ou seguir é do humano. **Decidida pelo humano em 2026-11-19: seguir em paralelo com o `0013`** |
| L-02 | **A correção chega a quem já instalou só no próximo release** | Mesmo caso do `L-01` do `0011`: a norma viaja e o `bootstrap` nunca sobrescreve a cópia do projeto |
| L-03 | **Quem roda o `bootstrap`: a revisão ou o `setup`?** | O item 4 põe o `bootstrap` como primeiro passo da revisão, rodado sem pergunta. Desde o `0009`, a etapa 0 do `setup` o **propõe** com o sim da pessoa (`setup/SKILL.md`, linha 54). A evidência citada (`apply-plugin-review`, linha 299) é anterior ao `setup`. Levantada na revisão de 2026-11-19. **Decidida pelo humano em 2026-11-19: sai da revisão**, sem linha substituta (`remover > reduzir`); o `bootstrap` fica só no `setup` |

## Fonte

- [`modelo-dev-units.md`](../system/modelo-dev-units.md), seções *Modo `review` — os seis checks*,
  *Fluxo completo*, *Tipo de plano*, *Guardrail fundador*, *Bootstrap*
- [`review-plan/SKILL.md`](../../../.claude/skills/review-plan/SKILL.md)
- `dc.py` (lista de subcomandos), `lint_skill._checar_links`, `guardrail.py` (docstring do módulo),
  `scaffold.py` (o `aprovar` não chama `lint_plano`)
- [`apply-plugin-review.md`](../_inbox/apply-plugin-review.md), *Observações*: a revisão não rodou o bootstrap
  num projeto zerado
