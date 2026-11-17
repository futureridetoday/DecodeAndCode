# Orquestração — plano 0009-onboard-new-project

Você orquestra a execução deste plano. **Você não executa unidade** — unidades rodam em cold-start
próprio, uma por vez. Você prepara, revisa o que volta, e versiona depois de revisar.

## Como disparar cold-start

Uma forma só: a skill `implement <unidade>`. Ela roda sempre num subagent isolado (`context: fork`,
Sonnet), em qualquer sessão, e por isso não gasta o contexto de orquestração que você guarda.

## Regras que não mudam

- **Aprovação é do humano.** Nenhum `derive` sem ele dizer, explicitamente, para aquele alvo
- `state` e `verified_at` **nunca se editam à mão** — são projetados por script a partir do teste
- **Nunca editar o miolo entre marcadores** (`<!-- backlog:start -->`, `<!-- planos:start -->`)
- Quem executa unidade **entrega arquivos e relatório, não commita**
- Unidade insuficiente é defeito **da unidade**: a correção volta para quem deriva, como `L-XX`
- Ação irreversível ou que toque mais de 5 arquivos: apresentar antes, aguardar aprovação
- **Todo número que este prompt afirma é alegação.** Meça com o oráculo do projeto, nunca com um
  equivalente montado na hora

## Como revisar — leia antes da primeira entrega

`docs/plan/system/modelo-dev-units.md`, seção *Como revisar uma entrega*. Ela é a parte que decide a qualidade do que sai, e
não está copiada aqui de propósito: uma fonte por fato.

O que ela exige em uma linha: **medir em vez de reler o relatório**.

## Estado no momento em que este arquivo foi gerado

Gerado em 2026-11-15, sobre o commit `0ab4c2b`. **Confira antes de agir** — se divergir do que
você medir, o que vale é a sua medição, e a divergência merece ser reportada.

| | |
|---|---|
| Unidades derivadas | 7 |
| Verificadas | 0 |
| Próximo número livre | 08 |

A suíte **não** está contada aqui, e é deliberado: número declarado envelhece no primeiro commit.
Rode você mesmo, e **some as duas linhas `Ran`** — o total é a soma, nunca a última linha:

```
./scripts/test-python.sh
```

## A fila

1. `0009-01` setup-record — base de `setup.md`; a `05` e a `06` dependem dela.
2. `0009-02` project-scan — independente.
3. `0009-03` project-scope — independente; muda `config.json` e `lib._DEFAULTS`.
4. `0009-04` method-brief — independente.
5. `0009-05` setup-notice — depende da `01`.
6. `0009-06` setup-skill — depende de `01` a `05`: o teste de drift de `test_dc.py` reprova subcomando citado que não existe.
7. `0009-07` setup-docs — depende da `06`; unidade `norma`.

As unidades `01` a `04` são independentes no contrato, mas todas mexem em `dc.py` e `tests/test_dc.py`: rodar uma por vez, nunca em paralelo.

## Pendências do humano

- A `0009-07` é `norma` e o `lint-unidade` a recusa sem `approved_by` e `approved_at`: o humano aprova a unidade antes do `implement`.
- Depois da `0009-05`, abrir uma sessão neste repositório mostra o aviso de setup no lugar do de huddle, porque não há `docs/plan/system/setup.md` aqui. Some quando a *Validação ponta a ponta* rodar o setup neste repositório.
- A *Validação ponta a ponta* não é unidade: roda depois da `0009-06`, em sessão real, e o resultado é registrado no plano.

## Onde eu começaria, e por quê

Começar pela `0009-01`, que destrava a `05` e a `06`, e seguir a ordem da fila. Revisar cada entrega antes de commitar; a `06` pede leitura atenta do `SKILL.md`, porque a conversa não tem oráculo automático.

> Sugestão registrada, não decisão. Quem escolhe a ordem é o humano.

## Onde ler, antes de qualquer coisa

1. `.claude/CLAUDE.md` — invariantes e protocolo
2. `docs/plan/system/modelo-dev-units.md` — a norma
3. As skills, uma por modo:
   - `.claude/skills/review-plan/SKILL.md`
   - `.claude/skills/derive/SKILL.md`
   - `.claude/skills/implement/SKILL.md`
4. `docs/plan/model/0009-onboard-new-project/0009-onboard-new-project.md` — o plano, com *Escopo*, *Decisões* e *Lacunas*
