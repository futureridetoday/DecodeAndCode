# Criar um guardrail

Versão 1.1.0 · guia de uso

[← Recursos](../../README.md#recursos)

Guia de procedimento. O que princípio, guideline e guardrail são, e as três portas que os gravam,
está no codex, seções *Princípio*, *Guideline*, *Guardrail* e *Rethink* (`dc.py codex <título>`) —
aqui só o **como**.

## Quando criar

Um guardrail é um **limite verificável** — o que nunca se faz, checável por máquina. Como a
guideline, **se escolhe por evidência de falha**: um incidente mostrou o limite que faltava.

**Declarar não é aspiração.** O guardrail formaliza um invariante que o trabalho **já respeita**.
Se o código ainda viola a regra, o trabalho é consertar o código primeiro; o guardrail entra
depois, para impedir a regressão.

## No primeiro uso

No `/decode-and-code:setup`, o projeto ainda não tem incidente, e o critério muda: o guardrail nasce de
**decisão explícita do time** que desvia do padrão da stack — o que a stack faria por padrão e o time
decidiu barrar. Ele barra o que uma escrita contém, por regex. Depois do primeiro uso, vale o critério
acima.

## Onde fica

Uma regra no array `regras` de [`.claude/guardrails.json`](../../.claude/guardrails.json), na raiz
do projeto que instala. O hook `PreToolUse` (`guardrail.decidir`) lê esse arquivo a cada chamada de
ferramenta.

## Como criar

Pelo comando, do diretório do projeto, com a regra e os dois casos que a provam:

```bash
dc.py adicionar-guardrail <<'FIM'
{
  "regra": {
    "nome": "<identificador-curto>",
    "ferramenta": "<regex contra o nome da ferramenta>",
    "detector": "<regex contra o conteúdo de tool_input>",
    "mensagem": "<o motivo mostrado na recusa>"
  },
  "proibido": {"tool_name": "<ferramenta>", "tool_input": {"<campo>": "<a chamada que deve ser negada>"}},
  "permitido": {"tool_name": "<ferramenta>", "tool_input": {"<campo>": "<a chamada que deve passar>"}}
}
FIM
```

O comando avalia a regra **sozinha**: ela precisa negar `proibido` com o próprio `nome` e liberar
`permitido` — junto das regras existentes, uma anterior que já negasse o caso aprovaria uma regra
que não casa nada. Só então acrescenta a regra ao fim de `regras`, criando o arquivo se faltar.
Sai `0` com o caminho; `1` com o motivo, sem escrever, se a regra for malformada, não se provar ou
repetir um `nome`.

- `ferramenta` — regex casado contra `tool_name` (ex.: `"(execute_sql|apply_migration)$"`).
- `detector` — regex casado contra os valores string de `tool_input`, juntados por `\n`. É o que
  distingue a chamada proibida da permitida.
- A **primeira** regra cujos dois regex casam decide a recusa; nenhuma casando, libera.

**A precisão do `detector` é o ponto.** Frouxo demais bloqueia trabalho legítimo; estreito demais
deixa passar o que ele existe para pegar. Escreva um caso da chamada **proibida** e um da
**permitida**, e confira que o regex separa os dois — foi a inversão exata que o incidente `H-09`
custou (bloqueava `truncate -s 0 arquivo.log`, liberava `psql -c "alter table ..."`).

## Como editar

Mesmo comando da criação, com `--replace`: `dc.py adicionar-guardrail --replace`, o mesmo JSON. A
regra com o mesmo `nome` precisa existir; a nova toma **o mesmo lugar** na lista, só depois de se
provar pelo par — senão sai `1` e a antiga fica.

## Como arquivar

`dc.py archive guardrail <nome>`. A regra sai de `.claude/guardrails.json` para
`.claude/archive/guardrails.json`, com `archived_at`, `archived_by` e `reason`, e o hook deixa de
negar o caso dela. O par proibido/permitido não vai junto: o `guardrails.json` não o guarda.
Arquivar **move, nunca apaga**: planos antigos podem citar o item. O motivo vai no stdin, e
`archived_by` é o `git config user.name`. O nome arquivado fica **reservado** — criar outro item com
ele sai `1` —, e a unidade que cita o arquivado passa a listá-lo em `Não resolvidas:` com
"arquivada em <data> por <quem>: <motivo>". Para trazer de volta, com o mesmo nome:
`dc.py restore guardrail <nome>`, com um par novo pelo stdin, o JSON `{proibido, permitido}`: a
regra só volta depois de se provar por ele. Codex, *Rethink* (editar e arquivar).

## Como validar

- O par proibido/permitido já foi provado pelo `adicionar-guardrail`.
- `dc.py lint-guardrails` — o arquivo inteiro, inclusive regra escrita à mão: JSON válido, as
  quatro chaves com texto, regex que compila, `nome` único. Regra malformada faz o guardrail
  **falhar aberto** (libera tudo), com aviso em stderr, por construção: guardrail que trava o
  trabalho por defeito próprio é obstáculo, não proteção.
- Numa sessão real, disparar a chamada proibida e ver a recusa com o `nome` da regra no motivo.

## Onde fica registrado

- A regra: o objeto em `.claude/guardrails.json`.
- O incidente que a motivou: o plano ou o huddle onde ele foi registrado.

## O que não fazer

- **Não declarar o que o código ainda viola** — conserte primeiro, formalize depois.
- **Não pôr nome de serviço, tabela ou projeto no mecanismo** — `guardrail.py` só conhece a
  *forma* de uma regra; a instância vive no `guardrails.json` do projeto que instala, e é só ela
  que não viaja no plugin.
- **Não confiar num `detector` sem os dois casos** — proibido e permitido — provando que ele
  separa.
- **Não usar guardrail para o que é guideline** — guardrail nega uma ação; guideline orienta como
  fazer. Se não dá para checar por regex, é guideline.
