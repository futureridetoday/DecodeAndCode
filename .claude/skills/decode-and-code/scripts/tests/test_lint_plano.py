#!/usr/bin/env python3
"""Teste declarado da unidade 0001-13 — formato de plano por porte e o `unit_type: norma`.

Três frentes, uma por oráculo que a unidade fecha:

- `lint_plano.lint` — os três portes bem formados devolvem `[]`, cada linha da tabela de portes
  recusa isoladamente (um problema só, nunca mais), `plan_size` ausente ou fora do vocabulário
  entra na lista sem levantar, e o plano real `0001` deste repositório — que é `grande` — aprova.
- `lint_unidade.lint` — aceita `unit_type: norma`, recusa a ausência de `approved_by`/`approved_at`,
  recusa `test:` preenchido em `norma` e vazio em `dev`, recusa a linha órfã `Último resultado` em
  qualquer unidade, e as onze unidades reais (`01` a `11`) continuam aprovando depois da remoção.
- `verificacao.verificar` — uma unidade `norma` fecha por aprovação, nunca por execução: `verified`
  sem rodar `subprocess` quando `approved_by`/`approved_at` estão preenchidos, `spec` sem eles.
"""

from __future__ import annotations

import sys
import tempfile
import unittest
from pathlib import Path
from unittest import mock

sys.path.insert(0, str(Path(__file__).resolve().parent))
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import fixtures
import lib
import lint_plano
import lint_unidade
import regioes
import verificacao
from fixtures import UNIDADE_VALIDA

PLANO_REAL_0001 = (
    lib.repo_root()
    / "docs"
    / "plan"
    / "model"
    / "0001-decode-and-code-foundation"
    / "0001-decode-and-code-foundation.md"
)

DIR_UNIDADES_REAIS = PLANO_REAL_0001.parent


def _arquivo(dir_plano: Path) -> Path:
    return dir_plano / f"{dir_plano.name}.md"


class TestTresPortesBemFormados(unittest.TestCase):
    """Um plano correto em cada porte aprova — sem ressalva."""

    def test_pequeno_sem_independencia_e_sem_backlog_aprova(self):
        with tempfile.TemporaryDirectory() as tmp:
            dir_plano = fixtures.plano(Path(tmp), plan_size="pequeno", com_backlog=False)
            self.assertEqual(lint_plano.lint(_arquivo(dir_plano)), [])

    def test_medio_com_tarefas_e_backlog_aprova(self):
        with tempfile.TemporaryDirectory() as tmp:
            dir_plano = fixtures.plano(Path(tmp), plan_size="médio", tarefas=True)
            self.assertEqual(lint_plano.lint(_arquivo(dir_plano)), [])

    def test_grande_com_escopo_independencia_e_backlog_aprova(self):
        with tempfile.TemporaryDirectory() as tmp:
            dir_plano = fixtures.plano(
                Path(tmp), plan_size="grande", previstas=2, independencia=True
            )
            self.assertEqual(lint_plano.lint(_arquivo(dir_plano)), [])


