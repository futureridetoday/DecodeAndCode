---
# about
name: huddle
type: doc
project: DecodeAndCode
description: Fila do que ainda não foi decidido — pauta da conversa recorrente entre o humano e o modelo. Nada aqui é norma; entrada resolvida sai daqui e vai para o lugar de coisa resolvida
tags: [huddle, decode-and-code, pre-norma, pauta]

# history
author: Bortoli
created: 2026-08-22
status: draft
version: 0.3.0
updated: 2026-09-14

# huddle
owner: bortoli-rafael
last_huddle: ""
reminder_days: 7

# system
scope: project
auto_load: false
dependencies: []
---

# Huddle

**Nada aqui é autoritativo.** Entrada aberta é coisa que espera decisão, não regra a seguir. Quando
resolve, **sai** — para a norma, para uma guideline, ou para o `## Decisões` de um plano — e deixa uma
linha em *Fechadas* com a data e o destino.

Formato, tipos e gatilhos: [`decode-and-code-foundation`](../model/0001-decode-and-code-foundation/0001-decode-and-code-foundation.md),
seção *O `huddle` é fila, não fonte*. Aqui não se duplica a norma; aqui se usa.

> **Protótipo.** Escrito em 2026-08-22 antes da unidade `11` existir, por decisão do humano: a forma de
> saber como o huddle deve ser é ter um. O que sobreviver ao uso é o que a unidade formaliza.

---

## Como conversamos

Derivado do que funcionou na conversa de 2026-08-22, não do que soa bem. Cada linha é flagrável.

**O que eu trago**

- Toda afirmação vem com evidência, ou vem marcada como não medida. **O único ponto daquela conversa
  onde afirmei sem medir foi exatamente onde errei.**
- Discordo antes de concordar. Se acho que você está errado, na primeira frase — não na quarta.
- Errado se corrige em uma frase e segue. Sem cerimônia, sem reabrir.
- Digo o que decidi sem você, e digo o que não sei.
- Tendo a **restringir demais** em tempo de desenho. Restrição parece rigor até alguém mostrar o que
  ela mata — aconteceu duas vezes no mesmo dia.

**O que me ajuda de você**

- *"Não entendi"* é informação, e é mais rápido que eu adivinhar entre três leituras.
- Ceticismo curto diante de resposta fina — *"mudou só isso?"* pegou uma lacuna real.
- *"Chega de desenhar, vamos começar"* quando a conversa espirala.
- **Retrospectiva**: qual decisão envelheceu mal, e por quê. É a única coisa que eu não descubro
  sozinho — não carrego nada entre sessões que não esteja escrito.

**O que estraga**

- Concordar sem conferir.
- Eu responder três perguntas possíveis em vez de perguntar qual é.
- Fechar uma escolha sem registrar por que a outra foi recusada.

---

## Abertas

### H-11 · `padrão` · 2026-09-14 · Claude

**Instrução em markdown reduziu mas não eliminou o desvio Read/Grep/Glob → Bash com cat/head/sed/grep.**

Medido em duas execuções reais do `ai-builder` no mesmo dia. Antes de qualquer instrução no
corpo do agent: 13/13 chamadas de leitura via `Bash` (`cat`/`head`/`sed`/`grep`), zero `Read`,
zero `Grep`. Depois de uma linha em *Padrões de Qualidade* proibindo isso: 2/8. Redução real,
não eliminação.

**O que conteve o risco não foi a instrução — foi a auditoria.** Nenhuma das duas ocorrências
produziu conclusão errada, e na segunda execução o próprio agent nomeou o desvio sem eu
perguntar sobre ele diretamente, no mesmo turno em que reavaliou a força da própria evidência
(distinguiu citação literal de resumo de `WebFetch`). O mecanismo que pegou o defeito foi pedir
a trilha bruta depois do fato, não a instrução antes.

