---
# about
name: norm-split
type: unit
project: DecodeAndCode
description: A norma se divide em mecanismo e registro — o operativo fica no arquivo que a skill já cita e viaja no pacote, e a evidência, as decisões e a história deste projeto saem para um documento que fica e é citado
tags: [decode-and-code, norma, divisao, mecanismo, registro]

# alvo
core: model
module: installable-method
block: ""
owner: model
unit_id: 0004-03
unit_type: dev

# verificação
state: verified
test: .claude/skills/decode-and-code/scripts/tests/test_normas_system.py
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

# 0004-03 — norm-split

**Responsabilidade:** separar, dentro da norma, o **mecanismo** — que qualquer projeto usa — do
**registro** deste projeto — evidência, decisões e história —, de modo que o primeiro possa viajar
no pacote sem levar o segundo junto.

## Contrato

| Campo | Detalhe |
|---|---|
| **Entrada** | `docs/plan/system/modelo-dev-units.md`, hoje com as duas metades juntas |
| **Saída** | Dois documentos: o mecanismo, no mesmo caminho; e `docs/plan/system/registro-dev-units.md`, novo |
| **Auth** | — |
| **Efeito** | Reescreve um arquivo e cria outro. Nenhum script muda |
| **Erro** | — |

**O mecanismo fica com o nome que já tem, e isso é o que torna a unidade barata** (`D-07`).
`SKILL.md` cita `<plan_root>/system/modelo-dev-units.md`, e **35 arquivos** citam a norma — 21
deles unidades do plano `0001`, fechado. Mantendo o nome no mecanismo, nenhum dos 35 precisa mudar,
e nenhuma unidade fechada é reescrita. **Unidade de plano fechado não se reescreve**: ela registra o
que a norma dizia quando aquele trabalho foi feito.

**A fronteira, seção a seção.** Medida em 2026-08-27 sobre as 1250 linhas atuais:

| Vai para o **registro** | Por quê |
|---|---|
| *Fundamentação — por que este modelo, e não outro* | Comparação com alternativas, feita uma vez, neste projeto |
| *Diagnóstico medido — o padrão atual* | Medição do AmFlow — instância pura |
| *Rastreamento de objetivos* | Onde vivem as 6 referências a `METR`/`DORA` |
| *Decisões* | As decisões numeradas, com a história de cada uma |
| *Referências* | Bibliografia deste projeto |

O resto é mecanismo: *Conceitos estruturantes*, *Modelo proposto*, *Formato do arquivo de unidade*,
*Formato do plano*, *Porte medido*, *Avaliação de escopo*, *Nomenclatura*, *Camada de execução*,
*Huddle* e *Fluxo completo*.

**A tabela acima é orientação, não contrato** (norma, *Precedência entre os blocos*). A fronteira
real se decide parágrafo a parágrafo, e o trabalho de verdade está dentro das seções de mecanismo:
elas citam `0001-XX`, `L-XX` e `D-XX` como proveniência, e cada citação dessas é instância. **Onde a
proveniência importa, ela vira link para o registro; onde não importa, sai.** O que não pode é a
regra operativa depender de abrir o registro para ser entendida.

**O registro cita o mecanismo; o mecanismo não cita o registro.** Citação nas duas direções faria
o mecanismo depender de um arquivo que não viaja — que é exatamente o defeito que este plano
existe para corrigir.

## Sequência

1. Ler a norma inteira e decidir a fronteira parágrafo a parágrafo, a partir da tabela do Contrato.
2. Criar `registro-dev-units.md` com frontmatter completo e as seções de registro, abrindo com uma nota que diz o que ele é e aponta para o mecanismo.
3. Remover essas seções de `modelo-dev-units.md` e abrir o arquivo com a nota inversa: este é o mecanismo, o registro deste projeto está no vizinho.
4. Varrer as seções de mecanismo eliminando instância: cada `0001-XX`, `L-XX`, `docs/mvp` e `AmFlow` vira link para o registro ou sai.
5. Estender `test_normas_system.py` com os invariantes dos dois documentos — sem módulo novo, ver *Critério de aceite*.
6. Conferir que os 35 citadores continuam resolvendo, com a checagem de links que o próprio `test_normas_system.py` já faz.
7. Rodar o gate e a suíte inteira, e relatar.

## Arquivos

| Caminho | O que muda |
|---|---|
| `docs/plan/system/modelo-dev-units.md` | fica só o mecanismo; nota de abertura nova |
| `docs/plan/system/registro-dev-units.md` | **novo** — evidência, decisões e história deste projeto |
| `.claude/skills/decode-and-code/scripts/tests/test_normas_system.py` | os invariantes dos dois documentos |

## Dependências

Nenhuma técnica. Precede a `0004-04`, que leva o mecanismo no pacote — dividir depois de empacotar
faria o pacote sair sujo uma vez.

## Normas aplicáveis

| Norma | Onde |
|---|---|
| O mecanismo mantém o caminho que a skill já cita | [`0004-installable-method.md`](0004-installable-method.md), `D-07` |
| A divisão não tem oráculo para "a metade certa foi para o lugar certo" | [`0004-installable-method.md`](0004-installable-method.md), `L-02` |
| Contrato e critério mandam; a tabela de fronteira é orientação | [`modelo-dev-units.md`](../../system/modelo-dev-units.md), *Precedência entre os blocos* |
| Uma fonte por fato — norma citada em dois lugares é drift | `.claude/CLAUDE.md`, *Invariantes não negociáveis*, item 1 |
| Nada específico de projeto viaja no plugin | `.claude/CLAUDE.md`, *Invariantes não negociáveis*, item 2 |
| Subtração antes de adição: `reaproveitar` vem antes de `criar` | `.claude/rules/principles.md`, *Subtração antes de adição* |

## Critério de aceite

`modelo-dev-units.md` não contém nenhuma das marcas de instância deste projeto: `0001-`, `docs/mvp`,
`AmFlow`, `METR`, `DORA`, nem o nome do repositório. Hoje ele contém **11, 3, 3 e 6** ocorrências
das quatro primeiras — medido em 2026-08-27 —, e cada uma precisa ter saído ou virado link.

`registro-dev-units.md` existe, tem frontmatter completo, e **cita** `modelo-dev-units.md`. A
verificação inversa também vale: o mecanismo **não** cita o registro, porque não pode depender de um
arquivo que não viaja.

Todo link relativo dos dois documentos resolve em disco — é a checagem que `test_normas_system.py`
já faz para os documentos de linguagem, aplicada aos dois novos.

**Os invariantes entram em `test_normas_system.py`, sem módulo novo.** O arquivo já verifica
exatamente esta classe de coisa — `_MARCAS_AMFLOW` e a resolução de links — para
`language-policy.md`. Criar um `lint_norma.py` seria `criar` onde `reaproveitar` resolve, e o
princípio ordena o contrário. Este verificador é sobre **o artefato deste repositório**: quem
instala recebe o mecanismo pronto e não divide nada.

**A suíte inteira continua verde**, e os 35 arquivos que citam a norma continuam com links que
resolvem.

## Verificação

```
./scripts/test-python.sh .claude/skills/decode-and-code/scripts/tests/test_normas_system.py
```

## Fonte

- [`0004-installable-method.md`](0004-installable-method.md), *Escopo* → *Fase 2*
- `D-26` do plano `0001` — a decisão de dividir, e por que ficou aberta lá
