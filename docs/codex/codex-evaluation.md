---
# about
name: codex-evaluation
type: doc
project: ""
description: Avaliação do codex no fim da fase 1 do redesign — teste prático em sessões sem histórico, leitura por etapa, comparação com a norma e revisão de texto, com os achados e o ajuste proposto para cada um
tags: [codex, redesign, avaliacao]

# history
author: Bortoli
created: 2026-11-26
status: stable
version: 0.3.0
updated: ""

# system
scope: project
source: ""
auto_load: false
checksum: ""
dependencies: [redesign-plan, codex-guide]
---

# Avaliação do codex

**Estado:** duas rodadas de teste prático, com os ajustes de cada uma aplicados ao codex (D-13 e D-14
do plano). Ver *Segunda rodada*, no fim.

Feita em 2026-11-26, no fim da fase 1 e antes da fase 2 do [plano do redesign](redesign-plan.md)
(D-11). "Etapa" e os títulos citados são seções do codex
(`.claude/skills/decode-and-code/codex/`).

## Como foi feita

| Frente | Como | Quem |
|---|---|---|
| Teste prático | Quatro sessões novas, só com o codex e sem nenhuma skill, percorreram um caso cada: pedido pequeno, pedido grande, duas correções (uma que vira produto), e setup com rethink e huddle. Cada uma relatou onde hesitou, inventou ou achou contradição | Sonnet, o modelo que executa unidades |
| Comparação com a norma | Leitura da norma inteira; 154 regras de método classificadas contra o codex, o guia, o inventário e o plano | Opus |
| Leitura por etapa | Para cada etapa, conferir se as seções que ela lê bastam para decidir certo | Opus, nesta sessão |
| Revisão de texto | O codex inteiro lido de uma vez: termos, tom, clareza | Opus, nesta sessão |

**Resultado em uma frase:** o codex conduz o fluxo — os quatro testes chegaram ao fim sem travar, e
a voz e os termos se sustentam —, mas deixa sem regra várias decisões que uma etapa precisa tomar, e
a norma tem 14 regras de método com perda real que não ganharam lugar.

**Comparação com a norma, em números:** 51 regras estão no codex; 30 mudaram de propósito, com
decisão registrada; 47 são mecanismo, com destino; 26 ficaram sem lugar — 14 com perda real, 4
contradições sem decisão e 8 detalhes.

## O que era esperado e não é defeito

Sem as skills, as sessões de teste inventaram tudo o que é procedimento: formato e caminho de cada
artefato, valor de `<plan_root>`, índice e próximo número, lista de tipos, vocabulário do huddle,
quando o huddle está atrasado, como conferir que um recurso existe, commit e branch. Isso confirma a
fronteira do guia — é da skill —, e entra no mapa da 2.1 como o que cada skill precisa entregar.

Um achado desse grupo é de método: **quando o codex é silencioso, o que Claude faz?** As quatro
sessões inventaram em silêncio. Proposta: uma regra curta — o que o codex e a skill não decidem,
Claude pergunta ao usuário em vez de inventar.

## Decisões que faltam no codex

Ordenadas pelo impacto: as primeiras travaram ou dividiram mais de um teste.

