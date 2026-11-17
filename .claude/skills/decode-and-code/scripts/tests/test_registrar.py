#!/usr/bin/env python3
"""Testes de `registry.registrar` — plano 0007, tarefa T2.

Raiz sintética passada explicitamente; nada toca `.claude/rules/` do repositório.
"""

from __future__ import annotations

import json
import sys
import tempfile
import unittest
from datetime import date
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import registry
import rules


def _guideline(dir_rules: Path, nome: str) -> Path:
    alvo = dir_rules / f"{nome}.md"
    alvo.write_text(
        f'---\nname: "{nome}"\ndescription: "d"\npaths: ["src/**/*"]\n---\n\nCorpo.\n',
        encoding="utf-8",
    )
    return alvo


class _Base(unittest.TestCase):
    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self._tmp.cleanup)
        self.raiz = Path(self._tmp.name)
        (self.raiz / "src").mkdir()
        (self.raiz / "src" / "a.py").write_text("x", encoding="utf-8")
        self.dir_rules = self.raiz / ".claude" / "rules"
        self.dir_rules.mkdir(parents=True)
        self.registro = self.dir_rules / "registry.json"

    def ler(self) -> dict:
        return json.loads(self.registro.read_text(encoding="utf-8"))


class TestRegistrar(_Base):
    def test_cria_registro_com_a_guideline_ligada_e_datada_de_hoje(self):
        _guideline(self.dir_rules, "estilo")
        registry.registrar(self.raiz, "estilo")
        self.assertEqual(
            self.ler(), {"estilo": {"estado": "ligada", "atualizado_em": date.today().isoformat()}}
        )

    def test_primeiro_registrar_inclui_todas_as_guidelines_do_diretorio(self):
        _guideline(self.dir_rules, "antiga")
        _guideline(self.dir_rules, "nova")
        registry.registrar(self.raiz, "nova")
        self.assertEqual(sorted(self.ler()), ["antiga", "nova"])

    def test_preserva_a_data_de_quem_nao_mudou(self):
        _guideline(self.dir_rules, "antiga")
        self.registro.write_text(
            json.dumps({"antiga": {"estado": "ligada", "atualizado_em": "2026-01-01"}}),
            encoding="utf-8",
        )
        _guideline(self.dir_rules, "nova")
        registry.registrar(self.raiz, "nova")
        self.assertEqual(self.ler()["antiga"]["atualizado_em"], "2026-01-01")

    def test_nome_que_nao_e_guideline_em_rules_recusado_sem_escrever(self):
        with self.assertRaises(ValueError):
            registry.registrar(self.raiz, "inexistente")
        self.assertFalse(self.registro.exists())

    def test_md_sem_frontmatter_ao_lado_nao_trava_o_registro(self):
        (self.dir_rules / "manual.md").write_text("Rule escrita à mão.\n", encoding="utf-8")
        _guideline(self.dir_rules, "estilo")
        registry.registrar(self.raiz, "estilo")
        self.assertEqual(sorted(self.ler()), ["estilo"])


class TestCriarGuidelineRegistra(_Base):
    def test_criar_guideline_registra_depois_de_gravar(self):
        rules.criar_guideline(self.raiz, "estilo", "d", ["src/**/*"], "Corpo.")
        self.assertEqual(self.ler()["estilo"]["estado"], "ligada")

    def test_reprovacao_nao_cria_registro(self):
        with self.assertRaises(ValueError):
            rules.criar_guideline(self.raiz, "estilo", "d", ["app/**/*"], "Corpo.")
        self.assertFalse(self.registro.exists())


if __name__ == "__main__":
    unittest.main()
