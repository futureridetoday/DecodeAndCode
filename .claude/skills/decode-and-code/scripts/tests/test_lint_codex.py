#!/usr/bin/env python3
"""Testes dos lints do codex — parte 1.4 do plano do redesign.

Cada lint reprova um caso com o defeito que procura, plantado num codex sintético mínimo que,
sozinho, aprova. Os lints de estrutura e de dependência também rodam sobre o codex aprovado na 1.3,
que precisa passar limpo. O de repetição roda sobre as skills do DC e só aceita os trechos de
`REPETICOES_CONHECIDAS`, cada um com a subparte da migração que o remove (2.2): repetição nova
reprova, e trecho que saiu da skill tem de sair da lista.
"""

from __future__ import annotations

import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import lint_codex

FRONTMATTER = "---\nname: codex-teste\ntype: knowledge\n---\n\n# Teste\n\n"

SECAO_A = """\
## Alfa

**O que é:** um conceito de teste que vale para conferir o lint do codex inteiro.

- **Regras:** a etapa aprovada segue para a próxima só depois do sim do usuário.

**Ver também:** Beta.
"""

SECAO_B = """\
## Beta

**O que é:** outro conceito de teste.

**Ver também:** Alfa.
"""


class _CodexSintetico(unittest.TestCase):
    def setUp(self) -> None:
        self._tmp = tempfile.TemporaryDirectory()
        self.raiz = Path(self._tmp.name)
        self.codex = self.raiz / "codex"
        self.codex.mkdir()
        self.escrever("um.md", SECAO_A)
        self.escrever("dois.md", SECAO_B)

    def tearDown(self) -> None:
        self._tmp.cleanup()

    def escrever(self, nome: str, corpo: str) -> Path:
        caminho = self.codex / nome
        caminho.write_text(FRONTMATTER + corpo, encoding="utf-8")
        return caminho


class TestEstrutura(_CodexSintetico):
    def test_codex_sintetico_aprova(self) -> None:
        self.assertEqual(lint_codex.lint_estrutura(self.codex), [])

    def test_titulo_repetido_reprova(self) -> None:
        self.escrever("tres.md", SECAO_B)
        problemas = lint_codex.lint_estrutura(self.codex)
        self.assertTrue(any("título repetido" in p and "Beta" in p for p in problemas), problemas)

    def test_ver_tambem_para_titulo_inexistente_reprova(self) -> None:
        self.escrever("dois.md", SECAO_B.replace("Alfa.", "Alfa, Gama."))
        problemas = lint_codex.lint_estrutura(self.codex)
        self.assertTrue(any("'Gama'" in p for p in problemas), problemas)

    def test_secao_sem_ver_tambem_reprova(self) -> None:
        self.escrever("dois.md", SECAO_B.replace("**Ver também:** Alfa.\n", ""))
        problemas = lint_codex.lint_estrutura(self.codex)
        self.assertTrue(any("não tem **Ver também:**" in p for p in problemas), problemas)

    def test_secao_sem_o_que_e_reprova(self) -> None:
        self.escrever("dois.md", SECAO_B.replace("**O que é:** outro", "Outro"))
        problemas = lint_codex.lint_estrutura(self.codex)
        self.assertTrue(any("não abre com **O que é:**" in p for p in problemas), problemas)

    def test_secao_acima_do_teto_reprova(self) -> None:
        longa = SECAO_B.replace("\n**Ver também:**", "\n" + "- item\n" * 40 + "\n**Ver também:**")
        self.escrever("dois.md", longa)
        problemas = lint_codex.lint_estrutura(self.codex)
        self.assertTrue(any("acima do teto de 40" in p for p in problemas), problemas)


