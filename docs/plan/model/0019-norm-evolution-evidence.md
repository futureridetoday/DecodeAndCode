---
# about
name: norm-evolution-evidence
type: plan
project: DecodeAndCode
description: Segundo de seis planos do ciclo de evolução da norma — entrada do huddle com campo de evidência opcional e destino `método`, no huddle e no log-resolver, que guarda o feedback ao método num M-XX local até a pessoa levá-lo, à mão, ao repositório do método
tags: [decode-and-code, norma, huddle, log, evolucao, metodo]

# alvo
plan_id: "0019"
plan_size: médio
plan_type: feature
core: model
module: norm-evolution-evidence
block: ""

# history
author: Claude
created: 2026-11-21
status: done
version: 1.0.0
updated: ""
approved_by: "Bortoli Rafael"
approved_at: "2026-11-21"

# system
scope: project
auto_load: false
dependencies: []
---

# Ciclo de evolução da norma — 2: evidência no huddle e destino `método`

> **Tipo proposto: `feature`** — campo novo no huddle, destino novo no fechamento e no
> `log-resolver`, dois comandos, com código e norma. **Porte proposto: `médio`** — pela *Quando cada
> porte cabe*, há passos (pergunta 1, não), e uma sessão os executa em sequência (pergunta 2, sim).
> O humano confirma tipo e porte na aprovação. *(recomendação do Claude)*
>
> **Autoria.** Por causa da `H-20` e da `H-21`, cada item leva a marca de quem o sustenta:
> **[humano]** decisão do humano, **[Claude]** recomendação do Claude, **[medido]** fato medido,
> com o comando ou o arquivo. As recomendações `P-01` a `P-04` foram aceitas pelo humano em
> 2026-11-21 e viraram `D-04` a `D-07`.
>
> **Recorte.** Item 2 da série (`D-03` do [`0018`](0018-norm-evolution-log.md)), que
> concluiu o item 1. Visão, ordem e decisões da série ficam lá e são citadas, nunca copiadas.

## Objetivo

**Clarificar.** Feedback sobre o próprio método, registrado num projeto que o usa, não tem caminho
até o repositório do método, e o fechamento do huddle o apaga. **[medido]** A `H-10` do huddle do
AmFlow, de 2026-10-01, registra um defeito do método: o `backlog.projetar` corta tarefa de várias
linhas. A própria entrada diz que a correção vai para o DecodeAndCode. Em 2026-11-21, 51 dias
depois, não chegou, e o defeito reproduz: `backlog._tarefas` devolve só a primeira linha de um item
quebrado. **[medido]** O único defeito medido no AmFlow que chegou aqui, o do `0010`, veio relatado
em conversa pela sessão que orquestrava o plano de lá. **[medido]** Hoje `huddle-fechar` aceita
destino em texto livre e tira o texto da entrada do arquivo, e `log-resolver` apaga o `E-XX`. Um
destino "DecodeAndCode" deixaria só a linha em `## Fechadas`.

**Métricas** *(recomendação do Claude)*:

- conteúdo perdido no fechamento com destino `método`: alvo 0, porque toda `H-XX` e todo `E-XX`
  fechados assim deixam um `M-XX` que só sai quando a pessoa diz que o levou;
- caminho absoluto do projeto ou da pessoa num `M-XX` gerado de `E-XX`: alvo 0, verificável por
  teste;
- entrada com origem declarada: hoje 0 por construção, porque o campo não existe. Quantas o usarão
  não é meta: é dado para os itens 3 e 5.

**Beneficiário:** quem mantém o método, que recebe o defeito com a evidência sem depender de alguém
lembrar de contar; e a pessoa no projeto que usa o método, que fecha a entrada sem perder o texto.

**Evitar.**

