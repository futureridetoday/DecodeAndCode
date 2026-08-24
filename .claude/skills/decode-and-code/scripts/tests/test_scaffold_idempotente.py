#!/usr/bin/env python3
"""Teste declarado da unidade 0001-06 — `scaffold._ja_aprovado` / `aprovar` idempotente.

O mecanismo já existe em `de4fc57`, corrigido fora de unidade por decisão do humano (`L-17`): esta
unidade fecha a dívida de teste que a correção abriu, sem reescrever o mecanismo. Fixtures em
`tempfile.TemporaryDirectory()`, como em `test_scaffold.py` — nenhum teste toca o plano real do
repositório.
"""

from __future__ import annotations

import sys
import tempfile
import unittest
from pathlib import Path
from unittest import mock

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import lib
import scaffold

CABECALHO_TABELA = (
    "| # | Plano | Core | Módulo | Origem | Situação | Aprovado |\n"
    "|---|---|---|---|---|---|---|\n"
)


class _BaseComRaizTemporaria(unittest.TestCase):
    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self._tmp.cleanup)
        self.raiz = Path(self._tmp.name).resolve()

        (self.raiz / "_inbox").mkdir()
        (self.raiz / "system").mkdir()
        (self.raiz / "system" / "norma.md").write_text("# norma\n", encoding="utf-8")

        self.planos_md = self.raiz / "_planos.md"
        self.planos_md.write_text(
            "<!-- planos:start -->\n"
            f"{CABECALHO_TABELA}"
            "| 0001 | [outro](builder/0001-outro/0001-outro.md) | builder | outro"
            " | — | em desenvolvimento | 2026-07-01 |\n"
            "<!-- planos:end -->\n",
            encoding="utf-8",
        )

        patcher_plan_root = mock.patch.object(lib, "plan_root", return_value=self.raiz)
        patcher_plan_root.start()
        self.addCleanup(patcher_plan_root.stop)

        patcher_repo_root = mock.patch.object(scaffold.move_md, "REPO_ROOT", self.raiz)
        patcher_repo_root.start()
        self.addCleanup(patcher_repo_root.stop)


class TestAprovarJaAprovadoNaoEscreve(_BaseComRaizTemporaria):
    def setUp(self):
        super().setUp()
        self.plano = self.raiz / "builder" / "0002-evolucao-tools" / "0002-evolucao-tools.md"
        self.plano.parent.mkdir(parents=True)
        self.plano.write_text(
            "---\n"
            'plan_id: "0002"\n'
            "core: builder\n"
            "module: evolucao-tools\n"
            'block: ""\n'
            "status: approved\n"
            "---\n\n"
            "# evolucao-tools\n",
            encoding="utf-8",
        )

    def test_devolve_o_proprio_caminho_resolvido(self):
        alvo = scaffold.aprovar(self.plano)
        self.assertEqual(alvo, self.plano.resolve())

    def test_nao_escreve_nada_plano_e_planos_md_byte_identicos(self):
        conteudo_plano_antes = self.plano.read_bytes()
        conteudo_planos_md_antes = self.planos_md.read_bytes()

        scaffold.aprovar(self.plano)

        self.assertEqual(self.plano.read_bytes(), conteudo_plano_antes)
        self.assertEqual(self.planos_md.read_bytes(), conteudo_planos_md_antes)


class TestAprovarSemPlanIdNaoEhNoOp(_BaseComRaizTemporaria):
    """O outro lado da guarda: fora do `_inbox`, mas sem `plan_id` — não é tratado como aprovado."""

    def setUp(self):
        super().setUp()
        # Estado malformado: já fora do _inbox (como um plano aprovado), mas sem
        # plan_id atribuído. A guarda não pode engolir isso como no-op — precisa
        # seguir o caminho normal, que morre em nomenclatura.validar_nome porque o
        # stem já carrega o prefixo numérico (mesmo motivo do bug corrigido em
        # de4fc57).
        self.plano = self.raiz / "builder" / "0002-evolucao-tools" / "0002-evolucao-tools.md"
        self.plano.parent.mkdir(parents=True)
        self.plano.write_text(
            "---\n"
            'plan_id: ""\n'
            "core: builder\n"
            "module: evolucao-tools\n"
            'block: ""\n'
            "status: draft\n"
            "---\n\n"
            "# evolucao-tools\n",
            encoding="utf-8",
        )

    def test_nao_e_no_op_e_segue_caminho_normal_ate_o_erro_de_nome(self):
        with self.assertRaises(ValueError):
            scaffold.aprovar(self.plano)

    def test_erro_do_caminho_normal_nao_escreve_nada(self):
        conteudo_plano_antes = self.plano.read_bytes()
        conteudo_planos_md_antes = self.planos_md.read_bytes()

        with self.assertRaises(ValueError):
            scaffold.aprovar(self.plano)

        self.assertEqual(self.plano.read_bytes(), conteudo_plano_antes)
        self.assertEqual(self.planos_md.read_bytes(), conteudo_planos_md_antes)


if __name__ == "__main__":
    unittest.main()
