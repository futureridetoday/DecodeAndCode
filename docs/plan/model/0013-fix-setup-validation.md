---
# about
name: fix-setup-validation
type: plan
project: DecodeAndCode
description: Correções e melhorias do setup do decode-and-code (plano 0009, plugin 2.3.1) medidas em quatro rodadas de validação — claude -p com remedição, CLI interativo e app desktop —, num esboço único, com C4 e C6 decididos na revisão e M8 levado ao backlog
tags: [decode-and-code, setup, huddle, guardrail, guideline, permissao]

# alvo
plan_id: "0013"
plan_size: médio
plan_type: fix
core: model
module: fix-setup-validation
block: ""

# history
author: Claude
created: 2026-11-18
status: approved
version: 1.0.0
updated: ""
approved_by: Bortoli
approved_at: 2026-11-19

# system
scope: project
auto_load: false
dependencies: []
---

# Correções do setup medidas na validação do 2.3.1

> **Esboço para discussão item a item.** Cada item tem um código (`C` defeito, `M` melhoria) que se
> mantém até a aprovação. C4 e C6 foram decididos pelo humano em 2026-11-19, na revisão; os que o
> gate B cortou ficam listados com o motivo, reabríveis na discussão.

## Objetivo

**Clarificar.** O setup do 2.3.1 funciona de ponta a ponta, mas na sessão real pelo app pede
permissão para comandos que a skill pré-aprova, e o modelo leu código do plugin e a norma para
descobrir o que a skill não diz. Métrica: no app, uma sessão de setup completa com **zero** pedidos
de permissão para `dc.py` e **zero** leituras de arquivo do plugin ou da norma (hoje, na sessão do
app registrada no `0009`: 7 pedidos de `dc.py` no 2º turno, 2 pedidos por `sed`/`grep` na norma e
`grep` no código do plugin). Beneficiário: quem roda o setup num projeto novo.

**Evitar.**

| Alternativa | Por que não basta |
|---|---|
| Liberar `dc.py` no `settings.json` do projeto pelo setup | `D-05` do `0009` limita o que o setup escreve, e permissão é escolha da pessoa, não do plugin |
| Documentar as falhas no README | O README não viaja no pacote; quem erra é o modelo, que lê a `SKILL.md` |
| Não fazer nada até o primeiro terceiro | A falha de permissão (C1) e o bootstrap não proposto (C2) já foram medidos; não dependem de terceiro |

A maior parte dos itens **é texto de skill**, não código: C1, C2, C3, C4, C5, C7, C9 e M7 mudam só
`setup/SKILL.md` ou `huddle/SKILL.md`.

**Reduzir.** Texto nas duas skills para tudo o que é instrução; código só onde o defeito está no
script (C6, C8) ou onde uma linha de formato evita releitura medida (M3, M4).

## Gates

| Gate | Resposta |
|---|---|
| **A — necessidade real** | **Sim, para os itens mantidos.** Todos foram medidos nas rodadas de 2026-11-16 a 2026-11-17 (registro no `0009`, *Validação ponta a ponta → Resultado*, `L-12` a `L-18`) e na sessão do app, registrada no mesmo *Resultado* em 2026-11-19. C5 é inferido: o mesmo heredoc com JSON que o Claude Code barrou no setup (`L-15`) está no `huddle/SKILL.md`, linha 62; não houve sessão de `huddle` que o medisse |
| **B — mínimo viável** | Cortados, reabríveis: **M1** e **M2** (mudam o contrato de `criar-guideline`, `adicionar-guardrail` e `setup-registrar` para poupar passos; com C1 os passos deixam de pedir permissão, e o ganho restante é latência — remedir depois de C1); **M5, parte de código** (testar caminho relativo no `adicionar-guardrail`: falta medir em que payload real o `file_path` chega relativo; a parte de texto fica); **M6** (aviso de `paths_pending` que já casa: não há incidente, e o aviso não pega o caminho com erro de digitação, que é o risco da `L-11`). Fora deste plano: **M8**, desenho próprio, registrado como `B-08` no `_backlog.md`. Fora por restrição: `intake/SKILL.md` (4095/4096 bytes) não é tocado |

## Itens

### Correções

