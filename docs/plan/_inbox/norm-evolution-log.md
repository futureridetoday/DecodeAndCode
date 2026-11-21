---
# about
name: norm-evolution-log
type: plan
project: DecodeAndCode
description: Primeiro de seis planos do ciclo de evolução da norma — o log de uso em .claude/log/ do projeto, com eventos do dc.py, bloqueios de guardrail e carregamento de instrução em eventos.jsonl, e um E-XX por defeito do método que só sai por resolução; registra a visão e a ordem dos seis itens decididas pelo humano
tags: [decode-and-code, norma, huddle, log, guardrail, evolucao]

# alvo
plan_id: ""
plan_size: médio
plan_type: feature
core: model
module: norm-evolution-log
block: ""

# history
author: Claude
created: 2026-11-20
status: draft
version: 1.0.0
updated: ""
approved_by: ""
approved_at: ""

# system
scope: project
auto_load: false
dependencies: []
---

# Ciclo de evolução da norma — 1: o log de uso

> **Tipo proposto: `feature`** — mecanismo novo (módulo de log, comando `log-resolver`, o `dc.py` e
> dois hooks passando a registrar), com código e norma. **Porte proposto: `médio`** — pela *Quando
> cada porte cabe*, há passos (pergunta 1, não), e uma sessão os executa em sequência (pergunta 2,
> sim): nenhuma parte pede cold-start isolado. O humano confirma tipo e porte na aprovação.
>
> **Recorte.** O pedido nomeia seis itens, um por semana (`D-03`). Este esboço é o **item 1**; os
> itens 2 a 6 ficam em *Próximos planos*, cada um a nascer pelo `intake` depois de validado o
> anterior. O nome sugerido, `norm-evolution-cycle`, vira o prefixo da série (`P-05`).

## Objetivo

**Clarificar.** Defeito do próprio método (saída 2 do `dc.py`) e bloqueio de guardrail em uso real
não deixam registro: `dc.py.main` só imprime em stderr (`dc.py:725-731`), o hook `PreToolUse` só
responde ao Claude Code (`pre_tool_use.py`), e o log de ativação vai para `gettempdir()`, um por
sessão (`instructions_loaded.py:30`). O huddle e o repositório do método só sabem do que alguém
lembra de contar. **Métricas:**

- saídas 2 com registro: hoje 0, por construção. Alvo: todas, cada uma num `E-XX`;
- bloqueios de guardrail com registro: hoje 0. Alvo: todos, como evento;
- `E-XX` sem resolução há 7 dias ou mais que não aparece para a pessoa: alvo 0 — aviso de abertura e
  pauta do huddle o mostram.

**Beneficiário:** a pessoa, no huddle do projeto; e quem mantém o método, que hoje recebe defeito só
por validação manual — o `0013` precisou de quatro rodadas para achar C1 a C9.

**Evitar.**

| Alternativa | Por que não basta |
|---|---|
| Ler os transcripts do Claude Code (`~/.claude/projects/`), que já guardam cada chamada de Bash com a saída | Formato interno, sem contrato; fica fora do projeto, e a CLI os apaga por prazo. Não traz o `InstructionsLoaded`, nem o `HEAD` e o working tree no instante do erro |
| O modelo abrir `H-XX` quando um comando falha, pelos gatilhos do huddle | Depende de atenção: os cinco gatilhos não são observáveis por script (norma, *Despejo*), e a ressalva do humano diz o mesmo |
| Manter o log de ativação em `gettempdir()` | Some com a sessão; nada acumula para a contagem do item 5 |
| Gravar em `docs/`, versionado | Ruído no git a cada comando, e o `.gitignore` do projeto não se edita (`D-05` do `0009`) |
| Telemetria OpenTelemetry do Claude Code | Coletor externo que cada pessoa configura, com o dado fora do projeto e longe do huddle. Não medido se os eventos trazem o código de saída do `dc.py` e a regra que barrou |

**Reduzir.** Um módulo (`eventos.py`) com três operações — registrar evento, registrar erro,
resolver erro —; o `main` do `dc.py` e dois hooks chamando-o; um comando (`log-resolver`); e o que
já existe — aviso de abertura e pauta do huddle — passando a mostrar o log. Nada agrega, conta ou
exporta: isso é dos itens 2 e 5.

