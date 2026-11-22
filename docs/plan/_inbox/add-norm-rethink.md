---
# about
name: add-norm-rethink
type: plan
project: DecodeAndCode
description: Comando `/decode-and-code:rethink`, para a pessoa pedir a reavaliação de princípios, guidelines e guardrails depois de uma mudança de rumo — revisa os existentes (Manter, Editar, Arquivar) e sugere novos —, com o mecanismo que falta para editar e arquivar item da norma sem apagá-lo
tags: [decode-and-code, norma, rethink, setup, arquivamento]

# alvo
plan_id: ""
plan_size: médio
plan_type: feature
core: model
module: add-norm-rethink
block: ""

# history
author: Claude
created: 2026-11-22
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

# `rethink` — repensar a norma do projeto depois de uma mudança de rumo

> **Tipo proposto: `feature`**: skill nova, subcomandos novos e norma, com código e teste. **Porte
> proposto: `médio`**: pela *Quando cada porte cabe*, há passos (pergunta 1, não), e uma sessão os
> executa em sequência (pergunta 2, sim). Nenhuma parte precisa de cold-start isolado: são scripts
> com teste e uma skill, na escala do `0008` (cerca de 20 arquivos num médio, `D-14` de lá). O humano
> confirma tipo e porte na aprovação. **[Claude]**
>
> **Autoria.** Por causa da `H-20` e da `H-21`, cada item leva a marca de quem o sustenta:
> **[humano]** decisão do humano, **[Claude]** recomendação do Claude ainda não confirmada item a
> item, **[medido]** fato medido, com o arquivo ou o comando. O humano aceitou levar ao intake o
> desenho com as recomendações do Claude, e isso **não** confirma cada uma (`D-06`): elas estão em
> *Pendentes de decisão*.

## Objetivo

**Clarificar.** Depois de uma mudança de rumo do projeto, os princípios, as guidelines e os
guardrails continuam dizendo o rumo antigo em toda sessão, e o método não tem caminho para
revisá-los. **[humano]** O exemplo do pedido, um cenário: app iOS que começou com marca azul,
design sóbrio e o objetivo de ajudar a economizar, e passou a marca laranja, design divertido e o
objetivo de ajudar o usuário a ser consciente das escolhas de compra — comprar menos e comprar
certo. "É essencial atualizar princípios, guidelines e guardrails logo depois de registrar essa
mudança." **[medido]** Os três escritores só criam: `rules.criar_principio` recusa nome repetido e o
sexto princípio, `rules.criar_guideline` recusa nome existente em `rules/` e `rules-off/`, e
`guardrail.adicionar` recusa nome repetido. Nenhuma função edita nem remove item. **[medido]** A
norma (*Camada normativa → Princípio*) dá duas portas ao princípio, plano com unidade `norma` e o
setup, e diz: "Fora dessas duas, `principles.md` não se edita". **[medido]** Rodar o setup de novo
não revisa: a etapa 3 diz que o que está em `setup-decididas` "não volta", e `setup.registrar` recusa
chave já registrada.

**Métricas** *(recomendação do Claude)*:

- itens das três camadas revisáveis numa conversa depois da mudança de rumo: hoje nenhum, sem um
  plano por item; alvo: todos, cada um com Manter, Editar ou Arquivar;
- item apagado: alvo 0. O arquivado conserva o texto, a data, quem arquivou e o motivo (`D-05`);
- referência antiga que passa a apontar, em silêncio, para outra regra: alvo 0, porque o nome
  arquivado fica reservado.

**Beneficiário:** a pessoa que muda o rumo do projeto, que revisa a norma inteira numa conversa; e
as sessões do Claude, que deixam de carregar norma do rumo antigo.

**Evitar.**