| # | Gravidade | Defeito medido | Onde | Proposta |
|---|---|---|---|---|
| C1 | alta | No app, o modelo pediu em prosa a descrição do 2º guardrail e encerrou o turno; a resposta abriu turno novo e a pré-aprovação do `allowed-tools` caiu: 7 comandos `dc.py` pediram permissão (gravados no `.claude/settings.local.json` do projeto de teste). No 1º turno, 49 passos sem nenhum pedido (`L-17`) | `setup/SKILL.md` | Toda pergunta, inclusive aberta, pela ferramenta de perguntas — exemplos como opções mais o texto livre; não encerrar o turno antes da etapa 6 |
| C2 | alta | Etapa 0 diz "Sem `.claude/` e `docs/`"; no projeto que tinha as duas pastas e não tinha a norma, o bootstrap não foi proposto | `setup/SKILL.md`, etapa 0 | Propor o bootstrap quando faltar `.claude/`, `docs/` **ou** a norma em `<plan_root>/system/`; dizer que o bootstrap nunca sobrescreve |
| C3 | média | A skill não explica a saída do `setup-escopo`; na sessão do app o modelo leu o código do plugin com `grep` para entendê-la (`0009`, *Resultado*) | `setup/SKILL.md`, etapa 0 | Uma frase: habilitado = `enabledPlugins`, marketplace = `extraKnownMarketplaces`; `--aplicar` acrescenta só o que falta |
| C4 | média | `criar-guideline` recusa arquivo da raiz pelo nome (`tailwind.config.ts`, `L-18`) e padrão com chaves (`{ts,tsx}`) — `rules._problema_de_padrao` | `setup/SKILL.md` | **Decidida pelo humano em 2026-11-19:** documentar a restrição na skill — arquivo da raiz entra como `**/<arquivo>`, e não se usam chaves. A recusa é a `D-02` do `0007`, que fica; a `L-01` do `0007` segue aberta |
| C5 | média | `huddle/SKILL.md` (plano `0008`) manda heredoc `<<'FIM'` com JSON no `criar-guideline` da promoção; o Claude Code barra ("Contains brace with quote character") — resto da `L-15` | `huddle/SKILL.md`, linha 62 | A mesma troca já feita no setup: JSON gravado em arquivo e passado por `<` |
| C6 | média | O guardrail barra o `Edit` que **remove** o problema: `guardrail._avaliar` aplica o detector a todo valor string de `tool_input`, `old_string` incluído (H-02 nos três testes) | `guardrail.py` | **Decidida pelo humano em 2026-11-19:** `_avaliar` deixa o `old_string` de fora; `file_path` e `new_string` seguem avaliados. Cumpre a `D-11` do `0009` — o guardrail barra o que a escrita contém, e o `old_string` é o que sai —, não a revisa |
| C7 | baixa | O modelo afirmou que o colega "recebe a oferta de instalação" ao abrir o projeto; a doc não garante (`L-07`) | `setup/SKILL.md`, etapa 0 ou fecho | Dizer: cada pessoa instala uma vez por clone; a habilitação commitada não baixa o plugin |
| C8 | baixa | `setup.perfil` grava linha em branco duplicada depois de `## Perfil` (três testes) | `setup.py`, `perfil` | Corrigir a montagem do corpo; teste que compara o texto gravado |
| C9 | baixa | As seções `###` *JSON pelo stdin*, *Formato do guardrail* e *Tipos do huddle* ficaram no meio de `## Etapas`; as etapas 4 a 6 aparecem sob *Tipos do huddle* | `setup/SKILL.md` | Mover as três seções para depois da etapa 6 |

### Melhorias

