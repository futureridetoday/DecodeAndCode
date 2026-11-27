---
# about
name: modules
type: doc
project: ""
description: Contrato técnico entre o núcleo do decode-and-code e os módulos — onde mora um módulo, o que o module.json declara, como o núcleo o descobre e como se inclui ou remove sem quebrar nada
tags: [manutencao, modulo, nucleo]

# history
author: Bortoli
created: 2026-11-27
status: stable
version: 1.0.0
updated: ""

# system
scope: project
source: ""
auto_load: false
checksum: ""
dependencies: [codex-guide]
---

# Módulos

Documentação de manutenção: o contrato técnico entre núcleo e módulo é arquitetura do plugin, não
do método (inventário, itens 34 e 58). Só quem mantém o plugin inclui ou remove um módulo; o projeto
que usa o DC não liga nem desliga módulo.

## Onde mora

Um módulo é uma pasta em `.claude/skills/decode-and-code/modules/<nome>/` com:

- `module.json` — o manifesto, lido por `lib.modulos()`;
- `codex/` — o capítulo do codex do módulo, quando ele tem um, escrito pelo guia
  ([`codex-guide.md`](codex-guide.md)) como qualquer capítulo;
- as skills que ele declara ficam em `.claude/skills/<skill>/`, ao lado das do núcleo, porque é ali
  que o Claude Code as procura.

## O `module.json`

| Campo | O que é |
|---|---|
| `name` | O nome do módulo, o da pasta |
| `version` | A versão do módulo |
| `core_format` | A versão do formato do plano que o módulo exige do núcleo (`lib.FORMATO_ATUAL`); outra é recusada |
| `plan_types` | Os tipos de plano com workflow próprio, que o `decode` passa para a skill do módulo |
| `skills` | As skills que viajam com o módulo |
| `plan_sections` | Por tipo, as seções que o `lint-plano` exige no lugar das de todo plano do formato 2 |

Manifesto ilegível, incompleto ou de outro formato é recusado inteiro, com o caminho no erro.

## Como o núcleo o usa

O núcleo nunca importa um módulo; só lê o que o `module.json` declara:

- `normas.pastas_do_codex()` e `lint_codex.pastas_do_codex()` juntam o capítulo do módulo ao núcleo,
  e `dc.py codex <título>` o acha pelo título;
- `lint_plano.secoes_exigidas()` usa `plan_sections` do tipo do plano;
- `lib.skills_do_pacote()` acrescenta as skills do módulo ao que o `empacotar` leva;
- `dc.py modulos` lista os tipos e as skills, e o `decode` segue por ela quando o tipo tem workflow
  próprio.

## Incluir e remover

Incluir é criar a pasta e as skills; remover é apagar as duas. Nada no núcleo muda, e a suíte do
núcleo passa sem o módulo: `test_modulos.py`, *TestNucleoSemModulo*, roda com a pasta de módulos
vazia. O capítulo do núcleo nunca cita um título do módulo (o mesmo teste confere).

## Módulos de hoje

| Módulo | Tipos | Skills | Capítulo |
|---|---|---|---|
| `fix` | `fix` | `diagnose` | `modules/fix/codex/fix.md` — o workflow de correção |
