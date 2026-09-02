# hooks

Versão 1.0.0 · hooks (4)

[← Como usar o Decode And Code](../../README.md#como-usar-o-decode-and-code)

> A norma de descrição de recurso do AmFlow não cobre `hook` — este documento descreve os quatro
> a partir dos próprios arquivos, para completar o inventário. Não há nada para o usuário invocar
> aqui: os hooks rodam sozinhos, no harness, **sem custo de contexto do modelo**.

## O que é

Quatro pontos de entrada em `hooks/`, cada um ligando um evento do Claude Code a um mecanismo da
skill sem decidir nada por conta própria:

| Hook | Evento | O que faz |
|---|---|---|
| `pre_tool_use` | `PreToolUse` | Aplica o guardrail do projeto que instala — lê `.claude/guardrails.json` e pode **negar** uma chamada de ferramenta, com a regra e a mensagem no motivo |
| `instructions_loaded` | `InstructionsLoaded` | Registra, num log por sessão fora do repositório, qual instrução carregou e o `load_reason`; guarda o estado das rules com `paths:` |
| `post_compact` | `PostCompact` | Depois de uma compactação, nomeia por stderr as rules com `paths:` que estavam ativas e não voltaram |
| `subagent_start` | `SubagentStart` | Anuncia por stderr, no transcript do próprio subagente, o `agent_type` e o `agent_id` que iniciaram |

## Problema que resolve

Duas coisas que o método precisa e que o modelo não vê sozinho: **a norma e as guidelines ativas
carregaram mesmo?** (e continuaram depois de compactar?), e **uma chamada de ferramenta violou um
guardrail do projeto?**. Os hooks tornam isso observável e, no caso do guardrail, exigível — sem
gastar contexto, porque o Claude Code descarta o `systemMessage` desses eventos e o canal real é
log e stderr.

## Como funciona

`empacotar.construir()` copia `.claude/hooks/*.py` e gera o `hooks/hooks.json` do pacote, que
casa cada evento (`matcher: "*"`) ao script correspondente via `python3 ${CLAUDE_PLUGIN_ROOT}/hooks/<script>.py`.
Toda a decisão vive nos módulos da skill (`guardrail.decidir`, `activation_notice.*`); os arquivos
em `hooks/` só ligam stdin/stdout ao mecanismo. Falham abertos e em silêncio: payload malformado
devolve `None` e nada é escrito.

## Como usar

Não se usa diretamente. Uma vez o plugin instalado e habilitado, os quatro disparam sozinhos. O
que o usuário faz com a saída deles:

- **Ler o log de ativação** — `"$TMPDIR"decode-and-code-activation-<session_id>.log` — para
  conferir que a norma e as guidelines certas carregaram. `activation_notice.relatorio(<log>)`
  devolve o veredito por linha (escopo não respeitado, guideline que continua carregando fora de
  escopo, colisão entre rules com `paths:`).
- **Escrever `.claude/guardrails.json`** no projeto que instala, para o `pre_tool_use` ter o que
  aplicar — o plugin carrega só o mecanismo, nunca as regras.

## Exemplos de uso

**Depurar uma rule com `paths:` que não ativa.** A guideline deveria carregar ao tocar um arquivo
e não carrega. O log do `instructions_loaded` mostra os `load_reason` de cada instrução — sem uma
linha `path_glob_match` para a rule, o escopo dela está errado.

**Provar que uma skill chega ao subagente.** O `subagent_start` anuncia o início no transcript do
subagente; combinado com uma sonda comportamental (pedir ao subagente conteúdo exclusivo do
`SKILL.md`), confirma que `skills:` no frontmatter do agent injeta a skill.

## Fundamentação

Unidade `0001-05` do plano `0001` (os três hooks de anúncio) e `0001-04` (o `pre_tool_use`). O
canal de cada evento — log, stderr, silêncio — foi medido contra `code.claude.com/docs/en/hooks`
em 2026-08-24: `InstructionsLoaded` e `PostCompact` descartam `systemMessage`, então o uso é
"audit logging, compliance tracking, or observability"; `SubagentStart` e `PostCompact` só exibem
stderr, sem afetar criação de subagente nem resultado da compactação.

## Base de conhecimento

Nenhuma própria. A lógica está em `scripts/guardrail.py` e `scripts/activation_notice.py`. As
regras de guardrail vêm de `.claude/guardrails.json` do projeto que instala.

## Limites

- **Não são invocáveis.** Rodam por evento, nunca por pedido.
- **`pre_tool_use` sem `guardrails.json` não faz nada.** As regras são do projeto que instala.
- **Anúncio, não injeção.** `instructions_loaded`/`post_compact`/`subagent_start` observam o que o
  harness carregou; não colocam nada no contexto do modelo — skill nunca aparece no log de
  ativação, só memória e rules.
- **Falha em silêncio.** Payload fora do esperado devolve `None` e nada é escrito — por
  construção.