| # | Atrito medido | Onde | Proposta | Situação |
|---|---|---|---|---|
| M1 | ~5 passos por aprovação (Write JSON, `criar-guideline`, Write JSON, `setup-registrar`, às vezes lint) | `dc.py`, `rules.py`, `guardrail.py`, `setup.py` | `criar-guideline` e `adicionar-guardrail` aceitarem a chave do setup e registrarem sozinhos → 2 passos | **Cortada pelo B**, remedir após C1 |
| M2 | Arquivo temporário para cada JSON | `dc.py` | `--json-arquivo`, ou flags simples no `setup-registrar` | **Cortada pelo B**: o caminho por arquivo e `<` já passa no `allowed-tools` (remedição de 2026-11-17) |
| M3 | O modelo releu `package.json`, `components.json` e `README` com `Read` nos três testes; `### <caminho>` colide com títulos dos trechos (`L-12`) | `descoberta.formatar` | Cerca de código em volta de cada trecho | Mantida |
| M4 | O modelo usou `sed`/`grep` na norma para *Huddle* e *Camada normativa*; no app, 2 pedidos de permissão | `dc.py`, `_explicar` | `explicar` aceitar nome de seção (`huddle`, `camada-normativa`), reaproveitando `normas.secoes` | Mantida |
| M5 | Um regex gerado não barrava caminho relativo | `setup/SKILL.md`; `guardrail.adicionar` | Texto: modelo de detector para "pasta X, conteúdo Y". Código: `adicionar-guardrail` provar também o caminho relativo | Texto mantido; **código cortado pelo B** até medir o payload |
| M6 | `paths_pending` não sai sozinho (`L-05` do `0007`, `L-11` do `0009`) | `rules.lint_guideline` ou hook `InstructionsLoaded` | Avisar quando a rule tem `paths_pending` e o caminho já casa arquivos | **Cortada pelo B** |
| M7 | No app, `.claude/settings.local.json` recebeu permissões; a pessoa não sabe o que vai para o git | `setup/SKILL.md`, fecho | Listar o que vai para o git e avisar que `settings.local.json` é pessoal (`D-05` impede escrever no `.gitignore`) | Mantida |
| M8 | Aviso de setup em todo projeto com o plugin no escopo de usuário (`L-10`) | — | "Não neste projeto", com a recusa guardada fora do repositório | **Fora deste plano:** `B-08` no `_backlog.md` |

## Tarefas

- [ ] C1 — `setup/SKILL.md`: toda pergunta pela ferramenta de perguntas, aberta inclusive; turno único até a etapa 6
- [ ] C2 — `setup/SKILL.md`, etapa 0: condição do bootstrap inclui a norma ausente; bootstrap nunca sobrescreve
- [ ] C3 — `setup/SKILL.md`, etapa 0: o que a saída do `setup-escopo` significa
- [ ] C4 — `setup/SKILL.md`: arquivo da raiz como `**/<arquivo>`, sem chaves em `paths`
- [ ] C5 — `huddle/SKILL.md`: JSON por arquivo e `<` no `criar-guideline` da promoção
- [x] C6 — `guardrail._avaliar` ignora `old_string`, com o teste escrito antes da correção
- [ ] C7 — `setup/SKILL.md`: cada pessoa instala uma vez por clone
- [x] C8 — `setup.py`, `perfil`: sem linha em branco duplicada, com teste
- [ ] C9 — `setup/SKILL.md`: seções de referência depois da etapa 6
- [ ] M3 — `descoberta.formatar`: trecho em cerca de código, com teste
- [ ] M4 — `dc.py explicar <seção>`, com teste; a `setup/SKILL.md` aponta o comando
- [ ] M5 — `setup/SKILL.md`: modelo de detector para "pasta X, conteúdo Y"
- [ ] M7 — `setup/SKILL.md`, fecho: o que vai para o git e o que é pessoal
- [ ] Remedir no app: uma sessão de setup completa, contando pedidos de permissão e leituras do plugin

## Oráculo

| Alvo | Como se sabe que funcionou |
|---|---|
| C1, C3, M4, M7 | Sessão de setup no app com o pacote novo: zero pedidos de permissão para `dc.py`, zero `grep`/`sed` em arquivo do plugin ou da norma, `settings.local.json` do projeto sem entrada nova |
| C2 | Projeto com `.claude/` e `docs/` sem a norma: a etapa 0 propõe o bootstrap |
| C5 | `grep "<<'FIM'"` em `huddle/SKILL.md` sem ocorrência com JSON |
| C8 | Teste de `setup.perfil` compara o arquivo gravado, sem duas linhas em branco seguidas |
| C9 | `lint_skill` aprova; as etapas 0 a 6 ficam contíguas sob `## Etapas` |
| M3 | Teste de `descoberta.formatar` com trecho que contém `###`: o título fica dentro da cerca |
| C4 | Sessão de setup no app com o pacote novo: a guideline de arquivo da raiz é gravada na primeira tentativa, sem recusa do `criar-guideline` |
| C6 | Teste de `guardrail._avaliar`: `Edit` cujo `old_string` casa o detector e cujo `new_string` não casa — recusado antes da correção (vermelho), liberado depois (verde); com o `new_string` casando, segue recusado |

