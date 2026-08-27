---
# about
name: project-anchor
type: unit
project: DecodeAndCode
description: lib passa a resolver o projeto onde o método opera, e não o diretório onde o próprio código mora — num plugin instalado esses dois são lugares diferentes, e hoje 14 scripts morrem por causa disso
tags: [decode-and-code, plugin, ancora, lib, instalacao]

# alvo
core: model
module: installable-method
block: ""
owner: model
unit_id: 0004-01
unit_type: dev

# verificação
state: spec
test: .claude/skills/decode-and-code/scripts/tests/test_lib.py
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

# 0004-01 — project-anchor

**Responsabilidade:** dar a `lib.repo_root()` um segundo ponto de partida, para que ele resolva **o
projeto onde o método opera** e não apenas a árvore onde o próprio código mora — sem mudar nada do
que ele já resolve hoje.

## Contrato

| Campo | Detalhe |
|---|---|
| **Entrada** | `lib.repo_root()` — mesma assinatura de hoje, sem parâmetro |
| **Saída** | O caminho resolvido do projeto onde o método opera |
| **Auth** | — |
| **Efeito** | Só lê o sistema de arquivos |
| **Erro** | `RuntimeError` quando **nenhum** dos pontos de partida resolve, nomeando os dois — hoje a mensagem nomeia um só |

**O defeito, medido em 2026-08-27.** `repo_root()` sobe a partir de `Path(__file__)`. Num plugin
instalado o `__file__` está no diretório do **plugin**, que não contém as marcas do projeto e nunca
as conterá:

```
RuntimeError: raiz do repositório não localizada a partir de .../skills/decode-and-code/scripts
              — nenhum diretório acima contém .claude/ e docs/.
```

Consequência medida: **19 dos 20 módulos importam**, e só `scaffold` não — ele chama `repo_root()`
em nível de módulo, na [linha 45](../../../../.claude/skills/decode-and-code/scripts/scaffold.py),
para carregar o `move-md`. Depois do import, `lib.plan_root()` e `numeracao.proximo_plano()`
levantam; `nomenclatura.validar_nome`, que não resolve caminho, responde normalmente. **14 dos 21
scripts** chamam `repo_root`/`plan_root`.

**Dois candidatos, e só dois.** Variável de ambiente está fora (`D-02`): `CLAUDE_PLUGIN_ROOT` já
foi medido vazio — está no docstring de `lib.py` — e `CLAUDE_PROJECT_DIR` também não existe no
ambiente de uma sessão, porque é substituição literal no `hooks.json`, não variável exportada.
Restam o `__file__` e o `cwd`.

**A ordem é `__file__` primeiro, `cwd` depois, e a razão é risco, não elegância.** Nessa ordem a
mudança é estritamente aditiva: tudo que resolve hoje continua resolvendo igual, e o segundo
candidato só roda onde hoje se levanta exceção. A ordem inversa mudaria o resultado de qualquer
teste que rode com `cwd` dentro de um projeto sintético, e a suíte tem muitos — regressão que não dá
para enumerar sem ler todos.

**O nome `repo_root` fica.** Renomear para `project_root` tocaria os 14 chamadores sem mudar
comportamento nenhum, e apelido seria dois nomes para o mesmo fato (invariante 1). O conceito é o
mesmo desde sempre — a raiz da árvore sobre a qual o método opera —; o que muda é como ela se acha.

## Sequência

1. Escrever o caso que **falha hoje**: copiar `lib.py` para um diretório fora de qualquer projeto, carregá-lo por `importlib.util`, e chamar `repo_root()` com o `cwd` dentro de um projeto sintético que tenha as marcas.
2. Escrever o caso de regressão: `repo_root()` com o `cwd` num diretório de `tempfile` sem marcas continua resolvendo **este** repositório, pelo `__file__`.
3. Escrever o caso de erro: nenhum dos dois resolve, e a `RuntimeError` nomeia os dois pontos de partida.
4. Em `lib.py`, fazer `repo_root()` tentar `_find_repo_root` a partir do `__file__` e, só se isso levantar, a partir de `Path.cwd()`.
5. Reescrever a mensagem de erro para nomear os dois pontos de partida — a de hoje nomeia um e mandaria o leitor procurar no lugar errado.
6. Atualizar o docstring do módulo: o parágrafo do `CLAUDE_PLUGIN_ROOT` passa a registrar também o `CLAUDE_PROJECT_DIR` e a ordem escolhida, com a razão.
7. Rodar o gate e a suíte inteira, e relatar.

## Arquivos

| Caminho | O que muda |
|---|---|
| `.claude/skills/decode-and-code/scripts/lib.py` | `repo_root` ganha o segundo ponto de partida; mensagem de erro e docstring |
| `.claude/skills/decode-and-code/scripts/tests/test_lib.py` | os três casos — o que falha hoje, a regressão e o erro |

## Dependências

Nenhuma. É a primeira unidade do plano, e as outras quatro dependem dela.

## Normas aplicáveis

| Norma | Onde |
|---|---|
| Por que a âncora é unidade própria, e primeira | [`0004-installable-method.md`](0004-installable-method.md), `D-01` |
| Variável de ambiente está fora, e por quê | [`0004-installable-method.md`](0004-installable-method.md), `D-02` |
| `__file__` deixa de ser a única âncora e não deixa de ser âncora | [`0004-installable-method.md`](0004-installable-method.md), `D-03` |
| Nenhuma ordem é segura em todo ambiente — o que o teste não alcança | [`0004-installable-method.md`](0004-installable-method.md), `L-03` |
| Tocar só o necessário; não refatorar o que não está quebrado | `.claude/CLAUDE.md`, *Simplicidade primeiro* |

## Critério de aceite

Com `lib.py` copiado para fora de qualquer projeto e o `cwd` dentro de um projeto sintético que
tenha `.claude/` e `docs/`, `repo_root()` devolve **o projeto sintético**. Esse caso levanta
`RuntimeError` hoje, e é o que a unidade existe para virar.

Com o `cwd` num diretório de `tempfile` sem marcas, `repo_root()` continua devolvendo **este
repositório** — é o que prova que o `__file__` segue sendo âncora, e é a condição de que a suíte
inteira não se mexa.

Com nenhum dos dois resolvendo, a `RuntimeError` cita os **dois** pontos de partida tentados.
Mensagem que nomeia um só manda procurar no lugar errado, que foi exatamente o que aconteceu na
medição que originou esta unidade.

**A suíte inteira continua verde**, e aqui isso não é formalidade: 14 scripts chamam a função que
esta unidade altera, e o gate desta unidade roda só `test_lib.py`. É a `L-11` do plano `0001` outra
vez — o gate prova menos do que a unidade entrega, e a suíte é o que cobre o resto.

## Verificação

```
./scripts/test-python.sh .claude/skills/decode-and-code/scripts/tests/test_lib.py
```

## Fonte

- [`0004-installable-method.md`](0004-installable-method.md), *Escopo* → *Fase 1*
- *O que foi medido* → *A derivação mediu de novo, e achou o que está abaixo disso*
