---
# about
name: derive-handoff-prompt
type: plan
project: DecodeAndCode
description: O derive passa a gravar o prompt que orquestra a execução do plano numa sessão nova — e a disciplina de revisão, que hoje só existe num prompt escrito à mão, vira norma
tags: [decode-and-code, derive, handoff, cold-start, revisao]

# alvo
plan_id: "0003"
plan_size: médio
core: model
module: derive-handoff-prompt
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

# O derive entrega o prompt que orquestra o que ele derivou

## Objetivo

O `derive` termina entregando estrutura, unidades e backlog — e **nada que diga como conduzir a
execução daquilo**. Hoje essa ponte é feita à mão: alguém escreve um prompt, cola numa sessão nova,
e a qualidade do que vem depois depende inteiramente de quanto esse texto acertou.

**O dado que motiva o plano é esta sessão.** O prompt escrito à mão em 2026-08-27 conduziu a
execução das Fases 5, 6 e 7 do plano `0001` — sete unidades, cada uma revisada, **e cada revisão
achou algo que o relatório da execução não tinha visto**. O que produziu isso não foi zelo: foi um
parágrafo do prompt mandando *medir em vez de reler*, e sete lições de revisão que ele carregava.

Esse parágrafo não existe em lugar nenhum do repositório. Se a sessão fechar, ele some.

> **Duas coisas são o mesmo problema.** O `derive` não entrega o prompt, e o repositório não tem a
> disciplina que o prompt precisaria carregar. Resolver só a primeira produz um gerador de texto
> vazio; resolver só a segunda deixa a norma escrita e ninguém a lendo na hora certa.

## Solução

**O `derive` grava `_handoff.md` no diretório do plano**, e o modo reporta ao humano o que fazer com
ele. Só no **grande**: é o único porte que deriva unidades e executa em sessões separadas — médio e
pequeno rodam na mesma sessão e não têm ponte a construir. O arquivo é **projeção**, regerada a cada
`derive` incremental, e o prefixo `_` o mantém fora do padrão `NN-*.md` que conta unidades.

**A divisão entre script e julgamento segue a do resto do método:**

| Quem | O quê |
|---|---|
| **Script** | O esqueleto fixo, e todo número medido no instante da geração — commit, suíte pela **soma das duas linhas `Ran`**, unidades derivadas e verificadas, próximo número livre, caminhos resolvidos do `config.json` |
| **Julgamento** | A fila das unidades com suas dependências, as pendências que são do humano, e onde eu começaria — que é sugestão registrada, nunca pauta fechada |

**A disciplina de revisão vira seção da norma, e o prompt a cita.** O invariante 1 recusa a cópia:
o `_handoff.md` aponta para a norma, e quem lê abre — mesmo contrato de *Normas aplicáveis* na
unidade, que já funciona em cold-start. O que o prompt carrega inline é só o que é **deste plano**.

> **Número declarado envelhece, e o prompt precisa dizer isso de si mesmo.** O prompt que originou
> esta sessão trazia estado medido **e** mandava conferir o estado real contra o que ele afirmava.
> Foi a segunda metade que valeu: a sessão começou achando divergência. Um gerador que só
> despejasse números seria a `H-08` institucionalizada, com o agravante de ser automática.

## Tarefas

- [x] Escrever, na norma, a seção **Como revisar uma entrega** — medir em vez de reler, a suíte pela soma das duas linhas, lints contra artefatos reais, uma afirmação medida por outro caminho, verde não é evidência quando teste e critério saíram da mesma cabeça, mock prova a saída e nunca o comando, caracterizar antes de corrigir, separar sintoma de raiz
- [x] Escrever `handoff.py` com `gerar(dir_plano)` — esqueleto fixo mais os números medidos pelo oráculo do projeto, nunca por equivalente montado na hora
- [x] Fazer o `derive` gravar `_handoff.md` no diretório do plano, só no grande, regerando a cada execução
- [x] Descrever na `SKILL.md` o passo novo do `derive` e o que o modo diz ao humano depois de gravá-lo
- [x] Escrever `tests/test_handoff.py`: geração contra plano sintético, os números vindo do oráculo, o arquivo fora do padrão que conta unidades, e o caso contra o plano `0001` real
- [x] Registrar na norma que `_handoff.md` é projeção regerada, não documento editável à mão

## Independência

Entregando só este plano e parando, o sistema fica em estado válido: o `derive` continua fazendo
tudo o que já faz, e passa a deixar mais um artefato. Não há parte separável que entregue valor
sozinha — a seção da norma sem o gerador é conhecimento que ninguém lê na hora certa, e o gerador
sem a seção produz um prompt que aponta para o vazio.

## Oráculo

`tests/test_handoff.py`, e o gate de saída é do **plano**, não de unidade — é o que o porte médio
define.

