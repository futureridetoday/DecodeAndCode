---
# about
name: huddle
type: doc
project: AmFlow
description: Fila do que ainda não foi decidido — pauta da conversa recorrente entre o humano e o modelo. Nada aqui é norma; entrada resolvida sai daqui e vai para o lugar de coisa resolvida
tags: [huddle, decode-and-code, pre-norma, pauta]

# history
author: Bortoli
created: 2026-08-22
status: draft
version: 0.3.0
updated: 2026-08-22

# system
scope: project
auto_load: false
dependencies: []
---

# Huddle

**Nada aqui é autoritativo.** Entrada aberta é coisa que espera decisão, não regra a seguir. Quando
resolve, **sai** — para a norma, para uma guideline, ou para o `## Decisões` de um plano — e deixa uma
linha em *Fechadas* com a data e o destino.

Formato, tipos e gatilhos: [`decode-and-code-foundation`](../_inbox/decode-and-code-foundation.md),
seção *O `huddle` é fila, não fonte*. Aqui não se duplica a norma; aqui se usa.

> **Protótipo.** Escrito em 2026-08-22 antes da unidade `11` existir, por decisão do humano: a forma de
> saber como o huddle deve ser é ter um. O que sobreviver ao uso é o que a unidade formaliza.

---

## Como conversamos

Derivado do que funcionou na conversa de 2026-08-22, não do que soa bem. Cada linha é flagrável.

**O que eu trago**

- Toda afirmação vem com evidência, ou vem marcada como não medida. **O único ponto daquela conversa
  onde afirmei sem medir foi exatamente onde errei.**
- Discordo antes de concordar. Se acho que você está errado, na primeira frase — não na quarta.
- Errado se corrige em uma frase e segue. Sem cerimônia, sem reabrir.
- Digo o que decidi sem você, e digo o que não sei.
- Tendo a **restringir demais** em tempo de desenho. Restrição parece rigor até alguém mostrar o que
  ela mata — aconteceu duas vezes no mesmo dia.

**O que me ajuda de você**

- *"Não entendi"* é informação, e é mais rápido que eu adivinhar entre três leituras.
- Ceticismo curto diante de resposta fina — *"mudou só isso?"* pegou uma lacuna real.
- *"Chega de desenhar, vamos começar"* quando a conversa espirala.
- **Retrospectiva**: qual decisão envelheceu mal, e por quê. É a única coisa que eu não descubro
  sozinho — não carrego nada entre sessões que não esteja escrito.

**O que estraga**

- Concordar sem conferir.
- Eu responder três perguntas possíveis em vez de perguntar qual é.
- Fechar uma escolha sem registrar por que a outra foi recusada.

---

## Abertas

### H-01 · `pergunta` · 2026-08-22 · Claude

**A Fase 4 do `decode-and-code-foundation` ficou no fim, então os dois agentes não executam nenhuma
unidade do próprio plano.**

Antecipá-la para logo após a Fase 1 é só renumerar. O argumento a favor: se o planejador acelera o
trabalho, o lugar dele é antes das cinco unidades que sobram, não depois. O argumento contra: usar o
agente para derivar as unidades que criam o agente é circular. Único acoplamento real — a `09` e a `10`
referenciariam a skill ainda chamada `dev-units` até a `06` renomear.

### H-02 · `pergunta` · 2026-08-22 · Claude

**Em 2026-08-22 o plano foi lido e considerado "ainda não pronto para desenvolvimento", e a razão não
ficou registrada em lugar nenhum.**

Ele passou pelo `dev-units review` — dois bloqueantes achados e corrigidos, `D-01` confirmada. Revisão
aprovada não é o mesmo que pronto, e quem decide isso é o humano. Mas sem o motivo escrito, a próxima
sessão vai propor `derive` de novo e receber a mesma recusa. **Uma hipótese levantada depois:** o plano
não enumera os artefatos de saída — decide mecanismos, não decide formas. Nunca foi confirmada.

### H-03 · `padrão` · 2026-08-22 · Claude

**Inferi decisão a partir de estado observado, e errei.**

Vi que o `hub/` não seguia clean architecture e concluí que a arquitetura tinha sido rejeitada como
escolha deliberada. Estava declarada em dois documentos desde o início — o que eu tinha medido era o
desvio, não o desenho. O humano corrigiu.