| # | Achado | Evidência | Ajuste proposto |
|---|---|---|---|
| 1 | **Porte sem critério de escolha.** Porte diz o que cada porte contém, não como escolher; o critério da norma ficou incompatível com o médio novo, e nada o substituiu | os 4 testes; norma:823-833 | Critério na seção Porte. Recomendação: pequeno quando cabe numa sessão sem perder contexto; médio quando é uma história que precisa de sessão nova; grande quando são duas ou mais histórias entregáveis em sequência. **Decisão sua** |
| 2 | **História, unidade e porte não fecham.** Unidade "corresponde a uma história"; o pequeno tem histórias e não tem unidade; uma história com duas entregas vira o quê; unidade só técnica (habilitadora) vale? | testes pequeno, grande, correção | Em História e Unidade: no pequeno, a história é aceita pela entrega única; uma unidade entrega uma história ou um corte vertical dela; unidade só técnica é permitida quando declara a história que habilita |
| 3 | **O plano não guarda o que a revisão produz.** A revisão refina viabilidade, erros, o que falta e decisões em aberto, e o derive passa "decisões e lacunas" à unidade — mas Plano e Plano técnico não têm decisões nem lacunas no *Contém* | os 4 testes; norma:520 | Plano técnico passa a conter decisões (com as em aberto) e riscos técnicos; Plano passa a conter as lacunas. Decisões em aberto fecham antes de P4 ou viram fora de escopo declarado |
| 4 | **Unidade e Definition of Ready circulares.** "A unidade tem o que o derive lhe dá", e o derive dá "contexto, memória e padrão" sem definir nenhum; "basta sozinha" não tem teste | testes grande e correção | DoR vira lista verificável: história, critério de aceite com o teste, tarefas, arquivos que toca, guidelines desses caminhos, recursos pelo nome, decisões e lacunas que valem para ela, e o que as unidades anteriores entregam |
| 5 | **Handoff e sessão nova sem regra.** Um por plano ou por unidade; uma sessão por unidade ou uma para todas; a sessão nova vê o codex? | teste grande | Handoff: um por plano; cada unidade roda na sua sessão; a sessão de code lê as seções do codex que a etapa code lê, pelo nome, e o handoff não as copia |
| 6 | **Unidades derivadas antes do code dependem do código real.** A unidade 2 precisa de nomes que só a 1 define; "memória" aparece em dois sentidos | teste grande | Derive declara, em cada unidade, o que ela espera das anteriores; se a entrega anterior divergir, a seguinte é ajustada antes de rodar. "Memória" passa a "decisões e lacunas" |
| 7 | **Lacuna sem fluxo.** Parar ou seguir; reaprovar a unidade; propagar às seguintes; numeração; tarefa do pequeno insuficiente. E a regra da norma de **precedência**: quando a unidade e o código divergem, o critério de aceite manda, e o escopo nunca se reduz em silêncio | testes grande, correção, pequeno; norma:574-593 | Lacuna ganha o fluxo (parar, propor o ajuste, aprovação do usuário, registro `L-XX` por plano, ajuste das unidades seguintes) e vale também para a tarefa do pequeno. Precedência entra em Code |
| 8 | **Recusa, gate que falha e teste que falha.** O que acontece quando o usuário recusa uma aprovação, quando o gate A ou B falha, quando o P7, o P8 ou o C4 falham | os 4 testes | Regra em Aprovação: a recusa volta à etapa que produziu o resultado, com a objeção como entrada, ou encerra o plano como descartado. Teste que falha volta ao code da mesma entrega |
| 9 | **Correção que vira produto.** O gatilho não cobre "não há defeito, há recurso ausente"; quem muda o tipo (Tipo só prevê o usuário); o destino do plano mínimo; onde reentra | teste de correção | Seção em `fix.md`: gatilho (ajuste grande ou recurso ausente), Claude propõe e o usuário aprova a troca de tipo, o plano mínimo é descartado, e o plano volta à confirmação do objetivo e segue de P1 |
| 10 | **Ordem do teste da correção.** O teste "falha antes do ajuste", mas é C4, depois do code; a norma exige a falha registrada antes | teste de correção; leitura; norma:858 e 1127 | O teste que reproduz o defeito é escrito e roda vermelho no início do C3, antes do ajuste; o C4 é o verde. Plano mínimo: "como verificar" é o critério de aceite, e o gate de entrada do code vale em C3 |
| 11 | **Tipo: o que cada um exige.** A lista fica fora do codex por decisão, mas o que cada tipo exige no aceite e na revisão (refactor, remove, spike, chore) não tem lugar; nem o critério entre defeito e produto | testes pequeno e correção; norma:845-873 | **Decisão sua**: (a) uma seção por tipo com o que ele exige, no codex; ou (b) a lista com as exigências fica na skill, como mecanismo. Recomendação: (a), porque é o critério do P3 e do P7. Em qualquer caso, Tipo ganha a regra "defeito é comportamento especificado que não se cumpre" e "na dúvida, pergunte" |
| 12 | **Independência entre planos.** Sem o teste da norma ("entregando só A e parando, o sistema fica válido e útil?"), sem "quando não dividir", "alvo" indefinido; o codex barra, a norma só avisava e registrava o porquê; a norma dispensava no pequeno | testes grande e correção; norma:792-812, 918-955 | Trazer o teste e a regra de não dividir. **Decisão sua**: barra ou avisa — recomendação: avisa e registra o porquê, como a norma, porque quem aprova é o usuário |
| 13 | **"O sim a cada escrita" sem escopo.** Lido ao pé da letra, vale para o arquivo do plano e para o código; o log e as projeções escrevem sem sim | os 4 testes; norma:1355-1360 | Usuário: o sim de escrita vale para setup e rethink e para escrita fora do que um plano aprovado cobre; o registro de uso e as projeções escrevem sem sim |
| 14 | **Portas da camada normativa.** A norma deixava princípio, guideline e guardrail mudarem por plano (tipo `rule`), setup ou rethink; o codex só fala de setup e rethink, o huddle também produz guideline, e o rethink não cria item novo | teste de setup; norma:244-289, 1588 | Uma regra única: esses itens mudam só por setup, rethink ou plano do tipo `rule`; o huddle propõe e uma dessas portas grava; o rethink também cria |
| 15 | **"Só o rethink cria ou remove recurso"** contra o time que cria uma skill por conta própria | teste de setup | Trocar por "só o rethink inclui ou retira um recurso do mapa" |
| 16 | **Hipótese medida depois do fechamento** não tem dono nem lugar | testes pequeno e grande | O ponto de verificação vira entrada aberta no huddle, com a data |
| 17 | **Como revisar uma entrega.** Da norma: número do relatório é alegação até ser medido; teste que decide tem de falhar com o código desligado; medir por outro caminho | norma:784-788, 1111-1132 | Regra em Teste. O que é mecanismo (lints, contagem de testes) fica na skill |
| 18 | **Quando Claude registra no huddle.** Os cinco gatilhos e o registro no fecho de cada etapa, mesmo com zero entradas | norma:1284-1311 | Huddle ganha quando registrar; o comando fica na skill |
| 19 | **A revisão não confere as referências técnicas** da proposta | norma:1094 | Revisão: abre cada referência técnica e confere que existe e serve |
| 20 | **Recurso só do usuário ou sem permissão; "permissão de uso" sem definição** | testes setup e pequeno | Definir permissão de uso em Recurso do projeto e dizer o que Claude faz com recurso que só o usuário chama: pede que o usuário o rode |
| 21 | **Foundation e `CLAUDE.md`.** O padrão de código costuma já estar no `CLAUDE.md`, que é recurso e não se copia | teste de setup; norma:1506-1509 | Foundation: quando o padrão já mora num recurso do projeto, a foundation o cita pelo nome. Setup e rethink nunca escrevem nas instruções do projeto |
| 22 | **Setup e rethink.** Ordem (o mapa vem antes da guideline que liga caminho a recurso); de onde sai o objetivo do projeto; o que é mudança de rumo; o que fazer com planos abertos que citam um recurso retirado; arquivar nunca apaga | teste de setup; norma:298-337 | Ajustes curtos em Setup, Rethink e Princípio |
| 23 | **Princípio.** Enunciado e teste só "no primeiro"; o teste não pode ser tautológico | teste de setup; norma:1486-1488 | Todo princípio tem enunciado e teste, e o teste nunca é "a mudança aproxima do objetivo" |
| 24 | **Estados do plano.** Fechado, registrado, descartado, rascunho: nenhum definido; onde o plano vive antes do número | testes correção e grande | Plano ganha os estados (rascunho até P4 ou C2, aprovado, fechado, descartado); o lugar de cada um é da skill |

