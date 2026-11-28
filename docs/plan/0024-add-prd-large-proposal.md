---
plan_id: "0024"
status: done
plan_type: feature
format_version: 2
plan_size: pequeno
approved_by: Bortoli
approved_at: 2026-11-28
test: .claude/skills/decode-and-code/scripts/tests/test_prd_grande.py
state: verified
verified_at: 2026-11-28
---

# Proposta em forma de PRD no plano grande

## Objetivo

No plano grande, a proposta passa a carregar métricas de sucesso, restrições rastreáveis e fases de
entrega, e nenhuma restrição aprovada se perde até a entrega.

## Proposta

### Problema e de quem é

O problema é de quem conduz um plano grande com o DC: o usuário que aprova a proposta e Claude, que
a leva até as unidades. No grande, a proposta fica para trás depois do derive. As unidades executam
a parte técnica, e ninguém relê o porquê do plano.

Três coisas não têm onde ficar:

- **O que conta como sucesso.** O sinal da hipótese existe, mas não há o valor atual, o alvo nem
  como se mede.
- **As restrições.** Requisitos não funcionais, limites e restrições herdadas de decisões
  anteriores não têm lugar na proposta.
- **A ordem em que o usuário passa a ver valor.** Só existe a ordem técnica das unidades.

A evidência vem do teste final do DC 3.0 (E-05, `docs/codex/teste-final-amflow-relatorio.md`):

- o decode do 0028 do AmFlow reduziu 662 linhas a 199;
- a restrição L-15 e o oráculo inteiro ficaram de fora;
- os dois só voltaram porque o mantenedor recusou a proposta.

### Hipótese e MVP

**Hipótese:** acreditamos que dar à proposta do grande métricas de sucesso, restrições com
identificador rastreadas até as unidades e fases de entrega, para quem conduz um plano grande com o
DC, vai fazer com que nenhuma restrição aprovada se perca entre a proposta e a entrega. Teremos
confiança para seguir quando, nos dois próximos planos grandes:

- toda restrição tiver dono na aprovação das unidades (P5);
- nenhuma restrição precisar ser reposta pelo usuário numa recusa do P2 ou do P4.

Esse ponto de verificação vai para o huddle como `revisitar`.

**MVP:** as três seções na proposta do grande e o lint que confere o rastreio. Nada de documento
novo nem de comando novo.

### Solução conceitual

1. **As três seções**, dentro de `## Proposta`, quando o apetite é grande:
   - **Métricas de sucesso**: para cada métrica, o valor atual, o alvo e como se mede. A métrica é a
     que o Clarificar pergunta e se liga ao sinal da hipótese. Ela mede o resultado depois da
     entrega e não se confunde com o teste do plano inteiro (P8).
   - **Requisitos não funcionais e restrições**: cada item com o identificador `R-NN`, numerado por
     plano. Cobre desempenho, segurança, compatibilidade, limites e o que vem de uma decisão ou
     aprovação anterior.
   - **Fases de entrega**: a ordem em que o usuário passa a ver valor; em cada fase, o que ele
     consegue fazer ao fim dela. É ordem de produto. A ordem de execução continua no
     `## Depende de` de cada unidade.
2. **Na revisão (P3):**
   - cada história indica a sua fase;
   - o plano técnico do grande declara `## Teste do plano inteiro`, com o critério que sai das fases
     e dos `R-NN` que nenhuma unidade cobre;
   - quando a revisão mede o porte como grande e o apetite era menor, ela escreve as três seções e
     as mostra no P4 como acréscimo à proposta.
3. **No derive (P5):**
   - cada unidade cita, no critério de aceite, os `R-NN` de que cuida;
   - um `R-NN` que nenhuma unidade cita fica com o teste do plano inteiro.
4. **O lint, que é a parte determinística:**
   - `lint-plano` exige as três seções e `## Teste do plano inteiro` quando `plan_size: grande`;
   - todo `R-NN` tem dono, uma unidade ou o teste do plano inteiro;
   - `lint-unidade` recusa a citação de um `R-NN` que a proposta não declara.
5. **No codex**, uma linha sobre a crítica de Marty Cagan (*Inspired*) ao PRD. A crítica vale
   quando o PRD substitui a discovery. Aqui ele não substitui: a proposta continua saindo do fluxo
   de decodificação e dos gates A e B, e o PRD é só a forma de escrever.

**Onde muda:**

- **Codex:**
  - `artifacts.md`: *Proposta* e *Plano técnico*;
  - `stages.md`: *Decode*, *Revisão* e *Derive*;
  - `rules.md`: *Porte* e *Teste do plano inteiro*.
