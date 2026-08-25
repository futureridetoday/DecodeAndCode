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

---

## Fundamentação — por que este modelo, e não outro

Ancorado em evidência empírica, não em tendência de mercado.

| Fonte | Dado | Implicação |
|---|---|---|
| **METR 2025** (RCT, 16 devs experientes, 246 tarefas) | Devs foram **19% mais lentos** com IA, mas estimaram ter sido **20% mais rápidos** | Percepção de progresso não é confiável. É preciso um **oráculo objetivo** |
| **DORA 2024** (~39 mil profissionais) | Adoção de IA acompanhada de **−1,5% throughput** e **−7,2% estabilidade**; causa apontada: o campo **esqueceu o small batch** | O gargalo é o **tamanho do lote**, não a ferramenta |
| **DORA 2025** (~5 mil profissionais) | "IA **amplifica** o que já existe"; **small batch amplifica os efeitos positivos** | Estrutura decide se a IA é ativo ou passivo |

**O que deliberadamente não foi adotado.** Spec-Driven Development (GitHub Spec Kit, AWS Kiro, Tessl)
é a corrente dominante, mas **nenhuma dessas ferramentas tem validação empírica**. A avaliação do
Spec Kit identificou incompatibilidade estrutural com este modelo: é **spec-first** (spec descartada
após uso) enquanto o modelo precisa de **spec-anchored**; tem baixo benefício relatado em sistemas
multi-módulo e brownfield; e produz **volume documental**, que é o modo de falha já vivido aqui.

Conclusão: adotar o **princípio** (spec-anchored, lote pequeno, verificação objetiva), não a
ferramenta.

---

## Diagnóstico medido — o padrão atual

Auditoria dos 18 arquivos `dev-units*.md` em `docs/mvp/20_delivery/`. **Este acervo não será migrado
agora** (ver *Estratégia de adoção*) — o diagnóstico justifica o desenho, não dimensiona retrabalho
imediato.

### O que funciona (preservar)

| Capacidade | Evidência |
|---|---|
| Fatia vertical como unidade | 86 unidades com contrato Entrada/Saída/Auth/Efeito/Erro |
| Rastreabilidade doc ↔ código | **90 referências** via comentário-cabeçalho (`proxy.ts:5` → `// AU-06`) |
| Registro de pendências | **11 lacunas** `L-XX` catalogadas |
| Preservação do racional | Notas `>` com trade-offs (ex.: invalidação antecipada em `AU-02`) |

### O que falta

| Lacuna | Medição |
|---|---|
| **Não define "pronto"** | **0 de 18** contêm critério de aceite |
| **Não liga à verificação** | **0 de 18** declaram teste — apesar de existirem **18 arquivos de teste** |
| **Não tem estado** | **18 de 18** em `status: draft`, com código em produção |
| **Não norma o lote** | De **1 a 18** unidades por arquivo; **22 de 86 (26%)** sem sequência numerada |
| **Não serve a cold-start** | Nenhuma declara arquivos a tocar nem normas aplicáveis |

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
quando eu toco Y* — é norma, e entra sozinha pelo caminho do arquivo. O caso medido:
`AmFlow:hub-front` (547 linhas, §1–7 e §9 normativas, §8 procedimento) descreve-se como checklist de
front-end, mas só entra em contexto se alguém a invocar — como guideline com
`paths: ["hub/app/**"]`, ativaria sempre que um arquivo daquele escopo fosse tocado, sem depender de
lembrança.

#### Validar a ativação

Dois atos permanecem humanos, e nenhum script os substitui: **abrir uma sessão nova**, e **tocar um
arquivo do escopo** de uma guideline. O que deixa de ser julgamento é o que se conclui depois de
feito isso — vira gate onde é estrutural, e relatório onde só a sessão real prova algo.

`rules.auditar_arvore()` roda sem argumento e devolve `[]` quando a árvore de `.claude/rules/` e
`.claude/rules-off/` está sã — recusa isoladamente um `.md` em subdiretório de `rules/` (a `L-26`
inteira: o matcher recursa, e o arquivo continua carregando), uma rule malformada em `rules/`, e
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

