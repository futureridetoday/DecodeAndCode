#!/usr/bin/env python3
"""Testes de `rules.criar_principio` — plano 0016.

Cada teste roda contra uma raiz sintética (`tempfile`), passada explicitamente — nunca contra o
`principles.md` real do repositório.
"""

from __future__ import annotations

import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import regioes
import rules


class _Base(unittest.TestCase):
    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self._tmp.cleanup)
        self.raiz = Path(self._tmp.name)
        self.dir_rules = self.raiz / ".claude" / "rules"
        self.alvo = self.dir_rules / "principles.md"

    def criar(self, nome="North star", enunciado="Marca nova não exige código novo.",
              teste="Adicionar uma marca muda só tokens vindos do Figma.", **kw):
        return rules.criar_principio(self.raiz, nome, enunciado, teste, **kw)

    def escrever_rule(self, nome: str, texto: str) -> Path:
        self.dir_rules.mkdir(parents=True, exist_ok=True)
        caminho = self.dir_rules / nome
        caminho.write_text(texto, encoding="utf-8")
        return caminho


class TestGravacao(_Base):
    def test_cria_o_arquivo_com_frontmatter_e_aprova_no_lint(self):
        self.assertEqual(self.criar(), self.alvo)
        self.assertEqual(rules.lint_rule(self.alvo), [])
        self.assertIsNone(regioes.ler_campo(self.alvo, "paths"))

    def test_formato_compacto_so_enunciado_e_teste(self):
        self.criar()
        texto = self.alvo.read_text(encoding="utf-8")
        self.assertIn(
            "## North star\n\n**Enunciado:** Marca nova não exige código novo.\n\n"
            "**Teste:** Adicionar uma marca muda só tokens vindos do Figma.\n",
            texto,
        )
        self.assertNotIn("Na prática", texto)

    def test_acrescenta_ao_arquivo_existente_sem_mexer_no_resto(self):
        original = "---\nname: principles\ndescription: Do time.\n---\n\n# Princípios\n\nTexto do time.\n"
        self.escrever_rule("principles.md", original)
        self.criar()
        texto = self.alvo.read_text(encoding="utf-8")
        self.assertTrue(texto.startswith(original))
        self.assertIn("## North star", texto)

    def test_entra_antes_da_fonte(self):
        """E-07 do teste final do DC 3.0: o princípio novo caía depois de `## Fonte`."""
        self.escrever_rule("principles.md", (
            "---\nname: principles\ndescription: Do time.\n---\n\n# Princípios\n\n"
            "## Antigo\n\n**Enunciado:** a.\n\n**Teste:** b.\n\n## Fonte\n\nDe onde veio.\n"
        ))
        self.criar()
        texto = self.alvo.read_text(encoding="utf-8")
        self.assertLess(texto.index("## Antigo"), texto.index("## North star"))
        self.assertLess(texto.index("## North star"), texto.index("## Fonte"))
        self.assertTrue(texto.endswith("## Fonte\n\nDe onde veio.\n"))
        self.assertEqual(rules.lint_rule(self.alvo), [])

    def test_descricao_vale_so_na_criacao(self):
        self.criar(descricao="Principles of the project.")
        self.assertEqual(regioes.ler_campo(self.alvo, "description"), '"Principles of the project."')


class TestTeto(_Base):
    def test_recusa_o_sexto_sem_mudar_o_arquivo(self):
        for i in range(rules.TETO_PRINCIPIOS):
            self.criar(nome=f"Princípio {i}")
        antes = self.alvo.read_text(encoding="utf-8")
        with self.assertRaisesRegex(ValueError, "teto"):
            self.criar(nome="Sexto")
        self.assertEqual(self.alvo.read_text(encoding="utf-8"), antes)

    def test_conta_enunciado_nao_titulo(self):
        secoes = "".join(f"## Seção {i}\n\nTexto.\n\n" for i in range(6))
        self.escrever_rule("principles.md", f"---\nname: principles\ndescription: x\n---\n\n{secoes}")
        self.criar()

    def test_conta_princípio_em_outra_rule_sem_paths(self):
        corpo = "".join(f"## P{i}\n\n**Enunciado:** e\n\n**Teste:** t\n\n" for i in range(5))
        self.escrever_rule("do-time.md", f"---\nname: do-time\ndescription: x\n---\n\n{corpo}")
        with self.assertRaisesRegex(ValueError, "teto"):
            self.criar()
        self.assertFalse(self.alvo.exists())

    def test_guideline_nao_entra_na_conta(self):
        corpo = "".join(f"## G{i}\n\n**Enunciado:** e\n\n" for i in range(5))
        self.escrever_rule("ui.md", f'---\nname: ui\ndescription: x\npaths: ["src/**/*"]\n---\n\n{corpo}')
        self.criar()


class TestRecusa(_Base):
    def test_nome_repetido_sem_diferenciar_caixa(self):
        self.criar()
        with self.assertRaisesRegex(ValueError, "já existe"):
            self.criar(nome="north STAR")

    def test_campo_vazio_recusado_sem_arquivo(self):
        for campo in ("nome", "enunciado", "teste"):
            with self.subTest(campo=campo), self.assertRaisesRegex(ValueError, "vazio"):
                self.criar(**{campo: "  "})
        self.assertFalse(self.alvo.exists())

    def test_campo_em_mais_de_uma_linha_recusado(self):
        with self.assertRaisesRegex(ValueError, "mais de uma linha"):
            self.criar(enunciado="linha um\n\nlinha dois")
        self.assertFalse(self.alvo.exists())

    def test_principles_com_paths_recusado(self):
        original = '---\nname: principles\ndescription: x\npaths: ["src/**/*"]\n---\n\nTexto.\n'
        self.escrever_rule("principles.md", original)
        with self.assertRaisesRegex(ValueError, "paths"):
            self.criar()
        self.assertEqual(self.alvo.read_text(encoding="utf-8"), original)


if __name__ == "__main__":
    unittest.main()
