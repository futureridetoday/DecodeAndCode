---
# about
name: add-judgment-protocol
type: plan
project: DecodeAndCode
description: A camada normativa ganha o protocolo de julgamento — como decidir numa atividade —, que vive como skill do projeto e ativa por invocação, por `skills:` num agent ou pela guideline-ponte; a norma define o que ele é, o formato e o teste que o separa das outras camadas, sem código novo
tags: [decode-and-code, norma, camada-normativa, protocolo, skill]

# alvo
plan_id: ""
plan_size: pequeno
plan_type: norma
core: model
module: add-judgment-protocol
block: ""

# history
author: Claude
created: 2026-11-24
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

# A camada normativa ganha o protocolo de julgamento

> **Tipo proposto: `norma`**: o carregamento por atividade já existe no Claude Code (skill), e o que
> falta é a norma dizer o que a camada é, onde vive e como ativa; nenhum arquivo de código. **Porte
> proposto: `pequeno`**: pela *Quando cada porte cabe*, é uma mudança só (pergunta 1, sim), uma
> subseção nova e duas linhas na *Camada normativa*. O humano confirma tipo e porte na aprovação.
> **[Claude]**
>
> **Autoria.** **[humano]** decisão da pessoa, **[Claude]** recomendação ainda não confirmada,
> **[medido]** fato medido, com o arquivo, o comando ou a página.
>
> **Numeração.** Os spikes citados são `persona-spike` (`0022`) e `persona-ablation-spike` (`0023`),
> renumerados em 2026-11-24 antes do merge, porque o `0021` do `dev` já era o
> `fix-packaged-norm-links` (huddle `H-02`). Este esboço os cita pelo nome.

## Escada — onde o protocolo carrega

O pedido cabe em duas leituras: recurso do Claude Code (como carregar texto conforme a atividade) e
trabalho do método (onde a camada vive na norma). A pessoa já escolheu o destino `_inbox`
**[humano]**. A escada responde à primeira leitura e alimenta o *Evitar* da segunda. **[Claude]**

| Degrau | Resolve? | Por quê |
|---|---|---|
| Nada | Em parte | O mecanismo existe, e a pessoa já o usa: o AmFlow e outro projeto dela têm skills de domínio, descritas por atividade ("Use when o usuário precisa desenhar a camada de dados…", `AmFlow/.claude/skills/data-architecture/SKILL.md:5`) **[medido]**. Falta a norma: o que vai nessas skills, e o que não vai |
| Instrução (rule) | Não | Sem `paths:`, carrega em toda sessão e conta no teto de princípios (`modelo-dev-units.md:240-242`). Com `paths:`, entra quando o Claude **lê** um arquivo que casa (`0001`, *Ativação silenciosa é o modo de falha da própria camada*), e o planejamento ainda não leu arquivo |
| Hook | Não | Atividade não tem evento nativo. Um `UserPromptSubmit` que injete o protocolo por palavra-chave é heurística em código, com o mesmo risco da descrição de skill e o custo de *Código é custo* |
| **Skill** | **Sim: a escada para aqui** | **[medido]** em code.claude.com: o corpo só carrega quando a skill é usada, e a descrição fica no contexto, limitada a 1.536 caracteres (*skills*, *Frontmatter reference*). Ativa por `/nome` na sessão principal. Num agent, `skills:` injeta o corpo inteiro no início, até 32 nomes, então o protocolo combina com o papel de qualquer agent (*sub-agents*, *Preload skills*). Depois da compactação, a última invocação volta com os primeiros 5.000 tokens (*skills*, *Skill content lifecycle*). Para atividade ligada a caminho, a guideline-ponte já leva o recurso ao `derive` e ao `implement` (`modelo-dev-units.md:1494-1497`, medida no `0017`) |
| Agent | Não | Contexto isolado não é requisito. Agent é papel e processo, nunca a norma: ele declara a skill em `skills:` (`modelo-dev-units.md:1188-1190`). É quem consome o protocolo, não o lugar onde ele mora |

## Objetivo

