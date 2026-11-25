---
# about
name: redesign-plan
type: doc
project: ""
description: Plano do redesign em duas fases — criar o codex a partir do inventário e do brief, e migrar para ele, um por vez, os consumidores da norma — com decisões, partes, critérios de aceite e checagens
tags: [codex, redesign, plano]

# history
author: Bortoli
created: 2026-11-25
status: draft
version: 0.1.0
updated: ""

# system
scope: project
source: ""
auto_load: false
checksum: ""
dependencies: [atomic-inventory, redesign-brief, redesign-handoff]
---

# Plano do redesign — da norma ao codex

Plano de execução do redesign que substitui a norma
([`modelo-dev-units.md`](../plan/system/modelo-dev-units.md)) pelo codex, em duas fases: a fase 1 cria
o codex; a fase 2 migra para ele, um por vez, tudo o que hoje consome a norma. O conteúdo do codex vem
do [inventário atômico](atomic-inventory.md) e do [brief](redesign-brief.md); este plano diz como
chegar lá e não repete o que eles dizem.

**Estado:** escrito em 2026-11-25; execução autorizada só para a parte 1.1, em 2026-11-25. Nenhuma
outra parte começa sem a aprovação da pessoa.

**Convenções:** "item NN" é o item NN do inventário; os caminhos partem da raiz do repositório.

## Objetivo

Ter o codex como o método do DC no plugin, com a norma apagada e nenhum ponto do plugin dependendo
dela. Aqui, redesign é o trabalho todo: a fase 1 e a fase 2, que o brief chama de redesign e de
propagação (`redesign-brief.md:231-232`), e a verificação final, que o fecha.

## Escopo

- **Dentro:** as partes das fases 1 e 2 e a verificação final.
- **Fora:** a revisão geral do DC e a release 3.0, que vêm depois da verificação final
  (`redesign-brief.md:231-232`); a revisão dos planos anteriores ao redesign, que ficam como estão
  (item 41); a extração do padrão de código (item 28); a memória de execução (item 44).

## Decisões

| # | Data | Decisão |
|---|---|---|
| D-01 | 2026-11-25 | O redesign se faz em duas fases: a fase 1 cria o codex, e a fase 2 migra para ele, um por vez, os consumidores da norma. Substitui a ideia de implementar todo o comportamento novo e trocar a norma de uma vez no fim. |
| D-02 | 2026-11-25 | Na fase 1, o codex é escrito sem a obrigação de manter o plugin funcionando. O conteúdo vem do inventário e do brief, e vale o inventário onde os dois divergem. A arquitetura da informação e a estratégia de conteúdo ficam abertas, para buscar a melhor. |
| D-03 | 2026-11-25 | Na fase 2, cada consumidor da norma passa a apontar para o trecho equivalente do codex. Equivalente, não idêntico: o codex é a versão melhorada, corrigida e equilibrada da norma. |
| D-04 | 2026-11-25 | Na migração, quando adaptar o consumidor ao que o codex diz for simples, muda o consumidor. Quando for complexo ou afetar uma feature inteira, a pessoa decide, com uma recomendação, entre um ajuste pontual no codex, feito com critério para não virar colcha de retalhos, e uma subparte própria que implementa o comportamento. O mesmo vale quando não estiver claro se a adaptação é simples. |
| D-05 | 2026-11-25 | A norma e o codex convivem durante a migração. Não é problema: a release atual segue com a norma, o trabalho acontece no plugin local, e a release nova só sai com o redesign concluído. |
| D-06 | 2026-11-25 | O teto de 8 passos por unidade sai quando o `lint_unidade.py` migrar, junto com o teste dele. Mantém a decisão 3 do brief, de o teto sair junto com a troca (`redesign-brief.md:258-261`). |
| D-07 | 2026-11-25 | A norma é apagada quando não sobrar consumidor dela. A migração nos projetos que já usam o DC (item 42) fecha a fase 2, antes da release. |
| D-08 | 2026-11-25 | O plano mora neste arquivo, fora do `_inbox/` e sem a numeração do `dc.py`. Não usa `intake`, `review-plan`, `derive`, `implement`, o backlog projetado nem os lints do DC como gate ([handoff](redesign-handoff.md), *Aviso central*). |