## Gates

| Gate | Resposta |
|---|---|
| **A — necessidade real** | **Sim, com base estreita, somada a exigência explícita do humano** (2026-11-20; protocolo de exceção, *exigência explícita*). **Medido:** a ausência de registro, nos três pontos de *Clarificar*; e o único defeito de guardrail conhecido — o falso positivo do `old_string`, C6 do `0013` — apareceu na validação manual, não num registro. **Não medido:** quantas saídas 2 e quantos bloqueios acontecem em uso real, aqui ou no AmFlow. É o que o log passa a medir, e o que responde o gate A dos itens seguintes |
| **B — mínimo viável** | Cortado: **itens 2 a 6**, cada um plano próprio, depois de validado o anterior (*Próximos planos*); **`E-XX` para saída 1 e bloqueio**, que ficam só como evento (`P-01`); **destino `método` no `log-resolver`** até o item 2 criar onde ele mora (`P-02`); **escrita do log em projeto que não adotou o método** (`P-03`); **contagem, agregação e exportação** (itens 2 e 5); **prazos configuráveis** — 14 e 7 dias são constantes; **registrar chamada de ferramenta em geral e pedido de permissão** — o C1 do `0013` fica fora; só `dc.py`, bloqueio e carregamento de instrução |

## Decisões

Tomadas pelo humano (Bortoli) em conversa em 2026-11-20. São decisões, não hipóteses. `D-01` a
`D-03` valem para a série inteira: os planos seguintes as citam daqui, sem copiar.

| # | Decisão |
|---|---|
| D-01 | **A norma evolui com o projeto.** Começa ampla, quase genérica; princípios, guidelines e guardrails são corrigidos, promovidos (guideline a princípio, por exemplo), combinados ou removidos, e o huddle sustenta essa evolução. Como o modelo domina mais ações a cada versão, e para o que ele domina regra ativada é mais eficiente que skill genérica, **o ciclo precisa remover regra, não só adicionar** |
| D-02 | **Aprendizado pelo contexto, sem fine-tuning**: o volume de um projeto não sustenta treino, e os pesos não são ajustáveis aqui. Regras são os parâmetros; sinais do uso, os dados; a decisão humana no huddle, o rótulo; promover, combinar, editar e remover, o passo de ajuste; o caso por regra, o conjunto de avaliação; o teto de princípios e o texto compacto, a regularização. **A peça que falta é a avaliação** |
| D-03 | **Seis itens, um por semana, nesta ordem: log; evidência e destino `método`; gatilho e retrospectiva; caso por regra; contagem; saúde da norma.** Começa pequeno, no tamanho do método, e valida cada item antes de escalar |
| D-04 | **O log mora em `.claude/log/` do projeto.** O script cria `.claude/log/.gitignore` com `*` na primeira escrita: a pasta se ignora sem editar o `.gitignore` do projeto, que a `D-05` do `0009` impede o setup de tocar |
| D-05 | **`.claude/log/eventos.jsonl`, uma linha JSON por evento, só acréscimo.** O `main` do `dc.py` registra comando, alvo (plano ou unidade), código de saída e data; o hook `PreToolUse` registra o bloqueio de guardrail, **nunca o conteúdo do `tool_input`**, que pode ter segredo; o hook `InstructionsLoaded` passa a gravar aqui. Os hooks que rodam em toda chamada seguem a restrição de desempenho (`0001`, *Restrições conhecidas*) |
| D-06 | **`.claude/log/erros/E-XX.md`, Markdown com frontmatter, um por erro**: comando e argumentos, código de saída, últimas linhas da saída com limite, plano ou unidade, commit `HEAD`, caminhos modificados no working tree (como links) e versão do plugin. Referências, não cópias |
| D-07 | **Três classes de sinal:** saída 1 (gate reprovou: sinal sobre unidade ou regra), saída 2 (exceção: defeito do próprio método) e bloqueio de guardrail (saúde da regra; por exemplo, o falso positivo do `old_string`, C6 do `0013`) |
| D-08 | **Validade.** Evento sai quando é consumido pela revisão do ciclo — `huddle-concluir` apaga o que foi lido —, com validade de 14 dias como rede de segurança. Erro só sai por resolução, nunca por prazo: `dc.py log-resolver E-XX "<destino>"` apaga o arquivo, com destino em `H-XX`, `L-XX`, `método` ou `descartado: <motivo>`. Com 7 dias sem resolução, o erro aparece no aviso do `SessionStart` e na pauta do huddle. Nada se apaga à mão |
| D-09 | **Item 2.** Entrada do huddle ganha campo de evidência — de onde veio: bloqueio, falha de gate, `L-XX`, achado de revisão, `E-XX`. Novo destino `método` no fechamento do huddle, para feedback ao próprio método; a saída 2 alimenta `método` direto; um comando lista as entradas `método` prontas para levar ao repositório DecodeAndCode. Envio **manual** e sem conteúdo específico do projeto, que pode ser de terceiro — o invariante "nada específico de projeto viaja" no sentido inverso. O AmFlow é o primeiro alimentador |
| D-10 | **Item 3.** Revisão sugerida pelo Claude a cada período de tempo **ou** evolução do projeto, o que vier primeiro. Tempo já existe (`reminder_days`); evolução é N planos fechados desde a última revisão, dado de `_planos.md` e `porte-medido.md`. Os sinais vêm da criação do plano, da revisão, da execução **e do resultado final**: retrospectiva curta quando um plano passa a `concluído` (lacunas `L-XX`, revisões com achado, bloqueios, porte declarado contra medido) |
| D-11 | **Item 4.** O par proibido/permitido do guardrail generaliza-se para guideline e princípio: situação, erro sem a regra, acerto com ela. Serve também para remover: roda-se o caso **sem** a regra e, se o modelo acerta sozinho, a regra sai |
| D-12 | **Item 5.** Um script lê `eventos.jsonl`: regras que nunca ativam, que nunca barram, que se sobrepõem |
| D-13 | **Item 6.** Saúde da norma é a segunda parte da skill `huddle` — um ritual só, sem cerimônia nova: podar, combinar e promover, com o caso de cada regra como prova de que nada se perdeu |

