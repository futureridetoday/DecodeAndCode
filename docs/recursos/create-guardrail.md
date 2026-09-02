# Criar um guardrail

Versão 1.0.0 · guia de uso

[← Como usar o Decode And Code](../../README.md#como-usar-o-decode-and-code)

Guia de procedimento. Definições na norma
([`modelo-dev-units.md`](../plan/system/modelo-dev-units.md), seção *Camada normativa*) — aqui só o
**como**.

## Quando criar

Um guardrail é um **limite verificável** — o que nunca se faz, checável por máquina. Como a
guideline, **se escolhe por evidência de falha**: um incidente mostrou o limite que faltava.

**Declarar não é aspiração.** O guardrail formaliza um invariante que o trabalho **já respeita**.
Se o código ainda viola a regra, o trabalho é consertar o código primeiro; o guardrail entra
depois, para impedir a regressão.

## Onde fica

Uma regra no array `regras` de [`.claude/guardrails.json`](../../.claude/guardrails.json), na raiz
do projeto que instala. O hook `PreToolUse` (`guardrail.decidir`) lê esse arquivo a cada chamada de
ferramenta.

## Como criar

Adicione um objeto a `regras`, com quatro campos:

```json
{
  "nome": "<identificador-curto>",
  "ferramenta": "<regex contra o nome da ferramenta>",
  "detector": "<regex contra o conteúdo de tool_input>",
  "mensagem": "<o motivo mostrado na recusa>"
}
```

- `ferramenta` — regex casado contra `tool_name` (ex.: `"(execute_sql|apply_migration)$"`).
- `detector` — regex casado contra os valores string de `tool_input`, juntados por `\n`. É o que
  distingue a chamada proibida da permitida.
- A **primeira** regra cujos dois regex casam decide a recusa; nenhuma casando, libera.

**A precisão do `detector` é o ponto.** Frouxo demais bloqueia trabalho legítimo; estreito demais
deixa passar o que ele existe para pegar. Escreva um caso da chamada **proibida** e um da
**permitida**, e confira que o regex separa os dois — foi a inversão exata que o incidente `H-09`
custou (bloqueava `truncate -s 0 arquivo.log`, liberava `psql -c "alter table ..."`).

## Como validar

- Rodar `guardrail.decidir(<payload>, <caminho de guardrails.json>)` com um payload da chamada
  proibida (espera recusa, com `nome`/`mensagem`) e um da permitida (espera `None`).
- Conferir que `guardrails.json` continua JSON válido — regra malformada faz o guardrail **falhar
  aberto** (libera tudo), com aviso em stderr, por construção: guardrail que trava o trabalho por
  defeito próprio é o obstáculo que a norma manda evitar.
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
