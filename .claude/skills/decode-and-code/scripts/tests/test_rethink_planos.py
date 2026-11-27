#!/usr/bin/env python3
"""Testes do que o rethink ganhou na subparte 2.2.12 (K-11): os planos abertos que citam um item
retirado e o histórico das decisões sobre a foundation (codex, *Rethink*)."""

from __future__ import annotations

import sys
import tempfile
import unittest
from pathlib import Path
from unittest import mock

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import lib
import rethink

CABECALHO = "| # | Plano | Core | Módulo | Origem | Situação | Aprovado |\n|---|---|---|---|---|---|---|\n"


class TestPlanosQueCitam(unittest.TestCase):
    def setUp(self) -> None:
        tmp = tempfile.TemporaryDirectory()
        self.addCleanup(tmp.cleanup)
        self.raiz = Path(tmp.name).resolve()
        (self.raiz / "_inbox").mkdir()
        p = mock.patch.object(lib, "plan_root", return_value=self.raiz)
        p.start()
        self.addCleanup(p.stop)
        linhas = (
            "| 0001 | [aberto](0001-aberto/0001-aberto.md) | — | | — | em desenvolvimento | 2026-11-27 |\n"
            "| 0002 | [fechado](0002-fechado.md) | — | | — | concluído | 2026-11-20 |\n"
        )
        (self.raiz / "_planos.md").write_text(
            f"<!-- planos:start -->\n{CABECALHO}{linhas}<!-- planos:end -->\n", encoding="utf-8"
        )

    def escrever(self, relativo: str, texto: str) -> Path:
        caminho = self.raiz / relativo
        caminho.parent.mkdir(parents=True, exist_ok=True)
        caminho.write_text(texto, encoding="utf-8")
        return caminho

    def test_acha_rascunho_plano_aberto_e_unidade(self) -> None:
        rascunho = self.escrever("_inbox/add-x.md", "usa a guideline `scripts`\n")
        plano = self.escrever("0001-aberto/0001-aberto.md", "cita scripts aqui\n")
        unidade = self.escrever("0001-aberto/01-u.md", "| scripts | [scripts](x.md) |\n")
        self.escrever("0001-aberto/_handoff.md", "scripts\n")
        self.assertEqual(rethink.planos_que_citam("scripts"), [rascunho, plano, unidade])

    def test_plano_fechado_fica_como_registro(self) -> None:
        self.escrever("0002-fechado.md", "scripts\n")
        self.assertEqual(rethink.planos_que_citam("scripts"), [])

    def test_palavra_inteira(self) -> None:
        self.escrever("_inbox/add-x.md", "test-scripts e scriptsx\n")
        self.assertEqual(rethink.planos_que_citam("scripts"), [])


class TestHistoricoDaFoundation(unittest.TestCase):
    def test_vocabulario(self) -> None:
        self.assertIn("recurso", rethink.CAMADAS)
        self.assertIn("padrão de código", rethink.CAMADAS)
        self.assertIn("retirado", rethink.DECISOES)
        self.assertIn("retirado", rethink.DECISOES_COM_MOTIVO)


if __name__ == "__main__":
    unittest.main()
