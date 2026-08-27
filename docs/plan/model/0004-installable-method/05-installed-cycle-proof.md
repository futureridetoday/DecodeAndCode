---
# about
name: installed-cycle-proof
type: unit
project: DecodeAndCode
description: O teste que roda o ciclo inteiro num projeto zerado a partir do pacote construído — bootstrap, aprovar, gate de entrada, gate de saída e fechamento — transformando o pacote instala em algo que a suíte afirma a cada execução
tags: [decode-and-code, plugin, ciclo, prova, instalacao]

# alvo
core: model
module: installable-method
block: ""
owner: model
unit_id: 0004-05
unit_type: dev

# verificação
state: spec
test: .claude/skills/decode-and-code/scripts/tests/test_ciclo_instalado.py
verified_at: ""

# history
author: Bortoli
created: 2026-08-27
status: draft
version: 1.0.0
updated: ""

# system
scope: project
auto_load: false
dependencies: []
---

# 0004-05 — installed-cycle-proof

**Responsabilidade:** percorrer o ciclo inteiro num projeto zerado, a partir do pacote construído, e
deixar isso rodando na suíte — para que *"o pacote instala"* deixe de depender de alguém lembrar de
testar num diretório vazio.

## Contrato

| Campo | Detalhe |
|---|---|
| **Entrada** | Nenhuma. O teste constrói o pacote e o projeto que usa |
| **Saída** | Verde ou vermelho |
| **Auth** | — |
| **Efeito** | Escreve só dentro de `tempfile` — o pacote e o projeto sintético, os dois descartáveis |
| **Erro** | Qualquer passo do ciclo que levante é falha do teste, não exceção tratada |

**O ciclo, passo a passo, todos a partir dos scripts do pacote:**

| # | Passo | O que prova |
|---|---|---|
| 1 | `empacotar.construir` para fora do repositório | O pacote sai do nada, sem depender de `dist/` versionado |
| 2 | `bootstrap.iniciar` num diretório vazio | A estrutura e a norma chegam ao projeto |
| 3 | Um plano escrito no `_inbox` e `scaffold.aprovar` | Numeração, movimentação e a linha em `_planos.md` |
| 4 | Uma unidade escrita, e `lint_unidade.lint` | O gate de entrada aceita o que o ciclo produziu |
| 5 | `verificacao.verificar` | O gate de saída roda o runner do projeto e projeta `state` |
| 6 | `backlog.projetar` | A situação vira `concluído`, e o plano ganha `status: done` |

**Os scripts vêm do pacote, não deste repositório**, carregados por caminho explícito. É isso que
separa esta unidade de mais um teste de integração: importar do repositório provaria que o código
funciona, nunca que o **pacote** funciona.

**O runner é do projeto, e o fixture escreve o dele.** `runners` mapeia `.py` para
`scripts/test-python.sh` relativo à raiz do projeto (`D-05`), então o fixture põe um stub executável
exatamente ali. Quem instala tem de honrar esse caminho, porque não tem como reconfigurá-lo — é a
`L-04`, e esta unidade a exercita em vez de contorná-la.

**Nenhuma chamada de `git` de verdade.** `move_md.esta_versionado` é mockado, como nos quatro
arquivos que já movem plano — é a lição do `B-04`, remedida com shim de `git` no `PATH`: 16 chamadas
reais viraram 0. `porte._linhas_alteradas` também dispara `subprocess` quando o plano está dentro da
raiz resolvida, e aqui ele estará: o projeto sintético **é** a raiz.

## Sequência

1. Escrever `tests/test_ciclo_instalado.py` com um fixture que constrói o pacote em `tempfile` e cria o projeto zerado ao lado.
2. Carregar os módulos do pacote por caminho explícito, isolados dos que a suíte já importa do repositório.
3. Mockar `esta_versionado` e o cálculo de linhas alteradas, para que nenhum `git` real seja invocado.
4. Escrever o stub de runner em `<projeto>/scripts/test-python.sh` e a unidade sintética que ele aprova.
5. Encadear os seis passos do ciclo num caso só, afirmando o efeito de cada um antes do próximo.
6. Acrescentar o caso negativo: sem o `bootstrap`, o passo 3 falha — é o defeito que abriu este plano, preso num teste.
7. Rodar o gate e a suíte inteira, e relatar.

## Arquivos

| Caminho | O que muda |
|---|---|
| `.claude/skills/decode-and-code/scripts/tests/test_ciclo_instalado.py` | **novo** — o ciclo inteiro, e o caso negativo |
| `docs/plan/system/modelo-dev-units.md` | a seção que registra o que o ciclo instalado prova, e o que fica fora dele |

## Dependências

Todas as quatro. A `0004-01` para que os scripts do pacote achem o projeto; a `0004-02` para o
passo 2; a `0004-03` para que a norma materializada seja o mecanismo; a `0004-04` para que a norma e
o `move-md` estejam dentro do pacote.

## Normas aplicáveis

| Norma | Onde |
|---|---|
| O runner é do projeto, e o bootstrap não o cria | [`0004-installable-method.md`](0004-installable-method.md), `D-05` |
| Quem instala não tem como configurar nada — o padrão é obrigatório | [`0004-installable-method.md`](0004-installable-method.md), `L-04` |
| `claude --plugin-dir` é sessão interativa: a prova final de instalação continua sendo ato humano | [`0004-installable-method.md`](0004-installable-method.md), *Restrições conhecidas* |
| Nenhum teste da suíte invoca `git` de verdade sem querer | [`_backlog.md`](../../_inbox/_backlog.md), `B-04` |
| Gate de entrada e gate de saída — o que cada um decide | [`modelo-dev-units.md`](../../system/modelo-dev-units.md), *Os dois gates* |

## Critério de aceite

Um caso único percorre os seis passos e afirma, ao final: `_planos.md` do projeto sintético mostra o
plano como `concluído`; o arquivo do plano tem `status: done`; a unidade tem `state: verified` com
`verified_at` preenchido; e `porte-medido.md` do projeto ganhou a linha do fechamento. Nada disso é
alcançável hoje — o passo 2 não existe e o passo 3 morre.

Um segundo caso prova o **negativo**: sem o `bootstrap`, `scaffold.aprovar` sobre o mesmo plano
falha. É o defeito que abriu este plano, preso num teste em vez de redescoberto por alguém.

Todos os módulos exercitados vêm da árvore construída por `empacotar.construir`, carregados por
caminho explícito. Um caso confere isso diretamente — o `__file__` do módulo usado está dentro do
pacote, não dentro deste repositório —, porque sem essa checagem um import distraído tornaria o
teste inteiro uma tautologia.

Nenhum `git` real é invocado.

**A suíte inteira continua verde.** E ela fica mais lenta, porque este teste constrói o pacote:
custo aceito, e é o que a `0001-16` já pagou ao verificar contra o pacote real em vez de fixture.

## Verificação

```
./scripts/test-python.sh .claude/skills/decode-and-code/scripts/tests/test_ciclo_instalado.py
```

## Fonte

- [`0004-installable-method.md`](0004-installable-method.md), *Escopo* → *Fase 3*
- *Objetivo* — o ciclo inteiro sem nada deste repositório
