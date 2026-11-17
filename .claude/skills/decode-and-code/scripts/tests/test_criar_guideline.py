#!/usr/bin/env python3
"""Testes de `rules.criar_guideline` — plano 0007, tarefa T1.

Cada teste roda contra uma raiz sintética (`tempfile`), passada explicitamente — o casamento de
`paths` contra o disco é feito ali, nunca na raiz real do repositório.
"""

from __future__ import annotations

import json
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
        (self.raiz / "src" / "ui").mkdir(parents=True)
        (self.raiz / "src" / "ui" / "botao.tsx").write_text("x", encoding="utf-8")
        (self.raiz / "docs").mkdir()
        (self.raiz / "docs" / "guia.md").write_text("x", encoding="utf-8")
        self.dir_rules = self.raiz / ".claude" / "rules"

    def criar(self, **kw):
        args = {
            "nome": "design-system",
            "descricao": "Componentes usam shadcn e Tailwind.",
            "paths": ["**/*.tsx"],
            "corpo": "Use os componentes de `src/ui`.",
        }
        args.update(kw)
        return rules.criar_guideline(self.raiz, **args)

    def residuos(self):
        if not self.raiz.joinpath(".claude").exists():
            return []
        return sorted(p.name for p in self.raiz.joinpath(".claude").rglob("*") if p.is_file())


class TestGravacao(_Base):
    def test_grava_em_rules_e_aprova_no_lint(self):
        alvo = self.criar()
        self.assertEqual(alvo, self.dir_rules / "design-system.md")
        self.assertEqual(rules.lint_guideline(alvo, raiz=self.raiz), [])

    def test_description_com_dois_pontos_e_cerquilha_vai_escapada(self):
        descricao = 'Regra: use "shadcn" # sempre'
        alvo = self.criar(descricao=descricao)
        valor = regioes.ler_campo(alvo, "description")
        self.assertEqual(valor, json.dumps(descricao, ensure_ascii=False))
        self.assertEqual(json.loads(valor), descricao)

    def test_name_vai_entre_aspas(self):
        alvo = self.criar()
        self.assertEqual(regioes.ler_campo(alvo, "name"), '"design-system"')

    def test_cada_entrada_de_paths_vai_entre_aspas(self):
        alvo = self.criar(paths=["**/*.tsx", "docs/**/*"])
        self.assertEqual(regioes.ler_campo(alvo, "paths"), '["**/*.tsx", "docs/**/*"]')

    def test_corpo_preservado(self):
        alvo = self.criar()
        self.assertIn("Use os componentes de `src/ui`.", alvo.read_text(encoding="utf-8"))

    def test_sem_aguardando_nao_grava_paths_pending(self):
        alvo = self.criar()
        self.assertIsNone(regioes.ler_campo(alvo, "paths_pending"))


class TestPadroesDePaths(_Base):
    def test_pasta_inteira_com_barra_dois_asteriscos_recusada(self):
        with self.assertRaises(ValueError):
            self.criar(paths=["docs/**"])
        self.assertEqual(self.residuos(), [])

    def test_pasta_inteira_na_forma_da_doc_aceita(self):
        alvo = self.criar(paths=["docs/**/*"])
        self.assertEqual(rules.lint_guideline(alvo, raiz=self.raiz), [])

    def test_chaves_recusadas(self):
        with self.assertRaises(ValueError):
            self.criar(paths=["src/**/*.{ts,tsx}"])

    def test_virgula_recusada(self):
        with self.assertRaises(ValueError):
            self.criar(paths=["src/a,b.ts"])

    def test_barra_inicial_recusada(self):
        with self.assertRaises(ValueError):
            self.criar(paths=["/src/**/*.tsx"])

    def test_sem_diretorio_recusado(self):
        with self.assertRaises(ValueError):
            self.criar(paths=["*.md"])

    def test_primeiro_segmento_curinga_recusado(self):
        with self.assertRaises(ValueError):
            self.criar(paths=["*/ui/*.tsx"])

    def test_diretorio_ancorado_aceito(self):
        alvo = self.criar(paths=["src/ui/*.tsx"])
        self.assertEqual(rules.lint_guideline(alvo, raiz=self.raiz), [])

    def test_lista_vazia_recusada(self):
        with self.assertRaises(ValueError):
            self.criar(paths=[])
        self.assertEqual(self.residuos(), [])


class TestNome(_Base):
    def test_acento_recusado(self):
        with self.assertRaises(ValueError):
            self.criar(nome="padrão-ui")

    def test_maiuscula_recusada(self):
        with self.assertRaises(ValueError):
            self.criar(nome="Design-system")

    def test_nome_existente_em_rules_recusado(self):
        self.criar()
        with self.assertRaises(FileExistsError):
            self.criar()

    def test_nome_existente_em_rules_off_recusado(self):
        off = self.raiz / ".claude" / "rules-off"
        off.mkdir(parents=True)
        (off / "design-system.md").write_text("x", encoding="utf-8")
        with self.assertRaises(FileExistsError):
            self.criar()
        self.assertFalse((self.dir_rules / "design-system.md").exists())


class TestReprovacaoSemResiduo(_Base):
    def test_corpo_vazio_reprova_e_nao_deixa_arquivo(self):
        with self.assertRaises(ValueError):
            self.criar(corpo="   ")
        self.assertEqual(self.residuos(), [])


class TestCaminhoAguardando(_Base):
    def test_caminho_inexistente_recusado_sem_aguardando(self):
        with self.assertRaises(ValueError):
            self.criar(paths=["app/**/*.tsx"])
        self.assertEqual(self.residuos(), [])

    def test_caminho_inexistente_aceito_com_aguardando(self):
        alvo = self.criar(paths=["app/**/*.tsx"], aguardando=True)
        self.assertEqual(regioes.ler_campo(alvo, "paths_pending"), "true")
        self.assertEqual(rules.lint_guideline(alvo, raiz=self.raiz), [])

    def test_aguardando_mantem_as_demais_checagens(self):
        with self.assertRaises(ValueError):
            self.criar(paths=["app/**/*.tsx"], corpo="", aguardando=True)


class TestLintGuidelineRaiz(_Base):
    """O parâmetro `raiz` do lint — e `paths_pending` só dispensa o casamento, nada mais."""

    def _escrever(self, frontmatter: str, corpo: str = "Corpo.") -> Path:
        self.dir_rules.mkdir(parents=True, exist_ok=True)
        alvo = self.dir_rules / "manual.md"
        alvo.write_text(f"---\n{frontmatter}---\n\n{corpo}\n", encoding="utf-8")
        return alvo

    def test_casamento_usa_a_raiz_passada(self):
        alvo = self._escrever('name: "m"\ndescription: "d"\npaths: ["src/ui/*.tsx"]\n')
        self.assertEqual(rules.lint_guideline(alvo, raiz=self.raiz), [])

    def test_sem_casamento_na_raiz_passada_reprova(self):
        alvo = self._escrever('name: "m"\ndescription: "d"\npaths: ["app/*.tsx"]\n')
        self.assertTrue(rules.lint_guideline(alvo, raiz=self.raiz))

    def test_paths_pending_nao_dispensa_paths_vazio(self):
        alvo = self._escrever('name: "m"\ndescription: "d"\npaths: []\npaths_pending: true\n')
        self.assertTrue(rules.lint_guideline(alvo, raiz=self.raiz))


if __name__ == "__main__":
    unittest.main()
