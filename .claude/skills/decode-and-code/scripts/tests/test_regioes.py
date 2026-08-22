#!/usr/bin/env python3
"""Testes do módulo de regiões delimitadas — unidade 0002-02.

O que dá valor à unidade é a preservação: copiar um documento real para
diretório temporário, escrever um campo ou uma região, e comprovar que todo
o resto do arquivo permanece byte a byte idêntico. Cobre também os dois
casos de recusa (campo ausente, marcador sem par) e a escrita idempotente.

As cópias usam `lib.repo_root()` para achar os fixtures reais — nunca
tocando os arquivos originais do repositório.
"""

from __future__ import annotations

import shutil
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import lib
import regioes


class TestCampoFrontmatter(unittest.TestCase):
    """Contra uma cópia de docs/plan/hub/0001-mcp/01-handler-auth.md — instância real."""

    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self._tmp.cleanup)
        origem = lib.plan_root() / "hub" / "0001-mcp" / "01-handler-auth.md"
        self.copia = Path(self._tmp.name) / "01-handler-auth.md"
        shutil.copy(origem, self.copia)
        self.original = origem.read_text(encoding="utf-8")

    def test_le_campo_existente(self):
        self.assertEqual(regioes.ler_campo(self.copia, "state"), "verified")

    def test_le_campo_ausente_devolve_none(self):
        self.assertIsNone(regioes.ler_campo(self.copia, "campo_inexistente"))

    def test_escrever_campo_muda_so_a_propria_linha(self):
        alterou = regioes.escrever_campos(self.copia, {"state": "wip"})
        self.assertTrue(alterou)

        linhas_originais = self.original.splitlines(keepends=True)
        linhas_novas = self.copia.read_text(encoding="utf-8").splitlines(keepends=True)
        self.assertEqual(len(linhas_originais), len(linhas_novas))

        diferentes = [
            i
            for i, (antiga, nova) in enumerate(zip(linhas_originais, linhas_novas))
            if antiga != nova
        ]
        self.assertEqual(len(diferentes), 1, f"mais de uma linha mudou: {diferentes}")

        i = diferentes[0]
        self.assertEqual(linhas_originais[i], "state: verified\n")
        self.assertEqual(linhas_novas[i], "state: wip\n")

    def test_escrita_idempotente_devolve_false(self):
        alterou = regioes.escrever_campos(self.copia, {"state": "verified"})
        self.assertFalse(alterou)
        self.assertEqual(self.copia.read_text(encoding="utf-8"), self.original)

    def test_campo_ausente_levanta_value_error_sem_gravar(self):
        with self.assertRaises(ValueError):
            regioes.escrever_campos(self.copia, {"campo_inexistente": "x"})
        self.assertEqual(self.copia.read_text(encoding="utf-8"), self.original)

    def test_multiplos_campos_em_uma_chamada(self):
        alterou = regioes.escrever_campos(
            self.copia, {"state": "wip", "verified_at": "2026-07-24"}
        )
        self.assertTrue(alterou)
        self.assertEqual(regioes.ler_campo(self.copia, "state"), "wip")
        self.assertEqual(regioes.ler_campo(self.copia, "verified_at"), "2026-07-24")


class TestFrontmatterMalformado(unittest.TestCase):
    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self._tmp.cleanup)
        self.dir = Path(self._tmp.name)

    def test_sem_abertura_levanta_value_error(self):
        alvo = self.dir / "sem-frontmatter.md"
        alvo.write_text("# Só um título\n\nSem frontmatter nenhum.\n", encoding="utf-8")
        with self.assertRaises(ValueError):
            regioes.ler_campo(alvo, "state")

    def test_sem_fechamento_levanta_value_error(self):
        alvo = self.dir / "frontmatter-quebrado.md"
        alvo.write_text("---\nname: x\n\n# Corpo\n", encoding="utf-8")
        with self.assertRaises(ValueError):
            regioes.ler_campo(alvo, "name")


