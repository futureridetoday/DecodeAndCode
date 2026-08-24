#!/usr/bin/env python3
"""Testes da projeção de backlog e de situação — unidade 0002-09.

O critério de aceite é a idempotência: projetar duas vezes seguidas, sem mudar unidade nenhuma,
produz arquivos idênticos, e o texto fora dos marcadores permanece intacto — `TestIdempotencia`
cobre exatamente isso. As demais classes cobrem cada passo da Sequência: ordenação por `unit_id`
(não pela ordem do sistema de arquivos), unidade sem título como problema visível — não exceção —,
situação derivada, e os dois erros declarados no Contrato.

Árvore inteiramente temporária, como em test_scaffold.py: `lib.plan_root` é o único ponto mockado,
e `lib.planos_md()` resolve a partir dele porque as duas funções vivem no mesmo módulo `lib`.
"""

from __future__ import annotations

import os
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

CABECALHO_PLANOS = "| # | Plano | Core | Módulo | Origem | Situação | Aprovado |\n|---|---|---|---|---|---|---|\n"

PLANO = """\
---
name: exemplo
type: plan
project: AmFlow
plan_id: "0009"
core: builder
module: exemplo
block: ""
status: approved
---

# 0009 — Plano sintético

Texto antes do backlog — precisa sobreviver à projeção.

## Backlog

<!-- backlog:start -->
conteúdo antigo, será substituído
<!-- backlog:end -->

Texto depois do backlog — também precisa sobreviver.
"""

UNIDADE = """\
---
name: exemplo-{unit_id}
type: unit
project: AmFlow
core: builder
module: exemplo
unit_id: {unit_id}
state: {state}
test: tests/test_exemplo.py
---

# {unit_id} — {titulo}

**Responsabilidade:** existir só para o teste do backlog.
"""

UNIDADE_SEM_TITULO = """\
---
name: exemplo-{unit_id}
type: unit
project: AmFlow
core: builder
module: exemplo
unit_id: {unit_id}
state: {state}
test: tests/test_exemplo.py
---

## Responsabilidade

Corpo sem H1 nenhum — parágrafo comum.
"""


class _BaseComPlano(unittest.TestCase):
    """Monta `raiz/builder/0009-exemplo/0009-exemplo.md` e `raiz/_planos.md` com a linha do plano."""

    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self._tmp.cleanup)
        self.raiz = Path(self._tmp.name).resolve()

        self.dir_plano = self.raiz / "builder" / "0009-exemplo"
        self.dir_plano.mkdir(parents=True)
        self.arquivo_plano = self.dir_plano / "0009-exemplo.md"
        self.arquivo_plano.write_text(PLANO, encoding="utf-8")

        self.planos_md = self.raiz / "_planos.md"
        self.planos_original = (
            "<!-- planos:start -->\n"
            f"{CABECALHO_PLANOS}"
            "| 0001 | [outro](hub/0001-outro/0001-outro.md) | hub | outro | — | concluído | 2026-07-01 |\n"
            "| 0009 | [exemplo](builder/0009-exemplo/0009-exemplo.md) | builder | exemplo | 0002-03"
            " | em desenvolvimento | 2026-07-20 |\n"
            "<!-- planos:end -->\n"
        )
        self.planos_md.write_text(self.planos_original, encoding="utf-8")

        patcher = mock.patch.object(lib, "plan_root", return_value=self.raiz)
        patcher.start()
        self.addCleanup(patcher.stop)

    def _escrever_unidade(self, nome_arquivo, unit_id, state, titulo="Título de exemplo", template=UNIDADE):
        (self.dir_plano / nome_arquivo).write_text(
            template.format(unit_id=unit_id, state=state, titulo=titulo), encoding="utf-8"
        )