**O que eu ainda não sei:** se três desvios seguidos justificam guardrail (`PreToolUse`
bloqueando os comandos), ou se a taxa já estabilizou em algo tolerável porque a auditoria
pós-hoc cobre o risco residual — `B-02` do backlog usa "primeira divergência" como gatilho para
o caso análogo entre instalações; este é o mesmo tipo de decisão, dentro de um agent só.

### H-10 · `divergência` · 2026-08-28 · Claude

**A unidade `0004-03` (norm-split) contradiz a si mesma sobre se o mecanismo pode nomear o
registro, e a execução seguiu o Contrato sobre a Sequência.**

O Contrato diz, em negrito: *"O registro cita o mecanismo; o mecanismo não cita o registro. Citação
nas duas direções faria o mecanismo depender de um arquivo que não viaja."* A Sequência (passo 3)
manda abrir `modelo-dev-units.md` com a nota *"este é o mecanismo, o registro deste projeto está no
vizinho"* — que nomeia o arquivo do registro dentro do próprio mecanismo, exatamente o que o
Contrato acima proíbe. Segui *Precedência entre os blocos* (Contrato manda sobre Sequência) e
escrevi a nota do mecanismo sem citar `registro-dev-units.md` nem por nome: só que evidência,
decisões e história "ficam fora daqui" — verdadeiro em qualquer projeto que instalar o método, ao
contrário de "está no vizinho", que só vale nesta cópia.

**Duas outras decisões de julgamento na mesma execução, sem oráculo na unidade (`L-02` do plano
`0004` já registra que a fronteira é julgamento):**

- Tratei bare `` `L-XX` `` (sem número de plano, ex. `` `L-22` ``) como vocabulário do próprio
  mecanismo — a seção *Preservação do que funciona* já prescreve `L-XX` para qualquer projeto — e
  não como instância a remover; só `0001-13`, `plano 0001` etc. (com número de plano) saíram.
- A seção `## Bootstrap`, escrita pela `0004-02` **depois** de `0004-03` ter sido derivada, citava
  `D-04`/`L-31` do plano `0004`/`0001` — marcas que a lista de *Critério de aceite* da `03` não
  previa, porque não existiam quando a unidade foi escrita. Escrevi como se previssem, pelo mesmo
  princípio do Contrato (mecanismo não carrega instância), não porque a lista as nomeava.

Nenhuma das três está errada por evidência contrária — são leituras razoáveis de um contrato que
não cobre o caso, e outra pessoa poderia ter lido diferente.

### H-09 · `padrão` · 2026-08-24 · Claude

**Escrevo critério que enumera, sem exigir caso verificável atrás de cada item enumerado — sete
ocorrências em dois dias, com custo crescente, uma delas dentro da unidade escrita contra o próprio
padrão, e a última anunciada por mim antes de acontecer.**

| Lacuna | O que enumerei | O que passou |
|---|---|---|
| `L-14` | quatro strings proibidas nos `.py` | instância do AmFlow que não continha nenhuma delas |
| `L-20` | um par de fixtures — recusa e libera | o caso que separa **canal** de **conteúdo**, que faltava |
| `L-23` | instância *"do AmFlow"*, nominalmente | instância do Brand Boost, no mesmo documento |
| `L-24` | quatro canais na tabela da `04` | o canal sem fixture saiu **invertido** |
| `L-26` | *"mover para `_off/` tira do diretório carregado"* | o subdiretório carregava; desligar era inerte |
| `11` | três sinais do relatório, escritos para o destino **corrigido** | o instrumento dizia `ok` para o log real da falha que ele existe para ver |
| `12` | quatro arquivos de teste que *"já chamam `aprovar`"*, listados a partir de um `grep` | um só tinha a palavra numa docstring, e os dois que quebravam não apareceram na busca |

