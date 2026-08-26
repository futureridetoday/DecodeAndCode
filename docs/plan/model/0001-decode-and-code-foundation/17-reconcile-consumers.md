---
# about
name: reconcile-consumers
type: unit
project: DecodeAndCode
description: A divergência entre o método e as cópias instaladas passa a ser medida por conteúdo, não declarada por versão — que hoje diz 1.0.0 nos dois lados enquanto seis componentes diferem
tags: [decode-and-code, plugin, reconciliacao, divergencia, distribuicao]

# alvo
core: model
module: decode-and-code
block: ""
owner: model
unit_id: 0001-17
unit_type: dev

# verificação
state: verified
test: .claude/skills/decode-and-code/scripts/tests/test_reconciliacao.py
verified_at: 2026-08-26

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

# 0001-17 — reconcile-consumers

**Responsabilidade:** dizer, por componente, o que difere entre este repositório e uma cópia
instalada do método — e não escrever nada na cópia, porque atualizar consumidor é decisão de quem
o mantém.

## Contrato

| Campo | Detalhe |
|---|---|
| **Entrada** | `reconciliar.comparar(origem, copia)` e `reconciliar.relatorio(origem, copia)` — dois diretórios de skill |
| **Saída** | `comparar` devolve uma lista de dicionários `{componente, veredito, sha_origem, sha_copia}`, ordenada por nome. `relatorio` devolve uma linha por componente, mais a linha de versão declarada dos dois lados |
| **Auth** | — |
| **Efeito** | **Nenhum.** As duas funções só leem — nem na origem, nem na cópia, nem em disco nenhum |
| **Erro** | Diretório inexistente levanta `FileNotFoundError`. Cópia sem `SKILL.md` não levanta: a versão sai `não declarada`, e a comparação de componentes segue |

**Os quatro veredictos**, e o que cada um significa para quem mantém a cópia:

| Veredito | Condição | O que quer dizer |
|---|---|---|
| `idêntico` | mesmo SHA-256 | nada a fazer |
| `divergente` | os dois existem, SHA diferente | correção daqui não chegou lá, ou a cópia foi editada à mão |
| `só na origem` | existe aqui, não lá | componente novo que a cópia nunca recebeu |
| `só na cópia` | existe lá, não aqui | a cópia ganhou coisa própria — o sinal de que virou fork |

> **Versão declarada não é evidência, e é o achado que desenha esta unidade.** Medido em 2026-08-26:
> o `SKILL.md` daqui e o do `AmFlow:.claude/skills/dev-units` declaram **`version: 1.0.0` os dois**,
> e ainda assim **seis** dos nove componentes compartilhados divergem. Uma reconciliação que
> comparasse versão reportaria "em dia" e estaria errada nos seis. A versão entra no relatório como
> **contexto**, nunca como veredito.

**A cópia é lida, nunca escrita.** O plano restringe a unidade a *preparar e reportar*; publicar em
repositório público é ato humano (*Restrições conhecidas*), e nenhuma unidade escreve no AmFlow.

## Sequência

1. Escrever `reconciliar._componentes(dir_skill)`: mapa `nome relativo → SHA-256` dos arquivos da skill, ignorando `__pycache__`.
2. Escrever `comparar(origem, copia)`: percorre a união dos dois mapas e atribui um dos quatro veredictos a cada componente.
3. Ler a versão declarada dos dois `SKILL.md` por `regioes.ler_campo`, devolvendo `não declarada` quando o arquivo ou o campo faltar.
4. Escrever `relatorio(origem, copia)`: uma linha por componente e a linha de versão dos dois lados, com a ressalva de que versão igual não implica conteúdo igual.
5. Escrever `tests/test_reconciliacao.py` cobrindo os quatro veredictos e a ausência de escrita, com as duas árvores em `tempfile`.
6. Rodar `relatorio` contra `~/Code/AmFlow/.claude/skills/dev-units` e **reportar** o resultado no relatório da unidade — medição, nunca gate.
7. Rodar o gate e relatar.