> **Ressalva do humano.** Os cinco gatilhos de escrita do huddle não são observáveis por script
> (norma, *Despejo*): a qualidade do sinal depende de quem escreve, e a retrospectiva no fecho do
> plano é onde a pessoa compensa.

### Pendentes de decisão

| # | Pergunta | Recomendação |
|---|---|---|
| P-01 | Quais classes geram `E-XX`? A `D-06` diz "um por erro" e a `D-07` define três classes | **Só a saída 2**, inclusive o erro de uso do `argparse`, que também sai com 2 e é levantado **antes** do `try` (`dc.py:726`): skill que escreve o comando errado é defeito do método. Saída 1 é o gate funcionando — o fluxo prevê reprovar, corrigir e rodar de novo —, e bloqueio pode ser acerto da regra; com `E-XX`, cada um pediria um `log-resolver`. Os dois ficam como evento, e a pauta os resume. O `E-XX` leva também o fim do traceback, que o `main` hoje suprime: é a evidência de que quem corrige o método precisa |
| P-02 | `método` como destino do `log-resolver` antes do item 2? | **Não; entra com o item 2.** `log-resolver` apaga o `E-XX`, e hoje nada guarda o que foi para `método`: a evidência sumiria antes de existir o comando que a leva ao repositório do método. Até lá, o destino é um `H-XX`, que o item 2 poderá fechar como `método` |
| P-03 | O log escreve em projeto que não adotou o método? | **Não.** Com o plugin no escopo de usuário, o `InstructionsLoaded` roda em todo projeto aberto (`L-10` do `0009`) e criaria `.claude/log/` em repositório que nunca pediu o método — o efeito colateral silencioso que o `0001` recusa (*Materializar não pode ser automático*). Condição: `<plan_root>/_planos.md` existe, a marca do bootstrap; um `stat`, compatível com hook |
| P-04 | `N` do gatilho de evolução (item 3) | **2 planos fechados** — recomendação do humano, pendente de confirmação. Decide-se no plano do item 3 |
| P-05 | Um plano ou seis, e o nome | **Seis, nesta ordem** (*Independência*). Este é `norm-evolution-log`; os seguintes levam o prefixo `norm-evolution-` |

## Tarefas

