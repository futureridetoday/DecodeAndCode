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
        for destino in ("metodo", "método: M-01", "descartado:", "H-", "qualquer"):
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


class TestMetodo(_Projeto):
    """Plano 0019 — o `M-XX`: gravado do huddle ou do `E-XX`, listado, e só sai por `levado`."""

    def test_campos_e_evidencia_so_e_xx_ou_l_xx(self):
        for evidencia, esperada in (("E-03 do derive", "E-03"), ("L-04", "L-04"),
                                    ("bloqueio: sem-segredo", ""), ("", "")):
            with self.subTest(evidencia=evidencia):
                id_metodo = eventos.registrar_metodo(self.p, "H-01", "Texto genérico.", evidencia, agora=AGORA)
                arquivo = self.p / ".claude" / "log" / "metodo" / f"{id_metodo}.md"
                self.assertEqual(eventos._campo(arquivo, "evidencia"), esperada)
                self.assertEqual(eventos._campo(arquivo, "origem"), "H-01")
                self.assertIn("Texto genérico.", arquivo.read_text(encoding="utf-8"))
                self.assertNotIn("sem-segredo", arquivo.read_text(encoding="utf-8"))

    def test_projeto_sem_bootstrap_nao_grava(self):
        (self.p / "docs" / "plan" / "_planos.md").unlink()
        self.assertIsNone(eventos.registrar_metodo(self.p, "H-01", "x"))

    def test_falha_de_escrita_devolve_none(self):
        (self.p / ".claude" / "log").mkdir()
        (self.p / ".claude" / "log" / "metodo").write_text("arquivo no lugar da pasta", encoding="utf-8")
        self.assertIsNone(eventos.registrar_metodo(self.p, "H-01", "x"))

    def test_listar_e_levar_sem_reusar_id(self):
        eventos.registrar_metodo(self.p, "H-01", "a", agora=AGORA)
        eventos.registrar_metodo(self.p, "E-02", "b", agora=AGORA)
        self.assertEqual([(m["id"], m["origem"]) for m in eventos.metodos(self.p)], [("M-01", "H-01"), ("M-02", "E-02")])
        self.assertIsNone(eventos.levado(self.p, "M-01", "DecodeAndCode H-22"))
        self.assertIsNone(eventos.levado(self.p, "M-02", "L-07"))
        self.assertEqual(eventos.metodos(self.p), [])
        self.assertEqual(eventos.eventos(self.p)[-2], {**eventos.eventos(self.p)[-2], "classe": "levado", "id": "M-01", "onde": "DecodeAndCode H-22"})
        self.assertEqual(eventos.registrar_metodo(self.p, "H-03", "c"), "M-03")

    def test_levado_recusa_sem_apagar(self):
        eventos.registrar_metodo(self.p, "H-01", "a")
        self.assertIn("onde", eventos.levado(self.p, "M-01", "   "))
        self.assertIn("formato", eventos.levado(self.p, "E-01", "x"))
        self.assertIn("não encontrado", eventos.levado(self.p, "M-09", "x"))
        self.assertEqual(len(eventos.metodos(self.p)), 1)


class TestResolverParaMetodo(_Projeto):
    """Plano 0019, `D-05` e `D-06` — o `E-XX` vira `M-XX` sem caminho absoluto, alvo, HEAD nem working tree."""

    def setUp(self):
        super().setUp()
        self.git_init()
        (self.p / "solto.txt").write_text("x", encoding="utf-8")
        self.home = Path.home()
        saida = (f'Traceback (most recent call last):\n  File "{self.p}/docs/x.py", line 1\n'
                 f'  File "{self.home}/.claude/plugins/dc.py", line 9\nValueError: falhou\n'
                 f"FileNotFoundError: '{self.p}/docs/plan/model/0007-x/01.md'")
        eventos.registrar_erro(self.p, ["normas", "docs/plan/model/0007-x/01.md"], 2, saida, "docs/plan/model/0007-x/01.md", AGORA)
        self.erro = self.p / ".claude" / "log" / "erros" / "E-01.md"

    def test_m_xx_sem_caminho_absoluto_alvo_head_nem_working_tree(self):
        self.assertIsNone(eventos.resolver(self.p, "E-01", "método"))
        self.assertFalse(self.erro.exists())
        [metodo] = eventos.metodos(self.p)
        texto = metodo["arquivo"].read_text(encoding="utf-8")
        self.assertEqual(metodo["origem"], "E-01")
        for ausente in (str(self.p), str(self.home), "0007-x", "head:", "alvo:", "solto.txt", "Working tree"):
            self.assertNotIn(ausente, texto)
        for presente in ('"<projeto>/docs/x.py"', '"~/.claude/plugins/dc.py"', "ValueError: falhou", "`dc.py normas`", "Saída 2",
                         "'<projeto>/<alvo>'"):
            self.assertIn(presente, texto)
        self.assertRegex(texto, r'versao: "\d+\.\d+\.\d+')
        self.assertEqual(eventos.eventos(self.p, AGORA)[-1]["destino"], "método: M-01")

    def test_gravacao_falhando_mantem_o_e_xx(self):
        (self.p / ".claude" / "log" / "metodo").write_text("arquivo no lugar da pasta", encoding="utf-8")
        self.assertIn("continua aberto", eventos.resolver(self.p, "E-01", "método"))
        self.assertTrue(self.erro.exists())


if __name__ == "__main__":
    unittest.main()