class TestRegiaoMarcadores(unittest.TestCase):
    """Contra uma cópia de docs/plan/_planos.md — instância real com marcadores."""

    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self._tmp.cleanup)
        origem = lib.planos_md()
        self.copia = Path(self._tmp.name) / "_planos.md"
        shutil.copy(origem, self.copia)
        self.original = origem.read_text(encoding="utf-8")

    def test_le_regiao_existente(self):
        miolo = regioes.ler_regiao(self.copia, "planos")
        self.assertIn("0001", miolo)
        self.assertIn("mcp", miolo)

    def test_le_regiao_inexistente_devolve_none(self):
        self.assertIsNone(regioes.ler_regiao(self.copia, "nao-existe"))

    def test_escrever_regiao_preserva_marcadores_e_resto(self):
        novo_miolo = (
            "\n| # | Plano | Core | Módulo | Origem | Situação | Aprovado |\n"
            "|---|---|---|---|---|---|---|\n"
        )
        alterou = regioes.escrever_regiao(self.copia, "planos", novo_miolo)
        self.assertTrue(alterou)

        texto_novo = self.copia.read_text(encoding="utf-8")
        self.assertIn("<!-- planos:start -->", texto_novo)
        self.assertIn("<!-- planos:end -->", texto_novo)

        antes_original, _, resto_original = self.original.partition(
            "<!-- planos:start -->"
        )
        _, _, depois_original = resto_original.partition("<!-- planos:end -->")

        antes_novo, _, resto_novo = texto_novo.partition("<!-- planos:start -->")
        _, _, depois_novo = resto_novo.partition("<!-- planos:end -->")

        self.assertEqual(antes_original, antes_novo)
        self.assertEqual(depois_original, depois_novo)

    def test_escrita_idempotente_devolve_false(self):
        miolo_atual = regioes.ler_regiao(self.copia, "planos")
        alterou = regioes.escrever_regiao(self.copia, "planos", miolo_atual)
        self.assertFalse(alterou)
        self.assertEqual(self.copia.read_text(encoding="utf-8"), self.original)

    def test_escrever_em_marcador_ausente_levanta_value_error(self):
        with self.assertRaises(ValueError):
            regioes.escrever_regiao(self.copia, "nao-existe", "x")
        self.assertEqual(self.copia.read_text(encoding="utf-8"), self.original)


class TestMarcadorSemPar(unittest.TestCase):
    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self._tmp.cleanup)
        self.alvo = Path(self._tmp.name) / "marcador-quebrado.md"
        self.alvo.write_text("<!-- foo:start -->\nconteudo\n", encoding="utf-8")

    def test_ler_regiao_com_par_incompleto_levanta_value_error(self):
        with self.assertRaises(ValueError):
            regioes.ler_regiao(self.alvo, "foo")

    def test_escrever_regiao_com_par_incompleto_levanta_value_error(self):
        with self.assertRaises(ValueError):
            regioes.escrever_regiao(self.alvo, "foo", "x")


class TestMarcadorCitadoEmProsa(unittest.TestCase):
    """Marcador mencionado no meio de uma frase não é marcador.

    Regressão do defeito medido em 2026-08-12: `texto.find()` casava a menção
    antes do marcador real, e a escrita apagava tudo entre as duas — o corpo do
    documento que descrevia o próprio marcador.
    """

    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self._tmp.cleanup)
        self.alvo = Path(self._tmp.name) / "com-citacao.md"
        self.alvo.write_text(
            "# Plano\n"
            "\n"
            "| L-01 | O script exige `<!-- foo:start -->` no arquivo, e falha sem ele |\n"
            "\n"
            "## Backlog\n"
            "\n"
            "<!-- foo:start -->\n"
            "miolo antigo\n"
            "<!-- foo:end -->\n"
            "\n"
            "## Fonte\n",
            encoding="utf-8",
        )

    def test_ler_regiao_ignora_a_citacao_e_le_o_miolo_real(self):
        self.assertEqual(regioes.ler_regiao(self.alvo, "foo"), "\nmiolo antigo\n")

    def test_escrever_regiao_nao_apaga_o_corpo_que_cita_o_marcador(self):
        regioes.escrever_regiao(self.alvo, "foo", "\nmiolo novo\n")

        texto = self.alvo.read_text(encoding="utf-8")
        self.assertIn("O script exige `<!-- foo:start -->` no arquivo", texto)
        self.assertIn("## Backlog", texto)
        self.assertIn("## Fonte", texto)
        self.assertIn("miolo novo", texto)
        self.assertNotIn("miolo antigo", texto)

    def test_documento_so_com_citacao_nao_tem_regiao(self):
        so_citacao = Path(self._tmp.name) / "so-citacao.md"
        so_citacao.write_text(
            "Cita `<!-- foo:start -->` e `<!-- foo:end -->` em prosa, sem região.\n",
            encoding="utf-8",
        )
        self.assertIsNone(regioes.ler_regiao(so_citacao, "foo"))


if __name__ == "__main__":
    unittest.main()
