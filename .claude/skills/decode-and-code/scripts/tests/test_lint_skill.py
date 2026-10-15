#!/usr/bin/env python3
"""Testes do lint de skill — unidade 0002-10.

O par do critério de aceite dá o essencial: as 11 skills reais do
repositório aprovam sem ressalva, e uma citação a script inexistente sob
`scripts/` reprova. As demais dimensões são cobertas isoladamente contra uma
skill sintética mínima que, sozinha, já aprova.
"""

from __future__ import annotations

import re
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import fixtures
import lib
import lint_skill

SKILL_VALIDA = """\
---
name: skill-sintetica
description: Descrição de teste para o lint.
disable-model-invocation: false
user-invocable: true

allowed-tools: "Read"

effort: low
context: ""
shell: bash

type: skill
project: DecodeAndCode
author: Teste
created: 2026-07-25
status: draft
version: 1.0.0
updated: ""
scope: project
auto_load: false
tags: []
dependencies: []

hub_id: ""
source: local
---

# skill-sintetica

Corpo de teste para o lint, citando o modo review.
"""


class TestSkillsReais(unittest.TestCase):
    """Toda skill real do repositório aprova sem ressalva — o critério de aceite.

    O piso existe para barrar verde falso: com o glob devolvendo vazio o laço
    não roda e o teste passaria sem verificar nada. Já o total exato não é
    asseverado de propósito — a versão original exigia 11 e quebrou na primeira
    skill criada, a própria `dev-units`. Contar skills não é o que esta unidade
    verifica.
    """

    def test_todas_as_skills_do_repositorio_aprovam(self):
        skills = sorted((lib.repo_root() / ".claude" / "skills").glob("*/SKILL.md"))
        self.assertGreaterEqual(len(skills), 1, skills)
        for skill in skills:
            with self.subTest(skill=skill.parent.name):
                self.assertEqual(lint_skill.lint(skill), [])


class TestArquivoInexistente(unittest.TestCase):
    def test_levanta_file_not_found_error(self):
        with tempfile.TemporaryDirectory() as tmp:
            alvo = Path(tmp) / "SKILL.md"
            with self.assertRaises(FileNotFoundError):
                lint_skill.lint(alvo)


class TestScriptCitadoNaoExiste(unittest.TestCase):
    """O caso negativo do critério de aceite — script citado que não existe."""

    def test_script_inexistente_reprova(self):
        texto = SKILL_VALIDA.replace(
            "Corpo de teste para o lint, citando o modo review.",
            "Corpo citando `${CLAUDE_SKILL_DIR}/scripts/nao-existe.py`.",
        )
        with tempfile.TemporaryDirectory() as tmp:
            pasta = Path(tmp) / "skill-sintetica"
            pasta.mkdir()
            alvo = pasta / "SKILL.md"
            alvo.write_text(texto, encoding="utf-8")
            problemas = lint_skill.lint(alvo)
        self.assertTrue(any("não existe" in p for p in problemas), problemas)


class TestScriptSemPermissaoNemInterprete(unittest.TestCase):
    """Script real sem +x sob `${CLAUDE_SKILL_DIR}/scripts/`.

    A versão anterior reaproveitava `backlog/scripts/create.py` do AmFlow — script real sem
    bit de execução, útil como fixture, mas ausente neste repositório (suposição de população
    medida na unidade 0001-02). `_checar_scripts` resolve contra o diretório da própria skill,
    então basta o script sem +x existir ao lado do `SKILL.md` sintético.
    """

    def _skill_com_script(self, tmp: str, corpo: str) -> Path:
        alvo = fixtures.skill(Path(tmp), nome="skill-sintetica", corpo=corpo)
        pasta_scripts = alvo.parent / "scripts"
        pasta_scripts.mkdir()
        script = pasta_scripts / "create.py"
        script.write_text("# sem bit de execução\n", encoding="utf-8")
        script.chmod(0o644)
        return alvo

    def test_reprova_sem_bit_de_execucao_e_sem_interpretador(self):
        with tempfile.TemporaryDirectory() as tmp:
            alvo = self._skill_com_script(
                tmp, "Corpo citando `${CLAUDE_SKILL_DIR}/scripts/create.py` direto, sem interpretador."
            )
            problemas = lint_skill.lint(alvo)
        self.assertTrue(
            any("create.py" in p and "interpretador" in p for p in problemas), problemas
        )

    def test_aprova_com_interpretador_explicito(self):
        with tempfile.TemporaryDirectory() as tmp:
            alvo = self._skill_com_script(
                tmp, "Composição via `python3`: `${CLAUDE_SKILL_DIR}/scripts/create.py`."
            )
            self.assertEqual(lint_skill.lint(alvo), [])


