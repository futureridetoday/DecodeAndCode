#!/usr/bin/env python3
"""Testes do move-md.

O caso que originou o script: aprovar um plano move
docs/plan/_inbox/<nome>.md para docs/plan/<core>/<NNNN>-<nome>/, um nível mais
fundo — e todo `../x` de dentro precisa virar `../../x`. Feito à mão em
2026-07-24, a correção dos links de dentro foi lembrada e a dos links de fora
não. Os dois sentidos estão cobertos aqui.
"""

from __future__ import annotations

import shutil
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import importlib.util

_spec = importlib.util.spec_from_file_location(
    "move_md", Path(__file__).resolve().parent.parent / "move-md.py"
)
move_md = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(move_md)


class TestSepararAncora(unittest.TestCase):
    def test_sem_ancora(self):
        self.assertEqual(move_md.separar_ancora("a/b.md"), ("a/b.md", ""))

    def test_com_ancora(self):
        self.assertEqual(
            move_md.separar_ancora("a/b.md#secao"), ("a/b.md", "#secao")
        )


class TestERelativo(unittest.TestCase):
    def test_aceita_relativo(self):
        for destino in ("../x.md", "./x.md", "x.md", "sub/x.md"):
            self.assertTrue(move_md.e_relativo(destino), destino)

    def test_recusa_o_que_nao_depende_de_lugar(self):
        for destino in (
            "https://exemplo.com",
            "http://exemplo.com",
            "#secao",
            "/abs/x.md",
            "mailto:a@b.c",
            "",
        ):
            self.assertFalse(move_md.e_relativo(destino), destino)


class TestReescritaEmArvoreReal(unittest.TestCase):
    """Monta uma árvore temporária e move de verdade."""

    def setUp(self):
        self.tmp = Path(tempfile.mkdtemp())
        # Espelha a estrutura de docs/plan que motivou o script.
        (self.tmp / "_inbox").mkdir()
        (self.tmp / "system").mkdir()
        (self.tmp / "builder" / "0002-dev-units").mkdir(parents=True)

        (self.tmp / "system" / "norma.md").write_text("# norma\n", encoding="utf-8")
        (self.tmp / "_planos.md").write_text(
            "# planos\n\nver [plano](_inbox/plano.md)\n", encoding="utf-8"
        )
        (self.tmp / "_inbox" / "plano.md").write_text(
            "# plano\n\n"
            "ver [norma](../system/norma.md) e [tabela](../_planos.md)\n"
            "link externo [site](https://exemplo.com) e âncora [x](#aqui)\n"
            "com fragmento [n](../system/norma.md#secao)\n",
            encoding="utf-8",
        )
        self._repo_root_original = move_md.REPO_ROOT
        move_md.REPO_ROOT = self.tmp

    def tearDown(self):
        move_md.REPO_ROOT = self._repo_root_original
        shutil.rmtree(self.tmp, ignore_errors=True)

    def test_links_internos_ganham_um_nivel(self):
        origem = self.tmp / "_inbox" / "plano.md"
        destino_dir = self.tmp / "builder" / "0002-dev-units"

        conteudo = origem.read_text(encoding="utf-8")
        novo, mudancas = move_md.reescrever_links_internos(
            conteudo, origem.parent, destino_dir
        )

        self.assertIn("../../system/norma.md", novo)
        self.assertIn("../../_planos.md", novo)
        self.assertEqual(len(mudancas), 3)  # norma, tabela, norma#secao

    def test_ancora_sobrevive(self):
        origem = self.tmp / "_inbox" / "plano.md"
        novo, _ = move_md.reescrever_links_internos(
            origem.read_text(encoding="utf-8"),
            origem.parent,
            self.tmp / "builder" / "0002-dev-units",
        )
        self.assertIn("../../system/norma.md#secao", novo)

    def test_link_externo_e_ancora_intocados(self):
        origem = self.tmp / "_inbox" / "plano.md"
        novo, _ = move_md.reescrever_links_internos(
            origem.read_text(encoding="utf-8"),
            origem.parent,
            self.tmp / "builder" / "0002-dev-units",
        )
        self.assertIn("https://exemplo.com", novo)
        self.assertIn("(#aqui)", novo)

    def test_referencia_de_outro_arquivo_e_corrigida(self):
        # É a direção que foi esquecida na movimentação manual.
        origem = self.tmp / "_inbox" / "plano.md"
        destino = self.tmp / "builder" / "0002-dev-units" / "0002-plano.md"

        aplicadas = move_md.reescrever_referencias(origem, destino, dry_run=False)

        self.assertEqual(len(aplicadas), 1)
        conteudo = (self.tmp / "_planos.md").read_text(encoding="utf-8")
        self.assertIn("builder/0002-dev-units/0002-plano.md", conteudo)
        self.assertNotIn("_inbox/plano.md", conteudo)

    def test_dry_run_nao_escreve(self):
        origem = self.tmp / "_inbox" / "plano.md"
        destino = self.tmp / "builder" / "0002-dev-units" / "0002-plano.md"
        antes = (self.tmp / "_planos.md").read_text(encoding="utf-8")

        move_md.reescrever_referencias(origem, destino, dry_run=True)

        self.assertEqual((self.tmp / "_planos.md").read_text(encoding="utf-8"), antes)

    def test_exemplo_em_bloco_de_codigo_nao_e_reescrito(self):
        # A norma dev-units ilustra o formato do backlog com caminhos dentro de
        # bloco de código. Reescrevê-los faria o exemplo mostrar outra coisa.
        doc = self.tmp / "_inbox" / "com-exemplo.md"
        doc.write_text(
            "real: [norma](../system/norma.md)\n"
            "\n"
            "```markdown\n"
            "exemplo: [norma](../system/norma.md)\n"
            "```\n",
            encoding="utf-8",
        )

        novo, mudancas = move_md.reescrever_links_internos(
            doc.read_text(encoding="utf-8"),
            doc.parent,
            self.tmp / "builder" / "0002-dev-units",
        )

        linhas = novo.split("\n")
        self.assertEqual(linhas[0], "real: [norma](../../system/norma.md)")
        self.assertEqual(linhas[3], "exemplo: [norma](../system/norma.md)")
        self.assertEqual(len(mudancas), 1)

    def test_exemplo_em_crase_inline_nao_e_reescrito(self):
        doc = self.tmp / "_inbox" / "com-inline.md"
        doc.write_text(
            "real [n](../system/norma.md) e citado `[n](../system/norma.md)`\n",
            encoding="utf-8",
        )

        novo, mudancas = move_md.reescrever_links_internos(
            doc.read_text(encoding="utf-8"),
            doc.parent,
            self.tmp / "builder" / "0002-dev-units",
        )

        self.assertIn("real [n](../../system/norma.md)", novo)
        self.assertIn("`[n](../system/norma.md)`", novo)
        self.assertEqual(len(mudancas), 1)

    def test_link_ja_quebrado_e_preservado(self):
        # Não inventar destino: o problema tem de continuar visível.
        quebrado = self.tmp / "_inbox" / "outro.md"
        quebrado.write_text("[nada](../nao-existe.md)\n", encoding="utf-8")

        novo, mudancas = move_md.reescrever_links_internos(
            quebrado.read_text(encoding="utf-8"),
            quebrado.parent,
            self.tmp / "builder",
        )

        self.assertIn("../nao-existe.md", novo)
        self.assertEqual(mudancas, [])


if __name__ == "__main__":
    unittest.main()