| Alternativa | Por que não basta |
|---|---|
| O que existe: `huddle-fechar <H-XX> "DecodeAndCode"`, texto livre | O texto sai do arquivo no fechamento **[medido]**. Ou a pessoa o leva na hora, ou ele se perde. A `H-10` do AmFlow mostra que escrever "vai para o DecodeAndCode" não leva nada a lugar nenhum **[medido]** |
| Manter a entrada aberta até levá-la | Ela já foi decidida, e a pauta a rediscutiria a cada huddle, contra a propriedade da seção *Huddle* ("quando resolve, sai"). Também não serve ao `E-XX`, que não tem entrada no huddle **[Claude]** |
| Seção `## Método` no arquivo de huddle, versionada | Sobrevive ao clone, mas o `E-XX` levado para lá poria traceback com caminho absoluto num arquivo do git. O despejo passaria a ter três estados, e o `lint_arquivo` cresceria junto **[Claude]** |
| O resumo na linha de `## Fechadas` | Uma célula de tabela não carrega traceback. Marcar como levado exigiria reescrever linha fechada, o que hoje nada faz **[Claude]** |
| Imprimir o bloco no fechamento, sem guardar | É a primeira alternativa com formato melhor: quem não leva na hora perde **[Claude]** |
| Abrir issue ou PR no repositório do método por script | A `D-09` do `0018` pede envio **manual**: o projeto pode ser de terceiro, e haveria credencial e rede **[humano]** |

**Reduzir** *(recomendação do Claude)*. O conteúdo vai para `.claude/log/metodo/M-XX.md`, no padrão
do `E-XX`: lugar que o git já ignora, contador que só cresce, frontmatter, e saída só por comando
explícito. Chegam lá dois caminhos: `huddle-fechar <H-XX> método`, com o texto genérico no stdin, e
`log-resolver <E-XX> método`, mecânico. Mais dois comandos, um que lista e um que marca como levado;
uma linha na pauta; e o campo de evidência, opcional, validado só pelo prefixo. As cinco skills não
mudam: o `huddle-fecho` já imprime a subseção *Momento* da norma, que passa a pedir `--evidencia`.

## Gates

| Gate | Resposta |
|---|---|
| **A — necessidade real** | **Sim, com base estreita, somada a exigência explícita do humano.** **[medido]** Um caso: a `H-10` do AmFlow, defeito do método parado há 51 dias e ainda reproduzível. **[medido]** A ressalva é que ela se perdeu porque **nenhum huddle aconteceu no AmFlow**: 10 abertas, 0 fechadas, sem `last_huddle`, e o arquivo segue único, sem `huddle-migrar`. Este plano trata a perda seguinte, fechar e esquecer, não essa. **[medido]** Não medido: o caminho `E-XX` para `método` tem 0 casos reais. Aqui o log tem 23 eventos desde o `0018`, 0 bloqueios e um só `E-XX`, o `E-01`, gerado por teste e resolvido como `descartado`. O AmFlow não tem `.claude/log/`, porque o `0018` ainda não saiu em release (`plugin.json` em 2.3.1, última tag `v2.3.1`). **[humano]** O gate A deste item deveria se responder com o dado do log (`0018`, *Próximos planos*). Esse dado não existe porque o humano decidiu, em 2026-11-20, desenvolver o item antes do release e antes de validar o log em uso real: exceção à `D-03` do `0018` pelo protocolo de exceção, *exigência explícita do humano* (`D-03` abaixo) |
| **B — mínimo viável** | **[Claude]** Cortado: **aviso de abertura para `M-XX`**, porque a pauta basta; **prazo ou alarme de 7 dias para `M-XX`**; **evidência na linha de `## Fechadas`**, que mudaria a tabela e os regex (itens 3 e 5 dizem se faz falta); **evidência escrita sozinha** quando `log-resolver <E-XX> <H-XX>` aponta para uma entrada; **conferir se o `E-XX` ou o `L-XX` citado existe**, porque só o prefixo é validado; **limpeza de prosa por script**, com só a troca mecânica de caminhos e a pessoa revisando o resto; **sexto tipo de evidência** para relato vindo de outro projeto; **envio automático** (`D-09` do `0018`, **[humano]**); **mudança nos `SKILL.md` das cinco skills**, porque a instrução chega pelo `huddle-fecho`. **Não cortado:** o campo de evidência, que é decisão do humano (`D-09` do `0018`). Hoje o único leitor dele é o `M-XX`, e os leitores de fato são os itens 3 e 5 (`L-04`) |

