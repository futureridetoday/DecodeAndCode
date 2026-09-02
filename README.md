# decode-and-code

Plugin do Claude Code que empacota o método **decode-and-code**: o ciclo `plano → unidade →
cold-start` que transforma trabalho novo em unidades executáveis por uma sessão sem contexto, e a
**norma em camadas** que decide o que cada unidade pode assumir sem perguntar.

**O problema.** Uma sessão nova do modelo não sabe o que a anterior sabia — o custo aparece como
retrabalho, decisão re-tomada e execução que diverge do combinado. Documentação solta não resolve:
não é lida no momento certo, e envelhece sem ninguém notar.

**A resposta.** O método faz o *plano* carregar a diferença entre sessões. Trabalho novo vira um
plano; o plano é derivado em *unidades*; cada unidade é escrita para quem chega **sem contexto** da
conversa que a produziu — com contrato, arquivos que toca, normas que referencia e um **teste
declarado**. O critério de que ela está pronta é esse teste passando, não a opinião de quem revisa.
O que a unidade não repete, ela referencia — a norma em camadas guarda o que vale, *uma fonte por
fato*.

**A evidência.** A skill de origem, medida no AmFlow: 15 de 15 unidades executadas por Sonnet em
sessões novas, sem uma pergunta sobre o conteúdo da unidade.

## Instalação

### Por comando

```bash
/plugin marketplace add futureridetoday/DecodeAndCode
```

```bash
/plugin install decode-and-code@future-ride-today
```

Os dois comandos rodam dentro do Claude Code. O primeiro registra o marketplace deste repositório;
o segundo instala o plugin a partir dele.

### Por upload