**Clarificar.** A camada normativa não tem lugar para *como decidir conforme a atividade*.
Princípio carrega sempre, não depende de domínio e tem teto de 5 (`modelo-dev-units.md:228` e
`:240`). Guideline prescreve a resposta e entra pelo caminho do arquivo (`:263-283`). O conteúdo
que os dois spikes mediram como ingrediente ativo, o protocolo de julgamento, fica sem lugar
(`D-01` do `persona-spike` e do `persona-ablation-spike`). **Métrica de entrega:** a norma diz o que
o protocolo é, onde vive, como ativa e que formato tem. Hoje não diz: `grep -n "protocolo de
julgamento" docs/plan/system/modelo-dev-units.md` volta vazio **[medido]**. **Métrica de efeito**,
mensurável só com a primeira instância: o resultado de uma atividade com protocolo mostra as
perguntas dele respondidas. **Beneficiário:** a pessoa que escreve a norma de um projeto, e o
Claude que planeja ou desenvolve numa atividade que tem protocolo.

**Evitar.**

| Alternativa | Por que não basta |
|---|---|
| Princípio (rule sem `paths:`) | Conta no teto de 5 (`:240-242`). O primeiro recorte o quer independente de domínio (`:228`). Carrega em toda sessão: o protocolo de marca entraria numa sessão de código |
| Guideline (rule com `paths:`) | Prescreve a resposta, não as perguntas, e entra por leitura de arquivo. Continua servindo de ponte para atividade ligada a caminho, sem mudança (guideline-ponte) |
| Output style | Um por sessão, vale para toda resposta, e chega só à sessão principal e ao fork: os outros subagents rodam o próprio system prompt **[medido]** (code.claude.com, *output-styles*, *How output styles work*). Não combina com outro agent |
| Hook por palavra-chave | Ver a escada: é heurística em código |
| Agent especialista por protocolo | Ver a escada: o agent consome o protocolo por `skills:` |
| A frase de persona ("atue como especialista em X") | Sem efeito medível, nem sozinha nem junto do protocolo (`D-01` do `persona-ablation-spike`) |
| Nada na norma: cada projeto escreve a skill | Resolve uma instância, e o vão de `:223` continua aberto. **[medido]** Nas quatro skills de domínio lidas, duas do AmFlow e duas do outro projeto, a regra já decidida ("Invariantes", "Stack decidida", "Definition of Done") vem misturada com a orientação, e nenhuma tem seção de perguntas antes de decidir. Sem o teste e o formato na norma, o próximo protocolo nasce como guideline dentro de skill |

**Reduzir.** Uma subseção `#### Protocolo` na *Camada normativa*, uma linha na tabela de elementos e
uma frase em *Princípio* que aponta para ela. Nenhum código, script, lint ou skill do método muda.
**[Claude]**

## Gates

| Gate | Resposta |
|---|---|
| **A — necessidade real** | **Sim, com base estreita, só para a versão sem código, somada à exigência explícita da pessoa** (protocolo de exceção, *exigência explícita*) **[humano]**. **[medido]** No `persona-spike`, as três saídas de C+D ficaram acima das três de A nos três julgamentos, e C não venceu A. No `persona-ablation-spike`, as seis saídas com protocolo ficaram acima das três de controle nos três julgamentos, e a frase de persona não fez diferença. **Ressalvas:** a evidência é circular em parte, porque o juiz premiou o que o protocolo manda e os dois têm o mesmo autor (*Leitura* do `persona-ablation-spike`); a pessoa seguiu sem medir a própria expectativa (`D-02` do mesmo plano); o briefing é fictício. **Sem dor medida em projeto:** nenhum projeto tem protocolo hoje, e nenhum projeto sob `~/Code` concluiu o setup (`ls ~/Code/*/docs/plan/system/setup.md` vazio) **[medido]**. Por isso o A não cobre nada que precise de instância para existir (ver B) |
| **B — mínimo viável** | **[Claude]** Cortado, porque não há instância que o justifique: lint de formato do protocolo; escritor `dc.py criar-protocolo` e `archive`/`restore` de protocolo; protocolo no setup e no `rethink`; check do `review-plan` sobre as respostas; uma linha no `intake` mandando invocar o protocolo (`P-03`); registro da invocação no log de uso (o `InstructionsLoaded` não vê skill); teto numérico de protocolos (o que carrega sempre é a descrição, e a listagem de skills já tem orçamento próprio); hook de ativação; output style; agent; a frase de persona; mudanças no título da seção *Camada normativa*, no `plugin.json`, no `marketplace.json` e no `README.md`, que descrevem o que o plugin cria e edita, e o plugin não cria protocolo. Gatilho comum: o primeiro protocolo em uso num projeto, com o caso registrado em `L-XX` ou `H-XX` |

