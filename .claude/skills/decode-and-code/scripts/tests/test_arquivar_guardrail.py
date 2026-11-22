#!/usr/bin/env python3
"""Testes de arquivar, restaurar e substituir guardrail — plano 0020, tarefa 4.

Raiz sintética passada explicitamente. O oráculo é o da norma, *Camada normativa → Editar e
arquivar*: arquivar move a regra com três campos e o hook deixa de negar o caso dela; o nome
arquivado fica reservado; `restore` só devolve a regra provada por um par novo; `replace` prova a
regra nova pelo par antes de trocar.
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

DATA = "2026-11-22"
AUTOR = "Pessoa Teste"
REGRA = {
    "nome": "cor-fixa",
    "ferramenta": "^(Write|Edit)$",
    "detector": "#0000FF",
    "mensagem": "Cor vem do tema, nunca fixa.",
}
OUTRA = {**REGRA, "nome": "sem-print", "detector": "print\\(", "mensagem": "Use o logger."}
PROIBIDO = {"tool_name": "Write", "tool_input": {"content": "cor = '#0000FF'"}}
PERMITIDO = {"tool_name": "Write", "tool_input": {"content": "cor = tema.primaria"}}


class _Base(unittest.TestCase):
    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self._tmp.cleanup)
        self.raiz = Path(self._tmp.name)
        self.arquivo = self.raiz / ".claude" / "guardrails.json"
        self.arquivo_morto = self.raiz / ".claude" / "archive" / "guardrails.json"

    def regras(self, arquivo: Path | None = None) -> list[dict]:
        return json.loads((arquivo or self.arquivo).read_text(encoding="utf-8"))["regras"]

    def adicionar(self, regra=REGRA, proibido=PROIBIDO, permitido=PERMITIDO, **kw):
        return guardrail.adicionar(self.raiz, regra, proibido, permitido, **kw)

    def arquivar(self, nome="cor-fixa", motivo="Marca laranja."):
        return guardrail.archive(self.raiz, nome, motivo, AUTOR, data=DATA)

    def nega(self, payload: dict) -> str | None:
        decisao, aviso = guardrail.decidir(json.dumps(payload), self.arquivo)
        self.assertIsNone(aviso)
        return (decisao or {}).get("regra")


class TestArquivar(_Base):
    def test_regra_sai_e_entra_no_arquivo_com_os_tres_campos(self):
        self.adicionar()
        self.adicionar(OUTRA, {"tool_name": "Write", "tool_input": {"content": "print(1)"}})

        self.assertEqual(self.arquivar(), self.arquivo_morto)

        self.assertEqual(self.regras(), [OUTRA])
        self.assertEqual(
            self.regras(self.arquivo_morto),
            [{**REGRA, "archived_at": DATA, "archived_by": AUTOR, "reason": "Marca laranja."}],
        )
        self.assertEqual(guardrail.lint_arquivo(self.arquivo), [])

    def test_o_hook_deixa_de_negar_o_caso_dela(self):
        self.adicionar()
        self.assertEqual(self.nega(PROIBIDO), "cor-fixa")
        self.arquivar()
        self.assertIsNone(self.nega(PROIBIDO))

    def test_recusas_sem_tocar_o_disco(self):
        self.adicionar()
        antes = self.arquivo.read_bytes()
        for caso, kw in {"desconhecida": dict(nome="outra"), "motivo vazio": dict(motivo=" ")}.items():
            with self.subTest(caso=caso), self.assertRaises(ValueError):
                self.arquivar(**kw)
        with self.assertRaises(ValueError):
            guardrail.archive(self.raiz, "cor-fixa", "Motivo.", "", data=DATA)
        self.assertEqual(self.arquivo.read_bytes(), antes)
        self.assertFalse(self.arquivo_morto.exists())


class TestNomeReservado(_Base):
    def test_adicionar_recusa_nome_arquivado(self):
        self.adicionar()
        self.arquivar()
        antes = self.arquivo.read_bytes()
        with self.assertRaisesRegex(ValueError, "arquivada"):
            self.adicionar()
        self.assertEqual(self.arquivo.read_bytes(), antes)


class TestRestaurar(_Base):
    def test_volta_com_o_mesmo_nome_sem_os_campos_e_volta_a_negar(self):
        self.adicionar()
        self.arquivar()
        novo_proibido = {"tool_name": "Edit", "tool_input": {"new_string": "fundo = '#0000FF'"}}

        self.assertEqual(guardrail.restore(self.raiz, "cor-fixa", novo_proibido, PERMITIDO), self.arquivo)

        self.assertEqual(self.regras(), [REGRA])
        self.assertEqual(self.regras(self.arquivo_morto), [])
        self.assertEqual(self.nega(PROIBIDO), "cor-fixa")

    def test_par_que_nao_prova_e_recusado_e_o_arquivo_fica_como_estava(self):
        self.adicionar()
        self.arquivar()
        antes = self.arquivo_morto.read_bytes()
        casos = {
            "não nega o proibido": (PERMITIDO, PERMITIDO),
            "nega o permitido": (PROIBIDO, PROIBIDO),
        }
        for caso, (proibido, permitido) in casos.items():
            with self.subTest(caso=caso), self.assertRaises(ValueError):
                guardrail.restore(self.raiz, "cor-fixa", proibido, permitido)
        self.assertEqual(self.arquivo_morto.read_bytes(), antes)
        self.assertEqual(self.regras(), [])

    def test_recusa_a_que_nao_esta_arquivada(self):
        with self.assertRaisesRegex(ValueError, "não está arquivada"):
            guardrail.restore(self.raiz, "cor-fixa", PROIBIDO, PERMITIDO)


class TestSubstituir(_Base):
    def test_troca_no_mesmo_lugar_depois_de_provar(self):
        self.adicionar()
        self.adicionar(OUTRA, {"tool_name": "Write", "tool_input": {"content": "print(1)"}})
        nova = {**REGRA, "detector": "#(0000FF|FF8800)", "mensagem": "Cor vem do tema laranja."}
        proibido = {"tool_name": "Write", "tool_input": {"content": "cor = '#FF8800'"}}

        self.adicionar(nova, proibido, replace=True)

        self.assertEqual(self.regras(), [nova, OUTRA])
        self.assertEqual(self.nega(proibido), "cor-fixa")

    def test_regra_nova_que_nao_prova_deixa_a_antiga_intacta(self):
        self.adicionar()
        antes = self.arquivo.read_bytes()
        casos = {
            "não nega o proibido": ({**REGRA, "detector": "nunca-casa"}, {}),
            "inexistente": ({**REGRA, "nome": "outra"}, {}),
        }
        for caso, (regra, kw) in casos.items():
            with self.subTest(caso=caso), self.assertRaises(ValueError):
                self.adicionar(regra, replace=True, **kw)
        self.assertEqual(self.arquivo.read_bytes(), antes)


if __name__ == "__main__":
    unittest.main()