## Decisões

| # | Decisão | Autoria |
|---|---|---|
| D-01 | **Escopo do item 2 é a `D-09` do [`0018`](0018-norm-evolution-log.md)**, citada de lá: campo de evidência, destino `método` no fechamento do huddle, saída 2 alimentando `método`, comando que lista, envio manual e sem conteúdo do projeto, AmFlow como primeiro alimentador | **[humano]**, 2026-11-20 |
| D-02 | **`método` como destino do `log-resolver` entra com este item** (`D-15` do `0018`) | **[humano]**, 2026-11-20 |
| D-03 | **Este item é desenvolvido antes do release e antes de validar o log do `0018` em uso real.** Exceção explícita à `D-03` do `0018` ("valida cada item antes de escalar"), pelo protocolo de exceção (`principles.md`), por *exigência explícita do humano*. O que já foi tentado: o item 1 está entregue e foi remedido num projeto descartável, mas não em uso real. O que se propõe no lugar: desenhar o item 2 sobre o desenho do item 1, sem o dado de uso. Quem aprovou: Bortoli Rafael | **[humano]**, 2026-11-20 |
| D-04 | **Onde o conteúdo do `método` mora até ser levado?** **`.claude/log/metodo/M-XX.md`**, ignorado pelo git, escrito por script no fechamento. Sai só por `dc.py metodo-levado <M-XX> "<onde>"`, que registra o evento `levado` com o destino. A numeração vem de `metodo/.ultimo`, pelo mesmo `_proximo_id` do `E-XX`, que passa a receber o prefixo. Frontmatter: `id`, `origem` (`H-XX` ou `E-XX`), `data`, `versao` do plugin e `evidencia`. A `evidencia` só é copiada quando o prefixo é `E-XX` ou `L-XX`, que são ids sem conteúdo; `bloqueio:`, `gate:` e `revisão:` levam nome do projeto e ficam de fora — se importarem ao método, entram no texto genérico, redigido com a pessoa (`L-06`, revisão de 2026-11-21). **Trade-off aceito:** não é versionado, então `M-XX` não levado se perde com o clone, como o `E-XX` (`L-02`). As alternativas estão em *Evitar* | **[Claude]**, aceita pelo humano em 2026-11-21 (era `P-01`) |
| D-05 | **"A saída 2 alimenta `método` direto" quer dizer o quê?** **`log-resolver <E-XX> método`, sem `H-XX` no meio, e nunca automático.** Todo `E-XX` virar `M-XX` sozinho contrariaria a `D-08` do `0018` (o erro só sai por resolução) e a revisão pela pessoa. O `M-XX` é gravado **antes** de o `E-XX` ser apagado. Se a gravação falhar, o `E-XX` fica | **[Claude]**, aceita pelo humano em 2026-11-21 (era `P-02`) |
| D-06 | **Como o conteúdo sai sem nada do projeto?** **`H-XX`:** `huddle-fechar <H-XX> método` exige o texto genérico no stdin. Ele é redigido na conversa do huddle, quando o contexto ainda existe, e aprovado pela pessoa antes da gravação. Sem stdin, recusa com 1 e não fecha. Se a gravação do `M-XX` falhar, a entrada não fecha. Fechada, a linha leva o destino `método: M-XX`. **`E-XX`:** cópia mecânica com o subcomando sem os argumentos, o código, o fim da saída e a versão. Ficam de fora o `alvo`, o `HEAD` e o working tree. A raiz do projeto vira `<projeto>`, e o diretório da pessoa vira `~`. Nos dois casos, `metodo-listar` mostra o `M-XX` inteiro, frontmatter e texto, para a pessoa revisar antes de levar (`L-03`, `L-06`) | **[Claude]**, aceita pelo humano em 2026-11-21 (era `P-03`) |
| D-07 | **Formato do campo de evidência.** **Opcional:** `huddle-abrir <tipo> --evidencia "<origem>"`. O prefixo vem de um vocabulário fechado de cinco, as origens da `D-09`: `E-XX`, `L-XX`, `bloqueio: <regra>`, `gate: <comando>` e `revisão: <plano>`. Depois do prefixo, o texto é livre. Recusa-se o valor que não é escolha nenhuma, nunca a escolha, como no tipo da entrada. Fica numa linha `Evidência: <origem>` no **fim** do corpo, para a pauta seguir mostrando a primeira linha do texto. O cabeçalho `### H-XX · …` não muda, e os regex que o leem também não. O `lint_arquivo` aceita entrada sem a linha, como as antigas, e recusa a linha com prefixo fora do vocabulário | **[Claude]**, aceita pelo humano em 2026-11-21 (era `P-04`) |

