---
# about
name: persona-ablation-spike
type: plan
project: DecodeAndCode
description: Spike que mede, às cegas e com regra de decisão fixada antes, se a frase de persona acrescenta algo ao protocolo de julgamento no formato C+D que o 0022 deu à feature persona, com um braço novo (protocolo sem persona) e as saídas de A e C+D do 0022 reaproveitadas
tags: [decode-and-code, spike, persona, camada-normativa]

# alvo
plan_id: "0023"
plan_size: pequeno
plan_type: spike
core: model
module: persona-ablation-spike
block: ""

# history
author: Claude
created: 2026-11-23
status: done
version: 1.0.0
updated: ""
approved_by: Bortoli
approved_at: 2026-11-23

# system
scope: project
auto_load: false
dependencies: []
---

# Spike — a persona acrescenta algo ao protocolo?

**Numeração.** Aprovado como `0022` e renumerado para `0023` em 2026-11-24, antes do merge, junto com
o `persona-spike` (`0021` → `0022`), porque o `0021` do `dev` já era o `fix-packaged-norm-links`
(huddle `H-02`). As citações, inclusive as do registro da revisão em `L-03`, usam os números novos.

**Autoria.** Continuação do [`0022-persona-spike`](0022-persona-spike.md), `D-01`. O
desenho abaixo foi aprovado pela pessoa na conversa de 2026-11-23, e este esboço só o registra. O
que foi conferido nesta sessão está marcado como *conferido*.

## Objetivo

**Clarificar.** Pela regra do `0022`, a feature `persona` entra no formato C+D: persona com teoria
nomeada mais protocolo de julgamento (`D-01`). A persona sozinha (C) não superou o controle (A), e o
braço D sozinho — protocolo sem persona — foi cortado no desenho do `0022`, que por isso não separou
o efeito do protocolo do efeito da persona dentro do C+D. Métrica: a ordem de nove saídas avaliadas
às cegas (3 A, 3 C+D, 3 D), lida pela regra de decisão abaixo. Beneficiário: a pessoa que desenha o
plano da feature e decide se o arquivo dela carrega a frase de especialista.

**Evitar.**

| Alternativa | Por que não basta |
|---|---|
| Ficar com o C+D que a regra do `0022` deu | O próprio `D-01` registra que o dado não separa protocolo de persona; a frase entraria sem medida (*Evidência acima de opinião*) |
| Tirar a frase porque C não venceu A | C sozinho não vencer A não mostra que a frase nada acrescenta junto do protocolo. Seria decidir por leitura, como o `P-06` fez (Gate A do `0022`) |
| Refazer o `0022` com quatro braços | Geraria de novo seis saídas que já existem, nas mesmas condições |

**Reduzir.** Um braço novo, três rodadas, uma ordenação de nove saídas às cegas, com as seis de A e
C+D reaproveitadas do `0022`. Nenhum código de produção.

## Gates

| Gate | Resposta |
|---|---|
| **A — necessidade real** | **Sim.** O `D-01` do `0022` deixou a pergunta em aberto e a nomeou como condição do plano da feature, antes de decidir se o arquivo carrega a frase de especialista. O plano da feature é o próximo passo, e o conteúdo do arquivo dele depende desta resposta. Decidir sem medir contraria *Evidência acima de opinião* |
| **B — mínimo viável** | Cortado: gerar de novo as saídas de A e C+D, reaproveitadas do `0022`; o braço C na ordenação, que não venceu A no `0022`; código de produção e qualquer arquivo nas fontes do pacote (`_fontes()`, `empacotar.py:106`); scripts versionados (`L-04` do `0022`); o Opus como executor, mais rodadas e mais tarefas. O desenho da feature fica fora: nasce num plano próprio, depois deste |

## Pergunta

Com a teoria nomeada no pedido e o protocolo de julgamento carregado, a frase de especialista
acrescenta algo à saída? A resposta decide se o arquivo da feature `persona` carrega essa frase.

**Destino da resposta:** `## Decisões` deste plano. Se a feature entrar, o desenho dela nasce num
plano próprio, depois deste.

## Experimento

**O que vem do `0022`, sem cópia.** A tarefa, o texto da tarefa, o briefing e o texto do braço C+D
têm fonte única no `0022`, seção *Experimento*. Este plano os cita, não os repete.

