#!/usr/bin/env python3
"""Testes de `guardrail.adicionar` — plano 0007, tarefa T4.

A regra só entra provada pelo par: nega `proibido` com a própria regra e libera `permitido`.
Raiz sintética passada explicitamente.
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

REGRA = {
    "nome": "estilo-separado",
    "ferramenta": "^(Write|Edit)$",
    "detector": "className=",
    "mensagem": "Estilo vai no arquivo .styles.ts, não no componente.",
}
PROIBIDO = {"tool_name": "Write", "tool_input": {"content": '<div className="x" />'}}
PERMITIDO = {"tool_name": "Write", "tool_input": {"content": "<Botao />"}}


class _Base(unittest.TestCase):
    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self._tmp.cleanup)
        self.raiz = Path(self._tmp.name)
        self.arquivo = self.raiz / ".claude" / "guardrails.json"

    def regras(self) -> list[dict]:
        return json.loads(self.arquivo.read_text(encoding="utf-8"))["regras"]

    def existente(self, *regras):
        self.arquivo.parent.mkdir(parents=True, exist_ok=True)
        self.arquivo.write_text(json.dumps({"regras": list(regras)}), encoding="utf-8")
        return self.arquivo.read_bytes()


class TestAdiciona(_Base):
    def test_cria_o_arquivo_quando_falta(self):
        alvo = guardrail.adicionar(self.raiz, REGRA, PROIBIDO, PERMITIDO)
        self.assertEqual(alvo, self.arquivo)
        self.assertEqual(self.regras(), [REGRA])

    def test_acrescenta_ao_fim_preservando_as_existentes(self):
        outra = {**REGRA, "nome": "outra", "detector": "TODO"}
        self.existente(outra)
        guardrail.adicionar(self.raiz, REGRA, PROIBIDO, PERMITIDO)
        self.assertEqual([r["nome"] for r in self.regras()], ["outra", "estilo-separado"])

    def test_resultado_passa_no_lint_e_o_hook_nega_o_proibido(self):
        guardrail.adicionar(self.raiz, REGRA, PROIBIDO, PERMITIDO)
        self.assertEqual(guardrail.lint_arquivo(self.arquivo), [])
        decisao, aviso = guardrail.decidir(json.dumps(PROIBIDO), self.arquivo)
        self.assertEqual((decisao or {}).get("regra"), "estilo-separado")
        self.assertIsNone(aviso)


class TestRecusa(_Base):
    def test_regra_que_nao_nega_o_proibido(self):
        with self.assertRaises(ValueError):
            guardrail.adicionar(self.raiz, {**REGRA, "detector": "nunca-casa"}, PROIBIDO, PERMITIDO)
        self.assertFalse(self.arquivo.exists())

    def test_regra_que_nega_o_permitido(self):
        with self.assertRaises(ValueError):
            guardrail.adicionar(self.raiz, {**REGRA, "detector": "<"}, PROIBIDO, PERMITIDO)
        self.assertFalse(self.arquivo.exists())

    def test_regra_avaliada_sozinha_d03(self):
        """Uma regra anterior que já nega o proibido não pode aprovar a candidata que nada casa."""
        anterior = {**REGRA, "nome": "anterior"}
        antes = self.existente(anterior)
        with self.assertRaises(ValueError):
            guardrail.adicionar(
                self.raiz, {**REGRA, "nome": "nova", "detector": "nunca-casa"}, PROIBIDO, PERMITIDO
            )
        self.assertEqual(self.arquivo.read_bytes(), antes)

    def test_nome_repetido(self):
        antes = self.existente(REGRA)
        with self.assertRaises(ValueError):
            guardrail.adicionar(self.raiz, REGRA, PROIBIDO, PERMITIDO)
        self.assertEqual(self.arquivo.read_bytes(), antes)

    def test_regra_malformada(self):
        with self.assertRaises(ValueError):
            guardrail.adicionar(self.raiz, {**REGRA, "detector": "[a-"}, PROIBIDO, PERMITIDO)
        self.assertFalse(self.arquivo.exists())

    def test_regra_sem_chave(self):
        regra = {k: v for k, v in REGRA.items() if k != "mensagem"}
        with self.assertRaises(ValueError):
            guardrail.adicionar(self.raiz, regra, PROIBIDO, PERMITIDO)
        self.assertFalse(self.arquivo.exists())

    def test_arquivo_existente_malformado_nao_e_sobrescrito(self):
        self.arquivo.parent.mkdir(parents=True)
        self.arquivo.write_text("{quebrado", encoding="utf-8")
        with self.assertRaises(ValueError):
            guardrail.adicionar(self.raiz, REGRA, PROIBIDO, PERMITIDO)
        self.assertEqual(self.arquivo.read_text(encoding="utf-8"), "{quebrado")


if __name__ == "__main__":
    unittest.main()
