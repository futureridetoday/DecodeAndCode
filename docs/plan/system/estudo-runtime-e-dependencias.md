---
# about
name: estudo-runtime-e-dependencias
type: doc
project: DecodeAndCode
description: "Estudo empírico dos ambientes de execução do Claude (Cowork e browser) e a decisão de linguagem/dependência do motor de Playbook do Brand Boost. Confirma Python e Node nativos na VM e corrige, com evidência, o precedente de descontinuar Python por 'zero-dep'. Base canônica da política de linguagem deste projeto"
tags: [cowork, runtime, python, typescript, dependencias, estudo, empirico, politica-linguagem]

# history
author: Bortoli
created: 2026-07-13
status: stable
version: 1.0.0
updated: 2026-07-13

# system
scope: project
auto_load: false
dependencies: []
---

> **Procedência.** Estudo conduzido no repositório **Brand Boost** e copiado para o AmFlow em
> 2026-07-24; migrado para este repositório em 2026-08-24, desacoplado das duas instâncias
> anteriores — a seção com as implicações específicas para o AmFlow não migrou. O corpo é o
> original; os links relativos apontam para este repositório, e as referências a arquivos do Brand
> Boost e do AmFlow que não existem aqui viraram texto.

# Estudo — Ambientes de execução do Claude e a decisão de linguagem/dependência

> **Como usar este documento.** Registra a investigação empírica feita em 2026-07-13 para decidir a
> linguagem do motor de Playbook (BB 6.0). Nasceu com escopo **duplo** — (1) para o Brand Boost,
> fundamenta a decisão de manter **Python** no motor; (2) para o AmFlow, revisitou com evidência a
> decisão anterior de "zero-dependência sem Python" —, e serve aqui a um terceiro propósito:
> fundamenta a versão-alvo e a liberdade de linguagem dos scripts deste repositório (seções 3 e 4 de
> [`language-policy.md`](language-policy.md)). É portátil: pode ser copiado/referenciado em outros
> repositórios.

---

## 1. Sumário executivo

A dúvida era se distribuir um motor em **Python** inviabilizaria o produto para usuários não-técnicos (o medo clássico: "usuário Windows não tem Python instalado"). A investigação passou por três camadas — documentação oficial, repositório oficial de plugins e **teste empírico** — e o veredito é claro:

- O código de plugins **não roda na máquina do usuário**; roda numa **VM Linux gerenciada** (nuvem por padrão). O dispositivo — Windows, Mac, futuro smartphone — é apenas cliente.
- Essa VM tem **Python e Node nativos**, confirmado por sondas executadas em **dois ambientes distintos** (Cowork e Claude no browser).
- Logo, o medo original **não se materializa**, e a decisão de linguagem volta a ser de engenharia. Veredito: **Python (stdlib) no motor**.
- **A lição geral:** a premissa de que "não se pode depender de um runtime" é falsa para estes ambientes. O princípio zero-dependência continua correto — mas equiparar "zero-dep" a "sem Python" é um passo além do necessário: **Python stdlib já é zero-dependência.**

---

## 2. Contexto e pergunta

O Brand Boost 6.0 será distribuído como plugin do Claude Cowork. Seu orquestrador é o `workflow.py` (Brand Boost — `bin/workflow.py`) — 975 linhas, Python, stdlib pura. A pergunta: **reescrever em quê, ou manter?**

Duas premissas precisavam de verificação, não de suposição:

1. **"Distribuir Python quebra para usuário não-técnico."** Verdadeiro apenas se o código rodar na máquina do usuário.
2. **Precedente de "zero-dependência, sem Python" em outro projeto.** Um projeto irmão já havia migrado sua orquestração para markdown + bash "zero-dep", descontinuando Python — segundo o autor, uma escolha derivada de **validação superficial** sobre dependências, não de medição. O que este estudo se propõe a corrigir.

A pergunta-raiz que organiza tudo: **onde o código roda, e o que isso exige da linguagem?**

---

## 3. Método

Três camadas, da mais fraca à mais forte:

| Camada | Fonte | O que resolveu |
|---|---|---|
| 1 · Documentação oficial | docs do Cowork e de Agent Skills | Confirmou VM Linux e execução de scripts; **não garante runtimes específicos** — inconclusiva sobre Python/Node |
| 2 · Repositório oficial | `anthropics/knowledge-work-plugins` | **Precedente**: 26 scripts Python em skills de plugins Cowork; zero Node/TS (só 1 `.js` de CI) |
| 3 · Teste empírico | Sondas instaladas e executadas | **Prova de primeira mão**: versões e disponibilidade reais em dois ambientes |

**Princípio metodológico: decisão sobre dependência não se toma por suposição; mede-se.** A doc
oficial é genérica de propósito; só o teste fecha.

---

## 4. Evidência empírica

### 4.1 Onde o código roda

- **Cowork** executa numa **VM Linux** — nuvem por padrão (*"the agent loop and code execution run on Anthropic's servers"*) ou local no desktop. Mobile e web são **clientes** (recurso Dispatch): o telefone despacha a tarefa; a execução acontece na nuvem/desktop.
- **Claude no browser** executa num **sandbox Linux** na nuvem.
- **Consequência:** o dispositivo do usuário (Windows, iOS, Android) **nunca é o runtime**. O medo "usuário Windows sem Python" não se aplica — a VM é Ubuntu com Python.

### 4.2 Resultados das sondas (dois ambientes)

Dois plugins mínimos (`cowork-probe-python`, `cowork-probe-typescript`) instalados via marketplace git e executados:

| Dimensão | Cowork (nuvem) | Claude no browser |
|---|---|---|
| Arquitetura | ARM64 (aarch64) | x86_64 |
| OS base | Ubuntu 22.04 (glibc 2.35) | Ubuntu 24.04 (glibc 2.39) |
| **Python** | ✅ 3.10.12 (`/usr/bin/python3`) | ✅ 3.12.3 (`/usr/bin/python3`) |
| **Node** | ✅ v22.22.3 (`/usr/bin/node`) | ✅ presente (versão não medida) |
| npm · npx · bash · git | ✅ | ✅ |
| jq | ✅ presente | ❌ ausente |
| TS via `--experimental-strip-types` | ✅ funcionou (sem build) | ⚠️ não testado (scripts não montados) |
| TS via `npx tsx` | ✅ funcionou → VM tem egress | ⚠️ não testado |
| `CLAUDE_PLUGIN_ROOT` | vazio (Claude resolveu o path) | vazio (falha inicial; exigiu `find`) |
| Montagem dos scripts do plugin | completa | só o `SKILL.md` (TS); Python presente |

### 4.3 Reprodutibilidade

Sondas em **https://github.com/rafaelbortoli/cowork-runtime-test** (público). Instalar via *Customize → Plugins → Add marketplace* → `rafaelbortoli/cowork-runtime-test`, e pedir ao Claude para usar as skills `probe-python` e `probe-typescript`.

---

## 5. Achados

### 5.1 Python e Node coexistem, nativos, em todos os ambientes testados
Não é preciso escolher a linguagem por disponibilidade de runtime — os dois estão presentes. A escolha é de engenharia, não de viabilidade.

### 5.2 Os ambientes são heterogêneos
Arquitetura (ARM ↔ x86), versão de Python (3.10 ↔ 3.12), OS (22.04 ↔ 24.04), utilitários (jq presente/ausente). **Implicação:** um artefato que dependa de uma versão específica, de arquitetura ou de um utilitário externo **quebra ao trocar de ambiente**. Zero-dependência e compatibilidade ampla não são preferência — são requisito. O `workflow.py` atual (stdlib pura, roda em 3.10 e 3.12) já satisfaz.

### 5.3 `CLAUDE_PLUGIN_ROOT` não é confiável
Vazia nos dois ambientes; no browser causou falha até o script ser localizado com `find`. **O motor precisa se auto-localizar** — e o `workflow.py` já faz certo: `PLUGIN_ROOT = Path(__file__).resolve().parent.parent` (Brand Boost — `bin/workflow.py:25`). Não depender de variável de ambiente para achar os próprios arquivos. Vale para qualquer linguagem (`__file__` em Python, `import.meta.url`/`__dirname` em Node).

### 5.4 A montagem de scripts varia por ambiente
No browser, o plugin TS teve **só o `SKILL.md` montado** — os scripts não estavam no filesystem. Causa não confirmada (provável: plugin não instalado/sincronizado nesse ambiente; possível: montagem incompleta, há relato de bug análogo). **Agnóstico à linguagem** — atingiria Python igual. Registra um risco de portabilidade para qualquer motor baseado em script empacotado, a validar antes de assumir o browser/mobile como alvo de execução.

---

## 6. Decisão: Python (stdlib) no motor de Playbook

Com a viabilidade empatada (ambos rodam), a decisão é de engenharia. **Python, por margem** — sem resíduo de custo afundado (a lógica validada é portável; os testes são o contrato que tornaria um porte seguro):

1. **Precedente do ecossistema real.** Scripts de plugin Cowork oficiais: 26 Python, 0 Node. O motor vive como script de plugin — o precedente relevante é Python.
2. **Zero-build total.** Python stdlib roda direto. TS roda sem build só no caso *type-only* (via `--experimental-strip-types`, experimental); TS completo (enums, decorators) exige `tsx` (rede) ou build.
3. **Já roda na VM.** O `workflow.py` atual executa em 3.10 e 3.12 sem ajuste.
4. **Tipagem é o único pró forte do TS** — e é largamente coberta por type hints + `mypy` + os 122 testes, numa base de ~1k linhas.

**Descartes explícitos** (para não reabrir):
- **Custo afundado** não conta como argumento — a lógica porta para qualquer linguagem.
- **"Protocolo em markdown" para a lógica** foi rejeitado: não-determinístico ("humor do modelo"). Lógica complexa exige código determinístico.
- **"Node em JS puro"** é opção dominada: entra no ecossistema JS sem o benefício (tipos) e perde o zero-build do Python.

**O que inverteria para TypeScript:** o Playbook crescer muito além de ~1k linhas, ser mantido por **equipe** (não solo), ou preferência explícita por tipagem imposta acima da simplicidade operacional. Nesse caso o TS é plenamente viável no Cowork (comprovado) — seria escolha defensável, não erro.

**Divisão de papéis por linguagem:**

| Camada | Linguagem | Motivo |
|---|---|---|
| Motor de Playbook | **Python (stdlib)** | Zero-dep, determinístico, precedente, já roda |
| Guard / invariantes | **bash fino** | Cola idiomática de hook |
| Skills (capacidade) | **markdown + scripts** | Padrão de Agent Skills |

---

## 7. Referências

- **Cowork / Skills:** `claude.com/docs/cowork/guide/plugins` · `claude.com/docs/cowork/3p/extensions` · `support.claude.com/.../claude-cowork-architecture-overview` · `anthropic.com/engineering/equipping-agents-for-the-real-world-with-agent-skills`
- **Repositórios:** `github.com/anthropics/knowledge-work-plugins` (precedente) · `github.com/rafaelbortoli/cowork-runtime-test` (sondas deste estudo)
- **Brand Boost:** `bin/workflow.py` · `docs/bb_60/proposta-plataforma-cowork.md` · `docs/bb_60/prd.md`
