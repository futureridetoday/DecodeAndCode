---
# about
name: decode-and-code-foundation
type: plan
project: DecodeAndCode
description: Toda norma é hoje persuasão — zero hooks configurados, nenhuma regra com escopo, e a camada normativa que a própria norma especifica nunca foi construída. O plano cria as três camadas que faltam (princípio, guideline, guardrail), cada uma no mecanismo certo, dá porte ao plano para que correção de oito linhas não pague estrutura de quinze unidades, e empacota o modelo como plugin instalável em qualquer projeto
tags: [dev-units, decode-and-code, principios, guardrails, guidelines, plugin, hooks]

# alvo
plan_id: "0001"
plan_size: grande
core: model
module: decode-and-code
block: ""

# history
author: Bortoli
created: 2026-08-21
status: approved
version: 2.4.0
updated: 2026-08-22

# system
scope: project
auto_load: false
dependencies: []
---

# A camada normativa passa a existir, a impor onde é verificável, e a viajar como plugin

O modelo dev-units resolveu o problema para que nasceu: trabalho grande, decomposto, executável em
cold-start. Está medido — 15 de 15 unidades do plano `0002` do AmFlow
executadas por Sonnet em sessões novas, sem uma pergunta sobre conteúdo de unidade.

O que ele não resolveu é a **consistência do que sai**. A mesma base de código, o mesmo modelo e a
mesma norma produzem trechos de qualidade muito diferente entre uma sessão e outra. O diagnóstico
corrente é "faltam regras". Está errado: o repositório tem 458 linhas de `CLAUDE.md` e 869 de norma.

O que falta é **camada**. Hoje tudo é a mesma coisa — texto que o modelo lê e tenta seguir.

## O que foi medido

Medição de **2026-08-21**, contra `AmFlow@dev` = `8395030`. **Os sete fatos são sobre o AmFlow, e é
deliberado:** ele é o campo de prova deste método — o único repositório onde o modelo rodou tempo
suficiente para as falhas aparecerem. Repo novo é greenfield e não tem incidente nenhum a mostrar.

| Fato | Evidência | Consequência |
|---|---|---|
| **A arquitetura declarada tem 0% de implementação** | `AmFlow:docs/mvp/40_reference/clean-architecture.md` nomeia 7 Use Cases e 5 Entities: **0 de 7** e **0 de 5** existem no código. A regra de dependência que ela declara — *"Use Cases nunca dependem de implementações concretas de infraestrutura"* — é violada por `hub/lib/catalog.ts` (2 imports de supabase), `licenses.ts` (1) e `queries.ts` (1) | Decisão arquitetural registrada, com invariante nº 4 do `CLAUDE.md` a sustentá-la, **nunca chegou ao código** — e ninguém percebeu até se rodar `grep` em 2026-08-21 |
| **Nenhum hook configurado** | `AmFlow:.claude/settings.json` declara `PreToolUse`, `PostToolUse`, `SessionStart`, `Stop` e `SubagentStop` — os cinco com array **vazio** | Não existe norma imposta no repositório. Toda regra é advisory por construção |
| **Nenhuma regra com escopo** | `.claude/rules/` não existe | Toda norma que é carregada, é carregada sempre — e o que não cabe no orçamento, não é carregado nunca |
| **`CLAUDE.md` acima do limiar de aderência** | 458 linhas em 2026-08-21; remedido em 2026-08-23 durante a revisão: **465**. A doc do Claude Code fixa o alvo em **200**: *"longer files consume more context and reduce adherence"* | Aderência degradada no arquivo mais importante do projeto, e a distância do alvo está crescendo, não encolhendo |
| **A camada normativa nunca foi construída** | A norma especifica princípio/guideline/guardrail/referência em `<core>/system/` ([`modelo-dev-units.md:256`](../../system/modelo-dev-units.md)) — componente 3 de 5. `find docs/plan -type d -name system` devolve **apenas** `docs/plan/system/` | O componente que resolveria a inconsistência foi desenhado e nunca instanciado |
| **O invariante com incidente registrado não tem imposição** | O `CLAUDE.md` proíbe DDL direto em ambiente remoto **e registra a violação**: `notifications_hub_id_fkey`, 2026-08-12, divergência que só apareceu quando alguém tropeçou nela em produção | A proibição existe, já foi violada, e segue dependendo de o modelo lembrar dela na hora |
| **A cópia no repositório público já divergiu** | A `AmFlow:0003-11` copiou a skill e a norma para `futureridetoday/AmFlowPlugins` à mão em 2026-08-01. Hoje: norma **21 linhas atrás** (falta `#### Precedência entre os blocos`), e 3 dos 9 scripts menores — `regioes.py` 6190/6750, `scaffold.py` 4669/5671, `verificacao.py` **5453/7092** | O repositório público roda um gate de verificação anterior aos planos `0005` e `0006`, ambos concluídos em 2026-08-12. Cópia manual não é distribuição |

> **O candidato óbvio de guardrail não existe mais.** A regra de dependência entre cores — *Worker→Hub,
> Builder→Hub, Hub→nenhum* — era o exemplo que a norma dava em
> [`modelo-dev-units.md:280`](../../system/modelo-dev-units.md). A `AmFlow:0003-08`
> extraiu `plugins/` para outro repositório, e o par que o `grep` verificava deixou de existir aqui.
> A própria norma já registra a aposentadoria, na linha 681. Por isso o primeiro guardrail é outro — e
> escolhido por evidência de falha, não por elegância.

> **Não foi rejeitada. Foi meio-lembrada.** O nível que sobreviveu foi o dos **nomes** — `catalog.ts`,
> `licenses.ts` e `publish/` existem e batem com a tabela do
> `AmFlow:docs/mvp/10_architecture/index.md:97`. O que se perdeu foi a **inversão de dependência**,
> que é o princípio de verdade: esses módulos importam infraestrutura direto, então são helpers de query
> com nome de use case. Ninguém decidiu abandonar a regra — ela não estava carregada no momento em que
> cada arquivo foi escrito, e a parte saliente sobreviveu enquanto a estrutural não. Um arquivo de cada
> vez. É o retrato do que este plano corrige.

**A leitura dos sete fatos junta-se numa frase.** A documentação do Claude Code separa três verbos —
*CLAUDE.md persuade, permissões filtram, hooks impõem*. O AmFlow usa exclusivamente o primeiro. A
oscilação de qualidade não é falha de redação da norma: é a variância esperada de instrução
puramente persuasiva, que degrada quando o contexto enche ou quando duas instruções competem — e a
doc é explícita de que instruções contraditórias fazem o modelo *"pick one arbitrarily"*.

## Objetivo

A norma passa a existir em três camadas, cada uma no mecanismo que lhe corresponde, e o conjunto
viaja como plugin instalável em qualquer projeto. Fora das três, e deliberadamente **antes** delas,
fica o canal onde o que ainda não foi decidido espera para ser.

```
princípios   → rule sem paths          sempre carregado     poucos, inegociáveis
guidelines   → rule com paths: <glob>  por escopo de arquivo   vários, ligáveis por projeto
guardrails   → hook PreToolUse         por evento           determinístico — exit 2 bloqueia
método       → skill decode-and-code   sob demanda          orquestra as três
huddle       → arquivo no repositório  nunca carregado      pré-norma — fila, não fonte
```

O que **não** muda: o ciclo plano → unidade → cold-start → gate de saída. Ele funciona e é
preservado inteiro.

## Escopo

### Fase 1 — A base migrada volta a ficar verde

| # | Unidade | Responsabilidade |
|---|---|---|
| 01 | `config-and-paths` | Os 6 scripts acoplados deixam de assumir `docs/plan/`, os cores do AmFlow e a norma em caminho fixo: tudo resolve por `config.json` com defaults embutidos (`D-11`). As **36 linhas da norma** que citam cores e caminhos do AmFlow saem no mesmo movimento, porque são **sobre a mesma coisa** |
| 02 | `test-fixtures` | Os **25 testes que usam arquivos reais do AmFlow como fixture** ganham fixtures próprios. Oráculo direto: `./scripts/test-python.sh` verde |

**Vem primeiro por medição, não por gosto.** Sob `./scripts/test-python.sh`, o harness do próprio
projeto, a suíte migrada rodava **158 testes: 133 passam, 25 falham**, 0 pulados — as 25 por
apontarem para arquivos como `docs/plan/hub/0001-mcp/01-handler-auth.md`, que não existem aqui.
Depois da `01`, são **167 rodados, 142 verdes, os mesmos 25 vermelhos** (medido em 2026-08-24).
A afirmação de que a suíte vermelha impede toda unidade de passar pelo gate **está errada**, e a
`L-13` a mediu: o gate roda por arquivo declarado. A Fase 1 vem primeiro pela `D-12`, não por
mecânica.

**São duas unidades porque são dois oráculos.** A `01` afirma que caminho resolve por configuração; a
`02` afirma que a suíte fica verde. Juntá-las daria uma unidade com três frentes e um oráculo só —
acima do teto de 8 passos, e logo na unidade que destrava todas as outras.

### Fase 2 — A norma ganha princípios, a primeira imposição e como se verificar

| # | Unidade | Responsabilidade |
|---|---|---|
| 03 | `principles-rule` | Os **três princípios** fechados na `D-03` — *código é custo*, *subtração antes de adição*, *evidência acima de opinião* — e o fluxo de decodificação (`Clarificar → Evitar → Reduzir`, Gate A/B) viram regra sempre carregada em `.claude/rules/`, sem `paths:` |
| 04 | `ddl-guardrail-hook` | O **mecanismo** de guardrail: hook `PreToolUse` que casa a ferramenta por regex e **inspeciona o conteúdo**. O incidente do `notifications_hub_id_fkey` **escolhe** a regra; o teste a **prova** com o statement real como fixture — aquele DDL é recusado, aquele `SELECT` diagnóstico passa. Instalar no AmFlow é consequência reportada, nunca gated |
| 05 | `activation-notice` | Ativação de norma deixa de ser silenciosa: hook `InstructionsLoaded` anuncia **qual** arquivo entrou em contexto, **quando** e **por quê** (`load_reason`), somado a `SubagentStart` para agente e à expansão de skill. Em `PostCompact`, anuncia quais rules com `paths:` estavam ativas e **não voltaram** — a perda continua, mas deixa de ser silenciosa (`L-09`). É o instrumento que prova a `03` |

### Fase 3 — Guideline vira artefato

| # | Unidade | Responsabilidade |
|---|---|---|
| 09 | `guideline-manifest` | O que é uma guideline: manifesto, escopo declarado por `paths:`, e a fronteira escrita contra skill. A instância de prova usa o conteúdo normativo da `AmFlow:hub-front` como **material** — o artefato vive aqui, e a instalação lá é consequência |
| 10 | `guideline-registry` | Registry por projeto e a operação que liga e desliga uma guideline sem editar arquivo à mão |

### Fase 4 — O plano ganha porte, e o processo deixa de cobrar o mesmo de todos

| # | Unidade | Responsabilidade |
|---|---|---|
| 12 | `plan-size-field` | `plan_size: pequeno \| médio \| grande` no frontmatter, **declarado pelo humano**. O gate recusa o campo **vazio**, nunca um valor — recusar ausência é procedimental, recusar valor seria julgamento, e a norma proíbe teto de unidades por escrito |
| 13 | `plan-formats` | O que cada porte dispensa, na norma e no template. Pequeno sem `## Independência` e sem decomposição; médio com lista de tarefas; grande como hoje. Pequeno e médio **não ganham diretório** — pasta para um arquivo é custo puro. E um terceiro valor de `unit_type`: **`norma`**, cujo oráculo é estrutura válida **somada a aprovação humana registrada em campo** — fecha a `L-01` sem fingir que teste estrutural julga prosa |
| 14 | `derive-by-size` | O `derive` ramifica: **não roda** no pequeno, projeta **tarefas** na região de backlog no médio, cria estrutura e arquivo por unidade no grande |
| 15 | `size-instrumentation` | No fechamento, o script registra o porte **declarado** ao lado do resultado **real** — arquivos tocados, linhas alteradas, número de tarefas ou unidades. É o que transforma a métrica em medição em vez de palpite que envelhece |

### Fase 5 — O modelo vira plugin

| # | Unidade | Responsabilidade |
|---|---|---|
| 16 | `plugin-package` | Empacotamento como plugin Claude Code, e a operação que **materializa** as guidelines escolhidas em `.claude/rules/` do projeto que instala |
| 17 | `reconcile-consumers` | O mecanismo de verificação de versão entre o plugin e as cópias instaladas, e o **diff** contra o `dev-units` congelado do AmFlow — preparado e reportado, **não publicado**. Publicar em repositório público é ato humano |

### Fase 6 — O método ganha operadores

| # | Unidade | Responsabilidade |
|---|---|---|
| 18 | `reopen-agent-decision` | A norma registra que o gate dela mesma abriu, e as duas pendências que dependiam de agent fecham — a **decisão 18** (modelo por modo, hoje política operacional manual) e a **pendência 2**. Vem primeiro da fase: escrever unidade de agente enquanto a norma diz *"fora de escopo"* é contradição |
| 19 | `planner-agent` | Agente de planejamento — `model: opus`, `skills: [decode-and-code]`, escrita restrita a `docs/plan/**`. Cobre revisar e derivar como subagente, e planejar do zero como **fork** |
| 20 | `developer-agent` | Agente de execução — `model: sonnet`, `skills: [decode-and-code]`, escrita em código e teste, **sem `memory:`**. Cobre codar e testar |

### Fase 7 — O time ganha um canal

| # | Unidade | Responsabilidade |
|---|---|---|
| 21 | `huddle-log` | O `huddle.md`: formato de entrada com vocabulário fechado de **cinco** tipos, regra de despejo, os cinco gatilhos de escrita e a regra de momento — *no fecho do trabalho, e só o que continuou aberto*. Alcança o contrato de relatório dos três modos, não só o do `implement`, e **exige a linha de fecho mesmo quando não há entrada** — *"entradas novas no huddle: 0"* separa *conferi e não havia* de *nunca conferi*, que hoje são indistinguíveis (`L-08`). **Formaliza o que sobreviver ao uso do protótipo** escrito em 2026-08-22, em vez de desenhar às cegas |

