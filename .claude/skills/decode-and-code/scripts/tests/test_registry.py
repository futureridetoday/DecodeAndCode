#!/usr/bin/env python3
"""Testes de `registry.listar/ligar/desligar` — unidade 0001-10.

Duas frentes. `TestGateSintetico*` roda contra árvore em `tempfile.TemporaryDirectory()`, com
`lib.repo_root` mockado — mesmo padrão de `test_scaffold.py` e `test_backlog.py`. `TestGuidelineReal`
roda sem mock nenhum, contra `.claude/rules/scripts.md` de verdade, a guideline que a unidade `09`
entregou — é o par do critério de aceite que exige desligar e religar a guideline real. A restauração
em `addCleanup` garante que uma falha no meio do teste não deixe a guideline real fora do lugar.
"""

from __future__ import annotations

import sys
import tempfile
import unittest
from pathlib import Path
from unittest import mock

sys.path.insert(0, str(Path(__file__).resolve().parent))
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import fixtures
import lib
import registry
import rules


class _BaseComRulesSinteticas(unittest.TestCase):
    """Monta `raiz/.claude/rules/` com uma guideline e um princípio — nenhum dos dois desligado."""

    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self._tmp.cleanup)
        self.raiz = Path(self._tmp.name).resolve()

        self.dir_rules = self.raiz / ".claude" / "rules"
        self.dir_off = self.dir_rules.parent / "rules-off"

        # "**/*.md" casa a própria fixture — lint_guideline exige match real contra o disco, e o
        # tempdir mockado como repo_root não tem nenhum .py para "**/*.py" casar.
        self.guideline = fixtures.rule(
            self.dir_rules, nome="minha-guideline", paths=["**/*.md"]
        )
        self.principio = fixtures.rule(self.dir_rules, nome="meu-principio", paths=None)
        self.bytes_guideline = self.guideline.read_bytes()

        patcher = mock.patch.object(lib, "repo_root", return_value=self.raiz)
        patcher.start()
        self.addCleanup(patcher.stop)

    def _arquivos(self) -> dict[str, bytes]:
        """Snapshot de todo arquivo sob `raiz/.claude/rules/` — caminho relativo -> bytes."""
        return {
            str(p.relative_to(self.dir_rules)): p.read_bytes()
            for p in self.dir_rules.rglob("*")
            if p.is_file()
        }


class TestListar(_BaseComRulesSinteticas):
    def test_lista_so_guideline_nao_principio(self):
        entradas = {e["nome"]: e for e in registry.listar()}
        self.assertIn("minha-guideline", entradas)
        self.assertNotIn("meu-principio", entradas)

    def test_guideline_recem_criada_aparece_ligada_e_nao_divergente(self):
        entradas = {e["nome"]: e for e in registry.listar()}
        self.assertEqual(entradas["minha-guideline"]["estado"], "ligada")
        self.assertFalse(entradas["minha-guideline"]["divergente"])

    def test_sem_off_nao_quebra(self):
        self.assertFalse(self.dir_off.is_dir())
        self.assertEqual(registry.listar(), [{"nome": "minha-guideline", "estado": "ligada", "divergente": False}])

    def test_listar_deriva_do_disco_e_reporta_divergencia_do_registry(self):
        # Transição real, para o registry.json gravar "ligada".
        registry.desligar("minha-guideline")
        registry.ligar("minha-guideline")

        # Movida à mão, contornando o registry — o registry.json continua dizendo "ligada".
        self.dir_off.mkdir(parents=True, exist_ok=True)
        self.guideline.rename(self.dir_off / self.guideline.name)

        entradas = {e["nome"]: e for e in registry.listar()}
        self.assertEqual(entradas["minha-guideline"]["estado"], "desligada")
        self.assertTrue(entradas["minha-guideline"]["divergente"])


