---
# about
name: ddl-guardrail-hook
type: unit
project: DecodeAndCode
description: O mecanismo de guardrail passa a existir — hook PreToolUse que casa a ferramenta por regex e inspeciona o conteúdo do comando, recusando DDL em ambiente remoto e deixando passar SELECT diagnóstico
tags: [decode-and-code, guardrail, hook, pre-tool-use, fase-2]

# alvo
core: model
module: decode-and-code
block: ""
owner: model
unit_id: 0001-04
unit_type: dev

# verificação
state: verified
test: .claude/skills/decode-and-code/scripts/tests/test_guardrail.py
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

# 0001-04 — ddl-guardrail-hook

**Responsabilidade:** provar que a camada de guardrail impõe de verdade — um hook que lê o payload
de `PreToolUse`, casa a ferramenta por regex, **inspeciona o conteúdo** do comando e recusa o caso
proibido, deixando passar o diagnóstico.

## Contrato

| Campo | Detalhe |
|---|---|
| **Entrada** | Payload JSON de `PreToolUse` em stdin — `tool_name` e `tool_input`, conforme a referência de hooks |
| **Saída** | JSON em stdout com a decisão. Recusa nomeia **qual regra** recusou e **por quê**; liberação é silenciosa |
| **Auth** | — |
| **Efeito** | Comando que casa a regra não chega a executar |
| **Erro** | **Falha aberta.** Payload ilegível, regra que levanta, ou qualquer exceção interna ⇒ libera e reporta em stderr. Guardrail que trava o trabalho por defeito próprio é o obstáculo que a norma manda evitar |

**A fronteira mecanismo / instância, que é o que decide o desenho:**

| Camada | O que é | Onde vive |
|---|---|---|
| **Mecanismo** | Ler payload, casar ferramenta por regex, aplicar uma lista de regras ao conteúdo, montar a decisão | `guardrail.py` — viaja no plugin |
| **Instância** | *"DDL em ambiente remoto é recusado"*, e o statement que a prova | Arquivo de regras do projeto — **não** viaja (invariante 2) |

**A regra é sobre canal, não sobre SQL — e é isso que ela recusa:**

| Canal | DDL passa? | Por quê |
|---|---|---|
| Ferramenta MCP do Supabase — `execute_sql`, `apply_migration` | **não** | É o ambiente remoto, e é o canal nomeado na regra |
| `psql` por `Bash` contra host remoto | **não** | Mesmo efeito, canal diferente |
| Ferramenta que **escreve arquivo** de migration | **sim** | É o caminho sancionado — recusar aqui inverte a regra |
| Qualquer canal, statement que não é DDL | **sim** | `SELECT` diagnóstico é o uso legítimo do mesmo canal |

> **Recusar DDL em todo lugar é o modo de falha desta unidade**, e passaria num teste que só
> verificasse "DDL é recusado". A regra do campo de prova é literal: *"toda mudança de schema entra
> por migration"* — a migration é onde o DDL **deve** estar.

> **Nenhum projeto que instale o plugin herda uma regra sobre banco de dados.** A Fase 5 empacota o
> mecanismo; esta unidade escreve a instância porque ela é o **campo de prova**, e prova mais que
> qualquer página de norma sobre hooks.

## Sequência

1. Escrever `guardrail.py`: lê o payload de stdin, resolve `tool_name` contra o regex de cada regra declarada e aplica as que casarem ao conteúdo de `tool_input`. Devolve decisão estruturada; **nunca** levanta para fora — exceção interna vira liberação com aviso em stderr.
2. Declarar as regras em arquivo próprio do projeto, carregado por `guardrail.py` — não embutidas no código do mecanismo. Uma regra é: regex de ferramenta, detector de conteúdo, e a mensagem de recusa.
3. Escrever o detector de DDL **ancorado no statement**, nunca em substring: casa o verbo no início de statement (após `;` ou início do texto, ignorando espaço e comentário), nunca a palavra solta no meio de uma string ou de um `SELECT`.
4. Escrever `.claude/hooks/pre_tool_use.py` como o ponto de entrada que o `settings.json` invoca, delegando a `guardrail.py`. O ponto de entrada não decide nada — só liga stdin e stdout ao mecanismo.
5. Registrar o hook em `.claude/settings.json`, no evento `PreToolUse`. **Barato por construção:** ele roda em toda chamada de ferramenta, então nada de I/O além da leitura do arquivo de regras, e nada de import pesado.
6. Escrever `tests/test_guardrail.py` cobrindo o critério de aceite, com os quatro casos que separam mecanismo de acidente — os fixtures estão em *Fixtures* abaixo, e a procedência de cada um está dita ali. **Artefato de teste que já tenha construtor em `tests/fixtures.py` vem de lá; o que faltar entra lá, nunca inline** (`L-21`).
7. Rodar o gate e relatar. **Não instalar no AmFlow** — instalar lá é consequência reportada, item do backlog daquele repositório, nunca gate desta unidade.

## Fixtures

Os quatro casos do teste, com a procedência de cada um — **ler a procedência importa tanto quanto o
texto** (`L-20`).

**1 · Recusado — transcrito verbatim** de `AmFlow:docs/plan/_inbox/notification-fk.md:80-86`, via
`execute_sql`:

