---
# about
name: installable-method
type: plan
project: DecodeAndCode
description: O método passa a funcionar no projeto que o instala — hoje o pacote entrega skill, agentes e hooks que carregam, e nenhum caminho para usá-los, porque os scripts não acham o projeto, a estrutura inicial não existe e a norma que os três modos citam não viaja
tags: [decode-and-code, plugin, bootstrap, norma, instalacao]

# alvo
plan_id: "0004"
plan_size: grande
core: model
module: installable-method
block: ""

# history
author: Bortoli
created: 2026-08-27
status: done
version: 1.0.0
updated: ""
approved_by: Bortoli
approved_at: 2026-08-27

# system
scope: project
auto_load: false
dependencies: []
---

# O pacote instala; agora o método precisa operar onde ele instalou

## O que foi medido

Em **2026-08-27**, o pacote foi carregado por `claude --plugin-dir` a partir de `/tmp` — fora do
repositório que o produziu. Três coisas ficaram provadas, e nenhuma delas era conhecida antes:

| Fato | Evidência |
|---|---|
| **Os hooks do pacote carregam** | O log de ativação foi escrito em `/tmp`, onde **não existe hook de projeto**. Uma linha, o `CLAUDE.md` global — exatamente o que aquele diretório tem. A troca de âncora para `${CLAUDE_PLUGIN_ROOT}` que a `0001-16` fez funciona |
| **Skill e agentes viajam** | `decode-and-code:decode-and-code`, `decode-and-code:planner` e `decode-and-code:developer` disponíveis fora do repositório de origem |
| **A norma não vai junto** | `docs/plan/system/modelo-dev-units.md` não existe lá, e os três modos da skill a citam |

E o resultado abriu um quarto, maior que os outros e que ninguém tinha procurado:

| Fato | Evidência |
|---|---|
| **Um projeto novo não consegue começar** | `scaffold.aprovar` sobre o primeiro plano de um projeto zerado morre com `FileNotFoundError` em `_planos.md`. **Nada no pacote cria a estrutura inicial** — `_planos.md` com os marcadores, `_inbox/`, `system/` são pré-condição, e o método assume que já existem |

> **Passou despercebido porque ninguém nunca rodou o ciclo do zero.** Na validação de 2026-08-27 eu
> montei o `_planos.md` à mão no repositório descartável e tratei isso como preparação de teste. Era
> o defeito, contornado sem ser visto. Aqui a estrutura existe porque este repositório **nasceu**
> com ela.

### A derivação mediu de novo, e achou o que está abaixo disso

Na derivação deste plano — **2026-08-27**, pacote construído fora do repositório e scripts rodados a
partir de um projeto zerado — o bootstrap ausente revelou-se sintoma, não causa:

| Fato | Evidência |
|---|---|
| **Os scripts não acham o projeto** | `lib.repo_root()` sobe a partir do `__file__`, que num plugin é o diretório do **plugin**. `RuntimeError: raiz do repositório não localizada` a partir de `.../skills/decode-and-code/scripts` |
| **`scaffold` morre no import** | [`scaffold.py:45`](../../../../.claude/skills/decode-and-code/scripts/scaffold.py) chama `lib.repo_root()` em nível de módulo, para carregar `move-md`. **19 dos 20 módulos importam; só ele não** |
| **A camada de determinismo fica inalcançável** | `lib.plan_root()` e `numeracao.proximo_plano()` levantam `RuntimeError`; `nomenclatura.validar_nome`, que é função pura, responde normalmente. **14 dos 21 scripts** chamam `repo_root`/`plan_root` |
| **`move-md.py` não viaja** | `config.json` declara `move_script: scripts/move-md.py`, relativo à raiz do repositório. O pacote não o leva, e é o que o `scaffold` carrega no import |

> **Os hooks funcionaram em `/tmp` justamente porque nenhum deles chama `repo_root`** — se ancoram
> em `__file__` e `gettempdir()`. A prova de ontem continua válida, e o que ela não cobria é isto.

