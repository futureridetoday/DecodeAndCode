#!/usr/bin/env python3
"""Teste declarado da unidade 0009-03 — `escopo.py`, o plugin no escopo do projeto."""

from __future__ import annotations

import json
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import escopo
import lib


class _Case(unittest.TestCase):
    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self._tmp.cleanup)
        self.projeto = Path(self._tmp.name).resolve() / "meu-projeto"
        self.projeto.mkdir()
        self.settings = self.projeto / ".claude" / "settings.json"
        self.mk = lib.config()["marketplace"]
        self.chave = f"{self.mk['plugin']}@{self.mk['name']}"

    def escrever(self, texto: str) -> None:
        self.settings.parent.mkdir(parents=True, exist_ok=True)
        self.settings.write_text(texto, encoding="utf-8")

    def ler(self) -> dict:
        return json.loads(self.settings.read_text(encoding="utf-8"))


class TestConfig(_Case):
    def test_config_traz_o_marketplace_do_proprio_plugin(self):
        self.assertEqual(self.mk["name"], "future-ride-today")
        self.assertEqual(self.mk["plugin"], "decode-and-code")
        self.assertEqual(self.mk["source"]["source"], "github")
        self.assertEqual(self.mk["source"]["repo"], "futureridetoday/DecodeAndCode")


class TestEstado(_Case):
    def test_sem_settings_nada_habilitado(self):
        self.assertEqual(escopo.estado(self.projeto), {"habilitado": "ausente", "marketplace": False})
        self.assertFalse(self.settings.exists())

    def test_reflete_o_que_esta_no_arquivo(self):
        self.escrever(json.dumps({"enabledPlugins": {self.chave: True}}))
        self.assertEqual(escopo.estado(self.projeto), {"habilitado": "true", "marketplace": False})
        self.escrever(json.dumps({"extraKnownMarketplaces": {self.mk["name"]: {"source": {}}}}))
        self.assertEqual(escopo.estado(self.projeto), {"habilitado": "ausente", "marketplace": True})

    def test_plugin_false_aparece_como_false_e_nao_como_ausente(self):
        self.escrever(json.dumps({"enabledPlugins": {self.chave: False}}))
        self.assertEqual(escopo.estado(self.projeto)["habilitado"], "false")

    def test_json_invalido_levanta(self):
        self.escrever("{ quebrado")
        with self.assertRaises(ValueError):
            escopo.estado(self.projeto)


class TestHabilitar(_Case):
    def test_preserva_hooks_e_permissions_e_acrescenta_so_as_duas_chaves(self):
        original = {
            "hooks": {"PreToolUse": [{"matcher": "Bash", "hooks": []}]},
            "permissions": {"allow": ["Bash(ls:*)"]},
        }
        self.escrever(json.dumps(original))
        self.assertTrue(escopo.habilitar(self.projeto))
        dados = self.ler()
        self.assertEqual(list(dados), ["hooks", "permissions", "enabledPlugins", "extraKnownMarketplaces"])
        for chave in original:
            self.assertEqual(json.dumps(dados[chave]), json.dumps(original[chave]))
        self.assertEqual(dados["enabledPlugins"], {self.chave: True})
        self.assertEqual(dados["extraKnownMarketplaces"], {self.mk["name"]: {"source": self.mk["source"]}})

    def test_segunda_chamada_devolve_false_e_nao_muda_o_arquivo(self):
        self.escrever(json.dumps({"hooks": {}}))
        escopo.habilitar(self.projeto)
        depois = self.settings.read_text(encoding="utf-8")
        self.assertFalse(escopo.habilitar(self.projeto))
        self.assertEqual(self.settings.read_text(encoding="utf-8"), depois)

    def test_sem_settings_cria_com_so_as_duas_chaves(self):
        self.assertTrue(escopo.habilitar(self.projeto))
        self.assertEqual(list(self.ler()), ["enabledPlugins", "extraKnownMarketplaces"])
        self.assertTrue(self.settings.read_text(encoding="utf-8").endswith("}\n"))

    def test_mantem_outros_plugins_e_marketplaces(self):
        self.escrever(json.dumps({
            "enabledPlugins": {"outro@m": True},
            "extraKnownMarketplaces": {"m": {"source": {"source": "github", "repo": "a/b"}}},
        }))
        escopo.habilitar(self.projeto)
        dados = self.ler()
        self.assertEqual(dados["enabledPlugins"], {"outro@m": True, self.chave: True})
        self.assertIn("m", dados["extraKnownMarketplaces"])
        self.assertIn(self.mk["name"], dados["extraKnownMarketplaces"])

    def test_plugin_false_fica_false(self):
        """E-06: no teste final, o `false` desligava a versão instalada; trocá-lo a reativaria."""
        self.escrever(json.dumps({"enabledPlugins": {self.chave: False}}))
        self.assertTrue(escopo.habilitar(self.projeto))  # acrescentou o marketplace
        self.assertIs(self.ler()["enabledPlugins"][self.chave], False)
        self.assertFalse(escopo.habilitar(self.projeto))

    def test_json_invalido_ou_raiz_nao_objeto_levanta_e_nao_muda_o_arquivo(self):
        for texto in ("{ quebrado", "[1, 2]"):
            with self.subTest(texto=texto):
                self.escrever(texto)
                with self.assertRaises(ValueError):
                    escopo.habilitar(self.projeto)
                self.assertEqual(self.settings.read_text(encoding="utf-8"), texto)


if __name__ == "__main__":
    unittest.main()
