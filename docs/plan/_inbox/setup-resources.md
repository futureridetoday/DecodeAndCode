---
# about
name: setup-resources
type: plan
project: DecodeAndCode
description: O setup inventaria skills, agents, commands e MCP do projeto e liga o recurso aos caminhos onde vale por guideline-ponte; o derive cita a ponte em Normas aplicáveis por script; começa medindo se o implement em fork alcança uma skill do projeto
tags: [decode-and-code, setup, recursos, guideline, derive, implement]

# alvo
plan_id: ""
plan_size: médio
plan_type: feature
core: model
module: setup-resources
block: ""

# history
author: Claude
created: 2026-11-20
status: draft
version: 1.0.0
updated: ""
approved_by: ""
approved_at: ""

# system
scope: project
auto_load: false
dependencies: []
---

# O setup descobre os recursos do projeto e os liga aos caminhos

> **Nasce da divisão do esboço `setup-principles-resources`**, decidida pelo humano em 2026-11-20
> na revisão: a fase A virou [`setup-principles`](../model/0016-setup-principles.md), e este esboço é a fase B.
> Fecha a `L-03` daquela revisão (nenhuma tarefa fazia o `derive` citar a ponte) com a tarefa 3.
>
> **Tipo proposto: `feature`. Porte proposto: `médio`** — há passos, e uma sessão os executa em
> sequência; a medição da tarefa 1 é feita pela própria sessão que orquestra. O humano confirma
> tipo e porte na aprovação.

## Objetivo

**Clarificar.** O setup não sabe que recursos o projeto já tem, e o `implement`, que roda em fork
sem o histórico da conversa, não tem como saber que uma skill do projeto vale para os arquivos que
ele toca. **Métrica:** unidade que toca um caminho ligado a recurso do projeto e o `implement` usa o
recurso. Hoje não há mecanismo. Alvo: o caso do design system (*Remedição*), depois de medido o
risco `R-01`. **Beneficiário:** quem executa unidades num projeto que tem recursos próprios.

**Evitar.**

| Alternativa | Por que não basta |
|---|---|
| Não fazer nada, porque a conversa principal já recebe skills, agents e MCP pela plataforma | Resolve o planejamento, que roda na conversa principal. **Não** liga o recurso a um caminho, nem chega ao `implement`, que roda em fork sem o histórico |
| Bloco `Recursos` na unidade, verificado pelo `lint-unidade` | É formato novo e uma checagem nova. Fica como saída se a ponte falhar na medição (`P-01`) |
| Guideline-ponte | **Escolhida, pendente da medição.** Usa o que existe: `criar-guideline`, ativação por `paths:`, citação em *Normas aplicáveis* e `dc.py normas` |
| O `derive` acha a guideline aplicável por julgamento, lendo `.claude/rules/` | Casar glob com caminho é determinismo, e determinismo fica em script (norma, *Fronteira skill / script*). Por julgamento, a citação some sem ninguém ver |

**Reduzir.** O `descobrir` lista só o nome e a `description` de cada recurso, sem trecho. A ponte é
uma guideline comum, gravada pelo escritor que já existe. Um subcomando novo lista as guidelines que
casam os arquivos de uma unidade; nenhum formato de unidade muda e nenhum gate novo entra.

## Gates

| Gate | Resposta |
|---|---|
| **A — necessidade real** | **Sim, com base estreita, somada a exigência explícita do humano** (2026-11-20; protocolo de exceção, *exigência explícita*). Um caso relatado pelo humano: design system multimarcas com skill própria de interface; o `implement` de uma LP precisa usá-la. Sem incidente registrado, e o mecanismo depende de `R-01`, que a tarefa 1 mede antes de qualquer código |
| **B — mínimo viável** | Cortado e reabrível: **recurso sem caminho listado no `## Perfil`**, porque nenhuma skill lê o `## Perfil` depois do setup e a conversa principal já recebe esses recursos pela plataforma (`P-02`); **bloco `Recursos` na unidade**, só se a ponte reprovar (`P-01`); **trecho de 60 linhas** de cada recurso no `descobrir`; **checagem no `lint-unidade`** de guideline aplicável não citada: mudaria o gate de entrada de toda unidade, inclusive as já verificadas, e a tarefa 3 já põe a citação no caminho do `derive` |

## Decisões

| # | Decisão |
|---|---|
| D-01 | **O setup inventaria skills, agents, commands e MCP do projeto.** Decidida pelo humano em 2026-11-20 |
| D-02 | **O plano anterior foi dividido em dois: princípios primeiro, recursos depois.** Decidida pelo humano em 2026-11-20, na revisão |

### Riscos a medir antes de prometer

| # | Risco | Fonte |
|---|---|---|
| R-01 | O `implement` roda com `context: fork` e `agent: general-purpose`, e o `allowed-tools` dele não lista `Skill`. **Não se sabe se o subagente consegue invocar uma skill do projeto**, com ou sem pedido de permissão | `implement/SKILL.md`, frontmatter |
| R-02 | **Subagente não cria subagente.** Agents do projeto não servem dentro do `implement`; servem ao planejamento e à execução de médio e pequeno, que rodam na conversa principal | Documentação do Claude Code, citada pelo Claude na conversa; não medido aqui |

### Pendentes de decisão