class TestProjetarCaminhoFeliz(_BaseComPlano):
    def setUp(self):
        super().setUp()
        self._escrever_unidade("01-a.md", "0009-01", "verified", "Primeira unidade")
        self._escrever_unidade("02-b.md", "0009-02", "spec", "Segunda unidade")

    def test_backlog_devolvido_tem_as_duas_linhas_ordenadas(self):
        backlog_texto, _ = backlog.projetar(self.dir_plano)
        self.assertIn("| [0009-01](01-a.md) | Primeira unidade | `verified` |", backlog_texto)
        self.assertIn("| [0009-02](02-b.md) | Segunda unidade | `spec` |", backlog_texto)
        self.assertLess(
            backlog_texto.index("0009-01"), backlog_texto.index("0009-02"), "01 deve vir antes de 02"
        )

    def test_rodape_conta_derivadas_e_verificadas(self):
        backlog_texto, _ = backlog.projetar(self.dir_plano)
        hoje = date.today().isoformat()
        self.assertIn(f"2 de 2 derivadas · 1 verificada · atualizado em {hoje}", backlog_texto)

    def test_situacao_em_desenvolvimento_com_unidade_fora_de_verified(self):
        _, situacao = backlog.projetar(self.dir_plano)
        self.assertEqual(situacao, "em desenvolvimento")

    def test_grava_o_backlog_no_arquivo_do_plano(self):
        backlog.projetar(self.dir_plano)
        conteudo = self.arquivo_plano.read_text(encoding="utf-8")
        self.assertIn("| [0009-01](01-a.md) | Primeira unidade | `verified` |", conteudo)
        self.assertNotIn("conteúdo antigo", conteudo)

    def test_texto_fora_dos_marcadores_permanece_intacto(self):
        backlog.projetar(self.dir_plano)
        conteudo = self.arquivo_plano.read_text(encoding="utf-8")
        self.assertIn("Texto antes do backlog — precisa sobreviver à projeção.", conteudo)
        self.assertIn("Texto depois do backlog — também precisa sobreviver.", conteudo)

    def test_planos_md_ganha_situacao_em_desenvolvimento(self):
        backlog.projetar(self.dir_plano)
        conteudo = self.planos_md.read_text(encoding="utf-8")
        self.assertIn(
            "| 0009 | [exemplo](builder/0009-exemplo/0009-exemplo.md) | builder | exemplo | 0002-03"
            " | em desenvolvimento | 2026-07-20 |",
            conteudo,
        )

    def test_planos_md_preserva_linha_de_outro_plano(self):
        backlog.projetar(self.dir_plano)
        conteudo = self.planos_md.read_text(encoding="utf-8")
        self.assertIn("| 0001 | [outro](hub/0001-outro/0001-outro.md) | hub | outro | — | concluído | 2026-07-01 |", conteudo)


class TestSituacaoConcluida(_BaseComPlano):
    def setUp(self):
        super().setUp()
        self._escrever_unidade("01-a.md", "0009-01", "verified", "Primeira unidade")
        self._escrever_unidade("02-b.md", "0009-02", "verified", "Segunda unidade")

    def test_situacao_concluido_com_todas_verified(self):
        _, situacao = backlog.projetar(self.dir_plano)
        self.assertEqual(situacao, "concluído")

    def test_planos_md_ganha_situacao_concluido(self):
        backlog.projetar(self.dir_plano)
        conteudo = self.planos_md.read_text(encoding="utf-8")
        self.assertIn(
            "| 0009 | [exemplo](builder/0009-exemplo/0009-exemplo.md) | builder | exemplo | 0002-03"
            " | concluído | 2026-07-20 |",
            conteudo,
        )


class TestNenhumaUnidadeDerivada(_BaseComPlano):
    def test_situacao_nunca_concluido_com_lista_vazia(self):
        _, situacao = backlog.projetar(self.dir_plano)
        self.assertEqual(situacao, "em desenvolvimento")

    def test_rodape_zero_a_zero(self):
        backlog_texto, _ = backlog.projetar(self.dir_plano)
        hoje = date.today().isoformat()
        self.assertIn(f"0 de 0 derivadas · 0 verificadas · atualizado em {hoje}", backlog_texto)

    def test_tabela_so_com_cabecalho(self):
        backlog_texto, _ = backlog.projetar(self.dir_plano)
        self.assertIn("| Unidade | Título | Estado |\n|---|---|---|\n\n", backlog_texto)


