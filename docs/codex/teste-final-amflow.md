---
# about
name: teste-final-amflow
type: doc
project: DecodeAndCode
description: Plano do teste final do DC 3.0 antes da release — atualização e uso do plugin numa cópia descartável do AmFlow, do aviso de migração até a execução parcial de uma unidade
tags: [codex, redesign, teste, release]

# history
author: Bortoli
created: 2026-11-27
status: draft
version: 1.0.0
updated: ""

# system
scope: project
source: local
auto_load: false
checksum: ""
dependencies: [redesign-plan, migration-map, release]
---

# Teste final do DC 3.0 no AmFlow

## Objetivo

Antes da release, provar o DC 3.0 num projeto real que já usa o método. O teste vai da atualização
do plugin até a execução parcial de uma unidade, e registra tudo o que acontece, para achar erros e
oportunidades de melhoria. O resultado é um relatório. As correções não são feitas no teste: voltam
para a sessão do redesign.

## Onde e com o quê

| Item | Valor |
|---|---|
| Ambiente | `/Users/rafaelbortoli/Code/decode-and-code-experiments/dc3-amflow-final/` (fora dos dois repositórios, durável) |
| Projeto | cópia do AmFlow em `<ambiente>/amflow/`, no commit `030e36b` do `origin/dev`, o pai da aprovação do 0028 (`8be45e5`, 2026-11-17) |
| Plugin | zip `decode-and-code-3.0.0.zip`, construído do `dev` (`7325ba1`) com a versão 3.0.0 só no staging, carregado com `claude --plugin-dir <zip>` |
| Logs | `<ambiente>/logs/`: um `NN-<etapa>.jsonl` por chamada (`--output-format stream-json --verbose`), mais `.claude/log/` da cópia |
| Relatório | `docs/codex/teste-final-amflow-relatorio.md`, neste repositório, sem commit |

### Por que o 0028

- Na cópia, o plano é **grande com certeza**: o original saiu com 11 unidades. Isso exercita o derive
  com várias unidades, o handoff e o gate entre unidades (`entrada-code`).
- **Há gabarito.** O plano aprovado, as 11 unidades, as lacunas abertas durante a execução e o
  relatório executivo final existem no `origin/dev`. Por isso dá para comparar o plano refeito com o
  que de fato aconteceu.
- O rascunho de partida (`docs/plan/_inbox/decouple-resource-transport.md`, 661 linhas,
  `plan_size: grande`) e os dois estudos que o acompanham estão em `030e36b`. O número que o plano
  vai receber é 0028, o mesmo do original.

A alternativa, mais leve, é o rascunho `authorize-prompt-domain.md` (médio, hub/mcp). O risco dele é
a revisão medir o porte como pequeno: nesse caso, o teste não teria derive.

### O que se sabe do AmFlow antes de começar

- O DC está instalado no **escopo de projeto, versão 2.0.0**, pelo marketplace `future-ride-today`
  (`~/.claude/plugins/installed_plugins.json`). A atualização real é 2.0.0 → 3.0.0, e não 2.4 → 3.0.
- Há uma cópia da norma em `docs/plan/system/modelo-dev-units.md`, um huddle único em
  `docs/plan/system/huddle.md` e 27 planos no formato 1, organizados em pastas por core.
- O hub é Next.js com `vitest`, e o AmFlow local não tem `node_modules`.

## Salvaguardas

- O AmFlow real (`/Users/rafaelbortoli/Code/AmFlow`) não é tocado. A cópia sai por `git clone` local,
  e o `origin` é removido dela logo depois: não há como fazer push.
- O estado global do Claude Code não muda: nenhum `plugin install`, nenhum `marketplace add`. A
  versão 3.0 entra só por `--plugin-dir`, e a cópia desliga o `enabledPlugins` do DC no próprio
  `.claude/settings.json`.
- Neste repositório, o teste só escreve o relatório e o zip temporário, que é gitignorado e sai
  daqui para o ambiente. Sem commit, sem branch.
- Defeito do DC achado no teste não se corrige no teste. Se ele bloquear o teste, o remendo vai só
  na cópia do pacote do ambiente, e o relatório o registra como contorno.
- Na cópia, o orquestrador faz um commit por etapa, com tag `etapa-NN`, para que cada diff fique
  isolado. São commits locais, numa cópia sem remoto.

## Como cada etapa roda e o que se mede

Cada etapa é uma chamada:

```bash
claude -p --plugin-dir <zip> --permission-mode acceptEdits --output-format stream-json --verbose "<pedido>"
```

As conversas de mais de um turno continuam com `--resume <session_id>`. Assim, as aprovações P2, P4,
P5 e P7 chegam como respostas, e não embutidas no primeiro pedido. Isso é mais fiel do que o ponta a
ponta anterior.

Quem aprova é a sessão do teste, no papel do mantenedor. Ela lê o artefato antes de cada sim e o
recusa uma vez se achar um problema real; não inventa recusa. Cada decisão e o motivo dela vão para
o relatório.

Por etapa, o relatório registra:

- **Execução:** duração, turnos, custo, modelo e `permission_denials`, tirados do evento `result`.
- **Comportamento:** os comandos `dc.py` chamados e a saída de cada um, as perguntas feitas ao
  usuário e as seções do codex lidas.
- **Arquivos:** o diff da etapa.
- **Conferência independente:** os mesmos lints rodados pela sessão do teste, fora do modelo
  (`lint-plano`, `lint-unidade`, `migrar`, `normas`, `entrada-code`).
