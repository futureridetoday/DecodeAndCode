# decode-and-code

Plugin do Claude Code que empacota o método **decode-and-code**: o caminho de um pedido até a
entrega, em que Claude entende e propõe antes de construir, e constrói em unidades que rodam numa
sessão nova, sem o histórico da conversa.

**O problema.** Uma sessão nova do modelo não sabe o que a anterior sabia — o custo aparece como
retrabalho, decisão re-tomada e execução que diverge do combinado. Documentação solta não resolve:
não é lida no momento certo, e envelhece sem ninguém notar.

**A resposta.** O método faz o *plano* carregar a diferença entre sessões. O pedido vira uma
proposta, que o usuário aprova; a proposta vira um plano técnico, com histórias e critérios de
aceite; o plano é derivado em *unidades*, cada uma pronta para quem chega **sem contexto**, com o
**teste declarado**. A entrega está pronta quando o teste passa e o usuário a aprova.

**O método é o codex**, em [`.claude/skills/decode-and-code/codex/`](.claude/skills/decode-and-code/codex/):
o workflow, as etapas, os artefatos, as regras e o que cada projeto define — princípios, guidelines,
guardrails e a foundation. Ele viaja no plugin, e as skills o leem pelo título da seção, nunca o
copiam.

**A evidência.** A skill de origem: 15 de 15 unidades executadas por Sonnet em sessões novas, sem uma
pergunta sobre o conteúdo da unidade.

## Instalação

### Por comando

```bash
/plugin marketplace add futureridetoday/DecodeAndCode@main
```

```bash
/plugin install decode-and-code@future-ride-today
```

Os dois comandos rodam dentro do Claude Code. O primeiro registra o marketplace deste repositório,
fixado no branch **`main`** (produção) — o `@main` persiste entre atualizações, mesmo com `dev`
como branch default; o segundo instala o plugin a partir dele.

### Por upload

Customize → Plugins → *upload a custom plugin file*, com o zip anexado ao
[Release](https://github.com/futureridetoday/DecodeAndCode/releases) mais recente.

### Atualização

```bash
/plugin marketplace update future-ride-today
```

```bash
/plugin update decode-and-code@future-ride-today
```

O primeiro refresca o metadado do marketplace; o segundo baixa o zip do Release novo, confere o
`sha256` e instala. **Reiniciar o Claude Code** para aplicar.

Mudança que fica só no repositório (`README.md`, `docs/`) não entra no pacote e não exige nada de
quem instalou. **Atualizar o plugin não é repensar o projeto**: quando é o projeto que muda de rumo,
o que se revisa são os princípios, as guidelines, os guardrails e a foundation dele, com
`/decode-and-code:rethink`.

## Como começar

1. **Instale no escopo do projeto**, não só no de usuário: assim cada colega que clonar o repositório
   trabalha com as mesmas guidelines e guardrails. A skill `setup` propõe gravar isso em
   `.claude/settings.json` (`dc.py setup-escopo`); cada pessoa ainda instala o plugin uma vez por clone.
   Pelo terminal, use `claude plugin install decode-and-code@future-ride-today --scope project`.
2. **Rode `/decode-and-code:setup`** — a primeira coisa a fazer; o aviso de abertura o propõe num
   projeto sem setup. Ele inicia o seu huddle e grava, uma sugestão por vez e só com o seu sim, os
   princípios, a foundation (padrão de código e mapa de recursos), as guidelines e os guardrails.
   Guia: [`docs/recursos/setup.md`](docs/recursos/setup.md).
3. **Traga um pedido** com `/decode-and-code:decode <pedido>`.

## O workflow

| Etapa | O que sai | Skill | Quem aprova |
|---|---|---|---|
| Entrada | o tipo, com o motivo, e o objetivo do plano | `decode` | o usuário confirma |
| P1, decode | a proposta, escrita para o usuário, no `_inbox/` | `decode` | P2, o usuário |
| P3, revisão | o plano técnico: histórias, porte, independência, tarefas ou unidades | `review-plan` | P4, o usuário; o plano recebe número |
| P5, derive | cada unidade pronta para rodar sem a conversa, e o handoff (médio e grande) | `derive` | o usuário aprova as unidades |
| P6, code | a entrega de cada unidade, ou das tarefas do pequeno | `code`, em fork | P7, o usuário testa e aprova |
| P8 | o teste do plano inteiro (só no grande) | — | aprovação final |

A correção (`fix`) segue um workflow próprio, o módulo `fix`: a skill `diagnose` reproduz o defeito e
escreve o plano mínimo, e o `code` faz o teste vermelho, o ajuste e o teste verde.

Quem executa uma unidade entrega arquivos e relatório, e não commita. A situação de cada unidade é
**projetada a partir do teste**, nunca editada à mão.

## Recursos

Em [`docs/recursos/`](docs/recursos/): um documento por recurso, e um guia de uso por item que o
projeto define.

| Tipo | Recurso | O que faz | Doc |
|---|---|---|---|
| skill | `decode` | Entrada e proposta (P1, P2) | [decode.md](docs/recursos/decode.md) |
| skill | `review-plan`, `derive`, `code` | Plano técnico (P3, P4), unidades (P5) e entregas (P6, P7) | [decode-and-code.md](docs/recursos/decode-and-code.md) |
| skill | `diagnose` | Diagnóstico e plano mínimo da correção (módulo `fix`) | [decode-and-code.md](docs/recursos/decode-and-code.md) |
| skill | `huddle` | Conduz o huddle da pessoa: decide, propõe ao rethink ou a um plano `rule`, descarta ou mantém | [huddle.md](docs/recursos/huddle.md) |
| skill | `setup` | Primeiro uso: huddle, princípios, foundation, guidelines e guardrails | [setup.md](docs/recursos/setup.md) |
| skill | `rethink` | Revisão depois de uma mudança de rumo, foundation inclusive | [rethink.md](docs/recursos/rethink.md) |
| hooks | 4 hooks, 3 no pacote | Guardrail (`PreToolUse`), log de ativação (`InstructionsLoaded`) e aviso de abertura (`SessionStart`) | [hooks.md](docs/recursos/hooks.md) |
| guia de uso | Princípio, guideline, guardrail | Quando e como criar, editar ou arquivar cada um | [create-principle.md](docs/recursos/create-principle.md), [create-guideline.md](docs/recursos/create-guideline.md), [create-guardrail.md](docs/recursos/create-guardrail.md) |

O plugin carrega o **mecanismo** e o codex. Princípios, guidelines, guardrails, a foundation e o
huddle são do projeto que instala, e nunca viajam com os deste repositório.

## Desenvolvimento

```bash
bash scripts/test-python.sh
```

O harness aceita Python ≥ 3.10, prefere o 3.10 e avisa quando roda em outra versão; o CI roda em
3.10 fixo e é a prova de compatibilidade com o Cowork
([`language-policy.md`](docs/plan/system/language-policy.md)).

Quem mantém o plugin: [`docs/maintenance/`](docs/maintenance/) — o guia do codex, o empacotamento,
o [procedimento de release](docs/maintenance/release.md), os módulos, e a fronteira entre skills e
scripts.
