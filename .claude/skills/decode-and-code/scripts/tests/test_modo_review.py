#!/usr/bin/env python3
"""Teste do modo `review` — unidade 0002-12.

Cobre exatamente o que a própria unidade declara como gate: o modo está descrito no corpo — não mais
placeholder — e os subcomandos do `dc.py` que ele compõe estão citados, com o comando inteiro, e o `dc.py` existe —
via `lint_skill.lint`, que já resolve existência e permissão de qualquer caminho
`${CLAUDE_SKILL_DIR}/../decode-and-code/scripts/*.py` citado. O comportamento do
julgamento (os checks conceituais, de arquitetura e de adequação de fontes) não é verificável por
script — limitação assumida em D-02 e na unidade 0002-10.
"""

from __future__ import annotations

import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import lib
import lint_skill
import regioes

SKILL = lib.repo_root() / ".claude" / "skills" / "review-plan" / "SKILL.md"

# O comando que a skill manda rodar — o atalho `dc.py` da pasta dela, que o `allowed-tools` casa (`P-14`).
COMANDO = 'python3 "${CLAUDE_SKILL_DIR}/dc.py"'

# As duas grafias que a liberação precisa cobrir: com aspas e sem — o modelo às vezes tira as aspas.
REGRAS_DO_ATALHO = (
    'Bash(python3 \\"${CLAUDE_SKILL_DIR}/dc.py\\" *)',
    'Bash(python3 ${CLAUDE_SKILL_DIR}/dc.py *)',
)

# Os subcomandos que o modo `review` compõe: `validar-nome` (era `nomenclatura.py`) e `concorrencia`
# (era a varredura de `_planos.md` por `regioes`/`numeracao.py`). `guardrail.py` foi aposentado pela
# unidade 0003-08: plugins/ não coexiste mais com hub/ neste repositório.
SUBCOMANDOS_COMPOSTOS = ("validar-nome", "concorrencia")


def _secao_review(corpo: str) -> str:
    """O miolo de `### \\`review <plano>\\`` até o próximo `## ` — nunca a skill inteira."""
    inicio = corpo.index("### `review <plano>`")
    resto = corpo[inicio:]
    fim = resto.index("\n## ", 1)
    return resto[:fim]


class TestModoReview(unittest.TestCase):
    def test_skill_aprova_com_o_modo_review(self):
        self.assertEqual(lint_skill.lint(SKILL, modos=["review"]), [])

    def test_libera_o_atalho_nas_duas_grafias(self):
        permissao = regioes.ler_campo(SKILL, "allowed-tools")
        for regra in REGRAS_DO_ATALHO:
            with self.subTest(regra=regra):
                self.assertIn(regra, permissao)

    def test_o_atalho_citado_existe_na_pasta_da_skill(self):
        self.assertTrue((SKILL.parent / "dc.py").is_file())

    def test_placeholder_removido(self):
        secao = _secao_review(SKILL.read_text(encoding="utf-8"))
        self.assertNotIn("A implementar", secao)

    def test_cita_os_subcomandos_que_o_modo_usa(self):
        secao = _secao_review(SKILL.read_text(encoding="utf-8"))
        for subcomando in SUBCOMANDOS_COMPOSTOS:
            with self.subTest(subcomando=subcomando):
                self.assertIn(f"{COMANDO} {subcomando} ", secao)


if __name__ == "__main__":
    unittest.main()
