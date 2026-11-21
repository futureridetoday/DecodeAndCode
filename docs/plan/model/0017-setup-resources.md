---
# about
name: setup-resources
type: plan
project: DecodeAndCode
description: O setup inventaria skills, agents, commands e MCP do projeto e liga o recurso aos caminhos onde vale por guideline-ponte; o derive cita a ponte em Normas aplicáveis por script; começa medindo se o implement em fork alcança uma skill do projeto
tags: [decode-and-code, setup, recursos, guideline, derive, implement]

# alvo
plan_id: "0017"
plan_size: médio
plan_type: feature
core: model
module: setup-resources
block: ""

# history
author: Claude
created: 2026-11-20
status: done
version: 1.0.0
updated: ""
approved_by: "Bortoli Rafael"
approved_at: "2026-11-20"

# system
scope: project
auto_load: false
dependencies: []
---

# O setup descobre os recursos do projeto e os liga aos caminhos

> **Nasce da divisão do esboço `setup-principles-resources`**, decidida pelo humano em 2026-11-20
> na revisão: a fase A virou [`setup-principles`](0016-setup-principles.md), e este esboço é a fase B.
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

- [x] **Medição de `R-01`**, antes de qualquer código. Num projeto de prova com uma skill própria, a sessão roda o `implement` de uma unidade cuja tarefa pede a skill. Mede: a skill é invocada? pede permissão? Com e sem `Skill` no `allowed-tools`. Mede também uma tool de MCP do projeto no fork, e se uma guideline com `paths:` que casa o arquivo tocado aparece no log de ativação do fork. O resultado vai em `## Medição`, neste plano. Se não alcança, o plano para aqui e volta ao humano
- [x] `descoberta.descobrir`: chave `recursos`, com teste. Traz o nome e a `description` de `.claude/skills/*/SKILL.md`, `.claude/commands/**/*.md` e `.claude/agents/*.md`, e os nomes de servidor de `.mcp.json`, sem trecho e sem as skills do próprio método (`lib.SKILLS`). `formatar` imprime a seção `## Recursos do projeto`
- [x] **Fecha a `L-03` da revisão.** `dc.py guidelines-aplicaveis <unidade>`, com teste: lê os caminhos da tabela *Arquivos* da unidade e imprime, para cada guideline de `.claude/rules/` cujo `paths:` casa algum deles, a linha de *Normas aplicáveis* pronta, no formato que o `lint-unidade` aceita. Casa o **texto** do caminho, não o disco, porque o arquivo da unidade pode ainda não existir. Cobre só o subconjunto que o `criar-guideline` grava (`rules._problema_de_padrao`, `D-02` do `0007`): padrão que começa por diretório ou por `**/`, sem chaves, sem `/` inicial e sem `/**` final — `dir/**/*`, `**/<arquivo>`, `dir/*.ext` —, com `**` valendo zero ou mais diretórios; guideline com padrão fora dele não entra na resposta, e o comando diz qual. O runner é Python ≥ 3.10, sem `PurePath.full_match`. `derive/SKILL.md`, passo 4: roda o comando para cada unidade e cita cada linha devolvida
- [x] `setup/SKILL.md`, etapa de guidelines: recurso ligado a caminho vira guideline-ponte. O corpo começa por um título, para que a citação resolva no `dc.py normas`. Exemplo: `paths: ["src/components/**/*"]`, corpo "Interface nova passa pela skill `ui-builder` do projeto". Agent só entra em ponte para trabalho na conversa principal (`R-02`). Na norma, *Setup*, uma frase
- [x] Só se a medição o exigir: `Skill` no `allowed-tools` de `implement/SKILL.md` — **não exigido**: a medição de 2026-11-20 alcançou a skill sem ele (*Medição*)
- [x] `scripts/test-python.sh` verde (a suíte inteira); `lint_skill` sem problema nas skills tocadas
- [x] Remedição no projeto de prova (*Remedição*)

## Medição

**`R-01`, 2026-11-20.** Claude Code 2.1.327, `claude -p` com o pacote construído por
`empacotar.construir` no scratchpad da sessão que orquestrou e carregado por `--plugin-dir`;
`--permission-mode acceptEdits` e `--allowedTools` com o atalho `dc.py` do `implement`, `Read`,
`Glob`, `Grep`, `Write`, `Edit` e `python3 -m unittest` — **sem `Skill`**. Projeto descartável com:

- a skill `ui-builder` em `.claude/skills/`, com três regras que só ela define: a linha
  `// ui-builder: aprovado`, `<Nome>.displayName = "DS<Nome>"` e cor por `var(--ds-<papel>)`;
- a guideline-ponte `ui-ponte`, gravada por `criar-guideline` com `paths: ["src/components/**/*"]`;
- um plano `grande` aprovado e a unidade `0001-01`, que cita a ponte em *Normas aplicáveis* e passa
  no `lint-unidade`.

Comando: `claude -p "/decode-and-code:implement docs/plan/app/0001-add-card/01-card-component.md"`.