## Lacunas

Nenhuma registrada. Formato: `L-NN`, data, parte, o que faltou e a correção.

## Como executar

- Uma parte por vez, salvo onde as *Checagens* dizem que duas podem correr juntas.
- Cada parte entra por branch a partir de `dev` e PR para `dev`, com revisão manual da pessoa; na
  2.2, cada PR leva um lote do mapa. Nada de commit sem pedido.
- Quem executa uma parte entrega arquivos e relatório; a pessoa testa ou confere e aprova.
- Uma sessão aninhada recebe um brief curto que aponta para a seção da sua parte; a seção basta
  sozinha.
- Parte com *Detalhamento pendente* é detalhada e aprovada antes de começar.
- Quando um passo chamaria uma skill ou um script do DC, faz-se à mão o que ele faria de útil, e a
  pessoa é avisada (D-08).
- Ao fechar uma parte, o campo *Estado* recebe a data e o PR.
- Se a execução mostrar que uma parte estava insuficiente, a correção é da parte, registrada como
  lacuna.

## Fase 1 — Criar o codex

A fase 1 não toca em nada que consome a norma: o plugin segue funcionando com ela (D-05).

### Parte 1.1 — Pontos em aberto

- **Entrega:** cada ponto abaixo decidido com a pessoa e registrado no inventário com a data.
  - Os sete da tabela *Termos e pontos em aberto* (`atomic-inventory.md:1052-1060`), entre eles se o
    brief recebe as três divergências ou se o inventário basta.
  - Quatro achados em 2026-11-24, fora da tabela:
    1. Quando o plano de correção recebe número: os itens 11 e 18 ligam o número à aprovação do
       plano técnico, P4 (`atomic-inventory.md:215`, `:315`), que a correção não tem, e o item 13
       não diz.
    2. Numeração, `_planos.md` e nomenclatura: o brief as manda para o codex como regra
       (`redesign-brief.md:399`), e o inventário não tem item para elas.
    3. Gates A e B: o item 50 diz que entram depois de revistos à luz das referências de produto
       (`atomic-inventory.md:808-809`), sem dizer quem os revê nem quando.
    4. MVP no DC: o trecho do item 66 marcado "proposta, sem fonte"
       (`atomic-inventory.md:1039-1040`) precisa de confirmação.
- **Alvo:** `docs/codex/atomic-inventory.md`; `docs/codex/redesign-brief.md` só se a decisão sobre as
  divergências pedir.
- **Depende de:** —
- **Critério de aceite:** nenhum ponto sem decisão datada; nenhum trecho do inventário marcado
  "proposta, sem fonte"; nenhum campo de item vazio ("—") sem motivo.
- **Como verificar:** leitura da tabela de pontos em aberto e busca por "sem fonte" e ": —" no
  inventário.
- **Onde roda:** esta sessão, ponto a ponto com a pessoa.
- **Estado:** em curso desde 2026-11-25.

### Parte 1.2 — Arquitetura da informação e estratégia de conteúdo