## Tarefas

- [x] Norma, seção *Huddle*: o campo de evidência (formato, os cinco prefixos, opcional, onde fica) e o destino `método` no fechamento, com o texto genérico no stdin. Em *Momento*, que chega às cinco skills pelo `huddle-fecho`, passar `--evidencia` quando a entrada tiver origem. Seção *Log de uso*: `metodo/M-XX.md`, `método` no vocabulário do `log-resolver`, a troca mecânica de caminhos, `metodo-listar` e `metodo-levado`, e o `M-XX` que só sai por `metodo-levado`. Nesta cópia, onde o repositório do método é o próprio projeto, levar é abrir aqui um `H-XX` ou registrar um `L-XX` no plano a que o defeito pertence, e então rodar `metodo-levado <M-XX> "<H-XX ou L-XX>"`
- [x] `huddle.py`, com teste: `abrir(..., evidencia=None)` valida o prefixo e grava a linha no fim do corpo; `lint_arquivo` recusa prefixo fora do vocabulário e aceita entrada sem a linha
- [x] `eventos.py`, com teste: `registrar_metodo(projeto, origem, texto, evidencia)` devolve o `M-XX` ou `None`, sem levantar; `metodos(projeto)` lista os pendentes; `levado(projeto, id, onde)` apaga e registra o evento; `resolver` aceita `método`, grava o `M-XX` a partir do `E-XX` com a troca de caminhos e só então apaga o `E-XX`; `_proximo_id` recebe o prefixo
- [x] `dc.py`, com teste: `huddle-abrir --evidencia`; `huddle-fechar <H-XX> método` lendo o stdin, gravando o `M-XX` antes de fechar e saindo com 1 sem fechar se faltar texto ou a gravação falhar; `log-resolver <E-XX> método`; `metodo-listar`; `metodo-levado <M-XX> "<onde>"`, que sai com 1 se o `onde` vier vazio; `huddle-pauta` lista os `M-XX` pendentes em `## Log`
- [x] `huddle/SKILL.md`: no passo 1, `método` entre os destinos do `log-resolver`; no passo 2, a saída `método`, em que o texto genérico é redigido com a pessoa, mostrado inteiro e gravado só depois de aprovado; em `registrar`, perguntar a evidência, que é opcional; o subcomando novo na lista. `lint_skill` sem problema. O guia [`docs/recursos/huddle.md`](../../recursos/huddle.md) ganha `--evidencia`, o destino `método`, `metodo-listar` e `metodo-levado` (revisão de 2026-11-21)
- [x] `scripts/test-python.sh` verde, inteiro; `empacotar.verificar` e o ciclo instalado aprovam o pacote
- [x] Remedição (*Remedição*)

## Oráculo