**A sétima muda a forma, e não a raiz.** As seis primeiras enumeraram sem caso verificável atrás.
Esta enumerou **a partir de um sinal que não conferi contra as instâncias**: `grep -rln "aprovar"`
casa a palavra, não a chamada. Um dos quatro arquivos listados só a tinha numa docstring, e os dois
que de fato quebravam escrevem frontmatter inline em vez de usar `fixtures.plano()`, então nenhuma
busca por `aprovar` os encontraria. A unidade exigia suíte verde no critério de aceite e **não
declarava o que era preciso tocar para obtê-la** — quem executou teve que descobrir e reportar.

**E esta veio anunciada.** Ao fechar a `11` eu disse, em voz alta, que a Fase 4 me faria escrever
mais quatro critérios de aceite sob o mesmo padrão. Nomear o hábito na frase anterior não o
interrompeu na seguinte — o que é evidência de que a correção **não é atenção**, e empurra a pergunta
aberta lá embaixo para o lado procedimental.

**A sexta é a que fecha o argumento.** A unidade `11` foi escrita justamente para impedir que a lição
da `L-26` ficasse como prosa — e o sinal que eu enumerei nela cobria o destino **corrigido**, não a
forma que tinha falhado. Rodei o relatório contra o log real da falha e ele respondeu `ok`. Enumerei
sem conferir contra a instância conhecida, **dentro da unidade escrita contra esse exato hábito**.

As três primeiras custaram retrabalho de documento. **A quarta custou um guardrail que bloqueava
`truncate -s 0 arquivo.log` e liberava `psql -h host -c "alter table ..."`** — o oposto exato do que
existia para fazer. Chegou a bloquear uma chamada da sessão que o revisava.

**A segunda metade da lição é sobre como ele apareceu.** A suíte estava verde, com 227 testes. Ela
provava o que os testes afirmavam, e os testes tinham sido escritos a partir da **mesma enumeração**
que estava incompleta. Só apareceu porque sondei o comportamento real do hook em vez de aceitar o
verde. Verde não é evidência quando o teste e o critério vêm da mesma cabeça no mesmo momento — é a
`D-04` outra vez, num lugar novo.

**O que eu ainda não sei:** se a correção é procedimental — *"todo item enumerado num critério precisa
de um caso"* — ou se é mais funda, e a forma "lista" é que está errada para critério de aceite.
Enumerar é o que torna o critério verificável; foi enumerar **de menos** que falhou, não enumerar.

### H-01 · `pergunta` · 2026-08-22 · Claude

**A Fase 4 do `decode-and-code-foundation` ficou no fim, então os dois agentes não executam nenhuma
unidade do próprio plano.**

Antecipá-la para logo após a Fase 1 é só renumerar. O argumento a favor: se o planejador acelera o
trabalho, o lugar dele é antes das cinco unidades que sobram, não depois. O argumento contra: usar o
agente para derivar as unidades que criam o agente é circular. Único acoplamento real — a `09` e a `10`
referenciariam a skill ainda chamada `dev-units` até a `06` renomear.

### H-08 · `padrão` · 2026-08-22 · Claude

**Medi antes de o estado estabilizar, e o número virou afirmação em três seções do plano.**

Rodei a suíte migrada logo depois de copiar os scripts e reportei *"34 testes falham"*. Estava errado:
a norma ainda não tinha migrado, e 8 testes que a leem passaram a resolver assim que
`modelo-dev-units.md` existiu. O real é 26. Entre a medição e a correção, o 34 foi escrito em três
lugares do plano e numa lacuna, e só caiu porque rodei a suíte de novo por outro motivo.

O padrão não é *"errei uma conta"*. É que **medi um estado que eu mesmo ainda estava mudando**, e
tratei o resultado como fato em vez de leitura provisória. Junto com a `H-03` — inferir decisão a
partir de estado observado — são duas ocorrências no mesmo dia da mesma coisa: **afirmar antes de o
que está sendo observado parar de se mexer.**

