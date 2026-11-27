#!/usr/bin/env python3
"""Testes da migração dos projetos para o codex — parte 2.4 do plano do redesign.

Critério de aceite: num projeto com a cópia da norma, o aviso de abertura aparece; sem aprovação,
nada é apagado nem alterado; com aprovação, a cópia sai e cada coisa da lista 6 do mapa recebe o
tratamento previsto; num projeto sem a cópia e sem nada do que a lista 6 nomeia, nenhum aviso. O
hook roda de verdade, por subprocesso, como em `test_session_start.py`.
"""

from __future__ import annotations

import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import huddle
import migracao
from test_session_start import _Projeto

CABECALHO = "| # | Plano | Core | Módulo | Origem | Situação | Aprovado |\n|---|---|---|---|---|---|---|\n"


class _ProjetoAntigo(_Projeto):
    """Um projeto com o setup concluído, huddle em dia e o que o método anterior gravava."""

    def setUp(self):
        super().setUp()
        huddle.concluir(self.arquivo, self.ha_dias(0))  # o aviso do huddle não entra no caminho
        self.raiz = self.projeto / "docs" / "plan"
        self.copia = self.raiz / "system" / "modelo-dev-units.md"

    def gravar_o_que_o_metodo_anterior_gravava(self) -> None:
        self.copia.write_text("# Modelo dev-units\n", encoding="utf-8")
        texto = self.arquivo.read_text(encoding="utf-8")
        for antigo, novo in huddle.ESQUELETO_ANTERIOR:
            texto = texto.replace(novo, antigo)
        self.arquivo.write_text(texto, encoding="utf-8")
        (self.raiz / "_inbox").mkdir(parents=True, exist_ok=True)
        (self.raiz / "_inbox" / "add-x.md").write_text(
            "ver [norma](../system/modelo-dev-units.md)\n", encoding="utf-8"
        )
        # projeção, não plano: não entra na lista mesmo citando a norma
        (self.raiz / "_inbox" / "_backlog.md").write_text("modelo-dev-units\n", encoding="utf-8")


class TestComACopia(_ProjetoAntigo):
    def setUp(self):
        super().setUp()
        self.gravar_o_que_o_metodo_anterior_gravava()

    def test_o_aviso_aparece_e_aponta_o_setup(self):
        saida = self.saida()
        self.assertIsNotNone(saida)
        self.assertIn("/decode-and-code:setup", saida["systemMessage"])
        self.assertIn("migração", saida["hookSpecificOutput"]["additionalContext"])

    def test_sem_aprovacao_nada_muda(self):
        antes = {p: p.read_bytes() for p in self.projeto.rglob("*") if p.is_file() and ".git" not in p.parts}
        p = migracao.pendencias(self.projeto)
        self.saida()
        depois = {p: p.read_bytes() for p in self.projeto.rglob("*") if p.is_file() and ".git" not in p.parts}
        self.assertEqual(antes, depois)
        self.assertEqual(p.norma, self.copia)
        self.assertEqual(p.huddles, [self.arquivo])
        self.assertEqual([c.name for c in p.planos], ["add-x.md"])

    def test_com_aprovacao_a_copia_sai_e_o_huddle_troca_o_esqueleto(self):
        self.assertEqual(migracao.aplicar(self.projeto, "norma"), [self.copia])
        self.assertFalse(self.copia.exists())
        self.assertEqual(migracao.aplicar(self.projeto, "huddle"), [self.arquivo])
        texto = self.arquivo.read_text(encoding="utf-8")
        self.assertNotIn("modelo-dev-units", texto)
        self.assertIn("### H-01", texto)  # a entrada aberta continua lá
        self.assertEqual(huddle.lint_arquivo(self.arquivo), [])

    def test_os_planos_so_se_listam(self):
        migracao.aplicar(self.projeto, "norma")
        migracao.aplicar(self.projeto, "huddle")
        rascunho = self.raiz / "_inbox" / "add-x.md"
        self.assertIn("modelo-dev-units", rascunho.read_text(encoding="utf-8"))
        with self.assertRaises(ValueError):
            migracao.aplicar(self.projeto, "plano")

    def test_aplicar_de_novo_nao_faz_nada(self):
        migracao.aplicar(self.projeto, "norma")
        migracao.aplicar(self.projeto, "huddle")
        self.assertEqual(migracao.aplicar(self.projeto, "norma"), [])
        self.assertEqual(migracao.aplicar(self.projeto, "huddle"), [])


class TestPlanosAbertos(_ProjetoAntigo):
    def test_lista_unidade_e_handoff_de_plano_aberto_e_ignora_o_fechado(self):
        linhas = (
            "| 0001 | [aberto](0001-aberto/0001-aberto.md) | — | | — | em desenvolvimento | 2026-11-01 |\n"
            "| 0002 | [fechado](0002-fechado/0002-fechado.md) | — | | — | concluído | 2026-10-01 |\n"
        )
        (self.raiz / "_planos.md").write_text(
            f"<!-- planos:start -->\n{CABECALHO}{linhas}<!-- planos:end -->\n", encoding="utf-8"
        )
        for nome in ("0001-aberto", "0002-fechado"):
            pasta = self.raiz / nome
            pasta.mkdir()
            (pasta / f"{nome}.md").write_text("# plano\n", encoding="utf-8")
            (pasta / "01-u.md").write_text("[n](../system/modelo-dev-units.md), seção *X*\n", encoding="utf-8")
            (pasta / "_handoff.md").write_text("`docs/plan/system/modelo-dev-units.md`\n", encoding="utf-8")
        planos = migracao.pendencias(self.projeto).planos
        self.assertEqual(
            [p.relative_to(self.raiz).as_posix() for p in planos],
            ["0001-aberto/01-u.md", "0001-aberto/_handoff.md"],
        )


class TestProjetoLimpo(_ProjetoAntigo):
    def test_sem_nada_do_metodo_anterior_nenhum_aviso(self):
        self.assertTrue(migracao.pendencias(self.projeto).vazias())
        self.assertIsNone(self.saida())


if __name__ == "__main__":
    unittest.main()