| Pergunta | Resultado |
|---|---|
| O fork recebe a ponte? | Sim, pelo `dc.py normas`: `.claude/rules/ui-ponte.md § Interface` |
| A skill do projeto é invocada? | **Sim, pela ferramenta `Skill`** (`Launching skill: ui-builder`), dentro do subagente, sem `Skill` no `allowed-tools` do `implement` nem no `--allowedTools` |
| Pede permissão? | Não: nenhuma negação para `Skill`. A única negação da sessão foi um `dc.py` montado com variável de shell, refeito literal |
| A entrega segue a skill? | Sim: `Card.tsx` com a linha-marca, `Card.displayName = "DSCard"` e `var(--ds-surface)`; o teste escrito pelo `implement` confere as três; `verificar` deu `verified` |
| Com `Skill` no `allowed-tools` | Não rodado: sem ele a skill já foi alcançada, e a tarefa condicional não é exigida |
| Ponte no log de ativação do fork | **Inconclusivo**: nenhum `decode-and-code-activation-*.log` foi gravado na sessão, e o evento `InstructionsLoaded` não aparece no stream de `-p`. Não afeta o desenho: a ponte chega pelo `dc.py normas`, que é determinístico |
| Tool de MCP do projeto no fork | **Não medido**: pede um servidor MCP no projeto de prova, e nenhuma tarefa deste plano depende disso |

**Conclusão:** o `implement` alcança a skill do projeto. A guideline-ponte se sustenta (`P-01`), e o
plano segue para a tarefa 2.

## Oráculo

| Alvo | Como se sabe que funcionou |
|---|---|
| Medição | `## Medição` registra o resultado de `R-01`, com versão do Claude Code e o comando usado |
| `descobrir` | Teste: projeto com uma skill, um command, um agent e `.mcp.json` lista os quatro com nome e `description`, sem trecho; as skills do método ficam fora |
| `guidelines-aplicaveis` | Teste: unidade com `src/components/Botao.tsx` em *Arquivos*, que ainda não existe no disco, devolve a guideline com `paths: ["src/components/**/*"]` e não devolve a de `paths: ["docs/**/*"]`; as duas guidelines do teste são gravadas pelo `criar_guideline`, não escritas à mão; a linha devolvida passa no `lint-unidade` |
| `derive` | `lint_skill` aprova `derive/SKILL.md`; o passo 4 cita o comando |

## Remedição

Num projeto de prova com uma skill própria ligada a `src/components/**/*`:

1. O setup lista a skill em *Recursos do projeto* e sugere a guideline-ponte; aprovada, ela fica em
   `.claude/rules/`.
2. O `derive` de uma unidade que toca `src/components/` roda `guidelines-aplicaveis` e cita a ponte
   em *Normas aplicáveis*.
3. O `implement` recebe a ponte pelo `dc.py normas` e invoca a skill.

### Resultado — 2026-11-20

`claude -p` (Claude Code 2.1.327) com o pacote reconstruído depois das tarefas 2 a 4, num projeto
descartável com a skill `ui-builder` em `.claude/skills/` e `src/components/Button.tsx`.

| Passo | Resultado |
|---|---|
| 1 — setup | O `descobrir` listou `skill ui-builder` com a `description`, sem trecho. Na etapa de guidelines, o setup propôs a ponte com `# Interface` e `paths: ["src/components/**/*.tsx", "src/components/**/*.ts"]`; aprovada, foi gravada pelo `criar-guideline` em `.claude/rules/interface.md` |
| 2 — derive | Rodou `guidelines-aplicaveis` (encadeado com o `lint-unidade`), que devolveu `| Interface | [interface](../../../../.claude/rules/interface.md), seção *Interface* |`; a unidade derivada cita a ponte, e o `lint-unidade` aprovou |
| 3 — implement | Coberto pela *Medição*: com a ponte entregue pelo `dc.py normas`, o subagente invocou a skill pela ferramenta `Skill` e a entrega seguiu as regras dela. Não rodado de novo sobre a unidade derivada, que já copia as regras da skill no contrato (`L-04`) |

**Achado corrigido:** o setup não sabia que origem dar à ponte — anunciou `existente` e registrou
`proposto`. A `setup/SKILL.md` passou a dizer `arquivo <caminho do recurso>`. Texto de uma linha,
não remedido.

## Independência

**Ordem: depois do `setup-principles`.** Os dois tocam `setup/SKILL.md` e a norma, seção *Setup*; em
paralelo, seria a concorrência que a norma barra. Nada deste plano depende do resultado daquele.

## Lacunas

