#!/usr/bin/env python3
"""Testes do gate de entrada do code e da aprovação da entrega — subparte 2.2.09 (K-06).

Codex, *Code*: a próxima unidade só começa depois da aprovação da anterior. *Aprovação*: cada
entrega é aprovada com o teste (P7); no pequeno, a aprovação da entrega única é a final.
"""

from __future__ import annotations

import re
import shlex
import sys
import tempfile
import unittest
from pathlib import Path
from unittest import mock

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import entrega
import handoff
import lib
import regioes
from tests.test_formato_derive import UNIDADE


class _Plano(unittest.TestCase):
    def setUp(self) -> None:
        self._tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self._tmp.cleanup)
        self.raiz = Path(self._tmp.name).resolve()
        self.dir_plano = self.raiz / "0001-add-algo"
        self.dir_plano.mkdir()
        (self.dir_plano / "0001-add-algo.md").write_text(
            "---\nplan_id: \"0001\"\nstatus: approved\nplan_size: grande\nplan_type: feature\n"
            "format_version: 2\n---\n\n# add-algo\n",
            encoding="utf-8",
        )
        for nome in ("repo_root", "plan_root"):
            p = mock.patch.object(lib, nome, return_value=self.raiz)
            p.start()
            self.addCleanup(p.stop)

    def unidade(self, nn: str, **campos: str) -> Path:
        texto = UNIDADE.replace("unit_id: 0001-01", f"unit_id: 0001-{nn}")
        for chave, valor in campos.items():
            texto = re.sub(rf"(?m)^{chave}: .*$", f"{chave}: {valor}", texto)
        caminho = self.dir_plano / f"{nn}-algo.md"
        caminho.write_text(texto, encoding="utf-8")
        return caminho


class TestEntrada(_Plano):
    def test_primeira_unidade_pode_comecar(self) -> None:
        self.assertEqual(entrega.entrada(self.unidade("01")), [])

    def test_segunda_espera_a_aprovacao_da_primeira(self) -> None:
        self.unidade("01", state="verified")
        problemas = entrega.entrada(self.unidade("02"))
        self.assertEqual(problemas, ["a unidade anterior 0001-01 ainda não teve a entrega aprovada (P7)"])

    def test_com_a_anterior_aprovada_pode_comecar(self) -> None:
        self.unidade("01", state="verified", approved_by="Ana", approved_at="2026-11-27")
        self.assertEqual(entrega.entrada(self.unidade("02")), [])

    def test_arquivo_que_nao_e_unidade_nem_plano_pequeno(self) -> None:
        problemas = entrega.entrada(self.dir_plano / "0001-add-algo.md")
        self.assertTrue(problemas[0].startswith("o code recebe uma unidade"), problemas)


class TestAprovar(_Plano):
    def test_dev_sem_teste_verde_recusa_sem_escrever(self) -> None:
        unidade = self.unidade("01")
        antes = unidade.read_text(encoding="utf-8")
        with self.assertRaises(ValueError):
            entrega.aprovar(unidade, "Ana", "2026-11-27")
        self.assertEqual(unidade.read_text(encoding="utf-8"), antes)

    def test_dev_verificada_grava_quem_e_quando(self) -> None:
        unidade = entrega.aprovar(self.unidade("01", state="verified"), "Ana", "2026-11-27")
        self.assertEqual(regioes.ler_campo(unidade, "approved_by"), "Ana")
        self.assertEqual(regioes.ler_campo(unidade, "approved_at"), "2026-11-27")

    def test_rule_se_aprova_antes_do_verificar(self) -> None:
        unidade = self.unidade("01", unit_type="rule", test='""')
        entrega.aprovar(unidade, "Ana", "2026-11-27")
        self.assertEqual(regioes.ler_campo(unidade, "approved_at"), "2026-11-27")

    def test_sem_quem_aprova_recusa(self) -> None:
        with self.assertRaises(ValueError):
            entrega.aprovar(self.unidade("01", state="verified"), "  ")

    def test_formato_1_recusa(self) -> None:
        plano = self.dir_plano / "0001-add-algo.md"
        plano.write_text(plano.read_text(encoding="utf-8").replace("format_version: 2\n", ""), encoding="utf-8")
        with self.assertRaises(ValueError):
            entrega.aprovar(self.unidade("01", state="verified"), "Ana")


