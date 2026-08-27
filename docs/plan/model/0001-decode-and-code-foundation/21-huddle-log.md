---
# about
name: huddle-log
type: unit
project: DecodeAndCode
description: A fila do que ainda não foi decidido ganha invariante verificável — despejo, vocabulário fechado e a linha de fecho que separa conferi e não havia de nunca conferi — e o pacote passa a levar os operadores
tags: [decode-and-code, huddle, pre-norma, despejo, empacotamento]

# alvo
core: model
module: decode-and-code
block: ""
owner: model
unit_id: 0001-21
unit_type: dev

# verificação
state: verified
test: .claude/skills/decode-and-code/scripts/tests/test_huddle.py
verified_at: 2026-08-27

# history
author: Bortoli
created: 2026-08-26
status: draft
version: 1.0.0
updated: ""

# system
scope: project
auto_load: false
dependencies: []
---

# 0001-21 — huddle-log

**Responsabilidade:** dar oráculo ao que o huddle promete — entrada resolvida **sai** do arquivo, o
tipo vem de vocabulário fechado, e o relatório declara quantas entradas novas houve mesmo quando
foram zero — e fechar o pacote reexecutando o empacotamento com os agentes dentro.

## Contrato

| Campo | Detalhe |
|---|---|
| **Entrada** | `huddle.lint_arquivo(caminho)`, `huddle.lint_relatorio(texto)` e `huddle.iniciar(destino)` |
| **Saída** | Os dois `lint_*` devolvem lista de problemas, vazia quando sã — padrão de todo lint daqui. `iniciar` devolve o caminho escrito, ou `None` quando o arquivo já existe |
| **Auth** | — |
| **Efeito** | Os `lint_*` só leem. `iniciar` escreve **um** arquivo, e nunca sobre um existente |
| **Erro** | Arquivo inexistente levanta `FileNotFoundError`; estrutura quebrada entra como problema, nunca como exceção |

**Os três invariantes, e por que são mecânicos:**

| Invariante | O que recusa |
|---|---|
| **Despejo** | O mesmo `H-XX` aparecendo em `## Abertas` e na tabela de `## Fechadas`. É a promessa central do arquivo — *entrada resolvida sai daqui* —, e sem verificação um huddle onde nada fecha só cresce |
| **Vocabulário fechado** | Tipo fora de `pergunta`, `divergência`, `padrão`, `revisitar`, `observação` no cabeçalho da entrada. Mesmo padrão de `unit_type` e `plan_size`: recusa-se o valor que não é escolha nenhuma, nunca a escolha |
| **Linha de fecho** | Relatório sem `entradas novas no huddle: N`. **Inclusive com N igual a zero** — é isso que separa *conferi e não havia* de *nunca conferi*, hoje indistinguíveis (`L-08`) |

> **A mitigação da linha de fecho é fraca, e a `L-08` já diz o quanto.** Um relatório honesto com
> zero e um desatento com zero continuam idênticos: o que o lint alcança é a **ausência da
> declaração**, nunca a atenção de quem a escreveu. Os cinco gatilhos de escrita seguem sem oráculo,
> e nenhum campo os transforma num.

**Não há arquivo de template, e é a `D-20` aplicada.** O esqueleto do huddle vive em `iniciar`,
como `porte._CONTEUDO_INICIAL` já faz para a tabela de porte — formato com uma fonte só, que é o
script, com a norma descrevendo-o em prosa.

**O `huddle.md` deste repositório não viaja; o mecanismo, sim.** As entradas abertas são a conversa
entre o humano e o modelo **deste** projeto — instância pura, pelo invariante 2. Quem instalar
recebe `iniciar`, que cria o seu, vazio.

## Sequência

1. Escrever `huddle.py` com `TIPOS` — os cinco, vocabulário fechado — e `lint_arquivo(caminho)`, verificando cabeçalho de entrada, unicidade de `H-XX` e a regra de despejo entre `## Abertas` e `## Fechadas`.
2. Escrever `lint_relatorio(texto)`, que recusa a ausência da linha de fecho e aceita `0` como valor legítimo.
3. Escrever `iniciar(destino)`, que cria o esqueleto vazio — seções `## Abertas` e `## Fechadas` e o frontmatter — e devolve `None` sem escrever se o arquivo já existir.
4. Fazer `empacotar.construir` copiar `.claude/agents/` para `agents/` do pacote, no mesmo formato de `_copiar_hooks` (`D-27`).
5. Trocar, em `.claude/agents/planner.md`, a frase de escopo de escrita por uma relativa ao `plan_root`, como o `SKILL.md` já faz.
6. Escrever a seção do huddle na norma — formato, despejo, vocabulário, momento — e atualizar, na seção de empacotamento, o que o pacote passa a levar.
7. Escrever `tests/test_huddle.py` e acrescentar a `test_empacotamento.py` os casos de `agents/`.
8. Rodar o gate e relatar.

