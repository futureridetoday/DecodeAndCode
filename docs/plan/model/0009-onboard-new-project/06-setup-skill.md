---
# about
name: setup-skill
type: unit
project: DecodeAndCode
description: A skill setup conduz o primeiro uso do método no projeto — pré-condições, perfil, guidelines, guardrails, huddle e o princípio Decode → Code — na conversa principal, uma sugestão por vez, compondo os comandos das unidades 01 a 04 e dos planos 0007 e 0008
tags: [decode-and-code, setup, skill, onboarding]

# alvo
core: model
module: onboard-new-project
block: ""
owner: model
unit_id: 0009-06
unit_type: dev

# verificação
state: verified
test: .claude/skills/decode-and-code/scripts/tests/test_skill_base.py
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

# 0009-06 — setup-skill

**Responsabilidade:** levar quem instala o método do zero à norma do próprio projeto — guidelines e
guardrails aprovados um a um, huddle pronto e o método explicado —, com toda escrita passando pela
aprovação na conversa.

## Contrato

| Campo | Detalhe |
|---|---|
| **Entrada** | `/decode-and-code:setup`, sem argumento; ou o modelo propõe depois do aviso da `0009-05` |
| **Saída** | A conversa das etapas 0 a 6 e um relatório final com a linha de fecho do huddle |
| **Auth** | — |
| **Efeito** | Só pelos comandos do `dc.py`, e só depois do sim: `bootstrap`, `setup-*`, `setup-escopo --aplicar`, `criar-guideline`, `adicionar-guardrail`, `huddle-iniciar`, `huddle-migrar`, `huddle-abrir`. Nunca escreve no `CLAUDE.md` nem no `AGENTS.md` (`D-05`) |
| **Erro** | Comando que sai `1` volta para a pessoa com o motivo; o fluxo continua da sugestão em que parou |

**Linha da `TOPOLOGIA`** (`tests/test_skill_base.py`): `modo: setup`, `model: opus`,
`disable-model-invocation: "false"` — o modelo pode propor e iniciar depois do aviso, e o primeiro
passo é a confirmação —, sem `context` (a ferramenta de perguntas não existe em fork), `allowed-tools`
igual a `ALLOWED_TOOLS`. `"setup"` entra em `lib.SKILLS` e na tupla de
`test_so_as_skills_em_fork_declaram_agent`. Atalho `skills/setup/dc.py` copiado byte a byte dos
outros.

**O corpo conduz as etapas 0 a 6 de *O fluxo* do plano**, sem repeti-las além do necessário para
executar. O que o corpo precisa dizer, porque o plano não é lido em sessão:

- **0** — confirmar que o setup é desejado agora; sem `.claude/` e `docs/`, propor
  `dc.py bootstrap`; depois `dc.py setup-escopo` e, com o sim, `--aplicar`, explicando que cada colega
  instala uma vez por clone.
- **1** — `dc.py setup-iniciar`, `dc.py descobrir`; confirmar objetivo, escopo e stack uma pergunta
  por vez, com sugestões tiradas do inventário e o texto livre; gravar com `dc.py setup-perfil`.
- **2 e 3** — `dc.py setup-decididas` primeiro; o que está em `existentes` do `descobrir` é registrado
  como `existente` e não volta a ser sugerido. Todas as guidelines antes dos guardrails, uma por vez,
  com **Aprovar** / **Editar** / **Rejeitar**; **Editar** abre **Edição livre** ou **Edição guiada**
  (*O fluxo*, etapas 2 e 3). Guideline nasce da stack e do objetivo; guardrail, de decisão explícita
  do time que desvia do padrão da stack (`D-03`); caminho que ainda não existe vai com
  `aguardando: true`. Cada resultado vai para `dc.py setup-registrar`, e o corpo dá o vocabulário que
  o `setup.py` da `0009-01` aceita, porque valor fora dele sai `1`: `tipo` ∈ {`guideline`,
  `guardrail`, `princípio`}; `origem` ∈ {`stack`, `decisão do time`, `existente`, `arquivo
  <caminho>`}; `resultado` ∈ {`aceita`, `rejeitada`, `existente`}. Sugestão editada e depois aprovada
  é `aceita` — não há `editada`. Achado com cara de princípio vira `observação` no huddle (`D-04`) e
  é registrado com `tipo: princípio`, `resultado: rejeitada` e o id `H-XX` no detalhe; se o projeto
  ainda tem o arquivo único antigo, o `huddle-abrir` recusa, e a skill propõe o `huddle-migrar` da
  etapa 4 antes de registrar.

