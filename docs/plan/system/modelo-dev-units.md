---
# about
name: modelo-dev-units
type: doc
project: DecodeAndCode
description: Norma do modelo de Unidades de Desenvolvimento — hierarquia core/module/block/unit, unidade como arquivo autossuficiente para cold-start, estado derivado de verificação, norma de lote de 8 passos, avaliação de escopo e a skill dev-units. Documento normativo: define o formato que os planos obedecem
tags: [dev-units, metodologia, spec-driven, clean-architecture, core, cold-start, processo, documentacao, fix, plan]

# history
author: Bortoli
created: 2026-07-19
status: draft
version: 2.1.0
updated: 2026-07-24

# system
scope: project
auto_load: false
dependencies: []
---

# Modelo dev-units — norma

Define o método de **Unidades de Desenvolvimento**: hierarquia, formatos, nomenclatura, gates de
verificação e a skill que o executa.

> **Este documento é norma, não plano.** Não tem `plan_id`, não entra em `_planos.md`, e não segue o
> formato de plano — é o formato **que os planos obedecem**. A ordem importa: a norma existe
> primeiro, planos vêm depois e a seguem. Um documento que definisse o formato de plano *sendo* um
> plano nesse formato seria circular.

**Por que existe:** o padrão anterior especificava bem, mas não fechava o ciclo. Não definia
"pronto", não ligava à verificação, não tinha estado, e não produzia unidades executáveis por um
agente sem contexto. O resultado medido: 18 de 18 documentos em `status: draft` com código em
produção.

---

## O gargalo que o modelo precisa resolver

O fluxo que hoje produz os melhores resultados é **planejar com Opus, desenvolver com Sonnet**. Mas
ele depende de um passo manual e repetido: pedir, a cada vez, que as tarefas do plano sejam
documentadas com informação suficiente para **cold-start** — execução por um agente que não
participou do planejamento.

O modelo transforma esse pedido manual em **output obrigatório** da derivação de unidades.

> **Este documento é o mecanismo.** Hierarquia, formatos, gates de verificação e a skill que os
> executa — o que qualquer projeto que instala o método usa, e o que viaja no pacote. Evidência,
> decisões e história são registro de quem mantém este método, e ficam fora daqui: por definição,
> não viajam com o mecanismo para o projeto que instala.

---

## Conceitos estruturantes

### Plano e módulo são eixos diferentes

| | Plano | Módulo |
|---|---|---|
| Natureza | **Temporal** — um lote de trabalho aprovado | **Estrutural** — permanente |
| Densidade | Leve; não precisa ser denso | Denso — doc viva |
| Ciclo | Abre, executa, fecha | Nunca fecha, evolui |
| Contém | Backlog com as unidades | As unidades |

O plano nasce em `_inbox/`, passa por revisão e aprovação, e **é movido para a pasta que ele criou** —
tornando-se o registro permanente da intenção, ao lado das unidades que gerou.

### Cold-start é o critério de suficiência da unidade

> Uma unidade está completa quando um agente **sem nenhum contexto da conversa** consegue executá-la
> sem precisar perguntar nada.

Isso unifica o problema de origem: a variância do agente é variância por contexto insuficiente, e
cold-start é o caso extremo dessa condição. Uma unidade que sobrevive ao cold-start sobrevive a
qualquer contexto.

O teste é empírico e barato: **se o executor precisou perguntar, a unidade falhou** — e a correção é
da unidade, não do executor.

Campos exigidos:

| Campo | Estado no padrão atual |
|---|---|
| Contrato (Entrada/Saída/Auth/Efeito/Erro) | Existe |
| Sequência numerada (≤ 8 passos) | Falta em 26% |
| Dependências | Existe |
| **Arquivos a tocar** (caminhos concretos) | Não existe |
| **Normas aplicáveis** (referência, nunca cópia) | Implícito em skills de padrões, nunca declarado como norma |
| **Critério de aceite** | 0 de 18 |
| **Teste que o comprova** | 0 de 18 |

---

## Modelo proposto — cinco componentes

### 1. Hierarquia estrutural

```
System           → o repositório
  Core           → fronteira de ownership: declarada por projeto, em `config.json`
    Module       → capability de domínio: auth, catalog, mcp
      Block      → variação/extensão aditiva (opcional): login-google
        Unit     → fatia vertical mínima verificável: AU-02
```

> **Vocabulário.** Os nomes acima são a forma canônica em **código, caminhos de pasta e frontmatter**
> (`core`, `module`, `block`, `unit`). **Na prosa, usa-se português** — sistema, core, módulo, bloco,
> unidade. Forçar o inglês no texto explicativo custa precisão sem ganho: *"as unidades de
> desenvolvimento concluídas hoje"* não tem equivalente natural em inglês.

> **`core` aqui não é o `core` de Clean Architecture.** Aqui é uma fronteira **vertical** (por
> ownership) — conceitualmente um **Bounded Context** do DDD. Em Clean Architecture, "core" designa o
> centro **concêntrico** de política, oposto às bordas: um core vertical pode ter, ele próprio, um
> centro concêntrico de regras e bordas de infraestrutura. O princípio de Clean Architecture que este
> modelo adota é a **regra de dependência** (componente 3), não a nomenclatura.

**Ownership e localização são eixos independentes.** Um core pode possuir um módulo hospedado em
outro core, por necessidade arquitetural — por exemplo, o core hospedeiro é o único com a
infraestrutura de identidade configurada. O módulo declara `owner: <core-dono>` no frontmatter,
independente de onde estiver hospedado.

**Estrutura no disco — `docs/plan/`:**

```
docs/plan/
  _inbox/                     planos aguardando revisão e aprovação
  _planos.md                  tabela dos planos aprovados — fonte da numeração

  <core>/
    index.md                  doc geral do core, na raiz
    system/                   arquitetura, testes, ferramentas, infra do core
    <NNNN>-<módulo>/          módulo — a pasta recebe o número do plano que a criou
      <NNNN>-<módulo>.md      plano — mesmo nome da pasta
      index.md                doc geral do módulo
      01-<unidade>.md         unidade — numeração por plano
      02-<unidade>.md
      <NNNN>-<bloco>/         bloco — numerado pelo plano que o criou
        <NNNN>-<bloco>.md
        01-<unidade>.md
      fix/                    opcional

  <outro-core>/                index.md · system/
```

- **`system/`** guarda o que **não é feature** mas é fundamental ao core: definições de arquitetura,
  testes, ferramentas, infra. É onde vive a camada normativa do core (componente 3).
- **Bloco e `fix` são opcionais** — módulo simples guarda unidades direto na raiz.
- **Doc geral fica na raiz** do core e do módulo.

**Grão decidido:** bloco é **pasta**; unidade é **arquivo**. O arquivo por unidade é exigência do
cold-start — o executor recebe "leia este arquivo e execute", sem precisar extrair uma seção de um
documento de 500 linhas.

### 2. Estado derivado de verificação

A unidade não é dois artefatos (plano, depois documentação). É **um artefato com fases de vida**:

| Fase | O que a unidade é | Estado |
|---|---|---|
| Antes | Prescritiva — contrato a cumprir | `spec` |
| Durante | Contrato em execução | `wip` |
| Depois | **Descritiva — o que está verificado em produção** | `verified` |

**A transição não é editada à mão. É o teste passar.** Estado declarado manualmente é o que corrompe
— os 18/18 `draft` com código em produção são a prova.

Consequência: uma unidade `verified` cujo teste quebra **volta automaticamente a divergente**. A
documentação fica impedida de mentir em silêncio.

**Como o estado é computado:** a **unidade declara seu teste**; um script lê a declaração, roda o
alvo e deriva o estado. Direção `spec → teste`, nunca o inverso.

