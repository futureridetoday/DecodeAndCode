---
# about
name: packaging
type: doc
project: ""
description: O que o pacote do plugin leva e o que fica, como se audita, distribui e reconcilia, o bootstrap do projeto e o ciclo instalado que prova o pacote
tags: [manutencao, empacotamento, release]

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

# Empacotamento

Documentação de manutenção: serve a quem mantém o plugin, não ao método. O codex viaja no pacote e
nunca é copiado ao projeto (codex, *Restrição fundamental*).

## Empacotamento — o que o plugin leva, e o que fica

`empacotar.construir(destino)` produz a árvore do plugin **sempre a partir da fonte real**
(`lib.repo_root()`), nunca de um parâmetro de origem — o plugin é o que este repositório produz de
si mesmo. Viaja o manifesto (`.claude/plugin.json`, fonte única de nome e versão), as sete skills
(`lib.SKILLS`: os três modos — `review-plan`, `derive`, `implement` —, o `intake`, o `huddle`, o `setup` e o `rethink`) e a pasta
compartilhada `decode-and-code/` —
`scripts/`, `config.json` e, no pacote, `reference/` —, esta sem `scripts/tests/` nem `__pycache__`
(o que inclui `huddle.py` — o mecanismo do huddle viaja como qualquer outro script; a instância de
cada projeto, não), **três hooks** — `PreToolUse` (o guardrail), `InstructionsLoaded` (o log do
controle de três estados) e `SessionStart` (o lembrete do huddle, codex, *Huddle*) — com
`hooks/hooks.json` gerado a partir do bloco `hooks` do `settings.json` reduzido a esses três eventos (`_EVENTOS_DO_PACOTE`, a única lista; os scripts de
`hooks/` saem dos comandos deles) — a âncora `${CLAUDE_PROJECT_DIR}` reescrita para
`${CLAUDE_PLUGIN_ROOT}`, porque é essa variável que separa pacote de cópia —; o pacote não tem
`agents/`.

**Não viaja:** `.claude/rules/*` (guideline é instância do projeto), `.claude/guardrails.json`
(idem: a regra é do projeto que instala, só o mecanismo do hook viaja), `scripts/tests/` (prova
deste repositório, não componente do método), os **três scripts de desenvolvimento**
(`empacotar.py`, `reconciliar.py` e `lint_skill.py` — nenhum runtime nem hook os
importa, só os testes), o **hook de anúncio restante**
(`SubagentStart` — não chega ao modelo, e não há registro de projeto que instala o
plugin usando o controle de três estados; continua no `settings.json` daqui) e `docs/` (planos e
documentação são registro daqui — inclusive os arquivos de `docs/plan/system/huddle/`, que carregam a
conversa de cada pessoa deste projeto e são instância pura —); o codex viaja na pasta compartilhada e as skills o citam pelo título.
`empacotar.verificar(destino)` audita a árvore já
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

**Distribuir é a operação seguinte, e não cobra pacote no clone.** `empacotar.empacotar_zip(staging)`
zipa a árvore já construída e devolve `(caminho, sha256)`; o zip — `decode-and-code-<version>.zip` —
vira asset de um **GitHub Release**, e cada entrada do `marketplace.json` o referencia por
`source: { "source": "archive", "url": "<https>", "sha256": "<64 hex>" }`. O Claude Code baixa o zip
dessa URL e confere o hash a cada instalação: nada precisa existir de antemão no repositório
clonado, e `dist/decode-and-code/` — o `destino` default de `construir` — permanece **staging
gitignorado**, junto de `*.zip`. Publicar é ato humano: constrói, zipa, sobe o asset ao Release, e
copia `url`/`sha256` para o `marketplace.json`.

> **Os dois papéis do repositório de origem separam-se por diretório, e o `.claude-plugin/` da raiz
> é do marketplace.** O manifesto do plugin é **fonte**, e mora junto das outras fontes que
> `construir` copia (`.claude/plugin.json`); o `.claude-plugin/plugin.json` existe só **dentro do
> pacote**, escrito pelo build. Tê-lo na raiz declarava a raiz como plugin — e a raiz não tem
> `skills/` nem `hooks/` ao lado, só `.claude/`. `claude plugin validate` aprovava assim mesmo,
> porque valida o manifesto, não o que ele promete: quem instalasse da raiz teria um plugin válido
> que carrega nada.

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
destino se ele já existir — nunca sobrescreve guideline em silêncio. O plugin não embarca catálogo de
guideline nenhum; quem instala escolhe o que materializar.

