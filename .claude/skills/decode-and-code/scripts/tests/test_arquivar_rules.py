#!/usr/bin/env python3
"""Testes de arquivar, restaurar e substituir princípio e guideline — plano 0020, tarefa 3.

Cada teste roda contra uma raiz sintética (`tempfile`), passada explicitamente — nunca contra o
`.claude/` real do repositório. O oráculo é o da norma, *Camada normativa → Editar e arquivar*:
arquivar move com três campos e não perde byte; o nome arquivado fica reservado; `restore` só
devolve o que passa de novo no escritor; `replace` valida a versão nova antes de tirar a antiga.
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

DATA = "2026-11-22"
AUTOR = "Pessoa Teste"


class _Base(unittest.TestCase):
    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self._tmp.cleanup)
        self.raiz = Path(self._tmp.name)
        (self.raiz / "App" / "Theme").mkdir(parents=True)
        (self.raiz / "App" / "Theme" / "cores.swift").write_text("x", encoding="utf-8")
        self.dir_rules = self.raiz / ".claude" / "rules"
        self.dir_arquivo = self.raiz / ".claude" / "archive" / "rules"
        self.principles = self.dir_rules / "principles.md"
        self.principles_arquivo = self.dir_arquivo / "principles.md"

    def principio(self, nome="North star", enunciado="Ajudar a economizar.",
                  teste="Toda tela mostra quanto a pessoa poupou.", **kw):
        return rules.criar_principio(self.raiz, nome, enunciado, teste, **kw)

    def guideline(self, nome="paleta-azul", **kw):
        args = {
            "nome": nome,
            "descricao": "Vale ao tocar o tema do app.",
            "paths": ["App/Theme/**/*"],
            "corpo": "# Paleta\n\nA cor primária é azul.",
        }
        args.update(kw)
        return rules.criar_guideline(self.raiz, **args)

    def arquivar_principio(self, nome="North star", motivo="Rumo novo."):
        return rules.archive_principle(self.raiz, nome, motivo, AUTOR, data=DATA)

    def arquivar_guideline(self, nome="paleta-azul", motivo="Marca laranja."):
        return rules.archive_guideline(self.raiz, nome, motivo, AUTOR, data=DATA)

    def ler(self, caminho: Path) -> str:
        return caminho.read_text(encoding="utf-8")

    def registry(self) -> dict:
        return json.loads(self.ler(self.dir_rules / "registry.json"))


class TestArquivarPrincipio(_Base):
    def test_secao_sai_e_entra_no_arquivo_com_os_tres_campos(self):
        self.principio(nome="Simples")
        self.principio()
        secao = "## North star\n\n**Enunciado:** Ajudar a economizar.\n\n**Teste:** Toda tela mostra quanto a pessoa poupou.\n"

        self.assertEqual(self.arquivar_principio(), self.principles_arquivo)

        self.assertNotIn("North star", self.ler(self.principles))
        self.assertIn("## Simples", self.ler(self.principles))
        self.assertEqual(rules.lint_rule(self.principles), [])
        arquivo = self.ler(self.principles_arquivo)
        self.assertIn(
            secao.rstrip("\n") + f"\n\n**archived_at:** {DATA}\n\n**archived_by:** {AUTOR}\n\n**reason:** Rumo novo.\n",
            arquivo,
        )

    def test_nenhum_byte_da_secao_se_perde(self):
        original = (
            "---\nname: principles\ndescription: Do time.\n---\n\n"
            "## North star\n\n**Enunciado:** Ajudar a economizar.\n\n**Teste:** Mostra o que poupou.\n\n"
            "**Na prática:** sem tela de gasto.\n\n"
            "## Simples\n\n**Enunciado:** Menos é mais.\n\n**Teste:** Uma tela por tarefa.\n"
        )
        self.dir_rules.mkdir(parents=True)
        self.principles.write_text(original, encoding="utf-8")
        secao = original[original.index("## North star"):original.index("## Simples")]

        self.arquivar_principio()

        self.assertEqual(self.ler(self.principles), original.replace(secao, ""))
        self.assertIn(secao.rstrip("\n") + "\n\n**archived_at:**", self.ler(self.principles_arquivo))

    def test_libera_uma_vaga_no_teto(self):
        for i in range(rules.TETO_PRINCIPIOS - 1):
            self.principio(nome=f"P{i}")
        self.principio()
        with self.assertRaisesRegex(ValueError, "teto"):
            self.principio(nome="Sexto")
        self.arquivar_principio()
        self.principio(nome="Sexto")

    def test_ultimo_principio_arquivado_remove_o_arquivo_vazio(self):
        self.principio()
        self.arquivar_principio()
        self.assertFalse(self.principles.exists())
        self.assertIn("## North star", self.ler(self.principles_arquivo))

    def test_recusas_sem_tocar_o_disco(self):
        self.principio()
        antes = self.ler(self.principles)
        casos = {
            "desconhecido": dict(nome="Outro"),
            "motivo vazio": dict(motivo="  "),
        }
        for caso, kw in casos.items():
            with self.subTest(caso=caso), self.assertRaises(ValueError):
                self.arquivar_principio(**kw)
        with self.assertRaises(ValueError):
            rules.archive_principle(self.raiz, "North star", "Rumo novo.", " ", data=DATA)
        self.assertEqual(self.ler(self.principles), antes)
        self.assertFalse(self.dir_arquivo.exists())

    def test_secao_sem_enunciado_nao_e_principio(self):
        self.dir_rules.mkdir(parents=True)
        self.principles.write_text(
            "---\nname: principles\ndescription: x\n---\n\n## Fonte\n\nTexto.\n", encoding="utf-8"
        )
        with self.assertRaisesRegex(ValueError, "não é princípio"):
            self.arquivar_principio(nome="Fonte")


class TestArquivarGuideline(_Base):
    def test_arquivo_se_move_com_os_tres_campos_e_o_registry_e_reprojetado(self):
        original = self.ler(self.guideline())
        self.guideline(nome="tipografia")

        destino = self.arquivar_guideline()

        self.assertEqual(destino, self.dir_arquivo / "paleta-azul.md")
        self.assertFalse((self.dir_rules / "paleta-azul.md").exists())
        self.assertEqual(regioes.ler_campo(destino, "archived_at"), json.dumps(DATA))
        self.assertEqual(regioes.ler_campo(destino, "archived_by"), json.dumps(AUTOR))
        self.assertEqual(regioes.ler_campo(destino, "reason"), json.dumps("Marca laranja."))
        sem_campos = "\n".join(
            l for l in self.ler(destino).split("\n") if not l.startswith(("archived_at:", "archived_by:", "reason:"))
        )
        self.assertEqual(sem_campos, original)
        self.assertEqual(sorted(self.registry()), ["tipografia"])

    def test_desligada_tambem_se_arquiva(self):
        alvo = self.guideline()
        off = self.raiz / ".claude" / "rules-off"
        off.mkdir(parents=True)
        alvo.rename(off / alvo.name)
        self.arquivar_guideline()
        self.assertFalse((off / alvo.name).exists())
        self.assertTrue((self.dir_arquivo / alvo.name).exists())

    def test_recusas_sem_tocar_o_disco(self):
        self.guideline()
        self.principio()
        antes = self.ler(self.dir_rules / "paleta-azul.md")
        for caso, kw in {"desconhecida": dict(nome="outra"), "motivo vazio": dict(motivo=""),
                         "princípio": dict(nome="principles")}.items():
            with self.subTest(caso=caso), self.assertRaises(ValueError):
                self.arquivar_guideline(**kw)
        self.assertEqual(self.ler(self.dir_rules / "paleta-azul.md"), antes)
        self.assertFalse(self.dir_arquivo.exists())


class TestNomeReservado(_Base):
    def test_criar_principio_recusa_nome_arquivado(self):
        self.principio()
        self.arquivar_principio()
        with self.assertRaisesRegex(ValueError, "arquivado"):
            self.principio(nome="north star")
        self.assertFalse(self.principles.exists())

    def test_criar_guideline_recusa_nome_arquivado(self):
        self.guideline()
        self.arquivar_guideline()
        with self.assertRaisesRegex(FileExistsError, "arquivada"):
            self.guideline()
        self.assertFalse((self.dir_rules / "paleta-azul.md").exists())


class TestRestaurarPrincipio(_Base):
    def test_volta_com_o_mesmo_nome_e_sem_os_campos(self):
        self.principio(nome="Simples")
        self.principio()
        secao = self.ler(self.principles)[self.ler(self.principles).index("## North star"):]
        self.arquivar_principio()

        self.assertEqual(rules.restore_principle(self.raiz, "North star"), self.principles)

        texto = self.ler(self.principles)
        self.assertTrue(texto.endswith(secao), texto)
        self.assertNotIn("archived_at", texto)
        self.assertNotIn("North star", self.ler(self.principles_arquivo))
        self.assertEqual(rules.lint_rule(self.principles), [])

    def test_recusa_acima_do_teto_e_o_arquivo_fica_como_estava(self):
        self.principio()
        self.arquivar_principio()
        for i in range(rules.TETO_PRINCIPIOS):
            self.principio(nome=f"P{i}")
        antes = self.ler(self.principles_arquivo)
        with self.assertRaisesRegex(ValueError, "teto"):
            rules.restore_principle(self.raiz, "North star")
        self.assertEqual(self.ler(self.principles_arquivo), antes)
        self.assertNotIn("North star", self.ler(self.principles))

    def test_recusa_o_que_nao_esta_arquivado(self):
        with self.assertRaisesRegex(ValueError, "não está arquivado"):
            rules.restore_principle(self.raiz, "North star")


class TestRestaurarGuideline(_Base):
    def test_volta_com_o_mesmo_nome_sem_os_campos_e_registrada(self):
        original = self.ler(self.guideline())
        self.arquivar_guideline()

        destino = rules.restore_guideline(self.raiz, "paleta-azul")

        self.assertEqual(destino, self.dir_rules / "paleta-azul.md")
        self.assertEqual(self.ler(destino), original)
        self.assertFalse((self.dir_arquivo / "paleta-azul.md").exists())
        self.assertEqual(self.registry()["paleta-azul"]["estado"], "ligada")

    def test_recusa_a_que_reprova_no_lint_e_o_arquivo_fica_como_estava(self):
        self.guideline()
        self.arquivar_guideline()
        (self.raiz / "App" / "Theme" / "cores.swift").unlink()
        arquivada = self.dir_arquivo / "paleta-azul.md"
        antes = self.ler(arquivada)
        with self.assertRaisesRegex(ValueError, "não casa"):
            rules.restore_guideline(self.raiz, "paleta-azul")
        self.assertEqual(self.ler(arquivada), antes)
        self.assertFalse((self.dir_rules / "paleta-azul.md").exists())

    def test_recusa_a_que_nao_esta_arquivada(self):
        with self.assertRaisesRegex(ValueError, "não está arquivada"):
            rules.restore_guideline(self.raiz, "paleta-azul")


class TestSubstituirPrincipio(_Base):
    def test_mesmo_nome_e_mesmo_lugar_com_texto_novo(self):
        self.principio()
        self.principio(nome="Simples", enunciado="Menos é mais.")

        self.principio(enunciado="Consciência das escolhas de compra.",
                       teste="Toda compra mostra a alternativa de não comprar.", replace=True)

        texto = self.ler(self.principles)
        self.assertLess(texto.index("## North star"), texto.index("## Simples"))
        self.assertIn("**Enunciado:** Consciência das escolhas de compra.", texto)
        self.assertNotIn("Ajudar a economizar", texto)
        self.assertEqual(texto.count("## North star"), 1)

    def test_no_teto_substituir_nao_conta_como_sexto(self):
        for i in range(rules.TETO_PRINCIPIOS - 1):
            self.principio(nome=f"P{i}")
        self.principio()
        self.principio(enunciado="Outro.", replace=True)
        self.assertIn("**Enunciado:** Outro.", self.ler(self.principles))

    def test_versao_que_reprova_deixa_a_antiga_intacta(self):
        self.principio()
        antes = self.ler(self.principles)
        for caso, kw in {"inexistente": dict(nome="Outro"), "enunciado vazio": dict(enunciado=" ")}.items():
            with self.subTest(caso=caso), self.assertRaises(ValueError):
                self.principio(replace=True, **kw)
        self.assertEqual(self.ler(self.principles), antes)


class TestSubstituirGuideline(_Base):
    def test_mesmo_nome_e_mesmo_lugar_com_texto_novo(self):
        self.guideline()
        alvo = self.guideline(descricao="Vale ao tocar o tema.", corpo="# Paleta\n\nA cor primária é laranja.",
                              replace=True)
        self.assertEqual(alvo, self.dir_rules / "paleta-azul.md")
        self.assertIn("laranja", self.ler(alvo))
        self.assertNotIn("azul.", self.ler(alvo))
        self.assertEqual(rules.lint_guideline(alvo, raiz=self.raiz), [])
        self.assertEqual(sorted(self.registry()), ["paleta-azul"])

    def test_versao_que_reprova_deixa_a_antiga_intacta(self):
        alvo = self.guideline()
        antes = self.ler(alvo)
        casos = {
            "paths que não casa": dict(paths=["Outro/**/*"]),
            "inexistente": dict(nome="outra"),
        }
        for caso, kw in casos.items():
            with self.subTest(caso=caso), self.assertRaises(ValueError):
                self.guideline(replace=True, **kw)
        self.assertEqual(self.ler(alvo), antes)
        self.assertFalse((self.dir_rules / "outra.md").exists())


if __name__ == "__main__":
    unittest.main()
