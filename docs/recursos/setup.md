# setup

Versão 1.1.0 · skill

[← Recursos](../../README.md#recursos)

## O que é

A skill que conduz o **primeiro uso** do método num projeto: põe o plugin no escopo do projeto,
entende objetivo, escopo e stack, sugere princípios, guidelines e guardrails uma por vez, inicia o huddle da
pessoa e explica o método. Roda em Opus, na conversa principal (sem `context: fork`), porque a
ferramenta de perguntas não existe em subagente. O modelo pode propor e iniciar depois de ver o aviso
de abertura; o primeiro passo é sempre a confirmação de que o setup é desejado agora.

## Problema que resolve

O plugin carrega o **mecanismo**; `.claude/rules/` e `guardrails.json` são do projeto, e nada dizia
isso a quem instala. Os guias de criação moram em `docs/`, que não viaja no pacote, e pedem falha
observada ou incidente, que projeto novo não tem. Num time, cada pessoa podia ainda ter o plugin num
escopo diferente, ou nenhum, e trabalhar com guidelines e guardrails diferentes.

## Como funciona

- **Aviso.** O hook `SessionStart` propõe o setup enquanto `<plan_root>/system/setup.md` não tem
  `completed_at` — mesmo com o plugin só no escopo de usuário. Nunca escreve; enquanto o setup está
  pendente, o aviso de huddle não aparece.
- **Etapas**, na ordem do codex (*Setup*): 0 pré-condições (bootstrap, plugin em
  `.claude/settings.json`); 1 perfil; 2 huddle da pessoa; 3 princípios; 4 foundation (padrão de código
  e mapa de recursos, com a permissão de uso de cada recurso); 5 guidelines; 6 guardrails; 7 o método,
  a partir de `dc.py explicar`, `setup-concluir` e o fecho do huddle.
- **Uma sugestão por vez**, com **Aprovar**, **Editar** (livre ou guiada) ou **Rejeitar**. Nada é
  gravado antes do sim da pessoa.
- **Critério.** Princípio, no teto de 5 (ideal 3): o primeiro, tirado do objetivo; os demais, do que
  a pessoa diz que não se viola. Cada sugestão mostra o teste aplicado — uma equipe competente,
  trabalhando neste projeto, pode rejeitá-lo? —, e a que não passa cai para guideline. Guideline nasce
  da stack e do objetivo; guardrail, de decisão explícita do time que desvia do padrão da stack.
- **Estado.** `<plan_root>/system/setup.md`, versionado, com o perfil e uma linha por decisão.
  O setup é retomável: o que já foi decidido não volta.
- **Escreve só** no que o bootstrap cria, em `.claude/settings.json`, `.claude/rules/`,
  `guardrails.json`, na foundation (`<plan_root>/system/foundation.md`), em `setup.md` e no huddle da
  pessoa. Nunca no `CLAUDE.md` nem no `AGENTS.md`.

## Como usar

- `/decode-and-code:setup` — percorre as etapas 0 a 7.
- Projeto que já tem rules, princípios ou guardrails: cada um é registrado como `existente`, e o
  setup segue só com o que é novo. Princípio que o `CLAUDE.md` já afirma também: já carrega, não se
  copia.
- Projeto com o arquivo de huddle da pessoa já criado: a etapa 2 só explica. Com o arquivo único
  antigo, propõe `dc.py huddle-migrar`.
- A conversa e as rules geradas seguem o idioma da pessoa.

## Exemplos de uso

- Ao abrir a sessão num projeto novo, o aviso diz que o setup está pendente. A pessoa roda
  `/decode-and-code:setup`; a skill habilita o plugin no projeto, confirma "design system
  multimarcas em React com Tailwind, tokens vindos do Figma", propõe o north star "marca nova não
  exige código novo", com o teste "adicionar uma marca muda só tokens vindos do Figma", e a pessoa
  aprova; propõe "variantes com `cva`" como guideline e a pessoa aprova; propõe um
  guardrail para uma decisão do time e a pessoa rejeita. No fim, `setup.md` tem `completed_at`.

## Fundamentação

Codex, seções *Setup*, *Princípio*, *Foundation* e *Mapa de recursos do projeto*.
Plano [`0009-onboard-new-project`](../plan/model/0009-onboard-new-project/0009-onboard-new-project.md);
a etapa de princípios, plano [`0016-setup-principles`](../plan/model/0016-setup-principles.md).

## Limites

- **A sugestão é do modelo**: a qualidade depende do inventário e da confirmação do perfil.
- **O aviso só alcança quem abre o Claude Code.**
- **Cada colega instala o plugin uma vez por clone**; o escopo do projeto só declara a habilitação.
