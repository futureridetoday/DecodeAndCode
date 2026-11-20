#!/usr/bin/env python3
"""Teste declarado da unidade 0001-13 — formato de plano por porte e o `unit_type: norma`.

Três frentes, uma por oráculo que a unidade fecha:

- `lint_plano.lint` — os três portes bem formados devolvem `[]`, cada linha da tabela de portes
  recusa isoladamente (um problema só, nunca mais), `plan_size` ausente ou fora do vocabulário
  entra na lista sem levantar, e o plano real `0001` deste repositório — que é `grande` — aprova.
- `lint_unidade.lint` — aceita `unit_type: norma` **sem** `approved_by`/`approved_at` (é o gate de
  entrada, e a aprovação só existe depois da entrega), recusa `test:` preenchido em `norma` e vazio
  em `dev`, recusa a linha órfã `Último resultado` em qualquer unidade, e as onze unidades reais
  (`01` a `11`) continuam aprovando depois da remoção.
- `verificacao.verificar` — uma unidade `norma` fecha por aprovação, nunca por execução: `verified`
  sem rodar `subprocess` quando `approved_by`/`approved_at` estão preenchidos, `spec` sem qualquer
  um deles, com o campo que falta na saída.
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

    def _sem_linha(self, linha: str) -> list[str]:
        with tempfile.TemporaryDirectory() as tmp:
            dir_plano = fixtures.plano(Path(tmp), plan_size="pequeno", com_backlog=False)
            arquivo = _arquivo(dir_plano)
            texto = arquivo.read_text(encoding="utf-8")
            self.assertIn(linha, texto)
            arquivo.write_text(texto.replace(linha, ""), encoding="utf-8")
            return lint_plano.lint(arquivo)

    def test_plan_id_ausente_entra_como_problema(self):
        problemas = self._sem_linha('plan_id: "0009"\n')
        self.assertEqual(problemas, ["campo obrigatório ausente no frontmatter: plan_id"])

    def test_status_ausente_entra_como_problema(self):
        problemas = self._sem_linha("status: approved\n")
        self.assertEqual(problemas, ["campo obrigatório ausente no frontmatter: status"])

    def test_plan_id_vazio_e_valido_em_rascunho(self):
        with tempfile.TemporaryDirectory() as tmp:
            dir_plano = fixtures.plano(Path(tmp), plan_size="pequeno", com_backlog=False)
            arquivo = _arquivo(dir_plano)
            texto = arquivo.read_text(encoding="utf-8").replace('plan_id: "0009"', 'plan_id: ""')
            arquivo.write_text(texto, encoding="utf-8")
            self.assertEqual(lint_plano.lint(arquivo), [])


class TestPlanoRealDoRepositorio(unittest.TestCase):
    def test_plano_0001_grande_aprova(self):
        """Formato do porte limpo; a falta de `plan_type` é esperada — plano anterior ao 0012 (`D-03`)."""
        self.assertEqual(
            lint_plano.lint(PLANO_REAL_0001),
            ["campo obrigatório ausente no frontmatter: plan_type"],
        )


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

    def test_norma_recem_derivada_sem_aprovacao_aprova_no_gate_de_entrada(self):
        """A aprovação é do humano **depois** da entrega — exigi-la na entrada recusava toda `norma`.

        Medido no AmFlow (plano 0028, plugin 2.0.0): `lint-unidade` reprovava as três unidades
        `norma` recém-derivadas só pela ausência de `approved_by`/`approved_at`, e a `implement`
        encerrava antes de escrever qualquer coisa.
        """
        with tempfile.TemporaryDirectory() as tmp:
            alvo = fixtures.unidade(Path(tmp), unit_type="norma", test='""')
            self.assertEqual(lint_unidade.lint(alvo), [])

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
        """Prova que a linha saiu de todas as onze — não uma contagem.

        Citação de norma fica fora: as unidades `verified` do plano `0001` anteciparam o formato
        que resolve (plano `0006`, D5) e não se reescrevem — `test_lint_unidade` cobre essa checagem.
        """
        for numero in range(1, 12):
            candidatos = list(DIR_UNIDADES_REAIS.glob(f"{numero:02d}-*.md"))
            with self.subTest(unidade=numero):
                self.assertEqual(len(candidatos), 1, candidatos)
                problemas = [
                    p for p in lint_unidade.lint(candidatos[0]) if not p.startswith("norma aplicável")
                ]
                self.assertEqual(problemas, [])


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

    def test_cada_campo_de_aprovacao_ausente_fecha_spec_e_aparece_na_saida(self):
        """A exigência saiu do gate de entrada e mora no de saída — cada campo, isoladamente."""
        casos = {
            "approved_by": {"approved_at": "2020-01-01"},
            "approved_at": {"approved_by": "Bortoli"},
        }
        for ausente, presentes in casos.items():
            with self.subTest(ausente=ausente), tempfile.TemporaryDirectory() as tmp:
                raiz = Path(tmp).resolve()
                unidade = fixtures.unidade(raiz, unit_type="norma", test='""', **presentes)
                with mock.patch.object(lib, "repo_root", return_value=raiz):
                    with mock.patch.object(verificacao.subprocess, "run") as executar:
                        estado, _, saida = verificacao.verificar_com_saida(unidade, dry_run=True)

                executar.assert_not_called()
                self.assertEqual(estado, "spec")
                self.assertIn(ausente, saida)

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


class TestPlanType(unittest.TestCase):
    """`plan_type` (plano 0012): ausente ou fora do vocabulário entra na lista, sem encerrar o resto."""

    def _lint(self, plan_type: str) -> list[str]:
        with tempfile.TemporaryDirectory() as tmp:
            dir_plano = fixtures.plano(
                Path(tmp), plan_size="médio", tarefas=True, plan_type=plan_type
            )
            return lint_plano.lint(_arquivo(dir_plano))

    def test_plan_type_valido_nao_gera_problema(self):
        self.assertEqual(self._lint("fix"), [])

    def test_plan_type_ausente_entra_como_problema(self):
        with tempfile.TemporaryDirectory() as tmp:
            dir_plano = fixtures.plano(Path(tmp), plan_size="médio", tarefas=True)
            arquivo = _arquivo(dir_plano)
            texto = arquivo.read_text(encoding="utf-8").replace("plan_type: feature\n", "")
            arquivo.write_text(texto, encoding="utf-8")
            self.assertEqual(
                lint_plano.lint(arquivo), ["campo obrigatório ausente no frontmatter: plan_type"]
            )

    def test_plan_type_fora_do_vocabulario_nomeia_o_vocabulario(self):
        problemas = self._lint("perf")
        self.assertEqual(len(problemas), 1, problemas)
        self.assertIn("plan_type fora do vocabulário", problemas[0])
        self.assertIn(str(lib.PLAN_TYPES_VALIDOS), problemas[0])

    def test_plan_type_invalido_nao_encerra_as_demais_checagens(self):
        with tempfile.TemporaryDirectory() as tmp:
            dir_plano = fixtures.plano(Path(tmp), plan_size="médio", plan_type="perf")
            problemas = lint_plano.lint(_arquivo(dir_plano))
        self.assertTrue(any("plan_type" in p for p in problemas), problemas)
        self.assertTrue(any("Tarefas" in p for p in problemas), problemas)


if __name__ == "__main__":
    unittest.main()
