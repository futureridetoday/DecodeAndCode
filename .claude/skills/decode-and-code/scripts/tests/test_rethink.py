#!/usr/bin/env python3
"""Testes de `rethink` — o histórico do `rethink`, plano 0020, tarefa 6.

Projeto sintético em `tempfile`. O oráculo é o da norma, seção *Rethink → O histórico*: `start`
cria o arquivo com o esqueleto se faltar e abre uma seção com o que mudou; `record` acrescenta uma
linha com decisão de vocabulário fechado e recusa, sem escrever, valor fora dele ou motivo vazio
onde ele é exigido.
"""

from __future__ import annotations

import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import lib
import regioes
import rethink

DATA = "2026-11-22"


class _Base(unittest.TestCase):
    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self._tmp.cleanup)
        self.projeto = Path(self._tmp.name)
        self.arquivo = self.projeto / lib.config()["plan_root"] / "system" / "rethink.md"

    def start(self, mudanca="Marca laranja, design divertido.", autor="Pessoa", data=DATA):
        return rethink.start(self.projeto, mudanca, autor, data=data)

    def record(self, camada="guideline", nome="paleta-azul", decisao="arquivado", motivo="Marca laranja."):
        rethink.record(self.projeto, camada, nome, decisao, motivo)

    def texto(self) -> str:
        return self.arquivo.read_text(encoding="utf-8")


class TestStart(_Base):
    def test_cria_o_esqueleto_e_abre_a_secao(self):
        self.assertEqual(self.start(), self.arquivo)
        texto = self.texto()
        self.assertEqual(regioes.ler_campo(self.arquivo, "name"), "rethink")
        self.assertIn(
            f"## {DATA} · Pessoa\n\n**O que mudou:** Marca laranja, design divertido.\n\n"
            "| camada | nome | decisão | motivo |\n|---|---|---|---|\n",
            texto,
        )

    def test_segundo_start_acrescenta_sem_mexer_no_anterior(self):
        self.start()
        self.record()
        antes = self.texto()
        self.start(mudanca="Volta ao azul.", data="2026-12-01")
        texto = self.texto()
        self.assertTrue(texto.startswith(antes))
        self.assertIn("## 2026-12-01 · Pessoa\n\n**O que mudou:** Volta ao azul.", texto)

    def test_recusa_mudanca_ou_autor_vazio_sem_criar_o_arquivo(self):
        for caso, kw in {"mudança": dict(mudanca=" "), "autor": dict(autor="")}.items():
            with self.subTest(caso=caso), self.assertRaises(ValueError):
                self.start(**kw)
        self.assertFalse(self.arquivo.exists())


class TestRecord(_Base):
    def test_acrescenta_a_linha_na_secao_aberta(self):
        self.start()
        self.record()
        self.record(camada="princípio", nome="North star", decisao="editado", motivo="")
        self.assertTrue(
            self.texto().endswith(
                "|---|---|---|---|\n"
                "| guideline | paleta-azul | arquivado | Marca laranja. |\n"
                "| princípio | North star | editado | — |\n"
            ),
            self.texto(),
        )

    def test_cada_decisao_do_vocabulario_e_aceita(self):
        self.start()
        for decisao in rethink.DECISOES:
            with self.subTest(decisao=decisao):
                self.record(decisao=decisao)
        self.assertEqual(self.texto().count("| paleta-azul |"), len(rethink.DECISOES))

    def test_barra_vertical_e_quebra_de_linha_nao_quebram_a_tabela(self):
        self.start()
        self.record(motivo="azul | laranja\nnovo")
        self.assertIn("| azul \\| laranja novo |", self.texto())

    def test_recusas_sem_escrever(self):
        self.start()
        antes = self.texto()
        casos = {
            "camada fora": dict(camada="regra"),
            "decisão fora": dict(decisao="editada"),
            "nome vazio": dict(nome=" "),
            "arquivado sem motivo": dict(decisao="arquivado", motivo=" "),
        }
        for caso, kw in casos.items():
            with self.subTest(caso=caso), self.assertRaises(ValueError):
                self.record(**kw)
        self.assertEqual(self.texto(), antes)

    def test_sem_start_recusa_e_nao_cria_o_arquivo(self):
        with self.assertRaisesRegex(ValueError, "rethink-start"):
            self.record()
        self.assertFalse(self.arquivo.exists())


if __name__ == "__main__":
    unittest.main()