- **Entrega:** o guia do codex, decidido com a pessoa, em `docs/codex/codex-guide.md` (novo). Ele
  responde:
  - **Leitores e leitura:** quem lê o codex e quando — cada etapa lê o trecho de que precisa, quando
    roda (item 27), e quem mantém o plugin o altera (item 61) — e como cada trecho é achado sem ler o
    resto.
  - **Fronteira:** onde termina o que o codex diz — o que o DC faz, em que ordem, com que artefatos e
    com que garantias (`atomic-inventory.md:446-452`) — e onde começa o procedimento de cada etapa,
    que é da skill (`redesign-brief.md:435`); e o que é núcleo e o que é capítulo de módulo (itens
    34 e 58).
  - **Organização:** o sumário, a ordem, a divisão em arquivos, os nomes e o lugar no plugin, com o
    núcleo na pasta compartilhada das skills (`redesign-brief.md:436`).
  - **Tipos de conteúdo:** conceito, regra ou contrato, gate, workflow, referência de produto e
    invariante, cada um com o seu modelo de seção.
  - **Regras de escrita:** o teste da regra de dependência (`atomic-inventory.md:881-882`); uma fonte
    por fato (item 55); nada de mecanismo, evidência ou história (item 27); os termos do inventário
    como glossário; como citar as referências de produto; a política de idioma do projeto.
  - **Como mudar o codex depois:** a regra que o mantém coerente quando a fase 2 o ajustar (D-04) —
    por exemplo, o ajuste reescreve a seção afetada no modelo dela, em vez de acrescentar exceção ou
    nota.
  - **Documentação de manutenção:** onde fica o que serve só a quem mantém o plugin — o contrato de
    módulo, o empacotamento e a release (itens 34, 58 e 61), o conteúdo da norma que a 2.1 mandar
    para lá e o próprio guia.
  - **Mapa:** cada item do inventário para a seção do codex, e cada *Mecanismo hoje* para fora do
    codex.
- **Como se chega ao guia:** duas ou três alternativas de organização, comparadas por um critério
  medido — por exemplo, quantas seções e quantos arquivos cada etapa precisa ler —, e a pessoa
  escolhe.
- **Alvo:** `docs/codex/codex-guide.md`.
- **Depende de:** 1.1.
- **Critério de aceite:** o guia responde a cada pergunta acima; todo item do inventário tem destino
  no mapa; nenhum *Mecanismo hoje* tem destino no codex; a escolha da organização cita a medição;
  aprovação da pessoa.
- **Como verificar:** o mapa conferido contra a lista de itens do inventário; o guia lido contra a
  lista de perguntas.
- **Onde roda:** esta sessão.
- **Estado:** pendente.

### Parte 1.3 — Texto do codex

- **Entrega:** o codex escrito no lugar e na estrutura do guia (1.2). Começa por um capítulo piloto,
  aprovado antes dos outros; o que o piloto ensinar entra no guia antes de seguir. Nenhuma skill lê o
  codex na fase 1.
- **Alvo:** os arquivos novos do codex. Na pasta compartilhada das skills, eles entram no pacote
  (`empacotar.py:114`).
- **Depende de:** 1.2.
- **Critério de aceite:** todos os itens do inventário cobertos conforme o mapa; cada trecho passa no
  teste da regra de dependência; nenhum fato em dois lugares; o texto segue o guia; a suíte passa
  (`scripts/test-python.sh`); aprovação da pessoa.
- **Como verificar:** leitura contra o mapa e o guia, e a suíte. A 1.3 fecha sem esperar a 1.4.
- **No fechamento:** a pessoa decide se o codex passa a ser a fonte da verdade do método, com o
  inventário e o brief como registro do redesign. Recomendação: sim, para que os ajustes da fase 2
  mudem um lugar só.
- **Onde roda:** esta sessão; depois do piloto, sessões aninhadas por capítulo, se o guia der um
  arquivo por capítulo.
- **Estado:** pendente.

### Parte 1.4 — Lints do codex

- **Entrega:** um lint que reprova mecanismo citado no codex — skill, script, hook, versão do Claude
  Code ou projeto (item 54) — e um lint que reprova trecho do codex repetido literalmente nas skills
  ou na foundation (item 55), com testes.
- **Alvo:** scripts e testes novos em `.claude/skills/decode-and-code/scripts/`. Os lints não são
  ligados ao `dc.py` nem ao `verificacao.py`, que consomem a norma: essa ligação entra na migração
  deles (2.2).
- **Depende de:** 1.2 para começar; 1.3 para fechar.
- **Critério de aceite:** a suíte passa (`scripts/test-python.sh`); cada lint reprova um caso de teste
  com o defeito que procura; os dois rodam limpos no codex aprovado na 1.3, e um defeito que acharem
  nele vira lacuna da 1.3, corrigida antes de a 1.4 fechar.
