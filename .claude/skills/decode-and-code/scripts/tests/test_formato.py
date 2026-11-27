#!/usr/bin/env python3
"""Testes da versão do formato do plano e do tipo `rule` — subparte 2.2.03 do redesign (K-01, K-02).

Plano sem `format_version` é anterior ao redesign e segue a regra de antes, com o tipo `norma`;
plano com `format_version: 2` segue o codex, com o tipo `rule` no lugar (codex, *Plano anterior ao
redesign* e *Tipo*).
"""

from __future__ import annotations

import re
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import lib
import lint_plano
import lint_unidade
import scaffold
from tests import fixtures


def _arquivo(dir_plano: Path) -> Path:
    return dir_plano / f"{dir_plano.name}.md"


class TestFormato(unittest.TestCase):
    def setUp(self) -> None:
        self._tmp = tempfile.TemporaryDirectory()
        self.raiz = Path(self._tmp.name)

    def tearDown(self) -> None:
        self._tmp.cleanup()

    def test_plano_sem_campo_e_do_formato_anterior(self) -> None:
        plano = _arquivo(fixtures.plano(self.raiz))
        self.assertEqual(lib.formato(plano), lib.FORMATO_ANTERIOR)

    def test_plano_declara_o_formato_atual(self) -> None:
        plano = _arquivo(fixtures.plano(self.raiz, format_version=2))
        self.assertEqual(lib.formato(plano), lib.FORMATO_ATUAL)

    def test_formato_desconhecido_levanta_com_o_caminho(self) -> None:
        plano = _arquivo(fixtures.plano(self.raiz, format_version=7))
        with self.assertRaises(ValueError) as erro:
            lib.formato(plano)
        self.assertIn(str(plano), str(erro.exception))

    def test_unidade_herda_o_formato_do_plano(self) -> None:
        dir_plano = fixtures.plano(self.raiz, format_version=2)
        unidade = dir_plano / "01-algo.md"
        unidade.write_text("---\nunit_id: 0009-01\n---\n", encoding="utf-8")
        self.assertEqual(lib.formato(unidade), lib.FORMATO_ATUAL)

    def test_campo_da_unidade_vale_sobre_o_do_plano(self) -> None:
        dir_plano = fixtures.plano(self.raiz, format_version=2)
        unidade = dir_plano / "01-algo.md"
        unidade.write_text("---\nformat_version: 1\n---\n", encoding="utf-8")
        self.assertEqual(lib.formato(unidade), lib.FORMATO_ANTERIOR)

    def test_vocabulario_troca_norma_por_rule(self) -> None:
        anterior = set(lib.PLAN_TYPES_POR_FORMATO[lib.FORMATO_ANTERIOR])
        atual = set(lib.PLAN_TYPES_POR_FORMATO[lib.FORMATO_ATUAL])
        self.assertEqual(anterior - atual, {"norma"})
        self.assertEqual(atual - anterior, {"rule"})


class TestTipoPorFormato(unittest.TestCase):
    """`lint_plano` e `scaffold.aprovar` leem o vocabulário pelo formato do plano."""

    def _lint(self, plan_type: str, format_version: int | None) -> list[str]:
        with tempfile.TemporaryDirectory() as tmp:
            dir_plano = fixtures.plano(
                Path(tmp), plan_size="médio", tarefas=True, plan_type=plan_type,
                format_version=format_version,
            )
            return [p for p in lint_plano.lint(_arquivo(dir_plano)) if "plan_type" in p
                    or "format_version" in p]

    def test_rule_no_formato_atual_aprova(self) -> None:
        self.assertEqual(self._lint("rule", 2), [])

    def test_norma_no_formato_atual_reprova(self) -> None:
        problemas = self._lint("norma", 2)
        self.assertEqual(len(problemas), 1, problemas)
        self.assertIn("formato 2", problemas[0])

    def test_norma_no_formato_anterior_aprova(self) -> None:
        self.assertEqual(self._lint("norma", None), [])

    def test_rule_no_formato_anterior_reprova(self) -> None:
        self.assertEqual(len(self._lint("rule", None)), 1)

    def test_formato_desconhecido_entra_como_problema(self) -> None:
        problemas = self._lint("feature", 9)
        self.assertTrue(any("format_version" in p for p in problemas), problemas)

    def test_aprovar_recusa_norma_no_formato_atual(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            plano = fixtures.plano(
                Path(tmp), plan_type="norma", format_version=2, com_diretorio=False,
                status="draft",
            )
            # plano sem número, como no `_inbox`: o gate só roda sobre o que ainda não foi aprovado
            texto = plano.read_text(encoding="utf-8")
            plano.write_text(re.sub(r"(?m)^plan_id: .*$", 'plan_id: ""', texto), encoding="utf-8")
            with self.assertRaises(ValueError) as erro:
                scaffold.aprovar(plano, dry_run=True)
            self.assertIn("plan_type", str(erro.exception))


class TestUnidadePorFormato(unittest.TestCase):
    """`unit_type: rule` no formato atual; `norma` só no anterior. Os dois exigem `test` vazio."""

    def _problemas(self, unit_type: str, format_version: int | None, test: str = "") -> list[str]:
        with tempfile.TemporaryDirectory() as tmp:
            dir_plano = fixtures.plano(Path(tmp), format_version=format_version)
            unidade = fixtures.unidade(dir_plano, unit_type=unit_type, test=test)
            return [p for p in lint_unidade.lint(unidade) if "unit_type" in p or "test" in p]

    def test_rule_no_formato_atual(self) -> None:
        self.assertEqual(self._problemas("rule", 2), [])

    def test_norma_no_formato_atual_reprova(self) -> None:
        self.assertTrue(any("unit_type inválido" in p for p in self._problemas("norma", 2)))

    def test_norma_no_formato_anterior(self) -> None:
        self.assertEqual(self._problemas("norma", None), [])

    def test_rule_exige_test_vazio(self) -> None:
        problemas = self._problemas("rule", 2, test="tests/test_x.py")
        self.assertTrue(any("exige test: vazio" in p for p in problemas), problemas)


if __name__ == "__main__":
    unittest.main()