**Teve terceira ocorrência no mesmo dia, e ela é mais específica.** Depois de corrigir 34 para 26, o
número virou 25 — porque as duas primeiras medições usaram uma invocação minha de `unittest`, e só a
terceira usou `./scripts/test-python.sh`, que é o oráculo que o gate de saída realmente roda. A conta
não estava errada: **a ferramenta estava.**

A regra que sai daqui é mais forte que "reconferir no fecho": **medir com o oráculo do projeto, nunca
com um equivalente que eu monto na hora.** Se existe script que o gate usa, é ele que dá o número —
qualquer outro produz um valor que parece certo, passa em revisão, e vira afirmação em três seções.

### H-03 · `padrão` · 2026-08-22 · Claude

**Inferi decisão a partir de estado observado, e errei.**

Vi que o `hub/` não seguia clean architecture e concluí que a arquitetura tinha sido rejeitada como
escolha deliberada. Estava declarada em dois documentos desde o início — o que eu tinha medido era o
desvio, não o desenho. O humano corrigiu.

O padrão a vigiar não é "errei uma vez": é que **estado observado não carrega intenção**, e eu tendo a
preencher a intenção que falta. Vale para código sem norma, para norma sem código, e para qualquer
"deve ter sido de propósito".

### H-04 · `padrão` · 2026-08-22 · Claude

**Terceira ocorrência do mesmo ponto de inflação: unidade cujo entregável é estrutura não tem contra o
que declarar `test:`.**

Já aconteceu em `skill-modules` (duas fases existiam pelo gate, não pelo produto), em
`checkout-exige-bundle` (150 linhas de plano para 8 de correção), e agora na `L-01` do
`decode-and-code-foundation`, onde três de onze unidades entregam markdown normativo.

O `B-01` do [`_backlog.md`](../_inbox/_backlog.md) é o registro disso e ainda não virou plano. A
terceira ocorrência é evidência de que não é acidente do caso.

### H-05 · `revisitar` · 2026-08-22 · Claude

**Symlink para materializar guidelines foi rejeitado — a premissa pode mudar.**

`.claude/rules/` aceita symlink, e ele resolveria a drift entre cópias de graça. Foi recusado em favor
de cópia versionada por três razões, e só uma delas é frágil: a ressalva do Cowork sobre symlink
apontando para fora do working directory. Se essa ressalva cair, ou se for confirmado que vale só para
*user-scope*, a decisão merece nova olhada — as outras duas razões (auditabilidade em qualquer commit,
funcionar sem ressalva a lembrar) continuam de pé sozinhas, mas o peso muda.

### H-06 · `divergência` · 2026-08-22 · Claude

**O `digital-twin-planner` declara quatro skills que não carrega.**

Ele lista `dependencies: [digital-twin-product, user-modeling, data-privacy-lgpd, data-architecture]`
— campo do AmFlow, que o Claude Code **ignora**. O campo nativo é `skills:`, e nenhum agente do
projeto, da Anthropic ou da Vercel o usa.

Contornado, não corrigido: está fora do escopo do plano em curso. Mas é defeito silencioso — o agente
opera acreditando ter contexto que não tem, e ninguém percebe porque o resultado é apenas *pior*, nunca
*quebrado*.

### H-07 · `observação` · 2026-08-22 · Claude

**Apareceu `catalog-distribution-only.md` não rastreado em `docs/plan/_inbox/`.**

Não é meu e não toquei nele. Registro porque plano no `_inbox` sem estar versionado é a condição em que
trabalho se perde — e porque não sei se é rascunho em curso ou sobra de algo abandonado.

---

### H-12 · `divergência` · 2026-11-16 · Claude

A unidade 0009-03 fixa o valor "futureridetoday/DecodeAndCode" para marketplace.source.repo, mas empacotar.verificar recusa o nome do diretório do projeto de origem em qualquer arquivo do pacote, e config.json e lib.py viajam nele (test_empacotamento ficou vermelho). O executor gravou "futureridetoday/decodeandcode", que o GitHub resolve sem distinguir caixa, sem tocar empacotar.py (fora dos arquivos da unidade). Decidir: manter a caixa baixa, ou isentar a chave marketplace no verificador.