- **Como verificar:** a suíte e uma execução dos dois lints sobre o codex.
- **Detalhamento pendente:** como o lint reconhece mecanismo e o tamanho mínimo de um trecho
  repetido.
- **Onde roda:** aninhada.
- **Estado:** pendente.

## Fase 2 — Migração gradual

Consumir a norma é ler, copiar, extrair seção, linkar ou mencionar a norma, ou seguir uma regra dela
sem citá-la — no código, nas skills, nos hooks, nos testes e na documentação. A fase 2 começa por
levantar cada consumidor e depois troca um por vez.

### Parte 2.1 — Levantamento dos consumidores

- **Entrega:** o mapa da migração em `docs/codex/migration-map.md` (novo), com oito listas:
  1. **Consumidores da norma:** cada ponto, com o que consome; o sentido de "norma" ali; o trecho
     equivalente do codex; a classificação pela D-04; e como a migração dele se verifica. A palavra
     tem quatro sentidos:
     - o método, que vai para o codex;
     - a "norma do projeto", que vira o nome das três coisas: princípios, guidelines e guardrails
       (item 49);
     - o valor `norma` de `plan_type` e `unit_type`, que vira `rule` no formato novo e continua nos
       planos antigos (item 03);
     - o plural genérico "normas", as regras que valem para uma unidade — decisões do plano, seções
       da norma ou guidelines —, como na tabela `## Normas aplicáveis` das unidades
       (`docs/plan/model/0004-installable-method/01-project-anchor.md:104-107`) e no comando `normas`
       do `dc.py` (`dc.py:900`); não vira codex, e só a linha que cita a norma muda de destino.
  2. **Regras da norma seguidas sem citá-la:** o que segue uma regra ou um conceito da norma sem
     nomeá-la, achado lendo cada script, hook e skill do pacote contra o codex, e não por busca.
     Por exemplo: `porte.py` mede o porte com o vocabulário pequeno, médio e grande
     (`porte.py:4-5`), que o codex redefine (item 14); `reconciliar.py` reconcilia "duas cópias do
     método" (`reconciliar.py:2`), e o codex nunca é copiado para o projeto (item 56).
  3. **Nomes que mudam:** `intake` para `decode`, `implement` para `code` e norma para codex
     (`redesign-brief.md:192`), com as ocorrências.
  4. **O que o codex descreve e nenhum consumidor faz hoje:** cada comportamento novo, ligado ao
     consumidor cuja migração o traria, ou marcado sem consumidor. Por exemplo: o decode e a revisão
     novos (itens 06, 07, 31 a 33, 37, 50, 62, 63 e 66), o workflow de correção e o módulo (itens
     34, 39 e 58) e a foundation (itens 26, 28, 29 e 59).
  5. **Destino de cada seção da norma:** codex, skill, script, documentação de manutenção, no lugar
     decidido na 1.2, ou descarte. A norma tem 301 linhas de mecanismo e 115 que só servem a quem
     mantém o plugin (`redesign-brief.md:40-47`); nada disso pode sumir sem destino quando ela for
     apagada (2.3).
  6. **O que o DC grava num projeto a partir da norma:** além da cópia em `<plan_root>/system/`
     (item 42), o que as skills e os scripts do pacote gravam ou sugerem ao projeto com origem na
     norma — por exemplo, os princípios do método que o setup sugere a partir da tabela da norma
     (`.claude/skills/setup/SKILL.md:87`). Para cada um, o que a migração nos projetos faz com ele
     (2.4).
  7. **Restrições do brief:** cada restrição da tabela (`redesign-brief.md:190-200`) ligada à parte
     ou à subparte que a cumpre — por exemplo, a auditoria do pacote contra dado de outro projeto
     (`redesign-brief.md:199`), que nenhum consumidor faz hoje. Restrição que nenhuma parte cumpre
     vai à pessoa, com uma recomendação.
  8. **Ordem e lotes:** as subpartes da 2.2, com as dependências, as checagens de concorrência e o
     lote de PR de cada uma — por exemplo, as menções em documentação num lote só. A pessoa aprova os
     lotes.
