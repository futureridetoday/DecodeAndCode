#!/usr/bin/env python3
"""Testes de config() — unidade 0001-01.

O que dá valor à unidade é o par do critério de aceite: config.json ausente resolve para os mesmos
caminhos de hoje (os defaults embutidos), e um config.json declarando um `plan_root` diferente muda
tanto o que `lib.plan_root()` devolve quanto onde `scaffold.aprovar()` grava. As demais dimensões
(malformado, campo desconhecido, cache, `root_markers`, mapa `runners`) são cobertas isoladamente
contra defaults sintéticos, sem tocar o `config.json` real da skill.
"""

from __future__ import annotations

import json
import sys
import tempfile
import unittest
from pathlib import Path
from unittest import mock

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import lib
import scaffold
import verificacao


def _resetar_cache():
    lib._config_cache = None


class TestConfigAusente(unittest.TestCase):
    def setUp(self):
        _resetar_cache()
        self.addCleanup(_resetar_cache)

    def test_resolve_para_os_defaults_embutidos(self):
        with tempfile.TemporaryDirectory() as tmp:
            caminho_inexistente = Path(tmp) / "config.json"
            with mock.patch.object(lib, "_config_path", return_value=caminho_inexistente):
                resolvido = lib.config()

        self.assertEqual(resolvido, lib._DEFAULTS)


class TestConfigDoDisco(unittest.TestCase):
    def setUp(self):
        _resetar_cache()
        self.addCleanup(_resetar_cache)

    def test_sobrepoe_apenas_as_chaves_declaradas(self):
        with tempfile.TemporaryDirectory() as tmp:
            caminho = Path(tmp) / "config.json"
            caminho.write_text(json.dumps({"plan_root": "outro/lugar"}), encoding="utf-8")
            with mock.patch.object(lib, "_config_path", return_value=caminho):
                resolvido = lib.config()

        self.assertEqual(resolvido["plan_root"], "outro/lugar")
        self.assertEqual(resolvido["move_script"], lib._DEFAULTS["move_script"])
        self.assertEqual(resolvido["root_markers"], lib._DEFAULTS["root_markers"])
        self.assertEqual(resolvido["runners"], lib._DEFAULTS["runners"])

    def test_json_invalido_levanta_value_error_nomeando_o_arquivo(self):
        with tempfile.TemporaryDirectory() as tmp:
            caminho = Path(tmp) / "config.json"
            caminho.write_text("{ isso não é json", encoding="utf-8")
            with mock.patch.object(lib, "_config_path", return_value=caminho):
                with self.assertRaises(ValueError) as ctx:
                    lib.config()

        self.assertIn(str(caminho), str(ctx.exception))

    def test_campo_desconhecido_levanta_value_error_nomeando_o_campo(self):
        with tempfile.TemporaryDirectory() as tmp:
            caminho = Path(tmp) / "config.json"
            caminho.write_text(json.dumps({"campo_que_nao_existe": 1}), encoding="utf-8")
            with mock.patch.object(lib, "_config_path", return_value=caminho):
                with self.assertRaises(ValueError) as ctx:
                    lib.config()

        self.assertIn(str(caminho), str(ctx.exception))
        self.assertIn("campo_que_nao_existe", str(ctx.exception))

    def test_cache_evita_reler_o_arquivo(self):
        with tempfile.TemporaryDirectory() as tmp:
            caminho = Path(tmp) / "config.json"
            caminho.write_text(json.dumps({"plan_root": "primeiro"}), encoding="utf-8")
            with mock.patch.object(lib, "_config_path", return_value=caminho):
                primeiro = lib.config()
                caminho.write_text(json.dumps({"plan_root": "segundo"}), encoding="utf-8")
                segundo = lib.config()

        self.assertEqual(primeiro["plan_root"], "primeiro")
        self.assertEqual(segundo["plan_root"], "primeiro")


class TestPlanRootAcompanhaConfig(unittest.TestCase):
    """Primeira metade do critério de aceite: `plan_root` diferente muda o que `lib.plan_root()` devolve."""

    def setUp(self):
        _resetar_cache()
        self.addCleanup(_resetar_cache)

    def test_plan_root_segue_o_valor_declarado(self):
        with tempfile.TemporaryDirectory() as tmp:
            raiz = Path(tmp).resolve()
            alvo = raiz / "outro" / "lugar"
            alvo.mkdir(parents=True)

            caminho_config = raiz / "config.json"
            caminho_config.write_text(json.dumps({"plan_root": "outro/lugar"}), encoding="utf-8")

            with mock.patch.object(lib, "_config_path", return_value=caminho_config), mock.patch.object(
                lib, "repo_root", return_value=raiz
            ):
                self.assertEqual(lib.plan_root(), alvo.resolve())