Evidência que fixou a direção: a suíte atual tem apenas **4 referências** a identificadores de
unidade (`auth.test.ts:46` → AU-10, `licenses.test.ts:203` → LI-05, `connect.test.ts:22` → AU-01,
`reviews.test.ts:271` → RE-04), e os `describe()` são nomeados por função (`getCart`, `normalize`).
Exigir que o teste declare a unidade obrigaria a reescrever 18 arquivos, com benefício idêntico.

Granularidade inicial: **arquivo de teste**. Aceita-se a imprecisão — uma unidade pode ficar
não-verificada por falha de outra no mesmo arquivo — em troca de custo zero sobre a suíte existente.
Refina-se para bloco de teste (`vitest -t`) conforme testes novos forem escritos.

**Duas projeções, uma fonte.** O resultado é projetado no arquivo da unidade **e** no backlog do
arquivo do plano. Nunca são duas declarações independentes — por isso não divergem.

### 3. Camada normativa — princípios, guidelines, guardrails, referências

Vive em **`<core>/system/`**.

| Elemento | O que é | Exemplo |
|---|---|---|
| **Princípio** | direção, o porquê — estável | mobile first |
| **Guideline** | como técnico | breakpoints, biblioteca de UI |
| **Guardrail** | limite verificável | nunca `process.env` direto |
| **Referência** | fonte externa canônica | docs oficiais de uma biblioteca-chave |

**Regra anti-drift inegociável: uma fonte por fato.** A unidade *referencia* a norma, nunca a copia.

O `CLAUDE.md` permanece como camada normativa de **processo**; `<core>/system/` cobre o **domínio**;
um core transversal cobre o que vale para **todos** os outros cores.

#### Guardrail fundador — regra de dependência entre cores

É o que dá **função arquitetural** ao nível core, e a tradução real do princípio central de Clean
Architecture (*Dependency Rule*): o projeto declara um grafo acíclico entre os seus cores, e nenhuma
referência corre contra a seta.

```
<core-periférico>  ──►  <core-central>
<core-central>     ──►  (nenhum core)
```

**Declarar não é aspiração:** o grafo se escreve quando o código já o respeita, e a declaração
formaliza um invariante que já vale. Por ser **verificável por grep** — referências de um core ao
outro, contadas nas duas direções —, é o candidato natural a primeiro guardrail automatizado.

> **O grafo é do projeto que instala, nunca do plugin.** O mecanismo — declarar o grafo e verificá-lo
> por contagem — viaja; a instância não. Projeto que não declara grafo não ganha o check: ele volta a
> ser julgamento, e o *Modo `review`* registra isso.

#### Guideline

Manifesto — campos exigidos e o que cada um decide:

| Campo | Exige | Por quê |
|---|---|---|
| `name` | não vazio | identifica a rule |
| `description` | não vazio, diz **quando** vale — não o que ensina | é o texto que decide relevância; descrição de conteúdo não ajuda a decidir escopo |
| `paths:` | presente, não vazio, cada entrada compila como glob **e** casa ao menos um arquivo que existe no repositório | ausente é princípio, não guideline; presente e inerte é falha silenciosa — a mesma classe que *Ativação silenciosa é o modo de falha da própria camada* descreve |

**Guideline é instância e nunca viaja no plugin** (`.claude/CLAUDE.md`, invariante 2). O mecanismo —
`lint_guideline` e o carregamento nativo por `paths:` — é o que o plugin empacota; `paths:`,
`description` e o corpo normativo são do projeto que instala.

**Skill e guideline separam-se por outro teste: skill é invocada; guideline é ativada.** Skill
responde *como fazer X* — é procedimento, e alguém precisa pedir. Guideline responde *o que vale
quando eu toco Y* — é norma, e entra sozinha pelo caminho do arquivo. Um caso medido: um documento
de 547 linhas, majoritariamente normativo com uma seção de procedimento, descrevia-se como
checklist de front-end, mas só entrava em contexto se alguém o invocasse — como guideline com
`paths: ["app/**"]`, ativaria sempre que um arquivo daquele escopo fosse tocado, sem depender de
lembrança.

#### Validar a ativação

Dois atos permanecem humanos, e nenhum script os substitui: **abrir uma sessão nova**, e **tocar um
arquivo do escopo** de uma guideline. O que deixa de ser julgamento é o que se conclui depois de
feito isso — vira gate onde é estrutural, e relatório onde só a sessão real prova algo.

`rules.auditar_arvore()` roda sem argumento e devolve `[]` quando a árvore de `.claude/rules/` e
`.claude/rules-off/` está sã — recusa isoladamente um `.md` em subdiretório de `rules/` (o matcher recursa, e o arquivo continua carregando), uma rule malformada em `rules/`, e
uma guideline quebrada em `rules-off/`, porque ela volta a ser ligada um dia.

`activation_notice.relatorio(caminho_log)` lê o log de uma sessão —
`$TMPDIR/decode-and-code-activation-<session_id>.log`, escrito pelo hook `InstructionsLoaded` — e
devolve uma linha por instrução carregada, com caminho, motivo e veredito:

```
python3 -c "
import sys; sys.path.insert(0, '.claude/skills/decode-and-code/scripts')
import activation_notice
for linha in activation_notice.relatorio('<caminho-do-log>'):
    print(linha)
"
```

**O controle de três estados**, e que qualquer projeto que instalar o plugin
repete para validar a própria camada: guideline **ligada** produz entrada no log; movida para
**subdiretório** de `rules/` também produz entrada — é o defeito; movida para o diretório **irmão**
`rules-off/` não produz entrada nenhuma.

Os resultados de cada medição não são recopiados aqui — vivem em *Validação de ponta a ponta*, no
plano que instanciou este mecanismo pela primeira vez.

**Ligar e desligar uma guideline é operação, não edição de arquivo.** `desligar` move o arquivo para
`.claude/rules-off/` — diretório **irmão**, fora do que o Claude Code carrega —, e `ligar` devolve, sempre por
`Path.rename`, nunca reescrita; o `registry.json` que acompanha é projeção, nunca fonte, e reporta
divergência entre o que ele registra e o estado real do disco em vez de escolher um dos dois em
silêncio.

#### Empacotamento — o que o plugin leva, e o que fica

`empacotar.construir(destino)` produz a árvore do plugin **sempre a partir da fonte real**
(`lib.repo_root()`), nunca de um parâmetro de origem — o plugin é o que este repositório produz de
si mesmo. Viaja o manifesto (`.claude-plugin/plugin.json`, fonte única de nome e versão), a skill
sem `scripts/tests/` nem `__pycache__` (o que inclui `huddle.py` — o mecanismo do huddle viaja como
qualquer outro script; a instância de cada projeto, não), os hooks com `hooks/hooks.json` gerado a
partir do bloco `hooks` do `settings.json` — a âncora `${CLAUDE_PROJECT_DIR}` reescrita para
`${CLAUDE_PLUGIN_ROOT}`, porque é essa variável que separa pacote de cópia —, e os dois agentes
(`agents/planner.md`, `agents/developer.md`), copiados no mesmo formato dos hooks.

**Não viaja:** `.claude/rules/*` (guideline é instância — parágrafo acima), `.claude/guardrails.json`
(idem: a regra é do projeto que instala, só o mecanismo do hook viaja), `scripts/tests/` (prova
deste repositório, não componente do método) e `docs/` (plano e norma são registro daqui — inclusive
`docs/plan/system/huddle.md`, que carrega a conversa deste projeto e é instância pura —; a
norma é citada, nunca copiada para dentro da skill). `empacotar.verificar(destino)` audita a árvore já
construída por **busca de conteúdo** — o **nome do repositório de origem** em qualquer arquivo, e a
âncora `CLAUDE_PROJECT_DIR` **dentro de `hooks/`** —, como par de `construir`, que decide por
**exclusão de caminho**: o mesmo invariante fechado nos dois sentidos.