**O controle de três estados que provou a `L-26`**, e que qualquer projeto que instalar o plugin
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

Referência viva:
[`docs/plan/model/0001-decode-and-code-foundation/01-config-and-paths.md`](../model/0001-decode-and-code-foundation/01-config-and-paths.md) —
instância real, validada contra código em produção. O formato **não é duplicado aqui**: o exemplo é
a fonte.

### Regiões — quem escreve o quê

Esta é a regra que torna o estado projetável sem risco de perda:

| Região | Quem escreve | Conteúdo |
|---|---|---|
| **Frontmatter** | Script (bloco `# verificação`) e humano (demais) | `state`, `test`, `verified_at` são do script |
| **Corpo** | Humano / skill | Contrato, sequência, arquivos, normas, critério de aceite |

O script **nunca edita o corpo**. Escreve apenas três campos do frontmatter — região delimitada,
parseável e sem prosa. O mesmo princípio se aplica ao backlog no arquivo do plano, cujo formato é o
próximo item a definir.

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
| Verificação | Teste, comando para rodá-lo, último resultado |
| Fonte | De onde veio a spec |

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

> Origem: `L-17` e o gap de cobertura da `0001-13`, no plano que motivou esta regra. Nos dois casos
> o executor resolveu certo, mas teve de
> **derivar** a precedência, porque ela não estava escrita. Em um deles a derivação saiu ao contrário
> — a tabela de arquivos prevaleceu sobre o critério — e a única regra nova da unidade ficou sem
> oráculo.

### Identificador

O `unit_id` combina o número do plano com o número da unidade dentro dele:

```yaml
unit_id: 0001-02        # plano 0001, segunda unidade
```

A numeração das unidades é **por plano** — recomeça em `01` a cada plano novo. Quatro dígitos para o
plano, dois para a unidade.

### Tipo de unidade

Nem toda unidade entrega código. O campo `unit_type` define o que ela produz e qual é seu oráculo:

```yaml
unit_type: dev     # dev | plan
```

| Tipo | Entrega | Oráculo de conclusão |
|---|---|---|
| `dev` | Código | O teste declarado passa |
| `plan` | Um plano | O plano existe e consta em `_planos.md` |

Isso mantém **um único mecanismo**: todo plano gera unidades. Um plano de core, por exemplo, gera
unidades `plan` — cada uma produzindo o plano de um módulo. O oráculo continua verificável por
script, porque a linha aparece na tabela.

Sem isso, planos de nível alto exigiriam uma segunda mecânica de plano; com isso, a diferença fica
contida num campo.

É o `unit_id` que o comentário-cabeçalho cita no código, **não o nome do arquivo**. Isso preserva a
razão original da decisão 21: renomear o slug de uma unidade não quebra referência alguma, porque
nenhuma referência aponta para o filename.

Substitui o esquema de prefixo por módulo (`AU-`, `CA-`) do acervo em `docs/mvp/`, que permanece como
está — sem migração.

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

### Backlog — região delimitada por marcadores

O script projeta o backlog entre marcadores de comentário, invisíveis no markdown renderizado:

```markdown
<!-- backlog:start -->
| Unidade | Título | Estado |
|---|---|---|
| [0001-01](01-handler-auth.md) | Handler MCP com autenticação obrigatória | `verified` |
| [0001-02](02-search-catalog.md) | Tool search_catalog | `spec` |

1 de 9 verificadas · atualizado em 2026-07-19
<!-- backlog:end -->
```

O script substitui **exatamente** o conteúdo entre os marcadores; o resto do plano é intocável. É o
mesmo princípio do frontmatter na unidade — região delimitada, sem prosa —, aplicado ao corpo.
Parsear headings seria frágil: qualquer texto adicionado na seção se perderia na próxima projeção.