class TestCaminhoFixo(unittest.TestCase):
    """`P-01` do plano `apply-plugin-review` — o caminho fixo não existe no plugin instalado.

    O script existe de verdade ao lado do `SKILL.md`: a recusa vem do prefixo, não da ausência.
    """

    def test_caminho_fixo_da_propria_skill_reprova(self):
        with tempfile.TemporaryDirectory() as tmp:
            alvo = fixtures.skill(
                Path(tmp),
                nome="skill-sintetica",
                corpo="Composição via `python3`: `.claude/skills/skill-sintetica/scripts/create.py`.",
            )
            (alvo.parent / "scripts").mkdir()
            (alvo.parent / "scripts" / "create.py").write_text("", encoding="utf-8")
            problemas = lint_skill.lint(alvo)
        self.assertTrue(
            any("caminho fixo" in p and "create.py" in p for p in problemas), problemas
        )


class TestGateEstrutural(unittest.TestCase):
    """Contra uma skill sintética mínima que aprova — cada teste quebra uma dimensão por vez."""

    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self._tmp.cleanup)
        self.dir = Path(self._tmp.name) / "skill-sintetica"
        self.dir.mkdir()

    def _escreve(self, texto: str) -> Path:
        alvo = self.dir / "SKILL.md"
        alvo.write_text(texto, encoding="utf-8")
        return alvo

    def test_skill_valida_aprova(self):
        alvo = self._escreve(SKILL_VALIDA)
        self.assertEqual(lint_skill.lint(alvo), [])

    def test_frontmatter_ausente_por_completo(self):
        alvo = self._escreve("# Sem frontmatter\n\nConteúdo qualquer.\n")
        problemas = lint_skill.lint(alvo)
        self.assertTrue(any("frontmatter" in p for p in problemas), problemas)

    def test_cada_campo_obrigatorio_ausente_e_reportado(self):
        for campo in lint_skill.CAMPOS_FRONTMATTER:
            with self.subTest(campo=campo):
                padrao = re.compile(rf"(?m)^{re.escape(campo)}:.*\n")
                texto, n = padrao.subn("", SKILL_VALIDA, count=1)
                self.assertEqual(n, 1, f"linha do campo {campo!r} não encontrada na fixture")
                alvo = self._escreve(texto)
                problemas = lint_skill.lint(alvo)
                self.assertTrue(any(campo in p for p in problemas), (campo, problemas))

    def test_name_vazio(self):
        texto = SKILL_VALIDA.replace("name: skill-sintetica", "name:")
        alvo = self._escreve(texto)
        problemas = lint_skill.lint(alvo)
        self.assertTrue(any("name" in p and "vazio" in p for p in problemas), problemas)

    def test_name_nao_corresponde_ao_diretorio(self):
        texto = SKILL_VALIDA.replace("name: skill-sintetica", "name: outro-nome")
        alvo = self._escreve(texto)
        problemas = lint_skill.lint(alvo)
        self.assertTrue(any("não corresponde" in p for p in problemas), problemas)

    def test_description_vazia(self):
        texto = SKILL_VALIDA.replace(
            "description: Descrição de teste para o lint.", "description:"
        )
        alvo = self._escreve(texto)
        problemas = lint_skill.lint(alvo)
        self.assertTrue(any("description" in p for p in problemas), problemas)

    def test_modo_declarado_aprova(self):
        alvo = self._escreve(SKILL_VALIDA)
        self.assertEqual(lint_skill.lint(alvo, modos=["review"]), [])

    def test_modo_nao_declarado_reprova(self):
        alvo = self._escreve(SKILL_VALIDA)
        problemas = lint_skill.lint(alvo, modos=["review", "derive"])
        self.assertTrue(any("derive" in p for p in problemas), problemas)

    def test_link_relativo_quebrado_reprova(self):
        texto = SKILL_VALIDA + "\nVeja [outro doc](nao-existe.md).\n"
        alvo = self._escreve(texto)
        problemas = lint_skill.lint(alvo)
        self.assertTrue(any("nao-existe.md" in p for p in problemas), problemas)

    def test_link_dentro_de_bloco_de_codigo_e_ignorado(self):
        texto = SKILL_VALIDA + "\n```\n[link falso](nao-existe.md)\n```\n"
        alvo = self._escreve(texto)
        self.assertEqual(lint_skill.lint(alvo), [])

    def test_link_dentro_de_code_span_e_ignorado(self):
        texto = SKILL_VALIDA + "\nExemplo: `[link falso](nao-existe.md)`.\n"
        alvo = self._escreve(texto)
        self.assertEqual(lint_skill.lint(alvo), [])

    def test_link_absoluto_nao_e_checado(self):
        texto = SKILL_VALIDA + "\nVeja [outro](/nao-existe-mesmo-assim.md).\n"
        alvo = self._escreve(texto)
        self.assertEqual(lint_skill.lint(alvo), [])

    def test_link_valido_aprova(self):
        (self.dir / "outro.md").write_text("# Outro\n", encoding="utf-8")
        texto = SKILL_VALIDA + "\nVeja [outro doc](outro.md).\n"
        alvo = self._escreve(texto)
        self.assertEqual(lint_skill.lint(alvo), [])


if __name__ == "__main__":
    unittest.main()