> **A lista de marcadores é curta por medição, não por descuido**. Nome de arquivo que o
> mecanismo lê (`guardrails.json`) e caminho default que ele resolve (`docs/plan`) **são
> mecanismo**: proibi-los reprovava `guardrail.py`, o hook, `lib.py` e o `config.json` — e a âncora
> buscada no texto inteiro reprovava a própria constante que faz a troca. Instância é **nome de
> projeto**; e a auditoria só vale se rodar contra o pacote real, nunca só contra fixture.

**`empacotar.validar(destino)` é o par estrutural, e vem de fora.** Ele roda
`claude plugin validate` sobre a árvore construída: `verificar` recusa instância do projeto de
origem, e este confere o **formato** contra a ferramenta oficial, que conhece o manifesto e os
componentes. Ter só o nosso era conhecer só metade — o pacote passava no que nós sabíamos checar.
Binário ausente devolve problema em vez de levantar: gate que estoura por falta de dependência é
gate que se desliga.

> **Marketplace é distribuição, não instalação.** Medido na doc oficial em 2026-08-27: um plugin
> se instala direto, e `claude --plugin-dir <dir>` o carrega para desenvolvimento e teste — o
> `.claude-plugin/marketplace.json` só entra quando se quer **catalogar** plugins para outros. O
> pacote deste repositório passa em `claude plugin validate` sem marketplace nenhum.

**Os hooks do pacote carregam, e isso deixou de ser suposição em 2026-08-27.** O pacote foi
carregado por `--plugin-dir` a partir de `/tmp`, **fora do repositório de origem**, onde não existe
hook de projeto: o log de ativação registrou o carregamento, e a única linha foi o `CLAUDE.md`
global, que é exatamente o que aquele diretório tem. Qualquer linha ali só pode ter vindo do
plugin — é o controle que separa o hook empacotado do hook do projeto, e a troca de âncora para
`${CLAUDE_PLUGIN_ROOT}` é o que a torna possível.

> **Dentro do repositório de origem esse controle não existe.** O hook do projeto e o do pacote são
> o mesmo script, escrevendo o mesmo formato no mesmo caminho, e o log **não registra procedência**.
> A primeira tentativa de medir rodou lá dentro e foi inconclusiva por isso. Medir ativação de
> pacote exige diretório que não seja o que o produziu.

`empacotar.materializar(origem, projeto)` é a única operação que **recebe** uma origem: copia uma
guideline específica para `<projeto>/.claude/rules/`, e levanta `FileExistsError` sem tocar o
destino se ele já existir — nunca sobrescreve norma em silêncio. O plugin não embarca catálogo de
guideline nenhum; quem instala escolhe o que materializar.

**O pacote não é versionado** — `destino` default é `dist/decode-and-code/`, e `dist/` entra no
`.gitignore`. Árvore construída e commitada envelhece em silêncio a cada mudança da fonte. Publicar
é ato humano.

#### Reconciliação — divergência por conteúdo, nunca por versão

`reconciliar.comparar(origem, copia)` audita duas cópias do método por **SHA-256**, arquivo a
arquivo, nunca por número de versão declarado. Cada componente recebe um de quatro veredictos:
`idêntico` (mesmo hash), `divergente` (os dois existem, hash diferente), `só na origem` (a cópia
nunca recebeu) e `só na cópia` (a cópia ganhou coisa própria — sinal de fork). `_componentes` varre
a árvore inteira de cada lado, ignorando só `__pycache__` — inclui `scripts/tests/`, ao contrário
do que `empacotar` exclui para o pacote: aqui o objetivo é medir divergência real, e o fork dos
próprios testes de quem instalou é sinal, não ruído.

> **Versão declarada não é evidência.** Medido entre duas cópias reais do método: as duas
> declaravam a mesma versão, e ainda assim a maioria dos scripts compartilhados divergia. Uma
> reconciliação que confiasse na versão diria "em dia" e estaria errada. `reconciliar.relatorio`
> imprime a versão como **contexto**, nunca como veredito — o veredito de cada componente vem
> sempre do hash.

`reconciliar` só lê — nem a origem nem a cópia são escritas em caminho nenhum. Atualizar consumidor
é decisão de quem mantém a cópia — uma cópia pode ficar congelada por período indefinido, sem que
nenhuma unidade escreva nela.

### 4. Norma de lote e decomposição

- **Teto:** **8 passos de sequência por unidade**. Acima disso, a unidade divide-se.
- **Revisão de plano:** avalia contra a norma e **sugere os blocos**.
- **Decomposição:** informa se o trabalho vira **fases**, e cada fase em **unidades**.

O teto é o **p90 das 86 unidades existentes**, não arbítrio:

| Métrica | Passos |
|---|---|
| p50 | 5 |
| p75 | 6 |
| **p90 — teto adotado** | **8** |
| máximo atual | 15 (`PU-00`, `FE-11`) |

Marcaria 8 unidades como acima da norma — cerca de 9%, suficiente para o gate ter efeito sem travar
o fluxo.

Por que passos, e não linhas ou arquivos: é a única métrica **mensurável antes de implementar**.
Linhas de código só se conhecem depois, e gate corretivo não previne. Passos também correlacionam
com o número de decisões que o agente precisa tomar — a origem da variância.

**Unidade sem sequência é incompleta, não isenta.**

### 5. Preservação do que funciona

- **Comentário-cabeçalho** de rastreabilidade (90 refs) → formalizar como obrigatório.
- **Lacunas `L-XX`** (11 catalogadas) → manter.
- **Racional nas notas `>`** → promover a **ADR leve**, preservando o *porquê* sem inchar o documento.

> **Sobre o índice:** versões anteriores desta proposta previam um "índice vivo" como componente
> próprio. Ele foi **eliminado** — com a hierarquia de pastas no disco, o índice viraria uma terceira
> projeção do mesmo fato, e redundância é drift. A navegação passa a vir da própria estrutura; o
> estado de um trabalho, do backlog no arquivo do plano; e a visão agregada por core, de **consulta sob
> demanda** (script que varre e reporta), nunca de arquivo persistido que desatualiza.

---

## Formato do arquivo de unidade

### Regiões — quem escreve o quê

Esta é a regra que torna o estado projetável sem risco de perda:

| Região | Quem escreve | Conteúdo |
|---|---|---|
| **Frontmatter** | Script (bloco `# verificação`) e humano (demais) | `state`, `test`, `verified_at` são do script |
| **Corpo** | Humano / skill | Contrato, sequência, arquivos, normas, critério de aceite |

O script **nunca edita o corpo**. Escreve apenas três campos do frontmatter — região delimitada,
parseável e sem prosa. O mesmo princípio se aplica ao backlog no arquivo do plano, cujo formato é o
próximo item a definir.

> **No arquivo do plano, o campo projetado é `status`.** A tabela acima descreve a
> **unidade**; o plano é outro artefato, e nele `backlog.projetar` grava `status: done` na transição
> para `concluído` — mesmo instante e mesma guarda de `porte.registrar`. Sem isso o arquivo dizia
> `status: approved` para sempre, e saber se o trabalho fechou exigia abrir `_planos.md`: campo que
> ninguém projeta envelhece mentindo. **Só em médio e grande**, onde a
> situação é derivada; no pequeno o `status` é a **fonte** da situação, escrito pelo humano, e
> projetá-lo seria circular.

### Blocos do corpo

| Bloco | Função |
|---|---|
| Responsabilidade | Uma frase — o que faz e por que existe |
| Contrato | Entrada · Saída · Auth · Efeito · Erro |
| Sequência | Passos numerados, **teto de 8** |
| Arquivos | Caminhos concretos com `arquivo:linha` — exigência do cold-start |
| Dependências | O que precisa existir antes |
| Normas aplicáveis | Tabela de **referências**, nunca cópia |
| Critério de aceite | Uma frase verificável |
| Verificação | O comando que roda o teste declarado no frontmatter — e mais nada |
| Fonte | De onde veio a spec |