**Braço novo D** (texto anexado ao system prompt): o bloco do braço C+D do `0022` sem a primeira
linha — a frase "Atue como especialista em primal branding, dominando todos os fundamentos da
teoria." — e sem a linha em branco que a segue. O texto de D começa em "Protocolo de julgamento —" e
segue igual ao do C+D até o fim do bloco.

**Saídas na ordenação:**

| Braço | Saídas | Origem |
|---|---|---|
| A | 3 | `0022`: `s1`, `s2` e `s5`, reaproveitadas |
| C+D | 3 | `0022`: `s3`, `s6` e `s7`, reaproveitadas |
| D | 3 | novas, geradas neste spike |

As saídas de A e C+D são reaproveitadas porque foram geradas nas condições que D vai ter: mesma
tarefa, mesmo briefing, mesmo modelo e mesmas flags.

**Execução de D.** Igual à do `0022` (`D-01`, *Execução*): `claude -p --safe-mode --model
claude-sonnet-5-5 --output-format json --append-system-prompt <braço D>`, com a tarefa e o briefing
como prompt, cada execução num diretório descartável, três rodadas. O modelo vai pelo nome completo,
o mesmo que respondeu no `0022`, e não pelo alias (`L-02`). O nome do modelo que respondeu entra no
registro. *Conferido*: `claude --version` responde 2.1.330, a mesma versão do `0022`.

**Avaliação.** As nove saídas são re-rotuladas às cegas, com semente nova, e a chave fica à parte
até a ordenação terminar. O juiz é o do `0022`: o Opus numa sessão nova, com `claude -p --safe-mode
--model claude-opus-5-5 --output-format json` (`L-02`), em diretório descartável, sem conhecer o protocolo nem a
conversa que desenhou o spike, com a mesma instrução e os mesmos três critérios, em três julgamentos
com as saídas em ordens diferentes (sementes 1, 2 e 3). A regra de decisão se aplica à ordem pela
posição média nos três julgamentos. O Claude da sessão que orquestra não ordena.

Instrução do juiz, a mesma do `0022` (`L-01`). No prompt, vem seguida de `=== BRIEFING ===` com o
briefing e de um bloco `=== ESTRATÉGIA <rótulo> ===` por saída:

```text
Você vai avaliar nove estratégias de marca escritas para o mesmo briefing, todas pedidas com a teoria de primal branding (Patrick Hanlon). Ordene as nove da melhor para a pior.

Critérios, em ordem de peso:
1. Profundidade da teoria aplicada ao caso: os elementos do primal branding resolvem o problema desta marca, em vez de aparecerem listados.
2. Uso dos fatos do briefing: a estratégia se apoia no que o briefing diz sobre a marca.
3. Execução: dá para agir a partir dela dentro das restrições do briefing.

O tamanho do texto não é critério: não favoreça a resposta mais longa.

Responda só com um objeto JSON, sem texto antes ou depois, neste formato:
{"ordem": ["sX", ...nove ids, da melhor para a pior...], "motivo": {"sX": "uma frase", ...}}
```

**Regra de decisão, fixada antes.** Um braço vence outro só se as três saídas dele ficarem acima das
três do outro, na ordem pela posição média. Qualquer outro resultado é empate, e no empate fica o
mais barato (*Subtração antes de adição*).

1. Só concorre ao formato quem vence A nesta ordenação.
2. Se D e C+D vencem A: C+D só fica se vencer D; senão fica D, o protocolo sem persona, mais barato.
3. Se só um vence A, a feature tem o formato dele.
4. Se nenhum vence A, o resultado contradiz o `0022`: registra-se como inconclusivo, sem decidir o
   formato.

Sem diferença real entre os braços, a chance de C+D vencer D só por acaso é de 1/20 (5%).

**Arquivos.** As saídas novas, a chave e os julgamentos ficam fora do repositório, como no `0022`
(`L-05` dele). O plano registra os comandos, as sementes, a chave depois de aberta e o nome completo
do modelo.

## Oráculo

