#!/usr/bin/env python3
"""Testes do lint de agente — unidade 0001-19.

O par do critério de aceite dá o essencial: os quatro invariantes reprovam isoladamente, um por
vez, contra um agente sintético mínimo que sozinho já aprova; e o `planner.md` real aprova sem
ressalva — com `model`, `skills` (existência em disco incluída) e a declaração de escopo no corpo
conferidos em nome de caso próprio.
"""

from __future__ import annotations

import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import lib
import lint_agente

AGENTE_VALIDO = """\
---
name: agente-sintetico
description: Agente de teste para o lint.
tools: Read, Grep
model: sonnet
skills: [decode-and-code]
color: blue
---

Corpo de teste para o lint de agente.
"""


class TestPlannerReal(unittest.TestCase):
    """O caso contra o artefato real — sem ele, o lint prova só o mecanismo (L-31)."""

    def setUp(self):
        self.alvo = lib.repo_root() / ".claude" / "agents" / "planner.md"
        self.texto = self.alvo.read_text(encoding="utf-8")

    def test_planner_aprova_no_lint(self):
        self.assertEqual(lint_agente.lint(self.alvo), [])

    def test_planner_declara_model_opus(self):
        self.assertRegex(self.texto, r"(?m)^model:\s*opus\s*$")

    def test_planner_declara_skill_existente_em_disco(self):
        self.assertRegex(self.texto, r"(?m)^skills:.*decode-and-code")
        self.assertTrue((lib.repo_root() / ".claude" / "skills" / "decode-and-code").is_dir())

    def test_escopo_no_corpo_e_declaracao_nao_imposicao_por_tools(self):
        """`tools:` não tem granularidade de caminho (L-34) — o corpo declara, nunca impõe."""
        self.assertIn("docs/plan/**", self.texto)


class TestDeveloperReal(unittest.TestCase):
    """O caso contra o artefato real — sem ele, o lint prova só o mecanismo (L-31)."""

    def setUp(self):
        self.alvo = lib.repo_root() / ".claude" / "agents" / "developer.md"
        self.texto = self.alvo.read_text(encoding="utf-8")

    def test_developer_aprova_no_lint(self):
        self.assertEqual(lint_agente.lint(self.alvo), [])

    def test_developer_declara_model_sonnet(self):
        self.assertRegex(self.texto, r"(?m)^model:\s*sonnet\s*$")

    def test_developer_declara_skill_existente_em_disco(self):
        self.assertRegex(self.texto, r"(?m)^skills:.*decode-and-code")
        self.assertTrue((lib.repo_root() / ".claude" / "skills" / "decode-and-code").is_dir())

    def test_developer_nao_declara_memory(self):
        """A ausência é o invariante (D-06) — sozinha não prova a recusa (ver TestGateEstrutural)."""
        self.assertNotRegex(self.texto, r"(?m)^memory:")

    def test_developer_declara_contrato_nao_commita(self):
        self.assertIn("não commita", self.texto)

    def test_developer_declara_contrato_unidade_insuficiente_volta_a_quem_deriva(self):
        self.assertIn("volta para quem deriva", self.texto)


class TestArquivoInexistente(unittest.TestCase):
    def test_levanta_file_not_found_error(self):
        with tempfile.TemporaryDirectory() as tmp:
            alvo = Path(tmp) / "agente.md"
            with self.assertRaises(FileNotFoundError):
                lint_agente.lint(alvo)


class TestGateEstrutural(unittest.TestCase):
    """Contra um agente sintético mínimo que aprova — cada teste quebra um invariante por vez."""

    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self._tmp.cleanup)
        self.dir = Path(self._tmp.name)

    def _escreve(self, texto: str) -> Path:
        alvo = self.dir / "agente.md"
        alvo.write_text(texto, encoding="utf-8")
        return alvo

    def test_agente_valido_aprova(self):
        alvo = self._escreve(AGENTE_VALIDO)
        self.assertEqual(lint_agente.lint(alvo), [])

    def test_campo_nao_nativo_declarado_reprova(self):
        texto = AGENTE_VALIDO.replace(
            "color: blue\n", "color: blue\ndependencies: [outra-skill]\n"
        )
        alvo = self._escreve(texto)
        problemas = lint_agente.lint(alvo)
        self.assertTrue(
            any("dependencies" in p and "não-nativo" in p for p in problemas), problemas
        )

    def test_model_ausente_reprova(self):
        texto = AGENTE_VALIDO.replace("model: sonnet\n", "")
        alvo = self._escreve(texto)
        problemas = lint_agente.lint(alvo)
        self.assertTrue(any("model" in p and "ausente" in p for p in problemas), problemas)

    def test_model_fora_do_vocabulario_reprova(self):
        texto = AGENTE_VALIDO.replace("model: sonnet", "model: gpt4")
        alvo = self._escreve(texto)
        problemas = lint_agente.lint(alvo)
        self.assertTrue(any("vocabulário" in p for p in problemas), problemas)

    def test_skill_inexistente_em_disco_reprova(self):
        texto = AGENTE_VALIDO.replace(
            "skills: [decode-and-code]", "skills: [skill-que-nao-existe]"
        )
        alvo = self._escreve(texto)
        problemas = lint_agente.lint(alvo)
        self.assertTrue(any("skill-que-nao-existe" in p for p in problemas), problemas)

    def test_tools_ausente_reprova(self):
        texto = AGENTE_VALIDO.replace("tools: Read, Grep\n", "")
        alvo = self._escreve(texto)
        problemas = lint_agente.lint(alvo)
        self.assertTrue(any("tools" in p and "ausente" in p for p in problemas), problemas)

    def test_memory_declarado_reprova(self):
        """O caso contrário do `TestDeveloperReal`: sem este, a recusa podia nunca ter sido
        implementada e a ausência em `developer.md` passaria do mesmo jeito (D-06)."""
        texto = AGENTE_VALIDO.replace("color: blue\n", "color: blue\nmemory: sessao-anterior\n")
        alvo = self._escreve(texto)
        problemas = lint_agente.lint(alvo)
        self.assertTrue(any("memory" in p and "D-06" in p for p in problemas), problemas)


if __name__ == "__main__":
    unittest.main()
