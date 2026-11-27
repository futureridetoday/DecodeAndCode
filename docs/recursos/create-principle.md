# Criar um princípio

Versão 1.2.0 · guia de uso

[← Recursos](../../README.md#recursos)

Guia de procedimento. O que princípio, guideline e guardrail são, e as três portas que os gravam,
está no codex, seções *Princípio*, *Guideline*, *Guardrail* e *Rethink* (`dc.py codex <título>`) —
aqui só o **como**.

## Quando criar

Um princípio passa no teste que o separa de guideline: **uma equipe competente, trabalhando neste
projeto, pode rejeitar isto?** Se a resposta é **não**, é princípio do projeto. Se é **sim**, é
guideline — pare aqui e veja [`create-guideline.md`](create-guideline.md). O teste sem o recorte
"neste projeto" decide outra coisa, o que viaja no plugin; o codex, *Princípio*, traz o teste.

**Teto: 5 princípios no projeto, ideal 3.** Cada um carrega em toda sessão.

Princípio é a direção e o porquê, estável. Não se descobre em execução, e não muda por
conveniência: criar um é decisão deliberada, e rara.

## Onde fica

`principles.md` é **um arquivo só**, que carrega em toda sessão porque não declara `paths:`. Criar
um princípio é **adicionar uma seção** a
[`.claude/rules/principles.md`](../../.claude/rules/principles.md), nunca criar arquivo novo.

## Como criar

Três portas, todas com aprovação humana:

- **Pelo setup**, que sugere o north star, os princípios do método e, em projeto em andamento, os
  extraídos e os propostos. O aprovado na conversa é gravado por `dc.py criar-principio`
  (JSON `{nome, enunciado, teste}` pelo stdin), que escreve só *Enunciado* e *Teste*, recusa o sexto
  princípio e o nome repetido, e só grava o que passa em `rules.lint_rule`.
- **Pelo `rethink`**, depois de uma mudança de rumo do projeto ([`rethink.md`](rethink.md)).
- **Por plano**, no passo a passo abaixo.

1. **Passa pelo modelo.** Princípio entra por um plano do tipo `rule`, com **aprovação humana**
   registrada (o aceite do tipo `rule` é a aprovação). Não se edita `principles.md`
   direto fora das três portas.
2. **Escreva a seção** no formato das que já existem:
   - `## <Nome do princípio>`
   - **Enunciado:** uma frase que diz o que o princípio afirma.
   - **Teste:** a condição verificável que decide se ele foi seguido.
   - **Na prática:** (opcional) o que ele proíbe ou obriga em casos concretos.
3. **Atualize a `description` do frontmatter** se o novo princípio muda o resumo — ela é o texto
   que o modelo lê para saber o que o arquivo carrega.
4. **Anti-drift.** Não repita o que o codex ou uma guideline já diz. O princípio referencia; não
   copia.

## Como editar

Mesmo comando da criação, com `--replace`: `dc.py criar-principio --replace`, o JSON
`{nome, enunciado, teste}` pelo stdin. O princípio precisa existir; a seção é trocada **no mesmo
lugar**, com *Enunciado* e *Teste* novos, só se o arquivo passar em `lint_rule` — senão sai `1` e a
versão antiga fica. O teto não conta a versão antiga. *Na prática*, se havia, sai: fica no git.
Trocar o nome não é editar — é arquivar o antigo e criar o novo.

## Como arquivar

`dc.py archive principle "<nome>"`. A seção sai de `principles.md` e vai para
`.claude/archive/rules/principles.md`, com `archived_at`, `archived_by` e `reason`; a vaga no teto
volta. Arquivar **move, nunca apaga**: planos antigos podem citar o item. O motivo vai no stdin, e
`archived_by` é o `git config user.name`. O nome arquivado fica **reservado** — criar outro item com
ele sai `1` —, e a unidade que cita o arquivado passa a listá-lo em `Não resolvidas:` com
"arquivada em <data> por <quem>: <motivo>". Para trazer de volta, com o mesmo nome:
`dc.py restore principle "<nome>"`, que respeita o teto e o `lint_rule`. Codex, *Rethink* (editar e arquivar).

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
- **Não editar `principles.md` fora das três portas** — plano `rule` aprovado, setup ou `rethink` —, porque
  princípio tem gate humano.
- **Nada específico de um projeto que instala vira princípio do método.** O `principles.md` deste
  repositório é a instância dele; um projeto que instala escreve os seus (o mecanismo viaja, o
  conteúdo não).