- [ ] Norma, seção nova *Log de uso* depois de *Huddle*: onde mora, o `.gitignore` que se cria sozinho, o formato do evento e do `E-XX`, as três classes, a validade e o `log-resolver`. *Validar a ativação* troca o caminho em `$TMPDIR` pelo `eventos.jsonl`, filtrado pela sessão, e `docs/recursos/hooks.md` também. A exceção ao *Materializar não pode ser automático* fica escrita: hook escreve só em `.claude/log/`, ignorado pelo git, e só em projeto com bootstrap (`P-03`)
- [ ] `eventos.py`, com teste: `registrar(projeto, evento)` acrescenta a linha, cria `.claude/log/` e o `.gitignore` na primeira escrita e descarta evento com mais de 14 dias; `registrar_erro(...)` escreve o próximo `E-XX.md` com os campos da `D-06` (`HEAD` e working tree por `git`, só nesse caminho; versão do `plugin.json`), e a numeração nunca reutiliza um id já resolvido; `resolver(projeto, id, destino)` confere o destino no vocabulário e apaga o arquivo. Nenhuma das três levanta para quem chama
- [ ] `dc.py.main`: registra o evento de toda chamada e, na saída 2, o `E-XX` — exceção do handler e erro de uso do `argparse` (`P-01`). Código de saída e stderr não mudam, e falha do log não muda nenhum dos dois
- [ ] `dc.py log-resolver <E-XX> "<destino>"`, com teste: `H-XX` presente no huddle da pessoa, `L-XX` ou `descartado: <motivo>`; qualquer outro sai com 1, sem apagar. Registra um evento `resolvido` com o destino
- [ ] Hooks: `pre_tool_use.py` registra `{classe: bloqueio, regra, tool_name, data}` só quando nega, sem nada de `tool_input`; `instructions_loaded.py` grava em `eventos.jsonl` com o `session_id`; `activation_notice.relatorio` lê de lá, filtrando a sessão. As docstrings que dizem "nada de I/O além da leitura" mudam junto
- [ ] Superfície: `session_start.aviso` acrescenta os `E-XX` com 7 dias ou mais, sem mudar a precedência do aviso de setup; `huddle.pauta` mostra esses `E-XX` e um resumo dos eventos desde o último huddle, por classe e comando; `huddle-concluir` apaga os eventos até a última `huddle-pauta`, que o próprio log registra. O passo 1 do `huddle/SKILL.md` cita o resumo
- [ ] `scripts/test-python.sh` verde, inteiro; `empacotar.verificar` e o ciclo instalado aprovam o pacote com `eventos.py`; `lint_skill` sem problema no `huddle`
- [ ] Remedição (*Remedição*)

## Oráculo

| Alvo | Como se sabe que funcionou |
|---|---|
| `eventos.py` | Teste: a primeira escrita cria a pasta com `.gitignore` `*`, e o `git status` do repositório de teste não a mostra; evento de 15 dias some na escrita seguinte; `E-XX` traz os campos da `D-06`; resolvido o `E-01`, o erro seguinte é `E-02`; destino fora do vocabulário é recusado sem apagar |
| `dc.py.main` | Teste: handler que levanta → saída 2, o mesmo stderr de antes e um `E-XX` com o traceback; erro de uso do `argparse` → `E-XX`; `.claude/log/` sem permissão de escrita → saída 2 do mesmo jeito |
| Hooks | Teste: o evento de bloqueio não contém nenhum valor de `tool_input`; projeto sem `_planos.md` não ganha `.claude/log/` (`P-03`) |
| Superfície | Teste: `aviso` com `E-XX` de 8 dias o menciona, com 6 não; `huddle-concluir` apaga só os eventos que a pauta mostrou |

## Remedição

Num projeto de prova com o pacote novo e o bootstrap feito: forçar uma saída 2 do `dc.py`, um
bloqueio de guardrail e uma sessão nova. Esperado: as três classes em `eventos.jsonl`, um `E-XX` com
traceback, `HEAD` e versão do plugin, `.claude/log/` fora do `git status`, e, com a data do `E-XX`
recuada 8 dias, o aviso de abertura e a pauta mencionando-o. Num projeto **sem** bootstrap, a mesma
sessão não cria `.claude/log/`.

## Próximos planos

Cada um nasce pelo `intake` depois de validado o anterior (`D-03`); o gate A de cada um se responde
com o dado do que veio antes.