| Alternativa | Por que não basta |
|---|---|
| Rodar o setup de novo | Pula o que já foi decidido e não revisa item existente **[medido]** (`setup/SKILL.md`, etapas 3 e 4; `setup.registrar`) |
| Registrar a mudança no huddle e decidir lá | O huddle promove a guideline ou guardrail por `criar-guideline` e `adicionar-guardrail`, e não edita nem arquiva; percorre entradas abertas, não a norma **[medido]** (`huddle/SKILL.md`) |
| Um plano com unidade `norma` para cada item | É a porta que a norma dá hoje ao princípio **[medido]**. No AmFlow, a única edição de guideline existente foi um plano inteiro, o `0027-extend-canonical-source-rule` (2026-11-15), com o arquivo editado à mão, sem escritor **[medido]** (`git log` de `.claude/rules/` no AmFlow, lido sem escrita). Um ciclo de plano por item, depois de cada mudança de rumo, é o custo que o pedido quer evitar **[Claude]** |
| Editar à mão | A norma proíbe para princípio; a guideline editada à mão não passa pelo lint, e o guardrail, pela prova do par **[medido]** |
| Desligar a guideline (`registry.desligar`, que move para `.claude/rules-off/`) | Só guideline: recusa princípio **[medido]**. Não tem subcomando no `dc.py` **[medido]**. E não serve para arquivar: `rules.auditar_arvore` passa `lint_guideline` em `rules-off/`, que exige `paths` casando arquivo existente, porque a desligada "volta a ser ligada um dia" **[medido]** (`rules.py`). Guideline arquivada porque o caminho dela sumiu reprovaria a auditoria **[Claude]** |
| Apagar o item | Planos antigos podem citá-lo **[humano]** (`D-05`) |

**Reduzir** *(recomendação do Claude)*. Uma skill, `rethink`, que reaproveita a conversa do setup e os
três escritores; arquivar é mover, com três campos, para uma pasta que nada carrega; editar é o
`--replace` dos três escritores, que valida a versão nova antes de tirar a antiga; o histórico é um
arquivo só, que só recebe acréscimo. Nenhum hook novo, nenhuma mudança no formato do `setup.md`.

## Gates

| Gate | Resposta |
|---|---|
| **A — necessidade real** | **Sem caso medido; passa por exigência explícita do humano, pelo protocolo de exceção** (`principles.md`). **[medido]** O humano não disse se o exemplo é projeto real. Nenhuma entrada do huddle nem item do `_backlog.md` daqui registra mudança de rumo; no `huddle.md` do AmFlow, lido sem escrita, a busca por "rumo", "pivot", "mudança de direção" e "reavali" não achou nada. O que existe é o buraco de capacidade, medido acima, e um caso vizinho: a edição de guideline do AmFlow por plano inteiro (`0027`), que não foi mudança de rumo. **Registro da exceção:** a regra é o gate A (impacto mensurável agora); o que já foi tentado é rodar o setup de novo, que não revisa item existente **[medido]**; o que se propõe no lugar é desenvolver pelo pedido do humano e registrar o caso real como pendência (`L-01`); a exigência é do humano, no pedido de 2026-11-22 **[humano]**, e a aprovação da exceção é a aprovação deste plano |
| **B — mínimo viável** | **[Claude]** Cortado: **`restore`**, que traz de volta o arquivado: antes do commit, o desfazer é o git; depois, um item novo com outro nome (`P-05`); **mensagem nova no `dc.py normas`** para a norma arquivada: o comportamento que importa já existe, porque "arquivo ausente" e "seção não encontrada" vão para as não resolvidas, e o `implement` as relata como insuficiência da unidade **[medido]** (`normas.py`); a mensagem "arquivada em <data>: <motivo>" é conforto (`P-04`); **renomear no Editar**: Editar mantém nome e lugar, e trocar o nome é arquivar e criar; **guardar o par proibido/permitido** do guardrail, que é o item 4 da série (`norm-evolution-cases`); **lint do histórico**; **diff das edições no histórico**, que o git já guarda; **subcomando para `ligar`/`desligar`**, sem relação com o pedido; **renomear os subcomandos em português**, que é outro plano; **gatilho automático** para sugerir o `rethink`, que é o item 3 da série (`P-09`); **arquivar pelo huddle**, que é o item 6 (`D-13` do `0018`). **Não cortado:** o histórico, que o humano quer se não interferir (`D-01`); a reserva de nome, que é uma checagem a mais em cada escritor e impede a troca silenciosa de referência; o `--replace`, porque Editar é decisão do humano (`D-02`); e tirar do `setup/SKILL.md` o que as duas skills compartilham, pelo invariante "uma fonte por fato" (`P-01`) |