> **`Verificação` carregava também *"último resultado"*, e saiu.** Era
> linha órfã: nenhum script a projetava, a norma não a mencionava em seção nenhuma, e ela sempre
> mentia — as unidades em `verified` diziam *"não executado"* no corpo enquanto o frontmatter dizia
> o contrário. O dado já vive em `verified_at`; reescrevê-lo no corpo também violaria a regra de que
> script só escreve o bloco `# verificação` do frontmatter. `lint_unidade` recusa a
> linha para que não volte pela mesma porta.

#### Precedência entre os blocos

Os blocos podem divergir entre si — a derivação erra, e o código se move debaixo da unidade. Quando
divergirem:

> **O `Contrato` e o `Critério de aceite` mandam. `Sequência` e `Arquivos` são orientação.**

O contrato diz **o que a unidade tem de entregar**; a sequência diz **um caminho** para chegar lá, e
a tabela de arquivos diz **onde se esperava** encontrar as coisas. Um caminho incompleto não reduz a
entrega, e um `arquivo:linha` obsoleto não é permissão para deixar de fazer o que o critério exige.

Quem executa e encontra divergência: **entrega pelo contrato e registra a divergência no relatório** —
nunca escolhe em silêncio, e nunca reduz o escopo para caber na sequência. Corrigir a unidade é de
quem orquestra, e a divergência vira lacuna `L-XX` no plano.

> Origem: uma lacuna registrada e um gap de cobertura equivalente, no plano que motivou esta regra. Nos dois casos
> o executor resolveu certo, mas teve de
> **derivar** a precedência, porque ela não estava escrita. Em um deles a derivação saiu ao contrário
> — a tabela de arquivos prevaleceu sobre o critério — e a única regra nova da unidade ficou sem
> oráculo.

### Identificador

O `unit_id` combina o número do plano com o número da unidade dentro dele:

```yaml
unit_id: 0007-02        # plano 7, segunda unidade
```

A numeração das unidades é **por plano** — recomeça em `01` a cada plano novo. Quatro dígitos para o
plano, dois para a unidade.

### Tipo de unidade

Nem toda unidade entrega código. O campo `unit_type` define o que ela produz e qual é seu oráculo:

```yaml
unit_type: dev     # dev | plan | norma
```

| Tipo | Entrega | Oráculo de conclusão | `test:` |
|---|---|---|---|
| `dev` | Código | O teste declarado passa | obrigatório |
| `plan` | Um plano | O plano existe e consta em `_planos.md` | obrigatório |
| `norma` | Markdown normativo | `lint_unidade` limpo somado a `approved_by`/`approved_at` preenchidos | **vazio** |

Isso mantém **um único mecanismo**: todo plano gera unidades. Um plano de core, por exemplo, gera
unidades `plan` — cada uma produzindo o plano de um módulo. O oráculo continua verificável por
script, porque a linha aparece na tabela.

Sem isso, planos de nível alto exigiriam uma segunda mecânica de plano; com isso, a diferença fica
contida num campo.

#### `norma` — quando a unidade entrega prosa, não código

Todo plano que muda norma produz unidades cujo entregável é markdown normativo, e o gate de saída
original só sabia fechar por teste passando. Markdown não tem teste que prove que a prosa presta —
forçar um seria fingir um oráculo que não existe.

`norma` inverte a exigência de `test:` — passa a ser obrigatório **vazio**, no mesmo padrão de
vocabulário fechado que já vale para o próprio `unit_type` — e ganha dois campos novos no
frontmatter, ao lado de `unit_type`: `approved_by` e `approved_at`. Mesmo par, mesmo papel dos
campos homônimos do plano (*Aprovação — três campos declarados pelo humano*, mais abaixo): o humano
declara, o script só confere que a declaração existe.

`verificacao.verificar` fecha uma unidade `norma` quando `lint_unidade` está limpo — o que já exige
`approved_by`/`approved_at` preenchidos — **sem rodar nenhum `subprocess`**, e grava `verified_at`
igual a `approved_at`, nunca a data em que o script rodou: o fato verificado é a aprovação do
humano, e reexecutar o gate amanhã não pode mover a data de um fato que não mudou.

**O que continua em aberto.** O script segue sem julgar se a prosa presta — só confere que a
aprovação existe e está registrada em campo. Adequação de conteúdo continua sendo julgamento
humano, e nenhum campo transforma isso em oráculo.

É o `unit_id` que o comentário-cabeçalho cita no código, **não o nome do arquivo**: renomear o slug
de uma unidade não quebra referência alguma, porque nenhuma referência aponta para o filename.

### Ciclo quando o teste ainda não existe

O caso comum em trabalho novo, e o que o modelo precisa cobrir explicitamente:

1. A unidade declara `test:` com o caminho do teste **alvo**, mesmo antes de ele existir
2. `state: spec` enquanto o teste não existir ou não passar
3. O modo `implement` escreve **teste e código** — o teste é entregável da unidade, não pré-requisito
4. O gate de saída só promove a `verified` quando o arquivo existe **e** a execução passa

O gate de entrada exige o teste **declarado**, não o teste **existente**. A distinção é o que permite
começar uma unidade nova sem quebrar o ciclo.

---

## Formato do plano

### Alvo — declarado no frontmatter

O plano declara onde suas unidades vão viver, com os mesmos campos da unidade:

```yaml
core: <core>
module: <module>
block: ""        # vazio quando o plano não cria bloco
```

O modo `derive` lê esses campos para criar a estrutura e mover o arquivo do `_inbox`. Declarar no
documento, e não na invocação, mantém a decisão registrada onde ela pertence.

**Um plano, um alvo.** Trabalho que cruza módulos é dividido em planos distintos — o modo `review`
sinaliza e recomenda a divisão. Não é restrição arbitrária: deriva do princípio de lote pequeno e
resolve a ambiguidade de para onde mover o arquivo na aprovação.

> O alvo define onde o plano e suas unidades **vivem**, não a fronteira do que o código **toca**. Uma
> unidade pode tocar arquivos de qualquer lugar — é o campo *Arquivos* que declara isso.

### Aprovação — três campos declarados pelo humano

A etapa de aprovação (*Fluxo completo*, etapa 3) deixa um artefato: o plano declara, no
frontmatter, os três campos que só o humano pode preencher. `scaffold.aprovar` recusa a ausência de
qualquer um — antes de mover o plano, antes de escrever qualquer coisa, inclusive em `dry_run`.

| Campo | Valor | O que o gate faz |
|---|---|---|
| `plan_size` | `pequeno` \| `médio` \| `grande` | Recusa ausente **e** recusa valor fora do vocabulário |
| `approved_by` | nome de quem aprovou | Recusa ausente |
| `approved_at` | `YYYY-MM-DD` | Recusa ausente, e recusa o que não for data ISO |

Recusar `plan_size` fora do vocabulário não é julgar o porte: o gate segue sem opinar se `grande`
era a escolha certa para este plano — isso é julgamento humano. O que ele recusa é o valor que não é
escolha nenhuma, no mesmo padrão de vocabulário fechado que `unit_type` já usa.

A coluna *Aprovado* de `_planos.md` recebe o `approved_at` declarado — nunca a data em que o script
rodou.

### Backlog — região delimitada por marcadores

O script projeta o backlog entre marcadores de comentário, invisíveis no markdown renderizado:

```markdown
<!-- backlog:start -->
| Unidade | Título | Estado |
|---|---|---|
| [0007-01](01-handler-auth.md) | Handler MCP com autenticação obrigatória | `verified` |
| [0007-02](02-search-catalog.md) | Tool search_catalog | `spec` |

1 de 9 verificadas · atualizado em 2026-07-19
<!-- backlog:end -->
```