| Alvo | Como se sabe que funcionou |
|---|---|
| Evidência | Teste: `huddle-abrir padrão --evidencia "E-03"` grava a linha no fim do corpo, e a pauta mostra a primeira linha do texto, não a evidência; `--evidencia "palpite"` sai com 1 sem escrever; o huddle desta cópia, com as entradas antigas sem a linha, passa no `huddle-lint` |
| `método` no huddle | Teste: `huddle-fechar H-XX método` sem stdin sai com 1 e a entrada continua aberta; com stdin, cria o `M-XX` com `origem`, `evidencia` e o texto — a evidência `E-03` copiada, a `bloqueio: sem-segredo` não —, e a linha de `## Fechadas` diz `método: M-XX`; com a gravação do `M-XX` falhando, a entrada continua aberta |
| `método` no `log-resolver` | Teste: um `E-XX` com traceback que cita a raiz do projeto e o diretório da pessoa vira um `M-XX` sem nenhum dos dois caminhos absolutos, sem `alvo`, `head` nem working tree; com a gravação falhando, o `E-XX` continua lá |
| Fila | Teste: `metodo-listar` mostra os dois; `metodo-levado M-01 "DecodeAndCode H-22"` apaga o arquivo e registra `levado`; o `M-XX` seguinte não reusa o id, nem com a pasta vazia |

## Remedição

Num projeto de prova com o pacote novo e o bootstrap feito: abrir uma entrada com `--evidencia`,
fechá-la como `método` com um texto genérico, forçar uma saída 2 do `dc.py` e resolvê-la como
`método`. Esperado: dois `M-XX`. O do `E-XX` não traz caminho absoluto, `HEAD` nem alvo. A
`huddle-pauta` e o `metodo-listar` mostram os dois, `metodo-levado` apaga um, e `.claude/log/` não
aparece no `git status`.

### Resultado — 2026-11-21

Pacote construído por `empacotar.construir` no scratchpad da sessão (`verificar` sem problema), num
projeto descartável com git e bootstrap, rodando o `dc.py` do pacote. Duas rodadas: a segunda
depois da correção abaixo, num projeto novo.

| Alvo | Resultado |
|---|---|
| Evidência | `huddle-abrir padrão --evidencia "E-01 do projetar-backlog"` gravou `H-01` com a linha no fim do corpo; `huddle-lint` deu `ok` |
| `método` no huddle | Sem stdin, `huddle-fechar H-01 método` saiu 1 e a entrada ficou aberta. Com o texto, gravou `M-01` com `origem: "H-01"` e `evidencia: "E-01"` — só o id, sem o resto do valor —, e a linha de `## Fechadas` diz `método: M-01` |
| `método` no `log-resolver` | `dc.py normas docs/plan/model/0007-segredo/01.md` saiu 2 e gravou `E-01`; `log-resolver E-01 método` gravou `M-02` e apagou o `E-01`. No `M-02`, nenhuma ocorrência do caminho do projeto, do alvo, de `head:`, `alvo:` ou do working tree; a mensagem da exceção ficou `'<projeto>/<alvo>'` |
| Pauta e listagem | A `huddle-pauta` mostrou `## Log desde …` com `M-01 (de H-01)` e `M-02 (de E-01)` pendentes; o `metodo-listar` mostrou os dois inteiros, frontmatter e texto |
| `metodo-levado` | `metodo-levado M-01 "DecodeAndCode H-22"` apagou o `M-01`; o `metodo-listar` passou a mostrar só o `M-02` |
| `git status` | Só `docs/plan/system/huddle/`, o arquivo versionado da pessoa; `.claude/log/` fora |

**Achado da execução**, corrigido nela: na primeira rodada, o `M-02` trazia o alvo dentro da saída
— a mensagem do `FileNotFoundError` repete o caminho da unidade, com o nome do plano. A `D-06` diz
que o alvo fica de fora, e a cópia só o tirava do frontmatter. O `M-XX` vindo de `E-XX` passou a
trocar o alvo por `<alvo>` também dentro da saída, com teste. A norma diz isso na tabela de
*Feedback ao método*.