Customize → Plugins → *upload a custom plugin file*, com o zip anexado ao
[Release](https://github.com/futureridetoday/DecodeAndCode/releases) mais recente
(`decode-and-code-1.0.0.zip`).

### Atualização

Quando sai uma versão nova do plugin:

```bash
/plugin marketplace update future-ride-today
```

```bash
/plugin update decode-and-code@future-ride-today
```

O primeiro refresca o metadado do marketplace (nova `version`, `url`, `sha256`); o segundo baixa o
zip do Release novo, confere o `sha256` e instala. **Reiniciar o Claude Code** para aplicar — ou
usar o painel `/plugin` → aba Installed, que sinaliza *update available*.

Mudança que fica só no repositório (`README.md`, `docs/`, `docs/plan/`) não entra no pacote e não
exige nada de quem instalou.

### Para desenvolver ou testar sem instalar

Depois de `empacotar.construir()` (ver *Como este repositório se relaciona com o pacote*), que
escreve o staging em `dist/decode-and-code/`:

```bash
claude --plugin-dir dist/decode-and-code
```

Ou direto do asset publicado, sem build local:

```bash
claude --plugin-url https://github.com/futureridetoday/DecodeAndCode/releases/download/v1.0.0/decode-and-code-1.0.0.zip
```

## Como usar o Decode And Code

Um documento por recurso, em [`docs/recursos/`](docs/recursos/), no formato *o que é · problema que
resolve · como funciona · como usar · exemplos · fundamentação · base de conhecimento · limites*.

| Tipo | Recurso | O que faz | Doc |
|---|---|---|---|
| skill | `decode-and-code` | Os três modos — `review` um plano, `derive` estrutura e unidades, `implement` uma unidade em cold-start | [decode-and-code.md](docs/recursos/decode-and-code.md) |
| agent | `planner` | Revisa um plano antes da aprovação, e deriva as unidades de um plano aprovado (Opus) | [planner.md](docs/recursos/planner.md) |
| agent | `developer` | Implementa uma unidade já derivada, em cold-start isolado (Sonnet) | [developer.md](docs/recursos/developer.md) |
| command | `/decode-and-code:implement` | Roda o modo `implement` na sessão atual — pensado para sessão nova | [implement.md](docs/recursos/implement.md) |
| command | `/decode-and-code:delegate` | Delega a unidade ao agent `developer` sem sair da sessão de orquestração | [delegate.md](docs/recursos/delegate.md) |
| hooks | 4 hooks | Guardrail do projeto (`PreToolUse`) e anúncio de norma/guidelines/subagente — no harness, sem custo de contexto | [hooks.md](docs/recursos/hooks.md) |

O plugin carrega o **mecanismo**. Guardrail e guideline são do projeto que instala — o método os
materializa lá, e nunca viaja com os deste repositório.

## O ciclo

| # | Etapa | Onde |
|---|---|---|
| 1 | O plano nasce | `docs/plan/_inbox/` |
| 2 | Revisão | modo `review` |
| 3 | **Aprovação** | humano |
| 4 | Derivação em unidades | modo `derive` |
| 5 | Implementação, uma unidade por vez | modo `implement`, em cold-start |

Quem executa uma unidade entrega arquivos e relatório, e não commita. O estado de cada unidade
(`spec` → `wip` → `verified`) é **projetado a partir do teste**, nunca editado à mão.

## A norma em camadas

O que uma unidade pode assumir sem perguntar vive em quatro camadas, separadas por quão negociável
cada uma é. A unidade **referencia** a camada, nunca a copia — *uma fonte por fato*.

| Camada | O que é | Onde fica registrado | Como entra em contexto |
|---|---|---|---|
| **Princípio** | a direção e o porquê — estável, muda só por decisão deliberada | [`.claude/rules/principles.md`](.claude/rules/principles.md) | carrega em **toda sessão** — o arquivo não declara `paths:` |
| **Guideline** | o "como" técnico de um escopo — decisão de projeto | um arquivo por regra em `.claude/rules/`, com `paths:` no frontmatter (desligadas ficam no irmão `.claude/rules-off/`) | **ativa sozinha** quando um arquivo que casa `paths:` é tocado |
| **Guardrail** | um limite verificável — o que nunca se faz | `.claude/guardrails.json` | o hook `PreToolUse` consulta a cada chamada de ferramenta e pode **negar**, com a regra no motivo |
| **Referência** | fonte externa canônica — a doc oficial de uma biblioteca-chave | citada no `<core>/system/` | a unidade aponta quando é relevante |

O `CLAUDE.md` é a camada de **processo**; `<core>/system/` cobre o **domínio**.

**Princípio ou guideline? O teste.** *Uma equipe competente pode rejeitar isto e ainda estar
fazendo trabalho bom?* Se **não**, é princípio — os deste repositório (*código é custo*, *subtração
antes de adição*, *evidência acima de opinião*, mais o fluxo de decodificação e o protocolo de
exceção) estão em [`principles.md`](.claude/rules/principles.md), com a proveniência em
[`03-principles-rule.md`](docs/plan/model/0001-decode-and-code-foundation/03-principles-rule.md). Se
**sim**, é guideline. A marca mecânica: princípio não tem `paths:` e carrega sempre; guideline tem
`paths:` e carrega por escopo.

**Guideline ou skill?** Skill é **invocada** — alguém pede, e ela responde *como fazer X*. Guideline
é **ativada** — entra sozinha pelo caminho do arquivo, e responde *o que vale quando eu toco Y*.

### Como cada camada nasce

- **Princípio** — entra como unidade de tipo `norma` (entrega prosa normativa, com aprovação
  humana). Não se descobre em execução, e não muda por conveniência.
- **Guideline e guardrail** — **se escolhem por evidência de falha, não por elegância.** Uma
  guideline nasce na primeira divergência observada entre duas execuções; um guardrail, quando um
  incidente mostra o limite que faltava. Por isso a instância vive no projeto que instala — um repo
  novo é greenfield e não tem incidente nenhum.
- **Ligar e desligar guideline é operação de arquivo, não edição.** Mover entre `.claude/rules/` e
  o irmão `.claude/rules-off/` (fora do que o Claude Code carrega); o `registry.json` que acompanha
  é projeção, nunca fonte.

### O que viaja no plugin

O **mecanismo**: o carregamento nativo por `paths:`, o hook do guardrail, `rules.auditar_arvore()`,
e a norma [`modelo-dev-units.md`](docs/plan/system/modelo-dev-units.md) que **define** as camadas
(seção *Camada normativa*). **Não viaja** o conteúdo: `.claude/rules/*` e `.claude/guardrails.json`
são instância — cada projeto escreve os seus. `bootstrap.iniciar` materializa a norma no projeto que
instala; as camadas, cada projeto preenche.

## Huddle

[`docs/plan/system/huddle.md`](docs/plan/system/huddle.md) é a **fila do que ainda não foi
decidido** — a pauta da conversa recorrente entre quem conduz o projeto e o modelo. Um arquivo por
projeto, nunca carregado automaticamente: entra em contexto quando a conversa acontece, senão
competiria com norma já decidida.

**Para que serve.** As três camadas normativas (princípio, guideline, guardrail) só guardam o que
já foi decidido. O huddle guarda o resto: pergunta em aberto, contradição que a execução contornou,
padrão que uma sessão sozinha não revela, alternativa rejeitada cuja premissa pode ter mudado, algo
que o humano corrigiu. **Nada ali é autoritativo enquanto está ali.** Uma entrada nasce aberta, é
discutida, e quando resolve **sai** — para a norma, uma guideline, ou o `## Decisões` de um plano —,
deixando uma linha em `## Fechadas` com data e destino. Um huddle onde nada fecha só cresce.

**Como usar.**

- **Criar o seu.** O `huddle.md` não viaja no pacote — é instância pura de cada projeto. Quem
  instala o plugin roda `huddle.iniciar(<plan_root>/system/huddle.md)` e recebe o esqueleto vazio,
  com as seções `## Abertas` e `## Fechadas`.
- **Abrir uma entrada.** Cabeçalho de linha única — `### H-XX · <tipo> · AAAA-MM-DD · autor` —, com
  `<tipo>` de vocabulário fechado: `pergunta`, `divergência`, `padrão`, `revisitar`, `observação`.
- **Quando escrever.** No fecho do relatório de qualquer um dos três modos (`review`, `derive`,
  `implement`), uma linha declara `entradas novas no huddle: N` — obrigatória mesmo com `N` igual a
  zero, para separar *conferi e não havia* de *nunca conferi*.
- **Verificar.** `huddle.lint_arquivo(<caminho>)` prova o invariante de despejo: o mesmo `H-XX`
  nunca em `## Abertas` e `## Fechadas` ao mesmo tempo. `huddle.lint_relatorio(<texto>)` recusa o
  relatório sem a linha de fecho.
- **A conversa recorrente.** O próprio `huddle.md` traz um *Prompt de continuidade*, preenchido com
  o estado fresco no fim do trabalho e colado numa sessão nova: `## Como conversamos` define as
  condições da conversa, `## Abertas` é a pauta.

Formato completo, os cinco gatilhos de escrita e a regra de despejo:
[`modelo-dev-units.md`](docs/plan/system/modelo-dev-units.md), seção *Huddle*.

## Como este repositório se relaciona com o pacote

`.claude/` é a **fonte** — a skill, os hooks, os agentes, os comandos e o manifesto
(`.claude/plugin.json`). `dist/decode-and-code/` é staging **gitignorado**: `empacotar.construir()`
o escreve do zero a cada build, e nada dali é commitado. O que se distribui é o **zip** que
`empacotar.empacotar_zip()` produz a partir dessa mesma árvore, publicado como asset de um GitHub
Release e referenciado por `source: archive` (`url` + `sha256`) no `marketplace.json`.

```bash
python3 -c "import sys; sys.path.insert(0, '.claude/skills/decode-and-code/scripts'); import empacotar; empacotar.construir()"
```

### Procedimento de release

O repositório precisa estar **público**: `source: archive` baixa o asset por URL anônima, e um repo
privado devolve `404` para qualquer cliente sem token — inclusive `claude --plugin-url` e
`/plugin marketplace add`.

1. Bump de `version` em **`.claude/plugin.json` e na entrada do plugin no `marketplace.json`** — os
   dois têm que concordar (`claude plugin tag` valida isso)
2. `empacotar_zip()` — constrói, roda `verificar()`/`validar()` sobre o staging, zipa e imprime o
   caminho do zip e o SHA-256
3. `gh release create v<versão> decode-and-code-<versão>.zip --title "Decode and Code <versão>" --notes "…"`
4. Copiar a URL do asset publicado e o SHA-256 para a entrada do plugin no `marketplace.json`
   (`url`, `sha256`)
5. Commit, push
6. `/plugin marketplace update future-ride-today` — e os usuários rodam a *Atualização* acima

## Desenvolvimento

```bash
bash scripts/test-python.sh
```

Exige Python 3.10 explícito — ver [`language-policy.md`](docs/plan/system/language-policy.md) para
a medição de ambientes que fixou o alvo.

A norma completa fica em [`modelo-dev-units.md`](docs/plan/system/modelo-dev-units.md).