## Solução

**[Claude]** Só `docs/plan/system/modelo-dev-units.md`:

1. *Camada normativa*, tabela de elementos (`:190-195`): uma linha **Protocolo**, "como decidir numa
   atividade", com um exemplo curto ("estratégia de marca: quem não acredita na marca, e o que ela
   perderia tentando agradá-lo?").
2. *Princípio* (`:223-224`): depois de "Princípio é sobre como decidir; guideline, sobre o que
   decidir", uma frase: o *como decidir* que depende da atividade é protocolo, e não princípio
   (subseção *Protocolo*).
3. Subseção nova `#### Protocolo`, entre *Guideline* e *Editar e arquivar*, com:
   1. **O que é.** As perguntas obrigatórias antes de decidir, os trade-offs e como pesá-los, o que
      conta como evidência, em ordem de peso, os modos de falha registrados e a checagem antes de
      responder. Não leva regra (guideline), limite (guardrail), conhecimento geral (modelo ou
      *Referência*), tom (voz) nem persona.
   2. **O teste que o separa.** Tirando o protocolo, o que muda? Se só o tom, é voz; se a resposta,
      é guideline; se as perguntas feitas antes da resposta, é protocolo.
   3. **Subordinação.** O protocolo vale abaixo dos princípios. Protocolo que contradiz princípio é
      defeito do protocolo.
   4. **Onde vive.** Uma skill do projeto, `.claude/skills/<nome>/SKILL.md`, com a `description`
      dizendo **quando** vale, isto é, a atividade. Sem `context: fork`, porque o protocolo precisa
      entrar no contexto de quem decide. Sem `disable-model-invocation: true`, que impede a
      pré-carga em agent. É instância, e nunca viaja no plugin.
   5. **Como ativa.** Três vias não dependem de o modelo reconhecer a atividade: `/nome` na sessão
      principal; `skills:` no agent especialista, que pré-carrega o corpo e combina com outras
      skills; e a guideline-ponte, para atividade ligada a caminho. A quarta via, a descrição
      casando com o pedido, depende do modelo e falha em silêncio: protocolo que não carregou
      produz o mesmo sintoma de protocolo ignorado (`0001`, *Ativação silenciosa*). O `intake`,
      que roda em fork, só alcança o protocolo por essa quarta via (`P-03`).
   6. **Custo de contexto.** Vale o raciocínio do teto, aplicado ao que carrega sempre: a descrição.
      O corpo cabe nos 5.000 tokens que a compactação devolve, com as perguntas no topo.
   7. **Verificação.** O resultado mostra as perguntas do protocolo respondidas; num plano, na seção
      que o protocolo nomeia. A ausência delas é o sinal de que ele não carregou, e torna visível a
      falha da quarta via. Quem revisa o resultado faz essa conferência.
   8. **Evolução.** Entra e muda por plano do tipo `norma`, com aprovação humana. Um modo de falha
      novo nasce de `L-XX` ou `H-XX`. O setup e o `rethink` ainda não o criam nem o editam (Gate B).
   9. **Origem.** `D-01` do `persona-spike` e do `persona-ablation-spike`, com a circularidade
      registrada na *Leitura* do segundo. O formato em uso difere do medido em dois pontos, aceitos
      sem medir (`P-02`): o veículo, que nos spikes foi o system prompt e aqui é a skill; e a
      visibilidade, que nos spikes foi oculta e aqui deixa as respostas à vista.

## Decisões

### Pendentes de decisão

As três decididas pela pessoa em 2026-11-24 **[humano]**: P-01 com nome próprio, P-02 e P-03
aceitando a recomendação do Claude.