class TestRecusaIsoladaPorPorte(unittest.TestCase):
    """Cada linha da tabela de portes recusa sozinha — exatamente um problema, nunca mais."""

    def _assert_recusa_unica(self, dir_plano: Path, contem: str) -> None:
        problemas = lint_plano.lint(_arquivo(dir_plano))
        self.assertEqual(len(problemas), 1, problemas)
        self.assertIn(contem, problemas[0])

    def test_pequeno_com_independencia_recusa(self):
        with tempfile.TemporaryDirectory() as tmp:
            dir_plano = fixtures.plano(
                Path(tmp), plan_size="pequeno", com_backlog=False, independencia=True
            )
            self._assert_recusa_unica(dir_plano, "Independência")

    def test_pequeno_com_regiao_de_backlog_recusa(self):
        with tempfile.TemporaryDirectory() as tmp:
            dir_plano = fixtures.plano(Path(tmp), plan_size="pequeno")
            self._assert_recusa_unica(dir_plano, "backlog")

    def test_medio_sem_tarefas_recusa(self):
        with tempfile.TemporaryDirectory() as tmp:
            dir_plano = fixtures.plano(Path(tmp), plan_size="médio")
            self._assert_recusa_unica(dir_plano, "Tarefas")

    def test_medio_sem_regiao_de_backlog_recusa(self):
        with tempfile.TemporaryDirectory() as tmp:
            dir_plano = fixtures.plano(
                Path(tmp), plan_size="médio", tarefas=True, com_backlog=False
            )
            self._assert_recusa_unica(dir_plano, "backlog")

    def test_grande_sem_escopo_recusa(self):
        with tempfile.TemporaryDirectory() as tmp:
            dir_plano = fixtures.plano(Path(tmp), plan_size="grande", independencia=True)
            self._assert_recusa_unica(dir_plano, "Escopo")

    def test_grande_sem_independencia_recusa(self):
        with tempfile.TemporaryDirectory() as tmp:
            dir_plano = fixtures.plano(Path(tmp), plan_size="grande", previstas=2)
            self._assert_recusa_unica(dir_plano, "Independência")

    def test_grande_sem_regiao_de_backlog_recusa(self):
        with tempfile.TemporaryDirectory() as tmp:
            dir_plano = fixtures.plano(
                Path(tmp),
                plan_size="grande",
                previstas=2,
                independencia=True,
                com_backlog=False,
            )
            self._assert_recusa_unica(dir_plano, "backlog")


class TestPlanSizeAusenteOuInvalido(unittest.TestCase):
    """`plan_size` ausente ou fora do vocabulário entra na lista — `lint_plano` nunca levanta."""

    def test_plan_size_ausente_entra_como_problema(self):
        with tempfile.TemporaryDirectory() as tmp:
            dir_plano = fixtures.plano(Path(tmp), plan_size="pequeno", com_backlog=False)
            arquivo = _arquivo(dir_plano)
            texto = arquivo.read_text(encoding="utf-8").replace("plan_size: pequeno\n", "")
            arquivo.write_text(texto, encoding="utf-8")

            problemas = lint_plano.lint(arquivo)
            self.assertTrue(any("plan_size" in p for p in problemas), problemas)

    def test_plan_size_fora_do_vocabulario_entra_como_problema(self):
        with tempfile.TemporaryDirectory() as tmp:
            dir_plano = fixtures.plano(Path(tmp), plan_size="enorme")
            problemas = lint_plano.lint(_arquivo(dir_plano))
            self.assertTrue(any("plan_size" in p for p in problemas), problemas)


class TestPlanoRealDoRepositorio(unittest.TestCase):
    def test_plano_0001_grande_aprova(self):
        self.assertEqual(lint_plano.lint(PLANO_REAL_0001), [])