## Texto e termos

| # | Achado | Ajuste proposto |
|---|---|---|
| T1 | "Usuário" em dois sentidos: quem usa o DC (seção Usuário) e quem usa o produto (Mindset, História, Hipótese) | No segundo sentido, sempre "quem usa", nunca "usuário" (regra 4 do guia) |
| T2 | "DC" nunca é definido | Uma linha em Workflow ou Etapa: o DC é o método que o codex descreve |
| T3 | Termos sem definição: apetite, referências técnicas, contexto, entrega "documentada", estado derivado do teste, versão do formato, "procedimento das etapas" | Definir em uma frase onde aparecem, ou trocar por termo do codex |
| T4 | "Parte do sistema" no Plano contra "não há pasta por parte do sistema" na Raiz dos planos | Dizer que a parte do sistema é um campo do plano, não uma pasta |
| T5 | Workflow lista P7 e aprovação final separadas; no pequeno e no médio coincidem, e só se vê juntando Aprovação. A aprovação das unidades derivadas e a final não têm código | Uma frase no Workflow; códigos para as duas |
| T6 | "Decode enxuto" na correção, que não tem etapa decode | "O diagnóstico é um decode enxuto" |
| T7 | Numeração diz "na aprovação" sem dizer qual | Citar a regra do Plano |
| T8 | Guideline parece ter dois sentidos: diretriz por caminho e ligação de caminho a recurso | Uma guideline é diretriz por caminho; algumas nomeiam os recursos que valem ali |
| T9 | Guardrail "aparece no decode" — ele age em qualquer ação | Guardrail age em toda etapa; o decode o considera ao propor |
| T10 | Segurança e privacidade sem lugar natural nos quatro riscos | Dizer que entram em viabilidade técnica e de negócio |

