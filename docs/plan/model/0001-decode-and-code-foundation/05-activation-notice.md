---
# about
name: activation-notice
type: unit
project: DecodeAndCode
description: Ativação de norma deixa de ser silenciosa — hook InstructionsLoaded anuncia qual arquivo entrou em contexto, quando e por quê, e em PostCompact nomeia as rules com paths: que estavam ativas e não voltaram
tags: [decode-and-code, hooks, instructions-loaded, observabilidade, fase-2]

# alvo
core: model
module: decode-and-code
block: ""
owner: model
unit_id: 0001-05
unit_type: dev

# verificação
state: verified
test: .claude/skills/decode-and-code/scripts/tests/test_activation_notice.py
verified_at: 2026-08-24

# history
author: Bortoli
created: 2026-08-24
status: draft
version: 1.0.0
updated: ""

# system
scope: project
auto_load: false
dependencies: []
---

# 0001-05 — activation-notice

**Responsabilidade:** remover o silêncio da ativação de norma. Não corrige a perda — anuncia-a, que é
o que separa *carregou e foi ignorada* de *nunca carregou*, hoje indistinguíveis.

## Contrato

| Campo | Detalhe |
|---|---|
| **Entrada** | Payload JSON em stdin dos eventos `InstructionsLoaded`, `SubagentStart` e `PostCompact` |
| **Saída** | `systemMessage` nomeando o arquivo e o `load_reason`. Payload que não casa nada produz **silêncio**, não mensagem vazia |
| **Auth** | — |
| **Efeito** | Nenhum sobre o carregamento. `InstructionsLoaded` é monitoramento puro — *"cannot block instruction loading"* |
| **Erro** | **Falha aberta e silenciosa.** Qualquer exceção interna encerra sem mensagem; o anúncio nunca vira obstáculo |

> **Anunciar não é carregar, e a distinção é categórica.** Este hook nomeia o arquivo, nunca copia o
> texto — não duplica conteúdo, e por isso não é drift. É o que o mantém distinto da `04`, que impõe.

## Sequência

1. **Spike, e ele vem primeiro por decisão do plano.** A página de hooks se contradiz: a tabela-resumo marca `InstructionsLoaded` como `N/A (ignored)`, e a seção detalhada afirma que `systemMessage` funciona. Rodar um hook mínimo e observar se a mensagem chega ao usuário. **Se não chegar, o canal muda antes do resto da unidade** — e a troca é registrada como decisão, não descoberta em execução.
2. Escrever `activation_notice.py`: recebe o payload, resolve o evento, e monta a linha de anúncio — arquivo, `load_reason` e momento. Um evento por função, sem ramificação aninhada.
3. `InstructionsLoaded`: anunciar nomeando o arquivo e o `load_reason` bruto do payload — `session_start`, `path_glob_match`, `compact`, `nested_traversal`, `include`. **Não traduzir nem agrupar:** o valor cru é o que serve para depurar rule com `paths:`.
4. `PostCompact`: comparar as rules com `paths:` que estavam ativas antes da compactação com as que voltaram, e **nomear as que não voltaram**. A perda continua — o que sai é o silêncio (`L-09`).
5. `SubagentStart` e a expansão de skill: anunciar pelo canal que cada um aceita — stderr no primeiro, `systemMessage` na segunda. Entram por requisito declarado, não por lacuna medida, e o custo é marginal.
6. Registrar os eventos em `.claude/settings.json`, ao lado do `PreToolUse` que a `04` declarou.
7. Escrever `tests/test_activation_notice.py` cobrindo o critério de aceite, com payload sintético por evento — nenhum teste depende de sessão real. **Artefato de teste que já tenha construtor em `tests/fixtures.py` vem de lá; o que faltar entra lá, nunca inline** (`L-21`).
8. Rodar o gate e relatar, incluindo **o que o spike do passo 1 mediu**.

## Arquivos

| Caminho | O que muda |
|---|---|
| `.claude/skills/decode-and-code/scripts/activation_notice.py` | **novo** — o mecanismo de anúncio |
| `.claude/hooks/instructions_loaded.py` | **novo** — ponto de entrada de `InstructionsLoaded` |
| `.claude/hooks/post_compact.py` | **novo** — ponto de entrada de `PostCompact` |
| `.claude/hooks/subagent_start.py` | **novo** — ponto de entrada de `SubagentStart` |
| `.claude/settings.json` | acrescenta os três eventos ao bloco `hooks` |
| `.claude/skills/decode-and-code/scripts/tests/test_activation_notice.py` | **novo** — o teste declarado |

## Dependências

A unidade `0001-04`, que cria o bloco `hooks` em `.claude/settings.json` e o diretório
`.claude/hooks/`. Sem ela, esta unidade cria os dois — mas as duas editando o mesmo bloco em paralelo
é colisão evitável.

## Normas aplicáveis

| Norma | Onde |
|---|---|
| Ativação silenciosa é o modo de falha da própria camada | [`0001-decode-and-code-foundation.md`](0001-decode-and-code-foundation.md), seção de mesmo nome |
| `L-09` — a perda continua; o que sai é o silêncio | [`0001-decode-and-code-foundation.md`](0001-decode-and-code-foundation.md), seção *Lacunas* |
| `L-05` — duas rules ativas casando o mesmo path é o detector natural, e este hook o vê | [`0001-decode-and-code-foundation.md`](0001-decode-and-code-foundation.md), seção *Lacunas* |
| `InstructionsLoaded` é monitoramento puro; o canal é `systemMessage` | [`0001-decode-and-code-foundation.md`](0001-decode-and-code-foundation.md), seção *Restrições conhecidas* |
| Simplicidade primeiro | `.claude/CLAUDE.md` — anúncio, nunca cópia de conteúdo |

## Critério de aceite

Payload de rule que casa o glob produz anúncio **nomeando o arquivo e o `load_reason`**; payload fora
do escopo produz **silêncio**, não mensagem vazia. Payload de `PostCompact` nomeia as rules que
estavam ativas e não voltaram, e produz silêncio quando todas voltaram.

O anúncio **não contém uma linha do conteúdo** do arquivo anunciado — só o caminho, o motivo e o
momento. Se contiver, virou cópia, e cópia é o drift que o plano persegue.

Payload malformado e evento desconhecido encerram **em silêncio, sem exceção e sem bloquear**.

**A suíte inteira continua verde**, e nenhum teste existente é alterado.

## Verificação

```
./scripts/test-python.sh .claude/skills/decode-and-code/scripts/tests/test_activation_notice.py
```

Último resultado: não executado.

## Fonte

- [`0001-decode-and-code-foundation.md`](0001-decode-and-code-foundation.md), *Escopo* → Fase 2, e as seções *Ativação silenciosa* e *Restrições conhecidas*
- Medições de 2026-08-22 sobre a doc do Claude Code: catálogo de eventos de hook, canais de saída, `load_reason`, gatilho por leitura de rule com `paths:`, e comportamento após compactação
- A contradição da doc sobre `systemMessage` em `InstructionsLoaded` foi lida em documentação, **não em execução** — é o que o spike do passo 1 mede
