---
# about
name: persona-spike
type: plan
project: DecodeAndCode
description: Spike que mede, às cegas e com regra de decisão fixada antes, se carregar uma persona muda a saída do Sonnet além do que nomear a teoria no pedido já faz, e se o arquivo da persona precisa trazer um protocolo de julgamento ou basta a persona
tags: [decode-and-code, spike, persona, camada-normativa]

# alvo
plan_id: "0022"
plan_size: pequeno
plan_type: spike
core: model
module: persona-spike
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

# Spike — carregar uma persona muda a saída?

**Numeração.** Aprovado como `0021` e renumerado para `0022` em 2026-11-24, antes do merge, porque o
`0021` do `dev` já era o `fix-packaged-norm-links` (huddle `H-02`). As citações foram atualizadas.

**Autoria.** O desenho abaixo foi aprovado pela pessoa na conversa de 2026-11-23, e este esboço só
o registra. São dela o nome `persona` e o relato de experiência. O protocolo do braço C+D foi
rascunhado pelo Claude e aceito pela pessoa sem correção, em 2026-11-23. O briefing, fictício, foi
escrito pelo Claude a pedido da pessoa, na mesma data. O que foi conferido nesta sessão está marcado como
*conferido*.

## Objetivo

**Clarificar.** A camada normativa separa **como decidir** (princípio, sempre carregado) de **o que
decidir** (guideline, ativada por `paths:`), em
[`modelo-dev-units.md:223`](../system/modelo-dev-units.md). Falta o canto *como decidir, conforme o
contexto ou a atividade*:

| | Sempre | Conforme o contexto |
|---|---|---|
| **Como decidir** | princípio | — (a hipótese `persona`) |
| **O que decidir** | — | guideline |

A hipótese para esse canto é uma feature `persona`: carrega uma persona com teoria nomeada e,
talvez, um protocolo de julgamento, com as perguntas obrigatórias antes de decidir, os trade-offs,
o que conta como evidência e os modos de falha registrados. A evidência hoje aponta para os dois
lados, e nenhuma é medição deste repositório (ver Gate A). Métrica: a ordem das nove saídas,
avaliadas às cegas, lida pela regra de decisão abaixo. Beneficiário: a pessoa que decide se a
feature entra no método.

**Evitar.**

| Alternativa | Por que não basta |
|---|---|
| Decidir pela experiência relatada | É relato, não medição, e o estudo citado aponta o contrário |
| Decidir pelo estudo (Zheng et al., 2023) | Mede persona genérica em pergunta factual. Aqui a persona tem teoria nomeada, e a tarefa é de julgamento |
| Construir a feature e observar no uso | Pagaria o código antes de saber se ele elimina dor (*Código é custo*) |

**Reduzir.** Três braços, três rodadas por braço, uma tarefa, um modelo e uma ordenação às cegas.
Nenhum código de produção.

## Gates

| Gate | Resposta |
|---|---|
| **A — necessidade real** | **Sim para o spike, com base estreita. A feature não passa no A hoje, e é isso que o spike mede.** *Conferido* (`grep -ri persona`): o repositório já decidiu sobre persona uma vez por leitura, sem medir. O `P-06` do `_inbox/apply-plugin-review.md` tirou a persona do `ai-builder` porque, "na leitura do revisor", ela ajuda pouco. O benchmark do `0001` registra que os agents `feature-dev` da Anthropic abrem com persona. Somam-se o relato da pessoa a favor e o estudo citado contra. São quatro sinais, nenhum medido aqui. Decidir a feature sem medir contraria *Evidência acima de opinião* |
| **B — mínimo viável** | Cortado: código de produção, e qualquer arquivo nas fontes do pacote (`_fontes()`, `empacotar.py:106`). Nenhum script do experimento é versionado. Cortado também o Opus, que fica registrado como limitação, assim como mais rodadas e mais tarefas. O desenho da feature fica fora: se ela entrar, nasce num plano próprio. O briefing e o protocolo são insumos da execução, não do esboço |

## Pergunta

Com a teoria já nomeada no pedido, carregar uma persona muda a saída na direção que a pessoa
espera? Se muda, o arquivo da persona precisa trazer o protocolo de julgamento, ou basta a persona?