## Independência

**[Claude]** O teste da norma (*Avaliação de escopo*) separa as duas partes, com folga pequena. O
campo de evidência, sozinho, deixa o sistema válido, mas quase sem uso: agora ninguém o lê. O
destino `método`, sozinho, é válido e útil. **Recomendação: não dividir.** O campo cabe numa flag e
numa linha de lint, o `M-XX` é o primeiro leitor dele, e foi o humano quem agrupou os dois no
item 2 (`D-09` do `0018`). Dividir custaria um ciclo de plano para cerca de vinte linhas.

**Concorrência** **[medido]**. Nenhum plano está `em desenvolvimento` em `_planos.md`; o `0018`,
que também tocou `eventos.py`, `dc.py` e a seção *Huddle*, está concluído. No `_inbox` resta o
`apply-plugin-review`, que está desatualizado (`H-18`), é anterior à skill `huddle` e não a toca.
Nenhum item do `_backlog.md` cobre este trabalho.

## Lacunas

| # | Lacuna | Detalhe |
|---|---|---|
| L-01 | **O primeiro alimentador real ainda não pode alimentar** | **[medido]** O AmFlow usa o 2.3.1, sem o `0018`, e o huddle dele segue no arquivo único, que faz o `huddle-abrir` recusar até o `huddle-migrar` (`L-05` do `0008`, trabalho do AmFlow). O ganho só se mede depois do release e dessa migração |
| L-02 | **`M-XX` não é versionado** | **[Claude]** Se perde com o clone, como o `E-XX`. É o preço de não pôr traceback no git (`P-01`) |
| L-03 | **O "sem conteúdo do projeto" não é verificável por script** | **[Claude]** A troca mecânica cobre caminho absoluto. Nome de plano, de módulo ou um trecho de código do projeto no texto dependem da revisão da pessoa, no fechamento e na listagem |
| L-04 | **A evidência não sobrevive ao fechamento, a não ser no `M-XX`** | **[Claude]** A linha de `## Fechadas` não a leva (corte do gate B). Os itens 3 e 5, que a contam, dizem se isso faz falta |
| L-05 | **O caso medido se perdeu por outro motivo** | **[medido]** A `H-10` do AmFlow ficou parada porque nenhum huddle aconteceu lá, não por falta do destino `método`. Este plano não resolve essa causa |
| L-06 | **A evidência leva nome do projeto para o `M-XX` sem passar pela redação** | **[Claude]** O `P-01` copia a `evidencia` da entrada para o frontmatter do `M-XX`, e três dos cinco prefixos do `P-04` carregam instância: `bloqueio: <regra>`, `gate: <comando>` e `revisão: <plano>`. O texto genérico é redigido e aprovado na conversa (`P-03`), mas a evidência vai por cópia. O plano não diz se o `metodo-listar` mostra o frontmatter para a pessoa revisar (revisão de 2026-11-21). **Fechada em 2026-11-21**, antes da aprovação: o `P-01` copia só a evidência `E-XX` ou `L-XX`, as outras ficam de fora, e o `P-03` diz que o `metodo-listar` mostra o `M-XX` inteiro |
| L-07 | **A raiz do plugin fora da home fica no `M-XX`** | **[medido]** Na remedição, o pacote estava no scratchpad, em `/private/tmp/…`, e o traceback do `M-02` trouxe esse caminho inteiro: não é do projeto nem da home, e a `D-06` só troca esses dois. Instalado pelo marketplace, o plugin mora em `~/.claude/plugins/…`, que vira `~`. Fica para a revisão da pessoa no `metodo-listar` (`L-03`) |

## Fonte

