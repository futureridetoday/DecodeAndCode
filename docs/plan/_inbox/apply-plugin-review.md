---
# about
name: apply-plugin-review
type: plan
project: DecodeAndCode
description: Registro da revisão do plugin decode-and-code pela lente de configuração mínima, verificação e primitivo certo — treze achados por impacto, com a solução recomendada para cada um, organizados como plano de trabalho em quatro fases separáveis
tags: [decode-and-code, plugin, revisao, empacotamento, verificacao]

# alvo
plan_id: ""
plan_size: grande
core: model
module: apply-plugin-review
block: ""

# history
author: Claude
created: 2026-10-14
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

# Revisão do plugin decode-and-code — achados e plano de correção

## Como esta revisão foi feita

**Lente.** Práticas que Boris Cherny, criador do Claude Code, documentou publicamente: configuração
mínima, planejar antes de codar, dar ao Claude um jeito de verificar o próprio trabalho, `CLAUDE.md`
curto e vivo, slash commands para tarefa repetida, subagents com uma responsabilidade, hooks para o
que é determinístico, permissões explícitas, e revisar um MCP antes de instalá-lo. Os princípios de
engenharia usados junto com elas — simplicidade e composição, pouca camada entre usuário e modelo,
construir para o modelo de daqui a alguns meses, tipos e contratos explícitos, funcionalidade só
para uso real — são **interpretação** do revisor, não posição atribuída a ele. Toda recomendação
abaixo é do revisor.

**Critérios aplicados a cada componente.**

| # | Critério |
|---|---|
| C1 | Precisa existir, ou o Claude Code já faz isso sozinho? |
| C2 | Está no primitivo certo — command, skill, subagent, hook ou MCP? |
| C3 | O resultado pode ser verificado automaticamente? |
| C4 | O contexto que ele injeta é enxuto? |
| C5 | Continua útil com modelos melhores? |

**Base.** Tudo o que está abaixo foi medido ou lido em 2026-10-14, sobre o commit `55e2aac` (`dev`,
plugin `1.1.2`):