## Reconciliação — divergência por conteúdo, nunca por versão

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

## Bootstrap — o chão que o ciclo pressupõe

O ciclo do método assume uma estrutura já existente. Num projeto que acabou de instalar
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
instala**, não estrutura do método — o projeto escreve o script do seu runner no caminho que o mapa
`runners` declara, relativo à raiz. O mapa (extensão → script) vem do `config.json` do plugin, hoje
`.py` e `.ts`; o projeto não o estende, e o gate de saída recusa teste de extensão fora dele
(*"extensão de teste sem runner declarado"*). A config de projeto que o estenderia está desenhada e
adiada no plano `0011-fix-norma-config-claims`, *Desenho adiado*.
Criar um na casa de quem instala seria feature além do pedido, e é o invariante 2 aplicado à
operação que mais tenta violá-lo: a que escreve num projeto alheio.

### Por que o projeto chega por parâmetro

`iniciar` recebe `projeto`; não o resolve. **Resolver a raiz aqui seria circular** — antes do
bootstrap o projeto não tem as marcas que `lib.repo_root()` procura, e são exatamente as marcas que
esta operação vai criar. Toda outra operação do método pode se ancorar porque roda depois; esta é a
que roda antes.

O `plan_root` continua vindo do `config()`, componível com a entrada — `projeto /
lib.config()["plan_root"]` —, então o bootstrap honra a configuração sem precisar da âncora.

## Ciclo instalado — a prova de que o pacote funciona, não só o código

O resto deste documento descreve o mecanismo; nada nele garante que o mecanismo **funciona
depois de empacotado**. Um teste próprio fecha essa lacuna: constrói o pacote de verdade — fora do
checkout, pelo mesmo `construir` que qualquer instalação usa —, carrega os módulos **dessa árvore**,
por caminho explícito, e percorre bootstrap → aprovação → gate de entrada → gate de saída →
fechamento contra um projeto que nunca existiu antes daquele instante.

### O que prova

| Passo | O que fica provado |
|---|---|
| Módulos carregados do pacote | O `__file__` de cada um resolve dentro da árvore construída, nunca do checkout — importar do checkout provaria o código, nunca o pacote |
| Bootstrap num diretório vazio | A estrutura chega ao projeto que instala |
| Aprovação | Numeração, movimentação e a linha em `_planos.md` funcionam a partir do pacote |
| Gate de entrada | `lint_unidade` aceita o que o ciclo real produz, não só uma fixture isolada |
| Gate de saída | `verificacao` roda o runner que o **projeto** declara — não um mock de `subprocess` — e projeta `state`/`verified_at` a partir do resultado real |
| Fechamento | `backlog.projetar` fecha a situação e registra o porte, sem nenhuma chamada real a `git` |
| Caso negativo | Sem o bootstrap, a aprovação falha — o defeito que motivou este mecanismo, preso num teste em vez de redescoberto por alguém |

### O que fica fora

**Derivação não entra.** Decidir a fatia de uma unidade é julgamento da skill, não passo de script —
não há oráculo determinístico para isso, e forçar um criaria um teste tautológico, que confere o que o código
faz em vez do que o critério pede (codex, *Teste*).

**A instalação real continua sendo ato humano.** A sessão que carrega um plugin instalado é
interativa por natureza — nenhum script a substitui —, então o ciclo instalado prova o **mecanismo**
de ponta a ponta; que uma sessão de verdade carrega o pacote continua sendo medição reportada, não
gate automático. Pela mesma razão, o ciclo não prova que o agente que invoca a skill traz o método
junto — só que o método, uma vez carregado, opera corretamente.

**Se a fronteira entre o que viaja e o que fica está no lugar certo é julgamento sobre conteúdo, não
estrutura.** O ciclo instalado confere que o mecanismo funciona; não confere que a metade certa dele
foi para o lado certo da divisão entre o que é mecanismo e o que é registro de um projeto.