| # | Pergunta | Recomendação |
|---|---|---|
| P-01 | Que nome a camada recebe? | O nome `persona` é da pessoa, e é dela a decisão. **Recomendação:** *protocolo de julgamento* na prosa e `judgment-protocol` como identificador (este plano: `add-judgment-protocol`), porque o dado sustenta o protocolo, e não a persona, como conteúdo (`D-01` do `persona-ablation-spike`). Custo: a palavra *protocolo* já nomeia o *protocolo de exceção* em `principles.md`; o qualificador *de julgamento* os separa. **Decidida em 2026-11-24 pela pessoa** **[humano]**: *protocolo de julgamento* na prosa, `judgment-protocol` como identificador |
| P-02 | O formato em uso difere do medido em dois pontos. Aceitar sem medir? | **Recomendação: aceitar, e registrar na própria subseção.** O primeiro ponto é o veículo: os spikes anexaram o protocolo por `--append-system-prompt`, e a skill invocada ou pré-carregada não foi medida. O segundo é a visibilidade: o protocolo medido mandava não citá-lo, para manter o juiz cego, e a verificação (item 3.7) pede as respostas à vista. Gatilho para medir: o primeiro protocolo em uso cujo resultado a pessoa julgue igual ao sem protocolo. **Alternativa:** medir o veículo antes, com o braço D carregado como skill, três rodadas contra as três saídas de A do `persona-spike`, com o mesmo juiz. A visibilidade não se mede às cegas, porque as respostas à vista denunciam o braço. **Decidida em 2026-11-24 pela pessoa** **[humano]**: aceitar sem medir, e registrar a diferença na subseção (*Solução*, item 3.9) |
| P-03 | O `intake` roda em fork. Como o protocolo chega até ele? | **Recomendação: aceitar o limite.** Subagent não herda a skill invocada na conversa principal (code.claude.com, *sub-agents*), e o `intake` não tem caminho de arquivo para a ponte; só a descrição o alcança. O `implement` recebe pela guideline-ponte (`0017`). Gatilho: o primeiro esboço de uma atividade com protocolo em que as perguntas dele faltem. **Alternativa:** uma linha no `intake/SKILL.md` mandando invocar a skill de protocolo do projeto cuja descrição case com o pedido. **Decidida em 2026-11-24 pela pessoa** **[humano]**: aceitar o limite, e registrá-lo na subseção (*Solução*, item 3.5) |

## Oráculo

Tipo `norma`: aprovação humana do texto (`approved_by`/`approved_at`). Conferível no diff:

- `grep -n "^#### Protocolo" docs/plan/system/modelo-dev-units.md` acha a subseção entre
  *Guideline* e *Editar e arquivar*, e a tabela da *Camada normativa* tem a linha **Protocolo**.
- *Princípio* cita a subseção.
- `git diff --stat` lista só `docs/plan/system/modelo-dev-units.md` e o próprio plano. Nenhum
  arquivo de código.
- `bash scripts/test-python.sh` verde: `test_normas_system.py` confere os links relativos da norma.

## Limitações

- A evidência é de dois spikes com o mesmo autor no protocolo, no briefing e nos critérios do juiz,
  com um juiz da mesma família de modelos e três saídas por braço. A circularidade está na *Leitura*
  do `persona-ablation-spike`.
- O formato que a norma recomenda vem de um protocolo só, genérico, deduzido da teoria pelo Claude,
  e não de casos vividos (*Limitações* do `persona-spike`).
- A quarta via de ativação continua sem garantia. A verificação torna a falha visível só para quem
  confere o resultado.
- A skill também aceita `paths:` (code.claude.com, *skills*), o que daria ativação por caminho sem
  guideline-ponte. Isso não foi medido no método, e a subseção não o recomenda.

## Fonte

- [`modelo-dev-units.md`](../system/modelo-dev-units.md): *Camada normativa* (`:186-283`), *Antes do
  plano*, *O que cada porte carrega*, *Quando cada porte cabe*, *Tipo de plano*, *Modelos*
  (`:1182-1198`) e *Setup* (`:1494-1497`)
- [`0022-persona-spike.md`](../model/0022-persona-spike.md) e
  [`0023-persona-ablation-spike.md`](../model/0023-persona-ablation-spike.md): *Decisões*, *Leitura*
  e *Limitações*
- [`0001-decode-and-code-foundation.md`](../model/0001-decode-and-code-foundation/0001-decode-and-code-foundation.md),
  *Ativação silenciosa é o modo de falha da própria camada*
- [`principles.md`](../../../.claude/rules/principles.md): *Código é custo*, *Subtração antes de
  adição*, *Evidência acima de opinião* e *Protocolo de exceção*
- code.claude.com, lido em 2026-11-24: `docs/en/skills` (*Frontmatter reference*, *Skill content
  lifecycle*, *Skill not triggering*), `docs/en/sub-agents` (*Preload skills*) e
  `docs/en/output-styles` (*How output styles work*)
- `AmFlow/.claude/skills/data-architecture/SKILL.md` e `digital-twin-product/SKILL.md`, lidos em
  2026-11-24