O script substitui **exatamente** o conteúdo entre os marcadores; o resto do plano é intocável. É o
mesmo princípio do frontmatter na unidade — região delimitada, sem prosa —, aplicado ao corpo.
Parsear headings seria frágil: qualquer texto adicionado na seção se perderia na próxima projeção.

**Por que o backlog não é o índice eliminado.** O índice agregava por core, informação que a
estrutura de pastas já dá. O backlog agrega **por plano** — recorte temporal que a estrutura não
expressa, já que unidades de vários planos convivem na mesma pasta do módulo.

### `_handoff.md` — o prompt que conduz a execução

O `derive` grava, no diretório do plano, o prompt que orquestra a execução do que ele acabou de
derivar — a ser colado numa **sessão nova**, cujo papel é conduzir, nunca implementar unidade.
**Só no grande:** médio e pequeno executam na mesma sessão em que foram aprovados,
e não há ponte entre sessões a construir.

| Quem escreve | O quê |
|---|---|
| Script (`handoff.gerar`) | O esqueleto, e o que se mede sem opinar — commit, derivadas, verificadas, próximo número livre |
| Opus, na derivação | A fila com as dependências, as pendências do humano, e por onde começar |

**É projeção, e é regerada a cada `derive` incremental** — edição à mão se perde na próxima
execução, como no backlog. O prefixo `_` a mantém fora de `PADRAO_ARQUIVO_UNIDADE`, que é o que
conta unidades.

> **A suíte não entra contada, e é deliberado.** O prompt carrega o **comando** e a regra de somar
> as duas linhas `Ran`; quem lê mede. Número declarado envelhece no primeiro commit, e o prompt
> inteiro existe para dizer que declaração é alegação — congelar o próprio número seria contradizê-lo
> na primeira linha. A disciplina completa está em *Como revisar uma entrega*, **citada** pelo
> prompt e nunca copiada nele.

### Bloco obrigatório — Independência

Todo plano declara, no corpo, por que é **um** plano e não dois. Uma seção `## Independência` responde
ao teste: entregando apenas este plano e parando, o sistema fica em estado válido — e não há parte
separável que entregue valor sozinha.

A declaração é feita **no momento da escrita**, não descoberta na revisão: é quando ainda é barato
mudar de ideia. A revisão apenas audita se ela se sustenta (ver *Avaliação de escopo*).

### O que cada porte carrega

`plan_size` (ver *Aprovação*, acima) não é só rótulo — o formato exigido varia por porte, para que
correção de oito linhas não pague a estrutura de um plano de vinte unidades (`B-01`):

| Porte | Decomposição | `## Independência` | Região de backlog |
|---|---|---|---|
| `pequeno` | nenhuma | **recusada** | **recusada** |
| `médio` | `## Tarefas` — lista de caixas | dispensada | exigida |
| `grande` | `## Escopo` — tabela numerada | exigida | exigida |

**No `pequeno` os dois blocos marcados são recusados, não apenas dispensados.** Região de backlog
é promessa de projeção: se nenhum script escreve ali, ela mente para sempre. E `## Independência`
num plano sem decomposição responde a uma pergunta que ninguém fez.

`lint_plano.lint` verifica exatamente esta tabela — leitura, nunca escrita. `plan_size` ausente,
vazio ou fora do vocabulário entra na lista de problemas devolvida, e `lint_plano` **nunca
levanta**: quem recusa a aprovação por causa de `plan_size` é `scaffold.aprovar` (*Aprovação*,
acima), que é o gate. `lint_plano` também roda sobre plano ainda no `_inbox`, antes de existir
aprovação nenhuma para recusar.

---

## Porte medido — dado, não impressão

`plan_size` (acima) é o que o humano **declara** na aprovação. `docs/plan/system/porte-medido.md`
guarda o que o plano **foi** — uma linha por plano fechado, acrescentada por `porte.registrar` na
transição da situação para `concluído`, nunca reescrita.

| Coluna | O que significa |
|---|---|
| Plano | Link para o arquivo do plano |
| Porte declarado | `plan_size` no momento do fechamento |
| Unidades ou tarefas | Quantas unidades (grande) ou tarefas (médio) o plano fechou com — `—` no pequeno, que não decompõe |
| Arquivos declarados | Caminhos distintos das tabelas `## Arquivos` das unidades — `não declarado` fora do grande, onde não existem unidades |
| Linhas alteradas | `git diff --numstat` do commit que criou o plano até o fechamento, restrito aos arquivos declarados — `não medido` com o motivo quando git não responde, `—` fora do grande |
| Fechado em | Data da transição para `concluído` |

> **"Até o fechamento" é `HEAD` no instante em que `registrar` roda**, não o commit da última
> unidade. O intervalo inclui o que for commitado entre fechar a última unidade e projetar a
> situação — inclusive a revisão do próprio fechamento. O número não é errado; ele **é** do
> instante em que foi tirado, e é por isso que a tabela é append-only e nunca recalcula uma linha
> já gravada.

**Para que serve:** é o dado que falta para saber se o que hoje se chama `médio` custa, na
prática, o que se chamava `grande` — sem essa tabela a calibração do vocabulário de porte
continuaria por impressão, não por evidência (princípio, *Evidência acima de opinião*).

---

## Avaliação de escopo — quando dividir um plano

O check mais importante do modo `review`, e o único com evidência concreta de necessidade dentro do
próprio repositório.

### O caso que originou a regra

Um esforço de separar um componente em dois foi executado junto com a troca do mecanismo de conexão
entre eles. Resultado: funcionalidades com erros e conflitos, e documentação que não se sustentou —
volume total registrado de 1.826 linhas em cinco documentos, entre plano, escopo e runbook.

Não foi um plano grande demais: foram **dois planos acoplados**, um alterando decisões do outro
enquanto ambos corriam.

### O teste — independência

> Entregando **apenas a parte A** e parando aqui, o sistema fica em estado válido e útil?
> Se a resposta for sim para A **e** para B, são dois planos.

Aplicado ao caso: o split entrega valor sozinho — dois plugins funcionando com REST. A troca para MCP
entrega valor sozinha — conexão MCP no plugin monolítico. Ambos passam isolados; eram dois planos.

### A checagem — concorrência

Determinística, via `_planos.md`: **existe plano `em desenvolvimento` no mesmo core ou módulo?**

Se existe, ou o novo plano espera, ou se declara dependente — e dependência declarada entre planos em
andamento é exatamente o padrão que falhou. Esta checagem sozinha teria sinalizado o caso.

### Quando **não** dividir

Dividir tem custo. Se A depende de B, separá-los cria dependência **entre planos** — o problema
original invertido, e pior, porque a coordenação passa a ser entre documentos numerados independentes.

| Situação | Divisão correta |
|---|---|
| As partes passam no teste de independência | **Planos separados** |
| Dependência sequencial, objetivo único | **Fases** no mesmo plano |
| Agrupamento de capability sob o mesmo módulo | **Blocos** |
| Alvo é domínio novo, não variação | **Módulo novo** |

### O que a avaliação não faz

- **Não impõe teto de unidades.** Tamanho é reportado como contexto — unidades previstas, módulos e
  cores tocados — nunca como critério de reprovação. Um número sem base empírica competiria com o
  teste de independência e dividiria planos coesos.
- **Não bloqueia a aprovação.** Quem aprova é o humano; um check que recusa vira obstáculo a
  contornar. Quando a avaliação sinaliza divisão e a decisão é não dividir, **o plano registra o
  porquê** — mesmo princípio das lacunas `L-XX`. O custo de justificar por escrito já filtra o
  "aproveitando o escopo", que foi exatamente como o caso real começou.