- **Skills:** `decode`, `review-plan` e `derive`.
- **Scripts:** `lint_plano.py` e `lint_unidade.py`, com os testes.

**Fontes técnicas:**

- o codex, nas seções acima;
- Marty Cagan, *Inspired*, já citado em *Os quatro riscos*;
- o relatório do teste final, em `docs/codex/teste-final-amflow-relatorio.md`.

### Apetite

Pequeno: uma entrega, que cabe numa sessão.

### Riscos

- **Valor:** a proposta do grande fica mais longa e pode virar formulário. A mitigação é valer só no
  grande, com três seções e nada mais, mantendo a regra "a proposta tem o tamanho do pedido".
- **Usabilidade:** o usuário lê mais no P2. As seções são curtas por construção: uma linha por
  métrica, por restrição e por fase.
- **Viabilidade técnica:** o rastreio é casar `R-NN` por texto, como o gate do `entrada-code` já faz
  com `NNNN-nn`. Não há dependência nova.
- **Viabilidade de negócio:** atrasa a release 3.0.0 em uma entrega. Deixar para depois custa mais:
  seções obrigatórias que entram depois exigem migrar os planos grandes já escritos no formato 2, e
  hoje não existe nenhum.

### Fica de fora

- O PRD para compartilhar, gerado por script a partir da proposta e do plano técnico. Só entra
  quando houver quem o leia fora do DC.
- Um comando que imprima o texto do `R-NN` no cold-start. Só entra se o code mostrar que faz falta.
- **A execução do teste do plano inteiro.** O codex já o exige no grande, mas nenhuma skill nem
  script o conduz: o plano fecha na aprovação da última unidade. Isso é um defeito à parte, para
  um plano `fix` próprio. Este plano só faz o plano técnico declarar o critério.
- O pequeno e o médio, que não mudam.
- Perguntas em aberto e não objetivos, que já existem como lacunas e como esta seção.

## Gates

**A, necessidade real: aprovado.** O problema aconteceu no teste final (E-05), num plano grande de
um projeto real, e o pedido explícito do usuário confirma. O sinal é mensurável sem instrumentação
nova: basta ler o rastreio dos `R-NN` na aprovação das unidades e as recusas registradas nos dois
próximos planos grandes.

**B, mínimo viável: aprovado, com cortes.** O desenho é o mínimo que produz o sinal: as três seções
e o lint do rastreio. Cortados:

- o PRD gerado por script;
- o comando do texto do `R-NN`;
- a execução do teste do plano inteiro, que vai para um plano `fix` próprio;
- qualquer mudança no pequeno e no médio.

## Aprovação da proposta

Aprovada por Bortoli em 2026-11-28 (P2).

## Recursos

| Recurso | Tipo | Onde entra |
|---|---|---|
| `scripts` | guideline | nas mudanças em `lint_plano.py` e `lint_unidade.py` |
| `scripts/test-python.sh` | runner | no teste da entrega |

## Histórias

**H1.** Como usuário que aprova um plano grande, quero ver na proposta as métricas de sucesso, as
restrições numeradas e as fases de entrega, e no plano técnico o critério do teste do plano
inteiro, para decidir sabendo o que conta como sucesso e o que não pode se perder.

- **Critério:**
  - o `lint-plano` reprova um plano grande do formato 2 quando falta, dentro de `## Proposta`,
    qualquer uma das três seções `### Métricas de sucesso`,
    `### Requisitos não funcionais e restrições` e `### Fases de entrega`;
  - reprova também quando falta `## Teste do plano inteiro`;
  - aprova o mesmo plano com as quatro;
  - um plano médio ou pequeno sem elas continua aprovado;
  - um plano do formato 1 não muda.

**H2.** Como usuário que aprova as unidades de um plano grande, quero que cada restrição `R-NN`
tenha dono, uma unidade ou o teste do plano inteiro, para que nenhuma restrição aprovada se perca
até a entrega.

- **Critério:**
  - com as unidades derivadas no disco, o `lint-plano` de um grande reprova uma `R-NN` declarada que
    nenhum `## Critério de aceite` de unidade nem `## Teste do plano inteiro` cita, e aprova quando
    todas têm dono;
  - antes do derive, sem unidades, a checagem de dono não roda;
  - o `lint-unidade` reprova a unidade de um grande que cita uma `R-NN` que o plano não declara.

O aceite das duas é o teste `test_prd_grande.py` verde e a aprovação da entrega.

## Independência

