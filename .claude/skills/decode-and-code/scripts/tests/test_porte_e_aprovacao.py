#!/usr/bin/env python3
"""Teste declarado da unidade 0001-12 — os três campos de aprovação humana em `scaffold.aprovar`.

`plan_size`, `approved_by` e `approved_at` passam a ser exigidos antes de qualquer escrita — cada
um ausente ou inválido recusa a aprovação isoladamente, sem tocar disco (mesmo cuidado que a
checagem de `core` já tem). Plano já aprovado continua no-op mesmo sem os campos novos — é o caso
do plano `0001` real, e é o que a `_ja_aprovado` (unidade 0001-06) já garante. Árvore inteiramente
temporária, no mesmo padrão de `test_scaffold.py`.
"""

from __future__ import annotations

import sys
import tempfile
import unittest
from datetime import date
from pathlib import Path
from unittest import mock

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import lib
import scaffold

CABECALHO_TABELA = (
    "| # | Plano | Core | Módulo | Origem | Situação | Aprovado |\n"
    "|---|---|---|---|---|---|---|\n"
)

_OMITIR = object()


class _BaseComRaizTemporaria(unittest.TestCase):
    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self._tmp.cleanup)
        self.raiz = Path(self._tmp.name).resolve()

        (self.raiz / "_inbox").mkdir()

        self.planos_md = self.raiz / "_planos.md"
        self.planos_original = f"<!-- planos:start -->\n{CABECALHO_TABELA}<!-- planos:end -->\n"
        self.planos_md.write_text(self.planos_original, encoding="utf-8")

        patcher_plan_root = mock.patch.object(lib, "plan_root", return_value=self.raiz)
        patcher_plan_root.start()
        self.addCleanup(patcher_plan_root.stop)

        patcher_repo_root = mock.patch.object(scaffold.move_md, "REPO_ROOT", self.raiz)
        patcher_repo_root.start()
        self.addCleanup(patcher_repo_root.stop)

    def _escrever_plano(self, nome: str = "plano-exemplo", **overrides) -> Path:
        """Plano no `_inbox` com os três campos válidos por default.

        `overrides[campo] = _OMITIR` remove a linha inteira do frontmatter — para testar
        ausência, distinta de campo presente e vazio.
        """
        campos = {
            "plan_id": '""',
            "core": "builder",
            "module": "plano-exemplo",
            "block": '""',
            "status": "draft",
            "plan_size": "pequeno",
            "approved_by": "Bortoli",
            "approved_at": "2026-08-20",
        }
        campos.update(overrides)
        linhas = "\n".join(
            f"{chave}: {valor}" for chave, valor in campos.items() if valor is not _OMITIR
        )
        plano = self.raiz / "_inbox" / f"{nome}.md"
        plano.write_text(f"---\n{linhas}\n---\n\n# {nome}\n", encoding="utf-8")
        return plano

    def _assert_recusa_sem_escrever(
        self, plano: Path, campo_esperado: str, dry_run: bool = False
    ) -> None:
        conteudo_antes = plano.read_bytes()
        planos_md_antes = self.planos_md.read_bytes()

        with self.assertRaisesRegex(ValueError, campo_esperado):
            scaffold.aprovar(plano, dry_run=dry_run)

        self.assertEqual(plano.read_bytes(), conteudo_antes)
        self.assertEqual(self.planos_md.read_bytes(), planos_md_antes)


class TestCamposDeAprovacaoAusentesOuInvalidos(_BaseComRaizTemporaria):
    def test_plan_size_ausente(self):
        plano = self._escrever_plano(plan_size=_OMITIR)
        self._assert_recusa_sem_escrever(plano, "plan_size")

    def test_plan_size_vazio(self):
        plano = self._escrever_plano(plan_size='""')
        self._assert_recusa_sem_escrever(plano, "plan_size")

    def test_plan_size_fora_do_vocabulario(self):
        plano = self._escrever_plano(plan_size="enorme")
        self._assert_recusa_sem_escrever(plano, "plan_size")

    def test_approved_by_ausente(self):
        plano = self._escrever_plano(approved_by=_OMITIR)
        self._assert_recusa_sem_escrever(plano, "approved_by")

    def test_approved_at_ausente(self):
        plano = self._escrever_plano(approved_at=_OMITIR)
        self._assert_recusa_sem_escrever(plano, "approved_at")

    def test_approved_at_nao_e_data_iso(self):
        plano = self._escrever_plano(approved_at="25/08/2026")
        self._assert_recusa_sem_escrever(plano, "approved_at")

    def test_dry_run_tambem_recusa_antes_de_escrever(self):
        """O ramo que a unidade, o docstring de `aprovar` e a norma afirmam, e que nenhum caso cobria.

        `approved_at` é a **última** das checagens novas, imediatamente antes do retorno de
        `dry_run`: se ela recusa aqui, as anteriores recusam também. Escrito na revisão de
        2026-08-25 — a afirmação existia em três lugares e em teste nenhum (`H-09`).
        """
        plano = self._escrever_plano(approved_at="25/08/2026")
        self._assert_recusa_sem_escrever(plano, "approved_at", dry_run=True)


class TestAprovarComCamposValidos(_BaseComRaizTemporaria):
    def test_planos_md_recebe_approved_at_declarado_nao_a_data_de_hoje(self):
        plano = self._escrever_plano(approved_at="2020-01-01")

        alvo = scaffold.aprovar(plano)

        self.assertTrue(alvo.is_file())
        conteudo_planos_md = self.planos_md.read_text(encoding="utf-8")
        self.assertIn("2020-01-01", conteudo_planos_md)
        self.assertNotIn(date.today().isoformat(), conteudo_planos_md)


class TestPlanoJaAprovadoIgnoraCamposNovos(_BaseComRaizTemporaria):
    def test_plano_ja_aprovado_sem_campos_novos_e_no_op(self):
        plano = self.raiz / "builder" / "0002-plano-exemplo" / "0002-plano-exemplo.md"
        plano.parent.mkdir(parents=True)
        plano.write_text(
            "---\n"
            'plan_id: "0002"\n'
            "core: builder\n"
            "module: plano-exemplo\n"
            'block: ""\n'
            "status: approved\n"
            "---\n\n"
            "# plano-exemplo\n",
            encoding="utf-8",
        )
        conteudo_antes = plano.read_bytes()

        alvo = scaffold.aprovar(plano)

        self.assertEqual(alvo, plano.resolve())
        self.assertEqual(plano.read_bytes(), conteudo_antes)


if __name__ == "__main__":
    unittest.main()
