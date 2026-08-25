---
# about
name: guideline-registry
type: unit
project: DecodeAndCode
description: Registry por projeto e a operação que liga e desliga uma guideline sem editar arquivo à mão — desligar move para fora do diretório que o Claude Code carrega, e o registry é a fonte de qual estava ativa quando
tags: [decode-and-code, guideline, registry, rules, fase-3]

# alvo
core: model
module: decode-and-code
block: ""
owner: model
unit_id: 0001-10
unit_type: dev

# verificação
state: verified
test: .claude/skills/decode-and-code/scripts/tests/test_registry.py
verified_at: 2026-08-25

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

# 0001-10 — guideline-registry

**Responsabilidade:** tornar ligar e desligar uma guideline uma **operação**, não uma edição manual —
e deixar registrado qual estava ativa em cada momento, que é o que um revisor precisa saber.

## Contrato

| Campo | Detalhe |
|---|---|
| **Entrada** | `registry.ligar(nome)` e `registry.desligar(nome)`; `registry.listar()` sem argumento |
| **Saída** | `listar()` devolve a lista de guidelines conhecidas com o estado de cada uma. `ligar`/`desligar` devolvem o caminho final |
| **Auth** | — |
| **Efeito** | Guideline ligada vive em `.claude/rules/`; desligada vive em `.claude/rules-off/`, **diretório irmão**. O `registry.json` acompanha, e é projetado — nunca editado à mão |
| **Erro** | Nome desconhecido levanta `ValueError` nomeando o que existe. Ligar o que já está ligado é **no-op**, não erro |

**Por que desligar é mover, e não um campo:**

O Claude Code carrega `.claude/rules/*.md`; não existe campo de frontmatter que desative um. Um
campo `enabled: false` seria norma que o modelo lê afirmando que não vale — o pior dos dois mundos,
e custo de contexto por nada. Mover para fora do diretório carregado desliga de verdade e mantém o
arquivo versionado, auditável e a um comando de voltar.

> **O destino é `.claude/rules-off/`, irmão, e não um subdiretório — isto foi medido, não deduzido.**
> A primeira versão desta unidade mandava mover para `.claude/rules/_off/`, e o instrumento da `05`
> mostrou o arquivo carregando de lá por `path_glob_match`: **o matcher recursa para dentro do
> subdiretório**. Desligava no disco sem desligar em contexto — falha silenciosa e indistinguível de
> sucesso, com `listar()` reportando `desligada` e a norma ainda ativa. Ver `L-26`.

> **O `registry.json` fica em `.claude/rules/` e isso é seguro, também por medição:** ele existe lá
> e **não** aparece no log de carregamento, o que prova que o diretório pega `.md` e não todo
> arquivo.

> **O `registry.json` é projeção, não fonte.** A verdade é o disco: onde o arquivo está. O registry
> registra **quando** cada guideline foi ligada ou desligada — informação que o disco não carrega e
> que um revisor precisa para responder *"qual norma estava ativa neste commit?"* (`L-02`).

## Sequência

1. Escrever `registry.py` com `listar`, `ligar` e `desligar` — sem classe, sem estado em módulo, no estilo dos outros scripts. `listar` varre `.claude/rules/` e `.claude/rules-off/` e devolve o estado derivado do disco.
2. `ligar`/`desligar` movem o arquivo entre os dois diretórios e reprojetam o `registry.json`. Validação antes de qualquer escrita: nome desconhecido levanta sem tocar em nada.
3. `desligar` recusa guideline que **não** declara `paths:` — princípio não se desliga. A `D-01` fixa que o que é ligável é escolha técnica; princípio não é rejeitável, e por isso não tem chave.
4. Projetar `registry.json` com uma entrada por guideline: nome, estado, e a data da última transição. Reprojetado inteiro a cada operação, no padrão de região das outras projeções deste repositório.
5. Escrever `tests/test_registry.py` cobrindo o critério de aceite, com árvores montadas em `tempfile.TemporaryDirectory()`. Artefato de teste vem de `fixtures.rule()` (`L-21`).
6. Registrar a operação na norma, na seção *Camada normativa*, ao lado do manifesto que a `09` escreveu — duas frases, sem recopiar o docstring.
7. Rodar o gate e relatar, incluindo o resultado de desligar e religar a guideline real que a `09` entregou.

