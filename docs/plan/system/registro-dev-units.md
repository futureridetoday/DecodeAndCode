---
# about
name: registro-dev-units
type: doc
project: DecodeAndCode
description: Registro do modelo de Unidades de Desenvolvimento — evidência, decisões e história deste projeto. O mecanismo, que qualquer projeto usa, vive em modelo-dev-units.md
tags: [dev-units, registro, decisoes, evidencia, historia]

# history
author: Bortoli
created: 2026-08-28
status: draft
version: 1.0.0
updated: 2026-08-28

# system
scope: project
auto_load: false
dependencies: []
---

# Registro — modelo dev-units

> **Este documento é registro, não mecanismo.** Guarda a evidência, as decisões e a história deste
> projeto por trás do modelo de Unidades de Desenvolvimento. O **mecanismo** — o que qualquer
> projeto que instala o método usa, e o que viaja no pacote — vive em
> [`modelo-dev-units.md`](modelo-dev-units.md). Este documento não viaja.

---

## Fundamentação — por que este modelo, e não outro

Ancorado em evidência empírica, não em tendência de mercado.

| Fonte | Dado | Implicação |
|---|---|---|
| **METR 2025** (RCT, 16 devs experientes, 246 tarefas) | Devs foram **19% mais lentos** com IA, mas estimaram ter sido **20% mais rápidos** | Percepção de progresso não é confiável. É preciso um **oráculo objetivo** |
| **DORA 2024** (~39 mil profissionais) | Adoção de IA acompanhada de **−1,5% throughput** e **−7,2% estabilidade**; causa apontada: o campo **esqueceu o small batch** | O gargalo é o **tamanho do lote**, não a ferramenta |
| **DORA 2025** (~5 mil profissionais) | "IA **amplifica** o que já existe"; **small batch amplifica os efeitos positivos** | Estrutura decide se a IA é ativo ou passivo |

**O que deliberadamente não foi adotado.** Spec-Driven Development (GitHub Spec Kit, AWS Kiro, Tessl)
é a corrente dominante, mas **nenhuma dessas ferramentas tem validação empírica**. A avaliação do
Spec Kit identificou incompatibilidade estrutural com este modelo: é **spec-first** (spec descartada
após uso) enquanto o modelo precisa de **spec-anchored**; tem baixo benefício relatado em sistemas
multi-módulo e brownfield; e produz **volume documental**, que é o modo de falha já vivido aqui.

Conclusão: adotar o **princípio** (spec-anchored, lote pequeno, verificação objetiva), não a
ferramenta.

---

## Diagnóstico medido — o padrão atual

Auditoria dos 18 arquivos `dev-units*.md` em `docs/mvp/20_delivery/`. **Este acervo não será migrado
agora** (ver *Estratégia de adoção*) — o diagnóstico justifica o desenho, não dimensiona retrabalho
imediato.

### O que funciona (preservar)

| Capacidade | Evidência |
|---|---|
| Fatia vertical como unidade | 86 unidades com contrato Entrada/Saída/Auth/Efeito/Erro |
| Rastreabilidade doc ↔ código | **90 referências** via comentário-cabeçalho (`proxy.ts:5` → `// AU-06`) |
| Registro de pendências | **11 lacunas** `L-XX` catalogadas |
| Preservação do racional | Notas `>` com trade-offs (ex.: invalidação antecipada em `AU-02`) |

### O que falta

| Lacuna | Medição |
|---|---|
| **Não define "pronto"** | **0 de 18** contêm critério de aceite |
| **Não liga à verificação** | **0 de 18** declaram teste — apesar de existirem **18 arquivos de teste** |
| **Não tem estado** | **18 de 18** em `status: draft`, com código em produção |
| **Não norma o lote** | De **1 a 18** unidades por arquivo; **22 de 86 (26%)** sem sequência numerada |
| **Não serve a cold-start** | Nenhuma declara arquivos a tocar nem normas aplicáveis |

---


## Rastreamento de objetivos

