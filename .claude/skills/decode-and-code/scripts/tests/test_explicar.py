#!/usr/bin/env python3
"""Testes de `dc.py explicar` e de `normas.secao_do_codex` — subparte 2.2.04 (K-12, K-13).

O `explicar` lê o codex do pacote pelo título da seção, nunca a norma copiada ao projeto; `conversa`
imprime o procedimento compartilhado, que mora fora do codex.
"""

from __future__ import annotations

import contextlib
import io
import sys
import tempfile
import unittest
from pathlib import Path
from unittest import mock

sys.path.insert(0, str(Path(__file__).resolve().parent))
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import dc
import normas


class TestSecaoDoCodex(unittest.TestCase):
    def test_toda_secao_que_o_dc_imprime_existe_no_codex(self):
        titulos = set(dc._SECOES_DO_METODO) | set(dc._SECOES_DO_FECHO)
        for nomes in dc._SECOES_AVULSAS.values():
            titulos |= set(nomes)
        for titulo in sorted(titulos):
            with self.subTest(titulo=titulo):
                capitulo, trecho = normas.secao_do_codex(titulo)
                self.assertEqual(capitulo.parent, normas.codex_dir())
                self.assertTrue(trecho.startswith(f"## {titulo}\n"))
                self.assertNotIn("\n## ", trecho)

    def test_titulo_exato_nao_casa_prefixo(self):
        with tempfile.TemporaryDirectory() as tmp:
            (Path(tmp) / "a.md").write_text("## Plano técnico\n\nx\n\n## Plano\n\ny\n", encoding="utf-8")
            _, trecho = normas.secao_do_codex("Plano", Path(tmp))
        self.assertEqual(trecho, "## Plano\n\ny")

    def test_titulo_ausente_levanta_nomeando_o_titulo(self):
        with self.assertRaises(ValueError) as ctx:
            normas.secao_do_codex("Não existe")
        self.assertIn("Não existe", str(ctx.exception))

    def test_procedimento_compartilhado_existe_fora_do_codex(self):
        for arquivo in dc._PROCEDIMENTOS.values():
            caminho = normas.procedimentos_dir() / arquivo
            self.assertTrue(caminho.is_file(), caminho)
            self.assertNotEqual(caminho.parent, normas.codex_dir())


class TestExplicar(unittest.TestCase):
    def setUp(self):
        # `dc.main` roda no processo, a partir do checkout; o log do plano 0018 não é o que se prova.
        patcher = mock.patch.object(dc, "_registrar")
        patcher.start()
        self.addCleanup(patcher.stop)

    def _rodar(self, *argv: str) -> str:
        saida = io.StringIO()
        with contextlib.redirect_stdout(saida):
            codigo = dc.main(list(argv))
        self.assertEqual(codigo, 0)
        return saida.getvalue()

    def _cabecalhos(self, texto: str) -> list[str]:
        return [l for l in texto.splitlines() if l.startswith("### ")]

    def test_sem_secao_imprime_as_do_metodo_na_ordem(self):
        cabecalhos = self._cabecalhos(self._rodar("explicar"))
        self.assertEqual([c.split(" § ")[1] for c in cabecalhos], list(dc._SECOES_DO_METODO))
        self.assertTrue(all(c.startswith("### codex/") for c in cabecalhos))

    def test_cada_secao_avulsa_imprime_as_suas(self):
        for nome, titulos in dc._SECOES_AVULSAS.items():
            with self.subTest(nome=nome):
                cabecalhos = self._cabecalhos(self._rodar("explicar", nome))
                self.assertEqual([c.split(" § ")[1] for c in cabecalhos], list(titulos))

    def test_conversa_imprime_o_procedimento_sem_frontmatter(self):
        texto = self._rodar("explicar", "conversa")
        self.assertTrue(texto.startswith("### procedures/suggestion-conversation.md\n"))
        self.assertIn("## JSON pelo stdin", texto)
        self.assertIn("## Formato do guardrail", texto)
        self.assertNotIn("checksum:", texto)

    def test_huddle_fecho_imprime_a_secao_huddle_do_codex(self):
        texto = self._rodar("huddle-fecho")
        self.assertIn("### codex/concepts.md § Huddle", texto)
        self.assertIn("mesmo\n    que nenhuma", texto)

    def test_nao_le_a_norma(self):
        texto = self._rodar("explicar") + self._rodar("explicar", "setup") + self._rodar("huddle-fecho")
        self.assertNotIn("modelo-dev-units", texto)

    def test_secao_desconhecida_e_erro_de_uso(self):
        with contextlib.redirect_stderr(io.StringIO()), self.assertRaises(SystemExit) as ctx:
            dc.main(["explicar", "nao-existe"])
        self.assertEqual(ctx.exception.code, 2)


if __name__ == "__main__":
    unittest.main()
