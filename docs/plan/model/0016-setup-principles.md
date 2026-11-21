---
# about
name: setup-principles
type: plan
project: DecodeAndCode
description: O setup passa a sugerir e gravar princípios do projeto — north star a partir do objetivo, extraídos e propostos, com o teste aplicado à vista e teto de cinco —; reabre a D-04 do 0009
tags: [decode-and-code, setup, principio, norma]

# alvo
plan_id: "0016"
plan_size: médio
plan_type: feature
core: model
module: setup-principles
block: ""

# history
author: Claude
created: 2026-11-20
status: done
version: 1.1.0
updated: 2026-11-20
approved_by: "Bortoli Rafael"
approved_at: "2026-11-20"

# system
scope: project
auto_load: false
dependencies: []
---

# O setup sugere princípios

> **Tipo proposto: `feature`** — capacidade nova do setup, com código (`rules`, `setup`, `dc.py`) e
> norma. **Porte proposto: `médio`** — pela *Quando cada porte cabe*, há passos (pergunta 1, não), e
> uma sessão os executa em sequência (pergunta 2, sim). O humano confirma tipo e porte na aprovação.
>
> **Este plano reabre a `D-04` do `0009`** ("o setup não sugere princípio", decidida pelo humano em
> 2026-11-15), por decisão do humano em 2026-11-20.
>
> **Dividido na revisão de 2026-11-20** (decisão do humano): a parte de recursos do projeto virou
> [`setup-resources`](../_inbox/setup-resources.md), que vem depois deste.

## Objetivo

**Clarificar.** O setup termina com **zero** princípios no projeto que instala. Isso acontece por
construção: a `D-04` do `0009` o proíbe, e os princípios do método não viajam no pacote
(`dist/decode-and-code/` leva só `hooks/` e `skills/`; a `D-06` do `apply-plugin-review` levou os
gates para a norma e deixou `principles.md` fora). **Métrica:** princípios em
`.claude/rules/principles.md` ao fim do setup. Hoje 0. Alvo: de 1 a 5, ideal 3, cada um com origem
e teste aplicado visíveis na conversa. **Beneficiário:** quem roda o setup num projeto.

**Evitar.**

| Alternativa | Por que não basta |
|---|---|
| Manter a `D-04`: achado com cara de princípio vira `observação` no huddle e depois plano com unidade `norma` | Um plano inteiro para cada frase de direção. O humano decidiu abrir uma segunda porta (`D-05`) |
| Escrever o princípio no `CLAUDE.md` | A `D-05` do `0009` proíbe o setup de escrever ali |
| Levar o `principles.md` deste repositório no pacote | Recusado pela `D-06` do `apply-plugin-review`, porque seria a instância deste projeto viajando. E não cobre o north star de cada projeto |
| Catálogo de princípios por tipo de projeto | Sem dado de repetição (`D-06`) |

**Reduzir.** Um escritor (`dc.py criar-principio`), que impõe o teto e o formato por script, não
pelo texto da skill; um valor novo de `origem`; uma etapa de texto no setup; e a norma.

## Gates

| Gate | Resposta |
|---|---|
| **A — necessidade real** | **Sim, com base estreita, somada a exigência explícita do humano** (2026-11-20; protocolo de exceção, *exigência explícita*). Medido: a ausência. O setup grava 0 princípios por construção (`setup/SKILL.md`, etapas 2 e 3; `D-04` do `0009`), e os do método não chegam ao projeto (`D-06` do `apply-plugin-review`). **Não medido:** nenhum incidente registrado de decisão errada por falta de princípio, aqui ou no AmFlow |
| **B — mínimo viável** | Cortado e reabrível: **catálogo por tipo de projeto** (`D-06`); **"Na prática"** no princípio gerado (`D-05`); **escopo pelo `amflow-worker`** (`D-07`); **huddle como terceira porta de princípio**, porque o *Decidir* do huddle já leva à porta existente (`P-02`); **script que classifica o projeto como novo ou em andamento**: a skill decide com a pessoa, e o north star vale nos dois casos |

## Decisões

