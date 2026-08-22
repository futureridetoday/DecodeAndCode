#!/usr/bin/env python3
"""Teste da base da skill dev-units — unidade 0002-11.

Cobre só o que `lint_skill.lint()` já verifica: frontmatter completo e os
três modos declarados no corpo. Comportamento de cada modo não é testado
aqui — chega com as unidades 12-14.
"""

from __future__ import annotations

import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import lib
import lint_skill

MODOS = ["review", "derive", "implement"]


class TestSkillBase(unittest.TestCase):
    def test_skill_aprova_com_os_tres_modos(self):
        skill = lib.repo_root() / ".claude" / "skills" / "dev-units" / "SKILL.md"
        self.assertEqual(lint_skill.lint(skill, modos=MODOS), [])


if __name__ == "__main__":
    unittest.main()