class TestPequeno(unittest.TestCase):
    def _plano(self, tarefas: str, plan_id: str = '"0002"', state: str = "verified") -> Path:
        tmp = tempfile.TemporaryDirectory()
        self.addCleanup(tmp.cleanup)
        plano = Path(tmp.name) / "0002-fix-algo.md"
        plano.write_text(
            f"---\nplan_id: {plan_id}\nstatus: approved\nplan_size: pequeno\nplan_type: chore\n"
            "format_version: 2\napproved_by: Ana\napproved_at: 2026-11-27\ntest: tests/test_x.py\n"
            f"state: {state}\nverified_at: \"\"\n---\n\n# fix-algo\n\n"
            "## Objetivo\n\nx\n\n## Histórias\n\nx\n\n## Independência\n\nx\n\n## Recursos\n\nnenhum\n\n"
            f"## Tarefas\n\n{tarefas}\n",
            encoding="utf-8",
        )
        return plano

    def test_entrada_do_pequeno_aprovado(self) -> None:
        self.assertEqual(entrega.entrada(self._plano("- [ ] fazer")), [])

    def test_entrada_do_pequeno_sem_numero(self) -> None:
        problemas = entrega.entrada(self._plano("- [ ] fazer", plan_id='""'))
        self.assertIn("plano sem número: a revisão o aprova (P4) antes do code", problemas)

    def test_aprovar_com_tarefa_aberta_recusa(self) -> None:
        with self.assertRaises(ValueError):
            entrega.aprovar(self._plano("- [x] fazer\n- [ ] conferir"), "Ana")

    def test_aprovar_sem_teste_verde_recusa(self) -> None:
        with self.assertRaisesRegex(ValueError, "teste verde"):
            entrega.aprovar(self._plano("- [x] fazer", state="spec"), "Ana")

    def test_aprovar_com_tudo_feito_fecha_o_plano(self) -> None:
        plano = entrega.aprovar(self._plano("- [x] fazer\n- [x] conferir"), "Ana")
        self.assertEqual(regioes.ler_campo(plano, "status"), "done")


class TestVerificarNoPequeno(unittest.TestCase):
    """O pequeno não tem unidade: o `verificar` roda o teste que o plano declara e projeta o estado
    no próprio plano — o caminho determinístico até o teste, que o teste ponta a ponta mostrou faltar."""

    def test_projeta_verified_no_plano_e_libera_a_aprovacao(self) -> None:
        import verificacao

        tmp = tempfile.TemporaryDirectory()
        self.addCleanup(tmp.cleanup)
        raiz = Path(tmp.name).resolve()
        (raiz / "tests").mkdir()
        (raiz / "tests" / "test_x.py").write_text("x\n", encoding="utf-8")
        plano = TestPequeno._plano(self, "- [x] fazer", state="spec")
        with mock.patch.object(lib, "repo_root", return_value=raiz), mock.patch.object(
            verificacao, "_executar", return_value=(0, "Ran 3 tests\n\nOK\n")
        ):
            estado, escreveu = verificacao.verificar(plano)
        self.assertEqual((estado, escreveu), ("verified", True))
        self.assertEqual(regioes.ler_campo(plano, "state"), "verified")
        entrega.aprovar(plano, "Ana")
        self.assertEqual(regioes.ler_campo(plano, "status"), "done")


class TestDcNoPequeno(unittest.TestCase):
    """Achados da 2ª rodada do ponta a ponta: `aprovar-entrega` fecha o plano em `_planos.md` na hora,
    e `normas` sobre o plano pequeno responde sem erro."""

    def setUp(self) -> None:
        import dc

        self.dc = dc
        tmp = tempfile.TemporaryDirectory()
        self.addCleanup(tmp.cleanup)
        self.raiz = Path(tmp.name).resolve()
        (self.raiz / "system").mkdir()
        cabecalho = "| # | Plano | Core | Módulo | Origem | Situação | Aprovado |\n|---|---|---|---|---|---|---|\n"
        (self.raiz / "_planos.md").write_text(
            f"<!-- planos:start -->\n{cabecalho}"
            "| 0002 | [fix-algo](0002-fix-algo.md) | — | | — | em desenvolvimento | 2026-11-27 |\n"
            "<!-- planos:end -->\n",
            encoding="utf-8",
        )
        self.plano = self.raiz / "0002-fix-algo.md"
        self.plano.write_text(
            TestPequeno._plano(self, "- [x] fazer").read_text(encoding="utf-8"), encoding="utf-8"
        )
        for nome in ("plan_root", "repo_root"):
            p = mock.patch.object(lib, nome, return_value=self.raiz)
            p.start()
            self.addCleanup(p.stop)
        p = mock.patch.object(dc, "_registrar")
        p.start()
        self.addCleanup(p.stop)

    def _rodar(self, *argv: str) -> str:
        import contextlib
        import io

        saida = io.StringIO()
        with contextlib.redirect_stdout(saida):
            self.assertEqual(self.dc.main(list(argv)), 0)
        return saida.getvalue()

    def test_aprovar_entrega_fecha_o_plano_em_planos_md(self) -> None:
        saida = self._rodar("aprovar-entrega", str(self.plano), "--por", "Ana")
        self.assertIn("situação: concluído", saida)
        self.assertIn("| concluído |", (self.raiz / "_planos.md").read_text(encoding="utf-8"))

    def test_normas_no_pequeno_responde_sem_erro(self) -> None:
        self.assertIn("plano pequeno", self._rodar("normas", str(self.plano)))


class TestSkillDoCode(unittest.TestCase):
    def test_le_as_mesmas_secoes_que_o_handoff_cita(self) -> None:
        texto = (lib.repo_root() / ".claude" / "skills" / "code" / "SKILL.md").read_text(encoding="utf-8")
        linha = re.search(r'dc\.py" codex (.+)`', texto)
        self.assertIsNotNone(linha)
        self.assertEqual(tuple(shlex.split(linha[1])), handoff.SECOES_DO_CODE)


if __name__ == "__main__":
    unittest.main()