Tomadas pelo humano (Bortoli) em conversa em 2026-11-20. São decisões, não hipóteses.

| # | Decisão |
|---|---|
| D-01 | **Reabre a `D-04` do `0009`: o setup sugere princípio** |
| D-02 | **Projeto novo: os princípios começam vazios, exceto um north star** proposto a partir do objetivo do `## Perfil`. Molde: *Enunciado* = o objetivo; *Teste* = a mudança aproxima o projeto do objetivo? Exemplo, para um design system multimarcas com tokens vindos do Figma: "Marca nova não exige código novo. Teste: adicionar uma marca muda só tokens vindos do Figma." Os demais nascem pelo huddle, com o tempo |
| D-03 | **Projeto em andamento: no início do setup, ler o projeto e sugerir princípios**, como já se faz com as guidelines. Há duas origens, sempre visíveis para a pessoa. `extraído`: o projeto já o afirma, e a sugestão cita o arquivo, com origem `arquivo <caminho>`. `proposto`: inferido, simples, ligado diretamente ao objetivo do projeto |
| D-04 | **Teste ajustado para princípio de projeto:** "uma equipe competente, trabalhando **neste** projeto, pode rejeitar isso?". Cada sugestão mostra o teste aplicado e por que passou, ou por que caiu para guideline. **Muda a norma explicitamente** |
| D-05 | **O setup grava o princípio aprovado na conversa.** É uma segunda porta, além do plano com unidade `norma`, e `create-principle.md` e a norma mudam para aceitá-la. **Teto de 5 princípios, ideal 3.** Texto objetivo e compacto, porque carrega em toda sessão: só *Enunciado* e *Teste*, sem *Na prática* |
| D-06 | **Sem catálogo de princípios por tipo de projeto agora.** As propostas saem do perfil. Reabre só com dado de repetição |
| D-07 | **O escopo de projeto feito pelo plugin `amflow-worker` fica fora deste plano.** É temporário; o decode-and-code o absorve depois, por plano próprio. O setup continua lendo o `## Perfil` |
| D-08 | **Divisão em dois planos, princípios primeiro.** Decidida pelo humano na revisão de 2026-11-20 |
| D-09 | **Aceita a recomendação do `P-01`: o setup oferece os três princípios do método**, um por vez e rejeitáveis, dentro do teto. O texto viaja na norma, seção *Camada normativa*, que é a fonte; o `principles.md` de cada projeto, este incluído, é instância. Decidida pelo humano em 2026-11-20, antes da execução |
| D-10 | **Aceita a recomendação do `P-02`: o huddle não ganha *Promover → princípio*.** Decidida pelo humano em 2026-11-20 |
| D-11 | **Aceita a recomendação do `P-03`: princípio extraído de `CLAUDE.md` ou `.claude/CLAUDE.md` se registra como `existente`, sem cópia.** Decidida pelo humano em 2026-11-20 |

### Pendentes de decisão — decididos

As três perguntas abaixo foram decididas pelo humano em 2026-11-20, na aprovação: viraram `D-09` a
`D-11`. O texto fica como registro do que se perguntou.

| # | Pergunta | Recomendação do Claude |
|---|---|---|
| P-01 | O setup **oferece os princípios do método** ao projeto, um por vez e rejeitáveis, o que fecha a lacuna de eles não viajarem? | **Sim, dentro do teto.** Três ressalvas para decidir junto. (1) O *protocolo de exceção* não tem *Enunciado* e *Teste*, então não cabe no formato da `D-05`: são três princípios oferecíveis, não quatro. (2) Os três mais o north star dão 4 e deixam uma vaga no teto. (3) O texto só existe na instância deste repositório, e o pacote não o leva (`D-06` do `apply-plugin-review`). Se for sim, o plano decide antes onde o texto viaja, com uma fonte só. A candidata é a norma, seção *Camada normativa*, que já viaja e que `dc.py explicar camada-normativa` imprime; o `principles.md` deste repositório passaria a citá-la |
| P-02 | O huddle ganha *Promover → princípio*? | **Não.** "Os demais nascem pelo huddle" já se cumpre pelo *Decidir*, com destino na porta do plano com unidade `norma`, e a `D-05` nomeou só o setup como segunda porta |
| P-03 | Princípio extraído de arquivo que já carrega em toda sessão (`CLAUDE.md`, `.claude/CLAUDE.md`)? | **Registrar como `existente`, sem copiar** para `principles.md`. É a `D-05` do `0009` estendida: o que eles carregam não se repete. Extraído de `README`, `CONTRIBUTING` e afins, que não carregam, grava-se normalmente |

