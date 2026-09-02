# Criar um princípio

Versão 1.0.0 · guia de uso

[← Como usar o Decode And Code](../../README.md#como-usar-o-decode-and-code)

Guia de procedimento. As definições das camadas estão na norma
([`modelo-dev-units.md`](../plan/system/modelo-dev-units.md), seção *Camada normativa*) — aqui só o
**como**.

## Quando criar

Um princípio passa no teste que o separa de guideline: **uma equipe competente pode rejeitar isto e
ainda estar fazendo trabalho bom?** Se a resposta é **não**, é princípio. Se é **sim**, é guideline
— pare aqui e veja [`create-guideline.md`](create-guideline.md).

Princípio é a direção e o porquê, estável. Não se descobre em execução, e não muda por
conveniência: criar um é decisão deliberada, e rara.

## Onde fica

`principles.md` é **um arquivo só**, que carrega em toda sessão porque não declara `paths:`. Criar
um princípio é **adicionar uma seção** a
[`.claude/rules/principles.md`](../../.claude/rules/principles.md), nunca criar arquivo novo.

## Como criar

1. **Passa pelo modelo.** Princípio é norma — entra por um plano, como unidade de tipo `norma`
   (entrega prosa normativa), com **aprovação humana** registrada. Não se edita `principles.md`
   direto fora desse fluxo.
2. **Escreva a seção** no formato das que já existem:
   - `## <Nome do princípio>`
   - **Enunciado:** uma frase que diz o que o princípio afirma.
   - **Teste:** a condição verificável que decide se ele foi seguido.
   - **Na prática:** (opcional) o que ele proíbe ou obriga em casos concretos.
3. **Atualize a `description` do frontmatter** se o novo princípio muda o resumo — ela é o texto
   que o modelo lê para saber o que o arquivo carrega.
4. **Anti-drift.** Não repita o que a norma ou uma guideline já diz. O princípio referencia; não
   copia.

## Como validar

- `rules.lint_rule(<caminho>)` — frontmatter (`name`, `description` não vazios), ausência de
  `paths:` (é o que o mantém princípio), corpo não vazio.
- `rules.auditar_arvore()` — a árvore `.claude/rules/` + `.claude/rules-off/` inteira.
- Abrir uma **sessão nova** e conferir que `principles.md` aparece no log de ativação
  (`activation_notice.relatorio(<log>)`), com `load_reason=session_start`.

## Onde fica registrado

- O princípio em si: a seção em `principles.md`.
- A proveniência — por que existe, o que ficou de fora — no `## Decisões` do plano que o criou,
  como [`03-principles-rule.md`](../plan/model/0001-decode-and-code-foundation/03-principles-rule.md)
  fez para os atuais.

## O que não fazer

- **Não criar arquivo novo** em `.claude/rules/` para um princípio — ele carregaria como rule
  independente sem `paths:`; o lugar é uma seção em `principles.md`.
- **Não colocar `paths:`** — com escopo de arquivo, deixa de ser princípio.
- **Não editar `principles.md` fora de um plano aprovado** — é norma, e norma tem gate humano.
- **Nada específico de um projeto que instala vira princípio do método.** O `principles.md` deste
  repositório é a instância dele; um projeto que instala escreve os seus (o mecanismo viaja, o
  conteúdo não).