| # | Lacuna | Detalhe |
|---|---|---|
| L-01 | **O caso de recursos é um só** | Até a remedição, o plano se apoia num relato do humano. Se o projeto de prova não for o design system real, a remedição prova o mecanismo, não o caso |
| L-02 | **Os exemplos de `paths` estão fora do subconjunto que o escritor aceita** | A tarefa 4, o *Oráculo* de `guidelines-aplicaveis` e a *Remedição* usam `src/components/**` e `docs/**`; `rules._problema_de_padrao` recusa padrão terminado em `/**` (a forma é `dir/**/*`, `D-02` do `0007`). O setup não conseguiria gravar a ponte do exemplo, e o teste provaria um padrão que o setup nunca gera. A "semântica de `**` do Claude Code" da tarefa 3 também não diz qual subconjunto o casamento cobre (revisão de 2026-11-20). **Fechada em 2026-11-20**, antes da aprovação: os exemplos passaram a `dir/**/*`, o *Oráculo* grava as guidelines do teste pelo `criar_guideline`, e a tarefa 3 cobre só o subconjunto da `D-02` do `0007` |
| L-04 | **O `derive` copia as regras da skill para a unidade** | Na remedição, o `derive` leu a `SKILL.md` da `ui-builder` e escreveu as três regras dela no contrato da unidade, além de citar a ponte. A unidade passa a ser uma segunda fonte das regras da skill: se a skill mudar, a unidade diverge sem aviso, e o `implement` segue a cópia. A ponte existe para que o `implement` invoque a skill; o `derive/SKILL.md` não diz que a regra do recurso se cita, não se copia. Um caso só (remedição de 2026-11-20) |
| L-03 | **A ponte não sabe se o recurso ainda existe** | A guideline-ponte cita a skill pelo nome. Skill renomeada ou removida deixa a ponte apontando para nada, e nenhum lint olha isso; o `implement` descobre na hora (revisão de 2026-11-20) |

## Fonte

- [`setup-principles.md`](0016-setup-principles.md), de onde este plano foi separado
- [`modelo-dev-units.md`](../system/modelo-dev-units.md), *Setup — o primeiro uso*, *Formato do arquivo de unidade* (*Normas aplicáveis*), *Fronteira skill / script*, *Camada de execução*
- `.claude/skills/setup/SKILL.md`, `.claude/skills/derive/SKILL.md` (passo 4), `.claude/skills/implement/SKILL.md`, `.claude/skills/decode-and-code/scripts/descoberta.py`, `normas.py`, `rules.py`, `lint_unidade.py`

## Backlog

<!-- backlog:start -->
- [x] **Medição de `R-01`**, antes de qualquer código. Num projeto de prova com uma skill própria, a sessão roda o `implement` de uma unidade cuja tarefa pede a skill. Mede: a skill é invocada? pede permissão? Com e sem `Skill` no `allowed-tools`. Mede também uma tool de MCP do projeto no fork, e se uma guideline com `paths:` que casa o arquivo tocado aparece no log de ativação do fork. O resultado vai em `## Medição`, neste plano. Se não alcança, o plano para aqui e volta ao humano
- [x] `descoberta.descobrir`: chave `recursos`, com teste. Traz o nome e a `description` de `.claude/skills/*/SKILL.md`, `.claude/commands/**/*.md` e `.claude/agents/*.md`, e os nomes de servidor de `.mcp.json`, sem trecho e sem as skills do próprio método (`lib.SKILLS`). `formatar` imprime a seção `## Recursos do projeto`
- [x] **Fecha a `L-03` da revisão.** `dc.py guidelines-aplicaveis <unidade>`, com teste: lê os caminhos da tabela *Arquivos* da unidade e imprime, para cada guideline de `.claude/rules/` cujo `paths:` casa algum deles, a linha de *Normas aplicáveis* pronta, no formato que o `lint-unidade` aceita. Casa o **texto** do caminho, não o disco, porque o arquivo da unidade pode ainda não existir. Cobre só o subconjunto que o `criar-guideline` grava (`rules._problema_de_padrao`, `D-02` do `0007`): padrão que começa por diretório ou por `**/`, sem chaves, sem `/` inicial e sem `/**` final — `dir/**/*`, `**/<arquivo>`, `dir/*.ext` —, com `**` valendo zero ou mais diretórios; guideline com padrão fora dele não entra na resposta, e o comando diz qual. O runner é Python ≥ 3.10, sem `PurePath.full_match`. `derive/SKILL.md`, passo 4: roda o comando para cada unidade e cita cada linha devolvida
- [x] `setup/SKILL.md`, etapa de guidelines: recurso ligado a caminho vira guideline-ponte. O corpo começa por um título, para que a citação resolva no `dc.py normas`. Exemplo: `paths: ["src/components/**/*"]`, corpo "Interface nova passa pela skill `ui-builder` do projeto". Agent só entra em ponte para trabalho na conversa principal (`R-02`). Na norma, *Setup*, uma frase
- [x] Só se a medição o exigir: `Skill` no `allowed-tools` de `implement/SKILL.md` — **não exigido**: a medição de 2026-11-20 alcançou a skill sem ele (*Medição*)
- [x] `scripts/test-python.sh` verde (a suíte inteira); `lint_skill` sem problema nas skills tocadas
- [x] Remedição no projeto de prova (*Remedição*)

7 de 7 tarefas concluídas · atualizado em 2026-11-20
<!-- backlog:end -->