## Tarefas

- [x] Norma, *Camada normativa*: princípio de projeto com o teste ajustado (`D-04`), o formato compacto (*Enunciado* e *Teste*), o teto de 5 com ideal 3, e as duas portas: plano com unidade `norma`, e setup com aprovação na conversa (`D-05`). O teste original passa para a norma ao lado do ajustado, cada um com o que decide, o que fecha a `L-02`. Os três princípios do método, em formato compacto, como fonte do que o setup oferece (`D-09`). *Setup — o primeiro uso*: o critério de sugestão de princípio (north star, princípios do método, `extraído`, `proposto`) substitui "o setup não sugere princípio"
- [x] `rules.criar_principio` e `dc.py criar-principio` (JSON `{nome, enunciado, teste}` pelo stdin), com teste. O comando acrescenta `## <nome>`, *Enunciado* e *Teste* a `.claude/rules/principles.md` e cria o arquivo com frontmatter se faltar. Recusa o sexto princípio, contando as seções com `**Enunciado:**` em **toda** rule sem `paths:` de `.claude/rules/`, não só em `principles.md` (fecha a `L-03`; o `principles.md` deste repositório tem seis seções e três princípios), recusa nome repetido, e grava só se passar em `rules.lint_rule`
- [x] `setup.ORIGENS` ganha `proposto`, com teste. `extraído` usa a origem `arquivo <caminho>`, que já existe
- [x] `setup/SKILL.md`: etapa de princípios entre o perfil e as guidelines. Primeiro o north star, a partir do objetivo; depois os extraídos, com o arquivo citado; depois os propostos. Cada sugestão mostra a origem, o teste aplicado e por que passou ou caiu para guideline. **Aprovar**, **Editar** e **Rejeitar**, como nas guidelines; o que cai para guideline segue para a etapa seguinte. Sai o caminho "princípio vira `observação` no huddle", e `criar-principio` entra na lista de subcomandos
- [x] `docs/recursos/create-principle.md` (segunda porta, formato compacto, teto), `docs/recursos/setup.md` (critério e etapa) e `README.md` (*Como cada camada nasce*, linha do princípio)
- [x] `scripts/test-python.sh` verde (a suíte inteira); `lint_skill` sem problema na `setup/SKILL.md`
- [x] Remedição no projeto de prova (*Remedição*)

## Oráculo

| Alvo | Como se sabe que funcionou |
|---|---|
| `criar-principio` | Teste: grava a seção no formato compacto; cria o arquivo ausente com frontmatter válido; recusa o sexto, o nome repetido e o que não passa em `lint_rule`, sem deixar nada no disco |
| `setup-registrar` | Teste: `proposto` aceito; outro valor fora do vocabulário continua saindo `1` |
| Norma | *Camada normativa* carrega o teste ajustado e as duas portas; *Setup* não diz mais "não sugere princípio"; `dc.py explicar camada-normativa` imprime o teste ajustado |

## Remedição

Num projeto de prova **em andamento**, com `CLAUDE.md` e um `README` que afirma uma direção:

1. O setup sugere o north star, um `extraído` do `README` com o arquivo citado e um `proposto`. Cada
   um mostra o teste aplicado. Um rejeitado cai para guideline com o porquê.
2. O aprovado está em `.claude/rules/principles.md`, só com *Enunciado* e *Teste*, e o
   `setup.md` registra a origem.

Num projeto de prova **novo**, o setup sugere só o north star.

### Resultado — 2026-11-20

