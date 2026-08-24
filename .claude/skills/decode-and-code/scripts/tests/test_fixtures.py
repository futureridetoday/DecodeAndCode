#!/usr/bin/env python3
"""Testes de tests/fixtures.py — unidade 0001-02.

O critério de aceite: cada um dos quatro construtores produz artefato que passa no lint
correspondente — `lint_unidade` para `unidade()`, `lint_skill` para `skill()`, e
`regioes.ler_regiao`/`ler_campo` para `plano()` e `planos_md()`, que não têm lint próprio —
sem tocar em nenhum caminho real do repositório. Cada classe cobre também o erro declarado
no Contrato: argumento inválido levanta `ValueError` antes de escrever qualquer arquivo.
"""

from __future__ import annotations

import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import fixtures
import lint_skill
import lint_unidade
import regioes


class TestUnidade(unittest.TestCase):
    def test_aprova_no_lint_unidade(self):
        with tempfile.TemporaryDirectory() as tmp:
            alvo = fixtures.unidade(Path(tmp))
            self.assertEqual(lint_unidade.lint(alvo), [])

    def test_aceita_campos_customizados_e_aprova(self):
        with tempfile.TemporaryDirectory() as tmp:
            alvo = fixtures.unidade(
                Path(tmp),
                unit_id="0042-03",
                core="outro",
                module="modulo",
                state="verified",
                test="tests/test_outro.py",
                titulo="Outra unidade",
            )
            self.assertEqual(lint_unidade.lint(alvo), [])

    def test_unit_id_invalido_levanta_value_error_sem_escrever(self):
        with tempfile.TemporaryDirectory() as tmp:
            alvo = Path(tmp) / "01-exemplo.md"
            with self.assertRaises(ValueError):
                fixtures.unidade(Path(tmp), unit_id="abc")
            self.assertFalse(alvo.exists())


class TestSkill(unittest.TestCase):
    def test_aprova_no_lint_skill(self):
        with tempfile.TemporaryDirectory() as tmp:
            alvo = fixtures.skill(Path(tmp))
            self.assertEqual(lint_skill.lint(alvo), [])

    def test_aprova_com_modos_citados_no_corpo(self):
        with tempfile.TemporaryDirectory() as tmp:
            alvo = fixtures.skill(
                Path(tmp), corpo="Corpo citando os modos review, derive e implement."
            )
            self.assertEqual(
                lint_skill.lint(alvo, modos=["review", "derive", "implement"]), []
            )

    def test_nome_invalido_levanta_value_error_sem_escrever(self):
        with tempfile.TemporaryDirectory() as tmp:
            with self.assertRaises(ValueError):
                fixtures.skill(Path(tmp), nome="")
            self.assertEqual(list(Path(tmp).iterdir()), [])


class TestPlano(unittest.TestCase):
    def test_tem_backlog_e_frontmatter_validos(self):
        with tempfile.TemporaryDirectory() as tmp:
            dir_plano = fixtures.plano(Path(tmp))
            arquivo = dir_plano / f"{dir_plano.name}.md"
            self.assertIsNotNone(regioes.ler_regiao(arquivo, "backlog"))
            self.assertEqual(regioes.ler_campo(arquivo, "status"), "approved")
            self.assertEqual(regioes.ler_campo(arquivo, "core"), "builder")

    def test_core_vazio_levanta_value_error_sem_escrever(self):
        with tempfile.TemporaryDirectory() as tmp:
            with self.assertRaises(ValueError):
                fixtures.plano(Path(tmp), core="")
            self.assertEqual(list(Path(tmp).iterdir()), [])


class TestPlanosMd(unittest.TestCase):
    def test_regiao_planos_legivel(self):
        with tempfile.TemporaryDirectory() as tmp:
            alvo = fixtures.planos_md(Path(tmp))
            miolo = regioes.ler_regiao(alvo, "planos")
            self.assertIsNotNone(miolo)
            self.assertIn("0009", miolo)
            self.assertIn("exemplo", miolo)

    def test_linha_customizada_aparece_na_regiao(self):
        with tempfile.TemporaryDirectory() as tmp:
            linha = (
                "| 0042 | [outro](core/0042-outro/0042-outro.md) | core | outro"
                " | — | concluído | 2026-08-24 |\n"
            )
            alvo = fixtures.planos_md(Path(tmp), linhas=[linha])
            miolo = regioes.ler_regiao(alvo, "planos")
            self.assertIn("0042", miolo)

    def test_linha_malformada_levanta_value_error_sem_escrever(self):
        with tempfile.TemporaryDirectory() as tmp:
            alvo = Path(tmp) / "_planos.md"
            with self.assertRaises(ValueError):
                fixtures.planos_md(Path(tmp), linhas=["sem barra inicial\n"])
            self.assertFalse(alvo.exists())


class TestNenhumCaminhoRealTocado(unittest.TestCase):
    """O critério de aceite: os quatro construtores só escrevem dentro do diretório dado."""

    def test_todos_os_artefatos_ficam_sob_o_tempdir(self):
        with tempfile.TemporaryDirectory() as tmp:
            raiz = Path(tmp).resolve()
            dir_plano = fixtures.plano(raiz)
            caminhos = [
                fixtures.unidade(raiz),
                fixtures.skill(raiz),
                dir_plano / f"{dir_plano.name}.md",
                fixtures.planos_md(raiz),
            ]
            for caminho in caminhos:
                with self.subTest(caminho=caminho):
                    self.assertIn(raiz, caminho.resolve().parents)


if __name__ == "__main__":
    unittest.main()
