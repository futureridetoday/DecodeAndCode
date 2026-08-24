#!/usr/bin/env python3
"""Testes da situação projetada por `backlog.projetar` — unidade 0001-07 (L-18).

O defeito medido em 2026-08-24: ao fechar a 0001-02, `projetar` levou a situação a `concluído`
com quinze unidades ainda por derivar — porque a situação só olhava para o que já existia em
disco, nunca para o total previsto no plano. Esta suíte cobre o critério de aceite: a situação
agora depende do total declarado em `## Escopo`, e nunca projeta `concluído` por não saber contar.
"""

from __future__ import annotations

import sys
import tempfile
import unittest
from datetime import date
from pathlib import Path
from unittest import mock

sys.path.insert(0, str(Path(__file__).resolve().parent))
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import backlog
import fixtures
import lib


class _BaseComPlano(unittest.TestCase):
    """Árvore temporária com `lib.plan_root` mockado — mesmo padrão de test_backlog.py."""

    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self._tmp.cleanup)
        self.raiz = Path(self._tmp.name).resolve()

        patcher = mock.patch.object(lib, "plan_root", return_value=self.raiz)
        patcher.start()
        self.addCleanup(patcher.stop)

    def _montar_plano(self, *, previstas):
        dir_plano = fixtures.plano(self.raiz, core="builder", nome="exemplo", numero="0009", previstas=previstas)
        fixtures.planos_md(self.raiz)
        return dir_plano


class TestPrevistaNaoDerivadaNuncaConclui(_BaseComPlano):
    """O critério de aceite central: falta uma prevista, mesmo com as demais `verified`."""

    def test_uma_prevista_falta_derivar(self):
        dir_plano = self._montar_plano(previstas=2)
        fixtures.unidade(dir_plano, nome="01-a.md", unit_id="0009-01", state="verified")

        _, situacao = backlog.projetar(dir_plano)

        self.assertEqual(situacao, "em desenvolvimento")

    def test_derivadas_a_mais_que_previstas_tambem_nao_conclui(self):
        dir_plano = self._montar_plano(previstas=1)
        fixtures.unidade(dir_plano, nome="01-a.md", unit_id="0009-01", state="verified")
        fixtures.unidade(dir_plano, nome="02-b.md", unit_id="0009-02", state="verified")

        _, situacao = backlog.projetar(dir_plano)

        self.assertEqual(situacao, "em desenvolvimento")


class TestTodasPrevistasDerivadasEVerificadas(_BaseComPlano):
    def test_conclui(self):
        dir_plano = self._montar_plano(previstas=2)
        fixtures.unidade(dir_plano, nome="01-a.md", unit_id="0009-01", state="verified")
        fixtures.unidade(dir_plano, nome="02-b.md", unit_id="0009-02", state="verified")

        _, situacao = backlog.projetar(dir_plano)

        self.assertEqual(situacao, "concluído")

    def test_nao_conclui_se_alguma_nao_verified(self):
        dir_plano = self._montar_plano(previstas=2)
        fixtures.unidade(dir_plano, nome="01-a.md", unit_id="0009-01", state="verified")
        fixtures.unidade(dir_plano, nome="02-b.md", unit_id="0009-02", state="spec")

        _, situacao = backlog.projetar(dir_plano)

        self.assertEqual(situacao, "em desenvolvimento")


class TestEscopoIlegivelNuncaConclui(_BaseComPlano):
    def test_sem_secao_escopo_fica_em_desenvolvimento_mesmo_com_tudo_verified(self):
        dir_plano = self._montar_plano(previstas=None)
        fixtures.unidade(dir_plano, nome="01-a.md", unit_id="0009-01", state="verified")

        backlog_texto, situacao = backlog.projetar(dir_plano)

        self.assertEqual(situacao, "em desenvolvimento")
        self.assertIn("de desconhecido", backlog_texto)


class TestRodapeContaPrevistasDoEscopo(_BaseComPlano):
    def test_rodape_diz_n_de_m_com_m_do_escopo(self):
        dir_plano = self._montar_plano(previstas=5)
        fixtures.unidade(dir_plano, nome="01-a.md", unit_id="0009-01", state="verified")

        backlog_texto, _ = backlog.projetar(dir_plano)

        hoje = date.today().isoformat()
        self.assertIn(f"1 de 5 derivada · 1 verificada · atualizado em {hoje}", backlog_texto)

    def test_rodape_diz_desconhecido_sem_secao_escopo(self):
        dir_plano = self._montar_plano(previstas=None)
        fixtures.unidade(dir_plano, nome="01-a.md", unit_id="0009-01", state="spec")

        backlog_texto, _ = backlog.projetar(dir_plano)

        hoje = date.today().isoformat()
        self.assertIn(f"1 de desconhecido derivada · 0 verificadas · atualizado em {hoje}", backlog_texto)


class TestContaTodasAsTabelasDaSecao(_BaseComPlano):
    """A seção `## Escopo` pode ter mais de uma tabela — todas contam, até o próximo `## `."""

    def test_previstas_soma_linhas_de_tabelas_separadas_por_h3(self):
        dir_plano = self._montar_plano(previstas=None)
        arquivo_do_plano = dir_plano / "0009-exemplo.md"
        texto = arquivo_do_plano.read_text(encoding="utf-8")
        escopo = (
            "\n## Escopo\n\n"
            "### Fase 1\n\n"
            "| # | Unidade | Responsabilidade |\n|---|---|---|\n"
            "| 01 | primeira | sintética |\n"
            "| 02 | segunda | sintética |\n\n"
            "### Correções fora de fase\n\n"
            "| # | Unidade | Responsabilidade |\n|---|---|---|\n"
            "| 03 | terceira | sintética |\n"
        )
        texto = texto.replace("## Backlog", escopo + "\n## Backlog")
        arquivo_do_plano.write_text(texto, encoding="utf-8")

        fixtures.unidade(dir_plano, nome="01-a.md", unit_id="0009-01", state="verified")
        fixtures.unidade(dir_plano, nome="02-b.md", unit_id="0009-02", state="verified")
        fixtures.unidade(dir_plano, nome="03-c.md", unit_id="0009-03", state="verified")

        _, situacao = backlog.projetar(dir_plano)

        self.assertEqual(situacao, "concluído")


if __name__ == "__main__":
    unittest.main()
