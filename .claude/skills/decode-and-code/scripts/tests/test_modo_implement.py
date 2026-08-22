#!/usr/bin/env python3
"""Teste do modo `implement` — unidade 0002-14.

Cobre exatamente o que a própria unidade declara como gate: o modo está descrito no corpo — não mais
placeholder — e os scripts que ele compõe existem, via `lint_skill.lint`, que já resolve existência e
permissão de qualquer caminho `.claude/skills/dev-units/scripts/*.py` citado. A prova real do
`implement` é empírica e vem depois — a primeira unidade executada em sessão nova com Sonnet, prevista
para logo após a Fase 1 (unidade 0002-14, seção Verificação).
"""

from __future__ import annotations

import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import lib
import lint_skill

SKILL = lib.repo_root() / ".claude" / "skills" / "dev-units" / "SKILL.md"

# Os três scripts que o modo `implement` compõe (unidade 0002-14, tabela Arquivos).
SCRIPTS_COMPOSTOS = ("lint_unidade.py", "verificacao.py", "backlog.py")


def _secao_implement(corpo: str) -> str:
    """O miolo de `### \\`implement <unidade>\\`` até o próximo `## ` — nunca a skill inteira."""
    inicio = corpo.index("### `implement <unidade>`")
    resto = corpo[inicio:]
    fim = resto.index("\n## ", 1)
    return resto[:fim]


class TestModoImplement(unittest.TestCase):
    def test_skill_aprova_com_o_modo_implement(self):
        self.assertEqual(lint_skill.lint(SKILL, modos=["implement"]), [])

    def test_placeholder_removido(self):
        secao = _secao_implement(SKILL.read_text(encoding="utf-8"))
        self.assertNotIn("A implementar", secao)

    def test_compoe_os_tres_scripts_que_o_modo_usa(self):
        secao = _secao_implement(SKILL.read_text(encoding="utf-8"))
        for script in SCRIPTS_COMPOSTOS:
            with self.subTest(script=script):
                self.assertIn(script, secao)


if __name__ == "__main__":
    unittest.main()