## Decisões

| # | Decisão | Autoria |
|---|---|---|
| D-01 | **O comando e a feature se chamam `rethink`: `/decode-and-code:rethink`.** Manter um histórico é bom, desde que não interfira no funcionamento do decode. O nome era `update`; o humano o trocou por `rethink` depois da medição do `P-08`: no Claude Code, `update` é atualizar versão de software | **[humano]**, 2026-11-22 |
| D-02 | **A revisão começa pelos itens que existem, na ordem princípios → guidelines → guardrails** (ordem sugerida pelo Claude, aceita pelo humano). Para cada item, a pessoa escolhe **Manter**, **Editar** ou **Arquivar**. Comandos e desenvolvimento sempre em inglês; as opções mostradas à pessoa seguem em português | **[humano]**, 2026-11-22 |
| D-03 | **Depois da revisão dos existentes, o Claude lê os arquivos do projeto**, considera o que a pessoa manteve, editou ou arquivou, e sugere itens novos para as três camadas | **[humano]**, 2026-11-22 |
| D-04 | **Item rejeitado antes que continue relevante pode ser sugerido de novo** | **[humano]**, 2026-11-22 |
| D-05 | **Item não pode ser apagado, porque planos antigos podem mencioná-lo:** arquivado, é registrado como arquivado e o conteúdo vai para um arquivo de arquivo. O humano pediu ao Claude para melhorar essa regra: a proposta é o `P-04` | **[humano]**, 2026-11-22 |
| D-06 | **O desenho de *Pendentes de decisão* foi levado ao intake com aceite do humano, o que não equivale a confirmar cada recomendação.** Cada `P-XX` se decide na revisão ou na aprovação | **[humano]**, 2026-11-22 |

### Pendentes de decisão

Todas **[Claude]**. Os fatos que as apoiam vão marcados **[medido]**.

