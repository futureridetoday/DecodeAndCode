---
# about
name: package-carries-norm
type: unit
project: DecodeAndCode
description: O pacote passa a levar a norma-mecanismo e o move-md, o bootstrap materializa a norma no projeto que instala, e os dois validadores continuam aprovando
tags: [decode-and-code, plugin, empacotamento, norma, move-md]

# alvo
core: model
module: installable-method
block: ""
owner: model
unit_id: 0004-04
unit_type: dev

# verificação
state: spec
test: .claude/skills/decode-and-code/scripts/tests/test_empacotamento.py
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

# 0004-04 — package-carries-norm

**Responsabilidade:** fazer o pacote levar as duas coisas que faltavam para o método operar fora
daqui — a norma-mecanismo e o `move-md` — e fazer o bootstrap entregar a norma ao projeto que
instala.

## Contrato

| Campo | Detalhe |
|---|---|
| **Entrada** | `empacotar.construir(destino)` e `bootstrap.iniciar(projeto)`, ambos com a assinatura de hoje |
| **Saída** | `construir` devolve os caminhos escritos, agora incluindo a norma e o `move-md`. `iniciar` inclui a norma materializada na lista do que criou |
| **Auth** | — |
| **Efeito** | `construir` reescreve a árvore do pacote; `iniciar` continua sem sobrescrever nada |
| **Erro** | Fonte ausente levanta `FileNotFoundError` nomeando-a, antes de escrever — contrato que `construir` já tem |

### O `move-md` é mecanismo, e hoje não viaja

`config.json` declara `move_script: "scripts/move-md.py"`, resolvido contra a raiz do **projeto**.
Num projeto instalado esse arquivo não existe, e `scaffold` o carrega em **nível de módulo** — é por
isso que ele é o único dos 20 que não importa fora daqui.

**A correção é de quadro de referência, não de caminho.** `move_script` aponta para um arquivo do
**mecanismo**, e mecanismo se resolve contra a raiz da skill — que `handoff.py` já obtém por
`lib._config_path().parent`. Com `move-md.py` morando em `scripts/` da skill, ele viaja de graça
no `_copiar_skill` e a resolução passa a ser uma só, em todo ambiente.

`runners` continua relativo ao **projeto**: `test-python.sh` é instância (`D-05`), e cada projeto
declara o seu. **Os dois campos do `config.json` passam a ter quadros de referência diferentes, e
isso precisa estar escrito lá** — campo cujo quadro de referência é implícito é o defeito que esta
unidade corrige.

### A norma viaja como carga, e o bootstrap a entrega

A skill lê a norma de `<plan_root>/system/modelo-dev-units.md` — no **projeto**, não no plugin. Então
o pacote não pode só carregá-la: precisa entregá-la. `construir` a copia para `reference/` dentro da
skill do pacote, e `bootstrap.iniciar` a materializa em `<plan_root>/system/`, sem sobrescrever.

**O bootstrap procura a norma em dois lugares, e é a dualidade da `0004-01` de novo:** `reference/`
ao lado da skill, quando roda do pacote; `<plan_root>/system/` do próprio repositório, quando roda
de um checkout. Mecanismo e projeto são o mesmo diretório num checkout e diretórios diferentes num
plugin — a mesma razão, a mesma forma.

## Sequência

1. Mover `scripts/move-md.py` e `scripts/tests/test_move_md.py` para dentro de `scripts/` da skill, mantendo o `importlib` que o `scaffold` e o teste já usam.
2. Fazer `move_script` resolver contra a raiz da skill, e escrever no `config.json` o quadro de referência de cada um dos dois campos.
3. Fazer `construir` copiar `docs/plan/system/modelo-dev-units.md` para `reference/` dentro da skill do pacote, com a mesma checagem de fonte ausente das demais.
4. Fazer `bootstrap.iniciar` materializar a norma em `<plan_root>/system/`, procurando primeiro em `reference/` ao lado da skill e depois no `plan_root` do checkout.
5. Documentar em `SKILL.md` como um projeto novo começa — o bootstrap, e o que ele cria.
6. Acrescentar os casos a `test_empacotamento.py` e a `test_bootstrap.py`.
7. Rodar o gate, os dois validadores sobre o pacote real, e a suíte inteira; relatar.