| # | Pergunta | Recomendação do Claude |
|---|---|---|
| P-01 | Guideline-ponte ou bloco `Recursos` na unidade? | **Ponte**, condicionada à tarefa 1. Se o `implement` não alcança a skill, o plano para e volta ao humano antes da tarefa 2 |
| P-02 | Recurso sem caminho listado no `## Perfil` como disponível? | **Cortar** (gate B): não há leitor, e a plataforma já o mostra na conversa principal. Reabre quando alguma skill passar a ler o `## Perfil` |

## Tarefas

- [ ] **Medição de `R-01`**, antes de qualquer código. Num projeto de prova com uma skill própria, a sessão roda o `implement` de uma unidade cuja tarefa pede a skill. Mede: a skill é invocada? pede permissão? Com e sem `Skill` no `allowed-tools`. Mede também uma tool de MCP do projeto no fork, e se uma guideline com `paths:` que casa o arquivo tocado aparece no log de ativação do fork. O resultado vai em `## Medição`, neste plano. Se não alcança, o plano para aqui e volta ao humano
- [ ] `descoberta.descobrir`: chave `recursos`, com teste. Traz o nome e a `description` de `.claude/skills/*/SKILL.md`, `.claude/commands/**/*.md` e `.claude/agents/*.md`, e os nomes de servidor de `.mcp.json`, sem trecho e sem as skills do próprio método (`lib.SKILLS`). `formatar` imprime a seção `## Recursos do projeto`
- [ ] **Fecha a `L-03` da revisão.** `dc.py guidelines-aplicaveis <unidade>`, com teste: lê os caminhos da tabela *Arquivos* da unidade e imprime, para cada guideline de `.claude/rules/` cujo `paths:` casa algum deles, a linha de *Normas aplicáveis* pronta, no formato que o `lint-unidade` aceita. Casa o **texto** do caminho, não o disco, porque o arquivo da unidade pode ainda não existir; a semântica de `**` é a do Claude Code, e o runner é Python ≥ 3.10, sem `PurePath.full_match`. `derive/SKILL.md`, passo 4: roda o comando para cada unidade e cita cada linha devolvida
- [ ] `setup/SKILL.md`, etapa de guidelines: recurso ligado a caminho vira guideline-ponte. O corpo começa por um título, para que a citação resolva no `dc.py normas`. Exemplo: `paths: ["src/components/**"]`, corpo "Interface nova passa pela skill `ui-builder` do projeto". Agent só entra em ponte para trabalho na conversa principal (`R-02`). Na norma, *Setup*, uma frase
- [ ] Só se a medição o exigir: `Skill` no `allowed-tools` de `implement/SKILL.md`
- [ ] `scripts/test-python.sh` verde (a suíte inteira); `lint_skill` sem problema nas skills tocadas
- [ ] Remedição no projeto de prova (*Remedição*)

## Oráculo

| Alvo | Como se sabe que funcionou |
|---|---|
| Medição | `## Medição` registra o resultado de `R-01`, com versão do Claude Code e o comando usado |
| `descobrir` | Teste: projeto com uma skill, um command, um agent e `.mcp.json` lista os quatro com nome e `description`, sem trecho; as skills do método ficam fora |
| `guidelines-aplicaveis` | Teste: unidade com `src/components/Botao.tsx` em *Arquivos*, que ainda não existe no disco, devolve a guideline com `paths: ["src/components/**"]` e não devolve a de `paths: ["docs/**"]`; a linha devolvida passa no `lint-unidade` |
| `derive` | `lint_skill` aprova `derive/SKILL.md`; o passo 4 cita o comando |

## Remedição

Num projeto de prova com uma skill própria ligada a `src/components/**`:

1. O setup lista a skill em *Recursos do projeto* e sugere a guideline-ponte; aprovada, ela fica em
   `.claude/rules/`.
2. O `derive` de uma unidade que toca `src/components/` roda `guidelines-aplicaveis` e cita a ponte
   em *Normas aplicáveis*.
3. O `implement` recebe a ponte pelo `dc.py normas` e invoca a skill.

## Independência

**Ordem: depois do `setup-principles`.** Os dois tocam `setup/SKILL.md` e a norma, seção *Setup*; em
paralelo, seria a concorrência que a norma barra. Nada deste plano depende do resultado daquele.

## Lacunas

| # | Lacuna | Detalhe |
|---|---|---|
| L-01 | **O caso de recursos é um só** | Até a remedição, o plano se apoia num relato do humano. Se o projeto de prova não for o design system real, a remedição prova o mecanismo, não o caso |

## Fonte

- [`setup-principles.md`](../model/0016-setup-principles.md), de onde este plano foi separado
- [`modelo-dev-units.md`](../system/modelo-dev-units.md), *Setup — o primeiro uso*, *Formato do arquivo de unidade* (*Normas aplicáveis*), *Fronteira skill / script*, *Camada de execução*
- `.claude/skills/setup/SKILL.md`, `.claude/skills/derive/SKILL.md` (passo 4), `.claude/skills/implement/SKILL.md`, `.claude/skills/decode-and-code/scripts/descoberta.py`, `normas.py`, `rules.py`, `lint_unidade.py`

## Backlog

<!-- backlog:start -->
<!-- backlog:end -->