## Arquivos

| Caminho | O que muda |
|---|---|
| `.claude/skills/decode-and-code/scripts/registry.py` | **novo** — `listar`, `ligar`, `desligar` |
| `.claude/rules/registry.json` | **novo** — projeção do estado e das transições; fica no diretório de rules porque `.json` não carrega, medido |
| `docs/plan/system/modelo-dev-units.md` | duas frases sobre a operação, na seção *Camada normativa* |
| `.claude/skills/decode-and-code/scripts/tests/test_registry.py` | **novo** — o teste declarado |

## Dependências

A unidade `0001-09`, que entrega a primeira guideline e o `lint_guideline` que o registry usa para
recusar desligar um princípio.

## Normas aplicáveis

| Norma | Onde |
|---|---|
| Camada normativa e o manifesto de guideline | [`modelo-dev-units.md`](../../system/modelo-dev-units.md), seção *Camada normativa* |
| Regiões e projeção — quem escreve o quê | [`modelo-dev-units.md`](../../system/modelo-dev-units.md), seção *Regiões* |
| `D-01` — guideline diz escopo de validade, não opcionalidade | [`0001-decode-and-code-foundation.md`](0001-decode-and-code-foundation.md), seção *Decisões* |
| `L-02` — cópia versionada, e o revisor vê em qualquer commit qual texto estava ativo | [`0001-decode-and-code-foundation.md`](0001-decode-and-code-foundation.md), seção *Lacunas* |
| Projeção nunca se edita à mão | `.claude/CLAUDE.md`, invariantes 3 e 4 |

## Critério de aceite

`desligar` move a guideline para `.claude/rules-off/` e ela **deixa de estar sob `.claude/rules/`,
inclusive em qualquer subdiretório dele**; `ligar` devolve ao lugar. O conteúdo do arquivo é
**byte-idêntico** antes e depois do par — desligar não reescreve norma.

> **O que este critério prova, e o que não prova.** Teste de unidade alcança o **destino** — que o
> arquivo saiu da árvore carregada. Que ele **deixou de entrar em contexto** é comportamento de
> sessão, e nenhum teste daqui o mede. A prova real é a sessão registrada em *Validação de ponta a
> ponta*, e foi ela que reprovou a primeira versão desta unidade.

`listar` deriva o estado do **disco**, não do `registry.json`: com o arquivo movido à mão para
`rules-off/`, `listar` reporta desligada mesmo que o registry diga o contrário. Divergência entre os dois
é reportada, nunca silenciada.

`desligar` sobre um **princípio** — rule sem `paths:` — recusa, e a mensagem diz por quê. Nome
desconhecido levanta `ValueError` nomeando os que existem, sem escrever nada. Ligar o que já está
ligado é no-op silencioso.

Desligada e religada a guideline real da `09`, `rules.lint_guideline()` continua devolvendo `[]`
sobre ela.

**A suíte inteira continua verde.**

## Verificação

```
./scripts/test-python.sh .claude/skills/decode-and-code/scripts/tests/test_registry.py
```

Último resultado: não executado.

## Fonte

- [`0001-decode-and-code-foundation.md`](0001-decode-and-code-foundation.md), *Escopo* → Fase 3
- `D-01` e `L-02`, que fixam respectivamente o que é ligável e por que a cópia é versionada
- Comportamento do carregamento medido em **2026-08-24**, com o instrumento da `0001-05`: `.claude/rules/*.md` carrega, `.json` no mesmo diretório **não**, e **subdiretório carrega** — o `_off/` original não desligava nada. Não há campo de desativação; daí desligar ser mover para fora da árvore
