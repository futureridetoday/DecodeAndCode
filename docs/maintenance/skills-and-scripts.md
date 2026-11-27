---
# about
name: skills-and-scripts
type: doc
project: ""
description: Fronteira entre skill e script no plugin, o ponto de entrada dc.py, o modelo de cada skill, os esqueletos sem template e o porquê do log de uso e do porte medido
tags: [manutencao, skills, scripts]

# history
author: Bortoli
created: 2026-11-27
status: stable
version: 1.0.0
updated: ""

# system
scope: project
source: ""
auto_load: false
checksum: ""
dependencies: [codex-guide]
---

# Skills e scripts

Documentação de manutenção: serve a quem mantém o plugin, não ao método. O método — etapas, artefatos
e regras — está no codex; aqui fica como o plugin o executa.

## Fronteira skill / script

| Responsabilidade | Onde vive |
|---|---|
| Detectar modo, validar gates, medir lote, rodar teste, projetar estado, **validar nome e colisão** | **Script** — Python, em `.claude/skills/decode-and-code/scripts/` |
| Pesquisar, sintetizar, revisar com julgamento, decidir a fatia, escrever código, **sugerir nomes** | **Skill** |

Os scripts seguem a [política de linguagem](../plan/system/language-policy.md): Python 3.10 (versão do Cowork), stdlib
pura, verificados com `unittest` via `scripts/test-python.sh`.

**As skills chegam aos scripts por um ponto de entrada só**, `dc.py` — um dispatcher fino com um
subcomando por operação (`python3 "${CLAUDE_SKILL_DIR}/dc.py" <subcomando> …`, rodado do diretório do
projeto). O `${CLAUDE_SKILL_DIR}/dc.py` é um atalho que cada skill traz na própria pasta e que só
executa o `dc.py` da pasta compartilhada (`.claude/skills/decode-and-code/scripts/dc.py`): a liberação
do `allowed-tools` casa o **texto** do comando, e o caminho direto até a pasta irmã leva um `..` que o
modelo normaliza antes de rodar — medido em sessão real: 11 recusas nas três skills. O `allowed-tools`
de cada skill libera só o atalho, nas duas grafias (com aspas e sem),
`Bash(python3 "${CLAUDE_SKILL_DIR}/dc.py" *)` e `Bash(python3 ${CLAUDE_SKILL_DIR}/dc.py *)`, nunca
`Bash` solto: a skill pré-aprova o que lista durante o turno, e
`Bash` solto pré-aprovaria qualquer comando de shell em todo projeto que instalasse o plugin
(`P-14`, `D-05` do plano `apply-plugin-review`). `lint_skill` recusa `Bash` sem especificador, e `Bash(*)` também. Saída
em texto simples, um item por linha; código `0` ok, `1` problema ou reprovação, `2` erro de uso ou
exceção. Como o `dc.py` é o único caminho até o teste, o `verificar` fora de `verified` imprime a saída
dele (as últimas 80 linhas, dizendo quando corta). A lógica continua nos módulos — o `dc.py` só despacha.

Skill interpretando "verifique se está pronto" devolve a variância ao sistema. O que estabiliza é o
oráculo determinístico, e oráculo é código — conforme *Código vs. Instruções em Markdown* no
`CLAUDE.md`.

## Modelos

**Sonnet é o padrão no `implement`.** O `review` e o `derive` pedem julgamento denso — Opus. **Cada
skill declara o seu no `model:` do frontmatter:** `review-plan`, `derive`, `decode`, `huddle`, `setup` e `rethink` em `opus`,
`implement` em `sonnet`.

Medido em 2026-10-15 (Claude Code 2.1.300, pacote carregado com `claude -p --plugin-dir`): sem
fork, `model:` troca o modelo do turno — `/decode-and-code:review-plan` numa sessão Sonnet rodou em
Opus; com `context: fork`, o subagent roda no `model:` da skill — `/decode-and-code:implement`
numa sessão Opus rodou só em Sonnet.

A premissa anterior — a skill herda o modelo da sessão, verificada em 2026-07-19 olhando skills
locais — foi refutada em 2026-10-15 (plano `apply-plugin-review`, achado `P-03`): a documentação
atual (`code.claude.com/docs/en/skills`) lista `model`, `effort`, `context: fork` e `agent` como
campos de skill.