**A `21` reabre o empacotamento da `16`, e é esperado.** Empacotar é operação idempotente —
reexecutá-la ao fechar a Fase 7 incorpora o `huddle.md` ao plugin sem reabrir nenhuma decisão da `16`.
O plugin que a Fase 5 entrega e o que a Fase 7 fecha são a mesma operação, rodada duas vezes.

**Fase própria, com uma unidade só, e por escolha.** O huddle não é camada de norma nem operador —
dobrá-lo na Fase 2 ou na 6 seria rotulá-lo errado, e rótulo errado aqui é o defeito que o plano
inteiro persegue. Plano separado custaria mais do que economiza: a norma diz que **dividir tem custo**,
e isto é uma unidade.

### Correções descobertas na execução — fora de fase, e é deliberado

Quatro unidades que não estavam previstas. Nasceram de lacunas abertas **durante** a execução da
Fase 1, a derivação da Fase 2 e a revisão da Fase 3, e por isso não pertencem a fase nenhuma:
encaixá-las numa já fechada seria rótulo errado, e o rótulo errado é o defeito que este plano
persegue.

| # | Unidade | Responsabilidade |
|---|---|---|
| 06 | `incremental-derive` | A `L-17`: o passo 1 do modo `derive` chamava `scaffold.aprovar` incondicionalmente e morria no prefixo numérico do plano já movido. O mecanismo foi corrigido em 2026-08-24 fora de unidade, por decisão do humano — esta unidade o **formaliza com teste declarado** e registra o comportamento na norma |
| 07 | `plan-situation` | A `L-18`: a situação projetada em `_planos.md` mede as unidades **derivadas**, não o plano, e leva a `concluído` a cada fronteira de fase em que todas as derivadas estão verificadas. Consequência medida: a região `planos` fica sem linha `em desenvolvimento`, e o check de concorrência do `review` passa a aprovar o que deveria sinalizar |
| 08 | `language-policy` | A `L-15`: a norma cita `language-policy.md` quatro vezes, uma delas vinculante, e `estudo-runtime-e-dependencias.md` como a evidência que a fundamenta — **os dois estão no AmFlow**. Migram desacoplados, e o `CLAUDE.md` perde as três frases que hoje duplicam a norma |
| 11 | `activation-audit` | A `L-27`: o que a validação por sessão provou não vira gate nem procedimento. O check estrutural que a `L-26` deixou como comentário passa a ser teste, e o procedimento das seis medições — hoje só nesta conversa — vira norma somada a um relatório que lê o log e diz o que carregou e por quê |

**O número segue a derivação, não a fase.** `numeracao.proxima_unidade` lê o disco e toma o próximo
livre — elas foram derivadas conforme apareceram e por isso são `06`, `07`, `08` e `11`. A
alternativa era deslocar as unidades **já derivadas** para comprar a propriedade cosmética de o
número subir junto com a fase, ao custo de 51 referências num plano aprovado. Recusada em 2026-08-24.

**Os números das fases ainda não derivadas são outra coisa, e esses se deslocam.** Eles são previsão,
e a previsão erra: a Fase 3 previa `06`/`07` e recebeu `09`/`10`. Cada derivação toma do disco os
números da fase que está derivando e empurra os provisórios das seguintes, para que **em qualquer
instante** um número nomeie uma unidade só (`D-17`). Nada disso toca unidade já derivada — é o oposto
do que foi recusado acima.

**Vinte e uma unidades, sete fases mais as correções fora de fase — e o plano não é pequeno.** Vale dizer sem rodeio: ele nasceu com
onze, a absorção do `B-01` acrescentou quatro, a mudança de repositório acrescentou a Fase 1, e a
revisão de 2026-08-22 dividiu a primeira unidade em duas, e a **execução** acrescentou quatro
correções que nenhum planejamento anteciparia. Cada fase segue entregando uma capacidade
completa, e três coisas continuam cortadas na redação — um verificador de invariantes de guideline (é
o `B-02` do backlog do AmFlow, e a norma diz para escrevê-lo na primeira divergência observada, não
numa data), a separação entre desacoplar e empacotar, e a migração das **outras seis skills
normativas** do AmFlow (`hub-env`, `security-testing`, `data-architecture`, `data-privacy-lgpd`,
`digital-twin-product`, `user-modeling`), que vira item de backlog. Migrar sete de uma vez é o exato
over-engineering que o plano combate; migrar uma prova o mecanismo e **mede o custo real** da migração.

**O que a mudança de repositório apagou.** Duas unidades perderam objeto e não estão acima: a
extração de três seções do `CLAUDE.md` de 458 linhas do AmFlow, que era metade da antiga
`principles-rule` e agora é limpeza daquele repositório, não trabalho deste; e a renomeação de
`dev-units` para `decode-and-code`, com as 164 ocorrências em 32 arquivos que a `L-03` mediu — aqui o
nome **nasce certo**. As duas viram item de backlog do AmFlow.

## Independência

**Entregando apenas este plano e parando, o sistema fica em estado válido:** as três camadas existem,
uma delas impõe de verdade, e o conjunto instala em outro projeto. Nada fica pela metade — e o AmFlow
segue operando com a cópia congelada do `dev-units` durante todo o percurso, sem depender de nenhuma
fase daqui para continuar funcionando.

**A dependência entre as camadas é sequencial e o objetivo é único:** a Fase 1 destrava tudo o que
vem depois, a Fase 3 empacota o que a Fase 2 cria, e a Fase 5 transporta o que a Fase 3 empacotou.
Guideline sem princípio é arquivo sem critério; plugin sem guideline é invólucro vazio. Pela tabela de
*Avaliação de escopo* da norma, dependência sequencial com objetivo único é **fase, não plano
separado**.

### A Fase 4 é a exceção, e a norma manda registrá-la

O `B-01` do backlog do AmFlow — tipos de plano, para que correção de oito linhas não pague
estrutura de quinze unidades — **passa no teste de independência isoladamente**. Ele muda o *processo*
(o que cada porte dispensa, e o gate); as outras fases mudam a *norma* (o que o código deve obedecer).
Pelo teste, seriam dois planos, e **versões anteriores deste documento assim o declararam**.

**A decisão do humano em 2026-08-22 foi absorvê-lo, e a norma prevê exatamente este caso:** *"quando a
avaliação sinaliza divisão e a decisão é não dividir, o plano registra o porquê"*. O porquê:

> **O modelo que viaja como plugin tem que ser o modelo.** A Fase 5 empacota o `decode-and-code` para
> instalação em qualquer projeto. Se o porte de plano chegar depois dela, o plugin entrega na v1 um
> formato único que o próprio projeto já abandonou — e quem instalar herda a versão que nós deixamos
> para trás. É a mesma classe de defeito que a divergência de 2026-08-01 com o `AmFlowPlugins`
> produziu, e que a `16` existe para fechar.

**O custo fica dito, não escondido:** o plano cresceu de doze para dezessete unidades. O risco que o
teste de independência protege — dois trabalhos alterando decisões um do outro enquanto correm —
**não se materializa aqui**, porque a Fase 4 não depende de nenhuma outra e nenhuma depende dela. A
posição antes da Fase 5 é escolha de completude do pacote, não acoplamento.

**Concorrência:** neste repositório, `_planos.md` está vazio — este é o primeiro plano a entrar em
desenvolvimento aqui, e não há concorrência possível. No AmFlow, os seis planos existentes
(`0001`–`0006`) estão `concluído` — também sem concorrência lá. O `AmFlow:module-install-update.md`
está em `builder/` com `status: stable` e sem `plan_id`, fora da tabela; não é concorrência, mas é um
plano do mesmo core não derivado, e vale saber que está lá.

## Direção de solução

### Não inventar ativação — a convergência já resolveu

Quatro ferramentas independentes chegaram na mesma forma: **diretório de arquivos pequenos, cada um
com frontmatter declarando escopo por glob**.

| Player | Mecanismo | O que se aproveita |
|---|---|---|
| Cursor | `.cursor/rules/*.mdc` — `description`, `globs`, `alwaysApply`; quatro modos de ativação | A taxonomia: *always* · *auto-attached* · *agent-requested* · *manual* |
| GitHub Copilot | `.github/instructions/*.instructions.md` — `applyTo` + `excludeAgent` | Guideline que vale para quem escreve e não para quem revisa |
| **Claude Code** | `.claude/rules/*.md` — frontmatter `paths:`; sem `paths` carrega sempre | **É nativo, está aqui, e não usamos** |
| ESLint flat config | Array de objetos com `files` glob, composto por shareable configs | Composição ordenada: depois sobrescreve antes |

O mapeamento com o mecanismo nativo é exato: *princípio* é regra sem `paths`, *guideline* é regra com
`paths`. Não há carregamento a construir.

### Princípio e guideline separam-se por um teste

> **Uma equipe competente pode rejeitar isso e ainda estar fazendo trabalho bom?**
> Não → princípio. Sim → guideline.

`Código é custo` e `subtração antes de adição` não são rejeitáveis — princípios. `Clean architecture`
e `mobile first` são escolhas técnicas legítimas de recusar — guidelines. A distinção operacional:
**princípio é sobre como decidir; guideline é sobre o que decidir.**

A consequência é o que torna o plugin portátil. Princípio embutido é norma que viaja; escolha técnica
embutida é arquitetura imposta a quem instalar — e aí o plugin não é portátil, é opinativo.

### Skill e guideline separam-se por outro teste

> **Skill é invocada; guideline é ativada.**

Skill responde *como fazer X* — é procedimento, tem passos, e alguém precisa pedir. Guideline responde
*o que vale quando eu toco Y* — é norma, tem critério, e entra sozinha pelo caminho do arquivo.

Das doze skills do repositório, cinco são procedimento e continuam skills: `dev-units`,
`frontmatter-check`, `backlog`, `backlog-worker` e `workflow-runner`. As outras sete são norma com
escopo, vestidas de skill.

**E é exatamente aí que nasce a oscilação.** A `AmFlow:hub-front`
descreve-se como *"padrões, primitivos e checklist de qualidade"* do front-end do Hub — mas só entra em
jogo se alguém a invocar. Editando `hub/app/(dashboard)/page.tsx` sem invocá-la, os padrões dela
simplesmente não estão no contexto, e o resultado sai sem eles. Como guideline com
`paths: ["hub/app/**"]`, ela entra sempre que o arquivo é tocado. A inconsistência não vem de o modelo
esquecer a norma: vem de a norma não ter sido carregada.

### O pipeline completo, na instância que tem incidente registrado

```
princípio   o repositório é a verdade sobre o banco
guideline   toda mudança de schema entra por migration
guardrail   DDL em ambiente remoto é recusado    verificável por inspeção do statement
```

A unidade `04` percorre esse pipeline inteiro, e é por isso que vem cedo: um hook funcionando prova
mais sobre a camada do que qualquer página de norma sobre hooks. Inspecionar conteúdo — e não apenas
caminho ou nome de ferramenta — é deliberado: é o que prova a capacidade real do mecanismo, já que
`SELECT` diagnóstico é permitido e DDL não.

> **Ancorar no statement, nunca em substring.** Casar `create` solto no texto daria falso positivo em
> qualquer `SELECT` que contenha a palavra. É a mesma classe de defeito que a `L-02` do plano
> `AmFlow:0006` documenta, onde um
> marcador citado em prosa foi tratado como marcador real e corrompeu o arquivo.

> **Guardrail é específico do projeto, por definição** — a norma dá *"nunca `process.env` direto"* como
> exemplo. A Fase 5 empacota o **mecanismo** de guardrail, nunca esta instância: nenhum projeto que
> instale o plugin herda uma regra sobre Supabase.

### Ativação silenciosa é o modo de falha da própria camada

Medido em **2026-08-22**, na doc de memória e de hooks do Claude Code. O mecanismo que a Fase 2 adota
carrega duas propriedades que ninguém observa sem instrumento:

| Propriedade medida | Consequência |
|---|---|
| *"Path-scoped rules trigger when Claude reads files matching the pattern, **not on every tool use**"* | A guideline entra na **leitura**, não na escrita. Arquivo novo criado sem leitura prévia não ativa a norma que deveria governá-lo — e é justamente onde a `hub-front` mais valeria |
| Após compactação, rule com `paths:` *"reload as Claude reads files they apply to"* — só na próxima leitura que casar | A camada de guideline tem a sua própria versão do defeito que o plano existe para tratar: degradação quando o contexto enche |

Nos dois casos a falha é **silenciosa e indistinguível do sucesso**: uma guideline que não carregou
produz o mesmo sintoma de uma guideline que carregou e foi ignorada. É a classe de defeito que o
`digital-twin-planner` já sofre — o agente opera acreditando ter contexto que não tem, e ninguém
percebe porque o resultado é apenas *pior*, nunca *quebrado*.

**O evento existe, e a doc o endossa para exatamente este uso:** *"Use the `InstructionsLoaded` hook to
log exactly which instruction files are loaded, when they load, and why. This is useful for debugging
path-specific rules."* Ele expõe `load_reason` — `session_start`, `path_glob_match`, `compact`,
`nested_traversal`, `include` — que é o *por quê* de cada carregamento.

**Anunciar não é carregar.** A opção C da tabela acima foi recusada como mecanismo de carregamento, e
com razão: reimplementa `paths:`. Como mecanismo de **anúncio** não tem concorrente, e não duplica
conteúdo nenhum — o hook nomeia o arquivo, nunca copia o texto. É monitoramento puro por construção:
o evento *"cannot block instruction loading"*, o que o mantém categoricamente distinto da `04`, que impõe.

> **Skill e agente entram por requisito declarado, não por lacuna medida.** Ambos já renderizam como
> tool call. Ficam no escopo porque o pedido é explícito, e o custo é marginal — `SubagentStart`
> entrega stderr ao usuário, e a expansão de skill aceita `systemMessage`. A lacuna **medida** é a
> rule com `paths:`, que não tem nenhuma superfície visível hoje.

