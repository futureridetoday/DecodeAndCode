#!/usr/bin/env python3
"""Teste do modo `derive` — unidade 0002-13.

Cobre exatamente o que a própria unidade declara como gate: o modo está descrito no corpo — não mais
placeholder — e os scripts que ele compõe existem, via `lint_skill.lint`, que já resolve existência e
permissão de qualquer caminho `.claude/skills/decode-and-code/scripts/*.py` citado. A prova real do `derive`
é empírica e vem depois — se o executor do `implement` precisou perguntar algo, a unidade falhou, e a
correção é da unidade, não do executor (unidade 0002-13, seção Verificação).
"""

from __future__ import annotations

import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import lib
import lint_skill

SKILL = lib.repo_root() / ".claude" / "skills" / "decode-and-code" / "SKILL.md"

# Os quatro scripts da Fase 1 que o modo `derive` compõe (unidade 0002-13, tabela Arquivos).
SCRIPTS_COMPOSTOS = ("scaffold.py", "numeracao.py", "lint_unidade.py", "backlog.py")


def _secao_derive(corpo: str) -> str:
    """O miolo de `### \\`derive <plano>\\`` até o próximo `### ` — nunca a skill inteira."""
    inicio = corpo.index("### `derive <plano>`")
    resto = corpo[inicio:]
    fim = resto.index("\n### ", 1)
    return resto[:fim]


class TestModoDerive(unittest.TestCase):
    def test_skill_aprova_com_o_modo_derive(self):
        self.assertEqual(lint_skill.lint(SKILL, modos=["derive"]), [])

    def test_placeholder_removido(self):
        secao = _secao_derive(SKILL.read_text(encoding="utf-8"))
        self.assertNotIn("A implementar", secao)

    def test_compoe_os_quatro_scripts_da_fase_1(self):
        secao = _secao_derive(SKILL.read_text(encoding="utf-8"))
        for script in SCRIPTS_COMPOSTOS:
            with self.subTest(script=script):
                self.assertIn(script, secao)


if __name__ == "__main__":
    unittest.main()