É um plano só. A H1 sozinha deixa o sistema válido, mas não útil para o objetivo: as restrições
ganham lugar e continuam podendo se perder. A H2 depende da H1, porque só confere o dono de uma
`R-NN` que a H1 declarou. As duas são sequenciais e têm um objetivo único, como o caso que a seção
*Independência entre planos* manda manter junto.

Concorrência: o `_planos.md` não tem plano em desenvolvimento. O plano `fix` da execução do teste do
plano inteiro (H-03 do huddle), quando for aberto, vai mudar a aprovação final, e não estes lints.
Ele parte da seção `## Teste do plano inteiro` que este plano cria. A ordem recomendada é este
primeiro.

## Decisões e riscos

**Decisões:**

- **D-01, onde as seções ficam.** As três são `###` dentro de `## Proposta`, com os títulos exatos
  da H1. O lint casa o título, como já faz com as seções `##`.
- **D-02, quando vale.** Com `plan_size: grande`, no formato 2. O pequeno e o médio não mudam, e o
  formato 1 não é conferido.
- **D-03, como uma restrição se declara.** É um item de lista que começa por `R-NN`, opcionalmente
  em negrito, dentro de `### Requisitos não funcionais e restrições`: `^\s*-\s*\**R-(\d{2})\b`.
  Fora dessa seção, qualquer `R-NN` no texto é citação.
- **D-04, dono.** A checagem de dono fica no `lint-plano` e só roda quando o plano está na pasta
  `<NNNN-nome>/` e há unidades nela (`porte._listar_unidades`). Antes do derive, não há o que
  conferir. O derive passa a rodar o `lint-plano` no fim (passo 5 da skill), além do
  `lint-unidade`.
- **D-05, citação na unidade.** O `lint-unidade` lê as `R-NN` da unidade inteira e as confere
  contra o plano `<pasta>/<pasta>.md`, só quando esse plano é grande do formato 2. É o mesmo
  caminho que `lib.formato` usa para achar o plano da unidade.
- **D-06, acréscimo da revisão.** Quando a revisão mede grande e a proposta não tem as seções, ela
  as escreve com a primeira linha `*Acrescentada na revisão (P3).*` e as aponta na pergunta do P4.
  O lint não distingue o caso.
- **D-07, o codex muda nas seções que a proposta lista:**
  - *Proposta*: as três seções no grande e a linha sobre Cagan;
  - *Plano técnico*: `## Teste do plano inteiro` no grande;
  - *Decode*, *Revisão* e *Derive*: quem escreve o quê;
  - *Teste do plano inteiro*: de onde sai o critério.
  
  O texto das skills cita a seção do codex pelo título e não repete a regra, por causa do lint de
  repetição.
- **D-08, as fixtures.** Os planos grandes do formato 2 dos testes existentes
  (`test_formato_porte.py`, `test_formato_derive.py`, `test_entrega.py` e `test_dc.py`) ganham as
  seções onde o `lint-plano` os confere.

**Riscos:**

- **Fixtures antigas reprovadas.** Teste que monta um grande do formato 2 e espera o lint limpo
  passa a falhar. Mitigação: a D-08; a suíte inteira roda no fim.
- **Lint de repetição do codex** (`test_lint_codex.py`): frase igual no codex e numa skill reprova.
  Mitigação: as skills citam a seção pelo título.
- **Falso dono.** Uma `R-NN` citada só de passagem no critério conta como coberta. Aceito: o lint
  confere que a restrição tem lugar, e o julgamento sobre a cobertura fica na aprovação das
  unidades.

## Tarefas

- [x] Escrever `test_prd_grande.py` com os casos das duas histórias e rodá-lo vermelho
  (`dc.py verificar <plano> --dry-run`).
- [x] No `lint_plano.py`: as três seções e `## Teste do plano inteiro` no grande do formato 2, a
  declaração das `R-NN` e o dono quando há unidades (D-01 a D-04).
- [x] No `lint_unidade.py`: a `R-NN` citada precisa existir no plano grande (D-05).
- [x] Ajustar as fixtures dos testes existentes (D-08).
- [x] Codex: as seções da D-07.
- [x] Skills: `decode` (as seções quando o apetite é grande), `review-plan` (a fase de cada
  história, o `## Teste do plano inteiro` e o acréscimo da D-06) e `derive` (a `R-NN` no critério e
  o `lint-plano` no fim).
- [x] Conferir se `docs/recursos/` e o `README.md` descrevem a proposta e o plano grande; atualizar
  só o que descrevem.
- [x] Rodar `scripts/test-python.sh` inteiro, verde, e o `dc.py verificar <plano>`.