> **O primeiro passo da unidade é um spike, e é deliberado.** A página de hooks se contradiz: a
> tabela-resumo marca `InstructionsLoaded` como *"N/A (ignored)"*, e a seção detalhada afirma que
> *"`systemMessage` and `terminalSequence` work; others ignored"*. Reconciliam se a tabela se referir
> só a stdout/stderr — que é como está titulada —, mas isso foi lido em doc, não em execução. Se
> `systemMessage` não chegar ao usuário, o canal muda antes de a unidade ser escrita, não depois.

**Por que não a regra de dependência da arquitetura declarada, que é a violação maior.** Porque ela
reprovaria `hub/lib/catalog.ts`, `licenses.ts` e `queries.ts` na primeira execução. **Guardrail que
falha no código existente é guardrail que ninguém liga** — vira exatamente o obstáculo a contornar que
a norma já avisa em *O que a avaliação não faz*. Ele entra depois da conformação, nunca antes dela — e
a conformação é do AmFlow, endereçada pelo plano `describe-as-built` daquele repositório.

### O porte do plano, e o único artefato novo que ele obriga

Hoje o modelo tem **uma** forma de decompor: a unidade — arquivo próprio, frontmatter, `state` e
`verified_at` projetados por script, gate de entrada e de saída, cold-start. O porte médio pede lista
de tarefas, que não é isso.

> **Tarefa é uma linha na região de backlog do próprio plano.** Sem arquivo, sem frontmatter, sem
> estado projetado, sem gate individual.

Não é economia preguiçosa: o médio executa **na mesma sessão**, então cold-start por tarefa não teria
o que verificar. O gate de saída aplica-se ao **plano** — o teste declarado passa, o plano fecha. E a
unidade continua sendo o único artefato que **promete** cold-start, que a norma define como *o critério
de suficiência da unidade* (`:127`). Nome diferente é o que impede alguém de assumir uma garantia que
a tarefa não dá — e rótulo errado é o defeito que este plano inteiro persegue.

| | Pequeno | Médio | Grande |
|---|---|---|---|
| `## Independência` | dispensa — não há o que dividir | curta | obrigatória |
| Decomposição | nenhuma | tarefas (linhas no plano) | fases → unidades (arquivos) |
| `derive` | **não roda** | projeta tarefas na região de backlog | cria estrutura + arquivo por unidade |
| Onde o plano vive | `<core>/<NNNN>-<nome>.md` | idem | `<core>/<NNNN>-<nome>/` |
| Execução | mesma sessão | mesma sessão | cold-start, uma unidade por vez |
| Gate de saída | teste do fix | teste do plano | teste por unidade |
| Corpo | Objetivo · Solução · Oráculo | + tarefas · Decisões e Lacunas se houver | tudo, como hoje |

**O humano declara o porte, e isso resolve o problema mais difícil.** Sem classificação automática, o
modelo não precisa acertar o tamanho antes de entender o trabalho, e o gate deixa de competir com a
norma: ele recusa **campo vazio**, nunca um valor. Recusar *"você não declarou"* é procedimental;
recusar *"seu plano é grande demais"* seria julgamento, e a norma proíbe teto de unidades com
argumento próprio — *"um número sem base empírica competiria com o teste de independência e dividiria
planos coesos"*.

> **A métrica é hipótese, não achado — e por isso a `11` existe.** Os critérios de porte vieram do uso
> diário, não de medição. Declaração sem verificação envelhece como opinião: a instrumentação grava o
> porte declarado ao lado do resultado real, e depois de ~10 planos existe a tabela que diz se
> *pequeno* ficou pequeno, ou se a declaração deriva sistematicamente para baixo. O ajuste dos
> critérios passa a vir de dado. Sem isso, a única coisa que se pode fazer com a métrica é acreditar
> nela.

### O plugin não pode enviar regras — e é isso que decide o desenho

Verificado na referência de plugins: plugin do Claude Code empacota skills, commands, agents, hooks,
workflows, MCP/LSP, output styles e `bin/` — *"Plugins contribute context through skills, agents, and
hooks rather than CLAUDE.md"*. **Não envia `.claude/rules/`.**

Três saídas, e a escolhida:

| | Caminho | Veredito |
|---|---|---|
| A | O plugin carrega as guidelines como dados; uma operação **materializa** as escolhidas em `.claude/rules/` do projeto | **Adotado** — ativação nativa, custo zero, arquivo legível e versionado no projeto |
| B | Cada guideline vira skill, e o modelo decide carregar pela `description` | **Recusado** — ativação por julgamento do modelo é a variância que o plano existe para remover. Guideline de front-end que carrega *às vezes* é pior que nenhuma |
| C | Hook injeta a norma conforme o path tocado | Reimplementa `paths:`. É o caminho certo para o **guardrail**, não para a norma |

**Materializar é cópia versionada, não symlink.** `.claude/rules/` aceita symlink, e ele resolveria a
drift de graça — mas perde em três pontos que importam mais: funciona em toda sessão sem ressalva a
lembrar; a cópia fica versionada no projeto, então um revisor vê **em qualquer commit qual texto
estava ativo**, propriedade de auditoria que symlink não dá; e a drift fecha pela verificação de
versão, que a unidade `17` constrói de qualquer maneira. A ressalva do Cowork sobre symlink existe,
mas é sobre *user-scope* (`~/.claude/rules/`) e as guidelines vão para *project-scope* — ela estreita
o risco, não decide a questão. A decisão é por mérito.

**Materializar não pode ser automático.** Hook de `SessionStart` que escreve no projeto do usuário a
cada sessão é efeito colateral silencioso. A operação é explícita; o que pode ser automático é o
aviso de que a cópia está fora de sincronia.

## Restrições conhecidas

| Restrição | Onde |
|---|---|
| Plugin não empacota `.claude/rules/` — a materialização é obrigatória, não conveniência | Referência de plugins do Claude Code |
| Em sessões **Cowork**, rule por symlink apontando para fora do working directory é ignorada — restrição de *user-scope*, que estreita mas não decide a escolha por cópia | Doc de memória do Claude Code, seção de symlinks |
| Hook de `PreToolUse` roda em toda chamada de ferramenta: precisa ser barato, e falha fechada trava o trabalho | `.claude/settings.json` |
| `InstructionsLoaded` é monitoramento puro — não bloqueia nem altera carregamento, e descarta `systemMessage`, `continue` **e** o exit code: nenhum canal alcança o usuário. `PostCompact` descarta os mesmos dois campos, mas seu exit code 2 mostra stderr sem bloquear nada — é o canal real dos dois. Corrige a leitura original desta linha; ver `L-25` | `code.claude.com/docs/en/hooks`, medido em 2026-08-24 |
| Rule com `paths:` ativa na **leitura** de arquivo que casa o glob, não na escrita nem em toda chamada de ferramenta | Doc de memória, *Path-specific rules* |
| A unidade `17` alcança um **repositório público** — efeito externo e irreversível. Entrega diff e mecanismo; publicar é ato humano | Precedente da `AmFlow:0003-05` |
| A suíte migrada roda 158 testes, **25 vermelhos** por fixture apontando para arquivo do AmFlow. O gate roda **por arquivo declarado**, não pela suíte — então `01` e `02` fecham normalmente com o resto vermelho | Medido em 2026-08-22 com `./scripts/test-python.sh` |
| Nenhuma unidade escreve no **AmFlow**. O incidente de lá escolhe a regra, o fixture a prova aqui, e instalar é consequência reportada — item do backlog daquele repositório | Decidido na revisão de 2026-08-22 |
| Python 3.10 (versão do Cowork), stdlib pura | `AmFlow:.claude/CLAUDE.md` |
| `state` e `verified_at` nunca se editam à mão — são projetados por script | Norma, *Os dois gates* |

> **A Fase 5 move arquivos que as fases anteriores criam**, e é por isso que vem tarde: empacotar
> antes de a norma existir seria empacotar invólucro.

### Agente: papel e processo, nunca a norma

A norma **não declara agente inútil.** Ela põe um gate com duas condições — *"Agent só se justifica
onde há julgamento somado a pesquisa ampla, **e só depois de a skill existir**"* ([:724](../../system/modelo-dev-units.md)) —
e ela mesma escreve o desbloqueio: *"se for requisito, e não conveniência, **reabre a decisão sobre
agents**"* (:843). A skill existe desde 2026-07-26, e a segunda condição foi declarada pelo humano em
2026-08-22, a partir de uso diário. A unidade `18` registra que o gate abriu; não reverte julgamento
nenhum.

**Benchmark medido em 2026-08-22**, sobre definições em disco:

| Fonte | Linhas | Tools | Model | Forma |
|---|---|---|---|---|
| Anthropic `feature-dev` ×3 | **34–51** | read-only, sem `Write`/`Edit` | `sonnet` | persona → processo numerado → formato de saída |
| Anthropic `agent-creator` | 176 | `Write, Read` | `sonnet` | é a norma de como criar agentes |
| Vercel ×3 | **302–935** | não declara | não declara | manual de referência: árvores de decisão e matrizes |
| AmFlow `digital-twin-planner` | 137 | leitura e escrita amplas | `opus` | frontmatter híbrido, nativo + AmFlow |

**São duas filosofias, e a escolha não é de gosto.** A Anthropic trata agente como *papel e processo*,
curtíssimo, com o conhecimento no código que o agente lê; a Vercel embute a expertise no prompt.
**Adotada a forma Anthropic:** agente que embute a norma cria uma segunda fonte para o mesmo fato — o
drift que este plano existe para combater. O agente carrega papel e processo; a norma continua na
norma, e o campo `skills:` faz a ponte.

Três padrões da Anthropic entram junto: descrição com blocos `<example>`, decisão em vez de menu de
opções (*"make confident architectural choices rather than presenting multiple options"*), e
**2–3 instâncias do mesmo agente em paralelo com focos distintos**, sintetizadas depois — que é o que
o `feature-dev` faz e o que mitiga o `B-07`, a revisão sem separação de funções que este plano sofreu.

**Uma divergência consciente do benchmark:** os três agentes da Anthropic são read-only, e o nosso
planejador não pode ser — `derive` escreve arquivos de unidade. A restrição vira escopo de caminho
(`docs/plan/**`), não ausência de escrita.

### O `huddle` é fila, não fonte

As três camadas normativas resolvem o que **já foi decidido**. Nada no projeto guarda o que ainda não
foi — a observação que uma sessão faz e a seguinte não herda, a pergunta que se responde por conta
própria porque perguntar custaria uma interrupção, a contradição entre duas fontes que se contorna em
silêncio. Isso não desaparece: reaparece como decisão tomada de novo, cada vez de um jeito.

**A propriedade que faz funcionar: nada ali é autoritativo enquanto está ali.** Uma entrada nasce
aberta, é discutida com o humano, e quando vira verdade **sai** — para a norma, para uma guideline, ou
para o `## Decisões` de um plano. Se não virar, é descartada com o motivo escrito. Enquanto for
estágio, o huddle nunca compete com a norma, e nenhuma anotação meio-formada é lida depois como
convenção estabelecida.

Vocabulário fechado de cinco tipos, cada um pedindo um tipo diferente de resposta:

| Tipo | O que é |
|---|---|
| `pergunta` | Decidi X assumindo Y — Y está certo? |
| `divergência` | Duas fontes do projeto se contradizem, e a execução contornou |
| `padrão` | Regularidade que uma sessão sozinha não revela |
| `revisitar` | Alternativa rejeitada cuja premissa pode ter mudado |
| `observação` | Algo notado que ainda não virou afirmação — o tipo mais solto, e deliberadamente |

**A peneira fica na saída, não na entrada.** Fila não filtra o que entra; filtra o que sai. O critério
de valor — *isto muda alguma decisão?* — vale na conversa, com as duas partes olhando, não no momento
de escrever.

> **A razão é empírica, e o caso está registrado neste plano.** A divergência entre arquitetura
> declarada e real começou como observação solta — *"o `hub/` não segue isso"*. Foi filtrada na
> entrada: virou conclusão (*"logo, é escolha deliberada"*) e seguiu adiante errada. Só se corrigiu
> porque o humano tropeçou nela. **Filtrar cedo custou mais do que teria custado registrar cru.**

**Critério de saúde:** um arquivo onde nada fecha só cresce. Entrada resolvida sai na mesma sessão em
que fecha, deixando uma linha com a data e o destino. O arquivo tende ao tamanho do que está
genuinamente em aberto — que é o tamanho certo, e é a lição que o `CLAUDE.md` de 458 linhas ensina.

#### Gatilho de escrita: evento, nunca impressão

*"Escreva quando notar algo relevante"* faria uma sessão registrar cinco entradas e outra nenhuma — a
mesma variância que o plano trata, num arquivo novo. Os gatilhos são observáveis:

| Gatilho | Tipo |
|---|---|
| O executor decidiu algo que o humano não decidiu — declarou premissa e seguiu | `pergunta` |
| Duas fontes do projeto discordam | `divergência` |
| Algo foi contornado em vez de corrigido, por estar fora de escopo | `divergência` |
| Uma alternativa foi rejeitada por premissa que pode mudar | `revisitar` |
| **O humano corrigiu o modelo** | `padrão` |
| Algo foi notado e ainda não virou afirmação | `observação` |

#### Momento: no fecho do trabalho, e só o que continuou aberto

Não no instante em que acontece — metade se resolve dentro da própria sessão. A `D-01` deste plano
nasceu premissa do autor e foi **resolvida pelo humano horas depois**; escrita na hora, teria sido
entrada natimorta.

> **O que resolveu vai para o lugar de coisa resolvida** — decisão de plano, norma, guideline — e nunca
> toca o huddle. O huddle guarda o que **não** fechou. É a mesma propriedade de fila, aplicada ao tempo.

E uma linha no fecho do relatório avisando que há entrada nova: sem isso, o arquivo depende de alguém
lembrar de olhar.

#### A rotina fica de fora do plugin

A conversa recorrente pode ser agendada, e vale a disciplina de **silenciar quando não há nada aberto**
— rotina que produz reunião sem pauta ensina a ignorar a rotina.