| # | Pergunta | Recomendação |
|---|---|---|
| P-01 | Onde mora a conversa do `rethink`? | **Skill própria `rethink`**, invocada só pela pessoa (`disable-model-invocation: true`), na conversa principal, sem `context: fork`, porque a ferramenta de perguntas não existe em subagente (norma, *Setup*), e em Opus. Reaproveita a conversa do setup: uma sugestão por vez; Editar com edição livre ou guiada; item novo com Aprovar, Editar ou Rejeitar; o teto de 5 princípios e o teste de princípio. **Para não copiar texto entre as duas skills**, o que elas compartilham — a conversa de uma sugestão (as opções e as duas edições) e os três formatos de *Referência* (JSON pelo stdin, padrões de `paths`, formato do guardrail) — sai do `setup/SKILL.md` para a norma, seção *Setup*, e as duas skills o imprimem por `dc.py explicar`, como o setup já faz com a subseção *Princípio*. O `huddle/SKILL.md` repete a instrução de JSON pelo stdin **[medido]** e passa a citá-la também. O `descobrir` lista os existentes **[medido]**: lê `.claude/rules/*.md` e o `guardrails.json` (`descoberta.py`). **Risco:** o setup foi validado em sessão real (`0009`, `0013`), e mexer no texto dele pede reconferir; a remedição começa por um setup |
| P-02 | Como a avaliação sabe o rumo novo? | **Passo 0, "o que mudou"**: vem no argumento do comando, ou numa pergunta só. Se o objetivo mudou, o perfil do `setup.md` é reescrito por `setup-perfil` **[medido]** (`setup.perfil` reescreve `## Perfil` inteiro). Motivo: julgar cada item pede o rumo novo, e o north star nasce do objetivo, então ele é o primeiro item da revisão. Sem `setup.md` com `completed_at`, o `rethink` manda para o setup |
| P-03 | Como o rejeitado volta (`D-04`)? | **Sem filtro, ao contrário do setup:** o `rethink` não pula o que está em `setup-decididas`. O que já foi rejeitado e ainda vale volta mostrando quando e por que foi rejeitado, lido das linhas `rejeitada` do `setup.md` e do histórico do `rethink` |
| P-04 | A regra de arquivamento melhorada (`D-05`) | **Vale para as três camadas, e arquivar move, nunca apaga**, para fora do que o Claude Code carrega e do que o hook lê, espelhando o caminho: guideline `.claude/rules/<nome>.md` → `.claude/archive/rules/<nome>.md`; princípio, a seção sai de `principles.md` para `.claude/archive/rules/principles.md`; guardrail, a regra sai de `.claude/guardrails.json` para `.claude/archive/guardrails.json`. O arquivado leva `archived_at`, `archived_by` (a identidade do huddle, `git config user.name`) e `reason`. **Nome reservado:** os três escritores recusam o nome arquivado, senão a referência antiga aponta em silêncio para outra regra — hoje o `criar_guideline` já confere `rules/` e `rules-off/` **[medido]**, e passa a conferir o arquivo. **Unidade que cita item arquivado:** o `dc.py normas` a põe nas não resolvidas, e o `implement` para e relata, o que já acontece **[medido]**; unidade já verificada não é tocada. **Editar mantém nome e lugar:** quem cita recebe o texto novo; a versão anterior fica no git e numa linha do histórico. **Três refinamentos do intake:** (a) **não reaproveitar `rules-off/`**, porque o `auditar_arvore` reprova guideline cujo caminho sumiu **[medido]**, e desligada não é arquivada; (b) **o guardrail arquivado vai sem o par proibido/permitido**, porque o `guardrails.json` não o guarda **[medido]** (`guardrail.adicionar`; `0018`, *Próximos planos*, item 4); (c) **a pasta de arquivo nunca recebe arquivo chamado `CLAUDE.md`**: a documentação diz que um `CLAUDE.md` de subdiretório carrega quando o Claude lê ou escreve outro arquivo dali **[medido]** (code.claude.com/docs/en/memory, lido em 2026-11-22). **A medir antes de prometer** (`L-02`): a mesma página diz que `.claude/rules/` carrega recursivamente e não cita outra pasta de `.claude/` como fonte de instrução, mas documentação não é observação (`B-07`). A primeira tarefa mede com o controle de três estados. Se `.claude/archive/` carregar, o arquivo vai para `<plan_root>/system/archive/` |
| P-05 | `restore`? | **Cortar nesta versão** (gate B). Antes do commit, o desfazer é o git; depois, a pessoa cria um item novo com outro nome. Se a falta aparecer em uso, `restore` é a operação inversa, num plano pequeno |
| P-06 | Onde fica o histórico (`D-01`)? | **`<plan_root>/system/rethink.md`**, versionado, uma seção por `rethink`: data, quem decidiu, o que mudou e uma linha por item (camada, nome, decisão — mantido, editado, arquivado, criado ou rejeitado — e motivo). Escrito por script, com o esqueleto no próprio script, como `setup.py`. **Dois subcomandos**: `rethink-start`, que abre a seção com o que mudou, e `rethink-record`, que acrescenta a linha na hora de cada decisão, para que a conversa interrompida não perca o que já foi gravado em disco. Nada o carrega em contexto, nenhum hook o lê, e o formato do `setup.md` não muda |
| P-07 | Nomes | **Em inglês** (`D-02`): skill `rethink`; subcomandos `archive <principle\|guideline\|guardrail> <name>` (motivo no stdin), `rethink-start` e `rethink-record`; `--replace` em `criar-principio`, `criar-guideline` e `adicionar-guardrail`, troca atômica que valida a versão nova antes de tirar a antiga (o guardrail novo passa pela prova do par, como no `adicionar`). Funções novas também em inglês. Os subcomandos existentes em português não mudam neste plano; renomear é outro plano |
| P-08 | Risco de confusão com atualizar o plugin | **Resolvido em 2026-11-22 pela troca do nome (`D-01`).** **[medido]** No CLI do Claude Code, `update` atualiza versão: `claude update` (o próprio Claude Code), `claude plugin update <plugin>` e `claude plugin marketplace update [nome]`; o painel `/plugin` mostra *update available*; e o README do método, em *Atualização*, manda rodar `/plugin update decode-and-code@future-ride-today`. `rebuild`, também considerado pelo humano, colidiria com o vocabulário de build (`empacotar.construir`). A descrição da skill diz logo de início que o que se repensa é a norma do projeto |
| P-09 | Relação com a série `norm-evolution` (`0018`, *Próximos planos*, itens 3 a 6) | **O `rethink` é o caminho manual.** O item 3, `norm-evolution-trigger`, continua o gatilho automático (tempo ou evolução do projeto) e passa a ser "quando sugerir rodar o `rethink`". O item 6, saúde da norma, poderá arquivar pelo `archive` deste plano. Nenhum dos dois muda aqui |
| P-10 | Um plano ou dois (*Independência*) | **Um**, com as tarefas do mecanismo antes das da skill |