## Leitura por arquivo

Cada teste usou só parte do codex — o setup, cerca de um quinto. Isso é o desenho: cada etapa lê só
as seções de que precisa, e a lista fica na skill (guia, *Organização*). O teste confirmou que, sem
essa lista, quem lê navega só por *Ver também*: na fase 2, cada skill precisa trazer a lista das
seções da sua etapa.

## Próximo passo

Aplicar os ajustes num ciclo único, com a lista das decisões marcadas como suas respondida antes; os
demais seguem a recomendação. Depois, repetir os quatro testes práticos para medir se os atritos
caíram.

## Segunda rodada

Feita em 2026-11-27, com os mesmos quatro casos e as mesmas regras, depois dos ajustes da D-13. Cada
atrito veio classificado como **método** (faltou regra para decidir) ou **procedimento** (faltou
formato, caminho, comando ou valor).

**O que mudou:** os pontos que travaram a primeira rodada funcionaram como escritos. As sessões
escolheram o porte pela regra, montaram a unidade pela Definition of Ready, escreveram o handoff,
rodaram o teste da correção vermelho antes do ajuste, fizeram a passagem de correção para produto,
aplicaram o teste de independência e a tabela de tipos, e abriram o ponto de verificação da hipótese
no huddle. Nenhuma sessão precisou inventar regra para atravessar o fluxo.

**O que sobrou de método** eram refinamentos dessas regras, e foram aplicados (D-14):

| Achado | Ajuste |
|---|---|
| Porte: pequeno e grande se sobrepunham quando duas histórias cabem numa sessão | O porte conta entregas primeiro; o pequeno pode ter várias histórias |
| Aprovação final no pequeno lida como ato separado | No pequeno e no médio, a aprovação final é a da única entrega |
| "Quem revisa" no P7 não existe | Claude mede uma afirmação por outro caminho e declara qual |
| Teste da entrega contra testes das tarefas | Pode ser a soma, quando cobre o critério |
| Ação irreversível ou fora do repositório | Pede o sim do usuário na hora, mesmo com o plano aprovado |
| Achado fora do escopo e escopo novo depois do P4 | Vira pedido novo, ou entrada no huddle |
| Divergência que é relatório contra divergência que é lacuna | Lacuna quando o critério não se cumpre com o que a unidade diz |
| O que Claude decide sozinho contra o que pergunta | Decide o que não muda escopo nem critério; registra no huddle o que muda o que quem usa vê |
| Sinal da hipótese sem analytics; cerimônia num pedido trivial | O sinal pode ser consulta ou observação; a proposta tem o tamanho do pedido |
| Apetite em porte antes da revisão | Vale o porte da revisão; a diferença vai ao usuário no P4 |
| `fix`: especificação implícita, tipo na dúvida, passagem que "descartava" o plano | Especificação pode ser implícita; na dúvida começa como `fix`; o plano continua e muda de conteúdo |
| Setup: huddle só no fim; fonte dos demais princípios; onde ficam os princípios | Huddle primeiro; demais princípios vêm do que nunca pode ser violado; princípios num lugar próprio |
| Rethink: editar contra arquivar; rethink contra plano `rule`; instruções do time desatualizadas | Critérios explícitos em Rethink |
| Papel do Designer; recurso pessoal; permissão por ação; padrão de código contra guideline; "referência" em dois sentidos; "módulo" sem definição | Uma frase em cada seção; "fontes técnicas" na proposta; "módulo" sai de Usuário |

**O que sobrou de procedimento** é o mesmo grupo da primeira rodada — formatos, caminhos, índice,
próximo número, vocabulário do huddle, commit —, que é da skill e entra no mapa da 2.1.

**Leitura:** a primeira rodada achou buracos de regra; a segunda, arestas. O ganho de uma terceira
rodada só com o codex tende a ser pequeno: o próximo teste útil é o da fase 2, com cada skill
migrada fornecendo o procedimento.

