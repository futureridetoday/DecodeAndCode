#!/usr/bin/env python3
"""Testes do hook `SessionStart` — plano 0008, T6.

Roda o hook de verdade, por subprocesso, com `CLAUDE_PROJECT_DIR` num projeto git `tempfile`, e a
configuração global e de sistema do git isoladas pelo ambiente.
"""

from __future__ import annotations

import json
import os
import subprocess
import sys
import tempfile
import unittest
from datetime import date, timedelta
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import huddle
import lib
import regioes
import setup

HOOK = lib.repo_root() / ".claude" / "hooks" / "session_start.py"


class _Projeto(unittest.TestCase):
    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self._tmp.cleanup)
        self.projeto = Path(self._tmp.name).resolve()
        self.ambiente = {
            **os.environ, "GIT_CONFIG_GLOBAL": os.devnull, "GIT_CONFIG_NOSYSTEM": "1",
            "CLAUDE_PROJECT_DIR": str(self.projeto),
        }
        for args in (["init", "-q"], ["config", "user.name", "Ana"]):
            subprocess.run(["git", *args], cwd=self.projeto, check=True, env=self.ambiente)
        self.setup_md = setup.iniciar(self.projeto)
        setup.concluir(self.setup_md, date.today().isoformat())
        self.arquivo = huddle.caminho(self.projeto, "ana")
        huddle.iniciar(self.arquivo, projeto=self.projeto, usuario="ana")
        huddle.abrir(self.arquivo, "pergunta", "x", "ana")

    def ha_dias(self, dias: int) -> str:
        return (date.today() - timedelta(days=dias)).isoformat()

    def hook(self) -> subprocess.CompletedProcess:
        return subprocess.run(
            [sys.executable, str(HOOK)], input="{}", capture_output=True, text=True,
            env=self.ambiente, timeout=30,
        )

    def saida(self) -> dict | None:
        r = self.hook()
        self.assertEqual(r.returncode, 0, r.stderr)
        self.assertEqual(r.stderr, "")
        return json.loads(r.stdout) if r.stdout.strip() else None


class TestAviso(_Projeto):
    def test_seis_dias_e_silencioso(self):
        huddle.concluir(self.arquivo, self.ha_dias(6))
        self.assertIsNone(self.saida())

    def test_sete_dias_avisa_a_pessoa_e_o_modelo(self):
        huddle.concluir(self.arquivo, self.ha_dias(7))
        saida = self.saida()
        self.assertIn("1", saida["systemMessage"])
        self.assertIn("7", saida["systemMessage"])
        self.assertIn("/decode-and-code:huddle", saida["systemMessage"])
        especifico = saida["hookSpecificOutput"]
        self.assertEqual(especifico["hookEventName"], "SessionStart")
        self.assertIn("/decode-and-code:huddle", especifico["additionalContext"])

    def test_oito_dias_avisa(self):
        huddle.concluir(self.arquivo, self.ha_dias(8))
        self.assertIn("8", self.saida()["systemMessage"])

    def test_reminder_days_zero_desliga(self):
        huddle.concluir(self.arquivo, self.ha_dias(30))
        regioes.escrever_campos(self.arquivo, {"reminder_days": "0"})
        self.assertIsNone(self.saida())

    def test_reminder_days_invalido_vale_sete(self):
        huddle.concluir(self.arquivo, self.ha_dias(7))
        regioes.escrever_campos(self.arquivo, {"reminder_days": "sete"})
        self.assertIsNotNone(self.saida())

    def test_last_huddle_ausente_conta_desde_created(self):
        texto = "".join(
            l for l in self.arquivo.read_text(encoding="utf-8").splitlines(True)
            if not l.startswith("last_huddle:")
        )
        self.arquivo.write_text(texto, encoding="utf-8")
        regioes.escrever_campos(self.arquivo, {"created": self.ha_dias(10)})
        self.assertIn("10", self.saida()["systemMessage"])

    def test_sem_entrada_aberta_e_silencioso(self):
        huddle.concluir(self.arquivo, self.ha_dias(30))
        huddle.fechar(self.arquivo, "H-01", "descartada")
        self.assertIsNone(self.saida())

    def test_outra_pessoa_com_abertas_nao_gera_aviso(self):
        huddle.fechar(self.arquivo, "H-01", "descartada")
        huddle.concluir(self.arquivo, self.ha_dias(30))
        outro = huddle.caminho(self.projeto, "beto")
        huddle.abrir(outro, "pergunta", "y", "beto")
        regioes.escrever_campos(outro, {"created": self.ha_dias(30)})
        self.assertIsNone(self.saida())


class TestSetup(_Projeto):
    def assertAvisoSetup(self, saida):
        self.assertIn("/decode-and-code:setup", saida["systemMessage"])
        especifico = saida["hookSpecificOutput"]
        self.assertEqual(especifico["hookEventName"], "SessionStart")
        self.assertIn("/decode-and-code:setup", especifico["additionalContext"])

    def test_sem_setup_md_propoe_o_setup(self):
        self.setup_md.unlink()
        self.assertAvisoSetup(self.saida())

    def test_completed_at_vazio_propoe_o_setup(self):
        regioes.escrever_campos(self.setup_md, {"completed_at": ""})
        self.assertAvisoSetup(self.saida())

    def test_concluido_nao_avisa_setup(self):
        self.assertIsNone(self.saida())

    def test_setup_pendente_com_huddle_atrasado_so_avisa_setup(self):
        huddle.concluir(self.arquivo, self.ha_dias(30))
        regioes.escrever_campos(self.setup_md, {"completed_at": ""})
        saida = self.saida()
        self.assertAvisoSetup(saida)
        self.assertNotIn("huddle", saida["systemMessage"].lower())

    def test_projeto_sem_docs_nem_claude_nem_user_name(self):
        with tempfile.TemporaryDirectory() as vazio:
            ambiente = {**self.ambiente, "CLAUDE_PROJECT_DIR": str(Path(vazio).resolve())}
            r = subprocess.run(
                [sys.executable, str(HOOK)], input="{}", capture_output=True, text=True,
                env=ambiente, timeout=30,
            )
        self.assertEqual(r.returncode, 0, r.stderr)
        self.assertAvisoSetup(json.loads(r.stdout))

    def test_sem_user_name_avisa_setup(self):
        subprocess.run(["git", "config", "--unset", "user.name"], cwd=self.projeto, check=True, env=self.ambiente)
        regioes.escrever_campos(self.setup_md, {"completed_at": ""})
        self.assertAvisoSetup(self.saida())


class TestSilencioEmErro(_Projeto):
    def test_sem_arquivo_da_pessoa(self):
        self.arquivo.unlink()
        self.assertIsNone(self.saida())

    def test_sem_user_name(self):
        subprocess.run(["git", "config", "--unset", "user.name"], cwd=self.projeto, check=True, env=self.ambiente)
        self.assertIsNone(self.saida())

    def test_frontmatter_quebrado(self):
        self.arquivo.write_text("sem frontmatter\n## Abertas\n### H-01 · `pergunta` · 2020-01-01 · a\n", encoding="utf-8")
        self.assertIsNone(self.saida())

    def test_sem_claude_project_dir(self):
        del self.ambiente["CLAUDE_PROJECT_DIR"]
        self.assertIsNone(self.saida())


if __name__ == "__main__":
    unittest.main()