**O gate de agent abriu, e o ciclo voltou a viver em skills.** A skill existe desde **2026-07-26**,
e o requisito de troca automática por modo — não mais conveniência — foi declarado pelo humano em
**2026-08-22**, a partir de uso diário; o agent deixou de estar fora de escopo. Com a troca
declarada na skill, o ciclo não precisa de agent, e o método fica sem agent. O `decode`, que antes
se chamava `intake` e isolava o contexto com `context: fork` (`D-03` do plano `apply-plugin-review`),
roda na sessão desde a subparte 2.2.06 do redesign: conversa com o usuário até a aprovação da
proposta, e a ferramenta de perguntas não existe em fork. O que um agent é aqui:
**papel e processo, nunca o método** — ele **declara** a skill em `skills:`, que é a ponte para o
método chegar sem ser reescrito dentro do próprio prompt; quem decide `model:` e `tools:` é quem o
instancia.

> **A ponte foi medida em 2026-10-15, e é assimétrica.** Num agent de plugin, `skills:` com nome
> curto **resolve**: o debug log mostra `Preloaded skill`, e o agent recebe o corpo da skill com o
> caminho absoluto dos scripts, fora do checkout. Numa skill de plugin, o inverso: `agent:` com nome
> curto de agent do próprio plugin **não resolve** — cai no padrão, sem aviso —, e só o nome com
> namespace (`plugin:agent`) resolve; por isso a skill com `context: fork` (`implement`)
> declara `general-purpose`. Que a skill carregue, ou o nome resolva, é comportamento de
> sessão, e só a medição o mostra.

## Divisão de responsabilidade

| Camada | Onde | O quê |
|---|---|---|
| Sugestão | **Skill** | 3 opções a partir de `core` + `module` + intenção declarada; aceita "outro" |
| Validação sintática | **Script** | Minúsculas e hífens, sem hífen inicial/final/consecutivo, ≤ 64, sem conectivo, sem prefixo numérico |
| Colisão | **Script** | Nome já existente no alvo; próximo ID livre no módulo |

A checagem de colisão não existe na regra de skills e é necessária aqui: o ID sequencial precisa
saber qual é o próximo livre no módulo.

## Sem arquivo de template, e o que não viaja

**O esqueleto vive em `huddle.iniciar(destino, projeto, usuario)`, nunca num `.md` para copiar** — mesmo
padrão de `porte._CONTEUDO_INICIAL`: formato com uma fonte só, que é o script, com esta seção
descrevendo-o em prosa. Escreve `destino` com o frontmatter e as duas seções vazias e devolve o
caminho escrito; sobre um `destino` que já existe, devolve `None` sem tocar em nada.

> **O arquivo de huddle de cada pessoa é instância pura, e não viaja no plugin — o mecanismo que cria um
> vazio, sim**. Entrada aberta é a conversa entre o humano e o modelo **daquele** projeto;
> empacotá-la entregaria a quem instala o registro de decisões de outro repositório — o invariante 2
> quebrado no artefato mais pessoal do método. Quem instala roda `dc.py huddle-iniciar` e recebe o seu, vazio.

## Log de uso — o que o método registra sozinho

Os gatilhos do huddle dependem de quem escreve (codex, *Huddle*). O log é a parte que não depende:
defeito do próprio método, gate que reprovou, guardrail que barrou e instrução que carregou ficam
registrados por script, e o huddle os lê (codex, *Registro de uso*). Veio do plano `0018`.

**Onde mora.** Em `<projeto>/.claude/log/`, que carrega o próprio `.gitignore` (`*`), criado na
primeira escrita: a pasta fica fora do git sem que nada edite o `.gitignore` do projeto. **Só em
projeto com `<plan_root>/_planos.md`**, a marca do bootstrap — com o plugin no escopo de usuário, os
hooks rodam em todo projeto aberto, e o log não pode ser efeito colateral num projeto que não
adotou o método. O hook escreve só ali, numa pasta que o git ignora.

**Eventos.** `.claude/log/eventos.jsonl`, uma linha JSON por evento, com `data` e `classe`:

| Classe | Quem grava | O que leva |
|---|---|---|
| `comando` | `dc.main`, em toda chamada | o subcomando, o código de saída e o alvo (plano ou unidade) |
| `bloqueio` | hook `PreToolUse`, só quando nega | a regra e o nome da ferramenta — **nunca** valor de `tool_input`, que pode ter segredo |
| `ativacao` | hook `InstructionsLoaded` | o anúncio de `activation_notice` e o `session_id` |
| `erro` e `resolvido` | `eventos.registrar_erro` e `eventos.resolver` | o `E-XX` e, no segundo, o destino |
| `levado` | `eventos.levado` | o `M-XX` e onde ele foi levado |

**Erros.** A saída 2 do `dc.py` — exceção de um handler ou erro de uso do `argparse` — é defeito do
método, e só ela vira `.claude/log/erros/E-XX.md`: o comando, o código, o fim da saída com o
traceback, o alvo, o `HEAD`, o working tree como links e a versão do plugin. Saída 1 é o gate
funcionando, e bloqueio pode ser acerto da regra: ficam só como evento. A numeração vem de
`erros/.ultimo`, que só cresce e que nada apaga.

**Validade.** O arquivo só recebe acréscimo, uma escrita por evento: os hooks rodam vários ao
mesmo tempo, e reescrever perdia eventos (medido no `0018`). O evento sai quando a revisão o lê:
`huddle-concluir` apaga os eventos até a última `huddle-pauta`, por posição — a única reescrita.
Evento com mais de 14 dias some da leitura e sai do arquivo nessa mesma reescrita. O `E-XX`
**só sai por resolução**, nunca por prazo: `dc.py log-resolver <E-XX> "<destino>"` o apaga, com
destino `H-XX` aberto no huddle da pessoa, `L-XX`, `método` ou `descartado: <motivo>`. Com 7 dias
sem resolução, ele aparece no aviso de abertura e na pauta do huddle. Nada se apaga à mão.

**Feedback ao método.** O que é sobre o próprio método, e não sobre o projeto, espera em
`.claude/log/metodo/M-XX.md` até a pessoa levá-lo ao repositório do método — à mão, porque o projeto
pode ser de terceiro, e envio por script pediria credencial e rede (plano `0018`, `D-09`). Chegam
lá dois caminhos:

| Origem | Como | O que o `M-XX` leva |
|---|---|---|
| Entrada do huddle | `huddle-fechar <H-XX> método`, texto genérico no stdin (codex, *Huddle*) | o texto, e a evidência só quando é `E-XX` ou `L-XX` — ids sem conteúdo; as outras três trazem nome do projeto e ficam de fora |
| Erro do log | `log-resolver <E-XX> método` — nunca automático: o erro só sai por resolução | cópia mecânica: o subcomando sem os argumentos, o código, o fim da saída e a versão. Ficam de fora o `HEAD`, o working tree e o alvo — também de dentro da saída, onde vira `<alvo>` |

Nos dois, o `M-XX` é gravado **antes** de a entrada fechar ou o `E-XX` sair; se a gravação falhar,
nada fecha. A raiz do projeto vira `<projeto>`, e o diretório da pessoa vira `~`. Só isso é
mecânico: nome de plano ou trecho de código no texto dependem da pessoa, que revisa cada `M-XX`
inteiro, frontmatter e texto, em `dc.py metodo-listar`. A pauta do huddle lista os pendentes. O
`M-XX` **só sai** por `dc.py metodo-levado <M-XX> "<onde>"`, que o apaga e registra o evento
`levado`; nunca por prazo. A numeração vem de `metodo/.ultimo`, como a do `E-XX`. Como o log, o
`M-XX` não é versionado e se perde com o clone — o preço de não pôr traceback no git.

No próprio repositório do método, levar é abrir ali um `H-XX` ou registrar um `L-XX` no plano a que
o defeito pertence, e então rodar `metodo-levado <M-XX> "<H-XX ou L-XX>"`.

**Contrato.** O log nunca muda o que já existia: o código de saída e o stderr do `dc.py`, e a
resposta dos hooks, são os mesmos com ou sem ele, e qualquer falha de escrita fica no próprio log.

## Porte medido — dado, não impressão

`plan_size` é o que o humano **declara** na aprovação. `docs/plan/system/porte-medido.md`
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