**Por que o backlog não é o índice eliminado.** O índice agregava por core, informação que a
estrutura de pastas já dá. O backlog agrega **por plano** — recorte temporal que a estrutura não
expressa, já que unidades de vários planos convivem na mesma pasta do módulo.

### Bloco obrigatório — Independência

Todo plano declara, no corpo, por que é **um** plano e não dois. Uma seção `## Independência` responde
ao teste: entregando apenas este plano e parando, o sistema fica em estado válido — e não há parte
separável que entregue valor sozinha.

A declaração é feita **no momento da escrita**, não descoberta na revisão: é quando ainda é barato
mudar de ideia. A revisão apenas audita se ela se sustenta (ver *Avaliação de escopo*).

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
> **identificador**, exigindo inglês. As duas normas se contradiziam até 2026-07-28 (ver decisão 32).
> A prosa do plano continua inteiramente em pt-BR: o inglês vale para o **nome**, não para o conteúdo.

**Na aprovação, recebe o número** — 4 dígitos, sequencial global, atribuído uma única vez:

```
_inbox/evolve-tools.md   →   <core>/0004-evolve-tools/0004-evolve-tools.md
```

A pasta criada tem **exatamente o mesmo nome** do arquivo. Quando o plano cria um módulo, seu nome
costuma ser o próprio módulo: `_inbox/mcp.md` → `<core>/0001-mcp/0001-mcp.md`.

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
| **`unit_id`** | `0001-02` | frontmatter, comentário-cabeçalho no código, testes, backlog | **Nunca** |
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
| 0001 | [mcp](<core>/0001-mcp/0001-mcp.md) | `<core>` | mcp | em desenvolvimento | 2026-07-20 |
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

**Fora do escopo desta fase:** qualquer agent. Agent só se justifica onde há julgamento somado a
pesquisa ampla, e só depois de a skill existir.

---

## Fluxo completo

| # | Etapa | Executor | Resultado |
|---|---|---|---|
| 1 | Plano nasce | Opus | `docs/plan/_inbox/nome.md` |
| 2 | Revisão | skill + script | Cinco checks |
| 3 | **Aprovação** | **humano** | gate |
| 4 | Número atribuído | script | Próximo livre em `_planos.md` — 4 dígitos |
| 5 | Estrutura criada | script | `docs/plan/<core>/<NNNN>-<nome>/` |
| 5b | Plano movido e prefixado | script | `_inbox/<nome>.md` → `<NNNN>-<nome>/<NNNN>-<nome>.md` |
| 6 | Unidades derivadas | Opus | Um arquivo por unidade, densas para cold-start |
| 7 | Backlog projetado | script | No arquivo do plano |
| 8 | Implementação | Sonnet (default) | Uma unidade por vez, em cold-start |
| 9 | Fechamento | script | Estado projetado na unidade e no backlog |

> **A etapa 4 é reentrante.** `scaffold.aprovar` sobre um plano já aprovado devolve o caminho sem
> escrever nada — derivar em lotes reinvoca a etapa sobre o mesmo plano, e isso é o caminho previsto,
> não uma exceção a tratar.

---

## Rastreamento de objetivos

| Origem | Objetivo | Componente |
|---|---|---|
| Inicial | Módulo como organizador; pasta por módulo | 1 |
| Inicial | Adição como bloco aditivo | 1 |
| Inicial | Doc deixa de ser PRD e vira o módulo | 2 |
| Inicial | Índice do sistema com link para o módulo | 1 — a hierarquia de pastas é auto-descritiva |
| Novo | Nível core para evoluir sob Clean Architecture | 1, 3 |
| Novo | Modular com blocos (Google/email como bloco) | 1 |
| Novo | Documentação é código em produção | 2 |
| Novo | Código documentado com inteligência | 5 |
| Novo | Índice para orientar agente e desenvolvedor | 1 — idem |
| Novo | Princípios, guidelines, guardrails, referências | 3 |
| Novo | Revisão de plano sugerindo blocos | 4, modo `review` |
| Novo | Quebrar plano em fases e fases em unidades | 4 |
| Novo | **Cold-start com Sonnet sem pedido manual** | Conceitos, modo `derive` |
| Novo | **Backlog do plano com as unidades** | 2 — projeção |
| Novo | **Registro de conclusão na unidade e no plano** | 2 — duas projeções, uma fonte |
| Auditoria | 0/18 com critério de aceite | 2 |
| Auditoria | 0/18 ligados a teste | 2 |
| Auditoria | 18/18 `draft`; sem estado | 2 |
| Auditoria | Lote sem norma | 4 |
| Auditoria | 90 refs código↔doc; lacunas; racional | 5 |

