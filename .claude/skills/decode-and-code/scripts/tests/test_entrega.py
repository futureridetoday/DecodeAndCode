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
    def _plano(self, tarefas: str, plan_id: str = '"0002"') -> Path:
        tmp = tempfile.TemporaryDirectory()
        self.addCleanup(tmp.cleanup)
        plano = Path(tmp.name) / "0002-fix-algo.md"
        plano.write_text(
            f"---\nplan_id: {plan_id}\nstatus: approved\nplan_size: pequeno\nplan_type: fix\n"
            "format_version: 2\napproved_by: Ana\napproved_at: 2026-11-27\n---\n\n# fix-algo\n\n"
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

    def test_aprovar_com_tudo_feito_fecha_o_plano(self) -> None:
        plano = entrega.aprovar(self._plano("- [x] fazer\n- [x] conferir"), "Ana")
        self.assertEqual(regioes.ler_campo(plano, "status"), "done")


class TestSkillDoCode(unittest.TestCase):
    def test_le_as_mesmas_secoes_que_o_handoff_cita(self) -> None:
        texto = (lib.repo_root() / ".claude" / "skills" / "code" / "SKILL.md").read_text(encoding="utf-8")
        linha = re.search(r'dc\.py" codex (.+)`', texto)
        self.assertIsNotNone(linha)
        self.assertEqual(tuple(shlex.split(linha[1])), handoff.SECOES_DO_CODE)


if __name__ == "__main__":
    unittest.main()