- Documentação oficial do Claude Code, lida no dia: [plugins-reference](https://code.claude.com/docs/en/plugins-reference),
  [skills](https://code.claude.com/docs/en/skills), [sub-agents](https://code.claude.com/docs/en/sub-agents),
  [hooks](https://code.claude.com/docs/en/hooks) e [plugin-marketplaces](https://code.claude.com/docs/en/plugin-marketplaces).
- O pacote construído por `empacotar.construir()` num diretório temporário: 380 KB; `verificar()` e
  `validar()` devolvem lista vazia.
- `claude plugin validate` (v2.1.300) sobre o pacote: *passed with warnings*, com 4 avisos. Sobre o
  marketplace: *passed*.
- Suíte de testes: 482 testes passam em Python **3.13**. O harness oficial não rodou — exige 3.10, e
  o ambiente da revisão não tinha 3.10 (ver `L-04`).
- Latência do hook `PreToolUse`, 20 execuções: mediana de 35 ms, p90 de 45 ms; só o interpretador
  `python3` vazio leva 16 ms.

## Veredito

1. O núcleo é bom: os scripts cuidam do que é determinístico, o modelo cuida do julgamento, e o
   estado da unidade sai do teste.
2. O pacote instalado tem um defeito real — a skill aponta os scripts por um caminho que não existe
   no projeto que instala — e a verificação escreve na árvore real do repositório.
3. Há peças demais em volta do núcleo, e elas vão para todo usuário. Isso pesa contra a configuração
   mínima e contra o princípio de que código é custo.

## Como as correções são executadas

Acordado com o humano em 2026-10-15 e revisto no mesmo dia. Vale para cada `P-XX`, um por vez:

| # | Etapa | Quem |
|---|---|---|
| 1 | Ler o achado e apresentar o problema e a solução recomendada, com detalhe suficiente para delegar sem pergunta: arquivos, mudança esperada, testes e critério de aceite | Orquestrador (Claude) |
| 2 | Aprovar a solução | Humano |
| 3 | Implementar num branch próprio, **sem PR** — agent `general-purpose` em Sonnet ou Haiku, modelo declarado antes de delegar. O agent `developer` não serve: seu gate de entrada exige unidade derivada. O prompt carrega as regras do projeto: não commitar, tocar só os arquivos listados, harness em 3.10 | Agente de desenvolvimento |
| 4 | Revisar a entrega — diff, suíte no harness em 3.10, reprodução do defeito e da correção quando der. Com erro, devolver ao **mesmo** agente a lista exata do que corrigir, até ficar certo | Orquestrador |
| 5 | Commit e push **só do branch**, com o link de comparação contra `dev` para o humano ver o diff | Orquestrador |
| 6 | Validar a solução implementada | Humano |
| 7 | Registrar no achado a linha **Implementado**, com data, commit e a evidência — commit no mesmo branch | Orquestrador |
| 8 | Abrir o PR, já completo: correção e registro juntos | Orquestrador |
| 9 | Merge | Humano |

**Um PR por correção**, aberto só depois de tudo pronto e aprovado: nada chega a `dev` sem a
validação do humano. O registro cita o **commit** da correção, não o PR: quando o registro é
escrito o PR ainda não existe, e o GitHub liga o commit ao PR que o mesclou.

A região `backlog` fica intocada: é projeção do script.

## Achados

Cada achado tem um `P-XX`, o impacto, o critério violado, a evidência, a solução recomendada e como
verificar que a solução funcionou. A coluna *Unidade* da seção `## Escopo` aponta de volta para eles.

### Impacto alto

#### P-01 · A skill instalada não encontra os próprios scripts

| | |
|---|---|
| **Onde** | `.claude/skills/decode-and-code/SKILL.md`, linhas 122, 145, 166 e 189; `lint_skill.py`, linhas 136–144; a norma, linha 259 |
| **Critério** | C3 e contrato explícito |

**Evidência.**

- A skill manda compor `.claude/skills/decode-and-code/scripts/*.py`. No plugin instalado, os
  scripts ficam no diretório do plugin; no projeto que instala, esse caminho não existe.
- O próprio repositório registra o sintoma no cabeçalho de `lib.py`, linha 8: "falha até o script
  ser localizado com `find`".
- A medição que levou ao caminho fixo era correta: `CLAUDE_PLUGIN_ROOT` chega vazio no ambiente do
  Bash, e a documentação confirma. O que ficou de fora é a outra metade da mesma documentação:
  `${CLAUDE_SKILL_DIR}` e `${CLAUDE_PLUGIN_ROOT}` são **substituídos no texto da skill e em
  `allowed-tools`**. Diz a página de skills: "Use `${CLAUDE_SKILL_DIR}` in the skill body so the
  path resolves wherever the skill is installed".
- O `lint_skill.py` só aceita o prefixo `.claude/skills/<nome>/scripts/`, ou seja, **exige** o
  caminho que quebra.
- Nenhum teste segue as instruções da skill a partir do pacote instalado. `test_ciclo_instalado`
  importa os módulos do pacote, mas não executa o que o `SKILL.md` manda fazer.

**Solução recomendada.**

1. Trocar no corpo do `SKILL.md` toda referência a `.claude/skills/decode-and-code/scripts/` por
   `${CLAUDE_SKILL_DIR}/scripts/`.
2. Fazer o `lint_skill.py` aceitar o prefixo `${CLAUDE_SKILL_DIR}/scripts/`, resolvendo contra o
   diretório da própria skill, e recusar o prefixo fixo.
3. No exemplo da norma (linha 259), trocar o caminho por um marcador. A norma é lida como
   arquivo, e `${CLAUDE_SKILL_DIR}` só é substituído no corpo da skill.

> **Corrigido na implementação.** A primeira versão desta recomendação também restringia
> `allowed-tools` a `Bash(python3 ${CLAUDE_SKILL_DIR}/scripts/*)`. Não funciona: a skill compõe os
> scripts por `python3 -c "…"`, e essa regra não casa. Restringir permissão fica com `P-09`.

**Como verificar.**

- Teste de pacote: o `SKILL.md` construído não contém `.claude/skills/` em nenhuma instrução de
  composição.
- Prova manual registrada: `claude --plugin-dir dist/decode-and-code` num projeto vazio, rodando
  `bootstrap` e depois `review` sobre um plano de exemplo, sem nenhuma chamada a `find`.

**Implementado em 2026-10-15** — [PR #6](https://github.com/futureridetoday/DecodeAndCode/pull/6),
commit [`d28fe5d`](https://github.com/futureridetoday/DecodeAndCode/commit/d28fe5d), mesclado em
`dev` como [`dc051f4`](https://github.com/futureridetoday/DecodeAndCode/commit/dc051f4). Validado
pelo humano. Entrou direto por PR, sem plano aprovado nem unidade derivada — exceção ao ciclo por
decisão do humano.

| Evidência | Resultado |
|---|---|
| Sonda com `claude -p --plugin-dir` num projeto vazio, **antes** | A skill citou `.claude/skills/decode-and-code/scripts/nomenclatura.py`; `ls` devolveu `No such file or directory` |
| A mesma sonda, **depois**, no plugin | O caminho citado virou o absoluto da skill dentro do plugin; `ls` encontrou o script |
| A mesma sonda, **depois**, neste repositório (skill de projeto) | O caminho citado virou `/…/DecodeAndCode/.claude/skills/decode-and-code/scripts/`; `ls` encontrou o script |
| `scripts/test-python.sh` em Python 3.10.20 | 490 testes OK |
| Os 3 testes novos contra o código anterior | Os 3 falham — pegam o defeito |
| `empacotar.verificar`, `empacotar.validar`, `claude plugin validate` | Limpos; os 4 avisos restantes são do `P-08` |

**O que ficou de fora.** A sonda carregou a skill e checou o caminho, mas não rodou `bootstrap` e
`review` de ponta a ponta no projeto vazio — isso continua com a unidade `02`
(`installed-skill-proof`), junto da medição do `P-13`.

#### P-02 · Os testes escrevem no repositório real

| | |
|---|---|
| **Onde** | `scripts/tests/test_registry.py`, linhas 157–158 |
| **Critério** | C3 — verificação confiável e sem efeito colateral |

**Evidência.**

- O teste usa o `.claude/rules/scripts.md` real e liga e desliga a guideline.
- O `registry.py` então grava a data do dia em `.claude/rules/registry.json`, também real.
- Aconteceu durante esta revisão: `atualizado_em` passou de `2026-09-14` para `2026-10-14` só por
  rodar a suíte.
- Como o gate de saída do modo `implement` roda a suíte, uma execução verde deixa diff no
  repositório. Isso contradiz "o executor entrega arquivos e relatório, não commita": ele entrega um
  arquivo que não pediu.

**Solução recomendada.** Mover o caso para um diretório temporário com `lib.repo_root()` simulado, o
mesmo padrão que `test_auditoria.py` já usa.

**Como verificar.** `git status --porcelain` vazio antes e depois de rodar a suíte inteira. Esse
teste pode virar um passo do próprio harness: falhar se a suíte deixar diff.

**Implementado em 2026-10-15** — [PR #8](https://github.com/futureridetoday/DecodeAndCode/pull/8),
commit [`e5bfdd2`](https://github.com/futureridetoday/DecodeAndCode/commit/e5bfdd2), mesclado em
`dev` como [`5b52111`](https://github.com/futureridetoday/DecodeAndCode/commit/5b52111). Validado
pelo humano com o merge. Implementado por agente `general-purpose` em Sonnet, revisado pelo
orquestrador sem rodada de correção.

| Evidência | Resultado |
|---|---|
| Suíte numa árvore limpa, **antes** | Deixava `.claude/rules/registry.json` modificado e `.claude/rules-off/` criado vazio — a pasta vazia o `git status` não mostra |
| `test_registry.py`, classe `TestGuidelineReal` | Os bytes reais de `scripts.md` vão para um `tempfile`, com `lib.repo_root` mockado; mesmas asserções, mais duas que provam que `desligar`/`ligar` operam no `tempfile`. Um `alvo.py` vazio mantém o `lint_guideline` significativo, porque o `paths:` real (`**/*.py`) é casado contra o disco |
| `scripts/test-python.sh` | Guarda nova: `git status --porcelain --untracked-files=all` antes e depois da suíte; diferença falha e lista o que mudou |
| `scripts/test-python.sh` em Python 3.10.20, **depois**, duas vezes seguidas | 490 testes OK; árvore intocada; sem `rules-off/` |
| Guarda contra o defeito original — `test_registry.py` antigo com o harness novo | Falha nomeando `M .claude/rules/registry.json` |

**Limite conhecido.** A guarda compara status, não conteúdo: um arquivo já modificado antes da
suíte e alterado de novo durante ela mantém o mesmo status e não dispara.

### Impacto médio

#### P-03 · Primitivos sobrepostos para a mesma tarefa

| | |
|---|---|
| **Onde** | `.claude/commands/implement.md`, `.claude/commands/delegate.md`, `.claude/agents/planner.md`, `.claude/agents/developer.md`, a skill |
| **Critério** | C1, C2 — pouca camada entre usuário e modelo |

**Evidência.**

- Implementar uma unidade tem 4 entradas: a skill (modo `implement`), `/implement`, `/delegate` e o
  agent `developer`. Revisar e derivar têm 2: a skill e o agent `planner`.
- A justificativa está na norma, seção *Modelos*: "A troca não é declarável na skill. Verificado em
  2026-07-19: das skills do projeto que declaram `model:` no frontmatter, todas o deixam vazio".
  Essa evidência veio de olhar skills locais, não da documentação.
- A documentação atual lista `model` e `effort` como campos de skill ("Model to use when this skill
  is active"), e `context: fork` com `agent:` para rodar a skill num subagent.
- A documentação também diz: "Custom commands have been merged into skills", e para plugins novos,
  "Prefer `skills/`".

**Solução recomendada (interpretação do revisor — depende de `D-01`).**

1. Dividir a skill em três: `review`, `derive` e `implement`.
   - `review` e `derive` com `model: opus`.
   - `implement` com `model: sonnet`.
2. O `/delegate` vira uma variante do `implement` com `context: fork` e `agent: developer`, ou some.
3. Remover a pasta `commands/`.
4. Reavaliar se o `planner` ainda tem papel quando `review` e `derive` já declaram o próprio modelo.

Efeitos colaterais que a mesma mudança carrega:

- `handoff.py` hoje nomeia `/implement` e `/delegate` no prompt que gera.
- A norma (seções *Modelos* e *`_handoff.md`*), o README, `docs/recursos/` e `test_agentes.py`
  precisam acompanhar.

**Como verificar.**

- `claude plugin validate --strict` limpo.
- Inventário do pacote com 3 skills, sem `commands/`.
- Numa sessão real, invocar `implement` sobre uma unidade de exemplo roda em Sonnet, conferido no
  transcript.

**Implementado em 2026-10-15**, em duas etapas no mesmo branch:
- commit [`6fa1b2a`](https://github.com/futureridetoday/DecodeAndCode/commit/6fa1b2a) — código e
  pacote;
- commit [`30edd4e`](https://github.com/futureridetoday/DecodeAndCode/commit/30edd4e) — norma,
  registro, README, `CLAUDE.md` e `docs/recursos/`.

`D-01` aprovada pelo humano antes da implementação, com os ajustes abaixo. Validado pelo humano em
2026-10-15, sobre o diff do branch, antes do PR. Cada etapa foi implementada por agente
`general-purpose` em Sonnet e revisada pelo orquestrador; cada uma teve uma rodada de correção (3
itens na A, 2 na B).

| Evidência | Resultado |
|---|---|
| Plugin de prova, Claude Code 2.1.300, `claude -p --plugin-dir`, **antes** de propor | `model: haiku` numa skill sem fork rodou o turno em Haiku. `context: fork` com `agent: general-purpose` e `model: haiku` rodou o subagent em Haiku. `agent: developer` (nome curto, agent do próprio plugin) **não resolveu**: caiu no padrão, sem aviso; `agent: probe:developer` resolveu. Uma pasta em `skills/` sem `SKILL.md` passou no `claude plugin validate` |
| Conteúdo dos modos | Os trechos `review`, `derive`, `implement` e *Começando um projeto do zero* foram conferidos contra o `SKILL.md` antigo: idênticos, salvo o caminho dos scripts |
| `scripts/test-python.sh` em 3.10, duas vezes por etapa | 502 testes OK (eram 490); `git status` igual antes e depois |
| Pacote construído: `verificar` e `validar` | Listas vazias. Inventário: `skills/{review-plan,derive,implement}/SKILL.md`, `skills/decode-and-code/` sem `SKILL.md`, sem `commands/`, `agents/` só com `ai-builder.md` |
| Sessão real: `/decode-and-code:implement 0001-01` numa sessão **Opus** | O subagent rodou só em Sonnet (`modelUsage`); o gate de entrada recusou a unidade inexistente sem escrever nada |
| Sessão real: `/decode-and-code:review-plan` numa sessão **Sonnet** | O turno rodou em Opus |
| Sessão real: o modelo chama `decode-and-code:derive` pelo Skill tool | Recusado: "cannot be used with Skill tool due to disable-model-invocation" |
| `ai-builder` no plugin, linha de base e branch | O debug log da linha de base mostra `Preloaded skill 'decode-and-code'`; com `skills: [review-plan]`, o agent recebe o caminho absoluto dos scripts no plugin |
| Referências e links | Nenhuma menção a `planner`, `developer`, `/delegate` ou `commands/` fora de planos históricos; 40 links relativos de README, `CLAUDE.md` e `docs/recursos/` resolvem |

**Diferenças em relação à solução recomendada.**
- **`implement` com `agent: general-purpose`, não `developer`.** Com nome curto, o agent do plugin
  não resolve (medido). O `model: sonnet` da skill vale para o subagent, e o agent `developer` saiu.
- **Scripts numa pasta compartilhada.** `decode-and-code/` ficou sem `SKILL.md`, com `scripts/`,
  `config.json` e `reference/`. As três skills a citam por `${CLAUDE_SKILL_DIR}/../decode-and-code/`,
  porque `${CLAUDE_PLUGIN_ROOT}` não é substituído numa skill de projeto. `lib.SKILLS` é a fonte única
  dos três nomes.
- **`review-plan`, não `review`.** `/review` é alias do `/code-review` embutido. A colisão foi deduzida
  da documentação, não medida.
- **O `planner` saiu na mesma mudança** (unidade `15`). O modelo de `review` e `derive` já está
  declarado na skill. Que o isolamento de contexto não faça falta é interpretação do revisor: os
  achados desses modos são conversados com o humano.
- **O `ai-builder` manteve `skills:`**, agora `[review-plan]`, contra a recomendação do `P-06` (ver
  a atualização lá).
- **O `effort` ficou vazio**, porque não há evidência para escolher um nível.

**O que ficou de fora.**
- O conteúdo não foi enxugado (`P-07`) e o frontmatter amflow continua (`P-10`).
- `.claude/plugin.json` segue em `1.1.2`, mas a invocação mudou de nome (`/decode-and-code:decode-and-code
  review` → `/decode-and-code:review-plan`). Subir a versão é decisão de release.
- Num projeto sem estrutura, o `review-plan` não rodou o bootstrap, e os scripts não acharam a raiz
  do repositório. O comportamento é anterior a esta mudança e fica para a unidade `02`.
- `docs/plan/_inbox/huddle-command.md` cita `.claude/commands/implement.md` como exemplo de formato.
  É plano pendente, por isso não foi editado.
- Nenhum teste lê README, `CLAUDE.md` ou `docs/recursos/`; o drift ali só é pego por conferência
  manual.
- O frontmatter da norma ainda descreve "a skill dev-units", e `version`/`updated` não acompanharam.

#### P-04 · O `/delegate` rebaixa o modelo da sessão que orquestra

| | |
|---|---|
| **Onde** | `.claude/commands/delegate.md`, linha 6 (`model: sonnet`) |
| **Critério** | C2 |

**Evidência.**

- O `model:` de um command vale para o turno em que ele roda.
- O corpo do `/delegate` termina com "revise a entrega … antes de registrar ou versionar". Essa
  revisão acontece nesse mesmo turno, portanto em Sonnet.
- O agent `developer` já declara `model: sonnet` por conta própria. A linha do command só muda o
  modelo de quem revisa.

**Solução recomendada.** Remover `model:` do `/delegate`. Se `D-01` aprovar a nova topologia, o
achado se resolve com ela.

**Como verificar.** Teste de frontmatter: `delegate.md` não declara `model:`.

**Resolvido pelo `P-03` em 2026-10-15.** O `/delegate` saiu, e o `implement` roda em fork com
`model: sonnet`. Medido: numa sessão Opus, só o subagent rodou em Sonnet. Ver o registro do `P-03`.

#### P-05 · Ferramentas de diagnóstico e de desenvolvimento vão para todo usuário

| | |
|---|---|
| **Onde** | `empacotar._copiar_skill`, `empacotar._escrever_hooks_json`, `.claude/hooks/pre_tool_use.py` |
| **Critério** | C1, C5 — configuração mínima; código é custo |

**Evidência.**

- **Scripts que só este repositório usa.** `empacotar.py` (376 linhas), `reconciliar.py`,
  `lint_skill.py` e `lint_agente.py` não são importados por nenhum script de runtime nem por nenhum
  hook — só pelos testes.
- **Instância do AmFlow no pacote.** `reconciliar.py` compara contra `AmFlow:.claude/skills/dev-units`.
  Isso fere a invariante "nada específico de projeto viaja no plugin". O `verificar()` não pega,
  porque procura só o nome deste repositório (`_marcadores_instancia`, linha 212).
- **Hooks de anúncio com canal fraco**, segundo a página de hooks:
  - `InstructionsLoaded` — "Exit code is ignored", sem controle de decisão. Só grava um log em
    `/tmp`.
  - `PostCompact` — "Shows stderr to user only".
  - `SubagentStart` — "the notice appears in the subagent's own transcript, not in the parent
    conversation".
  - Nenhum dos três chega ao modelo. Servem para observar o mecanismo, e a norma, seção *Validar a
    ativação*, oferece o controle de três estados também a quem instala — mas não há registro de
    projeto consumidor que o tenha usado.
- **`PreToolUse` com matcher `*`.** Roda `python3` a cada chamada de ferramenta: 35 ms de mediana.
  Num projeto sem `.claude/guardrails.json`, escreve `guardrail: falha aberta, liberando —
  FileNotFoundError` a cada chamada. Reproduzido com um projeto vazio.

**Solução recomendada.**

1. Excluir `empacotar.py`, `reconciliar.py`, `lint_skill.py` e `lint_agente.py` em
   `_copiar_skill`, no mesmo `ignore_patterns` que já exclui `tests`.
2. Tirar os três hooks de anúncio do `hooks.json` do pacote: `_escrever_hooks_json` passa a copiar só
   `PreToolUse`. Eles continuam no `settings.json` deste repositório. Se surgir evidência de uso do
   controle de três estados num projeto consumidor, manter só o `InstructionsLoaded` (`D-02`).
3. No `pre_tool_use.py`, sair com código 0 e sem escrever nada quando o `guardrails.json` não
   existir. Arquivo existente e malformado continua avisando.

**Como verificar.**

- `test_empacotamento`: o pacote não contém os quatro scripts e o `hooks.json` só tem `PreToolUse`.
- `test_guardrail`: projeto sem `guardrails.json` gera stdout e stderr vazios.

**Implementado em 2026-10-15**, no commit
[`597af95`](https://github.com/futureridetoday/DecodeAndCode/commit/597af95), com `D-02` = B.
Validado pelo humano em 2026-10-15, sobre o diff e o CI verde no branch, antes do PR. Implementado
por agente `general-purpose` em Sonnet, revisado pelo orquestrador, sem rodada de correção.

**O que mudou.**
- O pacote deixa de levar `empacotar.py`, `reconciliar.py`, `lint_skill.py` e `lint_agente.py`.
  Com isso sai também a menção ao AmFlow.
- O `hooks.json` do pacote fica só com `PreToolUse` e `InstructionsLoaded`, e `hooks/` só com os dois
  scripts. A lista é uma só, `_EVENTOS_DO_PACOTE`, e os scripts copiados são derivados dos comandos.
  `PostCompact` e `SubagentStart` continuam só neste repositório.
- Sem `guardrails.json`, o `pre_tool_use.py` sai com código 0 e não escreve nada. Com o arquivo
  malformado, continua avisando.

| Evidência | Resultado |
|---|---|
| Hook num projeto vazio, **antes** | stderr `guardrail: falha aberta, liberando — FileNotFoundError` a cada chamada |
| O mesmo, **depois** (fonte e pacote) | Código 0, stdout e stderr vazios. Com JSON malformado, o aviso continua |
| Sessão real com o pacote, projeto vazio | `PreToolUse` terminou com status 0, sem "falha aberta" no log |
| Imports | Um subprocesso isolado importa todo módulo e todo hook do pacote sem os quatro scripts |
| Suíte em 3.10 | 613 testes OK (eram 602) |
| Pacote | `verificar` e `validar --strict` vazios |
| [CI no branch](https://github.com/futureridetoday/DecodeAndCode/actions/runs/38817977191) | Verde |

**O que ficou de fora.**
- No pacote, o `instructions_loaded.py` ainda grava em `/tmp` um estado que só o `post_compact.py`
  lia. Não é erro: a escrita apenas fica sem leitor.
- O `P-12` (sinal falso do `post_compact`) deixa de afetar quem instala, mas continua valendo neste
  repositório.

#### P-06 · O `ai-builder` é grande, amplo e repete o que o Claude Code já faz

| | |
|---|---|
| **Onde** | `.claude/agents/ai-builder.md` |
| **Critério** | C1, C4, C5 |

**Evidência.**

- **Tamanho.** 14 KB no total. A descrição tem 2,6 mil caracteres e é carregada em toda sessão — a
  página de sub-agents: "Those descriptions take up context, so keep them short".
- **Escopo.** Inclui problema de produto (o exemplo do checkout), território do modo plan e do
  próprio `principles.md`, que já carrega sempre.
- **Pré-carga sem uso.** Declara `skills: [decode-and-code]`, que, segundo a documentação, injeta o
  conteúdo inteiro da skill no início (~3,5 mil tokens). O agent não executa nenhum dos três modos
  dela.
- **Caminho fixo.** Escreve em `docs/plan/_inbox/` direto no texto, ignorando o `plan_root` do
  `config.json`.
- **Regra que depende de memória.** O `H-11` do huddle mediu: a linha "use `Read`, não `cat`"
  reduziu o desvio de 13/13 para 2/8, sem eliminar.
- **Persona.** Abre com uma persona que cita o nome de uma pessoa real. Na leitura do revisor, isso
  ajuda pouco com modelos atuais e tende a virar peso morto.

**Solução recomendada.**

1. Reduzir o agent ao essencial: a escada de menor intervenção mais os gates A e B, em menos de um
   quarto do tamanho atual.
2. Descrição com menos de 600 caracteres e um exemplo só.
3. Tirar `skills:` e a persona.
4. Ler o `_inbox` a partir do `plan_root`.
5. Avaliar, em `D-03`, se uma skill de intake não basta no lugar de um agent.
6. Para o desvio do `H-11`: aceitar o resíduo, ou tirar o `Bash` das `tools` e expor os três scripts
   por outra via. Não acrescentar mais prosa.

**Como verificar.**

- `lint_agente` continua aprovando.
- Teste de tamanho: descrição ≤ 600 caracteres e arquivo ≤ 4 KB.
- Uma execução real com o exemplo de *exportação de relatórios*, conferindo que o esboço passa no
  `lint_plano`.

**Atualização de 2026-10-15, medida no `P-03`.** A "pré-carga sem uso" estava errada. No plugin, o
`skills:` é o que entrega ao `ai-builder` o caminho absoluto dos scripts que o passo 8 usa
(`numeracao`, `nomenclatura`, `lint_plano`); fora do checkout, ele não tem outro jeito de achá-los.
Hoje o agent declara `skills: [review-plan]`. O item 3 da solução vale só para a persona, e só tira o
`skills:` se outra via der o caminho dos scripts.

**Implementado em 2026-10-16**, no commit
[`dde5960`](https://github.com/futureridetoday/DecodeAndCode/commit/dde5960), com `D-03` = B.
Validado pelo humano sobre o diff e o CI verde no branch, antes do PR. Implementado por um agente
`general-purpose` em Sonnet e revisado pelo orquestrador, sem rodada de correção.

**O que mudou.**
- O agent `ai-builder`, de 14 KB, virou a skill `intake`, de 4,0 KB, com descrição de 520
  caracteres. A skill roda em fork, com Opus. O `allowed-tools` dela libera só o atalho `dc.py` e,
  no `WebFetch`, só o domínio `code.claude.com`. Saíram a persona e o `skills:`.
- O `dc.py` ganhou o subcomando `lint-plano`. O `proximo-plano` não entrou: pela norma, o esboço no
  `_inbox` não leva número, e o `ai-builder` contradizia isso ao numerar.
- `lib.MODOS` lista os três modos citados pelo handoff. `lib.SKILLS` é `MODOS + intake` e define o
  que vai no pacote.
- Saíram o agent, `lint_agente.py`, `test_agentes.py` e a seção *Agente* da norma. O pacote não leva
  mais `agents/`, e o método fica com quatro skills e nenhum agent.

| Evidência | Resultado |
|---|---|
| Sessão real num clone deste repositório, com um pedido concreto (CI sem `timeout-minutes`) | Gravou `_inbox/ci-job-timeout.md`, que passa no `lint-plano`. `validar-nome` e `lint-plano` rodaram pelo `dc.py` sem recusa. As 6 recusas foram tentativas do modelo de medir por fora (`gh run list` e a suíte com `time`); como estavam fora do `allowed-tools`, viraram pedido de aprovação, que é o comportamento certo |
| Sessão real num projeto vazio, com um pedido vago | Parou e listou o que faltava, sem gravar nada |
| Suíte em 3.10 | 604 OK: os 613 de antes, menos os 18 do `test_agentes` e mais 9 novos |
| Pacote | Quatro skills e nenhum `agents/`; `verificar` e `validar --strict` vazios |
| [CI no branch](https://github.com/futureridetoday/DecodeAndCode/actions/runs/38826418265) | Verde |

**O que ficou de fora.**
- O `intake` cita os gates de `.claude/rules/principles.md`, e esse arquivo não viaja no pacote. Ver
  `L-07`.
- Na prova, a resposta final do `intake` saiu em inglês.

#### P-07 · O contexto injetado é pesado e carrega histórico

| | |
|---|---|
| **Onde** | `SKILL.md` (13 KB), `reference/modelo-dev-units.md` no pacote (65 KB, cerca de 18 mil tokens), `skills:` em `planner` e `developer` |
| **Critério** | C4, C5 |

**Evidência.**

- Boa parte do `SKILL.md` é justificativa histórica: "decisão 18", "decisão 26", "unidade
  0001-14", "`L-32`".
- Para quem instala, essas referências apontam para planos que não viajam no pacote, ou seja, estão
  quebradas.
- Cada modo remete a seções da norma, que o modelo tende a abrir inteira.
- Os dois agents pré-carregam a skill inteira.

**Solução recomendada.**

1. O `SKILL.md` fica só com o procedimento — o quê e como, em passos. O porquê fica na norma.
2. Remover do pacote toda referência a `L-XX`, unidade ou decisão numerada que não resolva dentro
   do próprio pacote.
3. Apontar seções específicas da norma, ou dividir a norma do pacote por modo.

Se `D-01` aprovar a divisão em três skills, este achado se resolve junto: cada skill carrega só o
próprio modo.

**Como verificar.**

- Teste de pacote: nenhum `L-[0-9]` nem `unidade 0` dentro de `skills/`, `agents/` ou `commands/`.
- Teste de tamanho: `SKILL.md` ≤ 6 KB.

#### P-08 · A verificação do repositório tem lacunas

| | |
|---|---|
| **Onde** | `scripts/test-python.sh`, `empacotar.validar()`, `empacotar._escrever_hooks_json`; o repositório não tem CI |
| **Critério** | C3 |

**Evidência.**

- O harness exige Python **exatamente** 3.10 e recusa rodar em 3.11 ou mais. O gate oficial fica
  indisponível em qualquer ambiente sem 3.10 — incluindo o desta revisão.
- Não há workflow de CI. A verificação depende de alguém rodar o harness à mão.
- `validar()` só olha o código de saída. *Validation passed with warnings* sai com 0, e os 4 avisos
  de hoje passam calados.
- Os avisos: `${CLAUDE_PLUGIN_ROOT}` sem aspas nos quatro comandos do `hooks.json` — "If the expanded
  path contains a space the command can split into several words and fail".

**Solução recomendada.**

1. Workflow de CI (GitHub Actions) com Python 3.10 fixo, rodando `scripts/test-python.sh` e o build
   com validação.
2. Localmente, o harness aceita ≥ 3.10 com um aviso de que a prova de compatibilidade é a do CI.
   Isso muda a guideline `scripts.md` e por isso está em `D-04`.
3. `validar()` passa a rodar `claude plugin validate --strict`.
4. `_escrever_hooks_json` escreve `python3 "${CLAUDE_PLUGIN_ROOT}/hooks/<script>.py"`, com aspas.

**Como verificar.**

- `claude plugin validate --strict` sobre o pacote: *Validation passed*, sem avisos.
- O CI roda em todo PR para `dev`.

**Implementado em 2026-10-15**, em dois commits:
- [`8543bd7`](https://github.com/futureridetoday/DecodeAndCode/commit/8543bd7): a correção;
- [`b91a403`](https://github.com/futureridetoday/DecodeAndCode/commit/b91a403): o gatilho do CI
  em `claude/**`.

`D-04` foi aprovada pelo humano antes da implementação. A solução foi validada pelo humano em
2026-10-15, sobre o diff e o CI verde no branch, antes do PR. A implementação foi de um agente
`general-purpose` em Sonnet, revisada pelo orquestrador, com duas rodadas de ajuste: a linha do
README e o gatilho do CI.

| Evidência | Resultado |
|---|---|
| `claude plugin validate --strict` sobre o pacote, **antes** | 4 avisos de `${CLAUDE_PLUGIN_ROOT}` sem aspas, um por hook, e exit 1. Sem `--strict`, exit 0: o `validar()` deixava passar |
| Caracterização do `--strict` contra o binário real (2.1.300) | Aviso vira exit 1. A mensagem sai em stdout e o stderr fica vazio. Pacote limpo dá exit 0 com e sem a flag. O manifesto sem `description` ou sem `author` também reprova. Roda sem credencial (`env -i` com `HOME` vazio) |
| O mesmo validate, **depois** | *Validation passed*, exit 0. `verificar` e `validar` devolvem `[]` |
| Teste novo que executa o `claude` real | O pacote sem aspas reprova e o com aspas aprova. Sem o `--strict` em `validar()`, falha com `0 != 1 : []` |
| Teste novo sobre o `hooks.json` gerado | Todo `${CLAUDE_PLUGIN_ROOT}` entre aspas. Com as aspas tiradas do `settings.json`, os 4 subtestes falham |
| Hook com aspas numa sessão real com `--plugin-dir` | `PreToolUse` executou `python3 "<plugin>/hooks/pre_tool_use.py"` e terminou com status 0, em 48 ms |
| `scripts/test-python.sh` em 3.10, duas vezes | 504 testes OK (eram 502). `git status` igual antes e depois |
| Harness sem 3.10 (`python3` = 3.13) | Roda, com aviso em stderr de que a prova de compatibilidade é a do CI. Com `CI=true`, o teste de versão exata falha com mensagem clara |
| Primeiro CI do repositório, [run 38793471971](https://github.com/futureridetoday/DecodeAndCode/actions/runs/38793471971), push no branch | Verde. Python 3.10.22, `claude` 2.1.300, 504 testes, nenhum pulado. O teste do `claude` real rodou |

**Diferenças em relação à solução recomendada.**
- **As aspas foram postas no `.claude/settings.json`, e não no `_escrever_hooks_json`.** A troca de
  âncora do build carrega as aspas para o pacote. Fica uma fonte só, e o hook deste repositório ganha
  a mesma proteção.
- **O CI também roda no push dos branches `claude/**`.** O `workflow_dispatch` devolve 404 enquanto
  o workflow não está no branch default, e sem o push não havia como provar uma correção no CI antes
  do PR. O custo é que, com PR aberto, cada push roda duas vezes.
- **O CI instala o `claude` 2.1.300.** Sem ele, os testes pulam a validação real, e o CI passaria
  verde sem rodá-la.
- **Com `CI` definida, o teste de versão do harness exige 3.10 exato.** Localmente aceita qualquer
  versão a partir de 3.10.

**O que ficou de fora.**
- As actions `checkout@v4`, `setup-python@v5` e `setup-node@v4` foram feitas para Node 20, que está
  obsoleto. O runner já as força para Node 24, e funcionam. Subir de versão ficou para depois.
- A versão do `claude` está fixa no workflow. Subi-la é uma decisão consciente, porque uma versão
  nova pode trazer avisos novos ao `--strict`.
- Não há `actionlint` no ambiente. O YAML foi validado por parsers, e a prova é a execução verde.

#### P-09 · A permissão `Bash(python3*)` libera qualquer comando

| | |
|---|---|
| **Onde** | `.claude/settings.json` — vale só para este repositório, não viaja |
| **Critério** | Permissões explícitas em vez de pular todas as aprovações |

**Evidência.** `Bash(python3*)` permite `python3 -c` com qualquer conteúdo sem aprovação. Na prática,
é uma permissão de shell irrestrita.

**Solução recomendada.** Trocar `Bash(python3*)` por `Bash(python3 .claude/skills/decode-and-code/scripts/*)`
e manter `Bash(./scripts/test-python.sh*)`. Liberar `python3 -c` só se houver uso recorrente
comprovado. Rodar `/fewer-permission-prompts` depois de algumas sessões para ajustar pelo uso real.

**Como verificar.** Uma sessão de `review` e uma de `implement` rodam sem prompt para os scripts da
skill.

**Implementado em 2026-10-15**, no commit
[`cf3a15c`](https://github.com/futureridetoday/DecodeAndCode/commit/cf3a15c). Validado pelo humano
em 2026-10-15, sobre o diff e a prova em sessão real, antes do PR. A edição foi feita por um agente
`general-purpose` em Haiku e revisada pelo orquestrador, sem rodada de correção.

**A recomendação acima não servia, por dois motivos medidos na documentação de permissões e de
skills:**
- As skills compõem os scripts por `python3 -c "import sys; sys.path.insert(...); …"`, e uma regra
  por caminho de script nunca casa com essa forma.
- Dentro de uma skill, o `allowed-tools: … Bash …` já pré-aprova o Bash no turno dela. O
  `Bash(python3*)` do `settings.json` só valia fora das skills, e ali era liberação ampla.

**O que mudou no `.claude/settings.json`, só no `permissions.allow`:**
- Sai `Bash(python3*)`.
- Sai `Bash(sed -n*)`, que casa `sed -n -i` e `sed -n 'e …'`.
- Saem as regras que só repetiam o conjunto só-leitura embutido do Claude Code: `git status`,
  `git log*`, `git diff*`, `find*`, `grep*`, `ls*`, `cat*`, `wc*` e `pwd`. Elas o ampliavam, porque
  `git log`/`git diff` com `--output` gravam arquivo.
- Entra `Bash(bash scripts/test-python.sh *)`, que é a forma do README e do CI.

| Evidência (sessões `claude -p` no modo padrão, num clone, com o arquivo carregado por `--settings`, já que o `-p` ignora as regras `allow` de projeto não confiável) | Resultado |
|---|---|
| `python3 -c 'print(1)'` fora de skill, regras **antigas** | Rodou sem pedir |
| O mesmo, regras **novas** | Recusado: "This command requires approval" |
| `/review-plan` sobre um plano do `_inbox` | Opus, 12 comandos Bash (inclusive a composição `python3` com `nomenclatura`), nenhuma recusa |
| `/implement 9999-99` | Subagent Sonnet; o `python3 -c` do gate rodou e recusou a unidade inexistente; nenhuma recusa |
| `bash scripts/test-python.sh` | Rodou: 504 testes |
| `sed -n`, `grep`, `ls`, `cat`, `find` nessas sessões | Sem recusa: a lista embutida cobre a forma só-leitura |

**O que ficou de fora.** O `allowed-tools` das skills é o achado `P-14`, logo abaixo. `Read`, `Edit`
e `Write` continuam liberados sem restrição de caminho neste repositório. Não fazem parte deste
achado.

#### P-14 · O `allowed-tools` das skills libera qualquer comando de shell

*Achado acrescentado em 2026-10-15, durante o `P-09`. A revisão original não o pegou.*

| | |
|---|---|
| **Onde** | `.claude/skills/{review-plan,derive,implement}/SKILL.md` — `allowed-tools: "Read Write Edit Bash Glob Grep"`; viaja no pacote |
| **Critério** | Permissões explícitas; revisar o que se instala |

**Evidência.**

- Pela documentação de skills, `allowed-tools` "grants permission for the listed tools during the
  turn that invokes the skill". `Bash` sem especificador libera qualquer comando de shell nesse
  turno.
- A mesma página alerta: "A skill can grant itself broad tool access, so review the
  `allowed-tools` of skills checked into a repository before you run Claude Code there".
- Medido no `P-09`: dentro de `/review-plan` e `/implement`, todo comando Bash rodou sem aprovação.
  Ao contrário do `P-09`, isto vale para todo projeto que instala o plugin.

**Solução recomendada (interpretação do revisor — depende de `D-05`).** Nenhuma correção é barata:

| Opção | Efeito |
|---|---|
| A. `Bash(python3 -c *)` | Só troca o nome: continua liberando código arbitrário |
| B. Tirar o `Bash` | Cada chamada de script pede aprovação, inclusive dentro do `implement` em fork |
| C. **Recomendada.** Um ponto de entrada único, `scripts/dc.py <operação> <args>`, liberado por `Bash(python3 "${CLAUDE_SKILL_DIR}/../decode-and-code/scripts/dc.py" *)` | É o padrão que a documentação mostra. Muda como as skills compõem os scripts. Argumentos longos, como a fila do `handoff`, precisam de arquivo ou stdin |

**Como verificar.** Numa sessão real, dentro de uma skill, um comando fora do ponto de entrada pede
aprovação, e as operações das três skills rodam sem pedir.

**Implementado em 2026-10-15**, no commit
[`0a474ee`](https://github.com/futureridetoday/DecodeAndCode/commit/0a474ee), com a opção C (`D-05`).
Validado pelo humano em 2026-10-15, sobre o diff e o CI verde no branch, antes do PR. Implementado
por agente `general-purpose` em Sonnet, revisado pelo orquestrador, com duas rodadas de correção.

**O que mudou.**
- `scripts/dc.py` é o ponto de entrada único, um dispatcher fino com 9 subcomandos. O código de
  saída é 0 em sucesso, 1 em reprovação e 2 em erro de uso.
- Cada skill ganha um atalho `dc.py` na própria pasta, que repassa para o compartilhado.
- O `allowed-tools` de cada skill passa a ser `Bash(python3 "${CLAUDE_SKILL_DIR}/dc.py" *)`, mais a
  mesma regra sem aspas.
- A varredura de concorrência vira código, em `scaffold.concorrentes`. `verificacao.verificar_com_saida`
  expõe a saída do teste, que o `dc.py verificar` imprime quando a unidade não fica `verified`.
- O `lint_skill` recusa `Bash` sem especificador e `Bash(*)`.

| Evidência | Resultado |
|---|---|
| Plugin de prova, modo de permissão padrão | A regra estreita libera o `dc.py`, inclusive com heredoc, e recusa `python3 -c` |
| Sessão real, primeira versão (`${CLAUDE_SKILL_DIR}/../decode-and-code/scripts/dc.py`) | **11 recusas** de chamadas legítimas: o modelo normaliza o `..`, tira as aspas ou põe o caminho numa variável, e a regra deixa de casar o texto |
| Sessão real, com o atalho por skill | Todas as chamadas no formato da skill passaram. Sobraram 4 recusas: 3 leituras de arquivos internos do plugin por `cat`/`ls`/`grep` (as ferramentas `Read` e `Grep` continuam liberadas) e 1 chamada ao `dc.py` por caminho relativo. Em todos os casos, o que não casa pede aprovação em vez de rodar |
| Suíte em 3.10 | 602 testes OK (eram 504), com `git status` estável |
| Pacote | `verificar` e `validar` vazios; `--strict` limpo |
| [CI no branch](https://github.com/futureridetoday/DecodeAndCode/actions/runs/38809013470) | Verde |

**O que ficou de fora.**
- O `ai-builder` continua compondo `numeracao`, `nomenclatura` e `lint_plano` à moda antiga. Ele é
  agent, e o `allowed-tools` não se aplica a agent. Fica com o `P-06`.
- O `dc.py` não tem subcomando para o próximo número de plano nem para o `lint_plano`.
- Com a pasta compartilhada ausente, o atalho sai com traceback e código 1, e não com 2. Isso é
  instalação quebrada e não foi tratado.

### Impacto baixo

#### P-10 · Frontmatter fora da especificação no que viaja

| | |
|---|---|
| **Onde** | `SKILL.md`, `commands/*.md` — o bloco "amflow — rastreabilidade", mais `model: ""`, `effort: ""` e `context: ""` |
| **Critério** | C4, contrato explícito |

**Evidência.**

- O Claude Code ignora campos que não conhece: "Claude Code ignores a field it doesn't recognize
  without reporting an error".
- A mesma página avisa que fora do Claude Code a regra é outra: "packaging or upload fails with a
  hard error instead of ignoring the field". Vale para o claude.ai e para a Skills API.
- Não foi verificado se isso atinge o upload de plugin que o README oferece (`L-02`).
- Os campos vazios têm comportamento não documentado.

**Solução recomendada.**

- Manter o bloco na fonte, porque é o padrão de frontmatter do projeto.
- Removê-lo **no build**, como `_declarar_o_plugin` já faz com `project:` — o derivado se corrige no
  build, a fonte permanece honesta.
- Remover da fonte os três campos vazios.

**Como verificar.** Teste de pacote: o frontmatter do `SKILL.md` construído só contém campos da
tabela oficial.

**Implementado em 2026-10-16**, no commit
[`2ff6ea9`](https://github.com/futureridetoday/DecodeAndCode/commit/2ff6ea9). Aprovado pelo humano
sobre a validação local, antes do PR. Implementado por um agente `general-purpose` em Sonnet e
revisado pelo orquestrador, que cortou três testes e um assert além do pedido.

**O que mudou.**
- `empacotar._so_campos_oficiais` tira do `SKILL.md` empacotado todo campo de topo fora de
  `_CAMPOS_OFICIAIS`, com as linhas de continuação e o comentário que o antecede. A lista é a da
  documentação de skills, conferida em 2026-10-16: 20 campos, numa única constante.
- `_declarar_o_plugin` passa a valer só para a norma. O `SKILL.md` perde o bloco inteiro,
  `project:` incluído.
- A fonte perdeu `effort: ""` nas quatro skills e `context: ""` em `review-plan` e `derive`. O
  `lint_skill` deixou de exigir os dois.

| Evidência | Resultado |
|---|---|
| Frontmatter do `review-plan` empacotado | `name description disable-model-invocation user-invocable allowed-tools argument-hint arguments model shell` |
| Teste de pacote novo | Nas quatro skills, as chaves empacotadas são as da fonte que a lista oficial reconhece, e o corpo sai idêntico |
| Suíte | 607 OK (eram 604) |
| Pacote | `verificar` e `validar --strict` vazios |
| [CI no branch](https://github.com/futureridetoday/DecodeAndCode/actions/runs/38838477036) | Verde |

**O que ficou de fora.** O upload de plugin pelo claude.ai continua sem medição (`L-02`), mas deixa
de importar: o pacote só leva campos oficiais.

#### P-11 · Testes que conferem texto do `SKILL.md`

| | |
|---|---|
| **Onde** | `test_modo_review.py`, `test_modo_derive.py`, `test_modo_implement.py` |
| **Critério** | C3 |

**Evidência.** Os testes verificam que certas palavras aparecem numa seção do markdown — por exemplo,
que `nomenclatura.py` é citado. Isso protege texto, não comportamento, e quebra a cada reescrita do
`SKILL.md`, inclusive a que `P-07` recomenda.

**Solução recomendada.** Substituir pelo teste de `P-01` — os scripts citados existem, sob
`${CLAUDE_SKILL_DIR}/scripts/` — e pelo `lint_skill`. Apagar o resto.

**Como verificar.** A suíte continua verde depois da reescrita de `P-07`, sem tocar teste.

**Implementado em 2026-10-16**, no commit
[`5e4d441`](https://github.com/futureridetoday/DecodeAndCode/commit/5e4d441). Aprovado pelo humano
sobre a validação local, antes do PR. Implementado por um agente `general-purpose` em Sonnet e
revisado pelo orquestrador, que cortou um teste que repetia `test_frontmatter_de_topologia`.

**O que mudou.**
- Saíram `test_modo_review.py`, `test_modo_derive.py` e `test_modo_implement.py`: 22 testes, a
  maioria conferindo palavra no markdown.
- O que eles tinham de contrato já estava coberto: lint e atalho `dc.py` em `test_skill_base`,
  `allowed-tools` por igualdade em `TOPOLOGIA`, e subcomandos citados em `test_dc`.
- Fica um teste de contrato, em `test_handoff.py`: o `SKILL.md` do `derive` cita cada título que o
  `dc.py` lê do stdin (`_SECOES_HANDOFF`).

| Evidência | Resultado |
|---|---|
| Suíte | 583 OK (eram 604: saíram 22, entrou 1) |
| [CI no branch](https://github.com/futureridetoday/DecodeAndCode/actions/runs/38838480053) | Verde |

**O que ficou de fora.** A prova do *Como verificar* só acontece na reescrita do `P-07`.

#### P-12 · Possível sinal falso no `post_compact.py`

| | |
|---|---|
| **Onde** | `.claude/hooks/post_compact.py` |
| **Critério** | C3 |

**Evidência.** O hook sempre chama `anunciar_post_compact(ativas_antes, voltaram=[])`, então nomeia
**toda** guideline com `paths:` que estava ativa como "não voltou". Não foi medido se isso é falso na
prática, porque elas podem de fato não voltar até o próximo acesso.

**Solução recomendada.** Se `P-05` tirar o hook do pacote, medir uma vez neste repositório e corrigir
ou apagar. Se ficar, medir antes de manter.

**Como verificar.** Sessão com uma guideline ativa, compactação manual e leitura do arquivo coberto:
comparar o anúncio com o log de `InstructionsLoaded` com `load_reason: compact`.

**Implementado em 2026-10-16**, no commit
[`4c63876`](https://github.com/futureridetoday/DecodeAndCode/commit/4c63876). Aprovado pelo humano
sobre a validação local, antes do PR. Implementado por um agente `general-purpose` em Sonnet e
revisado pelo orquestrador, que cortou de `hooks.md` um parágrafo que repetia este registro.

**A medição controlada não foi feita; a documentação a substituiu.**
- A página de memória diz que as rules com `paths:` "load again on demand" depois da compactação. A
  de hooks define `load_reason: compact` como a recarga depois de uma compactação.
- Nesta sessão, depois de uma compactação, o hook anunciou `scripts.md` como não voltada, e ela
  voltou no próximo acesso a um `.py`.
- O aviso não era falso: descrevia o intervalo até o próximo acesso, que o Claude Code resolve
  sozinho. Custava contexto a cada compactação sem mudar comportamento.

**O que mudou.**
- Saíram o `post_compact.py` e sua entrada no `settings.json`.
- Do `activation_notice.py` saíram `anunciar_post_compact` e as quatro funções que só ele usava.
- O `instructions_loaded.py` não grava mais estado em `/tmp`, porque o único leitor era o
  `post_compact.py`. Isso resolve a sobra registrada no `P-05`.
- README, `docs/recursos/hooks.md` e a norma deixam de citar o hook.

| Evidência | Resultado |
|---|---|
| Suíte | 590 OK (eram 604) |
| Pacote | `verificar` e `validar --strict` vazios |
| `instructions_loaded.py` com payload de `scripts.md` | Código 0, log gravado, nenhum arquivo de estado novo |
| [CI no branch](https://github.com/futureridetoday/DecodeAndCode/actions/runs/38838390194) | Verde |

#### P-13 · Resolução de `skills:` dentro do namespace do plugin não está confirmada

| | |
|---|---|
| **Onde** | `agents/planner.md`, `agents/developer.md`, `agents/ai-builder.md` — `skills: [decode-and-code]` |
| **Critério** | C3 |

**Evidência.**

- No plugin instalado, a skill aparece como `decode-and-code:decode-and-code`.
- A documentação de sub-agents só mostra nomes curtos e diz: "If a listed skill is missing or
  disabled … Claude Code skips it and logs a warning to the debug log".
- Se o nome curto não resolver, os agents rodam sem a skill, e só o log de debug registra.
- A própria norma admite, seção *Modelos*: "A ponte é declarada, e o carregamento nunca foi medido".

**Solução recomendada.** Medir antes de mudar qualquer coisa: `claude --plugin-dir
dist/decode-and-code --debug` num projeto vazio, invocar o `developer` e procurar o aviso no log. Se
não resolver, usar o nome com namespace.

**Como verificar.** O log de debug não contém o aviso de skill ausente, e o transcript do subagent
mostra o conteúdo da skill.

**Medido em 2026-10-15, dentro do `P-03`.** O nome curto **resolve** em `skills:` de um agent de
plugin: o debug log mostra `[Agent: decode-and-code:ai-builder] Preloaded skill 'decode-and-code'`,
e o mesmo acontece com `skills: [review-plan]`. A falha silenciosa existe no caso inverso: `agent:`
com nome curto, numa skill de plugin, não acha o agent e cai no padrão sem aviso. Nenhuma mudança é
necessária aqui. Ver o registro do `P-03`.

## O que manter

| Peça | Por quê |
|---|---|
| Fronteira skill / script | Gates, numeração, projeção de estado e lint ficam em código; a fatia e o julgamento ficam com o modelo. Continua útil com modelos melhores, porque o que é determinístico não melhora com modelo |
| Gates de entrada e de saída do `implement` | É a prática de dar ao modelo um jeito de verificar o próprio trabalho. O estado projetado a partir do teste, nunca editado à mão, é a melhor peça do plugin |
| Modo explícito, nunca inferido | Um `derive` disparado por engano move arquivos |
| Guardrail como `PreToolUse` com `deny` | Hook para o que precisa ser garantido, não lembrado |
| "Se o executor precisou perguntar, a unidade falhou" | A correção volta para quem derivou, nunca fica com o executor |
| `verificar()` + `validar()` no build | O par que fecha a invariante de instância nos dois sentidos |
| Distribuição por `archive` com `sha256` | Confere com a documentação, inclusive `displayName` no manifesto |
| Disciplina de evidência | Lacunas `L-XX`, medições datadas, citação literal da documentação nos comentários dos hooks |

## Escopo

As fases seguem a ordem de prioridade. Cada uma passa sozinha no teste de independência (ver
`## Independência`).

### Fase 1 — Corrigir o que está quebrado

| # | Unidade | Responsabilidade | Achado |
|---|---|---|---|
| 01 | `skill-dir-paths` | O `SKILL.md` compõe os scripts por `${CLAUDE_SKILL_DIR}/scripts/`; o `lint_skill` aceita o novo prefixo e recusa o fixo; o exemplo da norma passa a usar um marcador | P-01, P-11 |
| 02 | `installed-skill-proof` | Teste de pacote sobre o `SKILL.md` construído, mais o roteiro da prova manual com `--plugin-dir`, registrado no plano com o resultado. A mesma sessão mede `P-13` | P-01, P-13 |
| 03 | `hermetic-registry-test` | `test_registry` isolado em `tempfile`; o harness falha se a suíte deixar diff no repositório | P-02 |
| 04 | `strict-validate` | `validar()` com `--strict`; `hooks.json` com o caminho entre aspas | P-08 |
| 05 | `ci-workflow` | Workflow de CI com Python 3.10 fixo: harness, build e validação em todo PR para `dev` | P-08 |
| 06 | `narrow-permissions` | `settings.json` sem `Bash(python3*)` | P-09 |
| 07 | `delegate-model` | `delegate.md` sem `model:`. Pular se `D-01` aprovar a Fase 3 antes | P-04 |
| 18 | `skill-allowed-tools` | `allowed-tools` das skills sem `Bash` livre, conforme `D-05` | P-14 |

### Fase 2 — Enxugar o pacote

| # | Unidade | Responsabilidade | Achado |
|---|---|---|---|
| 08 | `package-dev-excludes` | `_copiar_skill` exclui `empacotar.py`, `reconciliar.py`, `lint_skill.py` e `lint_agente.py` | P-05 |
| 09 | `package-hooks-trim` | `_escrever_hooks_json` leva só `PreToolUse`, ou também `InstructionsLoaded`, conforme `D-02` | P-05, P-12 |
| 10 | `guardrail-silent-default` | `pre_tool_use.py` silencioso quando não há `guardrails.json` | P-05 |
| 11 | `package-frontmatter-strip` | O build remove do frontmatter distribuído os campos fora da tabela oficial; a fonte perde os campos vazios | P-10 |

### Fase 3 — Topologia: três skills (só com `D-01` aprovada)

| # | Unidade | Responsabilidade | Achado |
|---|---|---|---|
| 12 | `skill-split` | `review`, `derive` e `implement` viram três skills, cada uma com `model:` e `effort:` próprios e só o próprio procedimento | P-03, P-07 |
| 13 | `delegate-as-fork` | O `/delegate` vira `implement` com `context: fork` e `agent: developer`, ou sai; `commands/` sai do pacote | P-03, P-04 |
| 14 | `handoff-and-norm-sync` | `handoff.py`, a norma (*Modelos*, *`_handoff.md`*), o README, `docs/recursos/` e `test_agentes` passam a nomear a topologia nova | P-03 |
| 15 | `planner-reassess` | Decidir com evidência se o `planner` continua. Se sair, o agent e a doc saem junto | P-03 |

### Fase 4 — Contexto enxuto

| # | Unidade | Responsabilidade | Achado |
|---|---|---|---|
| 16 | `skill-procedure-only` | O `SKILL.md` fica só com o procedimento; nenhuma referência `L-XX`, unidade ou decisão numerada no pacote. Absorvida pela `12` se a Fase 3 rodar antes | P-07 |
| 17 | `ai-builder-slim` | `ai-builder` com menos de um quarto do tamanho, sem `skills:` e sem persona, lendo o `plan_root`; ou substituído por uma skill de intake, conforme `D-03` | P-06 |

## Independência

**As quatro fases passam no teste de independência**: entregar só uma delas e parar deixa o sistema
em estado válido e útil.

- A Fase 1 conserta o pacote instalado e a verificação sem depender de nada.
- A Fase 2 encolhe o pacote sem mudar como ele se usa.
- A Fase 3 é decisão arquitetural própria.
- A Fase 4 é limpeza de contexto.

Pela norma (*Avaliação de escopo*), isso faz delas **planos separados**, não um.

**Por que o documento nasce único mesmo assim.** Ele é o registro de uma revisão: os achados se
explicam uns pelos outros (`P-04` e `P-07` se resolvem dentro de `P-03`; `P-11` cai junto com
`P-01`), e separá-los antes da aprovação perderia esse fio.

**A recomendação para o `review` é dividir:**

| Plano proposto | Conteúdo |
|---|---|
| A | Fase 1 |
| B | Fase 2 |
| C | Fase 3, só depois de `D-01` |
| D | Fase 4 — se C for aprovado, a unidade `16` some e a `17` pode virar um plano pequeno |

Este documento fica como fonte comum, citado pelos quatro.

**Dependências entre as fases.** A Fase 1 vem primeiro, porque a `12` reescreve o `SKILL.md` que a
`01` corrige, e a correção precisa existir antes, para que o pacote atual funcione. A Fase 2 não
depende das outras. A Fase 4 depende de `D-01` só para decidir se a `16` existe.

## Oráculo

| Alvo | Como se sabe que funcionou |
|---|---|
| Pacote instalado | `claude --plugin-dir` num projeto vazio roda `bootstrap` e `review` sem nenhum `find` e sem prompt de permissão para os scripts |
| Verificação | `git status --porcelain` vazio depois da suíte; CI verde em todo PR para `dev`; `claude plugin validate --strict` sem avisos |
| Pacote enxuto | O inventário do zip não contém os quatro scripts de desenvolvimento; o `hooks.json` contém só o que `D-02` decidir; um projeto sem `guardrails.json` gera stderr vazio no hook |
| Contexto | `SKILL.md` (ou cada skill da Fase 3) ≤ 6 KB; descrição do `ai-builder` ≤ 600 caracteres; nenhum `L-XX` no pacote |
| Topologia | Inventário com 3 skills e sem `commands/`; `implement` roda em Sonnet e `review` em Opus, conferido no transcript |

## Decisões

`D-01` e `D-04` foram aprovadas em 2026-10-15, com os ajustes registrados no `P-03` e no `P-08`. `D-05` foi aprovada em 2026-10-15 (opção C, ver `P-14`). `D-02` foi aprovada em 2026-10-15 (opção B, ver `P-05`). `D-03` foi decidida em 2026-10-15: o `ai-builder` vira skill de intake (ver `P-06`).

| # | Decisão pendente | Recomendação | Por que importa |
|---|---|---|---|
| D-01 | **Adotar a topologia de três skills** (Fase 3) — **aprovada em 2026-10-15** | Sim | É decisão arquitetural (`CLAUDE.md`, *Autonomia*). A premissa que justificou agents e commands — "a troca não é declarável na skill" (norma, *Modelos*) — não confere com a documentação atual |
| D-02 | **Quais hooks de anúncio continuam no pacote** — **aprovada em 2026-10-15: só `InstructionsLoaded`** | Nenhum, salvo evidência de uso do controle de três estados num projeto consumidor; com evidência, só `InstructionsLoaded` | Os três rodam em todo projeto que instala e nenhum chega ao modelo |
| D-03 | **O `ai-builder` continua como agent** — **decidida em 2026-10-15: vira a skill `intake` (ver `P-06`)** | Enxugar primeiro e medir; só depois decidir entre agent e skill | Agent isola contexto, e o intake pesquisa muitos arquivos — o isolamento pode pagar o custo. Sem medição, a escolha é opinião |
| D-04 | **O harness local aceita ≥ 3.10** — **aprovada em 2026-10-15** | Sim, com o CI fixando 3.10 como prova de compatibilidade | Muda a guideline `scripts.md`, que hoje exige 3.10 no harness |
| D-05 | **Como restringir o `allowed-tools` das skills** (`P-14`) — **aprovada em 2026-10-15** | Opção C: ponto de entrada único `dc.py` | Muda como as skills compõem os scripts; A não restringe nada, e B troca segurança por um pedido de aprovação a cada chamada |

## Lacunas

| # | Lacuna | Por que fica registrada |
|---|---|---|
| L-01 | **A resolução de `skills: [decode-and-code]` no namespace do plugin não foi medida** | A documentação não cobre plugin, e a falha é silenciosa — ver `P-13`. Medição prevista na unidade `02`. **Fechada em 2026-10-15**: o nome curto resolve (ver `P-13`) |
| L-02 | **Não se sabe se o upload de plugin pelo claude.ai recusa campos de frontmatter fora da especificação** | A documentação afirma isso para skill avulsa (claude.ai e Skills API), não para plugin. O README oferece o upload como caminho de instalação. **Mitigada em 2026-10-16**: o pacote só leva campos da tabela oficial (ver `P-10`); o upload continua sem medição |
| L-03 | **O sinal do `post_compact.py` não foi medido** | Ver `P-12`. **Fechada em 2026-10-16** pela documentação, sem a medição controlada: o hook saiu (ver `P-12`) |
| L-04 | **A suíte não rodou em 3.10 nesta revisão** | O ambiente tinha 3.11 a 3.13. Os 482 testes passam em 3.13, o que não prova compatibilidade com o Cowork. **Fechada em 2026-10-15**: o CI roda a suíte em 3.10 a cada push (ver `P-08`) |
| L-05 | **A latência do hook foi medida num só ambiente** | 35 ms de mediana num container Linux. Em macOS ou no Cowork o número pode ser outro; a recomendação de `P-05` não depende dele, mas o custo absoluto sim |
| L-06 | **Não houve sessão real com o plugin instalado** | Todos os achados sobre comportamento instalado vêm de leitura de código, da documentação e do pacote construído — nenhum de uma sessão com `--plugin-dir`. As unidades `02` e `13` fecham isso. **Parcialmente fechada em 2026-10-15**: `implement`, `review-plan` e `derive` rodaram em sessão real com `--plugin-dir` (ver `P-03`); o `bootstrap` e um `review` ponta a ponta continuam com a unidade `02` |
| L-07 | **Os princípios não viajam no pacote** | O `intake` aplica os gates A e B de `.claude/rules/principles.md`, que é regra do projeto e não vai no plugin. Num projeto que instalou só o plugin, os gates não estão onde a skill os cita. O `ai-builder` já tinha o mesmo problema. É preciso decidir se os princípios viajam com a norma em `reference/` ou se o `intake` os resume |

## Backlog

<!-- backlog:start -->
<!-- backlog:end -->

## Fonte

- Documentação oficial do Claude Code, lida em 2026-10-14:
  [plugins-reference](https://code.claude.com/docs/en/plugins-reference),
  [skills](https://code.claude.com/docs/en/skills),
  [sub-agents](https://code.claude.com/docs/en/sub-agents),
  [hooks](https://code.claude.com/docs/en/hooks),
  [plugin-marketplaces](https://code.claude.com/docs/en/plugin-marketplaces)
- [`modelo-dev-units.md`](../system/modelo-dev-units.md) — seções *Modelos*, *Empacotamento*,
  *Validar a ativação*, *Avaliação de escopo* e *O que cada porte carrega*
- [`huddle.md`](../system/huddle.md) — `H-11`, a medição do desvio de leitura no `ai-builder`
- [`principles.md`](../../../.claude/rules/principles.md) — código é custo, subtração antes de
  adição, gates A e B
- [`scripts.md`](../../../.claude/rules/scripts.md) — a guideline que `D-04` alteraria
- `.claude/skills/decode-and-code/SKILL.md`, `scripts/lib.py`, `scripts/lint_skill.py`,
  `scripts/empacotar.py`, `scripts/tests/test_registry.py`, `.claude/hooks/*.py`,
  `.claude/agents/*.md`, `.claude/commands/*.md`, `.claude/settings.json`