class TestDependencia(_CodexSintetico):
    NOMES = {"review-plan", "implement", "derive", "dc", "pre_tool_use"}
    PROJETOS = {"MeuProjeto"}

    def lint(self) -> list[str]:
        return lint_codex.lint_dependencia(self.codex, self.NOMES, self.PROJETOS)

    def plantar(self, frase: str) -> list[str]:
        self.escrever("dois.md", SECAO_B.replace("outro conceito de teste.", frase))
        return self.lint()

    def test_codex_sintetico_aprova(self) -> None:
        self.assertEqual(self.lint(), [])

    def test_termo_do_metodo_que_coincide_com_nome_de_skill_aprova(self) -> None:
        self.assertEqual(self.plantar("o derive prepara a unidade e o DC a executa."), [])

    def test_caminho_reprova(self) -> None:
        problemas = self.plantar("a regra mora em .claude/rules/x.md.")
        self.assertTrue(any("caminho" in p for p in problemas), problemas)

    def test_arquivo_com_extensao_reprova(self) -> None:
        problemas = self.plantar("quem confere é o porte.py.")
        self.assertTrue(any("caminho" in p and "porte.py" in p for p in problemas), problemas)

    def test_evento_de_hook_reprova(self) -> None:
        problemas = self.plantar("o bloqueio vem do PreToolUse.")
        self.assertTrue(any("evento de hook" in p for p in problemas), problemas)

    def test_comando_de_barra_reprova(self) -> None:
        problemas = self.plantar("o usuário chama /decode-and-code:setup.")
        self.assertTrue(any("comando de barra" in p for p in problemas), problemas)

    def test_versao_do_claude_code_reprova(self) -> None:
        problemas = self.plantar("vale desde o Claude Code 2.1.0.")
        self.assertTrue(any("versão" in p for p in problemas), problemas)

    def test_nome_de_skill_entre_crases_reprova(self) -> None:
        problemas = self.plantar("a etapa roda na skill `derive`.")
        self.assertTrue(any("nome de skill" in p and "derive" in p for p in problemas), problemas)

    def test_nome_com_hifen_solto_reprova(self) -> None:
        problemas = self.plantar("a revisão roda no review-plan.")
        self.assertTrue(any("review-plan" in p for p in problemas), problemas)

    def test_nome_do_projeto_reprova(self) -> None:
        problemas = self.plantar("como no MeuProjeto.")
        self.assertTrue(any("nome do projeto" in p for p in problemas), problemas)

    def test_frontmatter_nao_conta(self) -> None:
        caminho = self.codex / "dois.md"
        caminho.write_text("---\ndescription: lido por `derive` em .claude/x.py\n---\n\n" + SECAO_B, encoding="utf-8")
        self.assertEqual(self.lint(), [])

    def test_linha_do_problema_e_a_do_arquivo(self) -> None:
        problemas = self.plantar("o bloqueio vem do PreToolUse.")
        linha = next(
            i + 1
            for i, l in enumerate((self.codex / "dois.md").read_text(encoding="utf-8").split("\n"))
            if "PreToolUse" in l
        )
        self.assertTrue(any(p.startswith(f"dois.md:{linha}:") for p in problemas), problemas)