| # | Plano | Item | Depende de | O que já se sabe |
|---|---|---|---|---|
| 2 | `norm-evolution-evidence` | `D-09` | este plano (`E-XX`, saída 2) | `P-02` se resolve aqui |
| 3 | `norm-evolution-trigger` | `D-10` | em parte deste (bloqueios na retrospectiva) | `P-04`. A transição para `concluído` já tem ponto de gancho: `backlog.projetar` chama `porte.registrar` nela |
| 4 | `norm-evolution-cases` | `D-11` | nenhum | **A base é metade do que se supõe:** `guardrail.adicionar` prova a regra pelo par e **descarta** o par — `.claude/guardrails.json` guarda só `nome`, `ferramenta`, `detector` e `mensagem`. E o caso de princípio não pode morar no texto do princípio, que carrega em toda sessão e que o esboço `setup-principles` quer compacto (`D-05` de lá) |
| 5 | `norm-evolution-count` | `D-12` | este plano | **Tensão com a `D-08`:** o evento sai no `huddle-concluir`, então a contagem enxerga no máximo o intervalo entre dois huddles, com teto de 14 dias. "Nunca ativa" numa janela dessas é sinal fraco; janela maior pede guardar um agregado, que a `D-08` não prevê |
| 6 | `norm-evolution-health` | `D-13` | 4 e 5 | — |

## Independência

**O teste da norma (*Avaliação de escopo*) separa os seis.** Este plano, entregue sozinho, deixa o
sistema válido e útil: os defeitos do método e os bloqueios passam a ter registro e a aparecer para a
pessoa. O item 4 também passa sozinho, porque não depende de log; os itens 2, 3, 5 e 6 dependem do
que vem antes. Dependência sequencial com objetivo único seria fase no mesmo plano, mas **a `D-03`
pede validar cada item antes de escalar**, e o desenho do seguinte pode mudar com o dado do anterior
(*Próximos planos*, linhas 4 e 5): desenhá-los agora, num plano só, fixaria decisão sobre premissa
ainda não medida. A ordem é do humano; o item 4 é o único que poderia andar antes.

**Concorrência.** Nenhum plano `em desenvolvimento` em `_planos.md`. No `_inbox`,
`setup-principles` e `setup-resources` também tocam o `dc.py` (um comando novo cada) e a norma, em
seções diferentes (*Camada normativa*, *Setup*): se algum deles entrar em desenvolvimento junto com
este, o `_parser` do `dc.py` é o ponto de colisão. O `apply-plugin-review` está desatualizado (`H-18`).

## Lacunas

| # | Lacuna | Detalhe |
|---|---|---|
| L-01 | **O ganho do log não tem medição antes do uso** | As métricas medem a cobertura do registro. Se ele muda alguma decisão só se vê no primeiro huddle com eventos, e no item 2 |
| L-02 | **Saída 1 e bloqueio, só como evento, somem no huddle seguinte ou em 14 dias** | Se `P-01` for aceita, um padrão de reprovação que atravessa dois huddles não deixa rastro. O item 5 é quem diz se isso faz falta |

## Fonte

- [`modelo-dev-units.md`](../system/modelo-dev-units.md), *Huddle*, *Camada normativa* (*Validar a ativação*), *Porte medido*, *Avaliação de escopo*, *Quando cada porte cabe*, *Fluxo completo*
- [`0009-onboard-new-project.md`](../model/0009-onboard-new-project/0009-onboard-new-project.md), `D-05` e `L-10`
- [`0013-fix-setup-validation.md`](../model/0013-fix-setup-validation.md), C6
- [`0001-decode-and-code-foundation.md`](../model/0001-decode-and-code-foundation/0001-decode-and-code-foundation.md), *Materializar não pode ser automático* e *Restrições conhecidas*
- [`setup-principles.md`](../model/0016-setup-principles.md), `D-05`
- `.claude/skills/decode-and-code/scripts/dc.py:725-731`, `huddle.py`, `guardrail.py`, `porte.py`, `backlog.py`, `activation_notice.py`; `.claude/hooks/pre_tool_use.py`, `instructions_loaded.py`, `session_start.py`; `.claude/skills/huddle/SKILL.md`

## Backlog

<!-- backlog:start -->
<!-- backlog:end -->