## Arquivos

| Caminho | O que muda |
|---|---|
| `.claude/skills/decode-and-code/scripts/reconciliar.py` | **novo** — `comparar` e `relatorio` |
| `.claude/skills/decode-and-code/scripts/tests/test_reconciliacao.py` | **novo** — o teste declarado |
| `docs/plan/system/modelo-dev-units.md` | a seção curta que diz como se mede divergência entre cópias, e por que versão não basta |

## Dependências

A `0001-16`, pelo pacote: reconciliar pressupõe que exista uma forma definida do que é componente do
método. A `0001-01`, por `regioes.ler_campo`, que lê a versão declarada sem parsear YAML à mão.

## Normas aplicáveis

| Norma | Onde |
|---|---|
| Cópia manual não é distribuição — o caso de 2026-08-01 e o que ele custou | [`0001-decode-and-code-foundation.md`](0001-decode-and-code-foundation.md), *O que foi medido* |
| A `17` alcança repositório público: entrega diff e mecanismo, publicar é ato humano | [`0001-decode-and-code-foundation.md`](0001-decode-and-code-foundation.md), *Restrições conhecidas* |
| O `dev-units` do AmFlow está congelado — somente uso, nenhuma escrita | [`CLAUDE.md`](../../../../.claude/CLAUDE.md), *Relação com o AmFlow* |
| Comando externo: mock prova a saída, nunca o comando montado | [`scripts.md`](../../../../.claude/rules/scripts.md) |

## Critério de aceite

`comparar` devolve os quatro veredictos sobre duas árvores montadas em `tempfile`: um arquivo
idêntico nos dois lados sai `idêntico`; um com conteúdo trocado sai `divergente`; um que só existe na
origem sai `só na origem`; e um que só existe na cópia sai `só na cópia`. Cada um é um caso do teste
— quatro casos, quatro veredictos, sem item enumerado sem caso atrás.

`comparar` **não vê** `__pycache__`: uma árvore com `.pyc` plantado devolve a mesma lista que a
árvore sem ele.

A versão sai no relatório como contexto e nunca como veredito: com os dois `SKILL.md` declarando a
mesma versão e um componente divergente plantado, o relatório traz a linha de versão **e** a linha
`divergente`. Cópia sem `SKILL.md` produz `não declarada` sem levantar.

**Nenhuma das duas funções escreve.** O teste tira o SHA-256 da árvore da cópia inteira antes e
depois de rodar `comparar` e `relatorio`, e afirma que não mudou.

**A suíte inteira continua verde.**

## Verificação

```
./scripts/test-python.sh .claude/skills/decode-and-code/scripts/tests/test_reconciliacao.py
```

## Fonte

- [`0001-decode-and-code-foundation.md`](0001-decode-and-code-foundation.md), *Escopo* → *Fase 5*
- `D-23` — por que o veredito é por conteúdo e a versão é só contexto
- Medição de 2026-08-26 contra `~/Code/AmFlow/.claude/skills/dev-units`, pela própria ferramenta,
  sobre a árvore inteira — **54 componentes: 19 divergentes, 28 só na origem, 5 idênticos e 2 só na
  cópia** —, com `version: 1.0.0` declarada nos dois lados. O recorte dos **9 `scripts/*.py`**
  compartilhados é o que sustenta o argumento da versão na forma mais afiada: **3 idênticos**
  (`nomenclatura.py`, `numeracao.py`, `regioes.py`) contra **6 divergentes** (`backlog.py`,
  `lib.py`, `lint_skill.py`, `lint_unidade.py`, `scaffold.py`, `verificacao.py`).
- **Os dois `só na cópia` são o achado, e a derivação dizia que não havia nenhum** (`L-32`):
  `scripts/tests/test_deprecacao.py` — o arquivo que a `D-14` decidiu **remover deste
  repositório** — e `skill-description.md`. O veredito que a `D-23` acrescentou para distinguir
  cópia atrasada de fork encontrou, na primeira execução contra dado real, exatamente o caso que
  existe para nomear
