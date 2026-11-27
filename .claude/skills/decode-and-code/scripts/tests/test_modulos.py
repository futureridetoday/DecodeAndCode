#!/usr/bin/env python3
"""Testes dos módulos e do módulo de correção — subparte 2.2.10 do redesign (K-08).

Inventário, itens 34 e 58: incluir ou remover um módulo não quebra o núcleo, e o núcleo nunca
depende dele. O núcleo só lê o `module.json`; estes testes provam os dois lados — com o módulo
presente, e com a pasta de módulos vazia.
"""

from __future__ import annotations

import contextlib
import io
import json
import sys
import tempfile
import unittest
from pathlib import Path
from unittest import mock

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import dc
import lib
import lint_codex
import lint_plano
import lint_skill
import normas

SKILLS = lib.repo_root() / ".claude" / "skills"

PLANO_MINIMO = """\
---
plan_id: ""
status: draft
plan_size: pequeno
plan_type: fix
format_version: 2
approved_by: ""
approved_at: ""
test: tests/test_algo.py
state: spec
verified_at: ""
---

# fix-algo

## Objetivo

x

## Defeito

x

## Correção

x

## Como verificar

x

## Recursos

nenhum

## Tarefas

- [ ] teste vermelho, ajuste, teste verde
"""


class TestDescoberta(unittest.TestCase):
    def _pasta(self, manifesto: str) -> Path:
        tmp = tempfile.TemporaryDirectory()
        self.addCleanup(tmp.cleanup)
        pasta = Path(tmp.name)
        (pasta / "m").mkdir()
        (pasta / "m" / "module.json").write_text(manifesto, encoding="utf-8")
        return pasta

    def test_o_modulo_de_correcao_esta_presente(self) -> None:
        [modulo] = lib.modulos()
        self.assertEqual((modulo["name"], modulo["plan_types"], modulo["skills"]), ("fix", ["fix"], ["diagnose"]))

    def test_skills_do_pacote_trazem_as_do_modulo(self) -> None:
        self.assertEqual(lib.skills_do_pacote(), lib.SKILLS + ("diagnose",))

    def test_manifesto_ilegivel_recusa_nomeando(self) -> None:
        with self.assertRaisesRegex(ValueError, "ilegível"):
            lib.modulos(self._pasta("{"))

    def test_manifesto_incompleto_recusa(self) -> None:
        with self.assertRaisesRegex(ValueError, "sem"):
            lib.modulos(self._pasta(json.dumps({"name": "m"})))

    def test_modulo_de_outro_formato_recusa(self) -> None:
        dados = {"name": "m", "version": "1", "core_format": 9, "plan_types": [], "skills": [], "plan_sections": {}}
        with self.assertRaisesRegex(ValueError, "formato 9"):
            lib.modulos(self._pasta(json.dumps(dados)))

    def test_pasta_sem_modulos(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            self.assertEqual(lib.modulos(Path(tmp)), [])
            self.assertEqual(lib.skills_do_pacote(Path(tmp)), lib.SKILLS)


class TestNucleoSemModulo(unittest.TestCase):
    """Com a pasta de módulos vazia, o núcleo segue inteiro."""

    def setUp(self) -> None:
        tmp = tempfile.TemporaryDirectory()
        self.addCleanup(tmp.cleanup)
        p = mock.patch.object(lib, "modulos_dir", return_value=Path(tmp.name))
        p.start()
        self.addCleanup(p.stop)

    def test_codex_do_nucleo_basta(self) -> None:
        self.assertEqual(normas.pastas_do_codex(), [normas.codex_dir()])
        self.assertEqual(lint_codex.lint_estrutura(lint_codex.pastas_do_codex()), [])
        with self.assertRaises(ValueError):
            normas.secao_do_codex("Correção")

    def test_explicar_e_modulos_rodam(self) -> None:
        saida = io.StringIO()
        with mock.patch.object(dc, "_registrar"), contextlib.redirect_stdout(saida):
            self.assertEqual(dc.main(["explicar"]), 0)
            self.assertEqual(dc.main(["modulos"]), 0)
        self.assertIn("nenhum módulo", saida.getvalue())

    def test_fix_sem_modulo_segue_o_workflow_de_produto(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            plano = Path(tmp) / "fix-algo.md"
            plano.write_text(PLANO_MINIMO, encoding="utf-8")
            self.assertEqual(lint_plano.secoes_exigidas(plano), lint_plano.SECOES_DO_FORMATO_ATUAL)


class TestModuloDeCorrecao(unittest.TestCase):
    def test_capitulo_do_modulo_no_codex(self) -> None:
        capitulo, trecho = normas.secao_do_codex("Correção")
        self.assertEqual(capitulo.parent.parent.name, "fix")
        self.assertTrue(trecho.startswith("## Correção"))

    def test_nucleo_e_modulo_juntos_passam_nos_lints(self) -> None:
        pastas = lint_codex.pastas_do_codex()
        self.assertEqual(len(pastas), 2)
        self.assertEqual(lint_codex.lint_estrutura(pastas), [])
        nomes = lint_codex.nomes_de_mecanismo(lint_codex.SKILLS_DIR)
        projetos = lint_codex.nomes_de_projeto(lint_codex.SKILLS_DIR.parent.parent, None)
        self.assertEqual(lint_codex.lint_dependencia(pastas, nomes, projetos), [])

    def test_nucleo_nao_cita_o_capitulo_do_modulo(self) -> None:
        titulos = {s.titulo for c in lint_codex.capitulos(lint_codex.pastas_do_codex()[1]) for s in lint_codex.secoes(c)}
        for capitulo in lint_codex.capitulos(lint_codex.CODEX_DIR):
            texto = capitulo.read_text(encoding="utf-8")
            for titulo in titulos:
                self.assertNotIn(titulo, texto.replace("Correção do", ""), f"{capitulo.name} cita {titulo}")

    def test_plano_minimo_tem_as_secoes_do_modulo(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            plano = Path(tmp) / "fix-algo.md"
            plano.write_text(PLANO_MINIMO, encoding="utf-8")
            self.assertEqual(lint_plano.lint(plano), [])
            plano.write_text(PLANO_MINIMO.replace("## Defeito", "## Outro"), encoding="utf-8")
            self.assertIn("formato 2 exige '## Defeito'", lint_plano.lint(plano))

    def test_skill_do_modulo_aprova_no_lint_e_tem_o_atalho(self) -> None:
        skill = SKILLS / "diagnose" / "SKILL.md"
        self.assertEqual(lint_skill.lint(skill, modos=["diagnose"]), [])
        self.assertEqual((SKILLS / "diagnose" / "dc.py").read_bytes(), (SKILLS / "decode" / "dc.py").read_bytes())


if __name__ == "__main__":
    unittest.main()