Conduzida por `claude -p` (Claude Code 2.1.327), em turnos encadeados por `--resume`, com o pacote
construído por `empacotar.construir` no scratchpad da sessão que orquestrou e carregado por
`--plugin-dir` (`decode-and-code@inline`, que prevaleceu sobre o instalado). Projetos de prova
descartáveis: um **em andamento** (design system multimarcas, `CLAUDE.md` com duas regras do time e
`README` com três direções) e dois **novos** (portal de vagas). Mesmo desvio do `0009`: em `-p` não há
ferramenta de perguntas, e cada resposta foi um turno.

| Alvo | Resultado |
|---|---|
| Ordem da etapa 2 | North star, os três do método, o extraído; em projeto novo, só o north star e os do método, com "os outros vão surgir pelo huddle" |
| Teste aplicado à vista | Em toda sugestão, com o porquê ligado ao projeto |
| Extraído | WCAG AA do `README`, com a seção citada e origem `arquivo README.md` |
| `CLAUDE.md` (`D-11`) | As duas regras do time registradas como `existente`, uma como princípio e outra como guideline, sem cópia |
| Cai para guideline | "Todo estilo é feito com Tailwind", pedido pela pessoa como princípio: recusado pelo teste ("diz o que decidir, não como") e levado à etapa 3 |
| Editar → edição livre | Aplicou as duas mudanças e voltou com Aprovar, Editar e Rejeitar |
| Rejeitar | Registrado com o motivo dado pela pessoa |
| Teto | O modelo anunciou o teto e o ideal a cada passo e apontou a sobreposição entre princípios; a recusa do sexto só foi provada pelo teste de `criar_principio` |
| Disco | `principles.md` com quatro seções, só *Enunciado* e *Teste*, `lint_rule` sem problema; `setup.md` com a origem de cada decisão |