Mas o agendamento é configuração de máquina, não artefato de repositório: **o huddle viaja no plugin, a
rotina não.** Quem instalar decide se quer, e com que frequência.

> **A assimetria precisa estar escrita.** O humano aprende lendo; o modelo só aprende se a resolução
> for escrita, porque não carrega nada entre sessões que não esteja em arquivo. A consequência prática:
> o tipo de entrada mais valioso que **o humano** escreve não é instrução, é **retrospectiva** — *"aquela
> escolha envelheceu mal, e o motivo foi este"*. Hoje isso não tem onde morar, e evapora.

> **O campo `skills:` existe e ninguém usa.** A doc o define como *"skills to preload into context at
> startup"* — é exatamente "o agente já chega sabendo usar a skill". Medido em 2026-08-22: nenhum
> agente da Anthropic, da Vercel ou do próprio AmFlow o declara. Pior, o
> `AmFlow:digital-twin-planner` lista
> quatro skills em `dependencies:` — campo do AmFlow que o Claude Code **ignora**. Ele acredita
> carregar quatro skills e não carrega nenhuma.

## Validação de ponta a ponta

O gate de cada unidade roda o teste que ela declara. Isso prova a unidade, **não a fase** — e três
afirmações centrais das Fases 1 e 2 não tinham prova nenhuma até serem medidas em **2026-08-24**,
fora do gate.

| # | O que estava sem prova | Como foi medido | Resultado |
|---|---|---|---|
| 1 | *"Os scripts não assumem caminho fixo"* — o teste da `01` usa mock em `_config_path` e `repo_root` | `config.json` **real**, `plan_root: "planejamento"`, core `motor` que não existe aqui, ciclo `aprovar → numerar → projetar` em tempdir | Passa. O plano é movido e registrado sob o alvo novo, e **nada** é criado em `docs/plan/` do repositório |
| 2 | Se a suíte depende de estado acumulado nesta cópia de trabalho | Clone novo, sem `__pycache__` nem estado de sessão | Passa — 256 rodados, 0 vermelhos |
| 3 | **Se a rule da `03` realmente carrega** — `test_rules.py` prova que o arquivo é bem formado, nunca que o Claude Code o usa | Sessão nova neste repositório, lendo o log que a `05` escreve | Passa. `principles.md` aparece com `load_reason=session_start` |

| 4 | **Se rule com `paths:` fica fora do carregamento inicial** — nunca medido; se carregasse sempre, o escopo não estaria evitando custo nenhum | Sessão nova, log lido **antes** de qualquer `.py` ser tocado | Passa. Só as três sem escopo aparecem; `scripts.md` **não** está lá |
| 5 | **Se o matcher do Claude Code concorda com o `pathlib`** — o `lint_guideline` da `09` afirma que o glob casa disco, e a ferramenta usa matcher próprio, cuja semântica ninguém tinha medido | Mesma sessão, lendo um `.py`, e o log de novo | Passa. `scripts.md` aparece com `load_reason=path_glob_match` |

| 6 | **Se `desligar` desliga** — a `10` movia a guideline para `.claude/rules/_off/` e `listar()` reportava `desligada`; que ela **saía de contexto** nunca foi medido | Guideline desligada, sessão nova, leitura de um `.py`, log conferido | **Reprovou, e o reteste passou.** Com a guideline em `.claude/rules/_off/`, a leitura de um `.py` produziu entrada `path_glob_match` — o matcher recursa no subdiretório. Corrigido para `.claude/rules-off/`, irmão: a **mesma** leitura passou a não produzir entrada nenhuma. Comparação controlada de três estados — ligada produz entrada, em subdiretório produz entrada, em diretório irmão não produz |
> **A `03` e a `05` se provam mutuamente, e é o que a `05` foi escrita para fazer.** Até esta medição,
> a camada de princípio era um arquivo bem formado que ninguém tinha visto carregar, e o instrumento
> era um mecanismo sondado só por subprocesso. O dispatch real do `PreToolUse` já estava provado por
> acidente — o hook da `04` bloqueou uma chamada da própria sessão de revisão.

**O que a medição 3 mostrou além do que se pedia:** o instrumento vê **três fontes de instrução**
carregando juntas — o `CLAUDE.md` do projeto, o `principles.md` e o `CLAUDE.md` **global**. É a
condição que a `L-05` esperava para deixar de ser impressão, e agora é observável.

**O que continua sem prova, e é honesto listar:** o `PostCompact` numa compactação real, que não se
força — é o único ramo do instrumento ainda sem medição; e se o modelo **obedece** aos princípios e
à guideline depois de carregá-los, que é a `L-01` e nenhum campo transforma em oráculo.

> **As três camadas estão provadas vivas.** Princípio carrega em toda sessão; guardrail recusa no
> canal certo e libera nos outros; guideline entra **só** quando o arquivo do escopo é tocado.
> Nenhuma das três era mais que estrutura validada antes destas medições.

## Oráculo

Cada unidade declara o seu, e as vinte e uma dividem-se em duas naturezas:

| Natureza | Unidades | Oráculo |
|---|---|---|
| **Comportamento** | `01`, `02`, `04`, `05`, `06`, `07`, `10`, `11`, `12`, `14`, `15`, `17`, `21` | Teste real. O hook recusa o caso proibido e deixa passar o permitido; o registry liga e desliga; a skill opera com um alvo que não é `docs/plan/`; a reconciliação detecta divergência entre as duas cópias. Para a `12`: plano sem `plan_size` é recusado, plano com porte declarado passa. Para a `14`: pequeno não deriva, médio projeta tarefa, grande cria arquivo de unidade. Para a `15`: fechar um plano grava a linha com declarado e real. Para a `05`: payload de rule que casa o glob produz anúncio nomeando arquivo e `load_reason`; payload fora do escopo produz silêncio; e payload de `PostCompact` nomeia o que não voltou. Para a `21`: entrada com tipo fora do vocabulário é recusada, relatório sem a linha de fecho é recusado mesmo com zero entradas, e **entrada marcada como fechada não permanece no arquivo** — a regra de despejo é o invariante, e é mecanicamente verificável |
| **Estrutura** | `03`, `08`, `09`, `13`, `16`, `18`, `19`, `20` | Verificador dos invariantes do artefato — o frontmatter valida, o glob de `paths:` compila e casa o que promete, o manifesto resolve, e o `CLAUDE.md` perde exatamente o manifesto resolve. Para a `13`: os três portes validam, o pequeno **não** carrega `## Independência` nem região de backlog, e unidade `unit_type: norma` sem campo de aprovação não transiciona. Para a `16`: o `plugin.json` resolve, e nenhum componente empacotado referencia caminho do projeto que o produziu. Para `19` e `20`: o frontmatter usa **apenas campos nativos**, o `skills:` nomeia skill que existe, o `model:` é o que a norma manda por modo, e o `tools:` não concede escrita fora do escopo declarado — este último é o que impede o planejador de tocar código |

**Isto é o `B-01` acontecendo dentro deste plano, e está registrado como a `L-01`.** Unidade cujo
entregável é conteúdo normativo não tem contra o que declarar `test:` — foi assim que o plano
`skill-modules` ganhou duas fases que existiam pelo gate e não pelo produto. A saída adotada aqui é
oráculo estrutural: verifica os invariantes do artefato, não a qualidade da prosa. É honesto sobre o
que prova, e não inventa uma fase para ter o que testar.

## Decisões