A decisão registrada em `## Decisões`: o resultado que a regra deu, a ordenação, a chave, os
comandos com as sementes e o nome completo dos modelos que responderam. Quem executa é a sessão que
orquestra, sem `implement` (*Tipo de plano*, `spike`).

## Limitações

- Continuam valendo as do `0022`: protocolo, briefing e critérios do juiz têm o mesmo autor; o juiz
  é da mesma família de modelos; são três saídas por braço.
- As saídas reaproveitadas foram geradas em outra rodada de execução, no mesmo dia e com a mesma
  configuração.

## Lacunas

| # | Lacuna | Detalhe |
|---|---|---|
| L-01 | **A instrução do juiz do `0022` não está versionada** | *Conferido*: o `0022` registra os três critérios, não o texto que o juiz recebeu, e a pasta do experimento não o guarda. O texto existe só no script do juiz, no diretório temporário da sessão (scratchpad), que um reboot pode apagar. Sem ele, "juiz igual ao do `0022`" não se confere. Este esboço grava o texto em *Avaliação*, copiado do script; a pessoa confirma ou corta na aprovação. A `L-04` do `0022` vetou versionar scripts, não textos de entrada. **Fechada em 2026-11-23**, antes da aprovação, por decisão da pessoa: o texto fica em *Avaliação* |
| L-02 | **`--model sonnet` e `--model opus` são aliases** | O `0022` registra que o alias aponta para a versão mais recente. Se ele mudar antes de D rodar, as saídas reaproveitadas deixam de ter as mesmas condições, e o juiz também. Opções: fixar no comando o nome completo dos modelos que responderam no `0022` (`claude-sonnet-5-5`, `claude-opus-5-5`), ou manter o alias e conferir o modelo que respondeu, parando se divergir. Decisão da pessoa, na aprovação. **Fechada em 2026-11-23**, antes da aprovação, por decisão da pessoa: os comandos fixam `claude-sonnet-5-5` e `claude-opus-5-5` (ver *Execução de D* e *Avaliação*) |
| L-03 | **O `0022` segue `em desenvolvimento` no mesmo core** | *Conferido* (`dc.py concorrencia`, com os scripts deste checkout): `\| 0022 \| [persona-spike](model/0022-persona-spike.md) \| model \| persona-spike \| — \| em desenvolvimento \| 2026-11-23 \|`. Este plano depende do `D-01` do `0022` e reaproveita as saídas dele. Pela norma (*Avaliação de escopo → A checagem — concorrência*), o plano novo espera ou se declara dependente. O `0022` já tem o resultado em `## Decisões`, mas o `status` dele continua `approved`; no porte pequeno, quem grava `status: done` é o humano. Revisão de 2026-11-23. **Fechada em 2026-11-23**, antes da aprovação, por decisão da pessoa: o `0022` recebeu `status: done`, a situação foi projetada como `concluído` em `_planos.md`, e o `concorrencia` passou a responder "sem conflito" |

## Decisões

| # | Decisão |
|---|---|
| D-01 | **A frase de especialista não entra: a feature fica com o formato do braço D**, o protocolo de julgamento sem persona, pela regra fixada antes. Registrada em 2026-11-24. D e C+D vencem A, nenhum dos dois vence o outro, e o empate fica com o mais barato |
| D-02 | **A pessoa decidiu seguir para o plano da feature sem medir a própria expectativa**, em 2026-11-24, depois de ver a circularidade descrita em *Leitura*. A ordenação às cegas pela pessoa (3 saídas de A contra 3 de D) foi oferecida e recusada; a evidência segue com a circularidade registrada |

### D-01 — resultado

Ordem pela posição média nos três julgamentos, com a chave aberta:

| Posição | Saída | Braço | Origem | Posições nos julgamentos 1, 2 e 3 | Palavras |
|---|---|---|---|---|---|
| 1 | s1 | D | `0023`, rodada 1 | 2, 2, 1 | 963 |
| 2 | s3 | D | `0023`, rodada 3 | 1, 3, 2 | 850 |
| 3 | s5 | C+D | `0022`: `s7` | 5, 1, 4 | 960 |
| 4 | s8 | C+D | `0022`: `s6` | 3, 4, 5 | 900 |
| 5 | s9 | C+D | `0022`: `s3` | 4, 6, 3 | 907 |
| 6 | s4 | D | `0023`, rodada 2 | 6, 5, 6 | 877 |
| 7 | s6 | A | `0022`: `s1` | 7, 7, 7 | 957 |
| 8 | s2 | A | `0022`: `s5` | 9, 8, 8 | 925 |
| 9 | s7 | A | `0022`: `s2` | 8, 9, 9 | 816 |