class TestRootMarkersAcompanhaConfig(unittest.TestCase):
    def setUp(self):
        _resetar_cache()
        self.addCleanup(_resetar_cache)

    def test_find_repo_root_usa_as_marcas_declaradas(self):
        with tempfile.TemporaryDirectory() as tmp:
            raiz = Path(tmp).resolve()
            (raiz / "marca-propria").mkdir()
            sub = raiz / "sub"
            sub.mkdir()

            caminho_config = raiz / "config.json"
            caminho_config.write_text(
                json.dumps({"root_markers": ["marca-propria"]}), encoding="utf-8"
            )

            with mock.patch.object(lib, "_config_path", return_value=caminho_config):
                self.assertEqual(lib._find_repo_root(sub), raiz)


class TestRunnersAcompanhaConfig(unittest.TestCase):
    """O mapa `runners` do config substitui o if/elif fixo por extensão."""

    def setUp(self):
        _resetar_cache()
        self.addCleanup(_resetar_cache)

    def test_extensao_declarada_no_config_e_usada(self):
        with tempfile.TemporaryDirectory() as tmp:
            raiz = Path(tmp).resolve()
            (raiz / "test_algo.rb").write_text("# ruby\n", encoding="utf-8")

            caminho_config = raiz / "config.json"
            caminho_config.write_text(
                json.dumps({"runners": {".rb": "scripts/test-ruby.sh"}}), encoding="utf-8"
            )

            with mock.patch.object(lib, "_config_path", return_value=caminho_config):
                comando, cwd = verificacao._comando(raiz / "test_algo.rb", raiz)

        self.assertEqual(comando, [str(raiz / "scripts" / "test-ruby.sh"), "test_algo.rb"])
        self.assertEqual(cwd, raiz)

    def test_extensao_fora_do_mapa_levanta_value_error(self):
        with tempfile.TemporaryDirectory() as tmp:
            raiz = Path(tmp).resolve()
            caminho_config = raiz / "config.json"
            with mock.patch.object(lib, "_config_path", return_value=caminho_config):
                with self.assertRaises(ValueError):
                    verificacao._comando(raiz / "test_algo.js", raiz)


class TestScaffoldSegueOAlvoDoConfig(unittest.TestCase):
    """Segunda metade do critério de aceite: `scaffold` grava no alvo que o config declara."""

    def setUp(self):
        _resetar_cache()
        self.addCleanup(_resetar_cache)

        self._tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self._tmp.cleanup)
        self.raiz = Path(self._tmp.name).resolve()

        self.plan_root_novo = self.raiz / "outro" / "lugar"
        (self.plan_root_novo / "_inbox").mkdir(parents=True)
        (self.plan_root_novo / "_planos.md").write_text(
            "<!-- planos:start -->\n"
            "| # | Plano | Core | Módulo | Origem | Situação | Aprovado |\n"
            "|---|---|---|---|---|---|---|\n"
            "<!-- planos:end -->\n",
            encoding="utf-8",
        )

        self.plano = self.plan_root_novo / "_inbox" / "evolucao-tools.md"
        self.plano.write_text(
            "---\n"
            'plan_id: ""\n'
            "core: builder\n"
            "module: evolucao-tools\n"
            'block: ""\n'
            "status: draft\n"
            "---\n\n"
            "# evolucao-tools\n",
            encoding="utf-8",
        )

        caminho_config = self.raiz / "config.json"
        caminho_config.write_text(json.dumps({"plan_root": "outro/lugar"}), encoding="utf-8")

        patcher_config_path = mock.patch.object(lib, "_config_path", return_value=caminho_config)
        patcher_config_path.start()
        self.addCleanup(patcher_config_path.stop)

        patcher_repo_root = mock.patch.object(lib, "repo_root", return_value=self.raiz)
        patcher_repo_root.start()
        self.addCleanup(patcher_repo_root.stop)

        patcher_move_md_root = mock.patch.object(scaffold.move_md, "REPO_ROOT", self.raiz)
        patcher_move_md_root.start()
        self.addCleanup(patcher_move_md_root.stop)

    def test_aprovar_grava_sob_o_plan_root_declarado(self):
        alvo = scaffold.aprovar(self.plano)
        self.assertTrue(alvo.is_relative_to(self.plan_root_novo))
        self.assertTrue(alvo.is_file())


if __name__ == "__main__":
    unittest.main()
