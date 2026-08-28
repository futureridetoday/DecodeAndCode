---
# about
name: project-bootstrap
type: unit
project: DecodeAndCode
description: A operação que cria a estrutura mínima no projeto que instala o método — _planos.md com os marcadores, _inbox/, system/ e .claude/ — idempotente e nunca destrutiva
tags: [decode-and-code, plugin, bootstrap, estrutura, instalacao]

# alvo
core: model
module: installable-method
block: ""
owner: model
unit_id: 0004-02
unit_type: dev

# verificação
state: verified
test: .claude/skills/decode-and-code/scripts/tests/test_bootstrap.py
verified_at: 2026-08-28

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

# 0004-02 — project-bootstrap

**Responsabilidade:** criar, num projeto que acabou de instalar o método, a estrutura que todo o
resto pressupõe — e não tocar em nada que já exista.

## Contrato

| Campo | Detalhe |
|---|---|
| **Entrada** | `bootstrap.iniciar(projeto)` — o caminho do projeto, **explícito** |
| **Saída** | A lista dos caminhos criados, em ordem. Lista vazia quando não faltava nada |
| **Auth** | — |
| **Efeito** | Cria diretórios e **um** arquivo. Nunca sobrescreve, nunca apaga |
| **Erro** | `FileNotFoundError` se `projeto` não existir. Nada é escrito nesse caso |

**O projeto chega por parâmetro, e é deliberado.** Antes do bootstrap o projeto não tem as marcas
que `lib.repo_root()` procura — é justamente o que a operação vai criar. Resolver a raiz aqui seria
circular. O caminho de `plan_root` vem do `config()`, componível com a entrada:
`projeto / lib.config()["plan_root"]`.

**O que a operação cria:**

| Caminho | Por quê |
|---|---|
| `<plan_root>/_planos.md` | Fonte da numeração e da situação. Sem ele, `scaffold.aprovar` morre com `FileNotFoundError` — o defeito que abriu este plano |
| `<plan_root>/_inbox/` | Onde todo plano nasce |
| `<plan_root>/system/` | Onde a norma vai morar |
| `.claude/` | `root_markers` exige `.claude/` **e** `docs/`; sem os dois a âncora da `0004-01` não resolveria o projeto depois do bootstrap. Não é criação incidental — `empacotar.materializar` já escreve em `<projeto>/.claude/rules/` (`D-04`) |

**O `_planos.md` criado precisa ser legível pelos scripts que o leem.** Frontmatter, a região
delimitada por `<!-- planos:start -->` e `<!-- planos:end -->`, e o cabeçalho da tabela dentro dela.
O esqueleto vive no script, como `porte._CONTEUDO_INICIAL` e `huddle.iniciar` já fazem — formato com
uma fonte só (`D-20` do plano `0001`), sem arquivo de template.

**`project:` do frontmatter é preenchido com o nome do diretório do projeto**, nunca fixo. É a
`L-31` do plano `0001` literal: `porte._CONTEUDO_INICIAL` trazia o nome deste repositório embutido e
ia parar no arquivo de quem instalasse.

**O que a operação não cria:** runner de teste (`D-05` — `test-python.sh` é instância deste
repositório, e o projeto declara o seu em `runners`) e `_inbox/_backlog.md` (nenhum script o lê —
conferido em 2026-08-27; é lista deste projeto, não estrutura do método).

## Sequência

1. Escrever `bootstrap.py` com `iniciar(projeto)`, que confere a existência de `projeto` antes de escrever qualquer coisa e devolve a lista do que criou.
2. Definir o esqueleto de `_planos.md` no próprio módulo, com `{projeto}` preenchido a partir do nome do diretório no momento da escrita.
3. Criar os três diretórios e o arquivo, pulando cada um que já existir — o pulo é por item, não por tudo-ou-nada.
4. Escrever `tests/test_bootstrap.py`: diretório vazio, segunda chamada, projeto que já tem `_planos.md` com conteúdo, e projeto inexistente.
5. Acrescentar o caso que amarra o bootstrap ao passo seguinte do ciclo — `numeracao.proximo_plano()` sobre o projeto recém-criado, com `lib.repo_root` apontado para ele.
6. Escrever a seção do bootstrap na norma: o que cria, o que não cria, e por que o projeto chega por parâmetro.
7. Rodar o gate e a suíte inteira, e relatar.

## Arquivos

| Caminho | O que muda |
|---|---|
| `.claude/skills/decode-and-code/scripts/bootstrap.py` | **novo** — `iniciar` e o esqueleto de `_planos.md` |
| `.claude/skills/decode-and-code/scripts/tests/test_bootstrap.py` | **novo** — o teste declarado |
| `docs/plan/system/modelo-dev-units.md` | a seção do bootstrap |

## Dependências

A `0004-01`, pela âncora: sem ela, o caso que liga o bootstrap ao `numeracao` só existe com mock, e
a `0004-05` não fecha.

## Normas aplicáveis

| Norma | Onde |
|---|---|
| Por que `.claude/` entra no bootstrap | [`0004-installable-method.md`](0004-installable-method.md), `D-04` |
| Por que o bootstrap não cria runner de teste | [`0004-installable-method.md`](0004-installable-method.md), `D-05` |
| Não há arquivo de template: o formato vive no script e na norma | [`0001-decode-and-code-foundation.md`](../0001-decode-and-code-foundation/0001-decode-and-code-foundation.md), `D-20` |
| Nome de projeto embutido em template vaza para quem instala | [`0001-decode-and-code-foundation.md`](../0001-decode-and-code-foundation/0001-decode-and-code-foundation.md), `L-31` |
| Nada específico de projeto viaja no plugin | `.claude/CLAUDE.md`, *Invariantes não negociáveis*, item 2 |

## Critério de aceite

`bootstrap.iniciar` num diretório vazio devolve os quatro caminhos criados, e a árvore resultante é
**legível pelos scripts que a leem**: `regioes.ler_regiao(_planos.md, "planos")` devolve o miolo, e
`numeracao.proximo_plano()` sobre esse projeto devolve `0001`. O formato que o script escreve é o
formato que os scripts aprovam — mesmo par que `huddle.iniciar` fechou.

Chamado de novo sobre o mesmo projeto, devolve **lista vazia** e não toca em nada: o teste compara o
conteúdo de `_planos.md` antes e depois e exige que seja idêntico. Num projeto que já tem um
`_planos.md` com linhas de plano registradas, essas linhas continuam lá.

`projeto` inexistente levanta `FileNotFoundError`, e nenhum diretório é criado — a checagem vem
antes de toda escrita, como em `empacotar.construir`.

O `_planos.md` criado **não contém o nome deste repositório**. O caso confere o texto escrito, e é a
`L-31` verificada no artefato novo em vez de descoberta depois no pacote.

**A suíte inteira continua verde.**

## Verificação

```
./scripts/test-python.sh .claude/skills/decode-and-code/scripts/tests/test_bootstrap.py
```

## Fonte

- [`0004-installable-method.md`](0004-installable-method.md), *Escopo* → *Fase 1*
- *O que foi medido* — o `FileNotFoundError` em `_planos.md` que abriu o plano
