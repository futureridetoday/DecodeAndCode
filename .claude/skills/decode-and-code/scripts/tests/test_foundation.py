#!/usr/bin/env python3
"""Testes da foundation — subparte 2.2.11 do redesign (K-10).

Codex, *Foundation* e *Mapa de recursos do projeto*: o padrão de código e o índice dos recursos, em
`<plan_root>/system/foundation.md`, gravados um por vez; o mapa guarda o nome e os campos, nunca o
conteúdo do recurso.
"""

from __future__ import annotations

import sys
import tempfile
import unittest
from pathlib import Path
from unittest import mock

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import foundation
import lib
import regioes

RECURSO = {"nome": "ui-builder", "tipo": "skill", "etapa": "code", "so_usuario": "não",
           "escopo": "projeto", "permissao": "sim"}


class TestFoundation(unittest.TestCase):
    def setUp(self) -> None:
        tmp = tempfile.TemporaryDirectory()
        self.addCleanup(tmp.cleanup)
        self.raiz = Path(tmp.name).resolve() / "meu-projeto"
        (self.raiz / "docs" / "plan" / "system").mkdir(parents=True)
        for nome, valor in (("plan_root", self.raiz / "docs" / "plan"), ("repo_root", self.raiz)):
            p = mock.patch.object(lib, nome, return_value=valor)
            p.start()
            self.addCleanup(p.stop)

    def test_iniciar_cria_uma_vez_na_raiz_dos_planos(self) -> None:
        alvo = foundation.iniciar()
        self.assertEqual(alvo, self.raiz / "docs" / "plan" / "system" / "foundation.md")
        self.assertIn("project: meu-projeto", alvo.read_text(encoding="utf-8"))
        self.assertIsNone(foundation.iniciar())

    def test_padrao_de_codigo_vai_para_a_regiao(self) -> None:
        self.assertTrue(foundation.escrever_padrao("ruff com linha de 100.\n"))
        self.assertEqual(regioes.ler_regiao(foundation.caminho(), "padrao"), "\nruff com linha de 100.\n")
        self.assertFalse(foundation.escrever_padrao("ruff com linha de 100."))

    def test_padrao_vazio_recusa(self) -> None:
        with self.assertRaises(ValueError):
            foundation.escrever_padrao("  ")

    def test_recurso_entra_e_atualiza_pelo_nome(self) -> None:
        foundation.registrar_recurso(RECURSO)
        foundation.registrar_recurso({**RECURSO, "permissao": "não"})
        self.assertEqual(foundation.mapa(), [{**RECURSO, "permissao": "não"}])

    def test_recurso_fora_do_vocabulario_recusa_sem_escrever(self) -> None:
        for campo, valor in (("etapa", "sempre"), ("escopo", "time"), ("tipo", "plugin"), ("permissao", "talvez")):
            with self.subTest(campo=campo):
                with self.assertRaises(ValueError):
                    foundation.registrar_recurso({**RECURSO, campo: valor})
        self.assertFalse(foundation.caminho().exists())

    def test_recurso_incompleto_recusa(self) -> None:
        with self.assertRaisesRegex(ValueError, "permissao"):
            foundation.registrar_recurso({k: v for k, v in RECURSO.items() if k != "permissao"})

    def test_retirar(self) -> None:
        foundation.registrar_recurso(RECURSO)
        foundation.registrar_recurso({**RECURSO, "nome": "deploy", "tipo": "command", "so_usuario": "sim"})
        foundation.retirar_recurso("ui-builder")
        self.assertEqual([e["nome"] for e in foundation.mapa()], ["deploy"])
        with self.assertRaises(ValueError):
            foundation.retirar_recurso("ui-builder")

    def test_mapa_vazio_sem_foundation(self) -> None:
        self.assertEqual(foundation.mapa(), [])


if __name__ == "__main__":
    unittest.main()