O caso decisivo é contra a instância: `gerar` sobre o `0001` real produz um prompt cujos números
**batem com o que o oráculo do projeto responde no mesmo instante** — suíte, unidades, próximo
número livre. Fixture prova o esqueleto; só o caso real prova que os números vêm de medição e não
de literal (`L-31`).

E o caso contrário: com o plano ainda em desenvolvimento e com ele concluído, o prompt muda de
conteúdo — se não mudar, ele não está medindo.

## Decisões

| # | Decisão | Estado |
|---|---|---|
| D-01 | **Só o grande gera `_handoff.md`** | Médio e pequeno executam na mesma sessão em que foram aprovados — não há ponte entre sessões a construir, e gerar o arquivo lá seria promessa de um fluxo que aquele porte não tem |
| D-02 | **A disciplina de revisão vira norma, e o prompt cita** | O invariante 1 recusa a cópia. O precedente é a tabela *Normas aplicáveis* da unidade, que sobrevive ao cold-start por referência há 21 unidades |
| D-03 | **O arquivo é projeção, e o nome começa com `_`** | Regerado a cada `derive` incremental, como o backlog. O prefixo o mantém fora de `PADRAO_ARQUIVO_UNIDADE`, que é o que conta unidades em `numeracao` e em `porte` |

## Lacunas

| # | Lacuna | Por que fica registrada |
|---|---|---|
| L-01 | **Nada verifica se o prompt gerado de fato conduz bem uma sessão** | O teste alcança estrutura e números; que o texto produza uma orquestração boa é julgamento, e é a `L-01` do plano `0001` num lugar novo. O único dado que temos é esta sessão, com um prompt escrito à mão — amostra de um |
| L-02 | **A disciplina de revisão nasce de sete lições de uma sessão só** | Elas foram medidas, mas num único plano, com um único revisor. Vale escrever, e vale dizer que a base é estreita |
| L-03 | **A suíte não entra contada no prompt, contra o que a *Solução* listou** | **Divergência aberta e decidida na execução, em 2026-08-27.** A *Solução* listava a suíte entre os números medidos no instante da geração. Rodá-la dentro de `gerar` a faria rodar **dentro de si mesma** quando o teste deste módulo executasse — a recursão contra a qual `verificacao` mantém sentinela — e mockar a chamada nos devolveria ao defeito que a `L-28` registra: mock prova o parsing, nunca o comando. Entregue pelo contrato e não pela letra: o prompt carrega o **comando** e a regra de somar as duas linhas `Ran`, e quem lê mede. **Fortalece o desenho:** número congelado envelhece no primeiro commit, e um prompt cuja tese é *declaração é alegação* não pode abrir contradizendo-se |
| L-04 | **`gerar` quebrava para caminho fora da raiz do repositório** | **Aberta e corrigida na execução, em 2026-08-27, pelo caso contra a instância.** `Path.relative_to` levanta `ValueError` quando o caminho não está sob `lib.repo_root()`, e o caso que trabalha sobre uma cópia do plano `0001` em `tempfile` morria ali antes de escrever qualquer coisa. Corrigido com a mesma guarda que `porte._linhas_alteradas` já usa — relativo quando dentro, absoluto quando fora. **O achado é do caso real:** os sete casos sintéticos passavam, porque todos montam o plano dentro da raiz mockada |

## Fonte

- Sessão de 2026-08-27: execução das Fases 5, 6 e 7 do plano `0001` conduzida por prompt escrito à mão
- [`modelo-dev-units.md`](../system/modelo-dev-units.md), *Fluxo completo* e *Modo `derive`*
- `0001`, `L-31` — fixture prova o mecanismo, nunca a instância

## Backlog

<!-- backlog:start -->
- [x] Escrever, na norma, a seção **Como revisar uma entrega** — medir em vez de reler, a suíte pela soma das duas linhas, lints contra artefatos reais, uma afirmação medida por outro caminho, verde não é evidência quando teste e critério saíram da mesma cabeça, mock prova a saída e nunca o comando, caracterizar antes de corrigir, separar sintoma de raiz
- [x] Escrever `handoff.py` com `gerar(dir_plano)` — esqueleto fixo mais os números medidos pelo oráculo do projeto, nunca por equivalente montado na hora
- [x] Fazer o `derive` gravar `_handoff.md` no diretório do plano, só no grande, regerando a cada execução
- [x] Descrever na `SKILL.md` o passo novo do `derive` e o que o modo diz ao humano depois de gravá-lo
- [x] Escrever `tests/test_handoff.py`: geração contra plano sintético, os números vindo do oráculo, o arquivo fora do padrão que conta unidades, e o caso contra o plano `0001` real
- [x] Registrar na norma que `_handoff.md` é projeção regerada, não documento editável à mão

6 de 6 tarefas concluídas · atualizado em 2026-08-27
<!-- backlog:end -->
