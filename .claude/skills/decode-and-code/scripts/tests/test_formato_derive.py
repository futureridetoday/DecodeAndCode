#!/usr/bin/env python3
"""Testes da unidade e do handoff no formato 2 — subparte 2.2.08 do redesign (K-05).

Codex, *Definition of Ready*: a unidade traz os blocos que bastam para rodar sem a conversa, e o
teto de passos saiu (D-06). *Handoff*: um por plano, no médio e no grande, com a ordem, a situação
derivada do teste e as seções do codex que o code lê, citadas pelo título.
"""

from __future__ import annotations

import sys
import tempfile
import unittest
from pathlib import Path
from unittest import mock

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import handoff
import lib
import lint_unidade
import normas

UNIDADE = """\
---
unit_id: 0001-01
unit_type: dev
state: spec
test: tests/test_algo.py
verified_at: ""
approved_by: ""
approved_at: ""
---

# Algo

## História

Como quem usa, quero algo, para um fim.

## Critério de aceite

O comando devolve 0 quando algo existe.

## Tarefas

- escrever o teste
- escrever o código

## Arquivos

| Arquivo | O quê |
|---|---|
| `src/algo.py` | criar |

## Guidelines

nenhuma

## Recursos

nenhum

## Decisões e lacunas

nenhuma

## Depende de

nada
"""


class _Plano(unittest.TestCase):
    def setUp(self) -> None:
        self._tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self._tmp.cleanup)
        self.raiz = Path(self._tmp.name).resolve()
        self.dir_plano = self.raiz / "0001-add-algo"
        self.dir_plano.mkdir()
        self.plano = self.dir_plano / "0001-add-algo.md"
        self.plano.write_text(
            "---\nplan_id: \"0001\"\nstatus: approved\nplan_size: médio\nplan_type: feature\n"
            "format_version: 2\n---\n\n# add-algo\n",
            encoding="utf-8",
        )
        for nome in ("repo_root", "plan_root"):
            p = mock.patch.object(lib, nome, return_value=self.raiz)
            p.start()
            self.addCleanup(p.stop)

    def unidade(self, texto: str = UNIDADE, nome: str = "01-algo.md") -> Path:
        caminho = self.dir_plano / nome
        caminho.write_text(texto, encoding="utf-8")
        return caminho


class TestUnidadeFormatoAtual(_Plano):
    def test_unidade_com_a_definition_of_ready_aprova(self) -> None:
        self.assertEqual(lint_unidade.lint(self.unidade()), [])

    def test_core_e_module_nao_sao_exigidos(self) -> None:
        self.assertNotIn("core", "".join(lint_unidade.lint(self.unidade())))

    def test_cada_bloco_ausente_reprova_sozinho(self) -> None:
        for bloco in lint_unidade.BLOCOS_DO_FORMATO_ATUAL:
            with self.subTest(bloco=bloco):
                texto = UNIDADE.replace(f"## {bloco}\n", "## Outro\n")
                self.assertIn(f"bloco ausente: {bloco}", lint_unidade.lint(self.unidade(texto)))

    def test_bloco_vazio_reprova(self) -> None:
        texto = UNIDADE.replace("## Depende de\n\nnada\n", "## Depende de\n\n")
        self.assertIn("bloco sem conteúdo: Depende de", lint_unidade.lint(self.unidade(texto)))

    def test_tarefas_sem_lista_reprova(self) -> None:
        texto = UNIDADE.replace("- escrever o teste\n- escrever o código\n", "escrever tudo\n")
        self.assertIn("Tarefas sem item de lista", lint_unidade.lint(self.unidade(texto)))

    def test_muitas_tarefas_aprovam(self) -> None:
        tarefas = "".join(f"- tarefa {i}\n" for i in range(20))
        texto = UNIDADE.replace("- escrever o teste\n- escrever o código\n", tarefas)
        self.assertEqual(lint_unidade.lint(self.unidade(texto)), [])

    def test_guideline_que_nao_resolve_reprova(self) -> None:
        texto = UNIDADE.replace(
            "## Guidelines\n\nnenhuma\n",
            "## Guidelines\n\n| Guideline | Onde |\n|---|---|\n| scripts | [scripts](x.md), seção *Scripts* |\n",
        )
        problemas = lint_unidade.lint(self.unidade(texto))
        self.assertTrue(any(p.startswith("guideline não resolve") for p in problemas), problemas)

    def test_resolver_le_a_tabela_de_guidelines(self) -> None:
        rules = self.raiz / ".claude" / "rules"
        rules.mkdir(parents=True)
        (rules / "scripts.md").write_text("---\npaths: [\"src/**\"]\n---\n\n# Scripts\n\nregra\n", encoding="utf-8")
        texto = UNIDADE.replace(
            "## Guidelines\n\nnenhuma\n",
            "## Guidelines\n\n| Guideline | Onde |\n|---|---|\n"
            "| Scripts | [scripts](../.claude/rules/scripts.md), seção *Scripts* |\n",
        )
        resolvidas, nao = normas.resolver(self.unidade(texto))
        self.assertEqual((len(resolvidas), nao), (1, []))
        self.assertIn("regra", resolvidas[0].trecho)


class TestHandoffFormatoAtual(_Plano):
    def _gerar(self) -> str:
        return handoff.gerar(self.dir_plano, fila="1. 0001-01", pendencias="nenhuma",
                             sugestao="pela única").read_text(encoding="utf-8")

    def test_medio_tem_handoff(self) -> None:
        self.unidade()
        self.assertTrue(self._gerar().startswith("# Handoff — plano 0001-add-algo"))

    def test_cita_as_secoes_do_code_pelo_titulo_sem_copiar(self) -> None:
        self.unidade()
        texto = self._gerar()
        for titulo in handoff.SECOES_DO_CODE:
            self.assertIn(f"- *{titulo}*", texto)
        self.assertNotIn("**O que é:**", texto)
        self.assertNotIn("modelo-dev-units", texto)

    def test_situacao_derivada_do_state(self) -> None:
        self.unidade()
        self.assertIn("| 0001-01 | por fazer |", self._gerar())
        self.unidade(UNIDADE.replace("state: spec", "state: verified"))
        self.assertIn("| 0001-01 | verificada |", self._gerar())

    def test_grande_fecha_com_o_teste_do_plano_inteiro(self) -> None:
        self.plano.write_text(self.plano.read_text(encoding="utf-8").replace("médio", "grande"), encoding="utf-8")
        self.unidade()
        self.assertIn("(P8)", self._gerar())

    def test_aponta_a_skill_do_code(self) -> None:
        self.unidade()
        self.assertIn("/decode-and-code:code <unidade>", self._gerar())

    def test_secoes_do_code_existem_no_codex(self) -> None:
        for titulo in handoff.SECOES_DO_CODE:
            with self.subTest(titulo=titulo):
                normas.secao_do_codex(titulo)


if __name__ == "__main__":
    unittest.main()