---

## Decisões

### Resolvidas em 2026-07-19

| # | Decisão | Resolução |
|---|---|---|
| 1 | Norma de lote | **8 passos** (p90 das 86 unidades); sem sequência = incompleta |
| 2 | Grão de bloco e unidade | Bloco é **pasta**; unidade é **arquivo** (exigência do cold-start) |
| 3 | Como o estado é computado | **Declaração na spec** (`spec → teste`), granularidade de arquivo |
| 4 | Onde vive a normativa de domínio | **`<core>/system/`**; transversal em `<core-transversal>/system/` |
| 5 | Cobertura da normativa | Cada core ganha a sua, conforme for tocado |
| 6 | Localização dos docs | **`docs/plan/`** para o novo; acervo legado, se houver, somente leitura |
| 7 | Migração do acervo | **Não migrar agora** — tarefa futura |
| 8 | Modelo de desenvolvimento | **Sonnet** por padrão, com override do usuário |
| 9 | Core transversal | Dono de um módulo hospedado em outro core, sem produzir deployable próprio |
| 10 | Índice | **Eliminado** — substituído pela estrutura + backlog + consulta sob demanda |
| 11 | Vocabulário | Inglês em código, caminhos e frontmatter; **português na prosa** |
| 12 | Formato da unidade | Definido; referência viva em `docs/plan/model/0001-decode-and-code-foundation/01-config-and-paths.md` |
| 13 | Regiões de escrita | Script escreve só o bloco `# verificação` do frontmatter; nunca o corpo |
| 14 | Identificador da unidade | `unit_id` = `[nº plano]-[nº unidade]`, ex. `0001-02` — **revisa** o prefixo por módulo (`MC-`, `AU-`) |
| 15 | Teste inexistente | Gate de entrada exige teste **declarado**, não existente; `implement` escreve teste e código |
| 16 | Alvo do plano | Frontmatter com `core`/`module`/`block`; **um plano, um alvo** |
| 17 | Backlog | Marcadores `<!-- backlog:start -->` / `<!-- backlog:end -->`; script substitui só o miolo |
| 18 | Modelo por modo | **Não declarável em skill** — política operacional; automatizar exigiria agent |
| 19 | Nome do plano | Mantém o nome ao sair do `_inbox` e **recebe prefixo numérico**; nunca vira `plano.md` |
| 20 | Regra de nome | `<intenção>-<alvo>[-<qualificador>]`, kebab-case, sem repetir o caminho — idioma **revisado** pela decisão 32 |
| 21 | Arquivo da unidade | `[nn]-[nome].md` — **revisa** "só o ID"; a estabilidade vem do `unit_id`, não do filename |
| 22 | Numeração do plano | **4 dígitos**, sequencial global, atribuída na aprovação; **pasta = nome do arquivo** |
| 23 | Numeração da unidade | **2 dígitos, por plano** — recomeça em `01` a cada plano novo |
| 24 | Tabela de planos | `docs/plan/_planos.md` — só aprovados; fonte da numeração; situação projetada |
| 25 | Avaliação de escopo | Teste de **independência** declarado na escrita do plano, auditado na revisão; concorrência checada em `_planos.md` |
| 26 | Divisão não bloqueia | Sinaliza e exige registro do porquê quando não se divide; **sem teto de unidades** |
| 27 | Alvo do plano | Sempre `core`/`module`/`block` — não existe alvo `system` |
| 28 | Tipo de unidade | `unit_type: dev \| plan`; a unidade `plan` produz um plano, com oráculo em `_planos.md` |
| 29 | Relação entre planos | Coluna **Origem** em `_planos.md` — qual unidade de qual plano o gerou |
| 30 | Natureza deste documento | **Norma**, não plano; a implementação é o plano que a instancia no projeto |

