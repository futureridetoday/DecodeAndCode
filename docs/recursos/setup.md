# setup

Versão 1.0.0 · skill

[← Como usar o Decode And Code](../../README.md#como-usar-o-decode-and-code)

## O que é

A skill que conduz o **primeiro uso** do método num projeto: põe o plugin no escopo do projeto,
entende objetivo, escopo e stack, sugere guidelines e guardrails uma por vez, inicia o huddle da
pessoa e explica o método. Roda em Opus, na conversa principal (sem `context: fork`), porque a
ferramenta de perguntas não existe em subagente. O modelo pode propor e iniciar depois de ver o aviso
de abertura; o primeiro passo é sempre a confirmação de que o setup é desejado agora.

## Problema que resolve

O plugin carrega o **mecanismo**; `.claude/rules/` e `guardrails.json` são do projeto, e nada dizia
isso a quem instala. Os guias de criação moram em `docs/`, que não viaja no pacote, e pedem falha
observada ou incidente, que projeto novo não tem. Num time, cada pessoa podia ainda ter o plugin num
escopo diferente, ou nenhum, e trabalhar com normas diferentes.

## Como funciona

- **Aviso.** O hook `SessionStart` propõe o setup enquanto `<plan_root>/system/setup.md` não tem
  `completed_at` — mesmo com o plugin só no escopo de usuário. Nunca escreve; enquanto o setup está
  pendente, o aviso de huddle não aparece.
- **Etapas.** 0 pré-condições (bootstrap, plugin em `.claude/settings.json`); 1 perfil; 2 guidelines;
  3 guardrails; 4 huddle da pessoa; 5 o método, a partir de `dc.py explicar`; 6 `setup-concluir` e o
  fecho do huddle.
- **Uma sugestão por vez**, com **Aprovar**, **Editar** (livre ou guiada) ou **Rejeitar**. Nada é
  gravado antes do sim da pessoa.
- **Critério.** Guideline nasce da stack e do objetivo; guardrail, de decisão explícita do time que
  desvia do padrão da stack. O setup não sugere princípio: achado com essa cara vira entrada
  `observação` no huddle.
- **Estado.** `<plan_root>/system/setup.md`, versionado, com o perfil e uma linha por decisão.
  O setup é retomável: o que já foi decidido não volta.
- **Escreve só** no que o bootstrap cria, em `.claude/settings.json`, `.claude/rules/`,
  `guardrails.json`, `setup.md` e no huddle da pessoa. Nunca no `CLAUDE.md` nem no `AGENTS.md`.

## Como usar

- `/decode-and-code:setup` — percorre as etapas 0 a 6.
- Projeto que já tem rules, princípios ou guardrails: cada um é registrado como `existente`, e o
  setup segue só com o que é novo.
- Projeto com o arquivo de huddle da pessoa já criado: a etapa 4 só explica. Com o arquivo único
  antigo, propõe `dc.py huddle-migrar`.
- A conversa e as rules geradas seguem o idioma da pessoa.

## Exemplos de uso

- Ao abrir a sessão num projeto novo, o aviso diz que o setup está pendente. A pessoa roda
  `/decode-and-code:setup`; a skill habilita o plugin no projeto, confirma "design system em
  React com Tailwind", propõe "variantes com `cva`" como guideline e a pessoa aprova; propõe um
  guardrail para uma decisão do time e a pessoa rejeita. No fim, `setup.md` tem `completed_at`.

## Fundamentação

Norma, seção *Setup — o primeiro uso*, em [`modelo-dev-units.md`](../plan/system/modelo-dev-units.md).
Plano [`0009-onboard-new-project`](../plan/model/0009-onboard-new-project/0009-onboard-new-project.md).

## Limites

- **A sugestão é do modelo**: a qualidade depende do inventário e da confirmação do perfil.
- **O aviso só alcança quem abre o Claude Code.**
- **Cada colega instala o plugin uma vez por clone**; o escopo do projeto só declara a habilitação.