- **Casos complexos:** cada um vai à pessoa com uma recomendação, pela D-04.
- **Verificação:** cada linha do mapa diz como a migração se verifica — teste automatizado, para
  script e hook; execução num projeto de prova, para skill cujo comportamento muda, como no spike da
  decisão 12 (`redesign-brief.md:328-330`); ou leitura contra o codex, para documentação e menção.
- **Pontos já conhecidos:**
  - `empacotar.py:118` e `:286` levam a norma ao pacote;
  - o bootstrap a copia para o projeto (item 42);
  - o brief registra que o `dc.py` extrai 11 seções dela pelo título (`redesign-brief.md:49-50`);
  - `normas.py` resolve a tabela `## Normas aplicáveis` das unidades, onde a palavra mistura
    sentidos;
  - `lint_unidade.py:46` guarda o teto (D-06);
  - `.claude/skills/rethink/SKILL.md:5` usa "norma do projeto".
  - Medição de 2026-11-23: `norma` em 138 arquivos (50 Python), `intake` em 24 (6 Python) e
    `implement` em 43 (13 Python) (`redesign-brief.md:281-282`).
- **Registro, fora do levantamento:** os planos e o índice deles (`docs/plan/model/`,
  `docs/plan/_planos.md`), os rascunhos de plano e a projeção do backlog em `docs/plan/_inbox/`
  (planos anteriores ao redesign, item 41), o registro do método
  (`docs/plan/system/registro-dev-units.md`, evidência e história), o huddle
  (`docs/plan/system/huddle/`), `docs/codex/`, `.claude/log/`, `dist/` e o histórico do git.
- **Alvo:** `docs/codex/migration-map.md`.
- **Depende de:** 1.3.
- **Critério de aceite:** a busca, por palavra inteira, por `norma`, `normas`, `modelo-dev-units`,
  `intake`, `implement` e pelos títulos das seções que o `dc.py` extrai, fora do registro, só acha
  pontos que estão no mapa ou falso positivo justificado; cada script, hook e skill do pacote foi
  lido contra o codex, e o que segue uma regra da norma está no mapa; no mapa, cada consumidor das
  listas 1 e 2 tem trecho equivalente, classificação e verificação, e os da lista 1, o sentido da
  palavra; cada comportamento da lista 4 está ligado a um consumidor ou classificado pela D-04; cada
  seção da norma e cada coisa da lista 6 têm destino; cada restrição do brief está ligada a quem a
  cumpre; aprovação da pessoa.
- **Como verificar:** a busca refeita contra o mapa, e a lista do que foi lido conferida contra os
  scripts, hooks e skills do pacote.
- **Onde roda:** esta sessão.
- **Estado:** pendente.

### Parte 2.2 — Migração dos consumidores

- **Entrega:** uma subparte por consumidor, `2.2.NN`, na ordem do mapa. Quando a troca só fecha
  mudando vários arquivos juntos — por exemplo, renomear uma skill e tudo o que a chama —, o grupo é
  uma subparte só. Um comportamento que a pessoa mandou implementar pela D-04 também vira subparte,
  no mesmo formato e com o mesmo critério.
- **Cada subparte**, detalhada e aprovada antes de começar, diz:
  - o consumidor e as linhas do mapa;
  - a entrega: as referências trocadas pelo trecho equivalente do codex, e o que a D-04 pedir;
  - o alvo, a dependência e onde roda.
- **Critério de aceite de toda subparte:**
  - o consumidor não aponta mais para a norma, e os outros sentidos da palavra seguem o mapa;
  - o consumidor faz o que o trecho equivalente do codex diz, verificado como o mapa manda;
  - a suíte passa e os lints da 1.4 rodam limpos, inclusive o de repetição sobre o consumidor;
  - um ajuste no codex segue o guia (1.2) e foi aprovado pela pessoa;
  - o mapa registra a linha como migrada.
- **Como verificar:** a suíte, os lints e a busca no consumidor.
- **Depende de:** 2.1 e 1.4.
- **Onde roda:** sessões aninhadas, uma subparte por vez, salvo duas que o mapa mostre sem arquivo em
  comum.