### Resolvida em 2026-07-24

| # | Decisão | Resolução |
|---|---|---|
| 31 | Linguagem e verificação dos scripts | **Python 3.10** (versão do Cowork), stdlib pura, `unittest` via `scripts/test-python.sh` — ver [`language-policy.md`](language-policy.md) |

> A pendência de infra de teste que travava este modelo não era técnica: vinha do bloqueio "sem
> Python", revogado pela [norma de linguagem](language-policy.md) com base em medição. O oráculo
> determinístico previsto no componente 5 deixa de depender de uma decisão em aberto.

### Resolvida em 2026-07-28

| # | Decisão | Resolução |
|---|---|---|
| 32 | Idioma do nome de plano, módulo e unidade | **Inglês** — **revisa** a decisão 20, que dizia pt-BR |

> **O conflito que a originou.** A decisão 20 exigia pt-BR no nome; o `.claude/CLAUDE.md` § *Idioma e
> Nomenclatura* exige inglês em identificadores e nomeia **módulo** entre eles. Como o nome do plano
> vira o `module` do frontmatter e a pasta no disco, as duas normas se contradiziam — e o conflito só
> apareceu quando o terceiro plano precisou de um nome que não fosse termo técnico.
>
> **Custo de migração: zero.** Os planos que existiam quando a decisão foi tomada já eram termos
> técnicos em inglês; nenhum renomeio.
>
> **O que não muda:** a prosa. Documentação, plano e unidade seguem inteiramente em pt-BR — o inglês
> vale para o identificador, nunca para o conteúdo.

### Pendentes

1. **Alinhamento do `CLAUDE.md`.** A regra de precedência foi **antecipada em 2026-07-19**. Restam as
   doze referências a `docs/mvp` e a desambiguação entre o **Core Engine** (visão futura, telemetria)
   e a pasta **`system/`** — ambas acompanham a migração.
2. **Troca automática de modelo por modo.** Só é possível com agent (ver *Modelos*). Se for
   requisito, e não conveniência, reabre a decisão sobre agents — hoje fora de escopo.
> **Resolvidas nesta rodada:** as regiões no `index.md`, pelo mecanismo de marcadores (ver *Formato
> do plano*) — o mesmo padrão serve a qualquer arquivo com conteúdo humano e projeção de script no
> mesmo corpo; e a migração da unidade-referência, executada em 2026-07-20 junto com a criação do
> plano `0001` e da tabela `_planos.md`.

---

## Referências

**Evidência empírica**
- METR (2025), *Measuring the Impact of Early-2025 AI on Experienced Open-Source Developer
  Productivity* — https://metr.org/blog/2025-07-10-early-2025-ai-experienced-os-dev-study/
- DORA (2024), *Accelerate State of DevOps Report* — https://dora.dev/research/2024/dora-report/
- DORA (2025), *State of AI-assisted Software Development* — https://dora.dev/dora-report-2025/

**Análise de métodos**
- Böckeler, B., *Understanding Spec-Driven Development: Kiro, spec-kit e Tessl* —
  https://martinfowler.com/articles/exploring-gen-ai/sdd-3-tools.html
- GitHub Spec Kit — https://github.com/github/spec-kit

**Interno**
- Norma de linguagem dos scripts: [`language-policy.md`](language-policy.md)
- Evidência que a fundamenta: [`estudo-runtime-e-dependencias.md`](estudo-runtime-e-dependencias.md)
- Padrão atual: `.claude/skills/decode-and-code/SKILL.md`
- Restrições de processo e frontmatter: `.claude/CLAUDE.md`