## Arquivos

| Caminho | O que muda |
|---|---|
| `.claude/skills/decode-and-code/scripts/move-md.py` | **movido** de `scripts/move-md.py` |
| `.claude/skills/decode-and-code/scripts/tests/test_move_md.py` | **movido** de `scripts/tests/test_move_md.py` |
| `.claude/skills/decode-and-code/config.json` | `move_script` relativo à skill; o quadro de referência de cada campo |
| `.claude/skills/decode-and-code/scripts/scaffold.py` | resolve o `move-md` pelo novo quadro |
| `.claude/skills/decode-and-code/scripts/empacotar.py` | `construir` leva a norma para `reference/` |
| `.claude/skills/decode-and-code/scripts/bootstrap.py` | `iniciar` materializa a norma |
| `.claude/skills/decode-and-code/SKILL.md` | como um projeto novo começa |
| `.claude/skills/decode-and-code/scripts/tests/test_empacotamento.py` | norma e `move-md` no pacote |
| `.claude/skills/decode-and-code/scripts/tests/test_bootstrap.py` | a norma materializada |

## Dependências

A `0004-02`, pelo `bootstrap` que esta unidade estende. A `0004-03`, pela norma dividida — empacotar
antes de dividir faria o pacote sair sujo uma vez.

## Normas aplicáveis

| Norma | Onde |
|---|---|
| `move-md.py` viaja; `test-python.sh` não | [`0004-installable-method.md`](0004-installable-method.md), `D-06` |
| O bootstrap não cria runner de teste | [`0004-installable-method.md`](0004-installable-method.md), `D-05` |
| O mecanismo mantém o caminho que a skill já cita | [`0004-installable-method.md`](0004-installable-method.md), `D-07` |
| O que o pacote leva, e por que o `verificar` decide por conteúdo | [`0001-decode-and-code-foundation.md`](../0001-decode-and-code-foundation/0001-decode-and-code-foundation.md), `D-21` e `D-22` |
| Marcador de instância é nome de projeto; nome de arquivo que o mecanismo lê não é | [`0001-decode-and-code-foundation.md`](../0001-decode-and-code-foundation/0001-decode-and-code-foundation.md), `L-31` |
| Nada específico de projeto viaja no plugin | `.claude/CLAUDE.md`, *Invariantes não negociáveis*, item 2 |

## Critério de aceite

`empacotar.construir` sobre o **repositório real** produz um pacote que contém a norma-mecanismo e o
`move-md`, e `empacotar.verificar` sobre essa árvore continua devolvendo `[]`. É o caso contra a
instância, não contra fixture — a `L-31` só apareceu porque alguém construiu do repositório de
verdade.

`empacotar.validar` sobre o mesmo pacote continua devolvendo `[]`. Os dois validadores medem coisas
diferentes e os dois precisam passar: `verificar` recusa instância do projeto de origem, `validar` é
a ferramenta oficial conferindo a estrutura.

**`scaffold` importa a partir do pacote**, com os scripts fora de qualquer projeto — hoje é o único
dos 20 módulos que não importa, e o `move-md` ausente é a causa. O caso carrega o módulo do pacote
construído, não do repositório.

`bootstrap.iniciar` num projeto zerado deixa `<plan_root>/system/modelo-dev-units.md` no lugar, com
o conteúdo da norma-mecanismo. Chamado de novo, **não a sobrescreve** — a idempotência da `0004-02`
vale para a norma como vale para o `_planos.md`, e um projeto que editou a sua não pode perdê-la num
segundo bootstrap.

**A suíte inteira continua verde**, e o `lint_skill` continua limpo depois da edição do `SKILL.md`.

## Verificação

```
./scripts/test-python.sh .claude/skills/decode-and-code/scripts/tests/test_empacotamento.py
```

## Fonte

- [`0004-installable-method.md`](0004-installable-method.md), *Escopo* → *Fase 3*
- *O que foi medido* — o `move-md` ausente e o `scaffold` que morre no import