| # | Decisão | Estado |
|---|---|---|
| D-01 | **Clean architecture ocupa o slot de guideline no plugin, e está ligada no AmFlow.** As duas coisas são compatíveis: *guideline* diz **escopo de validade**, não opcionalidade. No plugin ela é ligável, porque quem instala não deve herdar a decisão arquitetural do AmFlow; aqui é vinculante, porque está registrada em `docs/mvp/` e o invariante nº 4 a sustenta | **Confirmada em 2026-08-21.** A formulação anterior — *"princípio ou guideline"* — era a pergunta errada, e apoiava-se num argumento inválido: inferir que a arquitetura fora rejeitada a partir de o código não a seguir. O `grep` mostrou o contrário |
| D-02 | **O primeiro guardrail em hook entra como unidade `04`, não como prova de conceito fora do plano.** Entra cedo justamente para valer como prova cedo, com o custo de uma unidade em vez do de um plano. **Só a Fase 1 vem antes**, e por necessidade mecânica: sem suíte verde nenhuma unidade passa pelo gate de saída | Adotada |
| D-03 | **Três princípios, e a lista está fechada:** *código é custo* · *subtração antes de adição* · *evidência acima de opinião*. Nenhum é rejeitável por equipe competente, que é o teste | **Aprovada em 2026-08-22.** A formulação anterior tinha quatro e adiava a decisão para dentro da unidade — o que colidia com o gate de saída: unidade que termina esperando aprovação não tem contra o que declarar teste. *Menor solução que resolve vence* foi **cortada por redundância** com *subtração antes de adição*: duas fontes para o mesmo fato é o drift que este plano persegue, e cortar aqui é o próprio princípio aplicado a si mesmo |
| D-04 | **A revisão de um plano escrito nesta mesma sessão roda de novo em sessão fria.** Quem escreveu e quem revisa foram o mesmo contexto — é o `B-07` do backlog, sem separação de funções | Adotada como prática, não como unidade. Não há solução estrutural num projeto de um dono; o que existe é barato e já foi provado aqui: as 15 unidades do `0002` rodaram em sessões sem contexto prévio, e funcionou |
| D-05 | **O planejador cobre planejar, revisar e derivar — mas planejar do zero é `fork`, não subagente.** A doc lista *"the task needs frequent back-and-forth with you"* entre os casos em que subagente é a ferramenta errada, e escrever um plano do zero é exatamente isso. `fork` herda a conversa inteira e serve; subagente comum começa limpo e não serviria | Adotada. O escopo pedido — planejar, revisar, derivar — é entregue inteiro; muda o **mecanismo** de invocação de um dos três, não o alcance |
| D-06 | **O agente de desenvolvimento não declara `memory:`.** Memória entre execuções faria o agente chegar com contexto acumulado — e aí a unidade deixa de precisar ser autossuficiente | O cold-start é o **critério de suficiência da unidade** (norma, :127). Um agente que lembra corrói o teste em silêncio: a unidade passa a funcionar por memória, não por estar completa, e a insuficiência só aparece quando outra pessoa a executa |
| D-07 | **Guardrail fica no projeto, não no frontmatter do agente.** O campo `hooks:` existe e permite ao agente carregar hooks próprios | Recusado pela mesma razão que a norma não entra no prompt: guardrail declarado nos dois lugares é duas fontes para o mesmo fato. Os hooks da Fase 1 valem para quem quer que edite, agente ou não |
| D-08 | **O `huddle.md` não é carregado automaticamente** — nem como rule, nem por `skills:`, nem por import. É aberto quando a conversa acontece | Carregá-lo faria dele mais uma coisa que o modelo lê e tenta seguir, com entradas **abertas** competindo com norma decidida. É o defeito que a Fase 1 existe para desfazer, reintroduzido pela porta dos fundos |
| D-09 | **O nome é `huddle`** — o arquivo é a pauta, o huddle é a conversa | Descartados: `ledger` (registro autoritativo — diz o oposto do que é), `notebook`/`journal` (sugerem acúmulo sem fechamento), `inbox` (colide com `docs/plan/_inbox/`), `loop`/`sync` (colidem com skill nativa e com comando do worker), `bench` (colide com *benchmark*), `pauta` (preciso, mas pt-BR não viaja no plugin) |
| D-10 | **O método é desenvolvido em repositório próprio, e o AmFlow vira campo de prova.** Os scripts e testes do `dev-units` migraram — 1300 e 2428 linhas, evidência de 15 de 15 unidades em cold-start; `SKILL.md`, norma, princípios e templates nascem aqui | **Decidida em 2026-08-22.** Reescrever do zero jogaria fora as correções dos planos `0005` e `0006` para reganhar bugs já resolvidos; forkar inteiro carregaria as premissas do AmFlow que depois teriam de sair uma a uma. A divisão é a mesma que a norma já traça — **o determinismo migra, a camada normativa nasce nova**. O `dev-units` do AmFlow congelou no mesmo dia: duas cópias editáveis é a condição exata que produziu a divergência de 2026-08-01 |
| D-11 | **A configuração dos scripts vive em `config.json`, em caminho convencional dentro da skill, com defaults embutidos** | **Decidida na revisão de 2026-08-22**, porque a `01` a exigia e a norma manda que decisão de desenho esteja no plano, não seja descoberta em execução. Env var não é versionável e some entre máquinas; argumento de linha de comando espalha a mesma decisão por chamada. Arquivo declarativo e versionado é o padrão que o projeto já usa em `module.json` e `plugin.json` |
| D-12 | **A derivação é incremental: a Fase 1 primeiro, o resto depois que ela fechar** | **Decidida na derivação de 2026-08-23.** A `01` reescreve a norma, e as unidades `03` em diante a citam em *Normas aplicáveis* — derivar quinze contra um documento prestes a mudar é retrabalho garantido. `numeracao.proxima_unidade` lê o disco e continua de onde parou, então o derive incremental é suportado sem nada novo. **Custo aceito:** `backlog._montar_rodape` sempre imprime "N de N derivadas", então o backlog dirá "2 de 2" com quinze unidades faltando |
| D-13 | **O ramo `.ts`/`npx vitest`/`hub/` sai de `verificacao.py`, substituído pelo mapa `runners` do `config.json`** | Decidida na derivação de 2026-08-23, ao fatiar a `01`. É instância do AmFlow dentro do mecanismo — invariante 2 do `CLAUDE.md`. Torná-lo configurável em vez de removê-lo seria configurabilidade para um caso que não existe aqui; o mapa `runners` preserva o mecanismo e deixa a instância para quem instalar. **Sai a função, fica a regex** — corrigido em 2026-08-23, antes da execução: `_comando_typescript` é instância e sai junto com a classe `TestComandoTypescript` que a cobre; `_VITEST_SKIPPED_RE` é leitura de saída de runner e **fica**, porque quem declarar um runner `.ts` no mapa continua precisando dela. Sem essa distinção por escrito, um executor em cold-start leva as duas e derruba quatro testes verdes com medição de 2026-08-12 por trás |
| D-14 | **`tests/test_deprecacao.py` é removido, não reapontado** | Decidida na derivação de 2026-08-23. Ele verifica que `plan-dev-units` e `digital-twin-product` deixaram de se citar — nenhum dos dois existiu neste repositório. Não é fixture errada, é uma unidade do AmFlow (`0002-15`) inteira sem objeto aqui. Reapontar exigiria inventar o que ele verifica |
| D-15 | **A aprovação deste plano é de 2026-08-24, e o registro anterior era efeito colateral do `derive`** | **Ratificada pelo humano em 2026-08-24.** O commit `693f18e` (2026-08-23) carimbou `status: approved`, registrou a linha em `_planos.md` e derivou a Fase 1 sem que a etapa 3 tivesse ocorrido — não por decisão de ninguém, mas porque `scaffold.aprovar` grava o campo como parte do `derive` (`scaffold.py:111`), e nenhum script confere o gate. A ratificação alcança o material já produzido: as unidades `01` e `02`, as decisões `D-12`–`D-14`, as lacunas `L-11`–`L-13` e a implementação da `01`. A data na coluna *Aprovado* do `_planos.md` continua sendo **2026-08-23**, que é quando o script rodou; corrigi-la à mão editaria projeção. O defeito de mecanismo que permitiu isso está na `L-16` |
| D-16 | **A instância de prova da `09` não é a `hub-front`, e o material dela vira o caso da fronteira** | **Decidida na derivação de 2026-08-24.** O escopo da `hub-front` é `hub/app/**`, que não existe neste repositório: como guideline viva aqui, ela validaria e **nunca ativaria** — o modo de falha que a própria `09` define um invariante para recusar, entregue pela unidade que o define. A `hub-front` fica onde é útil, como **caso medido** da fronteira skill × guideline, que é o papel para o qual este plano a nomeou. A guideline viva carrega a norma operativa de escrita de script, com `paths:` casando os `.py` daqui, e o corte segue o padrão da `03`: **a rule carrega o operativo, o documento de `docs/plan/system/` carrega evidência e racional**, citado — nunca as duas coisas nos dois lugares. Extrair a `hub-front` continua consequência reportada ao AmFlow, nunca gate |
| D-17 | **Os números provisórios das fases não derivadas deslocam-se a cada derivação** | **Decidida na derivação de 2026-08-25.** A Fase 4 tomou `12`–`15` do disco, e a Fase 5 carregava `12` e `13` como previsão — o mesmo número passaria a nomear duas unidades no mesmo documento, e a prosa já referenciava as duas. A colisão não era nova: as correções fora de fase tinham tomado `06`, `07`, `08` e `11`, que a Fase 4 também previa. Em vez de deixar o plano com dez números ambíguos, cada derivação desloca os provisórios das fases seguintes e atualiza as referências. **O que isso não compra:** os provisórios continuam sendo previsão — a Fase 3 previa `06`/`07` e recebeu `09`/`10`, e qualquer correção nova desloca tudo de novo. O que se ganha é que, **em qualquer instante**, um número nomeia uma unidade só |
| D-18 | **O gate de `plan_size` recusa valor fora do vocabulário, e isso não é julgar o porte** | **Decidida na derivação de 2026-08-25.** O Escopo diz que o gate recusa o campo vazio, *"nunca um valor"*, e a razão dada é que recusar valor seria julgamento. A leitura literal deixaria `plan_size: enorme` passar. O que a frase protege é o **julgamento sobre a escolha** — o script não opina se `grande` era certo para este plano. Membro de vocabulário fechado é outra coisa: é o que `lint_unidade.UNIT_TYPES_VALIDOS` já faz para `unit_type`, e a `14` ramifica por esse valor — um valor desconhecido chegando lá teria que falhar de algum jeito, e falhar na aprovação é mais cedo e mais barato |
| D-19 | **A instrumentação mede linhas por git, restrita aos arquivos que as unidades declaram** | **Decidida na derivação de 2026-08-25.** *"Linhas alteradas"* não existe sem git, e o churn do repositório inteiro no intervalo mediria todo trabalho paralelo chamando isso de custo do plano. A medição fica restrita aos caminhos das tabelas `## Arquivos`, que é o que é atribuível, e sai como `não medido` **com motivo** quando git não responde — nunca zero. Fora do porte grande não há unidade e portanto não há caminho declarado: a coluna fica vazia em vez de receber um número maior e errado |
| D-20 | **Não há arquivo de template: o formato de cada porte vive no lint e na norma** | **Decidida na derivação de 2026-08-25.** O Escopo fala em *"a norma e o template"*, e template não existe neste repositório — a busca por `template` não devolve nenhum arquivo de plano. Criar três seria três arquivos cuja única função é serem comparados com o que o lint já afirma, e o invariante 1 recusa: o formato passa a ter uma fonte, `lint_plano`, com a norma descrevendo-o em prosa. É o mesmo padrão de `scaffold._SECAO_BACKLOG`, onde o esqueleto vive no script e não em arquivo |
| D-21 | **O pacote é build reproduzível, e a árvore construída não é versionada** | **Decidida na derivação de 2026-08-26.** A alternativa era reestruturar o repositório para que a raiz *fosse* o plugin — `skills/` e `hooks/` na raiz —, e ela quebra o uso que este repositório faz de si mesmo no meio do plano: é a própria skill em `.claude/skills/` que roda o `derive`. Build para `dist/decode-and-code/`, `dist/` no `.gitignore`. **Árvore construída e commitada é a divergência de 2026-08-01 de novo**, agora dentro do mesmo repositório: envelhece a cada mudança da fonte, e nada avisa. A estrutura não foi suposta — foi medida em 2026-08-26 nos plugins instalados em `~/.claude/plugins/marketplaces/`: `.claude-plugin/plugin.json` com `name`/`description`/`version`/`author`, componentes na raiz do pacote, e `hooks/hooks.json` com a mesma forma do bloco `hooks` do `settings.json`, ancorado em `${CLAUDE_PLUGIN_ROOT}` em vez de `${CLAUDE_PROJECT_DIR}`. **Os testes da skill não viajam:** eles leem `docs/plan/system/` e o acervo daqui — são a prova deste repositório, não componente do método |
| D-22 | **Nenhuma instância de guideline viaja no pacote; `materializar` recebe a origem** | **Decidida na derivação de 2026-08-26, e fecha o que a `L-23` deixou em aberto.** A pergunta era se o `estudo-runtime-e-dependencias.md` viaja: **não viaja**, e a razão generaliza — hoje toda guideline que existe aqui é instância deste repositório, e o invariante 2 recusa embarcar instância. A operação copia **um** arquivo nomeado pelo chamador para `<projeto>/.claude/rules/`, em vez de carregar catálogo. Ganha o caso de uso imediato — extrair a `AmFlow:hub-front` para lá — sem que o plugin decida por quem instala, e sem que a `16` precise escolher quais guidelines "são boas o bastante" para viajar, que é julgamento que nenhum critério de aceite comporta |
| D-23 | **A reconciliação julga por conteúdo; versão declarada entra como contexto** | **Decidida na derivação de 2026-08-26, contra medição.** O `SKILL.md` daqui e o do `AmFlow:.claude/skills/dev-units` declaram **`version: 1.0.0` os dois**, e seis dos nove componentes compartilhados divergem — `backlog.py`, `lib.py`, `lint_skill.py`, `lint_unidade.py`, `scaffold.py` e `verificacao.py`. Uma reconciliação por versão reportaria "em dia" nos seis. O veredito sai de SHA-256 por componente, com quatro valores (`idêntico`, `divergente`, `só na origem`, `só na cópia`), e a versão aparece no relatório com a ressalva de que igualdade ali não implica igualdade de conteúdo. **`só na cópia` é o veredito que importa mais e não existia no desenho original:** é ele que distingue cópia atrasada de fork. **Corrigido em 2026-08-26, na revisão da `17`:** esta decisão foi escrita afirmando *"nenhum só lá"*, medido por mim sobre `scripts/*.py`. A ferramenta compara a árvore inteira e devolve **54 componentes — 19 divergentes, 28 só na origem, 5 idênticos e 2 só na cópia**, sendo os dois `scripts/tests/test_deprecacao.py`, que a `D-14` removeu daqui, e `skill-description.md`. O recorte dos nove scripts continua sendo a forma mais afiada do argumento da versão, e agora está nomeado como recorte (`L-32`) |
| D-24 | **A `18` é `dev` com oráculo estrutural, não `unit_type: norma`** | **Decidida na derivação de 2026-08-26.** A `L-01` nomeia a `18` entre as quatro unidades que entregam markdown normativo, e o tipo `norma` nasceu na `13` para elas. Mas `norma` exige `approved_by`/`approved_at` **preenchidos para passar no `lint_unidade`** — e o `lint_unidade` é o **gate de entrada** do `implement`. Consequência mecânica: uma unidade `norma` recém-derivada não passa no gate de entrada, então a aprovação teria de vir **antes** de a prosa existir, aprovando a intenção em vez do conteúdo. Preenchê-los eu mesmo reproduziria o defeito da `L-16`. A `03`, a `09` e a `13` entregaram markdown normativo e todas as três são `dev`, com oráculo estrutural — a `18` segue o mesmo caminho, verificando por conteúdo que as três frases mudaram. O que isso revela sobre o terceiro tipo fica na `L-33` |
| D-25 | **O `lint_agente` nasce na `19`, e a `20` só acrescenta um campo recusado** | **Decidida na derivação de 2026-08-26.** As duas unidades precisam validar a mesma coisa, e a alternativa era cada uma conferir frontmatter à mão no próprio teste — duas cópias da mesma regra, que divergem no dia em que um campo nativo muda. O lint segue o padrão que o repositório já tem quatro vezes (`lint_unidade`, `lint_plano`, `lint_skill`, `lint_guideline`), viaja no pacote como mecanismo, e serve a qualquer projeto que instale. As duas unidades declaram o **mesmo arquivo de teste**: a granularidade do gate é de arquivo, e casos da `20` que ainda não existem não afetam o fechamento da `19` |
| D-26 | **A norma passa a viajar, mas dividida — e a divisão é plano próprio, não a `21`** | **Decidida em 2026-08-26, aprovada pelo humano, e fecha o caminho da `L-31`.** Medido: `modelo-dev-units.md` tem **1087 linhas**, com **18** referências a unidades `0001-`, 6 a `METR`/`DORA`, 3 ao AmFlow e 3 a `docs/mvp` — auditoria de um acervo que só existe aqui. Empacotá-la inteira entrega a quem instala o nosso log de decisões datadas e `L-XX` apontando para o nosso plano: o invariante 2 quebrado no artefato mais central do método. Não empacotar quebra o produto pelo outro lado, porque os três modos da skill a citam. A saída é o padrão que a **`D-16` já validou** — o operativo vai para onde é carregado, evidência e racional ficam no documento do projeto, citados. **Fora da `21` por tamanho, não por preferência:** dividir 1087 linhas toca as referências da skill, os docstrings dos lints e as 20 unidades que a citam, e precisa de oráculo próprio; embutir isso na unidade do huddle é o `B-01` que este plano combate — unidade que existe pelo gate e não pelo produto. **O custo fica dito:** o plugin v1 sai sabidamente incompleto, e o `SKILL.md` empacotado já declara a dependência em vez de deixar quem instala tropeçar nela. A divisão é o candidato natural a plano `0002` |
| D-27 | **Os dois agentes viajam no pacote, e a `21` absorve isso** | **Decidida em 2026-08-26, aprovada pelo humano, e fecha o caminho da `L-35`.** Medido: `developer.md` tem **zero** ocorrências de caminho ou nome de projeto — viaja limpo sem tocar em nada. `planner.md` tem quatro, e **só uma importa**: três são exemplos na `description`, que a `L-14` já classificou como didática e não asserção; a quarta é normativa (`:46`, *"Escreve apenas sob `docs/plan/**`"*) e passa a ser relativa ao `plan_root`, exatamente como o `SKILL.md` fez na `16`. Do lado do empacotamento, `construir` ganha `agents/` no mesmo formato de `_copiar_hooks` — uma função e um caso —, e `verificar` já cobre o resto: nome de projeto que sobrar num agente é acusado. **A consequência que se aceita junto:** o pacote passa a distribuir operadores que dependem, pelo `skills:`, de uma skill que cita a norma que ainda não viaja. Não inviabiliza — quem já tem a norma opera —, mas **aumenta o custo de manter a `D-26` pendente**, porque passam a ser três componentes dependendo dela em vez de um |

## Lacunas

