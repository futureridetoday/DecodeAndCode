---
# about
name: DecodeAndCode
type: doc
project: DecodeAndCode
description: Plugin Claude Code que carrega o método decode-and-code — norma em camadas, porte de plano e o ciclo plano → unidade → cold-start
tags: [decode-and-code, plugin, claude-code, norma, dev-units]

# history
author: Bortoli
created: 2026-08-22
status: draft
version: 1.0.0
updated: 2026-08-22

# system
scope: project
auto_load: true
dependencies: []
---

# DecodeAndCode — Instruções do Projeto

## O que é

Plugin Claude Code que empacota o método **decode-and-code**: a norma em camadas (princípio,
guideline, guardrail), o porte de plano, e o ciclo `plano → unidade → cold-start` que o antecede.

Origem: a skill `dev-units` do AmFlow, medida funcionando — 15 de 15 unidades executadas por Sonnet
em sessões novas, sem uma pergunta sobre conteúdo de unidade. Os **scripts e testes migraram**; a
camada normativa nasce aqui, sem as premissas do AmFlow.

## Relação com o AmFlow

Os dois repositórios têm papéis distintos, e confundi-los é o que produz drift:

| Repositório | Papel |
|---|---|
| `DecodeAndCode` | Onde o método é **desenvolvido**. Única cópia editável |
| `AmFlow` | Onde o método é **provado**. Primeiro consumidor real, e campo de prova das guidelines e guardrails — é lá que existem os incidentes registrados |

A skill `dev-units` do AmFlow está **congelada desde 2026-08-22**: somente uso, nenhuma escrita.
Correção descoberta durante o desenvolvimento entra aqui. Se o AmFlow precisar dela antes da
conclusão, entra lá como cherry-pick registrado como tal.

> **Por que o campo de prova fica no AmFlow.** Guardrail e guideline se escolhem por evidência de
> falha, não por elegância. Repo novo é greenfield e não tem incidente nenhum — as unidades entregam
> o **mecanismo** aqui e a **instância de prova** contra o AmFlow.

## Mapa do repositório

| Caminho | O que vive aqui |
|---|---|
| `.claude/skills/decode-and-code/` | A skill e seus scripts — todo determinismo |
| `.claude/rules/` | A camada normativa: princípio (sem `paths:`) e guideline (com `paths:`) |
| `docs/plan/` | Planos e unidades — destino de todo trabalho novo |
| `docs/plan/system/` | Fundação: norma, política de linguagem, `huddle.md` |

## Invariantes não negociáveis

1. **Uma fonte por fato.** Norma citada em dois lugares é drift esperando acontecer
2. **Nada específico de projeto viaja no plugin.** Guardrail e guideline são do projeto que instala;
   o plugin carrega o mecanismo, nunca a instância
3. **`state` e `verified_at` nunca se editam à mão** — são projetados por script a partir do teste
4. **Nunca editar o miolo entre marcadores** (`<!-- backlog:start -->`, `<!-- planos:start -->`) — é
   projeção, e será sobrescrita
5. **Português brasileiro** na documentação; identificadores em inglês

## Este arquivo fica pequeno, e é de propósito

O alvo documentado do Claude Code é **200 linhas** — acima disso a aderência degrada. O `CLAUDE.md`
do AmFlow chegou a 458, e esse é um dos fatos que originaram este projeto.

Princípio vai para `.claude/rules/` sem `paths:`. Norma com escopo de arquivo vai para
`.claude/rules/` com `paths:`. Procedimento vai para skill. **Aqui fica só o que precisa estar em
toda sessão e não cabe em nenhum dos três.**

## Protocolo de execução

- **Aprovação antes de executar.** Apresentar o plano, aguardar confirmação, só então agir
- **Escopo exato.** Só o que foi pedido; qualquer adição exige aprovação prévia
- **Leitura nunca precisa de confirmação** — `Read`, `git status`, `git log`, `ls`, `find`, `grep`
- **Comando explícito é a aprovação.** "crie o arquivo X" executa na ordem e no escopo exatos
- **Apresentar antes de executar** quando a ação é irreversível (deletar, push, deploy) ou afeta mais
  de 5 arquivos
- **Ambiguidade:** declarar o entendimento em uma frase e aguardar. Nunca assumir e executar

### Trabalho novo passa pelo modelo

| # | Etapa | Quem |
|---|---|---|
| 1 | Plano nasce em `docs/plan/_inbox/` | Opus |
| 2 | Revisão | Opus |
| 3 | **Aprovação** | **humano** |
| 4 | Derivação | Opus |
| 5 | Implementação, uma unidade por vez em cold-start | Sonnet |

Quem executa uma unidade **entrega arquivos e relatório, não commita**. Se a execução revelar que a
unidade estava insuficiente, a correção é **da unidade**, registrada como lacuna `L-XX` no plano.

## Simplicidade primeiro

Código mínimo que resolve o problema. Sem features além do pedido, sem abstração para uso único, sem
configurabilidade não solicitada. Se 200 linhas podem ser 50, reescrever.

Ao editar código existente: tocar só o necessário, seguir o estilo que está lá, não refatorar o que
não está quebrado. Código morto não relacionado se **menciona**, não se deleta.

## Anti-alucinação

Verificar antes de afirmar — nenhuma informação declarada sem evidência da sessão atual. Citar
`arquivo:linha`. Quando faltam dados: listar as fontes consultadas, declarar *"não encontrei
evidências de..."* e pedir o input mínimo. Proibido inventar arquivo, função ou flag.

## Linguagem

Scripts em **Python 3.10** (versão do Cowork), **stdlib pura**. Dependência externa não é proibida,
mas exige fallback declarado.

Quando a lógica for previsível e repetível, ela vira **código**, não instrução em markdown —
markdown depende de interpretação e pode ser ignorado; código executa de forma determinística e
testável. Markdown fica com o que exige julgamento, tom ou raciocínio contextual.

## Uso de ferramentas

- Leitura com `Read`, edição com `Edit`, criação com `Write`. Nunca `echo >` nem `cat <<EOF`
- Bash só para o que é exclusivo de shell. Sempre paths absolutos, nunca flags interativas
- Chamadas independentes em paralelo; dependentes em sequência, nunca com placeholder