## Tarefas

- [ ] Medir, antes do resto, se o Claude Code carrega `.claude/archive/` (`P-04`, `L-02`): num projeto de prova, uma guideline em `.claude/archive/rules/` cujo `paths` casa um arquivo que a sessão toca; o humano abre a sessão nova, e `activation_notice.relatorio` sobre o `eventos.jsonl` mostra se ela carregou. Se carregar, trocar a pasta por `<plan_root>/system/archive/` nas tarefas abaixo
- [ ] Norma: em *Camada normativa*, a terceira porta (o `rethink`) para princípio, guideline e guardrail, e uma subseção *Editar e arquivar* com a pasta de arquivo, os três campos, o nome reservado, o que acontece com a unidade que cita o arquivado e o que não existe (apagar, `restore`); seção nova *Rethink* depois de *Setup*, com o passo 0, a ordem da revisão, as sugestões novas, o rejeitado que volta e o histórico; em *Setup*, a conversa de uma sugestão e os três formatos que as duas skills compartilham (`P-01`); onde o setup e o `rethink` escrevem
- [ ] `rules.py`, com teste: arquivar princípio (a seção sai de `principles.md` e entra no arquivo de arquivo com os três campos) e guideline (o arquivo se move, ganha os três campos e o `registry.json` é reprojetado); `--replace` de princípio e de guideline, recusando sem tocar o disco se a versão nova reprovar; `criar_principio` e `criar_guideline` recusam nome arquivado
- [ ] `guardrail.py`, com teste: arquivar regra (sai do `guardrails.json`, entra no arquivo de arquivo com os três campos; o hook deixa de negar o caso dela); `adicionar` com substituição, que prova a regra nova pelo par antes de trocar; nome arquivado recusado
- [ ] `rethink.py` novo, com teste: `start` cria o `rethink.md` com o esqueleto se faltar e abre a seção do dia com o que mudou; `record` acrescenta uma linha com decisão de vocabulário fechado e recusa, sem escrever, valor fora dele ou motivo vazio onde ele é exigido
- [ ] `dc.py`, com teste: `archive <principle|guideline|guardrail> <name>` com o motivo no stdin, que sai com 1 sem motivo, sem `user.name` ou com nome desconhecido; `--replace` nos três escritores; `rethink-start` e `rethink-record` com JSON pelo stdin
- [ ] Skill `rethink/` (`SKILL.md` e a cópia do `dc.py`), em `lib.SKILLS`; o `setup/SKILL.md` perde o texto que foi para a norma e passa a imprimi-lo por `explicar`, e o `huddle/SKILL.md` cita a instrução de JSON pelo stdin de lá; `lint_skill` sem problema nas três, e o teste que confere as cópias do `dc.py`. A tabela *Recursos Instalados* do `.claude/CLAUDE.md`; o guia `docs/recursos/rethink.md`; *Como editar* e *Como arquivar* em `create-principle.md`, `create-guideline.md` e `create-guardrail.md`; o README, com o `rethink` e a *Atualização* do plugin lado a lado (`P-08`)
- [ ] `scripts/test-python.sh` verde, inteiro; `empacotar.verificar` e o ciclo instalado aprovam o pacote, sem `.claude/archive/` nem `rethink.md` dentro dele
- [ ] Remedição (*Remedição*)