**A regra.** Passo 1: D e C+D vencem A, porque as seis saídas com protocolo estão nas posições 1 a
6 e as do A, em 7 a 9. Passo 2: C+D não vence D, porque duas saídas do D estão acima das três do
C+D; e D também não vence C+D, porque `s4`, do D, ficou em sexto. É empate, e fica o mais barato:
o D, sem a frase de especialista.

**Estabilidade.** Julgamento por julgamento, o resultado se repete nos três: D e C+D vencem A, e
nenhum dos dois vence o outro.

**Leitura.**

- Junto com o `D-01` do `0022`: a frase de especialista não mudou a avaliação nem sozinha (C contra
  A) nem junto do protocolo (C+D contra D). O que separa as saídas é o protocolo de julgamento, e
  a separação contra o controle foi completa nos três julgamentos.
- O que entra no plano da feature é o protocolo de julgamento: perguntas antes de decidir,
  trade-offs, o que conta como evidência e modos de falha. O nome `persona` é da pessoa; o dado
  não sustenta uma persona como o conteúdo da feature.
- Nenhuma saída revelou o braço pela abertura: as nove começam por "## 1. Crença central". As seis
  com protocolo usam "hipótese"; as três do A, não. O juiz não conhecia o protocolo.
- A ordem não acompanha o tamanho: a saída mais curta com protocolo (`s3`, 850 palavras) ficou em
  segundo.
- **Circularidade.** Os motivos do juiz (`juiz/j1.json` a `j3.json`) premiam o que o protocolo
  manda fazer: o teste do credo que um concorrente poderia assinar, o não crente como visão de
  mundo oposta, a separação entre fato e hipótese, e a penalidade a quem lista os elementos. O
  protocolo e os critérios do juiz têm o mesmo autor, então parte da vitória é o juiz medindo o
  protocolo por ele mesmo. Os motivos também apontam erros do A que não dependem do protocolo:
  gastar de 20% a 35% da verba em identidade antes da decisão do aporte, prometer prazo de
  afiação sem capacidade nova, inventar nomes de linha. O efeito do protocolo está nesses erros de
  julgamento sob restrição; a qualidade do A não é baixa.
- Valem as *Limitações* deste plano e as do `0022`.

**Execução.**

- Braço D: `claude -p --safe-mode --model claude-sonnet-5-5 --output-format json
  --append-system-prompt <braço D>`, com tarefa e briefing do `0022` como prompt, três execuções em
  paralelo, cada uma num diretório descartável. Modelo que respondeu: `claude-sonnet-5-5`.
- Re-rotulagem das nove saídas: semente 22.
- Juiz: `claude -p --safe-mode --model claude-opus-5-5 --output-format json`, com a instrução de
  *Avaliação*, o briefing e as nove saídas como prompt, sementes 1, 2 e 3 para a ordem de
  apresentação. Modelo que respondeu nos três: `claude-opus-5-5`.
- **Interrupção.** A primeira execução gerou o D, re-rotulou as saídas, gravou o julgamento 1 e
  parou no limite de uso de 5 horas da assinatura. A retomada, em 2026-11-24, rodou só os
  julgamentos 2 e 3, sobre as mesmas saídas e a mesma chave; o D não foi gerado de novo.
- As saídas, a chave e os julgamentos ficam fora do repositório (`L-05` do `0022`).

## Fonte

- [`0022-persona-spike.md`](0022-persona-spike.md): *Experimento*, *Limitações*, `L-04`,
  `L-05` e `D-01`
- [`modelo-dev-units.md`](../system/modelo-dev-units.md), seções *Antes do plano*, *O que cada porte
  carrega* e *Tipo de plano*
- [`principles.md`](../../../.claude/rules/principles.md): *Subtração antes de adição* e *Evidência
  acima de opinião*
- `claude --version`, 2.1.330
