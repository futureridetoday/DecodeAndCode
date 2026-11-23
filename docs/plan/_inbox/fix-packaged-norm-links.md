---
# about
name: fix-packaged-norm-links
type: plan
project: DecodeAndCode
description: A norma empacotada leva quatro links relativos para arquivos que o pacote não carrega — `empacotar` passa a reescrevê-los no build, e um teste prova que nenhum link relativo da norma empacotada fica sem alvo
tags: [decode-and-code, empacotamento, norma, links]

# alvo
plan_id: ""
plan_size: pequeno
plan_type: fix
core: model
module: fix-packaged-norm-links
block: ""

# history
author: Claude
created: 2026-11-23
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

# A norma empacotada para de levar links mortos

> **Tipo proposto: `fix`**: o pacote distribui um defeito medido. **Porte proposto: `pequeno`**: pela
> *Quando cada porte cabe*, é uma mudança só (pergunta 1, sim): uma função em `empacotar.py` e o
> teste que a prova. O humano confirma tipo e porte na aprovação. **[Claude]**
>
> **Autoria.** **[humano]** decisão do humano, **[Claude]** recomendação ainda não confirmada,
> **[medido]** fato medido, com o arquivo ou o comando.

## Objetivo

**Clarificar.** **[medido]** No build de 2026-11-23,
`dist/decode-and-code/skills/decode-and-code/reference/modelo-dev-units.md` tem sete links relativos
que não resolvem dentro do pacote. Três são exemplos dentro de blocos de código e não são defeito: `01-handler-auth.md` e
`02-search-catalog.md` (formato do backlog, `modelo-dev-units.md:747-748`) e
`<core>/0007-mcp/0007-mcp.md` (formato de `_planos.md`, `:1041`). Quatro são links reais:

| Linha da fonte | Link | Alvo no repositório |
|---|---|---|
| `modelo-dev-units.md:249` | `../../recursos/create-principle.md` | `docs/recursos/create-principle.md` (5.165 bytes) |
| `modelo-dev-units.md:387` | `../../recursos/create-guideline.md` | `docs/recursos/create-guideline.md` (5.943 bytes) |
| `modelo-dev-units.md:388` | `../../recursos/create-guardrail.md` | `docs/recursos/create-guardrail.md` (5.449 bytes) |
| `modelo-dev-units.md:1144` | `language-policy.md` | `docs/plan/system/language-policy.md` (5.409 bytes) |

**[medido]** Causa: `_fontes()` (`empacotar.py:106-116`) leva só `modelo-dev-units.md` como norma, e
`_copiar_norma` (`empacotar.py:232`) a copia para `reference/` sem tocar o corpo. O link morre duas
vezes: no pacote e na cópia que `bootstrap` materializa em `<plan_root>/system/` no projeto que
instala (`bootstrap.py:95-100`), onde nem `docs/recursos/` nem `language-policy.md` existem.

**[medido]** Remedido na revisão de 2026-11-23: `empacotar.construir` para um diretório temporário e
varredura de todo `.md` do pacote com a regex de `test_normas_system.py:33`, ignorando blocos de
código e links `http`, `mailto:` e `#`. Resultado: só os quatro links da tabela, todos em
`reference/modelo-dev-units.md`; nenhum `SKILL.md` nem outro `.md` do pacote tem link relativo sem
alvo.

**[medido]** O repositório não acusa, porque `test_normas_system.py:93`
(`test_todo_link_relativo_resolve_em_disco`) resolve os links da **fonte**, em
`docs/plan/system/`, onde os quatro alvos existem. Nenhum teste olha os links da norma **empacotada**.

**Métrica:** links relativos fora de bloco de código na norma empacotada que não resolvem dentro do
pacote: hoje 4; alvo 0.

**Beneficiário:** quem instala o plugin, que deixa de seguir um link que não abre; e a sessão do
Claude nesse projeto, que deixa de tentar ler um arquivo que não existe.

**Evitar.**

