#!/usr/bin/env python3
"""Testes de `handoff.gerar` — plano 0003.

Duas naturezas, e as duas são necessárias (`L-31` do plano 0001). **Fixture sintética** para o
esqueleto e para os ramos; **o plano `0001` real** para provar que os números vêm de medição e não
de literal — fixture prova o mecanismo, nunca a instância.
"""

from __future__ import annotations

import sys
import tempfile
import unittest
from pathlib import Path
from unittest import mock

sys.path.insert(0, str(Path(__file__).resolve().parent))
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import dc
import fixtures
import handoff
import lib
import numeracao
import porte
import regioes

_DIR_0001 = lib.plan_root() / "model" / "0001-decode-and-code-foundation"

_JULGAMENTO = {
    "fila": "1. `0009-01` — primeira, sem dependência.",
    "pendencias": "Push dos commits locais.",
    "sugestao": "Pela `01`, que destrava as outras.",
}


class _BaseComPlanoSintetico(unittest.TestCase):
    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self._tmp.cleanup)
        self.raiz = Path(self._tmp.name).resolve()

        for alvo, valor in (("plan_root", self.raiz), ("repo_root", self.raiz)):
            patcher = mock.patch.object(lib, alvo, return_value=valor)
            patcher.start()
            self.addCleanup(patcher.stop)

        patcher_cfg = mock.patch.object(
            lib, "_config_path", return_value=self.raiz / "skill" / "config.json"
        )
        patcher_cfg.start()
        self.addCleanup(patcher_cfg.stop)

        self.dir_plano = fixtures.plano(self.raiz, core="builder", nome="exemplo", numero="0009", previstas=2)

    def _gerar(self, **overrides):
        return handoff.gerar(self.dir_plano, **{**_JULGAMENTO, **overrides})


class TestEsqueleto(_BaseComPlanoSintetico):
    def test_grava_handoff_no_diretorio_do_plano(self):
        alvo = self._gerar()

        self.assertEqual(alvo, self.dir_plano / "_handoff.md")
        self.assertTrue(alvo.is_file())

    def test_nome_fica_fora_do_padrao_que_conta_unidades(self):
        """Se casasse `NN-*.md`, o handoff entraria na contagem de `numeracao` e de `porte`."""
        alvo = self._gerar()

        self.assertIsNone(numeracao.PADRAO_ARQUIVO_UNIDADE.match(alvo.name))
        self.assertNotIn(alvo, porte._listar_unidades(self.dir_plano))

    def test_julgamento_recebido_aparece_no_texto(self):
        texto = self._gerar().read_text(encoding="utf-8")

        for parte in _JULGAMENTO.values():
            self.assertIn(parte, texto)

    def test_nomeia_uma_unica_forma_de_executar_cada_unidade(self):
        """`0004-06` e `P-03` — o handoff diz como disparar a unidade, e não sobra comando antigo."""
        texto = self._gerar().read_text(encoding="utf-8")

        self.assertIn("`/decode-and-code:code <unidade>`", texto)
        self.assertNotIn("implement", texto)
        self.assertNotIn("delegate", texto)

    def test_plano_do_formato_1_tambem_recebe_o_esqueleto_do_codex(self):
        """Parte 2.3: um esqueleto só; o do formato 1 citava a norma, que saiu."""
        texto = self._gerar().read_text(encoding="utf-8")

        self.assertNotIn("modelo-dev-units", texto)
        self.assertIn("- *Code*", texto)

    def test_regera_sobrescrevendo_porque_e_projecao(self):
        primeiro = self._gerar(fila="1. `0009-01`").read_text(encoding="utf-8")
        segundo = self._gerar(fila="1. `0009-02`").read_text(encoding="utf-8")

        self.assertIn("0009-02", segundo)
        self.assertNotIn("0009-01", segundo)
        self.assertNotEqual(primeiro, segundo)

    def test_diretorio_sem_plano_levanta_antes_de_escrever(self):
        vazio = self.raiz / "sem-plano"
        vazio.mkdir()

        with self.assertRaises(FileNotFoundError):
            handoff.gerar(vazio, **_JULGAMENTO)
        self.assertFalse((vazio / "_handoff.md").exists())


class TestSituacaoMedida(_BaseComPlanoSintetico):
    def test_situacao_de_cada_unidade_vem_do_disco(self):
        fixtures.unidade(self.dir_plano, nome="01-a.md", unit_id="0009-01", state="verified")
        fixtures.unidade(self.dir_plano, nome="02-b.md", unit_id="0009-02", state="spec")

        texto = self._gerar().read_text(encoding="utf-8")

        self.assertIn("| 0009-01 | verificada |", texto)
        self.assertIn("| 0009-02 | por fazer |", texto)

    def test_a_situacao_muda_quando_o_disco_muda(self):
        """O caso contrário: número que não se move não está sendo medido."""
        antes = self._gerar().read_text(encoding="utf-8")
        fixtures.unidade(self.dir_plano, nome="01-a.md", unit_id="0009-01", state="verified")
        depois = self._gerar().read_text(encoding="utf-8")

        self.assertIn("nenhuma unidade derivada", antes)
        self.assertIn("| 0009-01 | verificada |", depois)

    def test_git_ausente_nao_levanta_e_diz_desconhecido(self):
        with mock.patch.object(handoff.subprocess, "run", side_effect=FileNotFoundError):
            texto = self._gerar().read_text(encoding="utf-8")

        self.assertIn("`desconhecido`", texto)


class TestContraOPlanoReal(unittest.TestCase):
    """`L-31` — só o caso real prova que a situação vem de medição, e não de literal."""

    def test_situacao_bate_com_o_state_de_cada_unidade(self):
        with tempfile.TemporaryDirectory() as tmp:
            copia = Path(tmp) / _DIR_0001.name
            copia.mkdir()
            for arquivo in _DIR_0001.glob("*.md"):
                (copia / arquivo.name).write_text(arquivo.read_text(encoding="utf-8"), encoding="utf-8")

            texto = handoff.gerar(copia, **_JULGAMENTO).read_text(encoding="utf-8")

            unidades = porte._listar_unidades(copia)
            self.assertTrue(unidades)
            for unidade in unidades:
                unit_id = (regioes.ler_campo(unidade, "unit_id") or "").strip(" \"'")
                state = (regioes.ler_campo(unidade, "state") or "").strip()
                situacao = "verificada" if state == "verified" else "por fazer"
                with self.subTest(unidade=unit_id):
                    self.assertIn(f"| {unit_id} | {situacao} |", texto)


class TestContratoComOSkillDoDerive(unittest.TestCase):
    """O `derive` manda o `handoff` ler três seções do stdin; o `dc.py` as lê pelos títulos de `_SECOES_HANDOFF`."""

    def test_skill_do_derive_cita_cada_titulo_que_o_dc_le(self):
        corpo = (lib.repo_root() / ".claude" / "skills" / "derive" / "SKILL.md").read_text(encoding="utf-8")
        for titulo in dc._SECOES_HANDOFF:
            with self.subTest(titulo=titulo):
                self.assertIn(f"`{titulo}`", corpo)


if __name__ == "__main__":
    unittest.main()
