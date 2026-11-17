---
# about
name: setup-notice
type: unit
project: DecodeAndCode
description: O hook SessionStart ganha o caso do setup — sem setup.md concluído, propõe o setup à pessoa e ao modelo, e o aviso de huddle espera; nunca escreve
tags: [decode-and-code, setup, hook, sessionstart]

# alvo
core: model
module: onboard-new-project
block: ""
owner: model
unit_id: 0009-05
unit_type: dev

# verificação
state: verified
test: .claude/skills/decode-and-code/scripts/tests/test_session_start.py
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

# 0009-05 — setup-notice

**Responsabilidade:** ser o gatilho do setup — não existe evento de instalação de plugin, e o aviso
na abertura da sessão é o que a plataforma oferece (`D-01`).

## Contrato

| Campo | Detalhe |
|---|---|
| **Entrada** | O payload do `SessionStart` no stdin (ignorado) e `CLAUDE_PROJECT_DIR` |
| **Saída** | Setup pendente: JSON com `systemMessage` para a pessoa e `hookSpecificOutput` (`hookEventName: "SessionStart"`, `additionalContext`) para o modelo, propondo `/decode-and-code:setup`. Setup concluído: o comportamento de hoje, o aviso de huddle ou nada |
| **Auth** | — |
| **Efeito** | Nenhum. O hook nunca escreve |
| **Erro** | Silêncio em qualquer exceção, como hoje (`main` em `.claude/hooks/session_start.py`) |

**Setup pendente** é `setup.caminho(projeto)` ausente, ou presente com `completed_at` vazio
(`setup.py`, da `0009-01`). A checagem vem **antes** de `huddle.usuario`: projeto recém-aberto pode
não ter `docs/`, `.claude/` nem `user.name` configurado, e o setup é justamente o que resolve isso.
Enquanto o setup estiver pendente, o aviso de huddle não aparece — um aviso por vez.

**O aviso aparece também com o plugin só no escopo de usuário** (`D-09`): a etapa 0 da skill é pôr o
plugin no projeto. A consequência — aviso em todo projeto aberto com o plugin habilitado — é a
`L-10` do plano, e não se resolve aqui.

**`additionalContext`** diz ao modelo que o setup deste projeto não foi feito, que a skill é
`/decode-and-code:setup` e que ela começa pela confirmação da pessoa — o modelo propõe, não inicia
sem o sim.

**Este repositório não tem `setup.md`:** depois desta unidade, abrir uma sessão aqui mostra o aviso
de setup no lugar do de huddle até a validação ponta a ponta rodar o setup nele.

## Sequência

1. Em `tests/test_session_start.py`, fazer o `setUp` de `_Projeto` gravar um `setup.md` concluído, para os casos de huddle continuarem valendo.
2. Acrescentar `TestSetup`: sem `setup.md`; com `completed_at` vazio; concluído (sem aviso de setup); setup pendente com huddle atrasado (só o de setup); projeto sem `docs/` nem `.claude/`; sem `user.name` (aviso de setup, não silêncio).
3. Em `.claude/hooks/session_start.py`, importar `setup` e checar o setup antes do huddle, com os textos acima.
4. Atualizar a docstring do hook, que hoje fala só do huddle.
5. Rodar o teste declarado, `test_empacotamento.py` e a suíte inteira.

## Arquivos

| Caminho | O que muda |
|---|---|
| `.claude/hooks/session_start.py:30-79` | `aviso` e `main`: o caso do setup antes do huddle; a docstring |
| `.claude/skills/decode-and-code/scripts/tests/test_session_start.py:30-42` | `setUp` com `setup.md` concluído, e a classe nova |

## Dependências

A `0009-01`: `setup.caminho` e o campo `completed_at`.

## Normas aplicáveis

| Norma | Onde |
|---|---|
| Por que o gatilho é um aviso, e o que ele não pode fazer | [`0009-onboard-new-project.md`](0009-onboard-new-project.md), seção *Restrições da plataforma* |
| O aviso com o plugin só no escopo de usuário | [`0009-onboard-new-project.md`](0009-onboard-new-project.md), seção *Decisões* |
| O hook do huddle que esta unidade estende | [`modelo-dev-units.md`](../../system/modelo-dev-units.md), seção *Huddle* |

## Critério de aceite

Por subprocesso, com `CLAUDE_PROJECT_DIR` num `tempfile`: sem `setup.md`, o hook devolve JSON com a
proposta de `/decode-and-code:setup` em `systemMessage` e em `additionalContext`; com `completed_at`
preenchido, não há aviso de setup e os casos de huddle de hoje continuam passando; com setup pendente
e huddle atrasado, só o aviso de setup aparece; num projeto sem `docs/`, sem `.claude/` e sem
`user.name`, o aviso de setup aparece e o hook sai `0`. **A suíte inteira continua verde.**

## Verificação

```
./scripts/test-python.sh .claude/skills/decode-and-code/scripts/tests/test_session_start.py
```

## Fonte

- [`0009-onboard-new-project.md`](0009-onboard-new-project.md), *Escopo* → *Fase 2*, unidade 05
