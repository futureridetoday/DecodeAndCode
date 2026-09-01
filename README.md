# decode-and-code

Plugin do Claude Code que empacota o método **decode-and-code**: a norma em camadas (princípio,
guideline, guardrail), o porte de plano, e o ciclo `plano → unidade → cold-start`.

O problema que ele resolve: uma sessão nova não sabe o que a anterior sabia. O método faz o plano
carregar essa diferença — cada unidade é escrita para ser executada por alguém que chega sem
contexto, e o critério de que ela está pronta é justamente esse.

## Instalação

```bash
/plugin marketplace add futureridetoday/DecodeAndCode
```

```bash
/plugin install decode-and-code@bortoli
```

Os dois comandos rodam dentro do Claude Code. O primeiro registra o marketplace deste repositório;
o segundo instala o plugin a partir dele.

### Para desenvolver ou testar sem instalar

```bash
claude --plugin-dir dist/decode-and-code
```

## O que vem junto

| Componente | O que faz |
|---|---|
| Skill `decode-and-code` | Os três modos — revisar um plano, derivar estrutura e unidades, implementar uma unidade em cold-start |
| Agent `planner` | Revisa um plano antes da aprovação, e deriva as unidades de um plano aprovado |
| Agent `developer` | Implementa uma unidade já derivada, em cold-start |
| Comando `/implement` | Dispara a implementação de uma unidade |
| Comando `/delegate` | Delega a unidade ao `developer` em sessão limpa |
| Hooks | Carregam a norma e as guidelines ativas na abertura da sessão e após compactação |

O plugin carrega o **mecanismo**. Guardrail e guideline são do projeto que instala — o método os
materializa lá, e nunca viaja com os deste repositório.

## O ciclo

| # | Etapa | Onde |
|---|---|---|
| 1 | O plano nasce | `docs/plan/_inbox/` |
| 2 | Revisão | modo `review` |
| 3 | **Aprovação** | humano |
| 4 | Derivação em unidades | modo `derive` |
| 5 | Implementação, uma unidade por vez | modo `implement`, em cold-start |

Quem executa uma unidade entrega arquivos e relatório, e não commita. O estado de cada unidade
(`spec` → `wip` → `verified`) é **projetado a partir do teste**, nunca editado à mão.

## Como este repositório se relaciona com o pacote

`.claude/` é a **fonte** — a skill, os hooks, os agentes, os comandos e o manifesto
(`.claude/plugin.json`). `dist/decode-and-code/` é o **pacote construído**, versionado porque quem
instala clona o repositório e não roda o build.

```bash
python3 -c "import sys; sys.path.insert(0, '.claude/skills/decode-and-code/scripts'); import empacotar; empacotar.construir()"
```

A sincronia entre os dois é um caso de teste, não disciplina: a suíte reprova quando o pacote
versionado e o recém-construído divergem em um byte.

## Desenvolvimento

```bash
bash scripts/test-python.sh
```

Exige Python 3.10 explícito — ver [`language-policy.md`](docs/plan/system/language-policy.md) para
a medição de ambientes que fixou o alvo.

A norma completa fica em [`modelo-dev-units.md`](docs/plan/system/modelo-dev-units.md).