- [`0018-norm-evolution-log.md`](0018-norm-evolution-log.md): `D-03`, `D-05`, `D-08`, `D-09`, `D-15`, *Resultado* e *Próximos planos*
- [`modelo-dev-units.md`](../system/modelo-dev-units.md): *Huddle*, *Log de uso*, *Antes do plano*, *Avaliação de escopo* e *Quando cada porte cabe*
- [`0010-fix-norma-entry-gate.md`](0010-fix-norma-entry-gate.md), *Fonte*: o defeito medido no AmFlow e relatado em conversa
- [`0008-wire-huddle-cycle.md`](0008-wire-huddle-cycle.md), `L-05`
- `AmFlow/docs/plan/system/huddle.md`, `H-10`, lido em 2026-11-21 sem escrita
- `.claude/skills/decode-and-code/scripts/huddle.py`, `eventos.py`, `dc.py` (`huddle-abrir`, `huddle-fechar`, `log-resolver`, `huddle-pauta`, `huddle-fecho`) e `backlog.py` (`_tarefas`); `.claude/skills/huddle/SKILL.md`
- [`huddle/bortoli-rafael.md`](../system/huddle/bortoli-rafael.md), `H-18` a `H-21`

## Backlog

<!-- backlog:start -->
- [x] Norma, seção *Huddle*: o campo de evidência (formato, os cinco prefixos, opcional, onde fica) e o destino `método` no fechamento, com o texto genérico no stdin. Em *Momento*, que chega às cinco skills pelo `huddle-fecho`, passar `--evidencia` quando a entrada tiver origem. Seção *Log de uso*: `metodo/M-XX.md`, `método` no vocabulário do `log-resolver`, a troca mecânica de caminhos, `metodo-listar` e `metodo-levado`, e o `M-XX` que só sai por `metodo-levado`. Nesta cópia, onde o repositório do método é o próprio projeto, levar é abrir aqui um `H-XX` ou registrar um `L-XX` no plano a que o defeito pertence, e então rodar `metodo-levado <M-XX> "<H-XX ou L-XX>"`
- [x] `huddle.py`, com teste: `abrir(..., evidencia=None)` valida o prefixo e grava a linha no fim do corpo; `lint_arquivo` recusa prefixo fora do vocabulário e aceita entrada sem a linha
- [x] `eventos.py`, com teste: `registrar_metodo(projeto, origem, texto, evidencia)` devolve o `M-XX` ou `None`, sem levantar; `metodos(projeto)` lista os pendentes; `levado(projeto, id, onde)` apaga e registra o evento; `resolver` aceita `método`, grava o `M-XX` a partir do `E-XX` com a troca de caminhos e só então apaga o `E-XX`; `_proximo_id` recebe o prefixo
- [x] `dc.py`, com teste: `huddle-abrir --evidencia`; `huddle-fechar <H-XX> método` lendo o stdin, gravando o `M-XX` antes de fechar e saindo com 1 sem fechar se faltar texto ou a gravação falhar; `log-resolver <E-XX> método`; `metodo-listar`; `metodo-levado <M-XX> "<onde>"`, que sai com 1 se o `onde` vier vazio; `huddle-pauta` lista os `M-XX` pendentes em `## Log`
- [x] `huddle/SKILL.md`: no passo 1, `método` entre os destinos do `log-resolver`; no passo 2, a saída `método`, em que o texto genérico é redigido com a pessoa, mostrado inteiro e gravado só depois de aprovado; em `registrar`, perguntar a evidência, que é opcional; o subcomando novo na lista. `lint_skill` sem problema. O guia [`docs/recursos/huddle.md`](../../recursos/huddle.md) ganha `--evidencia`, o destino `método`, `metodo-listar` e `metodo-levado` (revisão de 2026-11-21)
- [x] `scripts/test-python.sh` verde, inteiro; `empacotar.verificar` e o ciclo instalado aprovam o pacote
- [x] Remedição (*Remedição*)

7 de 7 tarefas concluídas · atualizado em 2026-11-21
<!-- backlog:end -->
