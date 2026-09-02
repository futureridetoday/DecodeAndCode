# Criar uma guideline

Versão 1.0.0 · guia de uso

[← Como usar o Decode And Code](../../README.md#como-usar-o-decode-and-code)

Guia de procedimento. Definições na norma
([`modelo-dev-units.md`](../plan/system/modelo-dev-units.md), seção *Camada normativa*) — aqui só o
**como**.

## Quando criar

Uma guideline **se escolhe por evidência de falha, não por elegância.** O gatilho é a **primeira
divergência observada entre duas execuções** — duas sessões fizeram a mesma coisa de formas
diferentes porque nada dizia qual era a certa. Não é uma data no calendário, e não é "seria bom
ter".

Se a regra passa no teste do princípio (*ninguém competente rejeitaria*), é princípio, não
guideline — veja [`create-principle.md`](create-principle.md). Se ela é *procedimento que alguém
invoca* em vez de *norma que ativa sozinha ao tocar um arquivo*, é skill.

## Onde fica

Um arquivo por guideline em [`.claude/rules/`](../../.claude/rules/) — `.claude/rules/<nome>.md`.
Desligada, vai para o diretório irmão `.claude/rules-off/`, fora do que o Claude Code carrega.

## Como criar

1. **Frontmatter** — três campos, todos obrigatórios:

   ```yaml
   ---
   name: <nome>
   description: <quando esta guideline vale — não o que ela ensina>
   paths: ["<glob>", "<glob>"]
   ---
   ```

   - `name` — não vazio, identifica a rule.
   - `description` — diz **quando** aplica. É o texto que o modelo lê para decidir relevância;
     descrever o conteúdo não ajuda a decidir escopo.
   - `paths:` — lista `[...]` de globs. Cada entrada compila como glob **e** casa ao menos um
     arquivo que existe no repositório. `paths:` ausente ⇒ é princípio; presente sem casar nada ⇒
     falha silenciosa (carrega e nunca ativa).

2. **Corpo** — a norma técnica daquele escopo, nunca vazio. Anti-drift: o que a norma ou outra
   guideline já diz, esta **referencia**, não copia (ex.: `scripts.md` cita `language-policy.md`
   para a medição de ambiente e não a repete).

3. **Registrar em `registry.json`** — `.claude/rules/registry.json` ganha
   `"<nome>": {"atualizado_em": "<data>", "estado": "ligada"}`. É **projeção**, não fonte: reporta
   divergência com o disco, nunca decide por ele.

## Como validar

- `rules.lint_guideline(<caminho>)` — tudo de `lint_rule` (frontmatter, formato de `paths:`, corpo
  não vazio) **mais** `paths:` presente, não vazio, e casando arquivo real.
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