**A leitura junta tudo numa frase.** Quem instala hoje recebe skill que funciona, agentes que
carregam e hooks que disparam — e nenhum caminho para usar nada disso. Falta a **âncora** (os
scripts não sabem qual é o projeto), falta o **chão** (a estrutura) e falta a **referência** (a
norma), e as três são a mesma pergunta: **o que um projeto precisa para o método operar nele.**

## Objetivo

O método passa a operar no projeto que o instala. Um diretório qualquer, com o plugin carregado,
consegue percorrer o ciclo inteiro — estrutura criada, plano aprovado, unidades derivadas,
implementadas e fechadas — **sem nada deste repositório**.

## Escopo

### Fase 1 — O projeto ganha âncora e chão

| # | Unidade | Responsabilidade |
|---|---|---|
| 01 | `project-anchor` | `lib` passa a resolver **o projeto onde o método opera**, e não o diretório onde o próprio código mora. É o que destrava as outras quatro: sem isso, todo script que resolve caminho morre num plugin instalado |
| 02 | `project-bootstrap` | A operação que cria a estrutura mínima no projeto que instala: `_planos.md` com os marcadores, `_inbox/`, `system/`. **Idempotente e nunca destrutiva** — projeto que já tem estrutura não é tocado, no mesmo contrato de `huddle.iniciar` e do bootstrap de `porte.registrar` |

### Fase 2 — A norma se divide

| # | Unidade | Responsabilidade |
|---|---|---|
| 03 | `norm-split` | O **operativo** da norma sai para um documento que viaja; a evidência, as decisões e a história deste projeto saem para um documento que fica, **citando** o mecanismo. É a `D-26` do plano `0001`, e o padrão é o que a `D-16` já validou: a rule carrega o operativo, o documento do projeto carrega o racional |

### Fase 3 — O pacote leva o que falta, e prova

| # | Unidade | Responsabilidade |
|---|---|---|
| 04 | `package-carries-norm` | `construir` passa a levar a norma-mecanismo e o `move-md`, e a expor o bootstrap; `verificar` continua limpo, e `claude plugin validate` continua aprovando |
| 05 | `installed-cycle-proof` | O teste que **roda o ciclo inteiro num projeto zerado**, a partir do pacote construído: bootstrap, aprovar, gate de entrada sobre uma unidade sintética, gate de saída, fechamento. É o oráculo que teria pego a Fase 1 antes de alguém tropeçar nela. *Derivar* fica de fora por natureza — é julgamento da skill, não passo de script |
| 06 | `commands-travel` | `construir` passa a levar `.claude/commands/` — `/implement` e `/delegate`, os dois comandos que disparam cold-start —, e o esqueleto do handoff mais a norma-mecanismo passam a dizer que eles existem. Não estava na Fase 3 original porque os comandos não existiam quando o plano foi derivado (`D-08`) |

**Seis unidades.** As quatro primeiras entregam o que falta; a quinta transforma *"o pacote
instala"* em algo que a suíte afirma a cada execução, em vez de depender de alguém lembrar de
testar num diretório vazio; a sexta fecha, no pacote, a mesma lacuna que abriu o plano — só que
num artefato que nasceu depois da derivação.

## Independência

**Entregando apenas este plano e parando, o sistema fica em estado válido:** o método passa a
operar onde é instalado, e este repositório continua funcionando exatamente como hoje — a divisão da
norma não muda o que ele lê, só onde cada metade vive.

**Não há parte separável que entregue valor sozinha.** Âncora sem bootstrap resolve um projeto que
não tem onde escrever; bootstrap sem norma dá a um projeto novo a estrutura e nenhuma referência
para preenchê-la; norma sem âncora dá a referência a scripts que não acham o projeto. As três juntas
é que fazem o ciclo fechar, e a `05` é o que prova que fechou.

**Concorrência:** os planos `0001`, `0002` e `0003` estão `concluído`; não há plano em
desenvolvimento no core `model`.

## Restrições conhecidas

