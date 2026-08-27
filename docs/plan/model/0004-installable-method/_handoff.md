# Orquestração — plano 0004-installable-method

Você orquestra a execução deste plano. **Você não executa unidade** — unidades rodam em cold-start
próprio, uma por vez. Você prepara, revisa o que volta, e versiona depois de revisar.

## Regras que não mudam

- **Aprovação é do humano.** Nenhum `derive` sem ele dizer, explicitamente, para aquele alvo
- `state` e `verified_at` **nunca se editam à mão** — são projetados por script a partir do teste
- **Nunca editar o miolo entre marcadores** (`<!-- backlog:start -->`, `<!-- planos:start -->`)
- Quem executa unidade **entrega arquivos e relatório, não commita**
- Unidade insuficiente é defeito **da unidade**: a correção volta para quem deriva, como `L-XX`
- Ação irreversível ou que toque mais de 5 arquivos: apresentar antes, aguardar aprovação
- **Todo número que este prompt afirma é alegação.** Meça com o oráculo do projeto, nunca com um
  equivalente montado na hora

## Como revisar — leia antes da primeira entrega

`docs/plan/system/modelo-dev-units.md`, seção *Como revisar uma entrega*. Ela é a parte que decide a qualidade do que sai, e
não está copiada aqui de propósito: uma fonte por fato.

O que ela exige em uma linha: **medir em vez de reler o relatório**.

## Estado no momento em que este arquivo foi gerado

Gerado em 2026-08-27, sobre o commit `f52a6f1`. **Confira antes de agir** — se divergir do que
você medir, o que vale é a sua medição, e a divergência merece ser reportada.

| | |
|---|---|
| Unidades derivadas | 5 |
| Verificadas | 0 |
| Próximo número livre | 06 |

A suíte **não** está contada aqui, e é deliberado: número declarado envelhece no primeiro commit.
Rode você mesmo, e **some as duas linhas `Ran`** — o total é a soma, nunca a última linha:

```
./scripts/test-python.sh
```

## A fila

| Ordem | Unidade | Depende de | Por quê |
|---|---|---|---|
| 1 | `0004-01` project-anchor | — | Destrava as outras quatro. Enquanto ela não entra, todo script que resolve caminho morre num plugin instalado |
| 2 | `0004-02` project-bootstrap | `01` | Sem a âncora, o caso que liga o bootstrap ao `numeracao` só existe com mock |
| 3 | `0004-03` norm-split | — | **Não depende de código nenhum.** Precede a `04` porque empacotar antes de dividir faria o pacote sair sujo uma vez |
| 4 | `0004-04` package-carries-norm | `02`, `03` | Estende o bootstrap e leva a norma já dividida |
| 5 | `0004-05` installed-cycle-proof | todas | Percorre o ciclo com o que as quatro entregaram |

**A `03` é a única que pode sair de ordem** — é markdown, sem dependência técnica. Se houver sessão
sobrando, ela roda ao lado da `01`/`02`. As outras quatro são estritamente sequenciais.

**A `04` é a maior:** 9 arquivos, dois deles movidos (`move-md.py` e seu teste, de `scripts/` para
dentro da skill). Vale mais atenção na revisão do que as outras.

## Pendências do humano

| # | Pendência | Natureza |
|---|---|---|
| `L-01` | Invocar `@decode-and-code:planner` numa sessão de pacote e reler o log de ativação, para saber se `skills:` carrega de verdade | Ato humano — não cabe em gate |
| — | A prova final de instalação: `claude --plugin-dir` abre sessão interativa, e nenhuma sessão do Claude a executa por dentro | Ato humano, reportado |
| `L-04` | Decidir onde mora o config de projeto. Hoje `config.json` viaja com o plugin, então quem instala não consegue mudar `plan_root` nem `runners` | Decisão de desenho — **fora do escopo deste plano**, por decisão registrada |
| `L-02` | Julgar se a fronteira entre mecanismo e registro ficou no lugar certo, depois que a `03` entregar | Julgamento — o teste não alcança |

Carregadas do plano `0001` e ainda abertas: `L-30` (a suíte escreve em
`.claude/rules/registry.json`, o que obriga `git add` explícito), `L-33` (`unit_type: norma` nunca
usado), `L-34` (`tools:` sem granularidade de caminho). E os itens `B-01`, `B-02`, `B-03` e `B-05`
do backlog do `_inbox`.

## Onde eu começaria, e por quê

**Começaria pela `0004-01`, e não é por ser a primeira da tabela.** É a única cujo defeito está
medido e reproduzível hoje — `RuntimeError` nomeado, 14 scripts afetados, `scaffold` morrendo no
import —, e todo o resto do plano é inalcançável até ela entrar. É também a menor: uma função, três
casos de teste. Isso a torna a maneira mais barata de confirmar que a sessão de execução está
funcionando antes de gastar contexto nas unidades grandes.

**O ponto de atenção da `01` não é o código, é a regressão.** A função que ela altera tem 14
chamadores e o gate roda só `test_lib.py`. Some as duas linhas `Ran` da suíte inteira antes de
aceitar a entrega — verde no gate dessa unidade prova pouco.

**A `0004-05` é a que muda o método**, e é a última por construção. Quando ela passar, *"o pacote
instala"* deixa de ser algo que alguém precisa lembrar de testar.

> Sugestão registrada, não decisão. Quem escolhe a ordem é o humano.

## Onde ler, antes de qualquer coisa

1. `.claude/CLAUDE.md` — invariantes e protocolo
2. `docs/plan/system/modelo-dev-units.md` — a norma
3. `.claude/skills/decode-and-code/SKILL.md` — os três modos
4. `docs/plan/model/0004-installable-method/0004-installable-method.md` — o plano, com *Escopo*, *Decisões* e *Lacunas*
