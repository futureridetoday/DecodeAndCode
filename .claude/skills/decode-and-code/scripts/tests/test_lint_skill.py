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

    def test_caminho_fixo_de_outra_skill_reprova(self):
        """`P-03` — os scripts moram numa pasta irmã, e o caminho fixo dela é a mesma armadilha.

        O script existe de verdade na pasta irmã: a recusa vem do prefixo, não da ausência.
        """
        with tempfile.TemporaryDirectory() as tmp:
            alvo = fixtures.skill(
                Path(tmp),
                nome="skill-sintetica",
                corpo="Composição via `python3`: `.claude/skills/outra/scripts/x.py`.",
            )
            (Path(tmp) / "outra" / "scripts").mkdir(parents=True)
            (Path(tmp) / "outra" / "scripts" / "x.py").write_text("", encoding="utf-8")
            problemas = lint_skill.lint(alvo)
        self.assertTrue(any("caminho fixo" in p and "outra/scripts/x.py" in p for p in problemas), problemas)


class TestScriptEmPastaIrma(unittest.TestCase):
    """`P-03` — as três skills citam os scripts da pasta irmã por `${CLAUDE_SKILL_DIR}/../<pasta>/`."""

    def _skill_citando(self, tmp: str, cita: str) -> Path:
        return fixtures.skill(
            Path(tmp), nome="skill-sintetica", corpo=f"Composição via `python3`: `{cita}`."
        )

    def test_script_existente_na_pasta_irma_aprova(self):
        with tempfile.TemporaryDirectory() as tmp:
            (Path(tmp) / "compartilhada" / "scripts").mkdir(parents=True)
            (Path(tmp) / "compartilhada" / "scripts" / "x.py").write_text("", encoding="utf-8")
            alvo = self._skill_citando(tmp, "${CLAUDE_SKILL_DIR}/../compartilhada/scripts/x.py")
            self.assertEqual(lint_skill.lint(alvo), [])

    def test_script_inexistente_na_pasta_irma_reprova(self):
        with tempfile.TemporaryDirectory() as tmp:
            (Path(tmp) / "compartilhada" / "scripts").mkdir(parents=True)
            alvo = self._skill_citando(tmp, "${CLAUDE_SKILL_DIR}/../compartilhada/scripts/x.py")
            problemas = lint_skill.lint(alvo)
        self.assertTrue(
            any("script citado não existe" in p and "compartilhada/scripts/x.py" in p for p in problemas),
            problemas,
        )

    def test_pasta_irma_inexistente_reprova(self):
        with tempfile.TemporaryDirectory() as tmp:
            alvo = self._skill_citando(tmp, "${CLAUDE_SKILL_DIR}/../nao-existe/scripts/x.py")
            problemas = lint_skill.lint(alvo)
        self.assertTrue(any("script citado não existe" in p for p in problemas), problemas)

    def test_script_da_pasta_irma_sem_interpretador_nem_bit_reprova(self):
        """O mesmo passo 5 vale para a irmã: resolver o `..` não afrouxa a checagem de execução."""
        with tempfile.TemporaryDirectory() as tmp:
            script = Path(tmp) / "compartilhada" / "scripts" / "x.py"
            script.parent.mkdir(parents=True)
            script.write_text("", encoding="utf-8")
            script.chmod(0o644)
            alvo = fixtures.skill(
                Path(tmp),
                nome="skill-sintetica",
                corpo="Corpo citando `${CLAUDE_SKILL_DIR}/../compartilhada/scripts/x.py` direto.",
            )
            problemas = lint_skill.lint(alvo)
        self.assertTrue(any("x.py" in p and "interpretador" in p for p in problemas), problemas)

    def test_subir_mais_de_um_nivel_nao_conta_como_citacao(self):
        """Só `../<pasta>/` — `../../` não é reconhecido, então o lint não o resolve nem o aprova."""
        with tempfile.TemporaryDirectory() as tmp:
            (Path(tmp) / "scripts").mkdir()
            (Path(tmp) / "scripts" / "x.py").write_text("", encoding="utf-8")
            alvo = self._skill_citando(tmp, "${CLAUDE_SKILL_DIR}/../../scripts/x.py")
            self.assertEqual(lint_skill._caminhos_de_scripts(alvo.read_text(encoding="utf-8")), {})


class TestScriptNaPastaDaSkill(unittest.TestCase):
    """`P-14` — `${CLAUDE_SKILL_DIR}/dc.py`, o atalho que mora ao lado do `SKILL.md`, sem `..`."""

    def _skill_citando(self, tmp: str, corpo: str, atalho: bool = True) -> Path:
        alvo = fixtures.skill(Path(tmp), nome="skill-sintetica", corpo=corpo)
        if atalho:
            (alvo.parent / "dc.py").write_text("", encoding="utf-8")
        return alvo

    def test_atalho_existente_aprova(self):
        with tempfile.TemporaryDirectory() as tmp:
            alvo = self._skill_citando(tmp, 'Rode `python3 "${CLAUDE_SKILL_DIR}/dc.py" validar-nome x`.')
            self.assertEqual(lint_skill.lint(alvo), [])

    def test_atalho_inexistente_reprova(self):
        with tempfile.TemporaryDirectory() as tmp:
            alvo = self._skill_citando(
                tmp, 'Rode `python3 "${CLAUDE_SKILL_DIR}/dc.py" validar-nome x`.', atalho=False
            )
            problemas = lint_skill.lint(alvo)
        self.assertTrue(any("script citado não existe" in p and "dc.py" in p for p in problemas), problemas)

    def test_atalho_sem_interpretador_nem_bit_reprova(self):
        with tempfile.TemporaryDirectory() as tmp:
            alvo = self._skill_citando(tmp, "Rode `${CLAUDE_SKILL_DIR}/dc.py` direto.")
            (alvo.parent / "dc.py").chmod(0o644)
            problemas = lint_skill.lint(alvo)
        self.assertTrue(any("dc.py" in p and "interpretador" in p for p in problemas), problemas)

    def test_arquivo_que_nao_e_script_na_pasta_da_skill_nao_conta(self):
        """Só `.py` direto na pasta: `${CLAUDE_SKILL_DIR}/notas.md` não é citação de script."""
        with tempfile.TemporaryDirectory() as tmp:
            alvo = self._skill_citando(tmp, "Veja `${CLAUDE_SKILL_DIR}/notas.md`.", atalho=False)
            self.assertEqual(lint_skill._caminhos_de_scripts(alvo.read_text(encoding="utf-8")), {})


