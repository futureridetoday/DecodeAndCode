#!/usr/bin/env python3
"""Teste declarado das unidades 0004-02 e 0004-04 — `bootstrap.iniciar`.

`TestIniciarDiretorioVazio` prova o caminho feliz e a amarração com o próximo passo do ciclo
(`numeracao.proximo_plano`, sequência da unidade, passo 5) — sem essa amarração, o `_planos.md`
criado poderia ter marcadores e ainda assim ser ilegível para quem lê a região. `TestIniciarIdempotente`
e `TestIniciarPreservaPlanosExistente` provam a idempotência item a item, no mesmo padrão de
`huddle.iniciar`: pulo por caminho, nunca tudo-ou-nada. `TestIniciarProjetoInexistente` prova que a
checagem vem antes de toda escrita, como em `scaffold.aprovar`.

A `0004-04` acrescenta a norma-mecanismo ao que `iniciar` materializa: `TestIniciarDiretorioVazio`
passa a esperar cinco caminhos, não quatro; `TestIniciarUsaReferenceQuandoPresente` prova a
prioridade de `reference/` sobre o `plan_root` do checkout; `TestIniciarNaoSobrescreveNormaEditada`
prova a idempotência da norma especificamente — o item que o critério de aceite nomeia.
"""

from __future__ import annotations

import sys
import tempfile
import unittest
from pathlib import Path
from unittest import mock

sys.path.insert(0, str(Path(__file__).resolve().parent))
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import bootstrap
import fixtures
import lib
import numeracao
import regioes


class TestIniciarDiretorioVazio(unittest.TestCase):
    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self._tmp.cleanup)
        self.projeto = Path(self._tmp.name).resolve()

    def test_devolve_os_cinco_caminhos_criados(self):
        criados = bootstrap.iniciar(self.projeto)

        esperados = [
            self.projeto / "docs" / "plan" / "_planos.md",
            self.projeto / "docs" / "plan" / "_inbox",
            self.projeto / "docs" / "plan" / "system",
            self.projeto / ".claude",
            self.projeto / "docs" / "plan" / "system" / "modelo-dev-units.md",
        ]
        self.assertEqual(criados, esperados)
        for caminho in esperados:
            self.assertTrue(caminho.exists(), caminho)

    def test_norma_materializada_tem_o_conteudo_da_norma_mecanismo(self):
        bootstrap.iniciar(self.projeto)

        norma = self.projeto / "docs" / "plan" / "system" / "modelo-dev-units.md"
        conteudo = norma.read_text(encoding="utf-8")
        self.assertIn("Modelo dev-units", conteudo)

    def test_planos_md_nao_contem_o_nome_deste_repositorio(self):
        bootstrap.iniciar(self.projeto)

        planos_md = self.projeto / "docs" / "plan" / "_planos.md"
        projeto_no_frontmatter = regioes.ler_campo(planos_md, "project")

        self.assertEqual(projeto_no_frontmatter, self.projeto.name)
        self.assertNotIn("DecodeAndCode", planos_md.read_text(encoding="utf-8"))

    def test_planos_md_e_legivel_por_regioes_e_por_numeracao(self):
        bootstrap.iniciar(self.projeto)

        planos_md = self.projeto / "docs" / "plan" / "_planos.md"
        self.assertIsNotNone(regioes.ler_regiao(planos_md, "planos"))

        with mock.patch.object(lib, "repo_root", return_value=self.projeto):
            self.assertEqual(numeracao.proximo_plano(), "0001")


class TestIniciarIdempotente(unittest.TestCase):
    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self._tmp.cleanup)
        self.projeto = Path(self._tmp.name).resolve()

    def test_segunda_chamada_devolve_lista_vazia_e_nao_toca_em_nada(self):
        bootstrap.iniciar(self.projeto)
        planos_md = self.projeto / "docs" / "plan" / "_planos.md"
        conteudo_apos_primeira = planos_md.read_text(encoding="utf-8")

        criados = bootstrap.iniciar(self.projeto)

        self.assertEqual(criados, [])
        self.assertEqual(planos_md.read_text(encoding="utf-8"), conteudo_apos_primeira)


class TestIniciarPreservaPlanosExistente(unittest.TestCase):
    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self._tmp.cleanup)
        self.projeto = Path(self._tmp.name).resolve()

        self.raiz_planos = self.projeto / "docs" / "plan"
        self.raiz_planos.mkdir(parents=True)
        fixtures.planos_md(self.raiz_planos)

    def test_nao_sobrescreve_planos_md_com_linhas_registradas(self):
        planos_md = self.raiz_planos / "_planos.md"
        conteudo_antes = planos_md.read_text(encoding="utf-8")

        criados = bootstrap.iniciar(self.projeto)

        self.assertEqual(planos_md.read_text(encoding="utf-8"), conteudo_antes)
        self.assertNotIn(planos_md, criados)
        self.assertEqual(
            set(criados),
            {
                self.raiz_planos / "_inbox",
                self.raiz_planos / "system",
                self.projeto / ".claude",
                self.raiz_planos / "system" / "modelo-dev-units.md",
            },
        )


class TestIniciarNaoSobrescreveNormaEditada(unittest.TestCase):
    """Segunda metade do critério de aceite da `0004-04`: a norma sobrevive a um segundo bootstrap."""

    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self._tmp.cleanup)
        self.projeto = Path(self._tmp.name).resolve()

    def test_segunda_chamada_preserva_edicao_do_projeto(self):
        bootstrap.iniciar(self.projeto)
        norma = self.projeto / "docs" / "plan" / "system" / "modelo-dev-units.md"
        norma.write_text("# a minha cópia, editada\n", encoding="utf-8")

        criados = bootstrap.iniciar(self.projeto)

        self.assertEqual(norma.read_text(encoding="utf-8"), "# a minha cópia, editada\n")
        self.assertEqual(criados, [])
        self.assertNotIn(norma, criados)


class TestIniciarUsaReferenceQuandoPresente(unittest.TestCase):
    """Simula o bootstrap rodando de um pacote: `reference/`, ao lado da skill, tem prioridade
    sobre o `plan_root` do checkout — é o primeiro dos dois lugares que `_fonte_norma` tenta."""

    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self._tmp.cleanup)
        raiz = Path(self._tmp.name).resolve()

        self.projeto = raiz / "projeto"
        self.projeto.mkdir()

        skill = raiz / "pacote" / "skills" / "decode-and-code"
        (skill / "reference").mkdir(parents=True)
        (skill / "reference" / "modelo-dev-units.md").write_text(
            "# norma do pacote\n", encoding="utf-8"
        )

        patcher = mock.patch.object(lib, "_config_path", return_value=skill / "config.json")
        patcher.start()
        self.addCleanup(patcher.stop)

    def test_norma_vem_da_reference_ao_lado_da_skill(self):
        bootstrap.iniciar(self.projeto)

        alvo = self.projeto / "docs" / "plan" / "system" / "modelo-dev-units.md"
        self.assertEqual(alvo.read_text(encoding="utf-8"), "# norma do pacote\n")


class TestIniciarProjetoInexistente(unittest.TestCase):
    def test_levanta_file_not_found_error_sem_escrever_nada(self):
        with tempfile.TemporaryDirectory() as tmp:
            projeto = Path(tmp) / "nao-existe"
            with self.assertRaises(FileNotFoundError):
                bootstrap.iniciar(projeto)
            self.assertFalse(projeto.exists())


if __name__ == "__main__":
    unittest.main()
