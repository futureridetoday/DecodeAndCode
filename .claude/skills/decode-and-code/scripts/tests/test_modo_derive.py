#!/usr/bin/env python3
"""Teste do modo `derive` — unidade 0002-13.

Cobre exatamente o que a própria unidade declara como gate: o modo está descrito no corpo — não mais
placeholder — e os subcomandos do `dc.py` que ele compõe estão citados, com o comando inteiro, e o `dc.py` existe —
via `lint_skill.lint`, que já resolve existência e permissão de qualquer caminho
`${CLAUDE_SKILL_DIR}/../decode-and-code/scripts/*.py` citado. A prova real do `derive`
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
import regioes

SKILL = lib.repo_root() / ".claude" / "skills" / "derive" / "SKILL.md"

# O comando que a skill manda rodar — o atalho `dc.py` da pasta dela, que o `allowed-tools` casa (`P-14`).
COMANDO = 'python3 "${CLAUDE_SKILL_DIR}/dc.py"'

# As duas grafias que a liberação precisa cobrir: com aspas e sem — o modelo às vezes tira as aspas.
REGRAS_DO_ATALHO = (
    'Bash(python3 \\"${CLAUDE_SKILL_DIR}/dc.py\\" *)',
    'Bash(python3 ${CLAUDE_SKILL_DIR}/dc.py *)',
)

# Os subcomandos que o modo `derive` compõe: `aprovar` (era `scaffold.py`), `proxima-unidade`
# (`numeracao.py`), `lint-unidade` (`lint_unidade.py`), `projetar-backlog` (`backlog.py`) e `handoff`
# (`handoff.py`, que a skill já citava e o teste não cobria).
SUBCOMANDOS_COMPOSTOS = ("aprovar", "proxima-unidade", "lint-unidade", "projetar-backlog", "handoff")


def _secao_derive(corpo: str) -> str:
    """O miolo de `### \\`derive <plano>\\`` até o próximo `## ` — nunca a skill inteira."""
    inicio = corpo.index("### `derive <plano>`")
    resto = corpo[inicio:]
    fim = resto.index("\n## ", 1)
    return resto[:fim]


class TestModoDerive(unittest.TestCase):
    def test_skill_aprova_com_o_modo_derive(self):
        self.assertEqual(lint_skill.lint(SKILL, modos=["derive"]), [])

    def test_libera_o_atalho_nas_duas_grafias(self):
        permissao = regioes.ler_campo(SKILL, "allowed-tools")
        for regra in REGRAS_DO_ATALHO:
            with self.subTest(regra=regra):
                self.assertIn(regra, permissao)

    def test_o_atalho_citado_existe_na_pasta_da_skill(self):
        self.assertTrue((SKILL.parent / "dc.py").is_file())

    def test_placeholder_removido(self):
        secao = _secao_derive(SKILL.read_text(encoding="utf-8"))
        self.assertNotIn("A implementar", secao)

    def test_cita_os_subcomandos_que_o_modo_usa(self):
        secao = _secao_derive(SKILL.read_text(encoding="utf-8"))
        for subcomando in SUBCOMANDOS_COMPOSTOS:
            with self.subTest(subcomando=subcomando):
                self.assertIn(f"{COMANDO} {subcomando} ", secao)

    def test_handoff_le_as_tres_secoes_do_stdin(self):
        secao = _secao_derive(SKILL.read_text(encoding="utf-8"))
        for titulo in ("## Fila", "## Pendências", "## Sugestão"):
            with self.subTest(titulo=titulo):
                self.assertIn(titulo, secao)


if __name__ == "__main__":
    unittest.main()
