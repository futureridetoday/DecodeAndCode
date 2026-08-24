---
# about
name: language-policy
type: unit
project: DecodeAndCode
description: A norma de linguagem e a medição que a fundamenta migram do AmFlow desacopladas, e o CLAUDE.md perde as três frases que hoje as duplicam — a norma passa a ter uma fonte só
tags: [decode-and-code, norma, linguagem, migracao, l-15]

# alvo
core: model
module: decode-and-code
block: ""
owner: model
unit_id: 0001-08
unit_type: dev

# verificação
state: verified
test: .claude/skills/decode-and-code/scripts/tests/test_normas_system.py
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

# 0001-08 — language-policy

**Responsabilidade:** fechar a dependência da norma em dois documentos que não existem aqui, sem
criar segunda fonte para fatos que o `CLAUDE.md` já afirma.

## Contrato

| Campo | Detalhe |
|---|---|
| **Entrada** | Os dois documentos no AmFlow — **somente leitura** |
| **Saída** | `docs/plan/system/language-policy.md` e `docs/plan/system/estudo-runtime-e-dependencias.md`, desacoplados |
| **Auth** | — |
| **Efeito** | Os quatro links da norma passam a resolver; o `CLAUDE.md` encolhe |
| **Erro** | — |

**O que migra, e o que fica** — medido em 2026-08-24: 21 das 165 linhas do `language-policy` e 15 das
181 do `estudo-runtime` são instância do AmFlow.

| § | Conteúdo | Decisão |
|---|---|---|
| 1 | Nenhuma linguagem é proibida | **Migra a regra.** A revogação do `native-only` e o invariante `D10` do Worker são instância e saem |
| 2 | O critério de escolha já é norma | **Migra reapontado** para o `CLAUDE.md` deste repositório |
| 3 | Ambientes medidos — Cowork 3.10.12, browser 3.12.3, macOS 3.9.6; `jq` só no Cowork; `CLAUDE_PLUGIN_ROOT` vazia | **Migra inteira.** É medição, e a `D-10` diz para não re-derivar medição |
| 4 | Python 3.10 porque é o que o Cowork tem | **Migra.** É o que o `scripts/test-python.sh` daqui já exige |
| 5 | Dependência externa exige fallback declarado | **Migra**, sem a citação ao `smoke-tests.py` do Hub |
| 6 | O que fica superado — 11 arquivos do `docs/mvp/` do AmFlow | **Não migra.** Instância pura, e sem objeto aqui |
| 7 | O que esta norma não faz | **Migra** |

> **Migração direta seria o erro.** O `CLAUDE.md` deste repositório já afirma Python 3.10, stdlib
> pura e fallback declarado, e já traz o critério código ↔ markdown. Copiar o documento inteiro daria
> **duas fontes** para três fatos — o invariante 1, que é o que este plano inteiro persegue.

## Sequência

1. Copiar os dois documentos do AmFlow e retirar deles a instância: cores, serviços, `docs/mvp/`, o invariante `D10` do Worker, a citação ao `smoke-tests.py`, e a seção 6 inteira. Generalizar afirmação de mecanismo escrita sobre exemplo do AmFlow — **nunca deletar a afirmação junto com o exemplo**, que é o erro que a `L-14` registra.
2. Ajustar o frontmatter dos dois: `project: DecodeAndCode`, e os links relativos apontando para este repositório.
3. Reapontar a seção 2 do `language-policy` para `.claude/CLAUDE.md` daqui, e conferir que a seção citada existe com esse nome.
4. Trocar no `CLAUDE.md` a seção *Linguagem* — as três frases sobre 3.10, stdlib e fallback — por **uma linha** apontando para a norma. O fato passa a ter uma fonte, e o arquivo encolhe, que é o objetivo declarado dele.
5. Conferir que os quatro pontos da norma que citam `language-policy.md` e o que cita `estudo-runtime-e-dependencias.md` resolvem em disco.
6. Escrever `tests/test_normas_system.py`, o teste declarado: todo link relativo dos documentos de `docs/plan/system/` resolve, e nenhum deles contém instância do AmFlow.
7. Rodar o gate e relatar. **Nenhuma escrita no AmFlow.**

## Arquivos

| Caminho | O que muda |
|---|---|
| `docs/plan/system/language-policy.md` | **novo** — migrado desacoplado, sem a seção 6 |
| `docs/plan/system/estudo-runtime-e-dependencias.md` | **novo** — migrado desacoplado |
| `.claude/CLAUDE.md` | a seção *Linguagem* vira uma linha apontando para a norma |
| `.claude/skills/decode-and-code/scripts/tests/test_normas_system.py` | **novo** — o teste declarado |

## Dependências

Nenhuma unidade. Depende de acesso de leitura ao AmFlow, que é onde os dois documentos vivem.

## Normas aplicáveis

| Norma | Onde |
|---|---|
| `D-10` — o determinismo migra, a camada normativa nasce nova | [`0001-decode-and-code-foundation.md`](0001-decode-and-code-foundation.md), seção *Decisões* |
| `L-14` — generalizar não é deletar | [`0001-decode-and-code-foundation.md`](0001-decode-and-code-foundation.md), seção *Lacunas* |
| Uma fonte por fato | `.claude/CLAUDE.md`, invariante 1 |
| Nada específico de projeto viaja no plugin | `.claude/CLAUDE.md`, invariante 2 |
| O `CLAUDE.md` fica pequeno, e é de propósito | `.claude/CLAUDE.md`, seção de mesmo nome |

## Critério de aceite

Os dois documentos existem em `docs/plan/system/` e **não contêm instância do AmFlow** — nem core,
nem serviço, nem caminho de `docs/mvp/`, nem o invariante `D10` do Worker. A seção 6 não existe.

Todo link relativo dos documentos de `docs/plan/system/` **resolve em disco**, e os quatro pontos da
norma que citavam `language-policy.md` deixam de ser links mortos.

O `CLAUDE.md` **não repete** o que a norma diz: Python 3.10, stdlib e fallback aparecem numa linha
que aponta, não em três que afirmam. E o arquivo fica menor do que estava.

**A suíte inteira continua verde.**

## Verificação

```
./scripts/test-python.sh .claude/skills/decode-and-code/scripts/tests/test_normas_system.py
```

Último resultado: não executado.

## Fonte

- [`0001-decode-and-code-foundation.md`](0001-decode-and-code-foundation.md), *Escopo* → *Correções descobertas na execução*, e `L-15`
- Documentos de origem, lidos em 2026-08-24: `AmFlow:docs/plan/system/language-policy.md` (165 linhas, 21 de instância) e `AmFlow:docs/plan/system/estudo-runtime-e-dependencias.md` (181 linhas, 15 de instância). Leitura apenas
- Duplicação medida contra `.claude/CLAUDE.md` deste repositório, seção *Linguagem*
