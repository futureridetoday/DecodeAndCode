#!/usr/bin/env python3
"""Testes de `normas.secoes` — unidade `0009-04`, `dc.py explicar`.

A norma real devolve as quatro seções que sustentam o método; uma norma sintética sem uma delas
levanta `ValueError` que a nomeia.
"""

from __future__ import annotations

import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import dc
import lib
import normas


def _titulos() -> tuple[str, ...]:
    return dc._SECOES_DO_METODO


class TestSecoes(unittest.TestCase):
    def test_norma_real_devolve_as_quatro_na_ordem(self):
        norma = lib.plan_root() / "system" / "modelo-dev-units.md"
        achadas = normas.secoes(norma, _titulos())
        self.assertEqual(len(achadas), 4)
        for (titulo, trecho), nome in zip(achadas, _titulos()):
            self.assertTrue(titulo.startswith(nome), titulo)
            self.assertTrue(trecho.strip())

    def test_seção_ausente_levanta_nomeando_a_que_faltou(self):
        for faltando in _titulos():
            with self.subTest(faltando=faltando), tempfile.TemporaryDirectory() as tmp:
                arquivo = Path(tmp) / "norma.md"
                arquivo.write_text(
                    "# Norma\n\n" + "".join(f"## {n}\n\ntexto\n\n" for n in _titulos() if n != faltando),
                    encoding="utf-8",
                )
                with self.assertRaises(ValueError) as ctx:
                    normas.secoes(arquivo, _titulos())
                self.assertIn(faltando, str(ctx.exception))


if __name__ == "__main__":
    unittest.main()
