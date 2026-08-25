#!/usr/bin/env python3
"""Testes de `rules.lint_guideline` — unidade 0001-09.

O par do critério de aceite: `.claude/rules/scripts.md` real aprova e **ativa** — casa arquivo
que existe no repositório, verificado contra o disco, não fixture —, e cada invariante reprova
isoladamente contra fixture sintética, no mesmo padrão de `test_rules.py`.
"""

from __future__ import annotations

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
from fixtures import RULE_COM_PATHS_VALIDA


class TestScriptsGuidelineReal(unittest.TestCase):
    """`.claude/rules/scripts.md` é o critério de aceite desta unidade."""

    @classmethod
    def setUpClass(cls):
        cls.caminho = lib.repo_root() / ".claude" / "rules" / "scripts.md"

    def test_arquivo_existe(self):
        self.assertTrue(self.caminho.is_file())

    def test_aprova_sem_ressalva(self):
        problemas = rules.lint_guideline(self.caminho)
        self.assertEqual(problemas, [], problemas)

    def test_declara_paths(self):
        self.assertIsNotNone(regioes.ler_campo(self.caminho, "paths"))


class TestArquivoInexistente(unittest.TestCase):
    def test_levanta_file_not_found_error(self):
        with tempfile.TemporaryDirectory() as tmp:
            alvo = Path(tmp) / "nao-existe.md"
            with self.assertRaises(FileNotFoundError):
                rules.lint_guideline(alvo)


class TestGateDeGuideline(unittest.TestCase):
    """Contra fixture sintética — cada teste reprova uma dimensão do escopo por vez.

    O diretório da fixture é sempre um `tempfile.TemporaryDirectory()`, mas o casamento
    contra o disco em `rules._checar_paths_guideline` roda contra `lib.repo_root()` — a raiz
    real do repositório —, não contra onde a fixture foi escrita. É a mesma mecânica que a
    unidade pede: casamento verificado no disco, nunca simulado.
    """

    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self._tmp.cleanup)
        self.dir = Path(self._tmp.name)

    def test_guideline_sintetica_com_paths_que_casam_disco_aprova(self):
        alvo = fixtures.rule(self.dir, paths=["**/*.py"])
        self.assertEqual(rules.lint_guideline(alvo), [])

    def test_sem_paths_reprova(self):
        alvo = fixtures.rule(self.dir, paths=None)
        problemas = rules.lint_guideline(alvo)
        self.assertTrue(any("paths" in p for p in problemas), problemas)

    def test_paths_vazio_reprova(self):
        alvo = fixtures.rule(self.dir, paths=[])
        problemas = rules.lint_guideline(alvo)
        self.assertTrue(any("paths" in p for p in problemas), problemas)

    def test_glob_que_nao_compila_reprova(self):
        texto = RULE_COM_PATHS_VALIDA.replace(
            'paths: ["hub/app/**", "hub/lib/**"]', 'paths: ["hub/app/**"'
        )
        alvo = self.dir / "regra.md"
        alvo.write_text(texto, encoding="utf-8")
        problemas = rules.lint_guideline(alvo)
        self.assertTrue(problemas, problemas)

    def test_glob_valido_que_nao_casa_nada_reprova(self):
        alvo = fixtures.rule(self.dir, paths=["__caminho_inexistente__/**/*.nunca"])
        problemas = rules.lint_guideline(alvo)
        self.assertTrue(any("não casa" in p for p in problemas), problemas)


if __name__ == "__main__":
    unittest.main()