class TestBashLivre(unittest.TestCase):
    """`P-14` — `allowed-tools` não libera `Bash` sem especificador, em nenhum dos formatos do campo.

    Contra a skill sintética mínima, trocando só a linha `allowed-tools`. O lado que aprova importa
    tanto quanto o que reprova: sem ele a regra poderia estar recusando `Bash(...)` também, que é
    justamente o que o `dc.py` precisa.
    """

    REGRA_DC = 'Bash(python3 \\"${CLAUDE_SKILL_DIR}/dc.py\\" *)'

    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self._tmp.cleanup)
        self.dir = Path(self._tmp.name) / "skill-sintetica"
        self.dir.mkdir()

    def _problemas(self, allowed_tools: str) -> list[str]:
        """`allowed_tools` é o trecho que vem depois de `allowed-tools:` — pode ocupar várias linhas."""
        texto = SKILL_VALIDA.replace('allowed-tools: "Read"', f"allowed-tools:{allowed_tools}")
        self.assertNotEqual(texto, SKILL_VALIDA)
        alvo = self.dir / "SKILL.md"
        alvo.write_text(texto, encoding="utf-8")
        return [p for p in lint_skill.lint(alvo) if "Bash" in p]

    def _aprova(self, allowed_tools: str) -> None:
        self.assertEqual(self._problemas(allowed_tools), [], allowed_tools)

    def _reprova(self, allowed_tools: str) -> None:
        problemas = self._problemas(allowed_tools)
        self.assertEqual(len(problemas), 1, (allowed_tools, problemas))
        self.assertIn("especificador", problemas[0])

    def test_string_com_bash_solto_reprova(self):
        self._reprova(' "Read Write Edit Bash Glob Grep"')

    def test_string_sem_aspas_com_bash_solto_reprova(self):
        self._reprova(" Read Bash")

    def test_string_so_com_bash_solto_reprova(self):
        self._reprova(' "Bash"')

    def test_string_com_bash_solto_depois_de_um_com_especificador_reprova(self):
        self._reprova(' "Bash(git status *) Bash"')

    def test_string_com_bash_so_com_asterisco_reprova(self):
        """`Bash(*)` casa qualquer comando — é o `Bash` solto com outra grafia."""
        self._reprova(' "Read Bash(*) Glob"')

    def test_bash_com_asterisco_e_espacos_reprova(self):
        self._reprova(' "Read Bash( * )"')

    def test_bash_com_asterisco_depois_de_um_especificador_reprova(self):
        self._reprova(' "Bash(git status *) Bash(*)"')

    def test_string_com_a_regra_do_dc_aprova(self):
        self._aprova(f' "Read Write Edit Glob Grep {self.REGRA_DC}"')

    def test_string_com_bash_e_especificador_aprova(self):
        self._aprova(' "Read Bash(git status *)"')

    def test_especificador_que_so_termina_em_asterisco_aprova(self):
        """O `*` só equivale a `Bash` solto quando é o especificador inteiro."""
        self._aprova(' "Bash(git *) Bash(npm run *)"')

    def test_string_sem_bash_aprova(self):
        self._aprova(' "Read Write Edit Glob Grep"')

    def test_outra_ferramenta_com_bash_no_nome_nao_conta(self):
        self._aprova(' "Read BashOutput"')

    def test_lista_em_bloco_com_bash_solto_reprova(self):
        self._reprova("\n  - Read\n  - Bash\n  - Glob")

    def test_lista_em_bloco_com_bash_solto_entre_aspas_reprova(self):
        self._reprova('\n  - Read\n  - "Bash"')

    def test_lista_em_bloco_com_especificador_aprova(self):
        self._aprova("\n  - Read\n  - 'Bash(git status *)'")

    def test_lista_em_bloco_com_bash_asterisco_reprova(self):
        self._reprova("\n  - Read\n  - 'Bash(*)'")

    def test_lista_em_linha_com_bash_asterisco_reprova(self):
        self._reprova(' [Read, "Bash(*)"]')

    def test_lista_em_linha_com_bash_solto_reprova(self):
        self._reprova(' [Read, Bash, Glob]')

    def test_lista_em_linha_com_especificador_aprova(self):
        self._aprova(' [Read, "Bash(git status *)"]')

    def test_a_lista_termina_no_proximo_campo(self):
        """`Bash` em outro campo, depois da lista, não é do `allowed-tools`."""
        texto = SKILL_VALIDA.replace('allowed-tools: "Read"', "allowed-tools:\n  - Read")
        texto = texto.replace("tags: []", "tags: [Bash]")
        alvo = self.dir / "SKILL.md"
        alvo.write_text(texto, encoding="utf-8")
        self.assertEqual(lint_skill.lint(alvo), [])


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
