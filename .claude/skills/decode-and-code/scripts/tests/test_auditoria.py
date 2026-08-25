#!/usr/bin/env python3
"""Testes de `rules.auditar_arvore` e `activation_notice.relatorio` — unidade 0001-11.

A árvore real deste repositório é o critério de aceite: `auditar_arvore()` aprova sem ressalva.
Cada recusa da tabela dispara isoladamente contra árvore sintética montada em
`tempfile.TemporaryDirectory()`, com `lib.repo_root()` mockado — mesmo padrão de
`test_config.py`. O caso do subdiretório reproduz a forma exata da `L-26`, `rules/_off/<nome>.md`.
Os três sinais de `relatorio` são exercitados contra logs sintéticos de `fixtures.log_ativacao()`.
"""

from __future__ import annotations

import sys
import tempfile
import unittest
from pathlib import Path
from unittest import mock

sys.path.insert(0, str(Path(__file__).resolve().parent))
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import activation_notice
import fixtures
import lib
import rules


class TestAuditarArvoreReal(unittest.TestCase):
    """`.claude/rules/` e `.claude/rules-off/` deste repositório são o critério de aceite."""

    def test_arvore_real_aprova(self):
        self.assertEqual(rules.auditar_arvore(), [])


class TestAuditarArvoreSintetica(unittest.TestCase):
    """Contra árvore sintética — cada teste dispara uma recusa da tabela por vez."""

    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self._tmp.cleanup)
        self.raiz = Path(self._tmp.name)
        self.dir_rules = self.raiz / ".claude" / "rules"
        self.dir_rules.mkdir(parents=True)

        patcher = mock.patch.object(lib, "repo_root", return_value=self.raiz)
        patcher.start()
        self.addCleanup(patcher.stop)

    def test_arvore_vazia_aprova(self):
        self.assertEqual(rules.auditar_arvore(), [])

    def test_md_em_subdiretorio_de_rules_e_recusado(self):
        # Reproduz a forma exata da L-26: rules/_off/<guideline>.md.
        fixtures.rule(self.dir_rules / "_off", paths=["**/*.py"])
        problemas = rules.auditar_arvore()
        self.assertTrue(any("subdiretório" in p and "L-26" in p for p in problemas), problemas)

    def test_rule_malformada_em_rules_e_recusada(self):
        (self.dir_rules / "quebrada.md").write_text("# sem frontmatter\n", encoding="utf-8")
        problemas = rules.auditar_arvore()
        self.assertTrue(any("quebrada.md" in p for p in problemas), problemas)

    def test_guideline_quebrada_em_rules_off_e_recusada(self):
        dir_off = self.raiz / ".claude" / "rules-off"
        fixtures.rule(dir_off, nome="quebrada", paths=None)  # sem paths — reprova lint_guideline
        problemas = rules.auditar_arvore()
        self.assertTrue(any("quebrada.md" in p for p in problemas), problemas)

    def test_rule_valida_em_rules_e_guideline_valida_em_rules_off_aprovam(self):
        fixtures.rule(self.dir_rules, nome="principio", paths=None)
        (self.raiz / "alvo.py").write_text("# alvo\n", encoding="utf-8")
        dir_off = self.raiz / ".claude" / "rules-off"
        fixtures.rule(dir_off, nome="desligada", paths=["*.py"])
        self.assertEqual(rules.auditar_arvore(), [])


class TestRelatorioLogInexistente(unittest.TestCase):
    def test_levanta_file_not_found_error(self):
        with tempfile.TemporaryDirectory() as tmp:
            alvo = Path(tmp) / "nao-existe.log"
            with self.assertRaises(FileNotFoundError):
                activation_notice.relatorio(alvo)


class TestRelatorioLinhaIlegivel(unittest.TestCase):
    def test_linha_ilegivel_entra_marcada_sem_derrubar_a_leitura(self):
        with tempfile.TemporaryDirectory() as tmp:
            log = Path(tmp) / "sessao.log"
            log.write_text("isto não é uma linha de log\n", encoding="utf-8")
            linhas = activation_notice.relatorio(log)
            self.assertEqual(len(linhas), 1)
            self.assertIn("ilegível", linhas[0])