- **Não depende de detectar frases.** Expressões como *"dentro de"*, ou seções de impacto em outro
  plano, são evidência histórica útil — mas morrem como detector: quem conhece a regra deixa de
  escrevê-las, e o acoplamento segue invisível.

---

## Nomenclatura

Mesmo desenho da regra de skills do `build-resource` (linha 80): **sugestão semântica** pela skill,
**validação sintática** pelo script.

### Plano

No `_inbox`, apenas o nome semântico:

```
<intenção>-<alvo>[-<qualificador>]
```

| Parte | O que é | Exemplos |
|---|---|---|
| **Intenção** | substantivo de ação ou tema | `evolve`, `simplify`, `split`, `required-login` |
| **Alvo** | o que é afetado — **sem repetir o caminho** | `dev-units-model`, `new-project-command` |
| **Qualificador** | opcional: fase, camada, variante | `l3`, `impl` |

Restrições: kebab-case, **inglês**, 2–5 tokens, ≤ 64 caracteres, sem conectivos.

> **Por que inglês, se a documentação é pt-BR.** O nome do plano vira o `module` do frontmatter e o
> nome da pasta no disco — e o `.claude/CLAUDE.md` § *Idioma e Nomenclatura* classifica módulo como
> **identificador**, exigindo inglês. As duas normas se contradiziam até essa regra ser revisada.
> A prosa do plano continua inteiramente em pt-BR: o inglês vale para o **nome**, não para o conteúdo.

**Na aprovação, recebe o número** — 4 dígitos, sequencial global, atribuído uma única vez:

```
_inbox/evolve-tools.md   →   <core>/0007-evolve-tools/0007-evolve-tools.md
```

A pasta criada tem **exatamente o mesmo nome** do arquivo. Quando o plano cria um módulo, seu nome
costuma ser o próprio módulo: `_inbox/mcp.md` → `<core>/0007-mcp/0007-mcp.md`.

> **"Sem repetir o caminho"** é regra nova, e só faz sentido quando o caminho já carrega contexto: num
> diretório plano, onde tudo era plano solto, o nome precisava carregar o contexto inteiro. Em
> `docs/plan/<core>/<module>/`, o contexto está no caminho — um plano em `<core>/mcp/` não se chama
> `evolve-tools-mcp-do-core`, e sim `evolve-tools`.

**O plano mantém o nome ao sair do `_inbox`** — nunca vira `plano.md`. Um módulo recebe vários planos
ao longo do tempo, e nome fixo colidiria. Além disso, descartar o nome na aprovação tornaria a regra
inútil justamente onde o documento se torna permanente.

### Unidade

Arquivo: `[nn]-[nome].md` — dois dígitos sequenciais **dentro do plano**, mais o slug semântico.

```
01-handler-auth.md
02-search-catalog.md
```

Três identificadores, com papéis distintos:

| | Forma | Onde aparece | Muda? |
|---|---|---|---|
| **`unit_id`** | `0007-02` | frontmatter, comentário-cabeçalho no código, testes, backlog | **Nunca** |
| **Arquivo** | `02-search-catalog.md` | disco | Ao renomear o slug |
| **Slug** | `search-catalog` | `name:` e no nome do arquivo | Pode |

A separação resolve a tensão entre legibilidade e estabilidade: o arquivo é autoexplicativo ao listar
a pasta, e o `unit_id` — que é o que o código cita — não depende dele. Renomear o slug não quebra
referência alguma.

Slug: mesmas restrições sintáticas do plano, sem repetir o módulo (já está no caminho).

### Tabela de planos

`docs/plan/_planos.md` — registro dos planos **aprovados**, e fonte da numeração:

````markdown
<!-- planos:start -->
| # | Plano | Core | Módulo | Situação | Aprovado |
|---|---|---|---|---|---|
| 0007 | [mcp](<core>/0007-mcp/0007-mcp.md) | `<core>` | mcp | em desenvolvimento | 2026-07-20 |
<!-- planos:end -->
````

- **Só entra plano aprovado.** O que está no `_inbox` não aparece — a tabela registra o que entrou em
  desenvolvimento.
- **O número é atribuído aqui:** o script lê o maior em uso e toma o próximo.
- **A situação é projetada, não digitada** — derivada do estado das unidades: `em desenvolvimento`
  enquanto houver unidade fora de `verified`, `concluído` quando todas estiverem.
- Vive em `docs/plan/`, não em `.claude/skills/decode-and-code/`: é dado do projeto, versionado junto dos
  planos, e sobrevive a qualquer troca da skill.

### Divisão de responsabilidade

| Camada | Onde | O quê |
|---|---|---|
| Sugestão | **Skill** | 3 opções a partir de `core` + `module` + intenção declarada; aceita "outro" |
| Validação sintática | **Script** | Minúsculas e hífens, sem hífen inicial/final/consecutivo, ≤ 64, sem conectivo, sem prefixo numérico |
| Colisão | **Script** | Nome já existente no alvo; próximo ID livre no módulo |

A checagem de colisão não existe na regra de skills e é necessária aqui: o ID sequencial precisa
saber qual é o próximo livre no módulo.

---

## Camada de execução

Operado por **uma skill única**, que delega todo determinismo a scripts.

### Skill `dev-units` — substitui `plan-dev-units`

O plano é insumo, não produto da skill: você o escreve com Opus, a skill revisa e deriva.

| Modo | O que faz |
|---|---|
| `review <plano>` | Os seis checks abaixo |
| `derive <plano>` | Cria a estrutura, move o plano do `_inbox`, gera as unidades, projeta o backlog |
| `implement <unidade>` | Executa em cold-start |

Adicionar um bloco **não é modo próprio** — é um plano cujo alvo é módulo existente, e passa pelo
mesmo `review` → `derive`.

### Modo `review` — os seis checks

Nem todos têm a mesma natureza; separar evita pedir julgamento onde cabe script:

| Check | Natureza | Como |
|---|---|---|
| **O plano precisa ser dividido?** | **Misto** | Script checa concorrência em `_planos.md` e reporta tamanho; julgamento audita a declaração de independência (ver *Avaliação de escopo*) |
| Usou a documentação oficial adequada ao escopo? | **Misto** | Script confere se as fontes citadas existem; julgamento avalia se são as certas |
| Há erros de arquitetura? | **Misto**, quando há grafo | Script conta referências contra a seta do grafo de cores (ver *Guardrail fundador*); sem grafo declarado, o check é julgamento inteiro |
| Há erros conceituais? | Julgamento | — |
| Há lacunas em aberto? | Julgamento | Registrar como `L-XX` |
| É compatível com os padrões do projeto? | **Misto** | Guardrails do `CLAUDE.md` são verificáveis; o resto é julgamento |

Quatro dos seis têm parte automatizável. Sem extraí-la, a revisão vira leitura subjetiva — e leitura
subjetiva é onde a variância volta.

### Os dois gates

São a razão de existir da skill:

- **Entrada (`implement`):** unidade sem critério de aceite, sem teste declarado ou sem os campos de
  cold-start → recusa e devolve ao `derive`. Impede começar sem oráculo.
- **Saída:** teste não passa → a unidade não transiciona para `verified`. Impede a doc de mentir.

### Como revisar uma entrega

Os dois gates provam a **unidade**. Não provam que a entrega está certa: gate verde é condição
necessária, e a revisão é onde se descobre o que ele não alcança.

**A base desta seção é estreita, e vale dizer:** ela sai de uma sessão só, em 2026-08-27, sobre
sete unidades entregues em sequência — **sete revisões com achado** —, e o que os produziu não
foi zelo, foi medir em vez de reler.

