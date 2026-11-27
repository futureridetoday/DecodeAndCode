#!/usr/bin/env python3
"""O esqueleto do huddle depois do redesign — subparte 2.2.13 (K-09, item 6.03 do mapa).

O arquivo de cada pessoa não cita mais a norma nem leva a tag `pre-norma`; quem diz o que o huddle é
é o codex. `ESQUELETO_ANTERIOR` guarda o que mudou, na forma exata, para a migração dos projetos.
"""

from __future__ import annotations

import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import huddle


class TestEsqueleto(unittest.TestCase):
    def test_esqueleto_novo_nao_cita_a_norma(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            alvo = huddle.iniciar(Path(tmp) / "ana.md", Path(tmp), "ana")
            texto = alvo.read_text(encoding="utf-8")
            self.assertEqual(huddle.lint_arquivo(alvo), [])
        self.assertNotIn("modelo-dev-units", texto)
        self.assertNotIn("pre-norma", texto)
        self.assertIn("seção *Huddle*", texto)

    def test_pares_do_esqueleto_anterior(self) -> None:
        for antigo, atual in huddle.ESQUELETO_ANTERIOR:
            with self.subTest(antigo=antigo[:30]):
                self.assertNotIn(antigo, huddle._CONTEUDO_INICIAL)
                self.assertIn(atual, huddle._CONTEUDO_INICIAL)


if __name__ == "__main__":
    unittest.main()