| Restrição | Onde |
|---|---|
| A norma tem **1250 linhas**, com 11 referências a unidades `0001-`, 6 a `METR`/`DORA`, 3 a `docs/mvp` e 3 a `AmFlow` — a divisão precisa separar mecanismo de registro deste projeto | Remedido na derivação, 2026-08-27. O `D-26` do plano `0001` dizia 1087 linhas e 18 refs `0001-` em 2026-08-26: o arquivo cresceu e as referências caíram desde então |
| **35 arquivos citam `modelo-dev-units.md`**, e 21 deles são unidades do plano `0001`, fechado | Medido em 2026-08-27. É o que torna o `D-07` barato: mantendo o nome no mecanismo, nenhum dos 35 precisa mudar |
| O log de ativação **não registra procedência**: dentro do repositório de origem, hook do projeto e hook do pacote se confundem. Medir ativação de pacote exige diretório que não seja o que o produziu | Medido em 2026-08-27 |
| `claude --plugin-dir` abre **sessão interativa** — nenhuma sessão do Claude a executa por dentro. A prova final de instalação é ato humano, reportado | Medido em 2026-08-27 |
| `CLAUDE_PROJECT_DIR` **não existe no ambiente** de uma sessão do Claude Code — é substituição literal feita no `hooks.json`, não variável exportada. Não serve de âncora para script invocado por Bash, do mesmo jeito que `CLAUDE_PLUGIN_ROOT` já não servia | Medido em 2026-08-27; o precedente do `CLAUDE_PLUGIN_ROOT` está no docstring de `lib.py` |
| `scripts/test-python.sh` tem `TEST_DIRS` fixo na estrutura deste repositório — é **instância**, e é correto que não viaje. O runner é do projeto que instala, declarado no `runners` do `config.json` | Medido em 2026-08-27 |
| `state` e `verified_at` nunca se editam à mão | Norma, *Os dois gates* |

## Oráculo

| Natureza | Unidades | Oráculo |
|---|---|---|
| **Comportamento** | `01`, `02`, `04`, `05` | Teste real. A âncora resolve um projeto a partir de scripts que moram fora dele, e dentro deste repositório nada muda; o bootstrap cria a estrutura num diretório vazio e **não toca** um que já a tenha; o pacote sai com a norma-mecanismo e o `move-md`, e segue limpo em `verificar` e em `claude plugin validate`; e a `05` percorre o ciclo do zero, o que hoje **falha** |
| **Estrutura** | `03` | Verificador dos invariantes do artefato: o documento que viaja não contém instância deste projeto — nem `0001-`, nem `docs/mvp`, nem nome de repositório —, e o que fica aqui **cita** o que saiu, nunca o copia |

## Decisões

Tomadas na derivação de **2026-08-27**, sobre a medição registrada acima.