class TestNomes(unittest.TestCase):
    def test_nomes_lidos_do_disco(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            skills = Path(tmp) / "skills"
            (skills / "derive").mkdir(parents=True)
            (skills / "derive" / "SKILL.md").write_text("x", encoding="utf-8")
            (skills / "compartilhada" / "scripts").mkdir(parents=True)
            (skills / "compartilhada" / "scripts" / "lint_plano.py").write_text("", encoding="utf-8")
            (Path(tmp) / "hooks").mkdir()
            (Path(tmp) / "hooks" / "session_start.py").write_text("", encoding="utf-8")
            self.assertEqual(
                lint_codex.nomes_de_mecanismo(skills), {"derive", "lint_plano", "session_start"}
            )

    def test_nomes_de_projeto(self) -> None:
        nomes = lint_codex.nomes_de_projeto(Path("/x/MeuProjeto"), "org/meu-repo")
        self.assertEqual(nomes, {"MeuProjeto", "meu-repo"})
        self.assertEqual(lint_codex.nomes_de_projeto(None, None), set())


class TestRepeticao(_CodexSintetico):
    def alvo(self, texto: str) -> Path:
        caminho = self.raiz / "SKILL.md"
        caminho.write_text("---\nname: x\n---\n\n" + texto, encoding="utf-8")
        return caminho

    def test_alvo_sem_repeticao_aprova(self) -> None:
        alvo = self.alvo("A skill conduz o passo a passo sem repetir o método.\n")
        self.assertEqual(lint_codex.lint_repeticao(self.codex, [alvo]), [])

    def test_trecho_repetido_reprova_com_origem_e_linha(self) -> None:
        alvo = self.alvo("Primeira linha.\nAqui a etapa aprovada segue para a próxima só depois do sim.\n")
        problemas = lint_codex.lint_repeticao(self.codex, [alvo])
        self.assertEqual(len(problemas), 1, problemas)
        self.assertIn(f"{alvo}:6:", problemas[0])
        self.assertIn("um.md, Alfa", problemas[0])
        self.assertIn("a etapa aprovada segue para a próxima só depois do sim", problemas[0])

    def test_trecho_menor_que_a_janela_aprova(self) -> None:
        alvo = self.alvo("a etapa aprovada segue para\n")
        self.assertEqual(lint_codex.lint_repeticao(self.codex, [alvo]), [])

    def test_ver_tambem_e_rotulo_nao_contam(self) -> None:
        alvo = self.alvo("**O que é:** **Regras:** Ver também: Beta. Alfa, Beta, Gama, Delta e Épsilon.\n")
        self.assertEqual(lint_codex.lint_repeticao(self.codex, [alvo], janela=3), [])

    def test_alvos_padrao_incluem_foundation_quando_existe(self) -> None:
        skills = self.raiz / "skills"
        (skills / "setup").mkdir(parents=True)
        (skills / "setup" / "SKILL.md").write_text("x", encoding="utf-8")
        plan_root = self.raiz / "plan"
        (plan_root / "system").mkdir(parents=True)
        self.assertEqual(lint_codex.alvos_padrao(skills, plan_root), [skills / "setup" / "SKILL.md"])
        (plan_root / "system" / "foundation.md").write_text("x", encoding="utf-8")
        self.assertIn(plan_root / "system" / "foundation.md", lint_codex.alvos_padrao(skills, plan_root))


class TestCodexAprovado(unittest.TestCase):
    """O codex aprovado na 1.3 passa limpo nos lints de estrutura e de dependência."""

    def test_estrutura(self) -> None:
        self.assertEqual(lint_codex.lint_estrutura(lint_codex.CODEX_DIR), [])

    def test_dependencia(self) -> None:
        nomes = lint_codex.nomes_de_mecanismo(lint_codex.SKILLS_DIR)
        self.assertIn("review-plan", nomes)
        raiz = lint_codex.SKILLS_DIR.parent.parent
        projetos = lint_codex.nomes_de_projeto(raiz, None)
        self.assertEqual(lint_codex.lint_dependencia(lint_codex.CODEX_DIR, nomes, projetos), [])


# Repetição que ainda existe nas skills, com a subparte da migração que a remove. A lista só diminui.
REPETICOES_CONHECIDAS: dict[tuple[str, str], str] = {
    ("setup", "a mudança aproxima o projeto do objetivo"): "2.2.11",
    ("rethink", "depois de uma mudança de rumo"): "2.2.12",
}


def _repeticoes_nas_skills() -> set[tuple[str, str]]:
    """(skill, trecho) de cada repetição que o lint acha nas skills reais."""
    achadas = set()
    for problema in lint_codex.lint_repeticao(
        lint_codex.CODEX_DIR, lint_codex.alvos_padrao(lint_codex.SKILLS_DIR, None)
    ):
        caminho = problema.split(":", 1)[0]
        trecho = problema.rsplit(": '", 1)[1].rstrip("'")
        achadas.add((Path(caminho).parent.name, trecho))
    return achadas


class TestRepeticaoNasSkills(unittest.TestCase):
    """O lint de repetição sobre as skills do DC: só os trechos conhecidos, e todos eles."""

    def test_nenhuma_repeticao_nova(self) -> None:
        novas = _repeticoes_nas_skills() - set(REPETICOES_CONHECIDAS)
        self.assertEqual(novas, set(), "repetição do codex numa skill: cite a seção pelo título")

    def test_conhecida_que_saiu_sai_da_lista(self) -> None:
        sairam = set(REPETICOES_CONHECIDAS) - _repeticoes_nas_skills()
        self.assertEqual(sairam, set(), "trecho que saiu da skill tem de sair de REPETICOES_CONHECIDAS")

    def test_repeticao_plantada_reprova(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            skill = Path(tmp) / "nova" / "SKILL.md"
            skill.parent.mkdir()
            skill.write_text(
                "A proposta é escrita para o usuário, não para quem executa.\n", encoding="utf-8"
            )
            self.assertTrue(lint_codex.lint_repeticao(lint_codex.CODEX_DIR, [skill]))


class TestLinhaDeComando(unittest.TestCase):
    def test_estrutura_sai_zero_no_codex_aprovado(self) -> None:
        self.assertEqual(lint_codex.main(["estrutura"]), 0)

    def test_repeticao_sai_um_com_alvo_repetido(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            alvo = Path(tmp) / "alvo.md"
            alvo.write_text(
                "A proposta é escrita para o usuário, não para quem executa.\n", encoding="utf-8"
            )
            self.assertEqual(lint_codex.main(["repeticao", str(alvo)]), 1)


if __name__ == "__main__":
    unittest.main()
