#!/usr/bin/env python3
"""Teste da base das skills do método — unidades 0002-11 e `P-03`.

Cobre o que `lint_skill.lint()` já verifica — frontmatter completo e o modo declarado no corpo — e
o que ele não vê: a topologia de `D-01`. São três skills, uma por modo, cada uma com o modelo e a
invocação que o modo pede; e `decode-and-code/` ficou só com o que as três compartilham, sem
`SKILL.md`. Comportamento de cada modo não é testado aqui — vive em `test_modo_*`.
"""

from __future__ import annotations

import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import lib
import lint_skill
import regioes

SKILLS = lib.repo_root() / ".claude" / "skills"

# O `allowed-tools` das três (`P-14`, `D-05`): sem `Bash` solto, só o atalho `dc.py` da própria pasta da skill,
# nas duas grafias — com aspas e sem. A liberação casa o texto do comando, e o modelo às vezes tira as aspas.
# O valor é o texto do frontmatter como está — `ler_campo` não interpreta YAML, então a barra antes das
# aspas internas fica.
ALLOWED_TOOLS = (
    '"Read Write Edit Glob Grep Bash(python3 \\"${CLAUDE_SKILL_DIR}/dc.py\\" *) '
    'Bash(python3 ${CLAUDE_SKILL_DIR}/dc.py *)"'
)

# Skill → modo que o corpo precisa citar. `model`, `disable-model-invocation` e `context` são o que
# a topologia decide: `derive` cria estrutura e move arquivos, então só se invoca de forma explícita;
# `implement` roda em fork. `agent` é `general-purpose` porque o nome curto de um agent do plugin
# não resolve numa skill de plugin e cai, sem aviso, no padrão (medido com Claude Code 2.1.300).
TOPOLOGIA = {
    "review-plan": {
        "modo": "review",
        "model": "opus",
        "disable-model-invocation": "false",
        "context": '""',
        "allowed-tools": ALLOWED_TOOLS,
    },
    "derive": {
        "modo": "derive",
        "model": "opus",
        "disable-model-invocation": "true",
        "context": '""',
        "allowed-tools": ALLOWED_TOOLS,
    },
    "implement": {
        "modo": "implement",
        "model": "sonnet",
        "allowed-tools": ALLOWED_TOOLS,
        "disable-model-invocation": "false",
        "context": "fork",
        "agent": "general-purpose",
        "background": "false",
    },
}


class TestSkillBase(unittest.TestCase):
    def test_topologia_cobre_exatamente_as_skills_de_lib(self):
        """`TOPOLOGIA` é a especificação do D-01; `lib.SKILLS` é a lista de produção. Têm de coincidir."""
        self.assertEqual(set(TOPOLOGIA), set(lib.SKILLS))

    def test_cada_skill_aprova_com_o_proprio_modo(self):
        for nome, esperado in TOPOLOGIA.items():
            with self.subTest(skill=nome):
                self.assertEqual(lint_skill.lint(SKILLS / nome / "SKILL.md", modos=[esperado["modo"]]), [])

    def test_frontmatter_de_topologia(self):
        for nome, esperado in TOPOLOGIA.items():
            for campo, valor in esperado.items():
                if campo == "modo":
                    continue
                with self.subTest(skill=nome, campo=campo):
                    self.assertEqual(regioes.ler_campo(SKILLS / nome / "SKILL.md", campo), valor)

    def test_so_o_implement_declara_agent(self):
        for nome in ("review-plan", "derive"):
            with self.subTest(skill=nome):
                self.assertIsNone(regioes.ler_campo(SKILLS / nome / "SKILL.md", "agent"))

    def test_cada_skill_tem_o_atalho_dc_py(self):
        """`${CLAUDE_SKILL_DIR}/dc.py` precisa existir em cada pasta — é o que a regra de permissão casa.

        Que os três são idênticos e repassam argumentos e código de saída é de `test_dc.py`.
        """
        for nome in TOPOLOGIA:
            with self.subTest(skill=nome):
                self.assertTrue((SKILLS / nome / "dc.py").is_file())

    def test_pasta_compartilhada_nao_tem_skill_md(self):
        compartilhada = SKILLS / "decode-and-code"
        self.assertFalse((compartilhada / "SKILL.md").exists())
        self.assertTrue((compartilhada / "scripts").is_dir())
        self.assertTrue((compartilhada / "config.json").is_file())


if __name__ == "__main__":
    unittest.main()
