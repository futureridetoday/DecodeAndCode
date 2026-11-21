#!/usr/bin/env python3
"""Testes de `rules.casa_caminho` e `normas.aplicaveis` — plano 0017, `L-03` da revisão.

As guidelines são gravadas pelo `rules.criar_guideline`, não à mão: o teste só pode provar padrões
que o setup consegue gerar (`L-02` do plano). A exceção é o padrão fora do subconjunto, que o
escritor recusa e por isso só existe escrito à mão.
"""

from __future__ import annotations

import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import fixtures
import lint_unidade
import normas
import rules


class TestCasaCaminho(unittest.TestCase):
    def test_pasta_inteira(self):
        for caminho in ("src/components/Botao.tsx", "src/components/a/b/c.tsx"):
            with self.subTest(caminho=caminho):
                self.assertTrue(rules.casa_caminho("src/components/**/*", caminho))
        self.assertFalse(rules.casa_caminho("src/components/**/*", "src/Botao.tsx"))
        self.assertFalse(rules.casa_caminho("src/components/**/*", "lib/src/components/x.tsx"))

    def test_arquivo_em_qualquer_nivel(self):
        self.assertTrue(rules.casa_caminho("**/tailwind.config.ts", "tailwind.config.ts"))
        self.assertTrue(rules.casa_caminho("**/tailwind.config.ts", "apps/web/tailwind.config.ts"))
        self.assertFalse(rules.casa_caminho("**/tailwind.config.ts", "tailwind.config.js"))

    def test_curinga_simples_nao_atravessa_barra(self):
        self.assertTrue(rules.casa_caminho("src/*.ts", "src/a.ts"))
        self.assertFalse(rules.casa_caminho("src/*.ts", "src/a/b.ts"))


class TestAplicaveis(unittest.TestCase):
    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self._tmp.cleanup)
        self.raiz = Path(self._tmp.name).resolve()
        (self.raiz / "src" / "components").mkdir(parents=True)
        (self.raiz / "src" / "components" / "Button.tsx").write_text("x", encoding="utf-8")
        (self.raiz / "docs").mkdir()
        (self.raiz / "docs" / "guia.md").write_text("x", encoding="utf-8")
        rules.criar_guideline(self.raiz, "ui-ponte", "Vale em src/components.", ["src/components/**/*"],
                              "# Interface\n\nPassa pela skill `ui-builder`.")
        rules.criar_guideline(self.raiz, "docs-tom", "Vale em docs.", ["docs/**/*"], "# Tom\n\nTexto direto.")
        self.dir_plano = self.raiz / "docs" / "plan" / "app" / "0001-add-card"
        self.unidade = fixtures.unidade(self.dir_plano, nome="01-card.md", unit_id="0001-01")
        self.trocar("| `caminho/para/arquivo.py` | Criar |", "| `src/components/Botao.tsx:12` | Criar |")

    def trocar(self, antes: str, depois: str) -> None:
        texto = self.unidade.read_text(encoding="utf-8")
        self.assertIn(antes, texto)
        self.unidade.write_text(texto.replace(antes, depois), encoding="utf-8")

    def test_devolve_a_ponte_e_nao_a_outra_com_arquivo_que_nao_existe(self):
        self.assertFalse((self.raiz / "src" / "components" / "Botao.tsx").exists())
        achadas = normas.aplicaveis(self.unidade, self.raiz)
        self.assertEqual([a.nome for a in achadas], ["ui-ponte"])
        self.assertEqual(
            achadas[0].linha,
            "| Interface | [ui-ponte](../../../../.claude/rules/ui-ponte.md), seção *Interface* |",
        )

    def test_a_linha_devolvida_passa_no_lint_e_resolve(self):
        linha = normas.aplicaveis(self.unidade, self.raiz)[0].linha
        self.trocar("| Norma | Onde |\n|---|---|\n", f"| Norma | Onde |\n|---|---|\n{linha}\n")
        self.assertEqual(lint_unidade.lint(self.unidade), [])
        resolvidas, nao_resolvidas = normas.resolver(self.unidade)
        self.assertEqual(nao_resolvidas, [])
        self.assertIn("ui-builder", resolvidas[0].trecho)

    def test_sem_titulo_volta_com_aviso(self):
        rules.criar_guideline(self.raiz, "sem-titulo", "Vale em src.", ["src/**/*"], "Só texto, sem título.")
        achada = {a.nome: a for a in normas.aplicaveis(self.unidade, self.raiz)}["sem-titulo"]
        self.assertEqual(achada.linha, "")
        self.assertIn("título", achada.aviso)

    def test_padrao_fora_do_subconjunto_volta_com_aviso(self):
        (self.raiz / ".claude" / "rules" / "antiga.md").write_text(
            '---\nname: antiga\ndescription: x\npaths: ["src/**"]\n---\n\n# Antiga\n', encoding="utf-8"
        )
        achada = {a.nome: a for a in normas.aplicaveis(self.unidade, self.raiz)}["antiga"]
        self.assertEqual(achada.linha, "")
        self.assertIn("subconjunto", achada.aviso)

    def test_principio_nao_entra(self):
        (self.raiz / ".claude" / "rules" / "principles.md").write_text(
            "---\nname: principles\ndescription: x\n---\n\n# P\n", encoding="utf-8"
        )
        self.assertNotIn("principles", [a.nome for a in normas.aplicaveis(self.unidade, self.raiz)])


if __name__ == "__main__":
    unittest.main()