## Arquivos

| Caminho | O que muda |
|---|---|
| `.claude/skills/decode-and-code/scripts/huddle.py` | **novo** — `lint_arquivo`, `lint_relatorio` e `iniciar` |
| `.claude/skills/decode-and-code/scripts/empacotar.py` | `construir` passa a copiar `agents/` |
| `.claude/agents/planner.md` | o escopo de escrita passa a ser relativo ao `plan_root` |
| `.claude/skills/decode-and-code/scripts/tests/test_huddle.py` | **novo** — o teste declarado |
| `.claude/skills/decode-and-code/scripts/tests/test_empacotamento.py` | casos de `agents/` no pacote |
| `docs/plan/system/modelo-dev-units.md` | seção do huddle, e o que o pacote leva |

## Dependências

A `0001-16`, pelo `empacotar` que esta unidade estende. A `0001-19` e a `0001-20`, pelos agentes que
passam a viajar — sem eles não há o que copiar.

## Normas aplicáveis

| Norma | Onde |
|---|---|
| O huddle é fila, não fonte — formato, tipos, gatilhos e a regra de momento | [`0001-decode-and-code-foundation.md`](0001-decode-and-code-foundation.md), *O `huddle` é fila, não fonte* |
| Os cinco gatilhos não são verificáveis por script; a regra de despejo é | [`0001-decode-and-code-foundation.md`](0001-decode-and-code-foundation.md), `L-08` |
| Os dois agentes viajam, e a frase de escopo do `planner` vira relativa | [`0001-decode-and-code-foundation.md`](0001-decode-and-code-foundation.md), `D-27` |
| Não há arquivo de template: o formato vive no script e na norma | [`0001-decode-and-code-foundation.md`](0001-decode-and-code-foundation.md), `D-20` |
| O huddle não é carregado automaticamente — nem rule, nem `skills:`, nem import | [`0001-decode-and-code-foundation.md`](0001-decode-and-code-foundation.md), `D-08` |

## Critério de aceite

`huddle.lint_arquivo` devolve `[]` sobre o `docs/plan/system/huddle.md` **real** — o caso contra a
instância, não só contra fixture (`L-31`) — e um problema por invariante violado, cada um num caso
próprio: `H-XX` presente nas duas seções, tipo fora dos cinco, e `H-XX` repetido em `## Abertas`.

`huddle.lint_relatorio` aceita um relatório que declara `entradas novas no huddle: 0` e **recusa** o
mesmo relatório sem a linha. Os dois casos andam juntos: sem o segundo, o lint poderia aceitar
qualquer texto.

`huddle.iniciar` cria o esqueleto num diretório vazio, e a árvore resultante passa em
`lint_arquivo` — o formato que o script escreve é o formato que o script aprova. Chamado de novo,
devolve `None` **sem tocar** no arquivo: o teste confere o conteúdo idêntico depois da segunda
chamada.

`empacotar.construir` produz `agents/planner.md` e `agents/developer.md` no pacote, e
`empacotar.verificar` continua devolvendo `[]` sobre a árvore construída **do repositório real** —
é ele que prova que a frase do `planner` deixou de citar caminho deste projeto. Os casos de
empacotamento ficam em `test_empacotamento.py`, com o tema; o gate desta unidade roda
`test_huddle.py`, e é a `L-11` outra vez: o gate prova menos do que a unidade entrega, e a suíte
inteira verde é a condição que fecha o resto.

**A suíte inteira continua verde.**

## Verificação

```
./scripts/test-python.sh .claude/skills/decode-and-code/scripts/tests/test_huddle.py
```

## Fonte

- [`0001-decode-and-code-foundation.md`](0001-decode-and-code-foundation.md), *Escopo* → *Fase 7*
- `D-27` — os agentes viajam, absorvido por esta unidade
- `D-28` — por que o `huddle.md` deste repositório não viaja, e o mecanismo sim