| # | Lacuna | Por que fica registrada |
|---|---|---|
| L-01 | **Unidade de conteúdo normativo não tem oráculo natural** | **Endereçada pela `13`, derivada em 2026-08-25, sem fingir resolver o irresolvível.** Quatro das vinte e uma unidades entregam markdown normativo (`03`, `09`, `13`, `18`), e o gate de saída exige teste passando. A saída é um terceiro valor de `unit_type` — **`norma`** —, cujo oráculo é estrutura válida **somada a aprovação humana registrada em campo**. O script continua sem julgar prosa; o que muda é que a aprovação deixa de ser etapa implícita que ninguém registra e vira passo verificável, no mesmo padrão do `plan_size`: recusa-se a ausência, nunca o valor. O que permanece em aberto e é honesto dizer: **adequação de conteúdo continua sendo julgamento humano**, e nenhum campo transforma isso em oráculo |
| L-02 | **Como a guideline chega ao projeto: cópia versionada ou symlink** | **✅ Resolvida na revisão de 2026-08-21 — cópia versionada.** A ressalva do Cowork sobre symlink é de *user-scope* e as guidelines vão para *project-scope*: medir só diria se o atalho funciona, não se é a escolha certa. A cópia vence no mérito — sem ressalva a lembrar, versionada no projeto (um revisor vê em qualquer commit **qual texto estava ativo**), e a drift fecha pela verificação de versão que a `17` constrói de qualquer jeito. Fechar decidindo, em vez de agendar medição, é *subtração primeiro* aplicado ao próprio plano |
| L-03 | **Escopo do rename `dev-units` → `decode-and-code`** | **Sem objeto desde 2026-08-22.** Ela mediu 164 ocorrências vivas em 32 arquivos do AmFlow, separadas de 414 de registro histórico e 452 de homônimo em `docs/mvp/`. Com o desenvolvimento em repositório próprio, **o nome nasce certo** e não há o que renomear. A medição fica registrada porque a limpeza do AmFlow ainda a usará — mas como item de backlog daquele repositório — `AmFlow:B-10`, criado em 2026-08-22 —, não como lacuna deste |
| L-04 | **O `CLAUDE.md` do AmFlow continua acima do limiar de aderência** | **Sem objeto neste plano desde 2026-08-22.** A extração das três seções saiu do escopo junto com a mudança de repositório: o `CLAUDE.md` daqui nasceu com 127 linhas, abaixo do alvo documentado de 200. As 458 linhas do AmFlow continuam sendo um fato — e um dos que originaram este projeto —, mas encolhê-las é curadoria daquele repositório, registrada como `AmFlow:B-11` em 2026-08-22. Fica nomeada para não passar por resolvida |
| L-05 | **Nenhuma checagem de consistência entre normas** | A doc do Claude Code afirma que instruções contraditórias fazem o modelo escolher arbitrariamente. Com `CLAUDE.md` + norma + princípios + N guidelines ativas, a superfície de contradição cresce, e nada a mede. **Fica fora do escopo, mas o gatilho deixou de ser impressão:** a colisão passa a existir quando **duas rules ativas casam o mesmo path**, que é condição observável — e a `05` já vê todo carregamento, então é o detector natural, sem construir nada. Item de backlog, a escrever quando a condição ocorrer, não numa data. **A condição passou a ser observável em 2026-08-24** (ver *Validação de ponta a ponta*): o log da `05` mostra **três** fontes normativas carregando na mesma sessão — `CLAUDE.md` do projeto, `principles.md` e `CLAUDE.md` global. Com a `09`, a primeira rule **com** escopo passou a existir, e foi vista ativando por `path_glob_match` em 2026-08-24. **Ainda não há colisão a detectar:** o `principles.md` não declara `paths:` e o `scripts.md` é o único que declara, então não existem duas rules disputando o mesmo path. A condição fica a um passo — nasce quando a **segunda** guideline com escopo existir. Continua item de backlog, agora com o mecanismo provado e a condição nomeada |
| L-08 | **Os cinco gatilhos de escrita do huddle não são verificáveis por script** | A regra de despejo é — entrada fechada não permanece no arquivo, e isso é o oráculo da `21`. Os gatilhos não: *"decidiu algo que o humano não decidiu"* é observável por quem escreve, e por mais ninguém. **A mitigação que a `21` passou a carregar é fraca e vale dizer o quanto:** exigir a linha de fecho mesmo com zero entradas separa *conferi e não havia* de *nunca conferi*, que hoje são indistinguíveis — mas não diz nada sobre os gatilhos terem disparado certo. Um relatório honesto com zero e um relatório desatento com zero continuam idênticos. É o `B-01` outra vez: conteúdo que depende de julgamento não ganha oráculo por se querer que ganhe |
| L-09 | **Guideline não sobrevive à compactação, e a correção continua cara demais** | Medido em 2026-08-22: rule com `paths:` recarrega apenas quando um arquivo que casa o glob é lido de novo. Numa sessão longa que compacta e segue editando sem reler, a guideline **sai de contexto e não volta**. As saídas candidatas — reler um arquivo-âncora após `PostCompact`, ou promover a guideline crítica a rule sem `paths:` — trocam correção por custo de contexto permanente, que é o problema que o escopo por glob existe para resolver. **O que a `05` passou a fazer é remover o silêncio, não a perda:** em `PostCompact` ela nomeia o que estava ativo e não voltou. Decidir a correção fica para quando houver guideline em uso real e dado sobre com que frequência isso morde |
| L-10 | **A suíte migrada está vermelha: 132 passam, 25 falham, 1 é pulado de 158** | **Fechada em 2026-08-22 — não era lacuna, era escopo.** As 25 falham por usarem arquivos reais do AmFlow como fixture, e é a razão de a unidade `02` existir. Os scripts em si têm apenas **5** auto-referências ao nome antigo: o acoplamento está nos testes, não no código. **O número mudou três vezes no mesmo dia, e a causa importa mais que ele:** 34 na primeira medição (feita antes de a norma migrar), 26 na segunda (feita com invocação própria de `unittest`), e 25 na terceira — a única feita com `./scripts/test-python.sh`, que é o oráculo que o gate de saída realmente usa. **Medir com equivalente ad hoc em vez da ferramenta do projeto produz número que parece certo e não é.** A lição foi para o huddle como `padrão`; o que fica aqui é o número canônico |
| L-11 | **O oráculo declarado da `02` não cabe no campo `test:`** | A `02` declara *"`./scripts/test-python.sh` verde"* — a suíte inteira. `verificacao.verificar` aceita **um arquivo** `.py` ou `.ts`: o caminho da suíte levanta `ValueError`, e um diretório devolve `spec` **em silêncio** (`verificacao.py:63`). **Decidido em 2026-08-23:** a `02` declara `tests/test_fixtures.py`, e "suíte verde" vira condição de fechamento da Fase 1, conferida pelo humano. Alargar o gate para a suíte foi recusado — reverteria a `0005-02`, que trocou granularidade de pacote por arquivo, e acoplaria o gate de cada unidade aos testes de todas as outras. **O que permanece em aberto:** o gate da `02` prova menos do que ela entrega, e é a `L-01` outra vez, num lugar novo |
| L-12 | **A norma define o formato da unidade por um arquivo que não existe aqui** | `modelo-dev-units.md:344` diz *"o formato **não é duplicado aqui**: o exemplo é a fonte"* e aponta para `docs/plan/hub/0001-mcp/01-handler-auth.md`, que ficou no AmFlow. **Contornado em 2026-08-23, não resolvido:** as unidades `01` e `02` foram escritas a partir da tabela de blocos (`:361`), da precedência (`:375`), das regex do `lint_unidade` e do fixture `UNIDADE_VALIDA` — e passaram no gate de entrada com `[]`. Trazer o arquivo do AmFlow foi recusado: cria segunda cópia editável, que é a condição da divergência de 2026-08-01. **Fecha na `01`**, que reescreve a norma e reaponta a referência viva para uma unidade deste repositório |
| L-13 | **O plano se contradiz sobre o que a suíte vermelha bloqueia** | `:107` e `:553` afirmam que *"nenhuma unidade posterior consegue passar pelo gate de saída"* enquanto a suíte estiver vermelha; `:410` afirma que *"o gate roda por arquivo declarado, não pela suíte"*. **Medido em 2026-08-23:** unidade sintética com teste próprio fechou em `verified` com os 25 vermelhos na suíte — a `:410` está certa e as outras duas erradas. Não muda o escopo: a Fase 1 continua vindo primeiro pela `D-12`, não pelo argumento mecânico. Fica registrada em vez de corrigida em silêncio, porque o texto é do humano |
| L-14 | **O critério de aceite da `01` mediu string, e não instância** | **Aberta e corrigida na mesma passada, em 2026-08-24.** O critério exigia a ausência de quatro literais — `AmFlow`, `AMFLOW`, `docs/plan/hub`, `docs/plan/builder` —, e isso errou nas duas direções. **Exigiu demais:** *"nenhum `.py` da skill"* alcança `tests/`, onde os fixtures sintéticos existem de propósito; três partes do mesmo arquivo declaravam três escopos diferentes, e o executor entregou pelo contrato, que é o que a norma manda. **Exigiu de menos:** `0003-08`, `plugins/`, `0002-dev-units` e `0003-public-catalog` são instância do AmFlow, não contêm nenhum dos literais, e passaram no gate — assim como `.claude/skills/dev-units/`, o **nome antigo da própria skill**, que sobreviveu em duas afirmações normativas. Nome usado como exemplo dentro de bloco de código fica: `_inbox/mcp.md → <core>/0001-mcp/…` é didática, não asserção sobre o AmFlow. E, por medir string, o critério não distinguiu **generalizar** de **deletar**: a subseção *Guardrail fundador* saiu inteira, levando junto a afirmação de mecanismo — que a regra de dependência entre cores é o que dá função arquitetural ao nível core, e é o candidato natural a primeiro guardrail automatizado. A norma ficou referenciando, no *Modo `review`*, um guardrail que ela não definia mais, e a contagem *"quatro dos seis checks têm parte automatizável"* passou a contradizer a própria tabela. O critério foi reescrito em termos de instância e com escopo em `scripts/*.py`; a subseção voltou generalizada. **O que permanece em aberto:** o critério continua sendo prosa conferida por leitura — instância não tem oráculo por grep, que é exatamente por que o grep errou. É a `L-01` num lugar novo. **Correção de 2026-08-24:** a redação original desta lacuna afirmava que retirar `project: AmFlow` dos fixtures era critério de aceite da `02`. **Não era** — a `02` reivindica os quatro caminhos, não a string —, e a alegação seguinte, de que o oráculo da `16` cobriria o resíduo, também não se sustenta: aquele oráculo fala em **caminho**, e `project:` é campo. As cinco strings inline remanescentes foram trocadas para `DecodeAndCode` à parte, sem unidade — cinco linhas de dado de teste, sem lógica, e unidade para isso é o `B-01` que este plano combate. As duas menções restantes são **prosa explicando por que a asserção mudou**, e ficam: o `CLAUDE.md` manda preservar o racional e remover só o ponteiro |
| L-21 | **O formato de frontmatter de teste tem duas fontes** | O `fixtures.py` que a `0001-02` entregou centraliza os construtores, mas quatro arquivos de teste mantêm templates de frontmatter **inline**, escritos antes dele. É o invariante 1 violado num lugar de baixo impacto: enquanto os dois concordarem, nada quebra; quando divergirem, o teste que usa o inline passa a provar um formato que o repositório não usa mais. **Não vira unidade agora** — consolidar é refactor de quatro arquivos de teste, tem risco real, e nenhuma unidade em aberto depende disso. Fica registrada para não passar por não-observada |
| L-22 | **A linha `Último resultado` existe no formato, ninguém a projeta, e ela sempre mente** | Medido em 2026-08-24: as três unidades em `verified` — `01`, `02` e `07` — dizem todas *"Último resultado: não executado."* no corpo, enquanto o frontmatter delas diz `verified` com data. `verificacao.verificar` projeta `state` e `verified_at` e **não toca essa linha**; a norma não a menciona em seção nenhuma; nenhum script a lê ou escreve. É campo órfão — nasceu no formato migrado do AmFlow, e todo executor o copia do modelo sem que nada o atualize. **Duas saídas, e a escolha é sobre o que o formato promete.** Projetá-la junto com `state` faz dela informação real, ao custo de mais uma coisa que o script escreve **no corpo** — e a norma hoje diz que script escreve só o bloco `# verificação` do frontmatter, nunca o corpo (decisão 13). Removê-la do formato é mais barato e não perde nada, porque o dado já está em `verified_at`. **Inclina para remover**, e a decisão pertence à unidade que tocar o formato da unidade — hoje a `13`. **Endereçada pela `13`**, derivada em 2026-08-25: a linha sai do formato e das onze unidades que a carregam, e `lint_unidade` passa a recusá-la, para que não volte pela mesma porta por onde entrou |
| L-23 | **O critério nomeou um repositório, e o que passou foi outro** | A `08` migrou `estudo-runtime-e-dependencias.md`, e o documento carrega instância do **Brand Boost** — o corpo descreve o orquestrador daquele projeto, com nome de arquivo e contagem de linhas. Passou no gate porque o critério de aceite que **eu** escrevi proibia instância *do AmFlow*, nominalmente, e o invariante 2 é sobre projeto — qualquer um. É a `L-14` pela terceira vez, e a raiz não muda: **critério escrito como lista de strings em vez de conceito**. Junto veio o mesmo defeito no teste: `_MARCAS_AMFLOW` não continha a string `AmFlow`, então o arquivo passava verde com quatro menções — corrigido em 2026-08-24, com a nota de procedência virando exceção **explícita e delimitada** em vez de silenciosa. **O que ficava em aberto — se o estudo viaja no plugin — fechou na derivação de 2026-08-26, pela `D-22`: não viaja.** Ele é referência, não norma, e o pacote não leva `docs/` nenhum; a razão generalizou para toda guideline, porque instância não viaja e é isso que a `16` verifica |
| L-24 | **A `04` declarou um canal sem exigir caso que o provasse, e o canal saiu invertido** | A tabela *Canal* da unidade listava `psql` por `Bash` como recusado, e a seção *Fixtures* trazia **quatro casos, nenhum deles `Bash`** — o único payload dessa ferramenta na suíte é `echo oi`, nos testes de falha aberta. Implementado conforme a tabela, o braço `Bash` **inverteu**: medido em 2026-08-24 contra o hook real, ele recusava `truncate -s 0 arquivo.log`, `cd x; drop old-cache` e uma mensagem de commit em prosa contendo `; alter`, e **liberava** `psql -h db.example.com -c "alter table t drop column c"`, que é o alvo. **A causa é de quadro de referência:** o detector ancora no início de statement — certo para SQL, e foi o que a unidade pediu para evitar substring —, mas no canal `Bash` o SQL está **aninhado dentro** do comando de shell, então ancorar na string externa mede a coisa errada. O hook chegou a bloquear uma chamada desta própria sessão. **Corrigido em 2026-08-24 retirando `^Bash$` do `ferramenta`** — uma linha, e é dado, não código: o hook para de bloquear shell legítimo e para de alegar um canal que não cobre. **Fica em aberto:** cobrir `psql` exige extrair o SQL de dentro do comando antes de ancorar, e isso é unidade, não ajuste. É a `L-14` na quarta ocorrência — critério que enumera sem caso verificável atrás |
| L-15 | **A norma cita como vinculantes dois documentos que não existem neste repositório** | `language-policy.md` é referenciado **quatro vezes** — `:650`, `:759`, `:762` e na seção *Fonte* —, uma delas normativa (*"os scripts seguem a norma de linguagem"*), e `estudo-runtime-e-dependencias.md` como a evidência que a fundamenta. Os dois estão no AmFlow (`docs/plan/system/`, 165 linhas o primeiro) e não migraram com a norma. Não é texto a corrigir: ou o documento migra, ou a norma para de depender dele. **Recomendação registrada, não executada:** migrar, porque a `D-10` já decidiu que o determinismo migra e este é a norma de linguagem dos scripts que já vieram — o `language-policy.md` traz 8 linhas com instância do AmFlow, que saem no mesmo movimento que a `01` fez aqui. **Endereçada pela unidade `08`**, derivada em 2026-08-24, que traz os dois documentos desacoplados e tira do `CLAUDE.md` as três frases que hoje os duplicam |
| L-16 | **A etapa 3 do fluxo não deixa registro, e o `derive` a carimba sozinho** | `scaffold.aprovar` grava `status: approved` no plano e a linha em `_planos.md` como parte do `derive` (`scaffold.py:111`), sem conferir nada — e a coluna *Aprovado* recebe a data em que o **script** rodou. Nenhum campo distingue *o humano aprovou* de *o derive rodou*, nos dois sentidos: um plano aprovado de verdade e um plano nunca visto por humano produzem arquivos idênticos. Foi o que aconteceu em 2026-08-23 e só apareceu porque o humano lembrava (`D-15`). A norma nomeia a etapa como gate humano (*Fluxo completo*, etapa 3) e não especifica registro nenhum dela. **Correção candidata:** campo de aprovação declarado, no mesmo padrão do `plan_size` e do `unit_type: norma` — recusa-se a ausência, nunca o valor. Isso a torna parente da `12` e da `13`. **Endereçada pela `12`**, derivada em 2026-08-25: `aprovar` passa a exigir `approved_by` e `approved_at` declarados pelo humano, para de carimbar `status: approved` por conta própria, e a coluna *Aprovado* passa a receber a data **declarada** em vez da data em que o script rodou |
| L-17 | **O modo `derive` não é re-executável, e a `D-12` supõe que seja** | A `D-12` afirma que o derive incremental *"é suportado sem nada novo"* porque `numeracao.proxima_unidade` lê o disco — verdadeiro para a numeração, que devolve `03` corretamente. Mas o passo 1 do modo chama `scaffold.aprovar(plano)` incondicionalmente, e sobre o plano já movido isso levanta `ValueError: nome de plano inválido '0001-decode-and-code-foundation' — começa com prefixo numérico` (medido em 2026-08-24, `dry_run`, sem escrita). Falha ruidosa e antes de qualquer escrita, então não corrompe nada — mas bloqueia a derivação da Fase 2 até o modo ganhar caminho para plano já aprovado. **Mecanismo corrigido em `de4fc57`**, fora de unidade, porque a unidade que conserta o `derive` precisaria do `derive` para ser derivada. **Endereçada pela unidade `06`**, que fecha a dívida que a correção abriu: teste declarado e registro na norma |
| L-18 | **A situação projetada em `_planos.md` mede as unidades derivadas, não o plano** | Ao fechar a `0001-02`, `backlog.projetar` levou a situação a `concluído` com quinze unidades ainda por derivar — e o efeito não é cosmético: a região `planos` ficou **sem nenhuma linha `em desenvolvimento`**, que é exatamente o que o check de concorrência do modo `review` varre. Um plano novo em `model`/`decode-and-code` teria passado num check que deveria sinalizá-lo. **Não é ocorrência única:** repete a cada fronteira de fase em que todas as unidades derivadas estão verificadas, e a derivação da Fase 2 em 2026-08-24 a reverteu para `em desenvolvimento` sem ninguém editar projeção. É a mesma raiz do custo que a `D-12` aceitou — o rodapé dizendo *"N de N derivadas"* —, mas com consequência funcional que a `D-12` não previu. **Endereçada pela unidade `07`**, derivada em 2026-08-24: a situação passa a comparar previstas com derivadas, e escopo ilegível falha fechado — nunca projeta `concluído` por não conseguir contar |
| L-19 | **O fluxo de decodificação da `03` era derivação, não cópia da fonte** | **✅ Resolvida em 2026-08-24, e a reconciliação mudou conteúdo.** O `CortexMachine` foi clonado nesta máquina no mesmo dia, e a `03` foi reescrita contra a fonte. A derivação anterior errava em três pontos que importam: *Clarificar* virou *"problema + métrica + beneficiário em 1 frase"*, e não *"o que foi pedido e o que foi suposto"* — a fonte exige **métrica e beneficiário**; *Evitar* enumera as quatro alternativas sem código (config, processo, doc, reuso); e os **Gates A/B são critérios, não posições no tempo** — *necessidade real* e *mínimo viável*, não *"antes de escrever"* e *"antes de entregar"*. A `D-03` saiu confirmada: a fonte tem quatro princípios operacionais, e o quarto é o que a `D-03` cortou por redundância. **O que foi deliberadamente deixado de fora, e é o invariante 2 aplicado:** os Gates 1–5 com limites numéricos, o catálogo de padrões de ML/scheduler, e a governança do protocolo HITL — Architecture Council, SLA em horas, matriz de risco. Ficam os cinco gatilhos de exceção e o registro mínimo, que são mecanismo |
| L-20 | **Metade do par de fixtures da `04` não existia no acervo** | **✅ Resolvida em 2026-08-24, e a leitura das fontes mudou o desenho da unidade.** O caso recusado **existe verbatim** e foi transcrito de `AmFlow:docs/plan/_inbox/notification-fk.md:80-86`; o `SELECT` diagnóstico **não existe** — o acervo registra dumps, fingerprints e hashes de function, nenhum statement de diagnóstico —, então ele é **autoral e vai marcado como tal** na unidade, em vez de ser reconstruído fingindo procedência. **O achado maior veio junto:** `AmFlow:.claude/CLAUDE.md:103` mostra que a regra é sobre **canal**, não sobre SQL — *"painel do Supabase, SQL Editor ou MCP"* —, e o mesmo `ALTER TABLE` dentro de um arquivo de migration é o caminho **sancionado**. A `04` falava em *"casar a ferramenta por regex"* sem nomear quais, e um hook que recusasse DDL em todo canal passaria no par original e inverteria a regra. O par virou **quatro casos**, com o DDL-em-migration liberado como o que prova que a regra é sobre canal |
| L-25 | **O passo 1 da `05` era spike por decisão do plano, e o canal saiu diferente do desenhado** | **✅ Resolvida em 2026-08-24 — o spike rodou contra a doc viva, não contra a paráfrase que originou esta unidade.** `code.claude.com/docs/en/hooks` é explícito, para `InstructionsLoaded`: *"Claude Code discards their JSON output fields, such as systemMessage and continue. Use this event for audit logging, compliance tracking, or observability"* — e o exit code também é ignorado para este evento, então nenhum canal chega ao usuário. Para `PostCompact`: mesma frase, *"Claude Code discards a PostCompact hook's systemMessage and continue fields"* — mas aqui o exit code 2 mostra stderr ao usuário sem bloquear nada (*"PostCompact hooks have no decision control. They can't affect the compaction result"*), e esse é o canal real. **A `05` corrigiu nos dois, como o próprio passo 1 previa:** `InstructionsLoaded` grava um log por sessão — o uso que a própria doc recomenda; `PostCompact` sai por stderr com exit 2, lendo o estado que `InstructionsLoaded` acumula para as rules com `paths:` (sinalizadas por `globs` não vazio no payload) e limpando-o depois de anunciar. `SubagentStart` já estava certo no plano original — stderr é exatamente o canal que a doc confirma (*"Shows stderr to user only"*; a notícia aparece só no transcript do próprio subagente, não no da conversa principal). **O que fica em aberto:** a doc não confirma nem nega `systemMessage` para `SubagentStart` de forma explícita — só documenta o canal de exit 2, que é o que a `05` usou; se existir também uma via por `systemMessage` para este evento, ninguém mediu. **Achado menor, sem ação:** o passo 5 da unidade cita *"a expansão de skill"* como um quarto canal a cobrir, mas não há evento de hook com esse nome no catálogo atual, e nem o Contrato nem a tabela de Arquivos da unidade declaram artefato para ele — ficou de fora por não ter contrato nenhum que o exigisse, não por omissão. **Onde o log fica, porque log que ninguém acha é log de escrita:** `$TMPDIR/decode-and-code-activation-<session_id>.log`, uma linha por instrução carregada, com caminho e `load_reason`. Sondado em 2026-08-24 contra os hooks reais — a metade que alcança o usuário é a do `PostCompact`, por stderr; a do `InstructionsLoaded` só existe nesse arquivo, e é da plataforma, não da entrega |
| L-26 | **`desligar` movia sem desligar, e o teste de unidade não podia ver** | A `10` mandava mover a guideline para `.claude/rules/_off/`, e eu afirmei na unidade que isso *"tira do diretório carregado"* — **afirmado sem medir**. O instrumento da `05` mostrou o contrário em 2026-08-24: `.claude/rules/_off/scripts.md` carregou por `path_glob_match`, ou seja, **o matcher recursa para dentro do subdiretório**. O efeito era o pior possível: `listar()` reportava `desligada`, os 14 testes passavam, o arquivo estava mesmo em `_off/`, **e a norma continuava em contexto** — falha silenciosa e indistinguível de sucesso, na unidade cujo propósito é controlar o que está ativo. **Corrigido em 2026-08-24** para `.claude/rules-off/`, diretório **irmão**, com o racional gravado no `_dir_off` para que ninguém o "simplifique" de volta. **Reteste em 2026-08-25: passa** — a mesma leitura que carregava de `_off/` não carrega de `rules-off/`. **O que a correção não pode fazer:** teste de unidade alcança o destino, nunca o carregamento — desligamento é comportamento de sessão. O critério de aceite passou a dizer isso, e a prova real é a sessão. **Quinta ocorrência do `H-09`**, e a primeira em que o defeito estava num mecanismo de controle: o instrumento da `05` foi a única coisa que o viu |
| L-27 | **A validação por sessão não é reproduzível, e a lição da `L-26` não é gate** | Duas metades do mesmo defeito, e as duas apareceram na revisão da `10`. **Primeira:** o racional que impede recriar um subdiretório sob `.claude/rules/` vive num docstring do `_dir_off` — **comentário depende de leitura, e foi assim que o problema nasceu**. Nada no repositório recusa um `.md` em subdiretório, e o defeito da `L-26` pode voltar inteiro. **Segunda, e é a maior:** as seis medições de *Validação de ponta a ponta* — as que provaram que princípio carrega, que guideline ativa só no escopo, e que desligar desliga — existem como **resultado**, nunca como procedimento. O que as produziu está numa conversa e em nenhum arquivo. Consequência concreta: se a Fase 5 empacotar o plugin e quebrar a ativação, **nada percebe** — a suíte fica verde porque nunca mediu isso, e ninguém consegue repetir os testes sem reconstruí-los do zero. É a classe de defeito que este plano inteiro persegue: conhecimento medido que não virou artefato. **Endereçada pela `11`** |
| L-28 | **O critério declarou o comportamento de um comando externo e nunca exigiu um caso que o executasse** | **Aberta e corrigida em 2026-08-25, na revisão da `15`.** `_commit_de_criacao` montava `git log --follow --diff-filter=A --reverse`, e o git responde a essa combinação com **saída vazia quando o arquivo foi movido** — que é a condição de **todo** plano, movido do `_inbox` pelo `derive`. Consequência medida: `porte.medir` sobre o plano `0001`, que tem 26 commits, devolvia `linhas_alteradas: None` com motivo *"plano sem commit de criação"*. A coluna que a `D-19` existe para produzir nunca carregaria número, em plano nenhum. **E a suíte estava verde** porque os quatro casos de git mockam `subprocess.run`: mock valida o **parsing da saída**, nunca o **comando montado** — e `test_plano_sem_commit_de_criacao` mockava stdout vazio, que é exatamente o que o git real sempre devolvia, então o teste que *provava* o ramo de falha cobria o único ramo que rodava. **Corrigido** tirando `--reverse` e lendo `linhas[-1]`: sem `--reverse` o git emite do mais novo para o mais antigo, e `--follow` fica porque é ele que atravessa o move — sem ele o comando acha o commit que *moveu* o plano, que é outro intervalo. Caracterizado num repositório descartável antes de escrever a correção, e o caso que faltava virou `TestComandoContraGitReal`, que roda git de verdade. Depois da correção, o mesmo plano mede **6634** linhas sobre 56 caminhos declarados, conferido contra `git diff --shortstat` (6308 + 326). **Segundo defeito, mesma raiz:** `medir` colapsava *"não se aplica"* (pequeno e médio) e *"grande sem caminho declarado"* em `(None, None)`, e a célula saía com a string literal `não medido (None)` — numa tabela **append-only**, que não se corrige reprojetando. **É a oitava ocorrência do `H-09`, e desloca a pergunta em aberto:** aqui não foi enumerar de menos, foi enumerar **contra um mock** em vez de contra a instância — o que é procedimental, não da forma "lista". **O que fica em aberto:** a afirmação *"nenhum teste executa `git` de verdade"* era sobre a suíte inteira e já era falsa antes desta unidade — `scripts/move-md.py` chama `git ls-files` em 16 testes. O critério foi reescopado para o que a unidade controla; isolar o `move-md` é escopo próprio, e virou item de backlog. **Fechado em 2026-08-25:** o `B-04` foi resolvido mockando `esta_versionado` nos quatro arquivos que movem plano — as 16 chamadas foram a zero, remedidas com o mesmo shim, e a lição virou norma operativa em [`scripts.md`](../../../../.claude/rules/scripts.md), seção *Comando externo*, que é o que faltava para ela alcançar a próxima unidade em vez de ficar só aqui |
| L-29 | **A `15` divergiu do que declarou em dois campos, e nenhum dos dois foi registrado no fecho** | **Aberta e corrigida em 2026-08-25, na revisão da revisão.** A tabela `## Arquivos` declarava `tests/fixtures.py`, que **não foi tocado** — `fixtures.plano` e `fixtures.unidade` já montavam o plano fechado nos três portes. A norma manda entregar pelo contrato e **registrar a divergência**; ela foi entregue certo e não foi registrada, e a linha da tabela seguia afirmando uma mudança que não existe. Sem efeito sobre a medição: outras dez unidades declaram o mesmo caminho, então os 56 não mudam. **Segunda, no `Contrato`:** a coluna *Unidades ou tarefas* dizia sair do `state` das unidades, e `_listar_unidades` conta **arquivos**, sem ler `state` nenhum. Inofensivo por acidente — plano só fecha com tudo `verified`, então os dois dariam o mesmo número —, mas `Contrato` é o bloco que **manda** quando os blocos divergem, e ele estava descrevendo um mecanismo que não existe. Os dois campos foram corrigidos no arquivo da unidade. **O que fica em aberto:** nada obriga a conferir `Arquivos` e `Contrato` contra o que a entrega de fato tocou — é `lint_unidade` medindo forma, e isto é conteúdo. É a `L-01` num lugar novo |
| L-30 | **A suíte escreve em `.claude/rules/registry.json` do repositório real, e o resíduo ficou invisível por causa do calendário** | **Aberta na derivação da Fase 5, em 2026-08-26, e não corrigida — é escopo próprio.** `TestGuidelineReal`, em `test_registry.py`, desliga e religa a guideline **real** `.claude/rules/scripts.md` — é o par do critério de aceite da `10`, e prova o que teste em `tempfile` não alcança. O `setUp` restaura o `.md`, mas `desligar`/`ligar` também reprojetam `registry.json`, e **essa escrita ninguém desfaz**: a suíte deixa o arquivo modificado com a data de hoje. **Por que só apareceu agora:** a projeção grava `date.today()`, então enquanto a última transição e a execução caem no mesmo dia o conteúdo sai idêntico e o git não vê nada. A virada de 25 para 26 de agosto, no meio desta sessão, tornou o efeito visível. **O risco não é o arquivo:** é que qualquer `git add -A` depois de rodar a suíte carrega a mudança junto sem ninguém decidir — foi o que quase aconteceu no commit `e4fb382`, que só ficou limpo porque a data ainda não tinha virado. **Correção candidata:** restaurar `registry.json` no mesmo `addCleanup` que já restaura o `.md`, guardando os bytes originais — mesmo padrão, três linhas. Fica registrada em vez de corrigida porque a Fase 5 não a toca, e emendar unidade fechada para acomodar achado de outra é o rótulo errado que este plano persegue |
| L-31 | **O oráculo da `16` verificava o pacote e nunca rodou contra o pacote real** | **Aberta e corrigida em 2026-08-26, na revisão da `16`.** O critério que **eu** escrevi mandava construir "em `tempfile`" e não dizia **de onde**; o executor construiu de árvore sintética, com `lib.repo_root` mockado, e reportou a decisão. Consequência medida construindo do repositório real: `verificar` devolvia **11 problemas em 7 arquivos**, enquanto o teste dizia `[]`. **Dos 11, oito eram falso positivo do meu critério:** `guardrails.json` acusava `guardrail.py` e o hook, que precisam nomear o arquivo que leem; `docs/plan` acusava `lib.py` e o `config.json`, que é a configurabilidade entregue pela `01`; e `CLAUDE_PROJECT_DIR` acusava a constante `_ANCORA_PROJETO` do próprio `empacotar.py` — o verificador reprovando o código que faz a substituição, que é o erro de quadro de referência da `L-24` outra vez. **Três eram defeito de verdade:** `project: DecodeAndCode` no frontmatter do `SKILL.md`; o mesmo nome dentro de `porte._CONTEUDO_INICIAL`, que é escrito **no arquivo do projeto que instalar**; e o `SKILL.md` citando `docs/plan/_inbox/decode-and-code-foundation.md`, caminho que deixou de existir na aprovação. **Corrigido:** os marcadores passam a ser nome de projeto e a âncora escopada a `hooks/`; `construir` reescreve o `project:` do `SKILL.md` copiado; `porte` preenche o projeto em tempo de execução; e `TestPacoteRealEstaLimpo` constrói deste repositório e exige `verificar() == []` — foi ele que expôs os dois últimos vazamentos, ambos em prosa escrita durante a própria correção. **É a nona ocorrência do `H-09`, e é minha:** enumerei quatro marcadores sem conferir nenhum contra as instâncias que eles iam varrer. **O que fica em aberto, e é maior que a unidade:** a norma `modelo-dev-units.md` não viaja no pacote (`D-21`), e os três modos da skill a citam — instalado num projeto que não a tem, o método opera sem a fonte. Decidir se a norma vira componente do plugin muda o que o pacote é, e não cabe em correção de revisão. **Caminho decidido em 2026-08-26 pela `D-26`:** a norma viaja, mas dividida — o operativo vira artefato empacotável, e evidência, decisões e história ficam no documento deste projeto. A divisão é plano próprio, não a `21`, e o plugin v1 sai sabidamente incompleto, com a dependência declarada no `SKILL.md` |
| L-32 | **O pacote levava lixo da máquina que o construiu, e a medição da derivação foi mais estreita que a da ferramenta** | **Aberta e corrigida em 2026-08-26, na revisão da `17`.** Duas coisas, e as duas apareceram porque a `17` mediu o que a `16` produz. **Primeira:** `construir` excluía `__pycache__` e `scripts/tests/`, e mais nada — um `.DS_Store` dentro da pasta da skill entrava no pacote, e `verificar` devolvia `[]` porque não há nome de projeto dentro de um arquivo do Finder. Medido: 26 arquivos no pacote, um deles `skills/decode-and-code/.DS_Store`; depois da correção, 25 e nenhum. A exclusão fica **num lugar só** — ensinar `verificar` a recusar lixo criaria duas listas do mesmo fato, contra o invariante 1 —, e o caso planta o arquivo na fonte antes de construir, porque foi exatamente a ausência dele na árvore sintética que deixou o defeito passar. Lixo novo entra na lista quando for observado, no padrão do `B-02`. **Segunda:** a `D-23` e a *Fonte* da `17` afirmavam *"nenhum só lá"* — medido por mim, na derivação, sobre `scripts/*.py`, antes de a ferramenta existir. A ferramenta compara a árvore inteira: 54 componentes, com **2 `só na cópia`**. É a `H-08` outra vez — medir com o equivalente montado na hora em vez do oráculo do projeto —, com o agravante de que aqui o oráculo passou a existir **na mesma unidade** cuja fonte eu não remedi. **O achado é melhor que o erro:** um dos dois é `test_deprecacao.py`, que a `D-14` removeu daqui, então o veredito `só na cópia` encontrou na estreia o caso que existe para nomear |
| L-33 | **`unit_type: norma` tem zero uso real, e a razão é mecânica** | **Aberta na derivação da Fase 6, em 2026-08-26.** A `13` criou o terceiro tipo para as unidades que entregam markdown normativo, e as **20 unidades derivadas até aqui são todas `dev`** — inclusive a `03`, a `09` e a `13`, que entregam exatamente isso, e agora a `18` pela `D-24`. Não é esquecimento: `lint_unidade` exige `approved_by`/`approved_at` preenchidos para uma `norma` passar, e é o mesmo `lint_unidade` que serve de **gate de entrada** ao `implement`. Uma `norma` recém-derivada portanto **não pode ser começada** antes de o humano aprovar — e aprovar antes da prosa existir é aprovar a intenção, não o conteúdo, que é o oposto do que o campo promete (*"o fato verificado é a aprovação do humano"*). **Três saídas, e a escolha não é de correção:** o gate de entrada passa a tolerar aprovação ausente em `norma`, aprovando-se no fecho; ou o tipo assume que aprovação é da **intenção** e a norma passa a dizer isso; ou o tipo é retirado, e markdown normativo continua fechando por oráculo estrutural, como as quatro já fizeram. Fica registrada em vez de decidida porque muda o modelo, e a `13` está fechada |
| L-34 | **`tools:` não tem granularidade de caminho, e o plano prometeu escopo de caminho** | **Aberta na derivação da Fase 6, em 2026-08-26.** O *Oráculo* do plano pede, para a `19` e a `20`, que *"o `tools:` não conceda escrita fora do escopo declarado — este último é o que impede o planejador de tocar código"*, e a seção de agentes fala em *"escopo de caminho (`docs/plan/**`)"*. Medido nos 34 agentes instalados nesta máquina: `tools:` é **lista de nomes de ferramenta** (`Glob, Grep, LS, Read, ...`), sem qualquer expressão de path. Não existe o campo que a frase supõe. A `19` entrega o que dá para entregar — a declaração de escopo no corpo, verificada por teste — e diz por escrito que é **declaração, nunca imposição**. **Impor de verdade é guardrail no projeto** (`D-07`), e o mecanismo para isso já existe desde a `04`: uma regra em `guardrails.json` que case `Write`/`Edit` fora de `docs/plan/**` quando o agente for o planejador. Não entra agora porque o hook hoje casa **ferramenta e conteúdo**, e não sabe qual agente fez a chamada — descobrir se o payload carrega essa informação é medição, não ajuste |
| L-35 | **Os agentes que a Fase 6 entrega não viajam no pacote** | **Aberta na revisão da `19`, em 2026-08-26.** Medido: `empacotar.construir` produz `skills/` e `hooks/`, e **`agents/` não existe na árvore** — quem instalar o plugin recebe a skill e os quatro hooks, e nenhum dos dois operadores do método. Não é defeito da `19` nem da `16`: quando a `16` definiu o que viaja, agente ainda não existia neste repositório. **E plugin do Claude Code empacota agente** — medido no `AmFlowPlugins:plugins/builder`, que distribui `agents/reviewer` e `agents/publisher`. **A decisão não é mecânica, é sobre o que o pacote é:** o `planner` e o `developer` são *mecanismo* (papel e processo do método, sem norma embutida) e por esse teste viajam; mas o `planner` declara escopo de escrita em `docs/plan/**`, que é convenção deste projeto, e num projeto com `plan_root` diferente a declaração chega errada. **Fica para a derivação da Fase 7**, junto com a `L-31`: as duas mexem no que o pacote leva, e a `21` é quem reexecuta o empacotamento. **Resolvida em 2026-08-26 pela `D-27`:** os dois viajam. O `developer.md` já está limpo, o `planner.md` troca uma frase por `plan_root`-relativa, e `construir` ganha `agents/` — absorvido pela `21` |

