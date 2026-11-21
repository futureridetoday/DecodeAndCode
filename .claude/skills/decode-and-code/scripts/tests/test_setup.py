#!/usr/bin/env python3
"""Teste declarado da unidade 0009-01 — `setup.py`, o registro do setup do projeto."""

from __future__ import annotations

import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import setup


class _Case(unittest.TestCase):
    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self._tmp.cleanup)
        self.projeto = Path(self._tmp.name).resolve() / "meu-projeto"
        self.projeto.mkdir()
        self.arquivo = setup.iniciar(self.projeto)

    def registrar(self, chave="usar-ruff", tipo="guideline", origem="stack", resultado="aceita",
                  detalhe="python.md"):
        setup.registrar(self.arquivo, chave, tipo, origem, resultado, detalhe)

    def texto(self) -> str:
        return self.arquivo.read_text(encoding="utf-8")


class TestIniciar(_Case):
    def test_cria_o_esqueleto_no_caminho(self):
        self.assertEqual(self.arquivo, setup.caminho(self.projeto))
        self.assertTrue(self.arquivo.is_file())
        self.assertIn("project: meu-projeto", self.texto())
        self.assertEqual(setup.lint(self.arquivo), [])

    def test_segunda_chamada_devolve_none_sem_tocar(self):
        self.registrar()
        antes = self.texto()
        self.assertIsNone(setup.iniciar(self.projeto))
        self.assertEqual(self.texto(), antes)


class TestFluxoCompleto(_Case):
    def test_lint_aprova_depois_de_perfil_registrar_e_concluir(self):
        setup.perfil(self.arquivo, "Loja online", "time de 3", "Next.js", "confirmado em chat")
        self.registrar()
        self.registrar("sem-any", "guardrail", "decisão do time", "rejeitada", "time prefere any")
        self.registrar("ruff-existente", "guideline", "arquivo pyproject.toml", "existente", "já lá")
        setup.concluir(self.arquivo, "2026-11-16")
        self.assertEqual(setup.lint(self.arquivo), [])
        self.assertIn("completed_at: 2026-11-16", self.texto())
        self.assertIn("- **Stack:** Next.js", self.texto())

    def test_perfil_reescreve_em_vez_de_acumular(self):
        setup.perfil(self.arquivo, "a", "b", "c", "d")
        setup.perfil(self.arquivo, "x", "y", "z", "w")
        self.assertEqual(self.texto().count("**Objetivo:**"), 1)
        self.assertIn("- **Objetivo:** x", self.texto())

    def test_decididas_devolve_a_chave_logo_depois_de_registrar(self):
        self.assertEqual(setup.decididas(self.arquivo), [])
        self.registrar("a-um")
        self.registrar("b-dois", "princípio", "existente", "existente", "x")
        self.assertEqual(setup.decididas(self.arquivo), ["a-um", "b-dois"])

    def test_pipe_no_detalhe_e_escapado_e_lint_aprova(self):
        self.registrar(detalhe="a | b")
        self.assertIn("a \\| b", self.texto())
        self.assertEqual(setup.lint(self.arquivo), [])
        self.assertEqual(setup.decididas(self.arquivo), ["usar-ruff"])

    def test_registrar_antes_de_proxima_secao(self):
        self.arquivo.write_text(self.texto() + "\n## Outra\n\ntexto\n", encoding="utf-8")
        self.registrar()
        self.assertLess(self.texto().index("usar-ruff"), self.texto().index("## Outra"))
        self.assertEqual(setup.lint(self.arquivo), [])


class TestRecusas(_Case):
    def assertRecusa(self, **kwargs):
        antes = self.texto()
        with self.assertRaises(ValueError):
            self.registrar(**kwargs)
        self.assertEqual(self.texto(), antes)

    def test_tipo_fora_do_vocabulario(self):
        self.assertRecusa(tipo="convenção")

    def test_origem_fora_do_vocabulario(self):
        self.assertRecusa(origem="palpite")
        self.assertRecusa(origem="arquivo ")
        self.assertRecusa(origem="extraído")

    def test_origem_proposto_aceita(self):
        """Plano 0016: princípio inferido do objetivo; o extraído usa 'arquivo <caminho>'."""
        self.registrar(chave="north-star", tipo="princípio", origem="proposto", detalhe="principles.md")
        self.assertIn("| north-star | princípio | proposto |", self.texto())

    def test_resultado_fora_do_vocabulario(self):
        self.assertRecusa(resultado="talvez")

    def test_chave_fora_de_kebab_case(self):
        self.assertRecusa(chave="Usar Ruff")

    def test_chave_repetida(self):
        self.registrar()
        self.assertRecusa()

    def test_detalhe_vazio(self):
        self.assertRecusa(detalhe="  ")

    def test_secao_ausente(self):
        self.arquivo.write_text(self.texto().replace("## Decisões", "## Outras"), encoding="utf-8")
        antes = self.texto()
        with self.assertRaises(ValueError):
            self.registrar()
        self.assertEqual(self.texto(), antes)

    def test_perfil_sem_linha_em_branco_duplicada(self):
        # C8 do plano `0013`: medido nos três testes da validação do `0009`.
        setup.perfil(self.arquivo, "a", "b", "c", "d")
        setup.perfil(self.arquivo, "x", "y", "z", "w")
        texto = self.texto()
        self.assertNotIn("\n\n\n", texto)
        self.assertIn("## Perfil\n\n- **Objetivo:** x\n", texto)

    def test_perfil_com_campo_vazio_nao_escreve(self):
        antes = self.texto()
        with self.assertRaises(ValueError):
            setup.perfil(self.arquivo, "a", "", "c", "d")
        self.assertEqual(self.texto(), antes)

    def test_concluir_com_data_invalida(self):
        antes = self.texto()
        with self.assertRaises(ValueError):
            setup.concluir(self.arquivo, "ontem")
        self.assertEqual(self.texto(), antes)


class TestLint(_Case):
    def test_reprova_o_que_a_mao_estragou(self):
        casos = {
            "tipo": ("| a-b | guideline | stack | aceita | x | 2026-11-16 |",
                     "| a-b | regra | stack | aceita | x | 2026-11-16 |"),
            "resultado": ("| a-b | guideline | stack | aceita | x | 2026-11-16 |",
                          "| a-b | guideline | stack | feita | x | 2026-11-16 |"),
        }
        for nome, (valida, quebrada) in casos.items():
            with self.subTest(nome):
                self.arquivo.write_text(self.texto().rstrip("\n") + "\n" + quebrada + "\n", encoding="utf-8")
                self.assertTrue(setup.lint(self.arquivo))
                self.setUp()

    def test_reprova_chave_repetida_e_completed_at_ruim(self):
        linha = "| a-b | guideline | stack | aceita | x | 2026-11-16 |\n"
        self.arquivo.write_text(self.texto() + linha + linha, encoding="utf-8")
        self.assertTrue(any("repetida" in p for p in setup.lint(self.arquivo)))
        self.arquivo.write_text(self.texto().replace('completed_at: ""', "completed_at: ontem"), encoding="utf-8")
        self.assertTrue(any("completed_at" in p for p in setup.lint(self.arquivo)))

    def test_reprova_secao_ausente(self):
        self.arquivo.write_text(self.texto().replace("## Perfil", "## Outro"), encoding="utf-8")
        self.assertTrue(any("Perfil" in p for p in setup.lint(self.arquivo)))


if __name__ == "__main__":
    unittest.main()