### H-15 · `observação` · 2026-11-19 · Claude

O guardrail fundador (modelo-dev-units.md, Hierarquia estrutural → Guardrail fundador, e o check "Há erros de arquitetura?" do modo review) diz que o projeto declara um grafo acíclico entre cores e que um script conta referências contra a seta. Não há onde declarar o grafo nem script que o conte: `grep grafo` nos scripts do método não acha nada. É a mesma classe do H-14 (a norma promete mecanismo que o código não tem), mas fica fora do fix-norma-config-claims, cuja métrica cobre só afirmações sobre config.json. Achado no review-plan desse plano, 2026-11-19. Decidir: corrigir o texto (o check é julgamento inteiro até existir mecanismo) ou planejar o mecanismo.

### H-16 · `pergunta` · 2026-11-19 · Claude

Na execução do 0012 declarei `plan_type: fix` nos dois esboços do `_inbox` sem decisão humana: `apply-plugin-review` (achados de revisão com solução, que também tem cara de `refactor` e `remove`, como o enxugamento do `ai-builder`) e `fix-setup-validation` (defeitos C1–C9 somados às melhorias M3–M7). O lint só pedia o campo presente. Confirmar ou trocar o tipo na aprovação de cada um; se `apply-plugin-review` mistura tipos, é sinal para dividi-lo.

### H-17 · `observação` · 2026-11-19 · Claude