class TestUnidadeSemTitulo(_BaseComPlano):
    def setUp(self):
        super().setUp()
        self._escrever_unidade("01-a.md", "0009-01", "spec", template=UNIDADE_SEM_TITULO)

    def test_entra_como_problema_visivel_sem_levantar(self):
        backlog_texto, _ = backlog.projetar(self.dir_plano)
        self.assertIn("| [0009-01](01-a.md) | (sem título) | `spec` |", backlog_texto)


class TestOrdenaPorUnitIdNaoPorArquivo(_BaseComPlano):
    """Nomes de arquivo em ordem inversa à ordem correta de `unit_id` — só a leitura do campo decide."""

    def setUp(self):
        super().setUp()
        self._escrever_unidade("01-terceira.md", "0009-03", "spec", "Terceira")
        self._escrever_unidade("02-primeira.md", "0009-01", "spec", "Primeira")
        self._escrever_unidade("03-segunda.md", "0009-02", "spec", "Segunda")

    def test_ordem_da_tabela_segue_unit_id(self):
        backlog_texto, _ = backlog.projetar(self.dir_plano)
        p1 = backlog_texto.index("0009-01")
        p2 = backlog_texto.index("0009-02")
        p3 = backlog_texto.index("0009-03")
        self.assertLess(p1, p2)
        self.assertLess(p2, p3)


class TestIgnoraArquivoDoProprioPlano(unittest.TestCase):
    """Diretório de plano com prefixo de 2 dígitos — caso em que o nome colidiria com `NN-*.md`."""

    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self._tmp.cleanup)
        self.raiz = Path(self._tmp.name).resolve()

        self.dir_plano = self.raiz / "builder" / "09-exemplo"
        self.dir_plano.mkdir(parents=True)
        self.arquivo_plano = self.dir_plano / "09-exemplo.md"
        self.arquivo_plano.write_text(PLANO, encoding="utf-8")
        (self.dir_plano / "01-a.md").write_text(
            UNIDADE.format(unit_id="0009-01", state="spec", titulo="Única unidade"), encoding="utf-8"
        )

        self.planos_md = self.raiz / "_planos.md"
        self.planos_md.write_text(
            "<!-- planos:start -->\n"
            f"{CABECALHO_PLANOS}"
            "| 0009 | [exemplo](builder/09-exemplo/09-exemplo.md) | builder | exemplo | — | em desenvolvimento | 2026-07-20 |\n"
            "<!-- planos:end -->\n",
            encoding="utf-8",
        )

        patcher = mock.patch.object(lib, "plan_root", return_value=self.raiz)
        patcher.start()
        self.addCleanup(patcher.stop)

    def test_arquivo_do_plano_nao_vira_linha_da_tabela(self):
        backlog_texto, _ = backlog.projetar(self.dir_plano)
        self.assertNotIn("09-exemplo.md)", backlog_texto)
        self.assertIn("01-a.md", backlog_texto)