```sql
alter table public.notifications
  drop constraint if exists notifications_hub_id_fkey;

alter table public.notifications
  add constraint notifications_hub_id_fkey
  foreign key (hub_id) references public.resources (hub_id);
```

**2 · Liberado — autoral, escrito nesta derivação.** O acervo do AmFlow registra dumps, fingerprints
e hashes, **nenhum `SELECT` de diagnóstico**; procurado em 2026-08-24 nas duas fontes. Este é o
diagnóstico natural da mesma constraint, e vai como fixture assumidamente autoral:

```sql
select conname, pg_get_constraintdef(oid)
from pg_constraint
where conrelid = 'public.notifications'::regclass;
```

**3 · Liberado — o caso anti-substring**, também autoral: um `SELECT` cujo texto **contém** o verbo
do DDL sem ser DDL, por exemplo filtrando por um valor literal `'alter'` ou lendo uma coluna chamada
`created_at`. Casar substring reprovaria este, e passaria por guardrail funcionando.

**4 · Liberado — o mesmo DDL do caso 1, escrito num arquivo de migration.** É o caso que prova que a
regra é sobre canal. Sem ele, um hook que recusa DDL em qualquer lugar passa nos três primeiros e
quebra o fluxo correto.

## Arquivos

| Caminho | O que muda |
|---|---|
| `.claude/skills/decode-and-code/scripts/guardrail.py` | **novo** — o mecanismo |
| `.claude/hooks/pre_tool_use.py` | **novo** — ponto de entrada, sem lógica de decisão |
| `.claude/guardrails.json` | **novo** — as regras deste projeto; é instância, não viaja no plugin |
| `.claude/settings.json` | acrescenta o bloco `hooks` com `PreToolUse` |
| `.claude/skills/decode-and-code/scripts/tests/test_guardrail.py` | **novo** — o teste declarado |

## Dependências

Nenhuma unidade. Depende de `.claude/settings.json`, que já existe e hoje só declara `permissions`.

## Normas aplicáveis

| Norma | Onde |
|---|---|
| O pipeline princípio → guideline → guardrail | [`0001-decode-and-code-foundation.md`](0001-decode-and-code-foundation.md), seção *O pipeline completo, na instância que tem incidente registrado* |
| Ancorar no statement, nunca em substring | mesma seção — e a `L-02` do `AmFlow:0006`, que registra o defeito da mesma classe |
| `PreToolUse` roda em toda chamada: barato, e falha fechada trava o trabalho | [`0001-decode-and-code-foundation.md`](0001-decode-and-code-foundation.md), seção *Restrições conhecidas* |
| `D-07` — guardrail fica no projeto, não no frontmatter do agente | [`0001-decode-and-code-foundation.md`](0001-decode-and-code-foundation.md), seção *Decisões* |
| Nada específico de projeto viaja no plugin | `.claude/CLAUDE.md`, invariante 2 |
| Guardrail fundador — o que é guardrail, e por que é verificável | [`modelo-dev-units.md`](../../system/modelo-dev-units.md), seção *Guardrail fundador* |

## Critério de aceite

Os quatro casos de *Fixtures* decidem como declarado: o DDL do incidente por `execute_sql` é
**recusado**; o `SELECT` diagnóstico é **liberado**; o `SELECT` que contém o verbo do DDL em literal,
nome de coluna ou comentário é **liberado**; e o mesmo DDL do caso 1, escrito num arquivo de
migration, é **liberado**.

**Os casos 3 e 4 são os que provam o mecanismo, e nenhum pode faltar.** Sem o 3, casar substring
passa por guardrail funcionando. Sem o 4, recusar DDL em todo canal passa — e inverte a regra que a
unidade existe para impor.

Payload malformado, arquivo de regras ausente e regra que levanta exceção **liberam**, cada um com
aviso em stderr. Nenhum desses casos bloqueia, e nenhum levanta para fora do hook.

`guardrail.py` não contém o nome de nenhum serviço, tabela ou projeto: o que ele conhece é a forma de
uma regra. Toda instância está em `.claude/guardrails.json`.

**A suíte inteira continua verde**, e nenhum teste existente é alterado.

## Verificação

```
./scripts/test-python.sh .claude/skills/decode-and-code/scripts/tests/test_guardrail.py
```

## Fonte

- [`0001-decode-and-code-foundation.md`](0001-decode-and-code-foundation.md), *Escopo* → Fase 2, e `D-02`
- **A regra vem de `AmFlow:.claude/CLAUDE.md:103`**, lida em 2026-08-24: *"Aplicar DDL direto em
  ambiente remoto — painel do Supabase, SQL Editor ou MCP. Toda mudança de schema entra por
  migration, sem exceção"*. É ela que nomeia os canais, e é por isso que a regra é sobre canal
- **O statement recusado é verbatim** de `AmFlow:docs/plan/_inbox/notification-fk.md:80-86`. O
  contexto do drift está em `AmFlow:docs/plan/hub/0004-close-surface-split/gate-encerramento-2026-08-12.md`.
  Leitura apenas — nenhuma unidade deste plano escreve no AmFlow
- **Os fixtures liberados são autorais**, escritos na derivação de 2026-08-24: o acervo não registra
  nenhum `SELECT` de diagnóstico. Ver `L-20`
- Catálogo de eventos de hook e canais de saída, medido em 2026-08-22 sobre a doc do Claude Code