| Origem | Objetivo | Componente |
|---|---|---|
| Inicial | Módulo como organizador; pasta por módulo | 1 |
| Inicial | Adição como bloco aditivo | 1 |
| Inicial | Doc deixa de ser PRD e vira o módulo | 2 |
| Inicial | Índice do sistema com link para o módulo | 1 — a hierarquia de pastas é auto-descritiva |
| Novo | Nível core para evoluir sob Clean Architecture | 1, 3 |
| Novo | Modular com blocos (Google/email como bloco) | 1 |
| Novo | Documentação é código em produção | 2 |
| Novo | Código documentado com inteligência | 5 |
| Novo | Índice para orientar agente e desenvolvedor | 1 — idem |
| Novo | Princípios, guidelines, guardrails, referências | 3 |
| Novo | Revisão de plano sugerindo blocos | 4, modo `review` |
| Novo | Quebrar plano em fases e fases em unidades | 4 |
| Novo | **Cold-start com Sonnet sem pedido manual** | Conceitos, modo `derive` |
| Novo | **Backlog do plano com as unidades** | 2 — projeção |
| Novo | **Registro de conclusão na unidade e no plano** | 2 — duas projeções, uma fonte |
| Auditoria | 0/18 com critério de aceite | 2 |
| Auditoria | 0/18 ligados a teste | 2 |
| Auditoria | 18/18 `draft`; sem estado | 2 |
| Auditoria | Lote sem norma | 4 |
| Auditoria | 90 refs código↔doc; lacunas; racional | 5 |

---

## Decisões

### Resolvidas em 2026-07-19

| # | Decisão | Resolução |
|---|---|---|
| 1 | Norma de lote | **8 passos** (p90 das 86 unidades); sem sequência = incompleta |
| 2 | Grão de bloco e unidade | Bloco é **pasta**; unidade é **arquivo** (exigência do cold-start) |
| 3 | Como o estado é computado | **Declaração na spec** (`spec → teste`), granularidade de arquivo |
| 4 | Onde vive a normativa de domínio | **`<core>/system/`**; transversal em `<core-transversal>/system/` |
| 5 | Cobertura da normativa | Cada core ganha a sua, conforme for tocado |
| 6 | Localização dos docs | **`docs/plan/`** para o novo; acervo legado, se houver, somente leitura |
| 7 | Migração do acervo | **Não migrar agora** — tarefa futura |
| 8 | Modelo de desenvolvimento | **Sonnet** por padrão, com override do usuário |
| 9 | Core transversal | Dono de um módulo hospedado em outro core, sem produzir deployable próprio |
| 10 | Índice | **Eliminado** — substituído pela estrutura + backlog + consulta sob demanda |
| 11 | Vocabulário | Inglês em código, caminhos e frontmatter; **português na prosa** |
| 12 | Formato da unidade | Definido; referência viva em `docs/plan/model/0001-decode-and-code-foundation/01-config-and-paths.md` |
| 13 | Regiões de escrita | Script escreve só o bloco `# verificação` do frontmatter; nunca o corpo — **estendido em 2026-08-27** (plano `0002`): no arquivo do **plano**, escreve também `status`, na transição para `concluído` e apenas em médio e grande (ver *Regiões*) |
| 14 | Identificador da unidade | `unit_id` = `[nº plano]-[nº unidade]`, ex. `0001-02` — **revisa** o prefixo por módulo (`MC-`, `AU-`) |
| 15 | Teste inexistente | Gate de entrada exige teste **declarado**, não existente; `implement` escreve teste e código |
| 16 | Alvo do plano | Frontmatter com `core`/`module`/`block`; **um plano, um alvo** |
| 17 | Backlog | Marcadores `<!-- backlog:start -->` / `<!-- backlog:end -->`; script substitui só o miolo |
| 18 | Modelo por modo | **Não declarável em skill** — política operacional; automatizar exigiria agent. Continua verdadeiro para a skill — **revisado em 2026-08-26**: agent deixou de estar fora de escopo (ver *Modelos*) |
| 19 | Nome do plano | Mantém o nome ao sair do `_inbox` e **recebe prefixo numérico**; nunca vira `plano.md` |
| 20 | Regra de nome | `<intenção>-<alvo>[-<qualificador>]`, kebab-case, sem repetir o caminho — idioma **revisado** pela decisão 32 |
| 21 | Arquivo da unidade | `[nn]-[nome].md` — **revisa** "só o ID"; a estabilidade vem do `unit_id`, não do filename |
| 22 | Numeração do plano | **4 dígitos**, sequencial global, atribuída na aprovação; **pasta = nome do arquivo** |
| 23 | Numeração da unidade | **2 dígitos, por plano** — recomeça em `01` a cada plano novo |
| 24 | Tabela de planos | `docs/plan/_planos.md` — só aprovados; fonte da numeração; situação projetada |
| 25 | Avaliação de escopo | Teste de **independência** declarado na escrita do plano, auditado na revisão; concorrência checada em `_planos.md` |
| 26 | Divisão não bloqueia | Sinaliza e exige registro do porquê quando não se divide; **sem teto de unidades** |
| 27 | Alvo do plano | Sempre `core`/`module`/`block` — não existe alvo `system` |
| 28 | Tipo de unidade | `unit_type: dev \| plan`; a unidade `plan` produz um plano, com oráculo em `_planos.md` |
| 29 | Relação entre planos | Coluna **Origem** em `_planos.md` — qual unidade de qual plano o gerou |
| 30 | Natureza deste documento | **Norma**, não plano; a implementação é o plano que a instancia no projeto |

