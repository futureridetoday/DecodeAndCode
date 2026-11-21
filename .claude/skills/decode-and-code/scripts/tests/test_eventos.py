#!/usr/bin/env python3
"""Testes de `eventos.py` — plano 0018, o log de uso do método."""

from __future__ import annotations

import subprocess
import sys
import tempfile
import unittest
from unittest import mock
from datetime import date, datetime, timedelta
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import eventos

AGORA = datetime(2026, 11, 20, 10, 0, 0)


def _git(projeto: Path, *args: str) -> str:
    return subprocess.run(["git", *args], cwd=projeto, capture_output=True, text=True, check=True).stdout


class _Projeto(unittest.TestCase):
    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self._tmp.cleanup)
        self.p = Path(self._tmp.name).resolve()
        (self.p / "docs" / "plan").mkdir(parents=True)
        (self.p / "docs" / "plan" / "_planos.md").write_text("x\n", encoding="utf-8")
        (self.p / ".claude").mkdir()

    def git_init(self):
        _git(self.p, "init", "-q")
        _git(self.p, "config", "user.name", "Teste")
        _git(self.p, "config", "user.email", "teste@example.invalid")
        _git(self.p, "add", "-A")
        _git(self.p, "commit", "-qm", "inicial")


class TestRegistrar(_Projeto):
    def test_primeira_escrita_cria_a_pasta_que_o_git_ignora(self):
        self.git_init()
        eventos.registrar(self.p, {"classe": "comando", "comando": ["bootstrap"]}, AGORA)
        self.assertEqual((self.p / ".claude" / "log" / ".gitignore").read_text(encoding="utf-8"), "*\n")
        self.assertEqual(_git(self.p, "status", "--porcelain"), "")
        self.assertEqual(eventos.eventos(self.p, AGORA), [{"data": "2026-11-20T10:00:00", "classe": "comando", "comando": ["bootstrap"]}])

    def test_projeto_sem_bootstrap_nao_ganha_a_pasta(self):
        (self.p / "docs" / "plan" / "_planos.md").unlink()
        eventos.registrar(self.p, {"classe": "comando"}, AGORA)
        self.assertIsNone(eventos.registrar_erro(self.p, ["x"], 2, "falhou"))
        self.assertFalse((self.p / ".claude" / "log").exists())

    def test_evento_vencido_some_da_leitura_e_sai_no_consumir(self):
        eventos.registrar(self.p, {"classe": "velho"}, AGORA - timedelta(days=15))
        eventos.registrar(self.p, {"classe": "novo"}, AGORA)
        self.assertEqual([e["classe"] for e in eventos.eventos(self.p, AGORA)], ["novo"])
        arquivo = self.p / ".claude" / "log" / "eventos.jsonl"
        self.assertIn("velho", arquivo.read_text(encoding="utf-8"))
        eventos.consumir(self.p, 0)
        self.assertNotIn("velho", arquivo.read_text(encoding="utf-8"))

    def test_consumir_apaga_por_posicao_mesmo_no_mesmo_segundo(self):
        for classe in ("a", "b", "c"):
            eventos.registrar(self.p, {"classe": classe}, AGORA)
        with mock.patch.object(eventos, "_agora", return_value=AGORA):
            self.assertEqual(eventos.consumir(self.p, 2), 2)
            self.assertEqual([e["classe"] for e in eventos.eventos(self.p, AGORA)], ["c"])
            self.assertEqual(eventos.consumir(self.p, 9), 1)

    def test_falha_de_escrita_nao_levanta(self):
        (self.p / ".claude" / "log").write_text("é arquivo, não pasta", encoding="utf-8")
        eventos.registrar(self.p, {"classe": "comando"}, AGORA)
        self.assertIsNone(eventos.registrar_erro(self.p, ["x"], 2, "falhou"))


class TestErro(_Projeto):
    def test_campos_do_e_xx(self):
        self.git_init()
        (self.p / "solto.txt").write_text("x", encoding="utf-8")
        saida = "\n".join(f"linha {i}" for i in range(100))
        id_erro = eventos.registrar_erro(self.p, ["normas", "u.md"], 2, saida, "u.md", AGORA)
        self.assertEqual(id_erro, "E-01")
        texto = (self.p / ".claude" / "log" / "erros" / "E-01.md").read_text(encoding="utf-8")
        for esperado in ('id: "E-01"', 'comando: "normas u.md"', "codigo: 2", 'alvo: "u.md"',
                         'data: "2026-11-20T10:00:00"', "linha 99", "[`solto.txt`](../../../solto.txt)"):
            self.assertIn(esperado, texto)
        self.assertNotIn("linha 59\n", texto)
        self.assertRegex(texto, r'head: "[0-9a-f]{40}"')
        self.assertRegex(texto, r'versao: "\d+\.\d+\.\d+')
        self.assertEqual(eventos.eventos(self.p, AGORA)[-1]["classe"], "erro")

    def test_numeracao_nao_reutiliza_id_resolvido(self):
        eventos.registrar_erro(self.p, ["x"], 2, "falhou", agora=AGORA)
        self.assertIsNone(eventos.resolver(self.p, "E-01", "descartado: teste"))
        (self.p / ".claude" / "log" / "eventos.jsonl").unlink()
        self.assertEqual(eventos.registrar_erro(self.p, ["x"], 2, "falhou", agora=AGORA), "E-02")

    def test_atrasados(self):
        eventos.registrar_erro(self.p, ["x"], 2, "falhou", agora=AGORA - timedelta(days=8))
        eventos.registrar_erro(self.p, ["y"], 2, "falhou", agora=AGORA - timedelta(days=6))
        self.assertEqual(eventos.erros(self.p), [("E-01", "2026-11-12T10:00:00"), ("E-02", "2026-11-14T10:00:00")])
        self.assertEqual(eventos.atrasados(self.p, date(2026, 11, 20)), ["E-01"])


class TestResolver(_Projeto):
    def setUp(self):
        super().setUp()
        eventos.registrar_erro(self.p, ["x"], 2, "falhou", agora=AGORA)
        self.arquivo = self.p / ".claude" / "log" / "erros" / "E-01.md"

    def test_destino_fora_do_vocabulario_nao_apaga(self):
        for destino in ("método", "descartado:", "H-", "qualquer"):
            with self.subTest(destino=destino):
                self.assertIn("vocabulário", eventos.resolver(self.p, "E-01", destino))
        self.assertTrue(self.arquivo.exists())

    def test_h_xx_que_nao_esta_aberto_nao_apaga(self):
        self.assertIn("abertas", eventos.resolver(self.p, "E-01", "H-09", abertas={"H-01"}))
        self.assertTrue(self.arquivo.exists())

    def test_resolve_e_registra_o_destino(self):
        self.assertIsNone(eventos.resolver(self.p, "E-01", "H-01", abertas={"H-01"}))
        self.assertFalse(self.arquivo.exists())
        self.assertEqual(eventos.eventos(self.p, AGORA)[-1]["destino"], "H-01")

    def test_id_inexistente(self):
        self.assertIn("não encontrado", eventos.resolver(self.p, "E-07", "L-01"))


if __name__ == "__main__":
    unittest.main()
