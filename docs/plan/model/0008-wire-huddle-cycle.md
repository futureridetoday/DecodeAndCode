---
# about
name: wire-huddle-cycle
type: plan
project: DecodeAndCode
description: O huddle deixa de depender de alguém lembrar dele — um arquivo por pessoa, registro e fechamento por comando, linha de fecho conferida nas skills, lembrete semanal ao abrir a sessão, promoção de item a guideline ou guardrail e uma skill que conduz a conversa
tags: [decode-and-code, huddle, hook, skill, plugin]

# alvo
plan_id: "0008"
plan_size: médio
core: model
module: wire-huddle-cycle
block: ""

# history
author: Claude
created: 2026-11-10
status: approved
version: 1.0.0
updated: "2026-11-15"
approved_by: Bortoli
approved_at: 2026-11-15

# system
scope: project
auto_load: false
dependencies: [add-norm-writers]
---

# O huddle passa a ser acionado — por pessoa, por comando e com lembrete

## Objetivo

**Clarificar.** O huddle existe como norma, script e 11 testes verdes, mas nenhuma skill do pacote
2.0.0 o aciona, e quem conduz o projeto perde a fila do que não foi decidido: nas duas instâncias
nenhuma conversa de huddle aconteceu desde 2026-08-22. E o desenho de hoje — um arquivo por projeto
— não serve a um time: as entradas do trabalho de uma pessoa aparecem para a outra, e duas pessoas
abrindo `H-12` em branches diferentes colidem. Métrica: linha de fecho presente e coerente nos
relatórios das skills, e intervalo entre huddles de cada pessoa dentro do que ela configurou.
Beneficiário: cada pessoa que trabalha num projeto que instalou o plugin.

**Evitar.**