class TestIdempotencia(_BaseComPlano):
    """O critério de aceite da unidade."""

    def setUp(self):
        super().setUp()
        self._escrever_unidade("01-a.md", "0009-01", "verified", "Primeira unidade")
        self._escrever_unidade("02-b.md", "0009-02", "spec", "Segunda unidade")

    def test_segunda_projecao_produz_arquivos_identicos(self):
        backlog.projetar(self.dir_plano)
        plano_apos_primeira = self.arquivo_plano.read_text(encoding="utf-8")
        planos_apos_primeira = self.planos_md.read_text(encoding="utf-8")

        backlog.projetar(self.dir_plano)
        plano_apos_segunda = self.arquivo_plano.read_text(encoding="utf-8")
        planos_apos_segunda = self.planos_md.read_text(encoding="utf-8")

        self.assertEqual(plano_apos_primeira, plano_apos_segunda)
        self.assertEqual(planos_apos_primeira, planos_apos_segunda)

    def test_texto_fora_dos_marcadores_nunca_muda(self):
        original = self.arquivo_plano.read_text(encoding="utf-8")
        prosa_antes = original.split("<!-- backlog:start -->")[0]
        prosa_depois = original.split("<!-- backlog:end -->")[1]

        backlog.projetar(self.dir_plano)
        backlog.projetar(self.dir_plano)

        conteudo = self.arquivo_plano.read_text(encoding="utf-8")
        self.assertTrue(conteudo.startswith(prosa_antes))
        self.assertTrue(conteudo.endswith(prosa_depois))


class TestDryRun(_BaseComPlano):
    def setUp(self):
        super().setUp()
        self._escrever_unidade("01-a.md", "0009-01", "verified", "Primeira unidade")

    def test_nao_escreve_em_nenhum_dos_dois_arquivos(self):
        backlog_texto, situacao = backlog.projetar(self.dir_plano, dry_run=True)

        self.assertIn("0009-01", backlog_texto)
        self.assertEqual(situacao, "concluído")
        self.assertEqual(self.arquivo_plano.read_text(encoding="utf-8"), PLANO)
        self.assertEqual(self.planos_md.read_text(encoding="utf-8"), self.planos_original)


class TestErros(_BaseComPlano):
    def test_sem_marcadores_de_backlog_levanta_value_error_sem_escrever(self):
        self.arquivo_plano.write_text("---\nname: sem-marcadores\n---\n\n# sem marcadores\n", encoding="utf-8")

        with self.assertRaises(ValueError):
            backlog.projetar(self.dir_plano)

        self.assertEqual(self.planos_md.read_text(encoding="utf-8"), self.planos_original)

    def test_sem_linha_em_planos_md_levanta_value_error_sem_escrever(self):
        self.planos_md.write_text(
            f"<!-- planos:start -->\n{CABECALHO_PLANOS}<!-- planos:end -->\n", encoding="utf-8"
        )
        original_plano = self.arquivo_plano.read_text(encoding="utf-8")

        with self.assertRaises(ValueError):
            backlog.projetar(self.dir_plano)

        self.assertEqual(self.arquivo_plano.read_text(encoding="utf-8"), original_plano)


if __name__ == "__main__":
    unittest.main()


class TestCaminhoRelativo(unittest.TestCase):
    """Caminho relativo funciona igual ao absoluto.

    Antes de 2026-07-26, passar relativo levantava ValueError obscuro em
    relative_to, porque lib.plan_root() vem resolvido e o argumento não. É a
    terceira aparição do mesmo padrão no plano — depois do symlink no move-md e
    da resolução que a unidade 0002-01 fixou.
    """

    def test_relativo_e_absoluto_produzem_o_mesmo(self):
        with tempfile.TemporaryDirectory() as tmp:
            raiz = Path(tmp).resolve()
            dir_plano = fixtures.plano(raiz, core="builder", nome="exemplo", numero="0009")
            fixtures.unidade(dir_plano, unit_id="0009-01")
            fixtures.planos_md(
                raiz,
                linhas=[
                    "| 0009 | [exemplo](builder/0009-exemplo/0009-exemplo.md) | builder"
                    " | exemplo | — | em desenvolvimento | 2026-08-24 |\n"
                ],
            )

            with mock.patch.object(lib, "plan_root", return_value=raiz):
                alvo = "builder/0009-exemplo"
                anterior = Path.cwd()
                os.chdir(raiz)
                try:
                    por_relativo = backlog.projetar(Path(alvo), dry_run=True)
                    por_absoluto = backlog.projetar(raiz / alvo, dry_run=True)
                finally:
                    os.chdir(anterior)
        self.assertEqual(por_relativo, por_absoluto)