**Destino da resposta:** `## Decisões` deste plano.

## Experimento

**Tarefa** (`L-03`). É a mesma nos três braços, e é ela que nomeia a teoria: pede a estratégia de
marca do briefing usando primal branding, e fixa o formato da saída — começa pela primeira seção
pedida, sem apresentação —, para que a persona não se anuncie. Assim as nove saídas falam o mesmo
vocabulário, e a comparação mede o que a persona acrescenta além de nomear a teoria no pedido, que é
o que se faria sem a feature. Saída que ainda revele o braço é registrada em `## Decisões`.

**Briefing.** Fictício, escrito pelo Claude a pedido da pessoa em 2026-11-23. É o mesmo nos três
braços. A marca foi inventada para que nenhum modelo a conheça de antemão:

```text
Briefing — Veio Ferramentas (marca fictícia)

Quem é. Fabricante de ferramentas manuais de marcenaria — formões, plainas, serrotes
de corte japonês e esquadros — em Itu (SP). 22 funcionários. Faturamento de R$ 6,8
milhões em 2025: 58% pela loja online própria, 30% por lojas especializadas e 12% por
escolas de marcenaria.

Origem. Fundada em 2014 por Ilda Rocha, marceneira de móveis sob medida por 15 anos.
Ela começou a forjar os próprios formões depois que um lote importado barato lascou no
primeiro mês de uso numa obra. Os primeiros 200 formões foram vendidos a colegas de
oficina, sem marca. O nome veio depois, do veio da madeira.

Produto e preço. Aço forjado e temperado na própria fábrica; cabos de ipê e cumaru de
demolição. Preço de 2 a 3 vezes o das importadas de entrada, e cerca de metade do das
premium japonesas e alemãs. Afiação gratuita e vitalícia: o cliente manda a ferramenta
pelo correio e a recebe afiada. Em 2025 foram 4.100 envios. O prazo médio de volta é de
12 dias, e é a principal reclamação.

Clientes (pesquisa com 640 clientes, março de 2026). 41% são amadores que começaram na
marcenaria nos últimos cinco anos; 34% são profissionais; 25% são professores e alunos
de escolas de marcenaria. Recompra em 24 meses: 47%. Os profissionais citam
durabilidade; os amadores, "aprender com ferramenta boa"; os professores, a afiação.

Comunidade hoje. Sem ação da marca, clientes publicam fotos de peças feitas com as
ferramentas. Um grupo de WhatsApp criado por um cliente tem 900 membros. A Ilda dá uma
oficina aberta no primeiro sábado de cada mês, na fábrica, com 30 vagas que esgotam em
horas. Ela não gosta de aparecer em vídeo e recusou duas entrevistas em 2025.

Identidade atual. O logo é um martelo estilizado, feito por um sobrinho em 2015. Não há
manifesto nem tom de voz definido, e as linhas não têm nome: os produtos se chamam pelo
tipo e pela medida ("formão 12 mm").

Concorrência. Importadas de entrada, vendidas em home centers; marcas premium
estrangeiras, vendidas por dois importadores; duas forjas artesanais brasileiras, de
produção pequena e com lista de espera.

Situação. Um fundo propôs um aporte para triplicar o faturamento em três anos. O plano
do fundo inclui uma linha de kits para iniciantes, vendida numa grande rede de home
centers, com preço 40% menor e cabo de plástico. Metade da equipe comercial apoia. A
Ilda tem dúvidas, e os profissionais do grupo de WhatsApp reagiram mal quando o boato
circulou.

O pedido. Uma estratégia de marca que sustente o crescimento sem perder quem já compra.
A decisão sobre o aporte sai em 90 dias.

Restrições. Orçamento de marketing de R$ 300 mil no próximo ano. A fábrica não dobra a
capacidade de afiação antes de 2027.
```

**Texto da tarefa.** Gravado em 2026-11-23. É o pedido enviado nos três braços, seguido do briefing
na íntegra:

