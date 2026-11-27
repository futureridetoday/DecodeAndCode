# Criar uma guideline

Versão 1.1.0 · guia de uso

[← Recursos](../../README.md#recursos)

Guia de procedimento. O que princípio, guideline e guardrail são, e as três portas que os gravam,
está no codex, seções *Princípio*, *Guideline*, *Guardrail* e *Rethink* (`dc.py codex <título>`) —
aqui só o **como**.

## Quando criar

Uma guideline **se escolhe por evidência de falha, não por elegância.** O gatilho é a **primeira
divergência observada entre duas execuções** — duas sessões fizeram a mesma coisa de formas
diferentes porque nada dizia qual era a certa. Não é uma data no calendário, e não é "seria bom
ter".

Se a regra passa no teste do princípio (*ninguém competente rejeitaria*), é princípio, não
guideline — veja [`create-principle.md`](create-principle.md). Se ela é *procedimento que alguém
invoca* em vez de *regra que ativa sozinha ao tocar um arquivo*, é skill.

## No primeiro uso

No `/decode-and-code:setup`, o projeto ainda não tem falha observada, e o critério muda: a guideline
nasce da **stack e do objetivo** do projeto, escopada pelos caminhos onde vale. O que o `CLAUDE.md`,
o `AGENTS.md` ou um linter já impõe não vira guideline. Caminho que ainda não existe se grava já,
com `aguardando: true`. Depois do primeiro uso, vale o critério acima.

## Onde fica

Um arquivo por guideline em [`.claude/rules/`](../../.claude/rules/) — `.claude/rules/<nome>.md`.
Desligada, vai para o diretório irmão `.claude/rules-off/`, fora do que o Claude Code carrega.

## Como criar

Pelo comando, do diretório do projeto — ele escreve o frontmatter, roda o lint e registra:

```bash
dc.py criar-guideline <<'FIM'
{"nome": "<nome>", "descricao": "<quando vale>", "paths": ["<glob>"], "corpo": "<a regra>"}
FIM
```

Sai `0` com o caminho gravado; `1` com o motivo, sem deixar arquivo no disco, se a guideline for
reprovada. O que cada campo pede:

- `nome` — kebab-case ASCII (`design-system`), único em `rules/` e `rules-off/`.
- `descricao` — diz **quando** aplica. É o texto que o modelo lê para decidir relevância;
  descrever o conteúdo não ajuda a decidir escopo.
- `paths` — globs relativos à raiz do projeto, começando por diretório (`src/ui/*.tsx`) ou por
  `**/` (`**/*.tsx`). Pasta inteira é `dir/**/*`, não `dir/**`. Sem chaves `{a,b}` nem vírgula —
  uma entrada por padrão. Cada uma compila **e** casa ao menos um arquivo que existe; sem casar
  nada, a guideline carrega e nunca ativa.
- `corpo` — a regra técnica daquele escopo, nunca vazio. Anti-drift: o que o codex ou outra
  guideline já diz, esta **referencia**, não copia (ex.: `scripts.md` cita `language-policy.md`
  para a medição de ambiente e não a repete).
- `aguardando` (opcional) — `true` para escopo que ainda não existe no disco: grava
  `paths_pending: true`, que dispensa só o casamento; a guideline vale desde o primeiro arquivo
  criado ali.

O registro em `.claude/rules/registry.json` é feito pelo comando. É **projeção**, não fonte:
reporta divergência com o disco, nunca decide por ele.

## Como editar

Mesmo comando da criação, com `--replace`: `dc.py criar-guideline --replace`, o mesmo JSON. A
guideline precisa existir em `rules/` ou `rules-off/`; a versão nova a substitui **no mesmo
lugar**, com o mesmo nome, só se passar em `lint_guideline` — senão sai `1` e a antiga fica.
Trocar o nome não é editar — é arquivar a antiga e criar a nova.

## Como arquivar

`dc.py archive guideline <nome>`. O arquivo sai de `rules/` (ou de `rules-off/`) para
`.claude/archive/rules/`, ganha `archived_at`, `archived_by` e `reason` no frontmatter, e o
`registry.json` é reprojetado sem ela. Arquivar não é desligar: a desligada volta um dia e por isso
passa no lint; a arquivada sai do que o projeto segue. Arquivar **move, nunca apaga**: planos antigos podem citar o item. O motivo vai no stdin, e
`archived_by` é o `git config user.name`. O nome arquivado fica **reservado** — criar outro item com
ele sai `1` —, e a unidade que cita o arquivado passa a listá-lo em `Não resolvidas:` com
"arquivada em <data> por <quem>: <motivo>". Para trazer de volta, com o mesmo nome:
`dc.py restore guideline <nome>`, que exige de novo `lint_guideline`. Codex, *Rethink* (editar e arquivar).

## Como validar

- `rules.lint_guideline(<caminho>)` — tudo de `lint_rule` (frontmatter, formato de `paths:`, corpo
  não vazio) **mais** `paths:` presente, não vazio, e casando arquivo real, salvo
  `paths_pending: true`. O `criar-guideline` já o roda antes de gravar; aqui serve para a guideline
  escrita à mão.
- `rules.auditar_arvore()` — recusa `.md` em subdiretório de `rules/` (o matcher recursa e o
  arquivo continua carregando), rule malformada em `rules/`, guideline quebrada em `rules-off/`.
- **Dois atos humanos que nenhum script substitui:** abrir uma **sessão nova** e **tocar um arquivo
  do escopo**. Depois, `activation_notice.relatorio(<log>)` deve mostrar a guideline carregada com
  `load_reason` de casamento de path — não só `session_start`.

## Onde fica registrado

- A guideline: o arquivo em `.claude/rules/`.
- O estado ligada/desligada: `registry.json` (projeção).
- Por que ela existe — a divergência que a disparou — no plano ou huddle que a originou.

## O que não fazer

- **Não criar sem `paths:`** — sem escopo, é princípio.
- **Não criar por elegância** — sem uma divergência observada, o item fica no
  [`_backlog.md`](../plan/_inbox/_backlog.md), não vira guideline.
- **Não editar `registry.json` para ligar/desligar** — isso é mover o arquivo entre `rules/` e
  `rules-off/`; o registry só acompanha.
- **Não pôr `.md` em subdiretório de `rules/`** — o Claude Code recursa e carrega, mas
  `auditar_arvore` recusa (incidente `L-26`).
- **Guideline é instância e não viaja no plugin** — o mecanismo (carregamento por `paths:`,
  `lint_guideline`) viaja; o conteúdo é do projeto que instala.