| # | Decisão | Por quê |
|---|---|---|
| D-01 | **A âncora é unidade própria, e vem primeiro** | É outro mecanismo — como `lib` resolve o projeto —, com oráculo próprio, e toca `lib.py` mais os 14 chamadores. Raio diferente de criar diretório. Dobrada na `project-bootstrap`, o contrato teria duas entradas sem relação entre si. Escolha do humano na derivação |
| D-02 | **A âncora não usa variável de ambiente** | `CLAUDE_PLUGIN_ROOT` já foi medido vazio (docstring de `lib.py`) e `CLAUDE_PROJECT_DIR` também não existe no ambiente. Restam dois candidatos reais: o `cwd` e o `__file__`. Inventar uma variável nossa seria configurabilidade não pedida |
| D-03 | **`__file__` deixa de ser a única âncora, e não deixa de ser âncora** | Ele é o certo para checkout e para teste que roda de `tempfile` — a suíte inteira depende disso. O que falta é um segundo candidato para o caso do plugin. A ordem entre os dois é decisão da unidade `01`, guiada pelo critério; o que o plano fixa é que **os dois existem** |
| D-04 | **`.claude/` entra no bootstrap** | `root_markers` exige `.claude/` **e** `docs/`, e projeto zerado não tem nenhum dos dois — a âncora não teria como resolvê-lo depois do bootstrap. Não é criação incidental: `empacotar.materializar` já escreve em `<projeto>/.claude/rules/`, então é onde a camada normativa do projeto vai morar de qualquer forma |
| D-05 | **O bootstrap não cria runner de teste** | `test-python.sh` é instância deste repositório. Criar um na casa de quem instala é feature além do pedido; o projeto declara o seu em `runners`. A `05` monta um stub no próprio fixture |
| D-06 | **`move-md.py` viaja; `test-python.sh` não** | O primeiro é mecanismo puro — reescrita de link markdown, sem instância nenhuma — e o `scaffold` o carrega no import. O segundo é instância. A distinção é o invariante 2 aplicado arquivo a arquivo |
| D-07 | **A norma-mecanismo mantém o caminho que a skill já cita** | `SKILL.md` referencia `<plan_root>/system/modelo-dev-units.md` em três lugares. O mecanismo fica com esse nome, e o **registro** deste projeto é que ganha arquivo novo. O contrário faria a skill ler o registro |
| D-08 | **`.claude/commands/implement.md` e `.claude/commands/delegate.md` viajam no pacote, como unidade nova (`06`) em vez de lacuna adiada** | Os dois comandos nasceram depois da derivação deste plano, em 2026-08-28, testando os cenários de execução em nova sessão e via agente. São mecanismo puro — sem marca de instância, mesmo padrão de skill/agents/hooks — e ficar de fora repetiria a lacuna que abriu o `0004`: *"skill que funciona, agentes que carregam... e nenhum caminho para usar nada disso"*. Adiar para plano futuro criaria dependência entre planos em andamento, o padrão que *Avaliação de escopo* pede para evitar; a `04` já tinha aberto o precedente de reescrever `project:` no frontmatter copiado (`_declarar_o_plugin`), que a `06` reaproveita |
| D-09 | **`dist/decode-and-code/` passa a ser versionado, revertendo a `D-21` do plano `0001`** | Feita fora de unidade, em 2026-09-01, ao publicar o plugin. A `D-21` decidiu build reproduzível com `dist/` no `.gitignore`, e a razão era boa: *árvore construída e commitada envelhece a cada mudança da fonte, e nada avisa*. A distribuição não deixa alternativa — o `source` de cada entrada do `marketplace.json` resolve contra a raiz do repositório clonado (doc oficial, `plugin-marketplaces`), e quem instala **não roda `construir`**. O que muda em relação à `D-21` não é o risco, é o *nada avisa*: `TestPacoteCommitadoEstaSincronizado` compara o commitado com o recém-construído byte a byte, e os dois braços — arquivo alterado e arquivo ausente — foram medidos falhando antes de o caso entrar verde |
| D-10 | **O manifesto-fonte sai de `.claude-plugin/plugin.json` para `.claude/plugin.json`, e a raiz vira só marketplace** | Mesmo ato, mesma data. Manifesto na raiz declarava a **raiz** como plugin, e ao lado dela não há `skills/` nem `hooks/` — só `.claude/`. `claude plugin validate .` aprovava, porque valida o manifesto e não o que ele promete: instalar da raiz daria um plugin válido que carrega nada. O manifesto é fonte, e passa a morar com as outras fontes que `construir` copia; `.claude-plugin/` da raiz fica com `marketplace.json`, e `.claude-plugin/plugin.json` existe só dentro do pacote, escrito pelo build |

## Lacunas