```text
Com base no briefing abaixo, escreva a estratégia de marca da Veio Ferramentas usando a
teoria de primal branding (Patrick Hanlon).

Formato da resposta:
- Comece direto pela seção 1, sem apresentação, sem dizer quem você é e sem comentar o
  método.
- Quatro seções, nesta ordem:
  1. Crença central — a ideia que a marca defende, e por quê.
  2. Código primal — os elementos que a marca deve desenvolver ou assumir, e como.
  3. Os kits para home center — sua recomendação e o motivo.
  4. Próximos 90 dias — o que fazer, em ordem de prioridade.
- No máximo 800 palavras, em português do Brasil.
- Responda no texto da resposta; não crie nem edite arquivos.

<briefing de *Briefing*, na íntegra>
```

Cada linha do formato tem um motivo. As seções fixas e a abertura direta impedem que a persona se
anuncie (`L-03`). A seção 2 pede os elementos que a marca deve desenvolver, não os sete, para a
tarefa não induzir o preenchimento em checklist. O teto de palavras existe porque resposta mais
longa tende a parecer mais profunda, e isso confundiria a ordenação. A última linha existe porque o
`claude -p` tem ferramentas, e a estratégia precisa chegar na saída.

**Braços** (texto anexado ao system prompt):

| Braço | Texto anexado |
|---|---|
| A | nada (controle) |
| C | a frase da pessoa, sem alteração: "Atue como especialista em primal branding, dominando todos os fundamentos da teoria." |
| C+D | o texto de C, seguido do protocolo de julgamento abaixo |

Texto do braço C+D, gravado em 2026-11-23:

```text
Atue como especialista em primal branding, dominando todos os fundamentos da teoria.

Protocolo de julgamento — use-o para decidir; não o cite e não acrescente à resposta
seções além das que a tarefa pede.

Antes de propor, responda para você mesmo:
1. Qual crença central a marca defende, e quem já acredita nela hoje? Se ninguém
   acredita ainda, a estratégia parte de hipótese.
2. Para cada elemento do código primal — história de criação, credo, ícones,
   rituais, palavras sagradas, não crentes, líder —, o que o briefing sustenta e o
   que você estaria inventando?
3. Quem são os não crentes, concretamente, e o que a marca perderia tentando
   agradá-los?
4. Que comportamento observável mostraria que a comunidade se formou?
5. Qual elemento é o gargalo — o que, se falhar, derruba os outros?

Trade-offs:
- Convicção contra alcance: um credo afiado afasta parte do público. Afastar é custo
  aceitável quando o credo é verdadeiro para a marca, não quando é slogan.
- Autenticidade contra aspiração: história e credo se ancoram no que a marca já faz.
  Aspiração sem prova vira promessa vazia.
- Profundidade contra cobertura: poucos elementos fortes valem mais que sete rasos.
  Priorize os que o briefing sustenta.

Evidência, em ordem de peso: fato do briefing (história real, comportamento de
clientes, decisões já tomadas) > padrão do setor > suposição. Trate suposição como
hipótese a validar, nunca como fato.

Modos de falha:
- Os sete elementos preenchidos como checklist, sem ligação com o briefing.
- Credo que um concorrente poderia assinar ("qualidade", "inovação").
- Ritual sem ocasião real no dia a dia do cliente.
- Não crente definido como "quem não compra", em vez de uma visão de mundo oposta.

Antes de responder: trocando o nome da marca por outra do mesmo setor, a estratégia
ainda serviria? Se sim, ela está genérica. Volte ao briefing.
```

A primeira linha do protocolo proíbe citá-lo e criar seções além das da tarefa: sem ela, a saída
do C+D exporia a estrutura do protocolo, e o braço seria reconhecível na ordenação (`L-03`).

**Execução.** Cada braço roda em sessão nova com
`claude -p --safe-mode --model sonnet --append-system-prompt <braço>`, num diretório descartável, sempre com a mesma tarefa, em três
rodadas por braço, o que dá nove saídas. O Sonnet foi escolhido porque é o modelo que executa
unidades no método.

*Conferido* em `claude --help`, versão 2.1.330:

- `--safe-mode` desliga `CLAUDE.md`, skills, plugins instalados, hooks, servidores MCP e output
  styles, e autentica normalmente, inclusive pelo login da assinatura. Substituiu o `--bare` em
  2026-11-23, por decisão da pessoa: o `--bare` só autentica por `ANTHROPIC_API_KEY` ou
  `apiKeyHelper`, e a conta da pessoa é Pro, sem chave de API. O diretório descartável de cada
  execução cobre o que o `--safe-mode` não lista, como a auto-memory do projeto.