class TestDesligarLigar(_BaseComRulesSinteticas):
    def test_desligar_move_e_preserva_bytes(self):
        destino = registry.desligar("minha-guideline")
        self.assertEqual(destino, self.dir_off / "minha-guideline.md")
        self.assertFalse((self.dir_rules / "minha-guideline.md").exists())
        self.assertTrue(destino.is_file())
        self.assertEqual(destino.read_bytes(), self.bytes_guideline)

    def test_ligar_devolve_ao_lugar_com_bytes_identicos(self):
        registry.desligar("minha-guideline")
        destino = registry.ligar("minha-guideline")
        self.assertEqual(destino, self.dir_rules / "minha-guideline.md")
        self.assertFalse((self.dir_off / "minha-guideline.md").exists())
        self.assertEqual(destino.read_bytes(), self.bytes_guideline)

    def test_ligar_ja_ligado_e_noop_silencioso(self):
        antes = self._arquivos()
        destino = registry.ligar("minha-guideline")
        self.assertEqual(destino, self.guideline)
        self.assertEqual(self._arquivos(), antes)
        self.assertFalse((self.dir_rules / "registry.json").exists())

    def test_desligar_ja_desligado_e_noop_silencioso(self):
        registry.desligar("minha-guideline")
        antes = self._arquivos()
        destino = registry.desligar("minha-guideline")
        self.assertEqual(destino, self.dir_off / "minha-guideline.md")
        self.assertEqual(self._arquivos(), antes)

    def test_desligar_sobre_principio_recusa_e_explica(self):
        antes = self._arquivos()
        with self.assertRaises(ValueError) as ctx:
            registry.desligar("meu-principio")
        mensagem = str(ctx.exception)
        self.assertIn("princípio", mensagem)
        self.assertIn("paths", mensagem)
        self.assertEqual(self._arquivos(), antes)

    def test_nome_desconhecido_levanta_valueerror_nomeando_o_que_existe(self):
        antes = self._arquivos()
        with self.assertRaises(ValueError) as ctx:
            registry.desligar("nao-existe")
        mensagem = str(ctx.exception)
        self.assertIn("minha-guideline", mensagem)
        self.assertIn("meu-principio", mensagem)
        self.assertEqual(self._arquivos(), antes)

    def test_ligar_nome_desconhecido_tambem_recusa(self):
        with self.assertRaises(ValueError):
            registry.ligar("nao-existe")

    def test_registry_json_grava_estado_e_data_apos_transicao_real(self):
        registry.desligar("minha-guideline")
        conteudo = (self.dir_rules / "registry.json").read_text(encoding="utf-8")
        self.assertIn('"minha-guideline"', conteudo)
        self.assertIn('"desligada"', conteudo)
        self.assertIn('"atualizado_em"', conteudo)

    def test_religa_e_lint_guideline_continua_limpo(self):
        registry.desligar("minha-guideline")
        destino = registry.ligar("minha-guideline")
        self.assertEqual(rules.lint_guideline(destino), [])


class TestGuidelineReal(unittest.TestCase):
    """Par do critério de aceite: desligar e religar `.claude/rules/scripts.md`, a guideline da `09`."""

    def setUp(self):
        self.ligada = lib.repo_root() / ".claude" / "rules" / "scripts.md"
        self.off = lib.repo_root() / ".claude" / "rules-off" / "scripts.md"
        self.original = self.ligada.read_bytes()
        self.addCleanup(self._restaurar)

    def _restaurar(self):
        if self.off.is_file() and not self.ligada.is_file():
            self.off.rename(self.ligada)
        if self.ligada.is_file() and self.ligada.read_bytes() != self.original:
            self.ligada.write_bytes(self.original)

    def test_desligar_e_ligar_a_guideline_real_mantem_lint_limpo(self):
        destino_off = registry.desligar("scripts")
        self.assertTrue(destino_off.is_file())
        self.assertFalse(self.ligada.is_file())
        self.assertEqual(destino_off.read_bytes(), self.original)

        destino_ligada = registry.ligar("scripts")
        self.assertTrue(destino_ligada.is_file())
        self.assertFalse(destino_off.is_file())
        self.assertEqual(destino_ligada.read_bytes(), self.original)
        self.assertEqual(rules.lint_guideline(destino_ligada), [])


if __name__ == "__main__":
    unittest.main()
