#!/usr/bin/env python3
"""Testes de nomenclatura e colisão — unidade 0002-03.

Nomes reais do repositório servem de caso válido: `dev-units` é o módulo
deste próprio plano, `evolucao-tools` é o exemplo do critério de aceite da
unidade. Para colisão, a árvore é toda temporária — `lib.plan_root` é
substituído por mock, nunca se depende do estado real de `docs/plan/`.
"""

from __future__ import annotations

import sys
import tempfile
import unittest
from pathlib import Path
from unittest import mock

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import lib
import nomenclatura


class TestValidarNomeCasosValidos(unittest.TestCase):
    """Nomes reais do repositório e da norma — lista vazia esperada."""

    def test_evolucao_tools_e_valido(self):
        # Critério de aceite da unidade.
        self.assertEqual(nomenclatura.validar_nome("evolucao-tools"), [])

    def test_dev_units_e_valido(self):
        # Nome antigo da skill, citado na norma como exemplo — sintaticamente válido.
        self.assertEqual(nomenclatura.validar_nome("dev-units"), [])

    def test_outros_exemplos_da_norma(self):
        for nome in (
            "modelo-dev-units",
            "comando-new-project",
            "login-obrigatorio",
            "evolucao-tools-l3",
        ):
            self.assertEqual(nomenclatura.validar_nome(nome), [], nome)


class TestValidarNomeRegras(unittest.TestCase):
    """Cada caso isola uma única regra violada."""

    def _motivo_unico(self, nome: str) -> str:
        motivos = nomenclatura.validar_nome(nome)
        self.assertEqual(len(motivos), 1, motivos)
        return motivos[0]

    def test_recusa_caractere_fora_do_alfabeto(self):
        motivo = self._motivo_unico("nome-Invalido-aqui")
        self.assertIn("caractere", motivo)

    def test_recusa_hifen_inicial(self):
        motivo = self._motivo_unico("-nome-valido")
        self.assertIn("hífen inicial", motivo)

    def test_recusa_hifen_final(self):
        motivo = self._motivo_unico("nome-valido-")
        self.assertIn("hífen final", motivo)

    def test_recusa_hifen_consecutivo(self):
        motivo = self._motivo_unico("nome--valido")
        self.assertIn("hífen consecutivo", motivo)

    def test_recusa_mais_de_64_caracteres(self):
        nome = ("a" * 40) + "-" + ("b" * 30)
        self.assertEqual(len(nome), 71)
        motivo = self._motivo_unico(nome)
        self.assertIn("64", motivo)

    def test_recusa_menos_de_2_tokens(self):
        motivo = self._motivo_unico("sozinho")
        self.assertIn("2 a 5", motivo)

    def test_recusa_mais_de_5_tokens(self):
        motivo = self._motivo_unico("a-b-c-g-h-i")
        self.assertIn("2 a 5", motivo)

    def test_recusa_conectivo_isolado(self):
        motivo = self._motivo_unico("evolucao-de-tools")
        self.assertIn("conectivo", motivo)

    def test_recusa_prefixo_numerico(self):
        motivo = self._motivo_unico("0001-evolucao-tools")
        self.assertIn("prefixo numérico", motivo)

    def test_caso_do_criterio_de_aceite_acumula_dois_motivos(self):
        # validar_nome("0001-Plano_De-Teste") — critério de aceite da unidade:
        # um motivo por regra violada, não apenas o primeiro.
        motivos = nomenclatura.validar_nome("0001-Plano_De-Teste")
        self.assertEqual(len(motivos), 2, motivos)
        self.assertTrue(any("caractere" in m for m in motivos), motivos)
        self.assertTrue(any("prefixo numérico" in m for m in motivos), motivos)


class TestValidarNomeNuncaLevanta(unittest.TestCase):
    def test_nomes_patologicos_nao_levantam(self):
        for nome in ("", "-", "--", "a" * 100, "-a-b-c-d-e-f-"):
            try:
                nomenclatura.validar_nome(nome)
            except Exception as exc:  # noqa: BLE001 — é o próprio contrato sendo testado
                self.fail(f"validar_nome({nome!r}) levantou {exc!r}")


class TestHaColisao(unittest.TestCase):
    """Árvore inteiramente temporária: `lib.plan_root` substituído por mock,
    nunca se depende do estado real de docs/plan/.
    """

    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self._tmp.cleanup)
        self.raiz = Path(self._tmp.name).resolve()

        (self.raiz / "_inbox").mkdir()
        (self.raiz / "hub" / "0001-mcp").mkdir(parents=True)
        (self.raiz / "hub" / "0001-mcp" / "01-handler-auth.md").write_text(
            "x", encoding="utf-8"
        )
        (self.raiz / "hub" / "0002-outro-modulo").mkdir()

        patcher = mock.patch.object(lib, "plan_root", return_value=self.raiz)
        patcher.start()
        self.addCleanup(patcher.stop)

    def test_colide_com_modulo_ja_aprovado(self):
        colisao = nomenclatura.ha_colisao("mcp", "hub")
        self.assertEqual(colisao, self.raiz / "hub" / "0001-mcp")

    def test_colide_com_plano_ja_proposto_no_inbox(self):
        (self.raiz / "_inbox" / "evolucao-tools.md").write_text("x", encoding="utf-8")
        colisao = nomenclatura.ha_colisao("evolucao-tools", "hub")
        self.assertEqual(colisao, self.raiz / "_inbox" / "evolucao-tools.md")

    def test_nome_de_plano_livre_devolve_none(self):
        self.assertIsNone(nomenclatura.ha_colisao("nome-completamente-livre", "hub"))

    def test_colide_com_unidade_ja_existente_no_modulo(self):
        colisao = nomenclatura.ha_colisao("handler-auth", "hub", module="mcp")
        self.assertEqual(
            colisao, self.raiz / "hub" / "0001-mcp" / "01-handler-auth.md"
        )

    def test_nome_de_unidade_livre_devolve_none(self):
        self.assertIsNone(
            nomenclatura.ha_colisao("nome-completamente-livre", "hub", module="mcp")
        )

    def test_modulo_inexistente_devolve_none(self):
        self.assertIsNone(
            nomenclatura.ha_colisao("qualquer-coisa", "hub", module="nao-existe")
        )

    def test_core_inexistente_levanta_value_error(self):
        with self.assertRaises(ValueError):
            nomenclatura.ha_colisao("qualquer-coisa", "core-que-nao-existe")


if __name__ == "__main__":
    unittest.main()
