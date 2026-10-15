#!/usr/bin/env python3
"""Teste do modo `implement` — unidade 0002-14.

Cobre exatamente o que a própria unidade declara como gate: o modo está descrito no corpo — não mais
placeholder — e os subcomandos do `dc.py` que ele compõe estão citados, com o comando inteiro, e o `dc.py` existe —
via `lint_skill.lint`, que já resolve existência e permissão de qualquer caminho
`${CLAUDE_SKILL_DIR}/../decode-and-code/scripts/*.py` citado. A prova real do
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
import regioes

SKILL = lib.repo_root() / ".claude" / "skills" / "implement" / "SKILL.md"

# O comando que a skill manda rodar — o atalho `dc.py` da pasta dela, que o `allowed-tools` casa (`P-14`).
COMANDO = 'python3 "${CLAUDE_SKILL_DIR}/dc.py"'

# As duas grafias que a liberação precisa cobrir: com aspas e sem — o modelo às vezes tira as aspas.
REGRAS_DO_ATALHO = (
    'Bash(python3 \\"${CLAUDE_SKILL_DIR}/dc.py\\" *)',
    'Bash(python3 ${CLAUDE_SKILL_DIR}/dc.py *)',
)

# Os subcomandos que o modo `implement` compõe: `lint-unidade` (era `lint_unidade.py`), `verificar`
# (`verificacao.py`) e `projetar-backlog` (`backlog.py`).
SUBCOMANDOS_COMPOSTOS = ("lint-unidade", "verificar", "projetar-backlog")


def _secao_implement(corpo: str) -> str:
    """O miolo de `### \\`implement <unidade>\\`` até o próximo `## ` — nunca a skill inteira."""
    inicio = corpo.index("### `implement <unidade>`")
    resto = corpo[inicio:]
    fim = resto.index("\n## ", 1)
    return resto[:fim]


class TestModoImplement(unittest.TestCase):
    def test_skill_aprova_com_o_modo_implement(self):
        self.assertEqual(lint_skill.lint(SKILL, modos=["implement"]), [])

    def test_libera_o_atalho_nas_duas_grafias(self):
        permissao = regioes.ler_campo(SKILL, "allowed-tools")
        for regra in REGRAS_DO_ATALHO:
            with self.subTest(regra=regra):
                self.assertIn(regra, permissao)

    def test_o_atalho_citado_existe_na_pasta_da_skill(self):
        self.assertTrue((SKILL.parent / "dc.py").is_file())

    def test_placeholder_removido(self):
        secao = _secao_implement(SKILL.read_text(encoding="utf-8"))
        self.assertNotIn("A implementar", secao)

    def test_cita_os_subcomandos_que_o_modo_usa(self):
        secao = _secao_implement(SKILL.read_text(encoding="utf-8"))
        for subcomando in SUBCOMANDOS_COMPOSTOS:
            with self.subTest(subcomando=subcomando):
                self.assertIn(f"{COMANDO} {subcomando} ", secao)

    def test_manda_rodar_o_teste_durante_o_trabalho_sem_gravar_estado(self):
        secao = _secao_implement(SKILL.read_text(encoding="utf-8"))
        self.assertIn(f"{COMANDO} verificar <unidade> --dry-run", secao)


class TestCorpoComoPromptDeSubagent(unittest.TestCase):
    """A skill roda em `context: fork`: o corpo é o prompt de um subagent sem histórico algum.

    O que o agent de implementação dizia por conta própria passou para cá — são os contratos que sobram
    quando a skill é a única coisa que o executor lê.
    """

    def setUp(self):
        self.corpo = SKILL.read_text(encoding="utf-8")

    def test_abre_com_a_ordem_para_o_subagent(self):
        depois_do_titulo = self.corpo.split("\n# implement\n", 1)[1].strip()
        self.assertTrue(
            depois_do_titulo.startswith("Implemente a unidade `$target` do método decode-and-code, em cold-start."),
            depois_do_titulo[:120],
        )

    def test_declara_contrato_nao_commita(self):
        self.assertIn("não commita", self.corpo)

    def test_declara_contrato_unidade_insuficiente_volta_a_quem_deriva(self):
        self.assertIn("volta para quem deriva", self.corpo)

    def test_declara_que_nunca_deriva_nem_revisa_planos(self):
        self.assertIn("nunca deriva nem revisa planos", self.corpo)

    def test_fecha_com_uma_unica_mensagem_de_saida(self):
        self.assertIn("## Saída", self.corpo)
        self.assertIn("Uma única mensagem", self.corpo)


if __name__ == "__main__":
    unittest.main()