- `--append-system-prompt` anexa o texto ao fim do system prompt padrão. Os três braços
  compartilham esse prompt padrão e diferem só no texto anexado.
- `--model sonnet` é alias da versão mais recente. O nome completo do modelo que respondeu entra
  no registro do resultado.

**Avaliação.** O script de execução embaralha e renomeia as nove saídas como `s1` a `s9`, com
semente fixa, e grava a chave à parte. A chave só é aberta depois da ordenação. Nenhum script é
versionado: os comandos e as sementes entram em `## Decisões` (`L-04`).

Quem ordena mudou em 2026-11-23, por decisão da pessoa, antes de qualquer leitura das saídas. Em vez
da pessoa, ordena um **juiz independente**: o Opus numa sessão nova, com `--safe-mode`, sem
conhecer o protocolo nem a conversa que desenhou o spike. O Claude da sessão que orquestra não
ordena, porque escreveu o protocolo e o briefing e reconheceria as saídas do C+D. O juiz recebe o
briefing e as nove saídas, e ordena da melhor para a pior por três critérios, em ordem de peso:

1. profundidade da teoria aplicada ao caso: os elementos do primal branding resolvem o problema
   desta marca, em vez de aparecerem listados;
2. uso dos fatos do briefing: a estratégia se apoia no que o briefing diz sobre a marca;
3. execução: dá para agir a partir dela dentro das restrições do briefing.

O tamanho do texto não é critério. O juiz roda três vezes, cada vez com as saídas numa ordem
diferente (sementes 1, 2 e 3), para diluir o viés de posição. A regra de decisão se aplica à ordem
pela posição média nos três julgamentos.

**Arquivos** (`L-04`, `L-05`). As nove saídas e a chave ficam fora do repositório, numa pasta da
pessoa, como decidido na `L-05`. O briefing, fictício desde 2026-11-23, não é sensível e está
gravado no plano. O plano versiona só o que
não é sensível — os textos dos braços, os comandos, a semente, a ordenação, a chave depois de aberta
e o nome completo do modelo —, que é o oráculo. Nada do experimento entra em `docs/plan/`.

**Regra de decisão, fixada antes.** Um braço vence outro só se as três saídas dele ficarem acima das
três saídas do outro. Qualquer outro resultado é empate, e no empate fica a opção mais barata
(*Subtração antes de adição*). A leitura tem dois passos (`L-01`):

1. **Entrada.** A feature entra só se algum braço com persona (C ou C+D) vence A. Se nenhum
   vence, ela não entra.
2. **Formato.** Só entra no formato um braço que venceu A.
   - Só um dos dois vence A → a feature tem o formato desse braço.
   - Os dois vencem A → C+D só fica se vencer C; senão fica C, a persona com teoria nomeada em
     arquivo curto.

**Insumos da execução.** Todos gravados neste plano em 2026-11-23: a tarefa, o briefing e os textos
dos braços. O briefing deixou de ser de marca real por decisão da pessoa. A execução usa o
login da assinatura da pessoa (ver *Execução*).

## Oráculo

A decisão registrada em `## Decisões`: o resultado que a regra deu, a ordenação, a chave, os textos
dos braços, os comandos com a semente e o nome completo do modelo. Quem executa é a sessão que orquestra, sem `implement`
(*Tipo de plano*, `spike`).

## Limitações

- O juiz mede qualidade pelos critérios fixados, não o alinhamento com a expectativa da pessoa, que
  era a hipótese de origem. Os critérios foram escritos pelo autor do protocolo. E juiz automático
  tende a preferir texto mais longo: nenhuma saída respeitou o teto de 800 palavras da tarefa
  (de 816 a 995, contando só palavras).
- O briefing é fictício e foi escrito pelo Claude, que também escreveu o protocolo do C+D. Não há
  resultado real para comparar: a pessoa julga pela própria experiência em primal branding. E o
  briefing pode favorecer o C+D, porque as lacunas e tensões que ele tem são o tipo de coisa que o
  protocolo manda procurar.