**Achado corrigido nesta remedição:** nos dois primeiros projetos o north star saiu com o *Teste* do
molde, literal — "a mudança aproxima o projeto desse objetivo" —, que não verifica nada. A etapa 2 da
`setup/SKILL.md` e o critério da norma passaram a pedir a condição verificável que só aquele objetivo
produz, e a nomear a frase genérica como o que não serve. Remedido num terceiro projeto, com o pacote
reconstruído: o *Teste* saiu concreto ("uma vaga sem faixa salarial é recusada, e a faixa aparece em
toda tela onde a vaga aparece").

**Achados menores, sem lacuna:** o modelo montou uma chave com acento, o `setup-registrar` recusou e
ele corrigiu na tentativa seguinte; um caminho do pacote digitado errado foi negado e refeito certo.

**Não medido:** a sessão no app, com a ferramenta de perguntas e a contagem de pedidos de permissão
(`L-04` abaixo).

## Independência

**Ordem: antes do `setup-resources`.** Os dois tocam `setup/SKILL.md` e a norma, seção *Setup*; em
paralelo, seria a concorrência que a norma barra. Nada deste plano depende daquele.

**Concorrência.** Nenhum plano está `em desenvolvimento` em `_planos.md`. No `_inbox` resta o
`apply-plugin-review` (rascunho de 2026-10-14). A tarefa 16 dele, `skill-procedure-only`, reescreve
todo `SKILL.md`, e a `D-06` dele é a decisão que `P-01` revisita (huddle `H-18`).

## Lacunas

| # | Lacuna | Detalhe |
|---|---|---|
| L-01 | **O benefício do princípio não tem medição definida** | A métrica de 0 para 1 a 5 mede preenchimento. Decisão melhor por ter princípio só se observa em uso, no huddle ou num incidente evitado |
| L-02 | **O teste original e o ajustado não têm fronteira escrita** | O teste da `0001` decide o que viaja no plugin; o da `D-04` decide o que é princípio do projeto. A primeira tarefa não diz se o ajustado substitui ou se soma. E `principles.md` cita o teste como "norma, seção *Princípio e guideline separam-se por um teste*", seção que hoje só existe no plano `0001`, não na norma (revisão de 2026-11-20). **Fechada em 2026-11-20** pela tarefa 1: os dois recortes estão na norma, *Camada normativa → Princípio*, e `principles.md` passou a citar essa seção |
| L-03 | **O teto conta só `principles.md`** | `descoberta` trata como princípio toda rule sem `paths:` (`registry._e_guideline`), mas `criar-principio` conta as seções com `**Enunciado:**` só em `principles.md`. Projeto com princípio em outro arquivo sem `paths:` passa do teto sem recusa (revisão de 2026-11-20). **Fechada em 2026-11-20** pela tarefa 2: `criar_principio` conta em toda rule sem `paths:` (`test_conta_princípio_em_outra_rule_sem_paths`) |
| L-04 | **A etapa 2 não foi medida no app** | A remedição rodou em `claude -p`, sem a ferramenta de perguntas. O comportamento das opções Aprovar, Editar e Rejeitar pela ferramenta, e a ausência de pedido de permissão para `criar-principio`, só uma sessão no app mostra, como no `0013` |

## Fonte

- [`0009-onboard-new-project.md`](0009-onboard-new-project/0009-onboard-new-project.md), `D-04` e `D-05`
- [`0001-decode-and-code-foundation.md`](0001-decode-and-code-foundation/0001-decode-and-code-foundation.md), *Princípio e guideline separam-se por um teste*
- [`modelo-dev-units.md`](../system/modelo-dev-units.md), *Camada normativa*, *Setup — o primeiro uso*, *Avaliação de escopo*, *Quando cada porte cabe*, *Tipo de plano*
- [`create-principle.md`](../../recursos/create-principle.md), [`setup.md`](../../recursos/setup.md)
- [`apply-plugin-review.md`](../_inbox/apply-plugin-review.md), `D-06` e `L-07`
- `.claude/skills/setup/SKILL.md`, `.claude/skills/decode-and-code/scripts/setup.py`, `rules.py`, `descoberta.py`

## Backlog

<!-- backlog:start -->
- [x] Norma, *Camada normativa*: princípio de projeto com o teste ajustado (`D-04`), o formato compacto (*Enunciado* e *Teste*), o teto de 5 com ideal 3, e as duas portas: plano com unidade `norma`, e setup com aprovação na conversa (`D-05`). O teste original passa para a norma ao lado do ajustado, cada um com o que decide, o que fecha a `L-02`. Os três princípios do método, em formato compacto, como fonte do que o setup oferece (`D-09`). *Setup — o primeiro uso*: o critério de sugestão de princípio (north star, princípios do método, `extraído`, `proposto`) substitui "o setup não sugere princípio"
- [x] `rules.criar_principio` e `dc.py criar-principio` (JSON `{nome, enunciado, teste}` pelo stdin), com teste. O comando acrescenta `## <nome>`, *Enunciado* e *Teste* a `.claude/rules/principles.md` e cria o arquivo com frontmatter se faltar. Recusa o sexto princípio, contando as seções com `**Enunciado:**` em **toda** rule sem `paths:` de `.claude/rules/`, não só em `principles.md` (fecha a `L-03`; o `principles.md` deste repositório tem seis seções e três princípios), recusa nome repetido, e grava só se passar em `rules.lint_rule`
- [x] `setup.ORIGENS` ganha `proposto`, com teste. `extraído` usa a origem `arquivo <caminho>`, que já existe
- [x] `setup/SKILL.md`: etapa de princípios entre o perfil e as guidelines. Primeiro o north star, a partir do objetivo; depois os extraídos, com o arquivo citado; depois os propostos. Cada sugestão mostra a origem, o teste aplicado e por que passou ou caiu para guideline. **Aprovar**, **Editar** e **Rejeitar**, como nas guidelines; o que cai para guideline segue para a etapa seguinte. Sai o caminho "princípio vira `observação` no huddle", e `criar-principio` entra na lista de subcomandos
- [x] `docs/recursos/create-principle.md` (segunda porta, formato compacto, teto), `docs/recursos/setup.md` (critério e etapa) e `README.md` (*Como cada camada nasce*, linha do princípio)
- [x] `scripts/test-python.sh` verde (a suíte inteira); `lint_skill` sem problema na `setup/SKILL.md`
- [x] Remedição no projeto de prova (*Remedição*)

7 de 7 tarefas concluídas · atualizado em 2026-11-20
<!-- backlog:end -->
