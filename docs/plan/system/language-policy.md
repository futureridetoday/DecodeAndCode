---
# about
name: language-policy
type: doc
project: DecodeAndCode
description: Norma de linguagem do projeto — nenhuma linguagem é proibida, publica os ambientes de execução medidos e fixa 3.10 como versão-alvo dos scripts. Documento normativo curto, ancorado em medição
tags: [norma, linguagem, python, javascript, html, runtime, dependencias, cowork]

# history
author: Bortoli
created: 2026-07-24
status: draft
version: 1.0.0
updated: ""

# system
scope: project
auto_load: false
dependencies: []
---

# Política de linguagem — norma

> **Este documento é norma, não plano.** Não tem `plan_id` e não entra em `_planos.md`.

Esta norma é curta de propósito. O princípio de quando usar código já existe e é do projeto inteiro
— falta apenas publicar os fatos de ambiente e a versão-alvo dos scripts.

---

## 1. Nenhuma linguagem é proibida

Python, JavaScript/TypeScript, HTML, shell — a escolha é de engenharia, decidida por adequação à
tarefa. A lista não é exaustiva e não é uma lista de permissões: linguagem fora dela não precisa de
autorização, precisa de justificativa técnica como qualquer outra decisão.

**O código de plugin não roda na máquina do usuário.** Roda numa VM Linux gerenciada, que já tem
Python e Node nativos — ninguém instala runtime nem configura nada via terminal. Evidência medida em
[`estudo-runtime-e-dependencias.md`](estudo-runtime-e-dependencias.md).

---

## 2. O critério de escolha já é norma

Quando usar código e quando usar markdown está definido em
[`CLAUDE.md` — seção *Linguagem*](../../../.claude/CLAUDE.md): código quando o resultado é
previsível e a repetibilidade é essencial; markdown quando a instrução exige julgamento, tom ou
raciocínio contextual.

Esta norma não recopia esse critério — apenas o aplica aos scripts, que é o domínio dela.

A consequência prática: **função e ferramenta podem ser código, não prompt**. Um script entrega o
mesmo resultado a cada execução; um markdown entrega o que o modelo interpretar naquela vez. Onde
essa variação não é desejável, ela é defeito.

**Precedente do ecossistema:** os repositórios oficiais da Anthropic escrevem skills majoritariamente
em Python — `anthropics/knowledge-work-plugins` tem 26 scripts Python e nenhum Node (medido no
estudo); `anthropics/skills` é majoritariamente Python (levantamento do autor, 2026-07). Escrever a
lógica de uma skill em código é o padrão, não a exceção.

---

## 3. Ambientes de execução — fato, não regra

Medições de 2026-07-13 (sondas do estudo) e 2026-07-24 (máquina local):

| Ambiente | Python | Node | Arquitetura | OS |
|---|---|---|---|---|
| Cowork (nuvem) | **3.10.12** | v22.22.3 | ARM64 | Ubuntu 22.04 |
| Claude no browser | 3.12.3 | presente | x86_64 | Ubuntu 24.04 |
| macOS local (`/usr/bin/python3`) | 3.9.6 | — | ARM64 | — |

Esta tabela **não é uma regra a obedecer** — é informação a consultar. Quem escreve um artefato
distribuído verifica aqui onde ele vai rodar. Não há permissão a pedir.

Dois fatos derivados que custam caro se ignorados:

- **Os ambientes são heterogêneos** — arquitetura, versão e utilitários variam (`jq` existe no Cowork,
  não no browser). Artefato que depende de um utilitário externo quebra ao trocar de ambiente.
- **`CLAUDE_PLUGIN_ROOT` não é confiável** — veio vazia nos dois ambientes medidos. Todo script deve
  se auto-localizar (`Path(__file__).resolve()` em Python, `import.meta.url` em Node).

---

## 4. Versão-alvo: Python 3.10

**3.10 é o alvo porque é o que o Cowork tem.** Desenvolver acima disso permite usar sintaxe que a VM
não aceita, e o erro só aparece em produção; desenvolver em 3.10 torna essa classe de defeito
impossível de escrever sem perceber.

| Onde | Como |
|---|---|
| Artefato distribuído | Shebang `#!/usr/bin/env python3` — na VM do Cowork, `python3` **é** 3.10. O artefato permanece agnóstico |
| Verificação local e CI | Roda em **3.10 explícito** — é o harness que fixa a versão, não o artefato |
| macOS local | `/usr/bin/python3` é 3.9.6 e não se atualiza (system Python da Apple, sob SIP). Instalar ao lado: `brew install python@3.10`. **Não** trocar o `python3` global — afeta outros projetos |

Paridade de patch não é buscada: o Cowork tem 3.10.12, o homebrew oferece 3.10.20. O que importa é o
piso de sintaxe.

O harness (`scripts/test-python.sh`) **exige** 3.10 e falha com instrução se não o encontrar. Passar
os testes em 3.10 é o que comprova compatibilidade com o Cowork.

---

## 5. Dependências externas

Stdlib não precisa de nada. `pip` e `npm` precisam de rede, e o egress pode ser restrito.

Não é proibição — é custo. Quem usa dependência externa **declara o fallback** para o caso de a
instalação falhar. Sem fallback declarado, o artefato tem um modo de falha não tratado, o que é
defeito comum, não violação de política.

---

## 6. O que esta norma não faz

Deliberado — a ausência é a política:

- **Não mantém lista de linguagens permitidas.** A lista viraria o próximo bloqueio.
- **Não cria gate nem processo de aprovação** para usar dependência ou linguagem.
- **Não impõe regra que não esteja ancorada em medição.** Onde não há dado, não há regra: registra-se
  como não-verificado. Java (JVM), por exemplo, não foi medido em ambiente nenhum — o que não o
  proíbe, apenas significa que quem o usar mede antes.

---

## Referências

- Evidência: [`estudo-runtime-e-dependencias.md`](estudo-runtime-e-dependencias.md)
- Critério código ↔ markdown: [`.claude/CLAUDE.md`](../../../.claude/CLAUDE.md)
- Sondas reprodutíveis: `github.com/rafaelbortoli/cowork-runtime-test`
- Precedente oficial: `github.com/anthropics/knowledge-work-plugins` · `github.com/anthropics/skills`
