#!/usr/bin/env python3
"""Testes do módulo base dos scripts da dev-units — unidade 0002-01.

O que precisa ficar provado é o critério de aceite: a origem dos caminhos não
depende de onde o script foi invocado. Daí o teste que troca de cwd antes de
perguntar pela raiz — inclusive para `/`, onde um fallback por cwd devolveria
outra coisa sem reclamar.
"""

from __future__ import annotations

import os
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import lib


class TestRepoRoot(unittest.TestCase):
    def test_acha_a_raiz_do_amflow(self):
        raiz = lib.repo_root()
        for marca in lib.ROOT_MARKERS:
            self.assertTrue((raiz / marca).is_dir(), marca)

    def test_independe_do_diretorio_de_trabalho(self):
        esperado = lib.repo_root()
        anterior = Path.cwd()
        try:
            for destino in (
                Path(tempfile.gettempdir()),
                esperado / "docs" / "plan",
                Path(os.sep),
            ):
                os.chdir(destino)
                self.assertEqual(lib.repo_root(), esperado, f"cwd={destino}")
        finally:
            os.chdir(anterior)

    def test_raiz_vem_resolvida(self):
        raiz = lib.repo_root()
        self.assertEqual(raiz, raiz.resolve())

    def test_sem_marcas_acima_levanta_runtime_error(self):
        # Diretório temporário não tem .claude/ + docs/ em nenhum nível acima.
        with tempfile.TemporaryDirectory() as tmp:
            with self.assertRaises(RuntimeError):
                lib._find_repo_root(Path(tmp).resolve())


class TestCaminhosDoPlano(unittest.TestCase):
    def test_plan_root_e_docs_plan(self):
        self.assertTrue(lib.plan_root().is_dir())
        self.assertEqual(
            lib.plan_root().relative_to(lib.repo_root()), Path("docs") / "plan"
        )

    def test_planos_md_existe_no_disco(self):
        # Segunda metade do critério de aceite.
        self.assertTrue(lib.planos_md().is_file())

    def test_inbox_fica_sob_plan_root(self):
        # O diretório pode não existir ainda; o caminho é derivado do mesmo lugar.
        self.assertEqual(lib.inbox().parent, lib.plan_root())
        self.assertEqual(lib.inbox().name, "_inbox")


class TestCoreDir(unittest.TestCase):
    def test_core_existente(self):
        # Deriva um core real do disco em vez de fixar um nome — "builder" é
        # população do AmFlow, ausente aqui (suposição medida na unidade 0001-02).
        candidatos = [
            item.name
            for item in lib.plan_root().iterdir()
            if item.is_dir() and item.name not in ("_inbox", "system")
        ]
        self.assertTrue(candidatos, "nenhum core encontrado sob plan_root()")
        core = candidatos[0]
        self.assertTrue(lib.core_dir(core).is_dir())
        self.assertEqual(lib.core_dir(core).parent, lib.plan_root())

    def test_nome_vazio_e_recusado(self):
        for nome in ("", "   "):
            with self.assertRaises(ValueError):
                lib.core_dir(nome)

    def test_separador_de_caminho_e_recusado(self):
        for nome in ("hub/auth", "hub\\auth", "/hub"):
            with self.assertRaises(ValueError):
                lib.core_dir(nome)


if __name__ == "__main__":
    unittest.main()