| Alternativa | Por que não basta |
|---|---|
| Empacotar os quatro alvos em `reference/` | Mais 21.966 bytes no pacote **[medido]**, e o link só volta a resolver no projeto que instala se o `bootstrap` também os materializar em `<plan_root>/system/`, com a árvore `../../recursos/` reproduzida. Abre uma lista de dependências da norma que alguém precisa manter, e os guias `create-*` são documentação do repositório para pessoas (`README.md:98`), não mecanismo **[Claude]** |
| Trocar por texto sem link na fonte | Resolve o pacote, mas quebra a navegação no repositório, onde os links funcionam e `test_normas_system.py` os prova **[Claude]** |
| Remover as citações | Quem instala perde a indicação de que os guias existem **[Claude]** |
| Corrigir só os quatro à mão | Nada impede o quinto: o próximo link relativo acrescentado à norma morre do mesmo jeito, sem teste que acuse **[Claude]** |

**Reduzir.** **[Claude]** Uma reescrita no build, no mesmo lugar e na mesma classe da reescrita de
`project:` (`_declarar_o_plugin`): a fonte continua honesta para o repositório, e o derivado se
corrige no build. Nenhum arquivo novo no pacote, nenhuma mudança no `bootstrap`.

## Gates

| Gate | Resposta |
|---|---|
| **A — necessidade real** | **[medido]** Quatro links mortos no pacote 2.4.0 distribuído, medidos no build de 2026-11-23. O defeito está no artefato que se publica, não numa hipótese |
| **B — mínimo viável** | **[Claude]** Cortado: verificar links de outros arquivos do pacote (`SKILL.md`, `hooks/`), porque a medição da revisão não achou link morto em nenhum deles **[medido]**, e entram quando um for medido (o mesmo critério do `.DS_Store`, `L-32`); empacotar os guias; mudar o `bootstrap`; mexer em `test_normas_system.py`, que continua provando a fonte. **Não cortado:** o teste sobre o pacote, porque sem ele o defeito volta no próximo link |

## Solução

**[Claude]** `_copiar_norma` passa o corpo da norma copiada por uma reescrita: **todo** link
markdown relativo fora de bloco de código vira URL absoluta do GitHub, presa à tag da versão (`D-01`). Link absoluto (`http://`,
`https://`, `mailto:`) e âncora pura (`#...`) passam intactos, e o que está dentro de bloco de código
também, porque é exemplo.

**Todo, e não só o que não resolve no pacote.** A norma é o único arquivo de `reference/`, e o
`bootstrap` a copia para `<plan_root>/system/` no projeto que instala (`bootstrap.py:86-100`). Um link
que resolvesse ao lado dela em `reference/` morreria na cópia. Por isso nenhum link relativo fica.

A regra é genérica, não uma lista dos quatro: o alvo se resolve a partir de `docs/plan/system/` na
fonte, vira caminho relativo à raiz do repositório, e o fragmento (`x.md#secao`) é mantido na URL.
Assim o quinto link já sai certo.

**Uma fonte para "bloco de código é exemplo".** Hoje a regra mora em `_sem_blocos_de_codigo`
(`test_normas_system.py:51`). A função passa para `empacotar.py`, que precisa dela em runtime de
build, e `test_normas_system.py` passa a importá-la de lá, em vez de manter uma cópia (invariante
"uma fonte por fato"). O comportamento não muda: a cerca de quatro crases em
`modelo-dev-units.md:1037-1043` não tem cerca interna, e não há link dentro de código inline na
norma **[medido]**.

Toca: `empacotar.py` (`_copiar_norma`, a função de reescrita e a de bloco de código),
`tests/test_empacotamento.py` e `tests/test_normas_system.py` (só o import). A fonte
`modelo-dev-units.md` não muda.

## Decisões

| # | Decisão | Autoria |
|---|---|---|
| D-01 | **O link reescrito vira URL absoluta do GitHub, presa à tag da versão** (`blob/v<versão>/...`), não texto sem link. Fecha o `P-01` | **[humano]**, 2026-11-23 |

### Pendentes de decisão

Todas **[Claude]**.