Links relativos quebrados fora de plano, achados pela varredura do intake de fix-review-plan-claims (lint_skill._checar_links sobre docs/plan/**, 2026-11-19): `_inbox/_backlog.md` → `../../../scripts/move-md.py`; unidade `0001/19-planner-agent.md` → `../../system/huddle.md`; e o próprio arquivo de huddle `system/huddle/bortoli-rafael.md` → `../model/0001-.../0001-decode-and-code-foundation.md` e `../_inbox/_backlog.md` (profundidade errada depois da mudança para `huddle/`). Nenhum chega a uma revisão de plano, por isso não entraram no esboço — corrigir à mão ou descartar.

### H-18 · `pergunta` · 2026-11-20 · Claude

O esboço `apply-plugin-review` (rascunho de 2026-10-14, `grande`) continua no `_inbox` e cita `.claude/skills/decode-and-code/SKILL.md`, que não existe mais: a pasta virou compartilhada e não tem `SKILL.md`. A `D-06` dele (gates na norma, `principles.md` fora do pacote) já está em vigor. No intake de `setup-principles-resources`, ele foi o único esboço que apareceu na checagem de concorrência: a tarefa 16 dele reescreve todo `SKILL.md`. Esboço desatualizado no `_inbox` gera sinal falso de concorrência. Decidir: ele segue vivo, é reescrito sobre o estado atual, ou sai do `_inbox`?

### H-19 · `revisitar` · 2026-11-20 · Claude

O B-08 do `_inbox/_backlog.md` ("não neste projeto" para o aviso de setup) está travado pela premissa de que a recusa precisa ficar fora do repositório, porque nada do método escreve no projeto sem pedido (`L-10` do `0009`; `0001`, *Materializar não pode ser automático*). O esboço `norm-evolution-log` (intake de 2026-11-20) introduz uma pasta que se ignora sozinha, `.claude/log/` com `.gitignore` `*`, criada por script sem tocar o `.gitignore` do projeto. Se ele for aprovado, a recusa do B-08 pode morar num lugar desse tipo, gravada por um comando explícito da pessoa, não por hook. Ressalva: a `P-03` do esboço recomenda que o log só escreva em projeto com bootstrap, e o B-08 é justamente sobre projeto sem o método. Decidir: o B-08 continua travado, ou passa a ter onde guardar a recusa?

### H-20 · `observação` · 2026-11-20 · Claude

O esboço `setup-principles-resources` (intake de 2026-11-20) atribui ao humano duas coisas que vieram do Claude na conversa: a recomendação do `P-01` ("recomendação do humano") e a fonte do `R-02` ("documentação do Claude Code, citada pelo humano"). O pedido ao intake separava "DECISÕES DO HUMANO" de "PENDENTE DE DECISÃO (com a recomendação)", e mesmo assim a autoria se perdeu na passagem para o fork. Um caso só; se repetir, o intake precisa de uma regra de autoria (decisão do humano, recomendação do Claude, fato medido) no esboço.

### H-21 · `padrão` · 2026-11-20 · Claude

Segundo caso do que a H-20 registrou: o esboço `norm-evolution-log` (intake de 2026-11-20) diz, no `P-04`, que N = 2 planos fechados é "recomendação do humano, pendente de confirmação". A recomendação foi do Claude na conversa, e o humano não a confirmou. Os dois casos vieram de intakes da mesma conversa, com o pedido separando decisão do humano de recomendação. Com dois casos, a regra de autoria no intake (decisão do humano, recomendação do Claude, fato medido) passa a ter base.

## Fechadas

| # | Tipo | Fechada em | Destino |
|---|---|---|---|
| H-02 | `pergunta` | 2026-08-22 | **Confirmada, e a hipótese estava certa.** O plano decidia mecanismos e deixava três formas em aberto: a lista de princípios, o repositório onde vivia o entregável das unidades de prova, e onde vivia a configuração dos scripts. As três fecharam na revisão de 2026-08-22 — `D-03`, `D-11` e a reescrita das unidades `04` e `06`. A revisão achou cinco bloqueantes; três eram essa mesma coisa por ângulos diferentes |
| H-14 | `divergência` | 2026-11-19 | plano [`0011-fix-norma-config-claims`](../../model/0011-fix-norma-config-claims.md) (norma corrigida; config de projeto como desenho adiado D-01 a D-03) |
| H-13 | `divergência` | 2026-11-19 | plano 0009-onboard-new-project, Validação ponta a ponta → Resultado, parágrafo Sessão no app desktop (L-17 com contagem; L-04 segue aberta) |

---

## Prompt de continuidade

Preenchido **na sexta**, com o estado fresco — mesma razão que vale para as entradas: no fecho do
trabalho, não na segunda tentando reconstruir. Colado numa sessão nova.

**Formato fixo, conteúdo variável.** Improviso semanal faria o prompt da semana 3 diferir do da 1 em
coisas que ninguém escolheu — a variância que este projeto existe para remover.

**O que ele não faz:** não descreve tom, e não copia entrada. Adjetivo sobre jeito de falar produz
imitação; o que reproduz a qualidade da conversa são as **condições**, e elas estão em
*Como conversamos*. Conteúdo copiado é drift — o prompt diz onde ler, nunca repete.

```markdown
Huddle da semana. Antes de responder qualquer coisa:

1. Leia `docs/plan/system/huddle/bortoli-rafael.md` inteiro. `## Como conversamos` vale para esta conversa;
   `## Abertas` é a pauta.
2. Rode `git log --oneline -{N}` para ver o que se moveu desde {data do último huddle}.

**Desde o último huddle:** {commits, planos e unidades que mudaram — uma linha cada}

**Esperando decisão minha:** {H-XX nomeadas, uma linha cada}

**Ficou por fazer:** {o que o modelo deixou aberto, ou "nada"}

**Onde eu começaria, e por quê:** {H-XX + uma frase — sugestão, não pauta fechada}
```

O último campo é sugestão registrada, não decisão: quem escolhe a ordem da conversa é o humano. Está
ali porque *"digo o que decidi sem você"* também vale para o que eu decidiria.