## Oráculo

| Alvo | Como se sabe que funcionou |
|---|---|
| Arquivar | Teste: para cada camada, o item some de onde carrega e aparece no arquivo de arquivo com texto igual e `archived_at`, `archived_by` e `reason`; arquivar princípio libera uma vaga no teto; o guardrail arquivado deixa de negar o caso proibido dele; nenhum byte do item se perde |
| Nome reservado | Teste: `criar-principio`, `criar-guideline` e `adicionar-guardrail` com nome arquivado saem com 1 e nada muda no disco |
| Editar | Teste: `--replace` com versão nova que reprova no lint ou na prova do par sai com 1 e deixa a antiga intacta; com versão válida, mesmo nome e mesmo lugar, texto novo |
| Unidade que cita arquivado | Teste de regressão: `dc.py normas` sobre unidade que cita guideline arquivada e seção de princípio arquivada lista as duas em `Não resolvidas:` |
| Histórico | Teste: `rethink-start` e `rethink-record` escrevem a seção e as linhas; o `setup.md` só muda pelo `setup-perfil` |
| Skill | `lint_skill` sem problema; `disable-model-invocation: true`; a cópia do `dc.py` idêntica às outras |

## Remedição

Num projeto descartável, com o pacote novo e o bootstrap feito, o cenário do pedido. O setup
grava o perfil do app iOS de marca azul, design sóbrio e objetivo de ajudar a economizar, o north
star, uma guideline de paleta azul em `App/Theme/**`, um guardrail e uma sugestão rejeitada. Uma
unidade em `spec` cita a guideline. Então `/decode-and-code:rethink` com "marca laranja, design
divertido, objetivo: consciência das escolhas de compra". Esperado: o perfil reescrito; a revisão
na ordem princípios → guidelines → guardrails, um item por vez, com Manter, Editar ou Arquivar; o
north star editado com o mesmo nome; a guideline azul editada ou arquivada; as sugestões novas
considerando o que foi decidido, e a rejeitada de volta com a data e o motivo; o `rethink.md` com a
seção do dia; o arquivado em `.claude/archive/`, fora do log de ativação; e o `dc.py normas` da
unidade listando a guideline nas não resolvidas, se ela foi arquivada.

## Independência