| # | Pergunta | Recomendação |
|---|---|---|
| P-01 | O link reescrito vira URL ou texto? | **Decidida em `D-01`: URL.** Recomendação original: **URL absoluta do GitHub, presa à tag da versão**: `https://github.com/futureridetoday/DecodeAndCode/blob/v<versão>/docs/recursos/create-guideline.md`, com a versão lida do `plugin.json`. Motivos: a pessoa que instala continua chegando ao guia; o conteúdo da tag é o que corresponde à norma daquela versão; e `verificar` já aceita o `repo` do marketplace, que retira do texto antes de buscar marcador de instância (`empacotar.py:356-364`) **[medido]**. **[medido]** A tag `v2.4.0` existe no `origin` e contém `docs/recursos/create-guideline.md`. **Custo em tokens:** cada URL tem 60 caracteres a mais que o link relativo, cerca de 240 caracteres no total, numa norma de 102.384 bytes: em torno de 0,2%, e só quando a norma é lida. **Alternativa:** texto sem link (`create-guideline.md`, no repositório do método), que tira cerca de 100 caracteres e não depende da tag existir, mas perde o caminho até o guia |
| P-02 | E se a tag ainda não existir quando o zip é construído? | **Aceitar.** O zip é asset do Release, e o Release é a tag: a URL resolve quando o pacote fica público. Entre o build e a publicação, ninguém instala. Se a ordem do release mudar, o teste não pega isso; fica registrado aqui |
| P-03 | `language-policy.md` (`:1144`) recebe o mesmo tratamento? | **Sim, pela mesma regra.** A frase descreve os scripts do próprio plugin (Python 3.10, stdlib, `unittest`), o que é verdade para quem instala também. Tratar por exceção seria uma segunda regra |
| P-04 | E os projetos que já instalaram (`L-02`)? | **Fora do escopo deste plano, registrado.** A correção chega a todo projeto que fizer o bootstrap depois dela. Quem já tem a cópia em `<plan_root>/system/` continua com os quatro links mortos depois do `/plugin update`, porque o `bootstrap` não sobrescreve a norma existente (`bootstrap.py:115-117`) e o `dc.py` lê primeiro a cópia do projeto (`dc.py:642`) **[medido]**. Como a norma do projeto se atualiza quando o plugin muda é uma pergunta maior que estes quatro links, e não cabe num `fix` pequeno |

## Lacunas

| # | Lacuna | Destino |
|---|---|---|
| L-01 | O esboço não dizia o que acontece com o fragmento de um link relativo (`x.md#secao`) | Resolvida nesta versão: a URL mantém o fragmento (*Solução*) |
| L-02 | Projetos que já instalaram não recebem a correção: a cópia da norma em `<plan_root>/system/` não é sobrescrita | Fora do escopo (`P-04`); fica como pergunta para um plano próprio sobre atualização da norma materializada |

## Oráculo

`tests/test_empacotamento.py`:

- `test_norma_empacotada_nao_tem_link_relativo`: depois de `construir`,
  `reference/modelo-dev-units.md` não tem nenhum link relativo fora de bloco de código. **Falha
  contra o código atual**, com os quatro links da tabela acima (a medir no início da execução, antes
  de mudar o código).
- `test_link_relativo_reescrito_aponta_para_a_tag_da_versao`: numa fonte sintética com um link
  `../../recursos/x.md#secao`, a cópia tem a URL com
  `blob/v<versão do plugin.json>/docs/recursos/x.md#secao` (`D-01`).
- `test_link_dentro_de_bloco_de_codigo_passa_intacto`: o exemplo `01-handler-auth.md` dentro de
  bloco cercado chega igual.
- `verificar() == []` sobre o pacote real continua passando, o que prova que a URL não é acusada como
  instância.

`test_normas_system.py` muda só no import da função de bloco de código e continua verde: a fonte da
norma não é tocada.

Critério de saída: suíte inteira verde (`bash scripts/test-python.sh`).

## Fonte

- Build de 2026-11-23, `dist/decode-and-code/skills/decode-and-code/reference/modelo-dev-units.md`,
  medido na análise de consumo de tokens da pasta `.claude/`
- `empacotar.py`: `_fontes` (`:106`), `_declarar_o_plugin` (`:221`), `_copiar_norma` (`:232`),
  `verificar` (`:338`)
- `bootstrap.py:86-100`, onde a norma sai de `reference/` para `<plan_root>/system/`
- `test_normas_system.py:51-104`, onde estão a regra de bloco de código e o teste de link da fonte