| Regra | Por quê |
|---|---|
| **Rode a suíte inteira você mesmo, e some as duas linhas `Ran`** | O relatório dá a contagem do diretório da skill como se fosse o total. Escorregou em **treze de treze** entregas |
| **Rode os lints contra os artefatos reais**, nunca só contra fixture | `lint_unidade` em cada unidade, `lint_plano` no plano, `lint_agente` em cada agente, o lint do artefato que a unidade entregou |
| **Pegue uma afirmação do relatório e meça-a por outro caminho** | *"Nenhum chamador muda de saída"* caiu comparando saídas contra o commit anterior; *"nenhum teste executa git"* caiu com um shim no `PATH`; *"os quatro casos falham no texto antigo"* confirmou-se aplicando as asserções ao texto de `HEAD` |
| **Verde não é evidência** quando o teste e o critério saíram da mesma cabeça no mesmo momento | Se um teste existe para gatear uma decisão, **desligue o código e rode o teste**: ele tem de falhar. Duas vezes o caso continuava verde sem o que devia provar |
| **Mock prova o parsing da saída, nunca o comando montado** | Ver *Comando externo* em `.claude/rules/scripts.md`, e o caso que a originou |
| **Caracterize o comportamento externo antes de escrever a correção** | Teste escrito a partir da mesma leitura que produziu o defeito passa contra o defeito |
| **Separe o sintoma da raiz** | Em duas ocasiões a raiz estava num fixture, não no código sob revisão — e corrigir a raiz desfez a acomodação construída em volta |

> **Todo número que o relatório afirma é alegação até você medir**, e a medição vale com o oráculo
> do projeto, nunca com um equivalente montado na hora — é o que custou três vezes no
> mesmo dia. Se existe script que o gate usa, é ele que dá o número.

**Quem revisa não conserta o executor.** Entrega fiel a uma unidade defeituosa é defeito **da
unidade**: a correção volta para quem deriva, e vira lacuna `L-XX` no plano.

### Fronteira skill / script

| Responsabilidade | Onde vive |
|---|---|
| Detectar modo, validar gates, medir lote, rodar teste, projetar estado, **validar nome e colisão** | **Script** — Python, em `.claude/skills/decode-and-code/scripts/` |
| Pesquisar, sintetizar, revisar com julgamento, decidir a fatia, escrever código, **sugerir nomes** | **Skill** |

Os scripts seguem a [norma de linguagem](language-policy.md): Python 3.10 (versão do Cowork), stdlib
pura, verificados com `unittest` via `scripts/test-python.sh`.

Skill interpretando "verifique se está pronto" devolve a variância ao sistema. O que estabiliza é o
oráculo determinístico, e oráculo é código — conforme *Código vs. Instruções em Markdown* no
`CLAUDE.md`.

### Modelos

**Sonnet é o padrão no `implement`**, com override do usuário conforme o escopo do trabalho. O
`review` e o `derive` pedem julgamento denso — Opus.

**A troca não é declarável na skill.** Verificado em 2026-07-19: das skills do projeto que declaram
`model:` no frontmatter, **todas o deixam vazio**; apenas os agents o usam preenchido
(`model: opus`). A skill roda no contexto de quem a invoca e herda o modelo da sessão.

Consequência: a política é **operacional** — o modelo é escolhido antes de invocar. Se a troca
automática por modo for requisito, e não conveniência, isso reabre a decisão sobre agents.

**O gate abriu — as duas condições foram cumpridas.** A skill existe desde **2026-07-26**, e o
requisito de troca automática por modo — não mais conveniência — foi declarado pelo humano em
**2026-08-22**, a partir de uso diário. Agent deixa de estar fora de escopo. O que ele é aqui:
**papel e processo, nunca a norma** — o agente **declara** a skill em `skills:`, que é a ponte
prevista para a norma chegar sem ser reescrita dentro do próprio prompt; quem decide `model:` e
`tools:` é quem o instancia, na `19` e na `20`.

> **A ponte é declarada, e o carregamento nunca foi medido.** Medido em 2026-08-26 nos 34 agentes
> instalados nesta máquina: **nenhum** declara `skills:` — o campo só aparece num template. O que um
> lint alcança é que a skill nomeada **existe em disco**; que ela entre em contexto é comportamento
> de sessão, e ninguém o observou. Afirmar o contrário repetiria o caso invertido, em que quatro skills
> declaradas num campo ignorado nunca carregaram e ninguém percebeu.

### Agente — o que o lint exige

`lint_agente.lint(caminho)` dá a esta camada o mesmo oráculo estrutural que `lint_unidade`,
`lint_plano` e `lint_skill` já dão às suas: verifica o artefato, nunca a qualidade do julgamento
que ele carrega. Quatro invariantes, todos sobre o frontmatter:

| Invariante | Exige |
|---|---|
| Campos nativos | Só `name`, `description`, `tools`, `model`, `skills`, `color` — nenhum bookkeeping de projeto (`type`, `project`, `author`...) entra no frontmatter de agente |
| `model` | Presente, e dentro de `sonnet`, `opus`, `haiku`, `inherit`. **Três foram medidos em uso** nos 34 agentes instalados em 2026-08-26 — `inherit` em 14, `sonnet` em 8, `opus` em 4; `haiku` está na lista por completar a família de modelos, **não por medição**: nenhum agente do acervo o declara |
| `skills` | Cada nome citado existe como diretório em `.claude/skills/` — não que ele carregue (parágrafo acima) |
| `tools` | Presente e não vazio — ausente concede o conjunto inteiro por default, o oposto de escopo declarado |

**`tools:` não tem granularidade de caminho**, e o lint não finge o contrário: é lista de nomes de
ferramenta, sem qualquer expressão de path. Escopo de escrita (`docs/plan/**`, no planejador) é
declaração no corpo do agente — verificada por teste, nunca imposta pelo frontmatter. Impor de
verdade é guardrail do projeto que instala, não deste mecanismo.

Referência viva: `.claude/agents/planner.md` — a instância que este lint aprova.

---

## Huddle — fila do que ainda não foi decidido

Fila do que ainda **não** foi decidido — o que as três camadas normativas não guardam, porque
resolvem só o que já foi decidido. Um arquivo por projeto, em `<plan_root>/system/huddle.md`, e
nunca carregado automaticamente: nem como rule, nem por `skills:`, nem por import — entra
em contexto quando a conversa acontece, do contrário compete com norma já decidida.

**A propriedade que faz funcionar: nada ali é autoritativo enquanto está ali.** Uma entrada nasce
aberta, é discutida com o humano, e quando resolve **sai** — para a norma, para uma guideline, ou
para o `## Decisões` de um plano — deixando uma linha em `## Fechadas` com data e destino. Não
resolvida, é descartada com o motivo escrito. Um arquivo onde nada fecha só cresce; o tamanho certo
é o do que está genuinamente em aberto.

### Formato e vocabulário fechado

Duas seções, `## Abertas` e `## Fechadas`. Entrada aberta abre com um cabeçalho de linha única:

```
### H-XX · `tipo` · AAAA-MM-DD · autor
```

`tipo` vem de vocabulário fechado de cinco — mesmo padrão de `unit_type` e `plan_size`: recusa-se o
valor que não é escolha nenhuma, nunca a escolha.

| Tipo | O que é |
|---|---|
| `pergunta` | Decidi X assumindo Y — Y está certo? |
| `divergência` | Duas fontes do projeto se contradizem, e a execução contornou |
| `padrão` | Regularidade que uma sessão sozinha não revela |
| `revisitar` | Alternativa rejeitada cuja premissa pode ter mudado |
| `observação` | Algo notado que ainda não virou afirmação |

Entrada fechada vira uma linha em `## Fechadas`, colunas `# | Tipo | Fechada em | Destino`.

### Despejo — o invariante verificável

