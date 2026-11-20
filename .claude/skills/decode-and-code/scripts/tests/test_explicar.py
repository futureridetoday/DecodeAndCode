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


class TestExplicarSecao(unittest.TestCase):
    """M4 do 0013: `explicar <seção>` imprime só aquela seção, e o modelo não abre a norma com `sed`."""

    def _rodar(self, *argv: str) -> str:
        import contextlib
        import io

        saida = io.StringIO()
        with contextlib.redirect_stdout(saida):
            codigo = dc.main(["explicar", *argv])
        self.assertEqual(codigo, 0)
        return saida.getvalue()

    def test_cada_secao_nomeada_imprime_um_bloco_com_o_titulo_dela(self):
        for nome, prefixo in dc._SECOES_AVULSAS.items():
            with self.subTest(nome=nome):
                texto = self._rodar(nome)
                cabecalhos = [l for l in texto.splitlines() if l.startswith("### ") and " § " in l]
                self.assertEqual(len(cabecalhos), 1, cabecalhos)
                self.assertTrue(texto.startswith(cabecalhos[0]))
                self.assertIn(f"§ {prefixo}", cabecalhos[0].replace("3. ", ""))

    def test_huddle_e_camada_normativa_existem(self):
        self.assertEqual(set(dc._SECOES_AVULSAS), {"huddle", "camada-normativa"})

    def test_sem_secao_continua_imprimindo_as_quatro_do_metodo(self):
        texto = self._rodar()
        cabecalhos = [l for l in texto.splitlines() if l.startswith("### ") and " § " in l]
        self.assertEqual(len(cabecalhos), len(dc._SECOES_DO_METODO))

    def test_secao_desconhecida_e_erro_de_uso(self):
        import contextlib
        import io

        with contextlib.redirect_stderr(io.StringIO()), self.assertRaises(SystemExit) as ctx:
            dc.main(["explicar", "nao-existe"])
        self.assertEqual(ctx.exception.code, 2)


if __name__ == "__main__":
    unittest.main()