| Alternativa | Por que não basta |
|---|---|
| Instrução só na norma | É o estado atual. A norma manda a linha de fecho, e nenhum `SKILL.md` a pede. Copiar os gatilhos para cada `SKILL.md` contraria a `D-06` do `apply-plugin-review`; o caminho que funcionou foi um subcomando que imprime o trecho (`D-08` de lá) |
| Agendamento — `/loop`, tarefa do Desktop, rotina na nuvem | `/loop` e cron de sessão expiram em 7 dias e só disparam com a sessão aberta ([scheduled-tasks](https://code.claude.com/docs/en/scheduled-tasks)). Desktop e nuvem são configuração de máquina e de conta — *A rotina fica de fora do plugin*, no `0001` |
| Hook `Stop` declarado em cada skill para cobrar a linha | A [doc](https://code.claude.com/docs/en/hooks) diz que hook de skill "keeps running them for the rest of the session": depois de um `review-plan`, toda resposta da sessão seria cobrada. Rejeitado em 2026-11-10 (`D-04`) |
| Editar `huddle.md` à mão | É o que existe hoje, e a evidência abaixo mede o resultado |

**Reduzir.** Comandos `dc.py huddle-*` que escrevem com formato garantido no arquivo de cada pessoa, um
gate de fecho rodado pelas skills, um aviso ao abrir a sessão quando o huddle da pessoa está
atrasado, e uma skill que conduz a conversa e promove item a guideline ou guardrail pelos comandos
do `add-norm-writers`.

## Gates

| Gate | Resposta |
|---|---|
| **A — necessidade real** | Sim, medida em 2026-11-10 (tabela *Evidência*): fila parada há 80 dias nas duas instâncias, e um caso em que a declaração do relatório divergiu do arquivo |
| **B — mínimo viável** | Cortado: agendamento fora da sessão; hook `Stop` por skill; hook `type: prompt` ou `agent` tentando detectar gatilho; carregar o arquivo do huddle automaticamente (veta a `D-08` do `0001`); o *Prompt de continuidade* preenchido à mão, que a `pauta` substitui; mecanismo elaborado de promoção — por ora, fechar com destino e gravar pelo comando |

## Evidência

Medida em 2026-11-10, só leitura.

| Fato | Onde |
|---|---|
| Nenhuma skill nem hook do pacote menciona o huddle; `huddle.iniciar` só é chamado por teste | `grep -rn -i huddle` no pacote 2.0.0 — só `huddle.py`, a norma e a docstring de `bootstrap.py` |
| Nenhum subcomando de huddle no `dc.py`; o único Bash liberado nas skills é o `dc.py`. Edit e Write estão liberados, então o registro à mão é possível, mas sem formato garantido e sem instrução que o peça | `dc.py:236-284`; `ALLOWED_TOOLS` em `tests/test_skill_base.py:33-36` |
| Esta instância: 10 abertas, 1 fechada (H-02, em 2026-08-22); último registro em 2026-09-14 | [`huddle.md`](../system/huddle.md) |
| AmFlow: 10 abertas, 0 fechadas; último registro em 2026-10-01 | `AmFlow/docs/plan/system/huddle.md` |
| *Prompt de continuidade* colado uma vez só, em 2026-08-22, com os campos ainda vazios | Transcripts locais dos dois projetos |
| 2026-09-03: um relatório declarou `entradas novas no huddle: 1` e o arquivo não ganhou entrada; o `lint_relatorio` de hoje aceitaria | Transcript da revisão de `adota-decode-and-code`, no AmFlow |
| A data do último huddle derivada de `## Fechadas` daria 2026-08-22 — 178 de 182 commits daqui | `git log --since=2026-08-22` |

## Solução

| Quem | O quê |
|---|---|
| **Arquivo por pessoa** | `<plan_root>/system/huddle/<usuario>.md`, versionado. `<usuario>` é o `git config user.name` em kebab-case ASCII. O fluxo, a pauta e o aviso leem só o arquivo de quem está na sessão; o arquivo dos outros continua no git (`D-02`) |
| **Script** (`huddle.py`, via `dc.py huddle-*`) | Tudo que é formato: identidade, próximo `H-XX`, cabeçalho, mover entrada fechada para `## Fechadas` com data e destino, gravar a data do huddle, montar a pauta, imprimir os gatilhos da norma, conferir a linha de fecho, migrar o arquivo único de projeto para o arquivo da pessoa |
| **Gate de fecho** | O último passo de cada skill roda `dc.py huddle-fecho`, que imprime os gatilhos, e depois `dc.py huddle-lint-relatorio` sobre a mensagem final, antes de enviá-la — mesmo padrão dos outros gates do método (`D-04`) |
| **Hook de sessão** (`SessionStart`) | Lê o arquivo da pessoa; atrasado e com entrada aberta, devolve o aviso. Nunca escreve |
| **Skill `huddle`** | Conduz a conversa da pessoa, uma entrada por vez, e promove item a guideline ou guardrail pelos comandos do `add-norm-writers` |

Os gatilhos continuam sem oráculo — a norma já diz que nenhum é observável por script. O que este
plano torna verificável é a **declaração**, o **formato**, a **posse** e o **atraso**.

## Tarefas

- [ ] **T1 — identidade e caminho.** `huddle.usuario(projeto) -> str`: `git config user.name` do
      projeto em kebab-case ASCII; sem nome configurado, recusa com mensagem que diz o comando para
      configurá-lo. `huddle.caminho(projeto, usuario)` devolve
      `<projeto>/<plan_root>/system/huddle/<usuario>.md`. Testes com nome acentuado, com espaço e
      ausente, contra `git` real num repositório `tempfile`.
- [ ] **T2 — operações no `huddle.py`.** Compatíveis com o contrato da `0001-21`: `iniciar(destino)`
      continua funcionando, e ganha os parâmetros opcionais `projeto` e `usuario`, sem
      `lib.repo_root()` quando `projeto` vem; o esqueleto passa a ter `owner`, `last_huddle: ""` e
      `reminder_days: 7` no frontmatter, e `lint_arquivo` passa a recusar `reminder_days` que não seja
      inteiro maior ou igual a zero. Novas:
      `abrir(arquivo, tipo, texto, autor) -> str` — texto pelo chamador, próximo id = maior `H-XX`
      de `## Abertas` e `## Fechadas` + 1, data de hoje, inserido no fim de `## Abertas`, antes do
      próximo `## `; recusa tipo fora do vocabulário fechado; cria o arquivo por `iniciar` se faltar;
      **recusa** enquanto existir o arquivo único de projeto, `<plan_root>/system/huddle.md`, com a
      mensagem que manda rodar `huddle-migrar` — sem isso, o primeiro registro num projeto como o
      AmFlow partiria o huddle em dois arquivos.
      `migrar(projeto, usuario) -> Path` — move `<plan_root>/system/huddle.md` para o arquivo da
      pessoa por `git mv` e acrescenta ao frontmatter `owner`, `last_huddle: ""` e
      `reminder_days: 7`; recusa se o destino já existir; sem o arquivo antigo, não faz nada.
      `fechar(arquivo, id, destino)` — tira a entrada de `## Abertas` e acrescenta a linha no fim da
      tabela de `## Fechadas`, antes do próximo `## `; recusa id inexistente.
      `concluir(arquivo, data)` — grava `last_huddle`.
      `pauta(arquivo, desde=None) -> dict` — abertas e `git log --oneline --since` com `cwd` no
      projeto; `desde` padrão é `last_huddle`, ou `created` se vazio ou ausente; no máximo 50 commits
      e a contagem dos omitidos; sem git, lista vazia e um aviso, nunca exceção.
      Testes num arquivo novo, `tests/test_huddle_cycle.py`, inclusive com uma seção extra depois de
      `## Fechadas`; `tests/test_huddle.py` só muda no caminho da instância real (T9).
- [ ] **T3 — linha de fecho com ids.** `lint_relatorio(texto, arquivo=None)`: sem `arquivo`, o
      contrato de hoje; com `arquivo`, exige `entradas novas no huddle: N` e, com `N > 0`, os ids
      entre parênteses — exemplo literal `entradas novas no huddle: 2 (H-12, H-13)` —, `N` igual à
      quantidade de ids, e cada id em `## Abertas` com a data de hoje no cabeçalho, para que entrada
      antiga não passe como nova. Testes para zero, `N` coerente, id inexistente, id antigo e `N`
      divergente.
- [ ] **T4 — subcomandos planos no `dc.py`**, na forma da `D-06` do `add-norm-writers`:
      `huddle-iniciar`, `huddle-abrir`, `huddle-fechar`, `huddle-concluir`, `huddle-pauta`,
      `huddle-fecho`, `huddle-lint`, `huddle-lint-relatorio` e `huddle-migrar`. Resolvem o arquivo da
      pessoa por T1, com a raiz de `lib.repo_root()`, como os outros subcomandos. `huddle-abrir` e
      `huddle-lint-relatorio` leem o texto do stdin, como o `handoff`; `huddle-lint-relatorio` mantém
      o contrato 0/1/2 do `dc.py`. `huddle-fecho` imprime as subseções da seção *Huddle* que tratam
      de gatilhos e de momento, pelos títulos que T8 fixar — hoje *Despejo — o invariante
      verificável* (onde estão os gatilhos) e *Momento — no fecho, e a linha de fecho é obrigatória
      mesmo em zero* —, no padrão do `dc.py normas`; se a norma do projeto não tiver esses títulos (a
      cópia materializada antes deste plano, `L-05`), lê a do pacote, na ordem de
      `bootstrap._fonte_norma`. Os nove entram em `SUBCOMANDOS` (`tests/test_dc.py:44-56`).
- [ ] **T5 — as quatro skills** (`intake`, `review-plan`, `derive`, `implement`): o passo final roda
      `dc.py huddle-fecho`, registra por `dc.py huddle-abrir` o que continuou aberto, e roda
      `dc.py huddle-lint-relatorio` sobre a mensagem final antes de enviá-la. No `implement`, fica
      explícito que o arquivo do huddle é exceção à regra de tocar só os arquivos declarados. O
      `intake` (hoje 4086 de 4096 bytes) é enxugado para caber no teto com o passo novo (`D-05`): o
      corte só remove texto que repete a norma ou outro trecho do próprio `SKILL.md` — a linha 57,
      com 458 caracteres, é a primeira candidata —, e o diff do corte vai na revisão da entrega com
      cada trecho removido apontando onde a mesma instrução continua. `lint_skill`,
      `test_skill_md_do_intake_cabe_no_teto_de_bytes` e `test_skills_citam_so_subcomandos_que_existem`
      continuam verdes.
- [ ] **T6 — `SessionStart` no pacote.** `session_start.py`, matcher `startup`, resolve o projeto por
      `CLAUDE_PROJECT_DIR` — nunca por `lib.repo_root()`. Acha os scripts pelo mesmo
      `sys.path.insert` de `pre_tool_use.py:41`, importa só `lib` (para `lib.config()["plan_root"]`)
      e `huddle` (para T1), e roda um `git config user.name` com `cwd` no projeto — o único
      subprocesso, na abertura da sessão; o custo medido entra no relatório da tarefa. `reminder_days`
      ausente ou inválido vale 7. Com o arquivo da pessoa presente, entrada aberta e
      `reminder_days > 0` dias ou mais desde `last_huddle` (ou `created`), devolve JSON com `systemMessage` para a pessoa e `additionalContext` para o
      modelo: quantas abertas, há quantos dias, e `/decode-and-code:huddle`. Silencioso em qualquer
      outro caso e em qualquer erro. `SessionStart` entra em `_EVENTOS_DO_PACOTE`, no `settings.json`
      e em `_EVENTOS_QUE_VIAJAM`, `_HOOKS_DA_FONTE` e `_HOOKS_QUE_VIAJAM`
      (`tests/test_empacotamento.py:64-70`), e a docstring de `empacotar.py:14-22` passa a contar três
      eventos. Teste por subprocesso com `CLAUDE_PROJECT_DIR` num `tempfile`: 6, 7 e 8 dias,
      `reminder_days: 0`, `last_huddle` ausente, e outra pessoa com entradas abertas — que não gera
      aviso para quem está na sessão.
- [ ] **T7 — skill `huddle`.** Linha da `TOPOLOGIA`: `modo: huddle`, `model: opus`,
      `disable-model-invocation: true` (a `D-08` do `0001`: o huddle se abre quando a conversa
      acontece), sem `context`, `allowed-tools` igual a `ALLOWED_TOOLS`. Atalho `skills/huddle/dc.py`
      copiado das outras; o corpo cita `${CLAUDE_SKILL_DIR}/../decode-and-code/scripts/`. Sem
      argumento: roda a `pauta` da pessoa e percorre as abertas uma a uma pela ferramenta de
      perguntas — decidir (destino em texto livre), promover a guideline ou guardrail, descartar
      (motivo), manter —; promover chama `dc.py criar-guideline` ou `dc.py adicionar-guardrail`
      (`add-norm-writers`) e depois `dc.py huddle-fechar` com o caminho gravado; termina com
      `dc.py huddle-concluir`. Com `registrar <texto>`: abre a
      entrada com a pessoa como autora e pergunta o tipo.
- [ ] **T8 — documentação.** Norma, seção *Huddle*: um arquivo por pessoa, identidade, comandos,
      linha com ids, quatro skills, `reminder_days`, promoção, quem registra. As enumerações que a
      quinta skill e o terceiro hook tornam falsas: norma (*Empacotamento*, *Camada de execução*,
      *Modelos*), README (contagem de hooks e de skills, seção *Huddle*), `docs/recursos/hooks.md`,
      `.claude/CLAUDE.md` (*Arquitetura* e *Recursos Instalados*), comentário de `lib.SKILLS`.
      `docs/recursos/huddle.md` novo.
- [ ] **T9 — migração desta instância e saída do rascunho antigo.** `dc.py huddle-migrar` move
      `docs/plan/system/huddle.md` para `docs/plan/system/huddle/<usuario>.md` — o mesmo comando que
      o AmFlow usará na sua migração. As referências vivas ao caminho antigo passam ao novo, medidas
      por `grep -rn "system/huddle.md"` em 2026-11-15: `.claude/CLAUDE.md:56`; `README.md:159-186`
      (link e a instrução de `huddle.iniciar`, que T8 reescreve); `tests/test_huddle.py:47`, o teste
      da instância real (`L-31` do `0001`), depois do qual `dc.py verificar` sobre a `0001-21` volta
      a passar; a *Fonte* do `apply-plugin-review.md`; e os dois links deste plano. Planos concluídos
      (`0001` e as unidades `19` e `21`) não são reescritos: são registro do que valia quando
      fecharam. `huddle-command.md` sai do `_inbox`.
- [ ] **T10 — versão**: o número é decisão humana no release; bump em `.claude/plugin.json` e
      `.claude-plugin/marketplace.json`.

## Oráculo

| Alvo | Como se sabe que funcionou |
|---|---|
| Operações | Testes de `test_huddle_cycle.py` verdes; `lint` sobre o arquivo depois de `abrir` e `fechar` devolve lista vazia; `test_huddle.py` continua verde |
| Despejo | Depois de `fechar H-XX`, o id está só em `## Fechadas` — o invariante da norma passa a ser produzido, não só verificado |
| Posse | Num `tempfile` com dois `user.name`, `abrir` grava no arquivo de cada um; `pauta` e o aviso de um não trazem entrada do outro |
| Fecho | Relatório que declara `1 (H-11)` com `H-11` antiga é recusado; com a entrada de hoje, aprovado |
| Lembrete | Teste de T6: 7 e 8 dias com entrada aberta geram o JSON; 6 dias, `reminder_days: 0` ou nada aberto, saída vazia. Em sessão real com `--plugin-dir`, registrar onde o `systemMessage` aparece (`L-02`) |
| Promoção | Num huddle desta instância, uma entrada promovida gera a rule ou a regra pelo comando, e a linha em `## Fechadas` aponta o caminho gravado |
| Migração | Num `tempfile` com `system/huddle.md`, `huddle-abrir` recusa e manda migrar; depois de `huddle-migrar`, o arquivo da pessoa tem os três campos, `lint` devolve lista vazia e o arquivo antigo não existe mais. Nesta instância, `git grep "system/huddle.md"` só acha planos concluídos |
| Fecho com norma antiga | Com uma norma de projeto sem os títulos de T8, `huddle-fecho` imprime as subseções da norma do pacote |
| Pacote | `claude plugin validate --strict` limpo; o inventário do zip tem `hooks/session_start.py` e `skills/huddle/SKILL.md` |

## Decisões

| # | Decisão | Estado |
|---|---|---|
| D-01 | **Três planos:** `add-norm-writers`, este, e `onboard-new-project` — que estende o mesmo `session_start.py` e usa estes comandos | Decidida pelo humano em 2026-11-10 |
| D-02 | **Um arquivo por pessoa, versionado e filtrado.** Cada pessoa vê, no fluxo e no aviso, só as suas entradas; o arquivo dos outros continua no git, e a promoção fica rastreada. A norma de hoje diz "um arquivo por projeto" — muda em T8 | Decidida pelo humano em 2026-11-10 |
| D-03 | **Lembrete ao abrir a sessão, com a frequência no arquivo da pessoa** (`reminder_days`, 0 desliga). Atende *A rotina fica de fora do plugin*, do `0001`: "quem instalar decide se quer, e com que frequência" | Lembrete decidido pelo humano em 2026-11-10; o campo, em 2026-11-15 |
| D-04 | **O fecho é conferido por gate do `dc.py` rodado pela skill, não por hook.** Mais fraco — depende de a skill rodar o passo —, e é o padrão de todos os outros gates do método | Decidida pelo humano em 2026-11-10 |
| D-05 | **O `intake` é enxugado para caber no teto de 4096 bytes**, em vez de subir o teto | Decidida pelo humano em 2026-11-10 |
| D-06 | **Os dois registram, cada um no próprio arquivo.** O modelo, por gatilho de evento, no arquivo da pessoa em cuja sessão o trabalho aconteceu; a pessoa, por `/decode-and-code:huddle registrar` — o tipo mais valioso que só ela escreve é a retrospectiva (`0001`, *A rotina fica de fora do plugin*). A peneira continua na saída | Decidida pelo humano em 2026-11-10 |
| D-07 | **Promoção simples:** fechar com destino e gravar pelo comando de `add-norm-writers`, com aprovação na conversa. Mecanismo mais elaborado fica para depois | Decidida pelo humano em 2026-11-10 |
| D-08 | **A data do último huddle é campo gravado (`last_huddle`)**, não derivada de `## Fechadas` | Decidida pelo humano em 2026-11-15 |
| D-09 | **O esqueleto continua sem *Prompt de continuidade* e sem *Como conversamos*** — como já é hoje (`huddle.py:94-131`). A `pauta` substitui o prompt; *Como conversamos* fica para cada pessoa, se quiser, fora do mecanismo | Decidida pelo humano em 2026-11-15 |
| D-10 | **Subcomando em pt-BR (`huddle-pauta`, `huddle-fecho`) é aceitável:** a `D-09` do `0001` vale para o nome do conceito e do arquivo, e os subcomandos do `dc.py` já são pt-BR. A forma é plana, com o prefixo `huddle-`, pela `D-06` do `add-norm-writers` | Decidida pelo humano em 2026-11-15 |
| D-11 | **Um plano só.** T1-T4 são a base de T5-T7; separar o par fecho (T3, T5) do par lembrete e skill (T6, T7) deixaria dois planos editando `huddle.py` ao mesmo tempo | Decidida pelo humano em 2026-11-15 |
| D-12 | **Aprovar só com o `add-norm-writers` em `concluído` em `_planos.md`**, rodando `dc.py concorrencia` de novo na aprovação: T7 chama os comandos dele, e nenhum script lê `dependencies:` do frontmatter | Decidida pelo humano em 2026-11-15 |
| D-13 | **`huddle-migrar` acrescenta campos ao frontmatter**, exceção declarada ao princípio de `regioes.escrever_campos` ("acrescentar campo é decisão humana"): os três campos são do mecanismo, e a migração só roda quando o humano a chama | Decidida pelo humano em 2026-11-15 |
| D-14 | **Porte: médio declarado, com cerca de 20 arquivos tocados** — `huddle.py`, `dc.py`, cinco `SKILL.md`, o hook novo, `settings.json`, `empacotar.py`, quatro testes, norma, README, `.claude/CLAUDE.md` e `docs/recursos`. Médio roda sem unidades, na sessão da aprovação; grande decompõe em unidades com cold-start. A escolha do porte é do humano na aprovação | Decidida pelo humano em 2026-11-15: médio |

## Lacunas

| # | Lacuna | Por que fica registrada |
|---|---|---|
| L-01 | **Os gatilhos continuam sem oráculo** | Mesma `L-08` do `0001`: o gate confere a declaração, nunca se o modelo deveria ter registrado algo |
| L-02 | **Onde o `systemMessage` de `SessionStart` aparece não está na doc** | A [doc](https://code.claude.com/docs/en/hooks) o define como "shown to the user", mas diz que alguns eventos o entregam fora do transcript. O `additionalContext` garante que o modelo veja; o que a pessoa vê se mede em sessão real |
| L-03 | **A pré-aprovação do `dc.py` vale só no turno da skill** | "The grant clears when you send your next message" ([skills](https://code.claude.com/docs/en/skills)). Se a conversa do huddle sair da ferramenta de perguntas para mensagem livre, os comandos seguintes pedem permissão — o que, aqui, vale como confirmação de cada fechamento. Se responder à ferramenta de perguntas conta como "next message" não está na doc |
| L-04 | **O aviso só existe para quem abre o Claude Code** | Não há canal para chamar quem não abriu. Desktop e nuvem resolvem, e ficam fora do plugin |
| L-05 | **Projetos já iniciados ficam com a seção *Huddle* antiga** | O bootstrap nunca sobrescreve a norma materializada. O AmFlow mantém "um arquivo por projeto" e a sua instância única até migrar, o que é trabalho do AmFlow. A nota de release precisa dizer isso |
| L-06 | **Identidade pelo `user.name` do git** | Duas pessoas com o mesmo nome compartilham arquivo, e quem muda o nome ganha um arquivo novo. Aceito por simplicidade |
| L-07 | **A métrica do objetivo só se lê depois de semanas** | `git log` sobre `last_huddle` dos arquivos e uma amostra de relatórios, quatro semanas depois do release |
| L-08 | **Virada de dia no fecho** | T3 exige que o id declarado tenha a data de hoje. Uma skill que abre a entrada antes da meia-noite e fecha o relatório depois dela é recusada. Revisão de 2026-11-15; não resolvida aqui |

## Backlog

<!-- backlog:start -->
- [ ] **T1 — identidade e caminho.** `huddle.usuario(projeto) -> str`: `git config user.name` do
- [ ] **T2 — operações no `huddle.py`.** Compatíveis com o contrato da `0001-21`: `iniciar(destino)`
- [ ] **T3 — linha de fecho com ids.** `lint_relatorio(texto, arquivo=None)`: sem `arquivo`, o
- [ ] **T4 — subcomandos planos no `dc.py`**, na forma da `D-06` do `add-norm-writers`:
- [ ] **T5 — as quatro skills** (`intake`, `review-plan`, `derive`, `implement`): o passo final roda
- [ ] **T6 — `SessionStart` no pacote.** `session_start.py`, matcher `startup`, resolve o projeto por
- [ ] **T7 — skill `huddle`.** Linha da `TOPOLOGIA`: `modo: huddle`, `model: opus`,
- [ ] **T8 — documentação.** Norma, seção *Huddle*: um arquivo por pessoa, identidade, comandos,
- [ ] **T9 — migração desta instância e saída do rascunho antigo.** `dc.py huddle-migrar` move
- [ ] **T10 — versão**: o número é decisão humana no release; bump em `.claude/plugin.json` e

0 de 10 tarefas concluídas · atualizado em 2026-11-15
<!-- backlog:end -->

## Fonte

- [`modelo-dev-units.md`](../system/modelo-dev-units.md) — seções *Huddle*, *Bootstrap*,
  *Empacotamento*, *Camada de execução* e *Modelos*
- [`huddle.md`](../system/huddle.md) — a instância e a evidência de uso
- [`0001-decode-and-code-foundation`](0001-decode-and-code-foundation/0001-decode-and-code-foundation.md)
  — `D-08`, `D-09`, `D-28`, `L-08`; *O huddle é fila, não fonte*, *Gatilho de escrita*, *Momento* e
  *A rotina fica de fora do plugin*
- [`21-huddle-log`](0001-decode-and-code-foundation/21-huddle-log.md) — o contrato atual de
  `huddle.py`, mantido
- [`add-norm-writers.md`](0007-add-norm-writers.md) — os comandos que a promoção usa
- [`apply-plugin-review.md`](../_inbox/apply-plugin-review.md) — `D-05`, `D-06`, `D-08` e `P-07`
- `huddle-command.md`, rascunho de 2026-09-02 que este plano substitui (T9)
- Documentação oficial do Claude Code, lida em 2026-11-10:
  [hooks](https://code.claude.com/docs/en/hooks),
  [skills](https://code.claude.com/docs/en/skills),
  [scheduled-tasks](https://code.claude.com/docs/en/scheduled-tasks)
