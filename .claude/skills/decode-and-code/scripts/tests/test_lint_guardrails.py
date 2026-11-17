#!/usr/bin/env python3
"""Testes de `guardrail.lint_arquivo` — plano 0007, tarefa T3.

Uma recusa por teste, contra arquivo sintético, e o `guardrails.json` real deste repositório
aprovando.
"""

from __future__ import annotations

import json
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import guardrail
import lib

REGRA = {"nome": "r1", "ferramenta": "Write$", "detector": "segredo", "mensagem": "Recusado."}


class _Base(unittest.TestCase):
    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self._tmp.cleanup)
        self.alvo = Path(self._tmp.name) / "guardrails.json"

    def lint_texto(self, texto: str) -> list[str]:
        self.alvo.write_text(texto, encoding="utf-8")
        return guardrail.lint_arquivo(self.alvo)

    def lint_regras(self, *regras) -> list[str]:
        return self.lint_texto(json.dumps({"regras": list(regras)}))

    def assertRecusa(self, problemas: list[str], trecho: str):
        self.assertTrue(problemas, "esperava recusa")
        self.assertTrue(any(trecho in p for p in problemas), problemas)


class TestAprova(_Base):
    def test_arquivo_real_do_repositorio_aprova(self):
        real = lib.repo_root() / ".claude" / "guardrails.json"
        self.assertEqual(guardrail.lint_arquivo(real), [])

    def test_regra_valida_aprova(self):
        self.assertEqual(self.lint_regras(REGRA), [])

    def test_lista_vazia_aprova(self):
        self.assertEqual(self.lint_regras(), [])


class TestRecusa(_Base):
    def test_arquivo_ausente_levanta(self):
        with self.assertRaises(FileNotFoundError):
            guardrail.lint_arquivo(self.alvo)

    def test_json_invalido(self):
        self.assertRecusa(self.lint_texto("{regras: []"), "JSON")

    def test_raiz_que_nao_e_objeto(self):
        self.assertRecusa(self.lint_texto("[]"), "regras")

    def test_sem_regras(self):
        self.assertRecusa(self.lint_texto("{}"), "regras")

    def test_regras_que_nao_e_lista(self):
        self.assertRecusa(self.lint_texto('{"regras": {}}'), "regras")

    def test_regra_que_nao_e_objeto(self):
        self.assertRecusa(self.lint_regras("r1"), "regra 1")

    def test_cada_chave_ausente(self):
        for chave in ("nome", "ferramenta", "detector", "mensagem"):
            with self.subTest(chave=chave):
                regra = {k: v for k, v in REGRA.items() if k != chave}
                self.assertRecusa(self.lint_regras(regra), chave)

    def test_cada_chave_vazia(self):
        for chave in ("nome", "ferramenta", "detector", "mensagem"):
            with self.subTest(chave=chave):
                self.assertRecusa(self.lint_regras({**REGRA, chave: "  "}), chave)

    def test_chave_que_nao_e_string(self):
        self.assertRecusa(self.lint_regras({**REGRA, "mensagem": 3}), "mensagem")

    def test_ferramenta_que_nao_compila(self):
        self.assertRecusa(self.lint_regras({**REGRA, "ferramenta": "(Write"}), "ferramenta")

    def test_detector_que_nao_compila(self):
        self.assertRecusa(self.lint_regras({**REGRA, "detector": "[a-"}), "detector")

    def test_nome_repetido(self):
        self.assertRecusa(self.lint_regras(REGRA, {**REGRA, "detector": "outro"}), "r1")


if __name__ == "__main__":
    unittest.main()