class TestRelatorioSinais(unittest.TestCase):
    """Um log sintético por sinal — os três casos da segunda tabela da unidade."""

    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self._tmp.cleanup)
        self.raiz = Path(self._tmp.name)

        patcher = mock.patch.object(lib, "repo_root", return_value=self.raiz)
        patcher.start()
        self.addCleanup(patcher.stop)

    def test_rule_com_paths_carregada_por_session_start_e_sinalizada(self):
        alvo = fixtures.rule(self.raiz, nome="escopo", paths=["**/*.py"])
        log = fixtures.log_ativacao(self.raiz, entradas=[(str(alvo), "session_start")])
        linhas = activation_notice.relatorio(log)
        self.assertEqual(len(linhas), 1)
        self.assertIn("session_start", linhas[0])
        self.assertIn("escopo não respeitado", linhas[0])

    def test_caminho_sob_rules_off_e_sinalizado(self):
        dir_off = self.raiz / ".claude" / "rules-off"
        alvo = fixtures.rule(dir_off, nome="desligada", paths=["**/*.py"])
        log = fixtures.log_ativacao(self.raiz, entradas=[(str(alvo), "path_glob_match")])
        linhas = activation_notice.relatorio(log)
        self.assertEqual(len(linhas), 1)
        self.assertIn("rules-off", linhas[0])
        self.assertIn("L-26", linhas[0])

    def test_caminho_em_subdiretorio_de_rules_e_sinalizado(self):
        """A forma **histórica** da `L-26`, e a que motivou esta unidade.

        `auditar_arvore` pega o subdiretório estruturalmente, mas só quando a suíte roda. Em
        sessão, quem vê é o relatório — e a primeira versão dele dizia `ok` para exatamente esta
        linha, conferida contra o log real da falha em 2026-08-25.
        """
        sub = self.raiz / ".claude" / "rules" / "_off"
        alvo = fixtures.rule(sub, nome="reintroduzida", paths=["**/*.py"])
        log = fixtures.log_ativacao(self.raiz, entradas=[(str(alvo), "path_glob_match")])
        linhas = activation_notice.relatorio(log)
        self.assertEqual(len(linhas), 1)
        self.assertIn("subdiretório", linhas[0])
        self.assertIn("L-26", linhas[0])
        self.assertNotIn("— ok", linhas[0])

    def test_duas_rules_que_casam_o_mesmo_arquivo_colidem(self):
        (self.raiz / "alvo.py").write_text("# alvo\n", encoding="utf-8")
        a = fixtures.rule(self.raiz, nome="rule-a", paths=["*.py"])
        b = fixtures.rule(self.raiz, nome="rule-b", paths=["*.py"])
        log = fixtures.log_ativacao(
            self.raiz, entradas=[(str(a), "path_glob_match"), (str(b), "path_glob_match")]
        )
        linhas = activation_notice.relatorio(log)
        self.assertEqual(len(linhas), 2)
        self.assertTrue(all("L-05" in linha for linha in linhas), linhas)

    def test_rule_sem_conflito_carregada_por_path_glob_match_fica_ok(self):
        alvo = fixtures.rule(self.raiz, nome="normal", paths=["**/*.py"])
        log = fixtures.log_ativacao(self.raiz, entradas=[(str(alvo), "path_glob_match")])
        linhas = activation_notice.relatorio(log)
        self.assertTrue(linhas[0].endswith("— ok"), linhas[0])

    def test_rule_sem_paths_carregada_por_session_start_fica_ok(self):
        alvo = fixtures.rule(self.raiz, nome="principio", paths=None)
        log = fixtures.log_ativacao(self.raiz, entradas=[(str(alvo), "session_start")])
        linhas = activation_notice.relatorio(log)
        self.assertTrue(linhas[0].endswith("— ok"), linhas[0])


if __name__ == "__main__":
    unittest.main()