## Backlog

<!-- backlog:start -->
| Unidade | Título | Estado |
|---|---|---|
| [0001-01](01-config-and-paths.md) | config-and-paths | `verified` |
| [0001-02](02-test-fixtures.md) | test-fixtures | `verified` |
| [0001-03](03-principles-rule.md) | principles-rule | `verified` |
| [0001-04](04-ddl-guardrail-hook.md) | ddl-guardrail-hook | `verified` |
| [0001-05](05-activation-notice.md) | activation-notice | `verified` |
| [0001-06](06-incremental-derive.md) | incremental-derive | `verified` |
| [0001-07](07-plan-situation.md) | plan-situation | `verified` |
| [0001-08](08-language-policy.md) | language-policy | `verified` |
| [0001-09](09-guideline-manifest.md) | guideline-manifest | `verified` |
| [0001-10](10-guideline-registry.md) | guideline-registry | `verified` |
| [0001-11](11-activation-audit.md) | activation-audit | `verified` |
| [0001-12](12-plan-size-field.md) | plan-size-field | `verified` |
| [0001-13](13-plan-formats.md) | plan-formats | `verified` |
| [0001-14](14-derive-by-size.md) | derive-by-size | `verified` |
| [0001-15](15-size-instrumentation.md) | size-instrumentation | `verified` |
| [0001-16](16-plugin-package.md) | plugin-package | `verified` |
| [0001-17](17-reconcile-consumers.md) | reconcile-consumers | `verified` |
| [0001-18](18-reopen-agent-decision.md) | reopen-agent-decision | `verified` |
| [0001-19](19-planner-agent.md) | planner-agent | `verified` |
| [0001-20](20-developer-agent.md) | developer-agent | `verified` |