## Independência

Dispensada no médio, registrada porque a revisão a levantou. C5 (`huddle/SKILL.md`, do `0008`) e C6
(`guardrail.py`) passariam isolados do resto: cada um deixa o sistema válido sozinho. Ficam aqui
porque são **um lote de correções da mesma validação**, com uma remedição só no fim — separados, cada
plano pagaria aprovação e remedição próprias para uma tarefa. As melhorias M3, M4, M5 e M7 ficam
pelo mesmo motivo: cada uma remove uma releitura ou um pedido de permissão medido na mesma sessão, e
a métrica do *Objetivo* só fecha com elas.

## Lacunas

| # | Lacuna | Detalhe |
|---|---|---|
| L-01 | **`L-04` do `0009` segue aberta** | Onde o `systemMessage` aparece no app aguarda relato do humano; não muda nenhum item daqui |
| L-02 | **Texto de skill não tem teste que reproduza o defeito** | O tipo `fix` pede o teste vermelho antes da correção. C1, C2, C3, C4, C7, C9, M5 e M7 mudam só texto de `SKILL.md`, e o comportamento que corrigem é do modelo numa sessão real: o oráculo deles é a remedição no app (*Oráculo*), medição reportada e não gate automático, como a *Validação ponta a ponta* do `0009`. Têm teste vermelho→verde só C6 e C8; M3 e M4 são melhoria, com teste novo; C5 e C9 têm checagem por `grep` e `lint_skill` além da sessão |

## Fonte

- [`0009-onboard-new-project.md`](0009-onboard-new-project/0009-onboard-new-project.md), *Validação ponta a ponta → Resultado*, `L-04`, `L-07`, `L-10` a `L-18`, `D-05`, `D-11`
- [`0007-add-norm-writers.md`](0007-add-norm-writers.md), `L-01` e `L-05`
- [`modelo-dev-units.md`](../system/modelo-dev-units.md), *Antes do plano*, *O que cada porte carrega* e *Tipo de plano*
- [`_backlog.md`](../_inbox/_backlog.md), `B-08` — o M8, fora deste plano

## Backlog

<!-- backlog:start -->
- [ ] C1 — `setup/SKILL.md`: toda pergunta pela ferramenta de perguntas, aberta inclusive; turno único até a etapa 6
- [ ] C2 — `setup/SKILL.md`, etapa 0: condição do bootstrap inclui a norma ausente; bootstrap nunca sobrescreve
- [ ] C3 — `setup/SKILL.md`, etapa 0: o que a saída do `setup-escopo` significa
- [ ] C4 — `setup/SKILL.md`: arquivo da raiz como `**/<arquivo>`, sem chaves em `paths`
- [ ] C5 — `huddle/SKILL.md`: JSON por arquivo e `<` no `criar-guideline` da promoção
- [x] C6 — `guardrail._avaliar` ignora `old_string`, com o teste escrito antes da correção
- [ ] C7 — `setup/SKILL.md`: cada pessoa instala uma vez por clone
- [x] C8 — `setup.py`, `perfil`: sem linha em branco duplicada, com teste
- [ ] C9 — `setup/SKILL.md`: seções de referência depois da etapa 6
- [ ] M3 — `descoberta.formatar`: trecho em cerca de código, com teste
- [ ] M4 — `dc.py explicar <seção>`, com teste; a `setup/SKILL.md` aponta o comando
- [ ] M5 — `setup/SKILL.md`: modelo de detector para "pasta X, conteúdo Y"
- [ ] M7 — `setup/SKILL.md`, fecho: o que vai para o git e o que é pessoal
- [ ] Remedir no app: uma sessão de setup completa, contando pedidos de permissão e leituras do plugin

2 de 14 tarefas concluídas · atualizado em 2026-11-19
<!-- backlog:end -->