class TestLintUnidadeAceitaTipoNorma(unittest.TestCase):
    """`unit_type: norma` — aceita bem formada, recusa cada ausência e a linha órfã em qualquer tipo."""

    def test_norma_com_aprovacao_e_test_vazio_aprova(self):
        with tempfile.TemporaryDirectory() as tmp:
            alvo = fixtures.unidade(
                Path(tmp),
                unit_type="norma",
                test='""',
                approved_by="Bortoli",
                approved_at="2026-08-25",
            )
            self.assertEqual(lint_unidade.lint(alvo), [])

    def test_norma_sem_approved_by_recusa(self):
        with tempfile.TemporaryDirectory() as tmp:
            alvo = fixtures.unidade(
                Path(tmp), unit_type="norma", test='""', approved_at="2026-08-25"
            )
            problemas = lint_unidade.lint(alvo)
            self.assertTrue(any("approved_by" in p for p in problemas), problemas)

    def test_norma_sem_approved_at_recusa(self):
        with tempfile.TemporaryDirectory() as tmp:
            alvo = fixtures.unidade(
                Path(tmp), unit_type="norma", test='""', approved_by="Bortoli"
            )
            problemas = lint_unidade.lint(alvo)
            self.assertTrue(any("approved_at" in p for p in problemas), problemas)

    def test_norma_com_test_preenchido_recusa(self):
        with tempfile.TemporaryDirectory() as tmp:
            alvo = fixtures.unidade(
                Path(tmp),
                unit_type="norma",
                test="caminho/para/test_exemplo.py",
                approved_by="Bortoli",
                approved_at="2026-08-25",
            )
            problemas = lint_unidade.lint(alvo)
            self.assertTrue(any("test" in p for p in problemas), problemas)

    def test_dev_com_test_vazio_recusa(self):
        with tempfile.TemporaryDirectory() as tmp:
            alvo = fixtures.unidade(Path(tmp), unit_type="dev", test='""')
            problemas = lint_unidade.lint(alvo)
            self.assertTrue(any("test" in p for p in problemas), problemas)

    def test_linha_ultimo_resultado_recusa_em_qualquer_unidade(self):
        with tempfile.TemporaryDirectory() as tmp:
            texto = UNIDADE_VALIDA + "\nÚltimo resultado: não executado.\n"
            alvo = Path(tmp) / "unidade.md"
            alvo.write_text(texto, encoding="utf-8")
            problemas = lint_unidade.lint(alvo)
            self.assertTrue(any("Último resultado" in p for p in problemas), problemas)

    def test_onze_unidades_reais_aprovam_depois_da_remocao(self):
        """Prova que a linha saiu de todas as onze — não uma contagem."""
        for numero in range(1, 12):
            candidatos = list(DIR_UNIDADES_REAIS.glob(f"{numero:02d}-*.md"))
            with self.subTest(unidade=numero):
                self.assertEqual(len(candidatos), 1, candidatos)
                self.assertEqual(lint_unidade.lint(candidatos[0]), [])


class TestVerificarUnidadeNorma(unittest.TestCase):
    """O ciclo de `unit_type: norma` em `verificacao.verificar` — sem rodar `subprocess`."""

    def test_com_aprovacao_fecha_verified_sem_executar_e_copia_approved_at(self):
        with tempfile.TemporaryDirectory() as tmp:
            raiz = Path(tmp).resolve()
            unidade = fixtures.unidade(
                raiz,
                unit_type="norma",
                test='""',
                approved_by="Bortoli",
                approved_at="2020-01-01",
            )
            with mock.patch.object(lib, "repo_root", return_value=raiz):
                with mock.patch.object(verificacao.subprocess, "run") as executar:
                    estado, escreveu = verificacao.verificar(unidade)

            executar.assert_not_called()
            self.assertEqual(estado, "verified")
            self.assertTrue(escreveu)
            self.assertEqual(regioes.ler_campo(unidade, "state"), "verified")
            self.assertEqual(regioes.ler_campo(unidade, "verified_at"), "2020-01-01")

    def test_sem_aprovacao_fecha_spec_sem_executar(self):
        with tempfile.TemporaryDirectory() as tmp:
            raiz = Path(tmp).resolve()
            unidade = fixtures.unidade(raiz, unit_type="norma", test='""')

            with mock.patch.object(lib, "repo_root", return_value=raiz):
                with mock.patch.object(verificacao.subprocess, "run") as executar:
                    estado, escreveu = verificacao.verificar(unidade)

            executar.assert_not_called()
            self.assertEqual(estado, "spec")
            self.assertEqual(regioes.ler_campo(unidade, "verified_at"), '""')

    def test_dry_run_nao_escreve(self):
        with tempfile.TemporaryDirectory() as tmp:
            raiz = Path(tmp).resolve()
            unidade = fixtures.unidade(
                raiz,
                unit_type="norma",
                test='""',
                approved_by="Bortoli",
                approved_at="2020-01-01",
            )
            original = unidade.read_text(encoding="utf-8")

            with mock.patch.object(lib, "repo_root", return_value=raiz):
                with mock.patch.object(verificacao.subprocess, "run") as executar:
                    estado, escreveu = verificacao.verificar(unidade, dry_run=True)

            executar.assert_not_called()
            self.assertEqual(estado, "verified")
            self.assertFalse(escreveu)
            self.assertEqual(unidade.read_text(encoding="utf-8"), original)


if __name__ == "__main__":
    unittest.main()