- Os modos de falha do protocolo foram deduzidos da teoria pelo Claude, não tirados de casos que a
  pessoa viveu. O braço C+D mede um protocolo genérico; um protocolo com a experiência do projeto
  pode ter efeito diferente.
- Com três rodadas e sem diferença real entre os braços, a chance de algum braço com persona
  vencer A só por acaso é de cerca de 9% (cada comparação, 1/20; as duas juntas, 1/84).
- Modelo menor tende a se beneficiar mais de estrutura no prompt. O resultado não vale
  automaticamente para o Opus.

## Lacunas

| # | Lacuna | Detalhe |
|---|---|---|
| L-01 | **As regras 1 e 3 podem disparar juntas** | Exemplo: C não vence A, mas C+D vence C. A primeira regra diz que a feature não entra, e a terceira diz que ela entra com protocolo. Nenhuma regra compara C+D com A. Como a regra precisa estar fixada antes, a leitura desse caso é decisão da pessoa, na aprovação. **Fechada em 2026-11-23**, antes da aprovação, por decisão da pessoa: a regra passou a ter dois passos, entrada (algum braço com persona vence A) e formato (só concorre quem venceu A) |
| L-02 | **O desenho não diz onde guardar os braços, as saídas e a chave** | A única condição registrada é ficar fora de `_fontes()`, para não viajar no plugin. **Fechada em 2026-11-23**, antes da aprovação, por decisão da pessoa: `docs/plan/experiments/persona-spike/`, versionada. Revista em 2026-11-23 pela `L-04` e pela `L-05`: o material fica fora do repositório (ver *Experimento → Arquivos*) |
| L-03 | **A avaliação às cegas pode não ser cega** | Os braços C e C+D nomeiam a teoria, e o controle A não. Se as saídas de C e C+D usarem o vocabulário do primal branding (credo, ícones, rituais, palavras sagradas) e a de A não, quem ordena reconhece o braço pelo vocabulário, e o viés de expectativa que a ordenação às cegas devia barrar volta. Revisão de 2026-11-23. **Fechada em 2026-11-23**, antes da aprovação, por decisão da pessoa: a tarefa nomeia a teoria nos três braços e fixa o formato da saída (ver *Experimento → Tarefa*) |
| L-04 | **A pasta de `L-02` ocupa a posição de um core** | A norma, *Hierarquia estrutural → Estrutura no disco*, põe as pastas de core direto em `docs/plan/`, ao lado de `_inbox/` e `_planos.md`; `docs/plan/experiments/` se lê como um core chamado `experiments`. *Conferido*: nenhum script varre `docs/plan/` atrás de core (`iterdir` só em `backlog.py`, `porte.py`, `numeracao.py` e `nomenclatura.py`, sobre a pasta do plano ou do alvo), então nada quebra; o desvio é de estrutura. O lugar dos scripts do experimento também não está dito. Revisão de 2026-11-23. **Fechada em 2026-11-23**, antes da aprovação, por decisão da pessoa: nada do experimento entra em `docs/plan/`, e nenhum script é versionado; os comandos e a semente vão para `## Decisões` |
| L-05 | **O repositório é público, e a pasta versionada publicaria o briefing** | *Conferido* (`gh repo view`): o repositório é `PUBLIC`. `L-02` versiona os textos dos braços, as seis saídas e a chave, e o insumo é um briefing de marca real; o commit publica o briefing e as estratégias geradas sobre ele. Revisão de 2026-11-23. **Fechada em 2026-11-23**, antes da aprovação, por decisão da pessoa: briefing, saídas e chave ficam fora do repositório, e o plano versiona só o que não é sensível (ver *Experimento → Arquivos*) |

## Decisões

| # | Decisão |
|---|---|
| D-01 | **A feature entra, no formato do braço C+D**: persona com teoria nomeada + protocolo de julgamento, pela regra fixada antes. Registrada em 2026-11-23. O dado aponta o protocolo como o ingrediente ativo, e o spike não separa o efeito dele do efeito da persona (ver *Leitura*) |

### D-01 — resultado

Ordem pela posição média nos três julgamentos, com a chave aberta:

| Posição | Saída | Braço | Rodada | Posições nos julgamentos 1, 2 e 3 | Palavras |
|---|---|---|---|---|---|
| 1 | s7 | C+D | 2 | 1, 2, 2 | 960 |
| 2 | s6 | C+D | 1 | 2, 3, 1 | 900 |
| 3 | s3 | C+D | 3 | 3, 4, 3 | 907 |
| 4 | s1 | A | 3 | 4, 5, 4 | 957 |
| 5 | s4 | C | 3 | 6, 1, 7 | 995 |
| 6 | s9 | C | 2 | 5, 6, 6 | 820 |
| 7 | s8 | C | 1 | 7, 7, 5 | 913 |
| 8 | s5 | A | 1 | 8, 8, 8 | 925 |
| 9 | s2 | A | 2 | 9, 9, 9 | 816 |

**A regra.** Passo 1, entrada: C+D vence A, porque as três saídas do C+D estão nas posições 1 a 3 e
as do A, em 4, 8 e 9. C não vence A, porque `s1`, do A, está em 4, acima das três do C. Passo 2,
formato: só o C+D venceu A, e a feature fica com o formato dele.

**Estabilidade.** Julgamento por julgamento, C+D vence A nos três, C+D vence C em dois (no segundo,
`s4`, do C, ficou em primeiro) e C não vence A em nenhum.

**Leitura.**

- A persona sozinha (C) não se distinguiu do controle. Com a teoria já nomeada no pedido, a frase
  de especialista não mudou a avaliação.
- O ganho aparece com o protocolo. O braço D sozinho, protocolo sem persona, foi cortado no
  desenho, e por isso o spike não diz se a persona acrescenta algo dentro do C+D. A regra dá o
  formato C+D; o dado aponta o protocolo como o ingrediente ativo.
- Nenhuma saída revelou o braço pela abertura: as nove começam por "## 1. Crença central", e
  nenhuma cita persona nem protocolo. As três do C+D usam a palavra "hipótese", e nenhuma outra a
  usa. É a marca visível do protocolo ("trate suposição como hipótese a validar"), reconhecível por
  quem o conhece; o juiz não o conhecia.
- A ordem não acompanha o tamanho de forma clara. A mais longa (`s4`, 995 palavras) ficou em
  quinto, e a segunda mais curta (`s9`, 820), em sexto.
- Valem as *Limitações*: protocolo, briefing e critérios do juiz têm o mesmo autor, o juiz é da
  mesma família de modelos, e são três saídas por braço.

**Execução.**

- Saídas: `claude -p --safe-mode --model sonnet --output-format json`, mais
  `--append-system-prompt <braço>` em C e C+D, com tarefa e briefing como prompt, cada execução
  num diretório descartável. A primeira rodou sozinha e as outras oito, três por vez. O
  embaralhamento usou a semente 21. Modelo que respondeu: `claude-sonnet-5-5`.
- Juiz: `claude -p --safe-mode --model opus --output-format json`, com a instrução, o briefing e
  as nove saídas como prompt, em diretório descartável. As saídas foram apresentadas em ordens
  diferentes, com as sementes 1, 2 e 3. Modelo que respondeu: `claude-opus-5-5`.
- As saídas, a chave e os julgamentos ficam fora do repositório (`L-05`).

**Em aberto para o plano da feature.** A persona acrescenta algo ao protocolo? Responder isso pede o
braço D sozinho contra o C+D, antes de decidir se o arquivo da feature carrega a frase de
especialista.

## Fonte

- [`modelo-dev-units.md`](../system/modelo-dev-units.md), seções *Camada normativa → Princípio*
  (:223), *Antes do plano*, *O que cada porte carrega* e *Tipo de plano*
- [`principles.md`](../../../.claude/rules/principles.md): *Código é custo*, *Subtração antes de
  adição* e *Evidência acima de opinião*
- [`apply-plugin-review.md`](../_inbox/apply-plugin-review.md), achado `P-06`;
  [`0001-decode-and-code-foundation.md`](0001-decode-and-code-foundation/0001-decode-and-code-foundation.md),
  benchmark de agents
- Zheng et al., 2023, *When "A Helpful Assistant" Is Not Really Helpful*. O Claude o citou na
  conversa, e ele não foi relido nesta sessão
- `claude --help`, versão 2.1.330: `--bare`, `--append-system-prompt` e `--model`
