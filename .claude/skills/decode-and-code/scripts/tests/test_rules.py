#!/usr/bin/env python3
"""Testes de `rules.lint_rule` — unidade 0001-03.

O par do critério de aceite dá o essencial: `.claude/rules/principles.md` real aprova sem
`paths:`, com exatamente os três princípios da `D-03` e o fluxo de três estágios e dois gates; e
cada invariante reprova isoladamente contra fixture sintética, no mesmo padrão de
`test_lint_unidade.py` e `test_lint_skill.py`.
"""

from __future__ import annotations

import re
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import fixtures
import lib
import regioes
import rules
from fixtures import RULE_VALIDA


class TestRulesReais(unittest.TestCase):
    """Toda rule real do repositório aprova sem ressalva — mesmo piso de TestSkillsReais."""

    def test_todas_as_rules_do_repositorio_aprovam(self):
        arquivos = sorted((lib.repo_root() / ".claude" / "rules").glob("*.md"))
        self.assertGreaterEqual(len(arquivos), 1, arquivos)
        for arquivo in arquivos:
            with self.subTest(rule=arquivo.name):
                self.assertEqual(rules.lint_rule(arquivo), [])


class TestPrinciplesReal(unittest.TestCase):
    """`.claude/rules/principles.md` é o critério de aceite desta unidade."""

    @classmethod
    def setUpClass(cls):
        cls.caminho = lib.repo_root() / ".claude" / "rules" / "principles.md"

    def test_nao_declara_paths(self):
        self.assertIsNone(regioes.ler_campo(self.caminho, "paths"))

    def test_tres_principios_presentes_e_nenhum_a_mais(self):
        corpo = self.caminho.read_text(encoding="utf-8")
        for principio in (
            "Código é custo",
            "Subtração antes de adição",
            "Evidência acima de opinião",
        ):
            with self.subTest(principio=principio):
                self.assertIn(principio, corpo)
        # O quarto princípio da fonte, cortado pela D-03 por redundância — não pode voltar.
        self.assertNotIn("Menor solução", corpo)
        self.assertNotIn("solução mínima", corpo)

    def test_fluxo_tem_tres_estagios_e_dois_gates(self):
        corpo = self.caminho.read_text(encoding="utf-8")
        for estagio in ("Clarificar", "Evitar", "Reduzir"):
            with self.subTest(estagio=estagio):
                self.assertIn(estagio, corpo)
        self.assertIn("A — necessidade real", corpo)
        self.assertIn("B — mínimo viável", corpo)
        # Os Gates 1-5 são de outro domínio, e o plano os recusou — não podem entrar.
        for numerico in ("Gate 1", "Gate 2", "Gate 3", "Gate 4", "Gate 5"):
            with self.subTest(gate_numerico=numerico):
                self.assertNotIn(numerico, corpo)


class TestArquivoInexistente(unittest.TestCase):
    def test_levanta_file_not_found_error(self):
        with tempfile.TemporaryDirectory() as tmp:
            alvo = Path(tmp) / "nao-existe.md"
            with self.assertRaises(FileNotFoundError):
                rules.lint_rule(alvo)


class TestGateEstrutural(unittest.TestCase):
    """Contra a fixture sintética mínima que aprova — cada teste quebra uma dimensão por vez."""

    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self._tmp.cleanup)
        self.dir = Path(self._tmp.name)

    def _escreve(self, texto: str, nome: str = "regra.md") -> Path:
        alvo = self.dir / nome
        alvo.write_text(texto, encoding="utf-8")
        return alvo

    def test_rule_valida_aprova(self):
        alvo = self._escreve(RULE_VALIDA)
        self.assertEqual(rules.lint_rule(alvo), [])

    def test_rule_com_paths_validos_aprova(self):
        alvo = fixtures.rule(self.dir, paths=["hub/app/**", "hub/lib/*.ts"])
        self.assertEqual(rules.lint_rule(alvo), [])

    def test_frontmatter_ausente_por_completo(self):
        alvo = self._escreve("# Sem frontmatter\n\nConteúdo qualquer.\n")
        problemas = rules.lint_rule(alvo)
        self.assertTrue(any("frontmatter" in p for p in problemas), problemas)

    def test_cada_campo_obrigatorio_ausente_e_reportado(self):
        for campo in rules.CAMPOS_FRONTMATTER:
            with self.subTest(campo=campo):
                padrao = re.compile(rf"(?m)^{re.escape(campo)}:.*\n")
                texto, n = padrao.subn("", RULE_VALIDA, count=1)
                self.assertEqual(n, 1, f"linha do campo {campo!r} não encontrada na fixture")
                alvo = self._escreve(texto, nome=f"sem-{campo}.md")
                problemas = rules.lint_rule(alvo)
                self.assertTrue(any(campo in p for p in problemas), (campo, problemas))

    def test_paths_com_glob_invalido_reprova(self):
        texto = fixtures.RULE_COM_PATHS_VALIDA.replace(
            'paths: ["hub/app/**", "hub/lib/**"]', 'paths: ["hub/app/**"'
        )
        alvo = self._escreve(texto)
        problemas = rules.lint_rule(alvo)
        self.assertTrue(any("paths" in p for p in problemas), problemas)

    def test_corpo_vazio_reprova(self):
        texto = RULE_VALIDA.replace("Corpo de teste para o lint de rule.\n", "")
        alvo = self._escreve(texto)
        problemas = rules.lint_rule(alvo)
        self.assertTrue(any("vazio" in p for p in problemas), problemas)


if __name__ == "__main__":
    unittest.main()