- **Estado:** pendente; as subpartes nascem do mapa.

### Parte 2.3 — Apagar a norma

- **Entrega:** `docs/plan/system/modelo-dev-units.md` apagado, com cada seção no destino que o mapa
  deu. Os links de planos fechados para a norma ficam como registro (item 42).
- **Alvo:** `docs/plan/system/modelo-dev-units.md`.
- **Depende de:** todas as subpartes da 2.2.
- **Critério de aceite:** a busca da 2.1 refeita só acha registro; todo destino do mapa foi cumprido;
  a suíte passa; o pacote é construído sem a norma.
- **Como verificar:** a busca, a suíte e um build do pacote.
- **Onde roda:** esta sessão.
- **Estado:** pendente.

### Parte 2.4 — Migração nos projetos que já usam o DC

- **Entrega:** na primeira sessão com a versão nova, a abertura avisa da migração. A migração apaga a
  cópia da norma do projeto e trata o que o mapa da 2.1 lista como gravado no projeto a partir da
  norma, cada coisa só com aprovação (item 42), para que nada no projeto repita ou contradiga o codex
  (item 55).
- **Alvo:** o hook de abertura da sessão (hoje `.claude/hooks/session_start.py`), um script novo da
  migração e o teste dele.
- **Depende de:** 2.3.
- **Critério de aceite:** num projeto com a cópia, o aviso aparece; sem aprovação, nada é apagado nem
  alterado; com aprovação, a cópia sai e cada coisa listada no mapa recebe o tratamento previsto; num
  projeto sem a cópia e sem nada do que o mapa lista, nenhum aviso.
- **Como verificar:** o teste.
- **Onde roda:** aninhada.
- **Estado:** pendente.

## Fechamento — Verificação final

- **Entrega:** um relatório que confere o redesign contra a tabela de restrições do brief
  (`redesign-brief.md:190-200`), cada restrição pelo seu *Como verificar* e na parte que o mapa da
  2.1 ligou a ela, e confere que todos os itens do inventário seguem cobertos pelo codex depois dos
  ajustes da fase 2. Uma restrição que um ajuste aprovado mudou vale como mudou, citando a decisão.
- **Alvo:** o relatório, anexado a este plano.
- **Depende de:** 2.4.
- **Critério de aceite:** toda restrição verificada; uma falha vira lacuna, corrigida antes de fechar;
  aprovação final da pessoa.
- **Como verificar:** cada *Como verificar* da tabela, executado.
- **Onde roda:** esta sessão.
- **Estado:** pendente.

## Checagens antes de aprovar

Feitas à mão em 2026-11-25, no lugar do `review-plan` (D-08).

**Duas partes no mesmo alvo ao mesmo tempo**

- 1.1 e 1.2 correm em sequência, as duas com a pessoa.
- 1.3 e 1.4 podem correr juntas: a 1.3 escreve os arquivos do codex, e a 1.4, scripts e testes novos.
- Nenhuma parte da fase 1 mexe em consumidor da norma. Em 2026-11-24, o `dc.py` e o `verificacao.py`
  chamavam os lints de hoje, e a 1.4 não liga os lints novos a eles.
- Na 2.2, nunca duas subpartes no mesmo arquivo; o mapa declara a ordem.
- 2.3, 2.4 e a verificação final, uma por vez.

**Dependências, conferidas e declaradas em cada parte**

- A 1.4 precisa da 1.2 para começar (lugar e estrutura do codex) e da 1.3 para fechar; a 1.3 fecha
  por leitura e pela suíte, sem esperar a 1.4.
- A 2.1 precisa do texto da 1.3 para achar os trechos equivalentes.
- A 2.2 precisa dos lints da 1.4, que são gate de cada subparte.
- O teto de 8 passos só sai na subparte do `lint_unidade.py` (D-06).

**Lacunas registradas:** nenhuma até aqui. O detalhamento pendente da 1.4 e de cada subparte da 2.2
está marcado nelas.