20 de 21 derivadas · 20 verificadas · atualizado em 2026-08-26
<!-- backlog:end -->

## Fonte

- Medições de 2026-08-21 sobre `dev` = `8395030`: `.claude/settings.json`, `wc -l .claude/CLAUDE.md`,
  `find docs/plan -type d -name system`, `grep -ro "dev-units"`, e `gh api` + `diff` contra
  `futureridetoday/AmFlowPlugins`
- Norma do modelo: [`modelo-dev-units.md`](../../system/modelo-dev-units.md), seções *Camada normativa*
  e *Avaliação de escopo*
- Backlog: `AmFlow:docs/plan/_inbox/_backlog.md`, itens `B-01` e `B-02`
- Documentação do Claude Code: memória e regras (`.claude/rules/`, frontmatter `paths:`, symlinks e
  a ressalva de Cowork), referência de plugins (componentes empacotáveis), e o material de orientação
  sobre quando usar `CLAUDE.md`, skill, hook ou subagent
- Medições de **2026-08-22** sobre a doc do Claude Code: catálogo de eventos de hook e canais de saída
  (`InstructionsLoaded`, `SubagentStart`, `systemMessage`, `additionalContext`), confirmação do
  frontmatter `paths:` em `.claude/rules/`, gatilho por leitura, e comportamento após compactação
- Ponto de partida conceitual: guideline `decode_code` do repositório `futureridetoday/CortexMachine`
  — aproveitados o fluxo `Clarificar → Evitar → Reduzir`, os Gates A/B, o princípio *código é custo* e
  o protocolo de exceção. **Não** aproveitados os limites numéricos dos Gates 1–5 (derivados de outro
  domínio) nem o catálogo de padrões Python de ML/scheduler (fora do stack do AmFlow)
