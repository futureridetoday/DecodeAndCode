#!/usr/bin/env python3
"""Teste declarado da unidade 0001-21 — `huddle.lint_arquivo`, `lint_relatorio` e `iniciar`.

`TestLintArquivoContraORealArquivo` é o caso contra a instância — `docs/plan/system/huddle.md`
real, não só fixture (`L-31`): é ele que prova que o parser aprova o arquivo que o time usa todo
dia, com suas nove entradas abertas e uma fechada. `TestLintArquivoInvariantesIsolados` isola cada
um dos três invariantes num caso próprio, contra um huddle sintético mínimo que sozinho já aprova —
mesmo padrão de `AGENTE_VALIDO`/`UNIDADE_VALIDA`.
"""

from __future__ import annotations

import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import huddle
import lib

_HUDDLE_VALIDO = """\
---
name: huddle
type: doc
---

# Huddle

## Abertas

### H-01 · `pergunta` · 2026-08-01 · Teste

Corpo da entrada aberta.

## Fechadas

| # | Tipo | Fechada em | Destino |
|---|---|---|---|
"""


class TestLintArquivoContraORealArquivo(unittest.TestCase):
    """`L-31` — sem este caso, o lint prova só o mecanismo, nunca a instância real."""

    def test_huddle_real_aprova_sem_ressalva(self):
        caminho = lib.plan_root() / "system" / "huddle.md"
        self.assertEqual(huddle.lint_arquivo(caminho), [])


class TestLintArquivoInvariantesIsolados(unittest.TestCase):
    """Cada teste quebra um invariante por vez, contra o mesmo huddle sintético mínimo."""

    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self._tmp.cleanup)
        self.dir = Path(self._tmp.name)

    def _escreve(self, texto: str) -> Path:
        alvo = self.dir / "huddle.md"
        alvo.write_text(texto, encoding="utf-8")
        return alvo

    def test_huddle_valido_aprova(self):
        alvo = self._escreve(_HUDDLE_VALIDO)
        self.assertEqual(huddle.lint_arquivo(alvo), [])

    def test_id_presente_nas_duas_secoes_reprova_despejo(self):
        texto = _HUDDLE_VALIDO.replace(
            "| # | Tipo | Fechada em | Destino |\n|---|---|---|---|\n",
            "| # | Tipo | Fechada em | Destino |\n|---|---|---|---|\n"
            "| H-01 | `pergunta` | 2026-08-02 | Norma X |\n",
        )
        alvo = self._escreve(texto)
        problemas = huddle.lint_arquivo(alvo)
        self.assertTrue(any("despejo" in p for p in problemas), problemas)

    def test_tipo_fora_do_vocabulario_reprova(self):
        texto = _HUDDLE_VALIDO.replace("`pergunta`", "`bug`")
        alvo = self._escreve(texto)
        problemas = huddle.lint_arquivo(alvo)
        self.assertTrue(
            any("vocabulário fechado" in p and "bug" in p for p in problemas), problemas
        )

    def test_id_repetido_em_abertas_reprova(self):
        texto = _HUDDLE_VALIDO.replace(
            "### H-01 · `pergunta` · 2026-08-01 · Teste\n\nCorpo da entrada aberta.\n",
            "### H-01 · `pergunta` · 2026-08-01 · Teste\n\nCorpo da entrada aberta.\n\n"
            "### H-01 · `padrão` · 2026-08-02 · Teste\n\nOutro corpo, mesmo id.\n",
        )
        alvo = self._escreve(texto)
        problemas = huddle.lint_arquivo(alvo)
        self.assertTrue(any("repetido" in p for p in problemas), problemas)

    def test_secao_ausente_e_problema_nao_excecao(self):
        texto = _HUDDLE_VALIDO.replace("## Fechadas", "## Outra coisa")
        alvo = self._escreve(texto)
        problemas = huddle.lint_arquivo(alvo)
        self.assertTrue(any("Fechadas" in p for p in problemas), problemas)


class TestArquivoInexistente(unittest.TestCase):
    def test_levanta_file_not_found_error(self):
        with tempfile.TemporaryDirectory() as tmp:
            alvo = Path(tmp) / "nao-existe.md"
            with self.assertRaises(FileNotFoundError):
                huddle.lint_arquivo(alvo)


class TestLintRelatorio(unittest.TestCase):
    """Os dois casos andam juntos: sem o segundo, o lint aceitaria qualquer texto."""

    def test_aceita_relatorio_que_declara_zero(self):
        texto = "Unidade implementada, gate de saída verde.\n\nentradas novas no huddle: 0\n"
        self.assertEqual(huddle.lint_relatorio(texto), [])

    def test_recusa_relatorio_sem_a_linha_de_fecho(self):
        texto = "Unidade implementada, gate de saída verde.\n"
        problemas = huddle.lint_relatorio(texto)
        self.assertTrue(any("entradas novas no huddle" in p for p in problemas), problemas)


class TestIniciar(unittest.TestCase):
    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self._tmp.cleanup)
        self.destino = Path(self._tmp.name) / "huddle.md"

    def test_cria_esqueleto_que_passa_em_lint_arquivo(self):
        escrito = huddle.iniciar(self.destino)
        self.assertEqual(escrito, self.destino)
        self.assertTrue(self.destino.is_file())
        self.assertEqual(huddle.lint_arquivo(self.destino), [])

    def test_segunda_chamada_devolve_none_sem_tocar_no_arquivo(self):
        huddle.iniciar(self.destino)
        conteudo_apos_primeira = self.destino.read_text(encoding="utf-8")

        resultado = huddle.iniciar(self.destino)

        self.assertIsNone(resultado)
        self.assertEqual(self.destino.read_text(encoding="utf-8"), conteudo_apos_primeira)


if __name__ == "__main__":
    unittest.main()