**O mesmo `H-XX` não pode estar em `## Abertas` e na tabela de `## Fechadas` ao mesmo tempo** — é a
promessa central do arquivo, e sem verificação um huddle onde nada fecha só cresce sem que ninguém
note. `huddle.lint_arquivo(caminho)` prova isso, lista vazia quando sã: cabeçalho de entrada bem
formado — tipo dentro do vocabulário fechado —, `H-XX` único dentro de `## Abertas`, e nenhum `H-XX`
presente nas duas seções.

**Os cinco gatilhos de escrita não têm o mesmo oráculo**: *o executor decidiu algo que o
humano não decidiu*, *duas fontes discordam*, *algo foi contornado em vez de corrigido*, *uma
alternativa foi rejeitada por premissa que pode mudar*, *o humano corrigiu o modelo* — nenhum é
observável por script, só por quem escreve. O lint alcança a estrutura de quem já escreveu; nunca
se deveria ter escrito.

### Momento — no fecho, e a linha de fecho é obrigatória mesmo em zero

Não no instante em que a observação acontece: metade se resolve dentro da própria sessão, e entrada
escrita na hora seria natimorta. No fecho do relatório de **qualquer um dos três modos** —
`review`, `derive` e `implement`, não só o último —, uma linha declara quantas entradas novas
houve:

```
entradas novas no huddle: N
```

**Inclusive com `N` igual a zero.** `huddle.lint_relatorio(texto)` recusa a ausência da linha —
lista vazia quando presente, com qualquer `N` —, porque é o que separa *conferi e não havia* de
*nunca conferi*, hoje indistinguíveis. **A mitigação é fraca, e vale dizer o quanto:** um relatório
honesto com zero e um desatento com zero continuam idênticos ao lint; o que ele alcança é a
ausência da declaração, nunca a atenção de quem a escreveu.

### Sem arquivo de template, e o que não viaja

**O esqueleto vive em `huddle.iniciar(destino)`, nunca num `.md` para copiar** — mesmo
padrão de `porte._CONTEUDO_INICIAL`: formato com uma fonte só, que é o script, com esta seção
descrevendo-o em prosa. Escreve `destino` com o frontmatter e as duas seções vazias e devolve o
caminho escrito; sobre um `destino` que já existe, devolve `None` sem tocar em nada.

> **O `huddle.md` de cada projeto é instância pura, e não viaja no plugin — o mecanismo que cria um
> vazio, sim**. Entrada aberta é a conversa entre o humano e o modelo **daquele** projeto;
> empacotá-la entregaria a quem instala o registro de decisões de outro repositório — o invariante 2
> quebrado no artefato mais pessoal do método. Quem instala roda `iniciar` e recebe o seu, vazio.

---

## Bootstrap — o chão que o ciclo pressupõe

Todo o *Fluxo completo* abaixo assume uma estrutura já existente. Num projeto que acabou de instalar
o método ela não existe, e a primeira etapa morre: medido em **2026-08-27**, `scaffold.aprovar`
sobre o primeiro plano de um projeto zerado levanta `FileNotFoundError` em `_planos.md`. O bootstrap
é a etapa **zero** — `bootstrap.iniciar(projeto)`, que cria esse chão uma vez.

> **Passou despercebido porque ninguém tinha rodado o ciclo do zero.** Nas validações anteriores o
> `_planos.md` era montado à mão no repositório de teste, e isso foi tratado como preparação. Era o
> defeito, contornado sem ser visto.

### O que cria

| Caminho | Por quê |
|---|---|
| `<plan_root>/_planos.md` | Fonte da numeração — com frontmatter, os marcadores `planos` e o cabeçalho da tabela |
| `<plan_root>/_inbox/` | Onde todo plano nasce |
| `<plan_root>/system/` | Onde vive a camada normativa do core |
| `<projeto>/.claude/` | `root_markers` exige `.claude/` **e** `docs/` — sem os dois a âncora não resolveria o projeto **depois** do bootstrap |

**Idempotente e nunca destrutiva**, no mesmo contrato de `huddle.iniciar` e do bootstrap de
`porte.registrar`: cada caminho só é criado se ainda não existir, e o pulo é **por item, nunca
tudo-ou-nada**. Um projeto que já tem `_planos.md` com linhas mantém as linhas, mesmo que `_inbox/`
ainda falte. `iniciar` devolve a lista do que criou — segunda chamada devolve lista vazia.

`project:` no frontmatter de `_planos.md` vem do **nome do diretório do projeto**, nunca fixo.
Embutir o nome do repositório de origem vazaria para quem instala.
Sem arquivo de template: o esqueleto vive em `_CONTEUDO_INICIAL`, como `porte.py` e
`huddle.py` já fazem.

### O que não cria

Runner de teste e `_inbox/_backlog.md` ficam de fora. São **instância do projeto que
instala**, não estrutura do método — o projeto declara o seu runner em `runners`, no `config.json`.
Criar um na casa de quem instala seria feature além do pedido, e é o invariante 2 aplicado à
operação que mais tenta violá-lo: a que escreve num projeto alheio.

### Por que o projeto chega por parâmetro

`iniciar` recebe `projeto`; não o resolve. **Resolver a raiz aqui seria circular** — antes do
bootstrap o projeto não tem as marcas que `lib.repo_root()` procura, e são exatamente as marcas que
esta operação vai criar. Toda outra operação do método pode se ancorar porque roda depois; esta é a
que roda antes.

O `plan_root` continua vindo do `config()`, componível com a entrada — `projeto /
lib.config()["plan_root"]` —, então o bootstrap honra a configuração sem precisar da âncora.

---

## Fluxo completo

| # | Etapa | Executor | Resultado |
|---|---|---|---|
| 1 | Plano nasce | Opus | `docs/plan/_inbox/nome.md` |
| 2 | Revisão | skill + script | Cinco checks |
| 3 | **Aprovação** | **humano** | `plan_size`/`approved_by`/`approved_at` declarados no plano |
| 4 | Número atribuído | script | Próximo livre em `_planos.md` — 4 dígitos |
| 5 | Estrutura criada | script | `docs/plan/<core>/<NNNN>-<nome>/` |
| 5b | Plano movido e prefixado | script | `_inbox/<nome>.md` → `<NNNN>-<nome>/<NNNN>-<nome>.md` |
| 6 | Unidades derivadas | Opus | Um arquivo por unidade, densas para cold-start |
| 7 | Backlog projetado | script | No arquivo do plano |
| 7b | Handoff gravado | script + Opus | `_handoff.md` no diretório do plano — **só no grande** |
| 8 | Implementação | Sonnet (default) | Uma unidade por vez, em cold-start |
| 9 | Fechamento | script | Estado projetado na unidade e no backlog |

> **A etapa 4 é reentrante.** `scaffold.aprovar` sobre um plano já aprovado devolve o caminho sem
> escrever nada — derivar em lotes reinvoca a etapa sobre o mesmo plano, e isso é o caminho previsto,
> não uma exceção a tratar.

> **As etapas 5 a 9 ramificam por porte.** No **pequeno**, `derive` **não roda**:
> `aprovar` move direto para `<core>/<NNNN>-<nome>.md`, sem subpasta (sem etapa 5) e sem unidade
> nenhuma para decidir, numerar ou derivar (sem etapa 6). A etapa 7 ainda roda, mas não escreve
> região de backlog — não existe o que projetar; a situação vem de `status`, e a etapa 9 fecha
> quando o **humano** grava `status: done`, nunca um script. No **médio**, `aprovar` também move
> sem subpasta, mas a etapa 7 projeta as caixas de `## Tarefas` em vez de unidades — a etapa 6
> continua sem rodar, porque médio não deriva unidade. No **grande**, as nove etapas seguem
> exatamente como na tabela. O formato completo de cada porte está em *O que cada porte carrega*,
> acima — não duplicado aqui.

---