O padrão a vigiar não é "errei uma vez": é que **estado observado não carrega intenção**, e eu tendo a
preencher a intenção que falta. Vale para código sem norma, para norma sem código, e para qualquer
"deve ter sido de propósito".

### H-04 · `padrão` · 2026-08-22 · Claude

**Terceira ocorrência do mesmo ponto de inflação: unidade cujo entregável é estrutura não tem contra o
que declarar `test:`.**

Já aconteceu em `skill-modules` (duas fases existiam pelo gate, não pelo produto), em
`checkout-exige-bundle` (150 linhas de plano para 8 de correção), e agora na `L-01` do
`decode-and-code-foundation`, onde três de onze unidades entregam markdown normativo.

O `B-01` do [`_backlog.md`](../_inbox/_backlog.md) é o registro disso e ainda não virou plano. A
terceira ocorrência é evidência de que não é acidente do caso.

### H-05 · `revisitar` · 2026-08-22 · Claude

**Symlink para materializar guidelines foi rejeitado — a premissa pode mudar.**

`.claude/rules/` aceita symlink, e ele resolveria a drift entre cópias de graça. Foi recusado em favor
de cópia versionada por três razões, e só uma delas é frágil: a ressalva do Cowork sobre symlink
apontando para fora do working directory. Se essa ressalva cair, ou se for confirmado que vale só para
*user-scope*, a decisão merece nova olhada — as outras duas razões (auditabilidade em qualquer commit,
funcionar sem ressalva a lembrar) continuam de pé sozinhas, mas o peso muda.

### H-06 · `divergência` · 2026-08-22 · Claude

**O `digital-twin-planner` declara quatro skills que não carrega.**

Ele lista `dependencies: [digital-twin-product, user-modeling, data-privacy-lgpd, data-architecture]`
— campo do AmFlow, que o Claude Code **ignora**. O campo nativo é `skills:`, e nenhum agente do
projeto, da Anthropic ou da Vercel o usa.

Contornado, não corrigido: está fora do escopo do plano em curso. Mas é defeito silencioso — o agente
opera acreditando ter contexto que não tem, e ninguém percebe porque o resultado é apenas *pior*, nunca
*quebrado*.

### H-07 · `observação` · 2026-08-22 · Claude

**Apareceu `catalog-distribution-only.md` não rastreado em `docs/plan/_inbox/`.**

Não é meu e não toquei nele. Registro porque plano no `_inbox` sem estar versionado é a condição em que
trabalho se perde — e porque não sei se é rascunho em curso ou sobra de algo abandonado.

---

## Fechadas

_Nenhuma ainda. A primeira conversa é que vai produzir as primeiras._

---

## Prompt de continuidade

Preenchido **na sexta**, com o estado fresco — mesma razão que vale para as entradas: no fecho do
trabalho, não na segunda tentando reconstruir. Colado numa sessão nova.

**Formato fixo, conteúdo variável.** Improviso semanal faria o prompt da semana 3 diferir do da 1 em
coisas que ninguém escolheu — a variância que este projeto existe para remover.

**O que ele não faz:** não descreve tom, e não copia entrada. Adjetivo sobre jeito de falar produz
imitação; o que reproduz a qualidade da conversa são as **condições**, e elas estão em
*Como conversamos*. Conteúdo copiado é drift — o prompt diz onde ler, nunca repete.

```markdown
Huddle da semana. Antes de responder qualquer coisa:

1. Leia `docs/plan/system/huddle.md` inteiro. `## Como conversamos` vale para esta conversa;
   `## Abertas` é a pauta.
2. Rode `git log --oneline -{N}` para ver o que se moveu desde {data do último huddle}.

**Desde o último huddle:** {commits, planos e unidades que mudaram — uma linha cada}

**Esperando decisão minha:** {H-XX nomeadas, uma linha cada}

**Ficou por fazer:** {o que o modelo deixou aberto, ou "nada"}

**Onde eu começaria, e por quê:** {H-XX + uma frase — sugestão, não pauta fechada}
```

O último campo é sugestão registrada, não decisão: quem escolhe a ordem da conversa é o humano. Está
ali porque *"digo o que decidi sem você"* também vale para o que eu decidiria.