> **Refeita em 2026-11-16** (`L-14`). A primeira execução listou `editada` entre os resultados, valor
> que o `setup-registrar` recusa. Só o corpo do `SKILL.md` muda.
- **4** — com o arquivo único antigo, propor `dc.py huddle-migrar`; senão `dc.py huddle-iniciar`, ou
  só explicar se o arquivo da pessoa já existe.
- **5** — `dc.py explicar` e explicar Decode e Code a partir do que ele imprime (`D-06`).
- **6** — `dc.py setup-concluir`, e o gate de fecho do huddle como nas outras skills: `huddle-fecho`,
  `huddle-abrir`, `huddle-lint-relatorio`.

Idioma: o do usuário, na conversa e nas rules geradas (`D-07`).

## Sequência

1. Acrescentar a linha `setup` à `TOPOLOGIA` e a tupla de `agent`, e ver o teste declarado falhar.
2. `"setup"` em `lib.SKILLS`, com o comentário de `lib.py:55-58` contando seis skills.
3. Copiar o atalho `dc.py` de `skills/huddle/`.
4. Escrever `skills/setup/SKILL.md` no formato das outras, com o corpo acima e o parágrafo *Composição via `dc.py`* listando os subcomandos usados.
5. Rodar o teste declarado, `test_dc.py` (o drift entre o que a skill cita e o que o `dc.py` aceita) e `test_empacotamento.py`.
6. Construir o pacote e conferir que `skills/setup/SKILL.md` está nele; rodar `claude plugin validate --strict` se o comando existir na máquina, e relatar a saída.
7. Rodar a suíte inteira.

## Arquivos

| Caminho | O que muda |
|---|---|
| `.claude/skills/setup/SKILL.md` | **novo** |
| `.claude/skills/setup/dc.py` | **novo** — cópia de `.claude/skills/huddle/dc.py` |
| `.claude/skills/decode-and-code/scripts/lib.py:55-58` | `SKILLS` e o comentário |
| `.claude/skills/decode-and-code/scripts/tests/test_skill_base.py:55-110` | `TOPOLOGIA` e a tupla de `agent` |
| `.claude/skills/huddle/SKILL.md` | modelo de formato e de *Composição via `dc.py`* |

## Dependências

`0009-01` a `0009-05`: os subcomandos que o corpo cita precisam existir, ou o drift de `test_dc.py`
reprova.

## Normas aplicáveis

| Norma | Onde |
|---|---|
| As etapas que a skill conduz | [`0009-onboard-new-project.md`](0009-onboard-new-project.md), seção *O fluxo* |
| Onde o setup escreve, o critério de sugestão, princípio e idioma | [`0009-onboard-new-project.md`](0009-onboard-new-project.md), seção *Decisões* |
| Por que a skill roda na conversa principal | [`0009-onboard-new-project.md`](0009-onboard-new-project.md), seção *Restrições da plataforma* |
| Como gravar guideline e guardrail | [`modelo-dev-units.md`](../../system/modelo-dev-units.md), seção *Camada normativa* |
| O gate de fecho do huddle | [`modelo-dev-units.md`](../../system/modelo-dev-units.md), seção *Huddle* |

## Critério de aceite

`test_skill_base.py` aprova a linha `setup` da `TOPOLOGIA` e o atalho; `lint_skill` aprova o
`SKILL.md` com o modo `setup`; `test_dc.py` confirma que todo subcomando citado existe; e o pacote
construído traz `skills/setup/SKILL.md`. **A suíte inteira continua verde.** A conversa em si não tem
oráculo automático: é medida na *Validação ponta a ponta* do plano.

## Verificação

```
./scripts/test-python.sh .claude/skills/decode-and-code/scripts/tests/test_skill_base.py
```

## Fonte

- [`0009-onboard-new-project.md`](0009-onboard-new-project.md), *Escopo* → *Fase 2*, unidade 06
