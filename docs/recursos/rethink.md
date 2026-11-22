# rethink

Versão 1.0.0 · skill

[← Como usar o Decode And Code](../../README.md#como-usar-o-decode-and-code)

## O que é

A skill que **repensa a norma do projeto** depois de uma mudança de rumo: revisa cada princípio,
guideline e guardrail que existe — **Manter**, **Editar** ou **Arquivar** —, sugere os novos e
registra cada decisão. Roda em Opus, na conversa principal (sem `context: fork`), porque a ferramenta
de perguntas não existe em subagente. Só a pessoa a invoca: `/decode-and-code:rethink`.

**Não atualiza o plugin.** Trocar a versão do método é `/plugin update` (README, *Atualização*); o
`rethink` revisa a norma **do projeto**.

## Problema que resolve

Quando o projeto muda de rumo — outro objetivo, outra marca, outro público —, princípios, guidelines
e guardrails continuam dizendo o rumo antigo em toda sessão. Rodar o setup de novo não revisa: ele
pula o que já foi decidido e só cria. Os escritores só criavam, e editar ou tirar um item da norma
pedia um plano por item, ou edição à mão, que a norma proíbe para princípio.

## Como funciona

- **Pré-condição.** O setup concluído (`setup.md` com `completed_at`); sem ele, a skill manda para o
  `setup`.
- **Passo 0 — o que mudou.** Vem no argumento do comando, ou numa pergunta. `rethink-start` abre a
  seção do dia no histórico.
- **Passo 1 — perfil.** Se o objetivo, o escopo ou a stack mudou, o perfil do `setup.md` é reescrito
  por `setup-perfil`. Objetivo novo pede north star novo, o primeiro item da revisão.
- **Passo 2 — os existentes.** Na ordem princípios → guidelines → guardrails, um por vez:
  - **Manter** — nada muda na norma.
  - **Editar** — o mesmo comando da criação, com `--replace`: mesmo nome, mesmo lugar, validado antes
    de a versão antiga sair.
  - **Arquivar** — `dc.py archive`, com o motivo: o item sai do que o Claude Code carrega e vai para
    `.claude/archive/`, com data, autor e motivo. Nada se apaga, e o nome fica reservado.
- **Passo 3 — os novos.** Lendo o projeto e o que foi decidido, sugere itens novos para as três
  camadas, com **Aprovar**, **Editar** ou **Rejeitar** e o critério do setup. O que foi **rejeitado**
  antes pode voltar, mostrando quando e por quê; o **arquivado** que volta a valer também, por
  `dc.py restore`, com o mesmo nome.
- **Histórico.** `<plan_root>/system/rethink.md`, versionado, uma seção por `rethink` e uma linha por
  decisão — `mantido`, `editado`, `arquivado`, `restaurado`, `criado` ou `rejeitado` —, gravada na hora
  por `rethink-record`. Nada o carrega em contexto.
- **Escreve só** em `.claude/rules/`, `.claude/archive/`, `guardrails.json`, no perfil do `setup.md`,
  no `rethink.md` e no huddle da pessoa. Nunca no `CLAUDE.md` nem no `AGENTS.md`.
- **Fecho.** Como as outras skills que registram, termina pelo fecho do huddle.

## Como usar

- `/decode-and-code:rethink <o que mudou>` — com o rumo novo no argumento.
- `/decode-and-code:rethink` — sem argumento, a skill pergunta o que mudou.
- Para editar ou arquivar um item fora de uma mudança de rumo, os comandos do `dc.py` rodam direto:
  *Como editar* e *Como arquivar* em [`create-principle.md`](create-principle.md),
  [`create-guideline.md`](create-guideline.md) e [`create-guardrail.md`](create-guardrail.md).

## Exemplos de uso

- Um app iOS nasceu com marca azul, design sóbrio e o objetivo de ajudar a economizar; passa a ter
  marca laranja, design divertido e o objetivo de ajudar a pessoa a ser consciente das escolhas de
  compra. A pessoa roda `/decode-and-code:rethink marca laranja, design divertido, objetivo:
  consciência das escolhas de compra`. A skill reescreve o perfil; edita o north star, com o mesmo
  nome; propõe arquivar a guideline da paleta azul, e a pessoa aprova com o motivo "marca laranja";
  mantém o guardrail; sugere uma guideline de paleta laranja. A unidade que citava a paleta azul
  passa a listá-la em `Não resolvidas:` com "arquivada em … por …: marca laranja", e o `rethink.md`
  guarda a seção do dia.

## Fundamentação

Norma, seções *Rethink* e *Camada normativa → Editar e arquivar*, em
[`modelo-dev-units.md`](../plan/system/modelo-dev-units.md). Plano
[`0020-add-norm-rethink`](../plan/model/0020-add-norm-rethink.md).

## Limites

- **A sugestão é do modelo**: a qualidade depende do que a pessoa diz que mudou e do inventário.
- **Não dispara sozinho**: sugerir quando rodá-lo é outro plano da série `norm-evolution`.
- **Não renomeia**: trocar o nome é arquivar e criar.
- **O guardrail arquivado perde a prova**: para restaurá-lo, um par proibido/permitido novo.