| # | Lacuna | Por que fica registrada |
|---|---|---|
| L-01 | **Não se sabe se `skills:` carrega de verdade** | A `D-05` do plano `0001` faz do campo a ponte entre agente e método, e a medição de 2026-08-26 mostra que **nenhum dos 34 agentes instalados o declara**. Em 2026-08-27 confirmou-se que os agentes ficam **disponíveis** fora do repositório — não que invocá-los traga a skill junto. O teste é invocar `@decode-and-code:planner` numa sessão de pacote e reler o log; fica registrado porque é ato humano e não cabe em gate |
| L-02 | **A divisão da norma não tem oráculo para "a metade certa foi para o lugar certo"** | O teste alcança ausência de instância no que viaja e presença de citação no que fica. Que a fronteira entre mecanismo e registro esteja no lugar certo é julgamento — é a `L-01` do plano `0001` num artefato novo, e o maior deste plano |
| L-03 | **Nenhuma ordem de âncora é segura em todo ambiente, e o teste não alcança a diferença** | Com `__file__` na frente, uma máquina que tenha `~/docs` resolveria a **home** como raiz, em silêncio — nesta não tem, e foi conferido. Com `cwd` na frente, invocação de fora de qualquer projeto resolve errado. As duas falhas dependem do sistema de arquivos de quem roda, e a suíte roda só neste. Fica registrada porque a `01` **escolhe** uma ordem e o risco da outra não desaparece |
| L-04 | **Quem instala não tem como configurar nada** | `lib._config_path()` é `config.json` na raiz da **skill** — viaja com o plugin, não com o projeto. Então `plan_root` e `runners`, que a unidade `0001-01` tornou configuráveis, são inalteráveis a partir de um projeto instalado: ele tem de aceitar `docs/plan` e pôr o runner em `scripts/test-python.sh`. Medido em 2026-08-27. Fica registrada e **não entra no escopo**: o padrão funciona, e a `05` prova o ciclo honrando-o. Resolver exige decidir onde mora o config de projeto, que é decisão de desenho, não correção |
| L-05 | **A unidade `03` se contradiz sobre se o mecanismo pode nomear o registro** | O Contrato proíbe — *"o mecanismo não cita o registro"*, porque citação nas duas direções faria o mecanismo depender de um arquivo que não viaja. A Sequência, passo 3, manda abrir o mecanismo com a nota *"o registro deste projeto está no vizinho"*, que é exatamente a citação proibida. A execução seguiu o Contrato, pela regra de precedência entre blocos, e registrou a divergência no huddle (`H-10`). Achada na execução de 2026-08-28. É defeito **da unidade**, não da entrega: derivação futura precisa escrever Contrato e Sequência que concordem, e o lint de unidade não alcança contradição entre blocos |
| L-06 | **A unidade `04` pede um "quadro de referência" em `config.json` que o formato não comporta** | Sequência, passo 2, e a tabela de Arquivos mandam escrever no `config.json` o quadro de referência de cada campo (`move_script` contra a skill, `runners` contra o projeto) — mas o arquivo é JSON puro, sem comentário, e `lib.config()` recusa chave fora de `lib._DEFAULTS`. A execução documentou o quadro de referência no docstring de `scaffold.py` (único consumidor de `move_script` no escopo da unidade) e não tocou `config.json`, cujo conteúdo já estava correto — só a base de resolução mudou, em código. Contrato e Critério de aceite não exigem mudança em `config.json`, e passam pela regra de precedência entre blocos. Achada na execução de 2026-08-28. É defeito **da unidade**: dar ao `config.json` um jeito de carregar essa metadata (ou aceitar que ela more só em código) é decisão de desenho, não correção de derivação |

## Fonte

- Medições de 2026-08-27 com `claude --plugin-dir ./dist/decode-and-code`, de dentro e de fora do
  repositório de origem
- Medição da derivação, 2026-08-27: pacote construído fora do repositório, scripts importados a
  partir de um projeto zerado — é de onde vêm a âncora, o `scaffold` que morre no import e o
  `move-md` ausente
- `0001`, `D-21`, `D-22`, `D-26` e `D-27` — o que viaja no pacote e por quê
- Documentação oficial: `code.claude.com/docs/en/plugins` e `plugin-marketplaces`, consultadas em
  2026-08-27

## Backlog

<!-- backlog:start -->
| Unidade | Título | Estado |
|---|---|---|
| [0004-01](01-project-anchor.md) | project-anchor | `verified` |
| [0004-02](02-project-bootstrap.md) | project-bootstrap | `verified` |
| [0004-03](03-norm-split.md) | norm-split | `verified` |
| [0004-04](04-package-carries-norm.md) | package-carries-norm | `verified` |
| [0004-05](05-installed-cycle-proof.md) | installed-cycle-proof | `verified` |
| [0004-06](06-commands-travel.md) | commands-travel | `verified` |

6 de 6 derivadas · 6 verificadas · atualizado em 2026-09-01
<!-- backlog:end -->