### Resolvida em 2026-07-24

| # | Decisão | Resolução |
|---|---|---|
| 31 | Linguagem e verificação dos scripts | **Python 3.10** (versão do Cowork), stdlib pura, `unittest` via `scripts/test-python.sh` — ver [`language-policy.md`](language-policy.md) |

> A pendência de infra de teste que travava este modelo não era técnica: vinha do bloqueio "sem
> Python", revogado pela [norma de linguagem](language-policy.md) com base em medição. O oráculo
> determinístico previsto no componente 5 deixa de depender de uma decisão em aberto.

### Resolvida em 2026-07-28

| # | Decisão | Resolução |
|---|---|---|
| 32 | Idioma do nome de plano, módulo e unidade | **Inglês** — **revisa** a decisão 20, que dizia pt-BR |

> **O conflito que a originou.** A decisão 20 exigia pt-BR no nome; o `.claude/CLAUDE.md` § *Idioma e
> Nomenclatura* exige inglês em identificadores e nomeia **módulo** entre eles. Como o nome do plano
> vira o `module` do frontmatter e a pasta no disco, as duas normas se contradiziam — e o conflito só
> apareceu quando o terceiro plano precisou de um nome que não fosse termo técnico.
>
> **Custo de migração: zero.** Os planos que existiam quando a decisão foi tomada já eram termos
> técnicos em inglês; nenhum renomeio.
>
> **O que não muda:** a prosa. Documentação, plano e unidade seguem inteiramente em pt-BR — o inglês
> vale para o identificador, nunca para o conteúdo.

### Pendentes

1. **Alinhamento do `CLAUDE.md`.** A regra de precedência foi **antecipada em 2026-07-19**. Restam as
   doze referências a `docs/mvp` e a desambiguação entre o **Core Engine** (visão futura, telemetria)
   e a pasta **`system/`** — ambas acompanham a migração.
> **Resolvidas nesta rodada:** as regiões no `index.md`, pelo mecanismo de marcadores (ver *Formato
> do plano*) — o mesmo padrão serve a qualquer arquivo com conteúdo humano e projeção de script no
> mesmo corpo; e a migração da unidade-referência, executada em 2026-07-20 junto com a criação do
> plano `0001` e da tabela `_planos.md`.
>
> **Resolvida em 2026-08-26:** a troca automática de modelo por modo, que só seria possível com
> agent. O gate abriu (ver *Modelos*), e o destino é `model:` declarado por agente — entregue pela
> `19` (planejador) e pela `20` (desenvolvedor).

---

## Referências

**Evidência empírica**
- METR (2025), *Measuring the Impact of Early-2025 AI on Experienced Open-Source Developer
  Productivity* — https://metr.org/blog/2025-07-10-early-2025-ai-experienced-os-dev-study/
- DORA (2024), *Accelerate State of DevOps Report* — https://dora.dev/research/2024/dora-report/
- DORA (2025), *State of AI-assisted Software Development* — https://dora.dev/dora-report-2025/

**Análise de métodos**
- Böckeler, B., *Understanding Spec-Driven Development: Kiro, spec-kit e Tessl* —
  https://martinfowler.com/articles/exploring-gen-ai/sdd-3-tools.html
- GitHub Spec Kit — https://github.com/github/spec-kit

**Interno**
- Norma de linguagem dos scripts: [`language-policy.md`](language-policy.md)
- Evidência que a fundamenta: [`estudo-runtime-e-dependencias.md`](estudo-runtime-e-dependencias.md)
- Padrão atual: `.claude/skills/decode-and-code/SKILL.md`