**[Claude]** O teste da norma (*Avaliação de escopo*) aplicado às duas partes que o pedido nomeia.
**O mecanismo** — arquivar e editar nas três camadas, com nome reservado — passa sozinho: deixa o
sistema válido e útil, porque os guias `create-*` já documentam o `dc.py` rodado direto, e ele
atende a `D-01` do `0018` ("o ciclo precisa remover regra, não só adicionar"). **A skill `rethink`
não passa sozinha:** Manter, Editar e Arquivar são a decisão do humano (`D-02`), e Editar e
Arquivar não têm mecanismo sem a primeira parte. Sim para uma e não para a outra é *dependência
sequencial, objetivo único*: fases no mesmo plano, e as tarefas põem o mecanismo antes da skill.
**Recomendação: não dividir.** A alternativa, o mecanismo num plano agora e a skill por outro
intake depois, deixaria o mecanismo com o mesmo gate A por exceção e sem caso próprio, e um esboço
da skill no `_inbox` esperando — o que a `H-18` mostrou gerar sinal falso de concorrência.

**Concorrência** **[medido]**. Nenhum plano `em desenvolvimento` em `_planos.md`. No `_inbox` resta o
`apply-plugin-review`, desatualizado (`H-18`), cuja tarefa 16 reescreve todo `SKILL.md`, inclusive o
do setup, que este plano também toca. Nenhum item do `_backlog.md` cobre este trabalho.

## Lacunas

| # | Lacuna | Detalhe |
|---|---|---|
| L-01 | **Sem caso real de mudança de rumo** | **[medido]** O gate A passa por exceção. Quando o primeiro caso real aparecer, aqui ou num projeto que usa o método, ele entra aqui como evidência, com o que o `rethink` resolveu ou não |
| L-02 | **Não medido se o Claude Code carrega `.claude/archive/`** | **[medido]** Só a documentação diz que não; é a primeira tarefa. O `rules-off/`, mesma forma de pasta irmã, foi medido sem carregar (norma, *Validar a ativação*), mas analogia não é medição **[Claude]** |
| L-03 | **O guardrail arquivado perde a prova** | **[medido]** O par proibido/permitido não é guardado em lugar nenhum. Quem quiser a regra de volta precisa de um par novo. O item 4 da série (`norm-evolution-cases`) é quem guarda o par |
| L-04 | **Subcomandos em duas línguas** | **[Claude]** Os novos em inglês (`D-02`) convivem com os existentes em português até outro plano renomeá-los |

## Fonte

- Pedido do humano de 2026-11-22, com as decisões `D-01` a `D-06` e as recomendações do Claude
- [`modelo-dev-units.md`](../system/modelo-dev-units.md): *Camada normativa* (*Princípio*, *Guideline*, *Validar a ativação*), *Setup*, *Huddle*, *Antes do plano*, *Avaliação de escopo*, *Quando cada porte cabe* e *Tipo de plano*
- [`0018-norm-evolution-log.md`](../model/0018-norm-evolution-log.md): `D-01`, `D-03`, `D-10`, `D-13` e *Próximos planos*
- [`0009-onboard-new-project`](../model/0009-onboard-new-project/0009-onboard-new-project.md), [`0016-setup-principles.md`](../model/0016-setup-principles.md) e [`0017-setup-resources.md`](../model/0017-setup-resources.md)
- `.claude/skills/decode-and-code/scripts/rules.py` (`criar_principio`, `criar_guideline`, `auditar_arvore`), `guardrail.py` (`adicionar`), `registry.py` (`desligar`), `normas.py` (`resolver`), `setup.py` (`perfil`, `registrar`), `descoberta.py` e `dc.py`; `.claude/skills/setup/SKILL.md` e `.claude/skills/huddle/SKILL.md`
- [Documentação do Claude Code, *memory*](https://code.claude.com/docs/en/memory), lida em 2026-11-22: carregamento de `.claude/rules/` e de `CLAUDE.md` em subdiretório
- AmFlow, lido sem escrita em 2026-11-22: `git log` de `.claude/rules/` (plano `0027-extend-canonical-source-rule`) e `docs/plan/system/huddle.md`
- [`huddle/bortoli-rafael.md`](../system/huddle/bortoli-rafael.md), `H-18`, `H-20` e `H-21`

## Backlog

<!-- backlog:start -->
<!-- backlog:end -->
