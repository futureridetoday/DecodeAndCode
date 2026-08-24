#!/usr/bin/env python3
"""Teste do modo `review` — unidade 0002-12.

Cobre exatamente o que a própria unidade declara como gate: o modo está descrito no corpo — não mais
placeholder — e os scripts que ele compõe existem, via `lint_skill.lint`, que já resolve existência e
permissão de qualquer caminho `.claude/skills/decode-and-code/scripts/*.py` citado. O comportamento do
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

SKILL = lib.repo_root() / ".claude" / "skills" / "decode-and-code" / "SKILL.md"

# Os dois scripts que o modo `review` compõe (unidade 0002-12, tabela Arquivos) —
# `guardrail.py` foi aposentado pela unidade 0003-08: plugins/ não coexiste mais
# com hub/ neste repositório, e o guardrail perdeu o par que verificava.
SCRIPTS_COMPOSTOS = ("nomenclatura.py", "numeracao.py")


def _secao_review(corpo: str) -> str:
    """O miolo de `### \\`review <plano>\\`` até o próximo `### ` — nunca a skill inteira."""
    inicio = corpo.index("### `review <plano>`")
    resto = corpo[inicio:]
    fim = resto.index("\n### ", 1)
    return resto[:fim]


class TestModoReview(unittest.TestCase):
    def test_skill_aprova_com_o_modo_review(self):
        self.assertEqual(lint_skill.lint(SKILL, modos=["review"]), [])

    def test_placeholder_removido(self):
        secao = _secao_review(SKILL.read_text(encoding="utf-8"))
        self.assertNotIn("A implementar", secao)

    def test_compoe_os_dois_scripts_da_fase_1(self):
        secao = _secao_review(SKILL.read_text(encoding="utf-8"))
        for script in SCRIPTS_COMPOSTOS:
            with self.subTest(script=script):
                self.assertIn(script, secao)


if __name__ == "__main__":
    unittest.main()
