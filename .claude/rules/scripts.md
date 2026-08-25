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

## Fonte

[`language-policy.md`](../../docs/plan/system/language-policy.md) — medição de ambientes e o porquê
do alvo 3.10 — e [`estudo-runtime-e-dependencias.md`](../../docs/plan/system/estudo-runtime-e-dependencias.md),
a evidência primária.
