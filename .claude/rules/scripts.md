---
name: scripts
description: Norma operativa de script — ativa sempre que um .py deste repositório é lido ou escrito.
paths: ["**/*.py"]
---

# Scripts

Ativa ao tocar qualquer `.py` deste repositório. Evidência de ambiente e o porquê do alvo de versão
ficam em [`language-policy.md`](../../docs/plan/system/language-policy.md), que esta guideline cita
e não repete.

## Versão-alvo: Python 3.10

| Onde | Como |
|---|---|
| Artefato distribuído | Shebang `#!/usr/bin/env python3` — na VM do Cowork, `python3` **é** 3.10. O artefato permanece agnóstico |
| Verificação local e CI | Roda em **3.10 explícito** — é o harness que fixa a versão, não o artefato |
| macOS local | `/usr/bin/python3` é 3.9.6 e não se atualiza (system Python da Apple, sob SIP). Instalar ao lado: `brew install python@3.10`. **Não** trocar o `python3` global — afeta outros projetos |

O harness (`scripts/test-python.sh`) **exige** 3.10 e falha com instrução se não o encontrar. Passar
os testes em 3.10 é o que comprova compatibilidade com o Cowork.

## Dependências externas

Stdlib não precisa de nada. Quem usa dependência externa (`pip`, `npm`) **declara o fallback** para
o caso de a instalação falhar — o egress pode ser restrito. Sem fallback declarado, o artefato tem
um modo de falha não tratado: defeito comum, não violação de política.

## Comando externo: mock prova a saída, nunca o comando montado

Mockar `subprocess.run` prova o que o script faz **com a saída** — o parsing, o ramo de erro, o
valor devolvido. Não prova nada sobre os **argumentos montados**: o comando errado recebe do mock
exatamente o que o mock mandar, e o teste fica verde.

| O que o critério afirma | O que o teste precisa ter |
|---|---|
| Comportamento da **saída** — parsing, ramo de falha, valor devolvido | Mock de `subprocess.run` basta |
| Comportamento do **comando** — flag, ordem, intervalo, o que a ferramenta responde àquela combinação | Ao menos um caso que **execute a ferramenta de verdade**, contra um diretório descartável em `tempfile` |

**Caracterizar antes de corrigir.** Teste escrito a partir da mesma leitura que produziu o defeito
passa contra o defeito. O comportamento real primeiro — num repositório descartável, reproduzindo o
ciclo real —, o teste depois.

O caso que originou a regra, com a medição e o custo:
[`L-28`](../../docs/plan/model/0001-decode-and-code-foundation/0001-decode-and-code-foundation.md),
seção *Lacunas*.

## Fonte

[`language-policy.md`](../../docs/plan/system/language-policy.md) — medição de ambientes e o porquê
do alvo 3.10 — e [`estudo-runtime-e-dependencias.md`](../../docs/plan/system/estudo-runtime-e-dependencias.md),
a evidência primária.