- **Desvios:** o que a skill manda e o modelo não fez, ou fez a mais.

## Etapas

| # | Etapa | O que valida | Para se |
|---|---|---|---|
| 0 | **Preparar.** Clonar o AmFlow, ir para `030e36b`, remover o `origin`, desligar o DC 2.0 na cópia e fazer o commit `etapa-00`. Construir o staging, trocar a versão para 3.0.0 no `plugin.json` do staging e rodar `empacotar_zip(staging)`. Mover o zip para o ambiente e conferir o conteúdo: versão, sem `reference/`, `verificar` e `validar` limpos | O artefato da release | O zip reprova |
| 1 | **Primeira sessão depois da atualização.** Um pedido neutro, com hooks e skills carregados. Conferir que só a versão 3.0.0 está carregada e capturar o aviso do `session_start` | Aviso de migração; nenhum resto do 2.0 | O aviso não aparece |
| 2 | **Migração.** Rodar `/decode-and-code:setup` e deixar que ele conduza a migração (`dc.py migrar`). Aprovar `--aplicar norma` e `--aplicar huddle`. Conferir que os planos do formato 1 só são listados e que o aviso some na sessão seguinte | 2.4 e K-10 num projeto real: huddle único, norma copiada, 27 planos | A migração perde ou corrompe dado |
| 3 | **Setup no que sobrar.** Foundation, guidelines e guardrails, só até onde der sem desfigurar o AmFlow. O setup usa a ferramenta de perguntas, e o modo `-p` pode não oferecê-la; o comportamento é registrado | K-10, e a primeira vez de uma skill interativa fora dos testes | — (vira achado) |
| 4 | **Decode** do rascunho existente, até a aprovação P2 | K-04: decode sem fork, partindo de um rascunho do formato 1 que já está no `_inbox` | A proposta não sai |
| 5 | **Review-plan**, até a P4: histórias, independência, decisões e unidades; plano com `format_version: 2` na raiz dos planos; número 0028 | K-01 a K-03 e o porte por entregas | O lint reprova sem conserto possível |
| 6 | **Derive**, até a aprovação das unidades | K-05: blocos da Definition of Ready, handoff, `## Aprovação das unidades` | Unidade sem os blocos |
| 7 | **Gate entre unidades.** Pedir o code da unidade 02 antes da 01 | `entrada-code` recusa | O gate deixa passar |
| 8 | **Code parcial** da primeira unidade que se testa localmente, de preferência uma de domínio puro (no original, a `02-package-spec`). Vai até o teste escrito e vermelho e, se a unidade for curta, até o verde e o `verificar`. Se a unidade pedir algo de fora (staging, Supabase), a parada do passo 6 do `code` é o próprio resultado | K-06: fork com Sonnet, `normas` no formato 2, `verificar --dry-run` pelo runner do AmFlow | — |
| 9 | **Aprovação P7.** `code aprovar`: o verde fecha a unidade; se não houver verde, a recusa (código 2) é o que se valida | O fecho, a projeção do backlog e o `_planos.md` | — |
| 10 | **Comparação com o gabarito.** Plano refeito contra o 0028 aprovado (`8be45e5`) e contra o que foi construído (`origin/dev`): porte, unidades, histórias, critérios e decisões; e as lacunas que a execução original só achou depois — quais o plano novo antecipou | Se o DC 3.0 planeja melhor, igual ou pior | — |
| 11 | **Relatório**, abaixo, e devolução à sessão do redesign | — | — |

## Formato do relatório

1. **Veredito:** pronto para a release, pronto com ressalvas, ou não pronto. O motivo em três linhas.
2. **Erros**, numerados `E-NN`. Cada um traz a severidade (bloqueia a release, grave ou menor), a
   etapa, a evidência (log e linha, ou arquivo), a causa provável no DC (`arquivo:linha`) e a
   correção sugerida.
3. **Oportunidades de melhoria**, numeradas `O-NN`. Cada uma traz a evidência e o custo estimado.
4. **Métricas por etapa** e o total.
5. **Comparação com o gabarito** (etapa 10).
6. **Limites do teste:** o que não foi exercido e por quê.
7. **Contornos** aplicados ao pacote, se houve.

## Depois do teste

O relatório volta para a sessão do redesign. Ali, cada erro vira correção, por PR para o `dev`, com
a aprovação da pessoa: a delegação D-15 terminou. Cada oportunidade é avaliada com a pessoa. A
release só sai depois disso e de um sim explícito.

## Autorizações que o teste pede

| # | O quê | Por quê | Sem ela |
|---|---|---|---|
| A-1 | `npm ci` em `amflow/hub/` (baixa dependências do registro npm) | O teste da unidade da etapa 8 roda com `vitest` | A etapa 8 para no teste escrito, sem rodar |
| A-2 | A sessão do teste aprova P2, P4, P5 e P7 no papel do mantenedor | Para o teste correr sem a pessoa | A pessoa aprova cada porta pela sessão do teste |
| A-3 | Opcional: a pessoa conduz a etapa 3 numa sessão interativa (`claude --plugin-dir <zip>` num terminal), enquanto a sessão do teste observa os arquivos e os logs | É o único jeito de ver a ferramenta de perguntas de verdade | A etapa 3 roda em `-p`, e o limite fica registrado |
