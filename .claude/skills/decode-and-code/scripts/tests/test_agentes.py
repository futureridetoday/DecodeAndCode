#!/usr/bin/env python3
"""Testes do lint de agente — unidade 0001-19.

O par do critério de aceite dá o essencial: os quatro invariantes reprovam isoladamente, um por
vez, contra um agente sintético mínimo que sozinho já aprova; e o `ai-builder.md` real — o único
agent que sobrou, depois que o ciclo `review` / `derive` / `implement` virou skill (`P-03`) — aprova
sem ressalva, com `model` e as fronteiras do corpo conferidos em nome de caso próprio.
"""

from __future__ import annotations

import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import lib
import lint_agente

AGENTE_VALIDO = """\
---
name: agente-sintetico
description: Agente de teste para o lint.
tools: Read, Grep
model: sonnet
skills: [review-plan]
color: blue
---

Corpo de teste para o lint de agente.
"""


class TestAiBuilderReal(unittest.TestCase):
    """O caso contra o artefato real — sem ele, o lint prova só o mecanismo (L-31)."""

    def setUp(self):
        self.alvo = lib.repo_root() / ".claude" / "agents" / "ai-builder.md"
        self.texto = self.alvo.read_text(encoding="utf-8")

    def test_ai_builder_aprova_no_lint(self):
        self.assertEqual(lint_agente.lint(self.alvo), [])

    def test_ai_builder_declara_model_opus(self):
        self.assertRegex(self.texto, r"(?m)^model:\s*opus\s*$")

    def test_ai_builder_declara_skill_existente_em_disco(self):
        """O `skills:` fica, e é o que faz o agent achar os scripts fora do checkout.

        Medido em 2026-10-15 com `--plugin-dir`: o debug log mostra `Preloaded skill` para o
        ai-builder, que recebe o corpo da skill com `${CLAUDE_SKILL_DIR}` já expandido para o
        caminho absoluto dos scripts no plugin — é por ele que o passo de numerar, validar o nome e
        rodar `lint_plano` acha `numeracao.py`, `nomenclatura.py` e `lint_plano.py`. Sem o campo, o
        agent perde o caminho, e `skills: [review-plan]` entrega
        `.../skills/review-plan/../decode-and-code/scripts/...`.
        """
        self.assertRegex(self.texto, r"(?m)^skills:.*review-plan")
        self.assertTrue((lib.repo_root() / ".claude" / "skills" / "review-plan" / "SKILL.md").is_file())

    def test_ai_builder_cita_as_skills_do_ciclo_e_elas_existem_em_disco(self):
        """`review-plan` é o próximo passo que ele recomenda; `derive` e `implement` são as
        fronteiras que ele declara não serem dele — os três nomes têm de existir."""
        for nome in lib.SKILLS:
            with self.subTest(skill=nome):
                self.assertIn(f"`{nome}", self.texto)
                self.assertTrue((lib.repo_root() / ".claude" / "skills" / nome / "SKILL.md").is_file())

    def test_ai_builder_declara_webfetch(self):
        """Confirmar schema oficial em docs.claude.com precisa de ferramenta que alcance."""
        self.assertRegex(self.texto, r"(?m)^tools:.*WebFetch")

    def test_ai_builder_declara_contrato_recomenda_review_plan(self):
        self.assertIn("`review-plan <caminho>`", self.texto)

    def test_ai_builder_declara_fronteira_com_derive(self):
        self.assertIn("isso é da skill `derive`", self.texto)

    def test_ai_builder_declara_fronteira_com_implement(self):
        self.assertIn("isso é da skill `implement`", self.texto)

    def test_ai_builder_aplica_gates_do_principles(self):
        """Defesa contra esboço inflado: reaproveita Clarificar/Evitar/Reduzir + Gates A/B de
        `principles.md` em vez de inventar um critério de tamanho próprio."""
        self.assertIn("Gate A", self.texto)
        self.assertIn("Gate B", self.texto)

    def test_ai_builder_declara_leitura_via_read(self):
        """Medido num teste de execução real: as 13 chamadas de uma invocação foram todas `Bash`
        com cat/head/sed/grep, nunca `Read`/`Grep`/`Glob` — apesar de declarados em `tools:`."""
        self.assertIn("nunca `cat`/`head`/`tail`/`sed`/`grep` via `Bash`", self.texto)


class TestArquivoInexistente(unittest.TestCase):
    def test_levanta_file_not_found_error(self):
        with tempfile.TemporaryDirectory() as tmp:
            alvo = Path(tmp) / "agente.md"
            with self.assertRaises(FileNotFoundError):
                lint_agente.lint(alvo)


class TestGateEstrutural(unittest.TestCase):
    """Contra um agente sintético mínimo que aprova — cada teste quebra um invariante por vez."""

    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self._tmp.cleanup)
        self.dir = Path(self._tmp.name)

    def _escreve(self, texto: str) -> Path:
        alvo = self.dir / "agente.md"
        alvo.write_text(texto, encoding="utf-8")
        return alvo

    def test_agente_valido_aprova(self):
        alvo = self._escreve(AGENTE_VALIDO)
        self.assertEqual(lint_agente.lint(alvo), [])

    def test_campo_nao_nativo_declarado_reprova(self):
        texto = AGENTE_VALIDO.replace(
            "color: blue\n", "color: blue\ndependencies: [outra-skill]\n"
        )
        alvo = self._escreve(texto)
        problemas = lint_agente.lint(alvo)
        self.assertTrue(
            any("dependencies" in p and "não-nativo" in p for p in problemas), problemas
        )

    def test_model_ausente_reprova(self):
        texto = AGENTE_VALIDO.replace("model: sonnet\n", "")
        alvo = self._escreve(texto)
        problemas = lint_agente.lint(alvo)
        self.assertTrue(any("model" in p and "ausente" in p for p in problemas), problemas)

    def test_model_fora_do_vocabulario_reprova(self):
        texto = AGENTE_VALIDO.replace("model: sonnet", "model: gpt4")
        alvo = self._escreve(texto)
        problemas = lint_agente.lint(alvo)
        self.assertTrue(any("vocabulário" in p for p in problemas), problemas)

    def test_skill_inexistente_em_disco_reprova(self):
        texto = AGENTE_VALIDO.replace(
            "skills: [review-plan]", "skills: [skill-que-nao-existe]"
        )
        alvo = self._escreve(texto)
        problemas = lint_agente.lint(alvo)
        self.assertTrue(any("skill-que-nao-existe" in p for p in problemas), problemas)

    def test_tools_ausente_reprova(self):
        texto = AGENTE_VALIDO.replace("tools: Read, Grep\n", "")
        alvo = self._escreve(texto)
        problemas = lint_agente.lint(alvo)
        self.assertTrue(any("tools" in p and "ausente" in p for p in problemas), problemas)

    def test_memory_declarado_reprova(self):
        """A recusa de `memory` provada pelo caso contrário: sem este, ela podia nunca ter sido
        implementada e a ausência do campo em `ai-builder.md` passaria do mesmo jeito (D-06)."""
        texto = AGENTE_VALIDO.replace("color: blue\n", "color: blue\nmemory: sessao-anterior\n")
        alvo = self._escreve(texto)
        problemas = lint_agente.lint(alvo)
        self.assertTrue(any("memory" in p and "D-06" in p for p in problemas), problemas)


if __name__ == "__main__":
    unittest.main()
