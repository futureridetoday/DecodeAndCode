# huddle

Versão 1.1.0 · skill

[← Como usar o Decode And Code](../../README.md#como-usar-o-decode-and-code)

## O que é

A skill que conduz o **huddle** da pessoa da sessão: a conversa sobre o que ainda não foi decidido.
Percorre as entradas abertas do arquivo da pessoa, uma por vez, e para cada uma decide, promove a
guideline ou guardrail, leva ao método, descarta com o motivo ou mantém. Com `registrar <texto>`,
abre uma entrada nova. Roda em Opus e só por invocação explícita (`disable-model-invocation: true`):
o huddle se abre quando a conversa acontece.

## Problema que resolve

As camadas normativas guardam o que já foi decidido; o resto — pergunta em aberto, contradição
contornada, padrão que uma sessão sozinha não revela — se perdia em conversa. Antes deste recurso,
o huddle era um arquivo único por projeto, sem ninguém que lembrasse de abri-lo, sem comando para
registrar, e a linha de fecho dos relatórios só provava que existia, não que os ids eram reais.

## Como funciona

- **Um arquivo por pessoa**, em `<plan_root>/system/huddle/<usuario>.md`, versionado. A pessoa é o
  `git config user.name` em kebab-case ASCII. Cada uma vê só o próprio arquivo.
- **Script para tudo que é formato**, pelo `dc.py`: `huddle-iniciar`, `huddle-abrir`,
  `huddle-fechar`, `huddle-concluir`, `huddle-pauta`, `huddle-fecho`, `huddle-lint`,
  `huddle-lint-relatorio` e `huddle-migrar`.
- **Registro no fecho.** As cinco skills que registram (`intake`, `review-plan`, `derive`, `implement`, `setup`)
  terminam rodando `huddle-fecho`, registram o que ficou aberto com `huddle-abrir --autor Claude`, e
  passam a mensagem final por `huddle-lint-relatorio`, que exige
  `entradas novas no huddle: N (H-XX, …)` com ids abertos hoje no arquivo da pessoa.
- **Lembrete.** O hook `SessionStart` avisa ao abrir a sessão quando há entrada aberta e o último
  huddle foi há `reminder_days` dias ou mais.
- **Promoção.** A proposta é montada com a pessoa, aprovada na conversa e gravada por
  `dc.py criar-guideline` ou `dc.py adicionar-guardrail`; a entrada fecha com o caminho gravado.
- **Evidência.** A entrada pode declarar de onde veio, por `huddle-abrir <tipo> --evidencia
  "<origem>"`: `E-XX`, `L-XX`, `bloqueio: <regra>`, `gate: <comando>` ou `revisão: <plano>`. Fica
  numa linha `Evidência:` no fim do texto; é opcional.
- **Feedback ao método.** Entrada sobre o próprio método fecha com `huddle-fechar <H-XX> método`,
  com um texto genérico, aprovado por você, no stdin; um erro do log, com
  `log-resolver <E-XX> método`. Os dois gravam `.claude/log/metodo/M-XX.md`, fora do git, com os
  caminhos absolutos trocados por `<projeto>` e `~`. `dc.py metodo-listar` mostra cada um inteiro,
  para você revisar antes de levar; `dc.py metodo-levado <M-XX> "<onde>"` o apaga depois que você
  o levou ao repositório do método. A pauta lista os pendentes.

## Como usar

- `/decode-and-code:huddle` — a conversa: pauta, entradas uma a uma, `huddle-concluir` no fim.
- `/decode-and-code:huddle registrar <texto>` — abre uma entrada com você como autor; a skill
  pergunta o tipo e, opcional, a evidência.
- **Frequência do lembrete** — o campo `reminder_days` do seu arquivo (padrão 7; `0` desliga).
- **Projeto com o arquivo único antigo** (`<plan_root>/system/huddle.md`) — rode
  `dc.py huddle-migrar` uma vez; até lá, registrar é recusado para o huddle não se partir em dois.
- **Sem `user.name`** — configure com `git config user.name "Seu Nome"`.

## Exemplos de uso

- O aviso de abertura diz "Huddle: 3 entrada(s) aberta(s), último huddle há 9 dias". A pessoa roda
  `/decode-and-code:huddle`; a skill mostra a pauta, decide uma entrada (destino: o `## Decisões` de
  um plano), promove outra a guideline depois de a pessoa aprovar o texto, mantém a terceira e grava
  a data do huddle.
- No meio do trabalho, a pessoa nota que dois documentos se contradizem e roda
  `/decode-and-code:huddle registrar "o README e a norma divergem sobre X"`; a skill confirma o tipo
  `divergência` e devolve o `H-XX`.

## Fundamentação

Norma, seções *Huddle* e *Log de uso*, em [`modelo-dev-units.md`](../plan/system/modelo-dev-units.md).
Planos [`0008-wire-huddle-cycle`](../plan/model/0008-wire-huddle-cycle.md) e
[`0019-norm-evolution-evidence`](../plan/model/0019-norm-evolution-evidence.md).

## Limites

- **Os gatilhos de escrita não têm oráculo**: o lint confere a declaração e a posse dos ids, nunca
  se o modelo deveria ter registrado algo.
- **O lembrete só alcança quem abre o Claude Code.**
- **Identidade pelo nome do git**: duas pessoas com o mesmo nome compartilham arquivo, e quem muda
  o nome ganha um arquivo novo.
- **Virada de dia**: uma entrada aberta antes da meia-noite e declarada num relatório depois dela é
  recusada como antiga.
- A pré-aprovação do `dc.py` vale só no turno da skill; fora dele, cada comando pede permissão.
- **O envio ao método é manual.** O `M-XX` não sai do projeto sozinho e não é versionado: se perde
  com o clone. A troca de caminhos é mecânica; nome de plano ou trecho de código no texto dependem
  da sua revisão.
