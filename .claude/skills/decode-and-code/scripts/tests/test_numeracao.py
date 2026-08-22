#!/usr/bin/env python3
"""Testes de numeração de plano e de unidade — unidade 0002-04.

`proximo_plano` é testado contra uma cópia de `_planos.md` real, para exercitar
a instância que existe em vez de uma fabricada. Mas **nenhuma expectativa é
fixada**: o arquivo é vivo, e todo plano aprovado move a resposta. A primeira
versão destes testes afirmava `"0003"` e ficou vermelha no dia em que o plano
0003 foi derivado — o valor era consequência do estado do repositório, não do
comportamento sob teste. Aqui a expectativa é derivada da região, e a
propriedade de ler por região (e não o arquivo inteiro) é provada por
invariância: injeta-se número fora dos marcadores e exige-se que a resposta não
se mova. `proxima_unidade` usa uma árvore inteiramente temporária, como em
test_nomenclatura.py.
"""

from __future__ import annotations

import shutil
import sys
import tempfile
import unittest
from pathlib import Path
from unittest import mock

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import lib
import numeracao
import regioes

CABECALHO_TABELA = (
    "| # | Plano | Core | Módulo | Origem | Situação | Aprovado |\n"
    "|---|---|---|---|---|---|---|\n"
)


class TestProximoPlano(unittest.TestCase):
    """Contra uma cópia de docs/plan/_planos.md — instância real."""

    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self._tmp.cleanup)
        self.copia = Path(self._tmp.name) / "_planos.md"
        shutil.copy(lib.planos_md(), self.copia)

        patcher = mock.patch.object(lib, "planos_md", return_value=self.copia)
        patcher.start()
        self.addCleanup(patcher.stop)

    def test_sucede_o_maior_numero_registrado_na_regiao(self):
        # Critério de aceite da unidade. A expectativa é derivada da própria
        # região, nunca fixada: `_planos.md` é vivo e todo plano aprovado move
        # a resposta. Fixar "0003" apodreceu no derive do plano 0003.
        miolo = regioes.ler_regiao(self.copia, "planos")
        numeros = numeracao._numeros_de_planos(miolo)
        if not numeros:
            # Repositório recém-criado — `TestProximoPlanoTabelaVazia` cobre
            # esse caso com fixture. Sem o guard, `max([])` levantaria aqui.
            self.skipTest("nenhum plano registrado ainda")
        esperado = str(max(numeros) + 1).zfill(numeracao.LARGURA_PLANO)
        self.assertEqual(numeracao.proximo_plano(), esperado)

    def test_numero_fora_dos_marcadores_nao_influencia(self):
        # A propriedade que importa é a invariância, não o valor: injeta uma
        # linha de tabela plausível FORA da região e exige que a resposta não
        # se mova. Lendo o arquivo inteiro, 9000 venceria.
        antes = numeracao.proximo_plano()
        with self.copia.open("a", encoding="utf-8") as arquivo:
            arquivo.write("\n| 9000 | isca fora da região | hub | x | — | concluído | 2026-01-01 |\n")
        self.assertEqual(numeracao.proximo_plano(), antes)


class TestProximoPlanoTabelaVazia(unittest.TestCase):
    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self._tmp.cleanup)
        self.copia = Path(self._tmp.name) / "_planos.md"
        self.copia.write_text(
            f"<!-- planos:start -->\n{CABECALHO_TABELA}<!-- planos:end -->\n",
            encoding="utf-8",
        )
        patcher = mock.patch.object(lib, "planos_md", return_value=self.copia)
        patcher.start()
        self.addCleanup(patcher.stop)

    def test_tabela_vazia_comeca_em_0001(self):
        self.assertEqual(numeracao.proximo_plano(), "0001")


class TestProximoPlanoErros(unittest.TestCase):
    def test_sem_regiao_planos_levanta_value_error(self):
        with tempfile.TemporaryDirectory() as tmp:
            copia = Path(tmp) / "_planos.md"
            copia.write_text("# Documento sem marcador nenhum\n", encoding="utf-8")
            with mock.patch.object(lib, "planos_md", return_value=copia):
                with self.assertRaises(ValueError):
                    numeracao.proximo_plano()

    def test_estouro_de_quatro_digitos_levanta_runtime_error(self):
        with tempfile.TemporaryDirectory() as tmp:
            copia = Path(tmp) / "_planos.md"
            copia.write_text(
                "<!-- planos:start -->\n"
                f"{CABECALHO_TABELA}"
                "| 9999 | x | hub | x | — | concluído | 2026-01-01 |\n"
                "<!-- planos:end -->\n",
                encoding="utf-8",
            )
            with mock.patch.object(lib, "planos_md", return_value=copia):
                with self.assertRaises(RuntimeError):
                    numeracao.proximo_plano()


class TestProximaUnidade(unittest.TestCase):
    """Árvore inteiramente temporária, como em test_nomenclatura.py."""

    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self._tmp.cleanup)
        self.dir_plano = Path(self._tmp.name) / "0002-dev-units"
        self.dir_plano.mkdir()

    def _tocar(self, *nomes: str) -> None:
        for nome in nomes:
            (self.dir_plano / nome).write_text("x", encoding="utf-8")

    def test_diretorio_so_com_arquivo_do_plano_comeca_em_01(self):
        self._tocar("0002-dev-units.md")
        self.assertEqual(numeracao.proxima_unidade(self.dir_plano), "01")

    def test_ignora_arquivo_do_proprio_plano_no_maximo(self):
        self._tocar("0002-dev-units.md", "01-lib-base.md", "02-regioes.md")
        self.assertEqual(numeracao.proxima_unidade(self.dir_plano), "03")

    def test_ignora_subdiretorio_mesmo_com_nome_no_padrao(self):
        self._tocar("0002-dev-units.md", "01-lib-base.md")
        (self.dir_plano / "02-pasta-nao-arquivo.md").mkdir()
        self.assertEqual(numeracao.proxima_unidade(self.dir_plano), "02")

    def test_estouro_de_dois_digitos_levanta_runtime_error(self):
        self._tocar("0002-dev-units.md", "99-ultima.md")
        with self.assertRaises(RuntimeError):
            numeracao.proxima_unidade(self.dir_plano)


if __name__ == "__main__":
    unittest.main()
