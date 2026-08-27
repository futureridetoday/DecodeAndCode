#!/usr/bin/env python3
"""Testes de `empacotar.construir/verificar/materializar` — unidade 0001-16.

Duas naturezas, e as duas são necessárias (`L-31`).

**Fonte sintética**, em `tempfile.TemporaryDirectory()` com `lib.repo_root` mockado — mesmo padrão
de `test_registry.py` e `test_scaffold.py` — para o **mecanismo**: manifesto, skill com
`scripts/tests/` e `__pycache__` para provar a exclusão, quatro hooks e um `settings.json` com a
âncora `${CLAUDE_PROJECT_DIR}/.claude/hooks`.

**Fonte real**, em `TestPacoteRealEstaLimpo`, para a **instância**: constrói deste repositório e
exige `verificar() == []`. A primeira entrega tinha só a sintética, e ela respondia `[]` sobre uma
árvore montada para não conter marcador nenhum — enquanto o pacote real saía com o nome do projeto
no `SKILL.md` e dentro do `_CONTEUDO_INICIAL` de `porte.py`. Fixture prova o mecanismo, nunca a
instância; é a `L-28` num lugar novo, e a guideline `scripts.md` já normatiza a regra.
"""

from __future__ import annotations

import json
import sys
import tempfile
import unittest
from pathlib import Path
from unittest import mock

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import empacotar
import lib


def _montar_fonte(raiz: Path) -> None:
    """Escreve a árvore-fonte sintética sob `raiz` — o par completo que `construir` exige."""
    manifesto = raiz / ".claude-plugin" / "plugin.json"
    manifesto.parent.mkdir(parents=True, exist_ok=True)
    manifesto.write_text(
        json.dumps({"name": "exemplo", "version": "1.0.0"}, ensure_ascii=False), encoding="utf-8"
    )

    skill = raiz / ".claude" / "skills" / "decode-and-code"
    skill.mkdir(parents=True, exist_ok=True)
    (skill / "SKILL.md").write_text("# skill sintética\n", encoding="utf-8")

    scripts = skill / "scripts"
    scripts.mkdir(parents=True, exist_ok=True)
    (scripts / "lib.py").write_text("# mecanismo\n", encoding="utf-8")

    pycache = scripts / "__pycache__"
    pycache.mkdir(parents=True, exist_ok=True)
    (pycache / "lib.cpython-310.pyc").write_text("lixo de bytecode\n", encoding="utf-8")

    testes = scripts / "tests"
    testes.mkdir(parents=True, exist_ok=True)
    (testes / "test_lib.py").write_text("# prova daqui, não do método\n", encoding="utf-8")

    hooks = raiz / ".claude" / "hooks"
    hooks.mkdir(parents=True, exist_ok=True)
    nomes_hooks = ("pre_tool_use.py", "instructions_loaded.py", "post_compact.py", "subagent_start.py")
    for nome in nomes_hooks:
        (hooks / nome).write_text(f"# {nome}\n", encoding="utf-8")

    agents = raiz / ".claude" / "agents"
    agents.mkdir(parents=True, exist_ok=True)
    (agents / "planner.md").write_text("# planner sintético\n", encoding="utf-8")
    (agents / "developer.md").write_text("# developer sintético\n", encoding="utf-8")

    settings = raiz / ".claude" / "settings.json"
    settings.write_text(
        json.dumps(
            {
                "hooks": {
                    "PreToolUse": [
                        {
                            "matcher": "*",
                            "hooks": [
                                {
                                    "type": "command",
                                    "command": "python3 ${CLAUDE_PROJECT_DIR}/.claude/hooks/pre_tool_use.py",
                                }
                            ],
                        }
                    ],
                    "PostCompact": [
                        {
                            "matcher": "*",
                            "hooks": [
                                {
                                    "type": "command",
                                    "command": "python3 ${CLAUDE_PROJECT_DIR}/.claude/hooks/post_compact.py",
                                }
                            ],
                        }
                    ],
                }
            }
        ),
        encoding="utf-8",
    )

    guardrails = raiz / ".claude" / "guardrails.json"
    guardrails.write_text(json.dumps({"rules": []}), encoding="utf-8")

    docs = raiz / "docs" / "plan"
    docs.mkdir(parents=True, exist_ok=True)
    (docs / "modelo-dev-units.md").write_text("# norma — registro deste projeto\n", encoding="utf-8")


class _BaseComFonteSintetica(unittest.TestCase):
    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self._tmp.cleanup)
        self.raiz = Path(self._tmp.name).resolve()
        _montar_fonte(self.raiz)

        patcher = mock.patch.object(lib, "repo_root", return_value=self.raiz)
        patcher.start()
        self.addCleanup(patcher.stop)

        self._tmp_destino = tempfile.TemporaryDirectory()
        self.addCleanup(self._tmp_destino.cleanup)
        self.destino = Path(self._tmp_destino.name).resolve() / "pacote"


class TestConstruir(_BaseComFonteSintetica):
    def test_devolve_lista_de_caminhos_que_existem(self):
        escritos = empacotar.construir(self.destino)
        self.assertTrue(escritos)
        for caminho in escritos:
            self.assertTrue(caminho.is_file(), f"não escrito: {caminho}")

    def test_manifesto_e_skill_md_presentes(self):
        empacotar.construir(self.destino)
        self.assertTrue((self.destino / ".claude-plugin" / "plugin.json").is_file())
        self.assertTrue((self.destino / "skills" / "decode-and-code" / "SKILL.md").is_file())
        self.assertTrue((self.destino / "skills" / "decode-and-code" / "scripts" / "lib.py").is_file())

    def test_sem_scripts_tests_sem_pycache_sem_guardrails_sem_docs(self):
        empacotar.construir(self.destino)
        self.assertFalse((self.destino / "skills" / "decode-and-code" / "scripts" / "tests").exists())
        self.assertFalse(
            any(self.destino.rglob("__pycache__")), "__pycache__ não deveria sobreviver ao empacotamento"
        )
        self.assertFalse((self.destino / ".claude" / "guardrails.json").exists())
        self.assertFalse((self.destino / "guardrails.json").exists())
        self.assertFalse((self.destino / "docs").exists())

    def test_ds_store_da_maquina_nao_entra_no_pacote(self):
        """`L-32` — a reconciliação da `0001-17` achou um dentro da skill, e o pacote o levava."""
        lixo = self.raiz / ".claude" / "skills" / "decode-and-code" / ".DS_Store"
        lixo.write_bytes(b"\x00\x01lixo do Finder")

        empacotar.construir(self.destino)
        self.assertEqual([], [str(p) for p in self.destino.rglob(".DS_Store")])

    def test_quatro_hooks_copiados(self):
        empacotar.construir(self.destino)
        copiados = {p.name for p in (self.destino / "hooks").glob("*.py")}
        self.assertEqual(
            copiados,
            {"pre_tool_use.py", "instructions_loaded.py", "post_compact.py", "subagent_start.py"},
        )

    def test_dois_agentes_copiados(self):
        empacotar.construir(self.destino)
        copiados = {p.name for p in (self.destino / "agents").glob("*.md")}
        self.assertEqual(copiados, {"planner.md", "developer.md"})

    def test_hooks_json_mesmos_eventos_do_settings_e_ancora_trocada(self):
        empacotar.construir(self.destino)

        eventos_settings = set(json.loads((self.raiz / ".claude" / "settings.json").read_text())["hooks"])
        hooks_json = self.destino / "hooks" / "hooks.json"
        conteudo = hooks_json.read_text(encoding="utf-8")
        eventos_gerados = set(json.loads(conteudo)["hooks"])

        self.assertEqual(eventos_gerados, eventos_settings)
        self.assertNotIn("CLAUDE_PROJECT_DIR", conteudo)
        self.assertIn("${CLAUDE_PLUGIN_ROOT}/hooks/pre_tool_use.py", conteudo)

    def test_sempre_do_zero_remove_o_que_ja_estava_no_destino(self):
        self.destino.mkdir(parents=True)
        sobra = self.destino / "arquivo-antigo.txt"
        sobra.write_text("resto de uma build anterior\n", encoding="utf-8")

        empacotar.construir(self.destino)
        self.assertFalse(sobra.exists())

    def test_fonte_ausente_levanta_antes_de_escrever(self):
        (self.raiz / ".claude" / "hooks" / "pre_tool_use.py").unlink()
        for hook in (self.raiz / ".claude" / "hooks").glob("*.py"):
            hook.unlink()
        (self.raiz / ".claude" / "hooks").rmdir()

        with self.assertRaises(FileNotFoundError):
            empacotar.construir(self.destino)
        self.assertFalse(self.destino.exists())


class TestVerificar(_BaseComFonteSintetica):
    def test_arvore_recem_construida_esta_limpa(self):
        empacotar.construir(self.destino)
        self.assertEqual(empacotar.verificar(self.destino), [])

    def test_planta_nome_do_projeto_e_verificar_acusa(self):
        empacotar.construir(self.destino)
        plantado = self.destino / "skills" / "decode-and-code" / "vazamento.md"
        plantado.write_text(f"declara project: {self.raiz.name}\n", encoding="utf-8")

        problemas = empacotar.verificar(self.destino)
        self.assertTrue(any("vazamento.md" in p for p in problemas))

    def test_ancora_conta_dentro_de_hooks_e_nao_fora(self):
        """A decisão contrária da `L-31`: fora de `hooks/` a âncora é dado, dentro é hook quebrado."""
        empacotar.construir(self.destino)

        fora = self.destino / "skills" / "decode-and-code" / "scripts" / "constante.py"
        fora.write_text('ANCORA = "${CLAUDE_PROJECT_DIR}/.claude/hooks"\n', encoding="utf-8")
        self.assertEqual(empacotar.verificar(self.destino), [])

        dentro = self.destino / "hooks" / "vazado.py"
        dentro.write_text('caminho = "${CLAUDE_PROJECT_DIR}/.claude/hooks/x.py"\n', encoding="utf-8")
        problemas = empacotar.verificar(self.destino)
        self.assertTrue(any("vazado.py" in p for p in problemas))


class TestPacoteRealEstaLimpo(unittest.TestCase):
    """`L-31` — o par sintético prova a cópia; só este prova que **este** repositório empacota limpo.

    Sem ele, `verificar` respondia `[]` sobre uma árvore montada para não ter marcador nenhum,
    enquanto o pacote real saía com o nome do projeto no `SKILL.md` e dentro do `porte.py`. É a
    lição da `L-28` noutro lugar: mock — ou fixture — prova o mecanismo, nunca a instância.
    """

    def test_construir_do_repositorio_real_passa_em_verificar(self):
        with tempfile.TemporaryDirectory() as tmp:
            destino = Path(tmp) / "pkg"
            empacotar.construir(destino)
            self.assertEqual(empacotar.verificar(destino), [])

    def test_skill_empacotada_declara_o_plugin_e_nao_o_repositorio(self):
        with tempfile.TemporaryDirectory() as tmp:
            destino = Path(tmp) / "pkg"
            empacotar.construir(destino)

            texto = (destino / "skills" / "decode-and-code" / "SKILL.md").read_text(encoding="utf-8")
            self.assertIn("project: decode-and-code", texto)
            self.assertNotIn(f"project: {lib.repo_root().name}", texto)

    def test_dois_agentes_presentes_no_pacote_real(self):
        """`D-27` — os dois agentes viajam, e o `planner` deixou de citar caminho deste projeto."""
        with tempfile.TemporaryDirectory() as tmp:
            destino = Path(tmp) / "pkg"
            empacotar.construir(destino)

            self.assertTrue((destino / "agents" / "planner.md").is_file())
            self.assertTrue((destino / "agents" / "developer.md").is_file())


class TestMaterializar(unittest.TestCase):
    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self._tmp.cleanup)
        self.raiz = Path(self._tmp.name).resolve()

        self.origem = self.raiz / "fonte" / "minha-guideline.md"
        self.origem.parent.mkdir(parents=True, exist_ok=True)
        self.origem.write_text("---\nname: minha-guideline\n---\n\nCorpo.\n", encoding="utf-8")

        self.projeto = self.raiz / "projeto-alvo"
        self.projeto.mkdir(parents=True, exist_ok=True)

    def test_copia_para_claude_rules_do_projeto(self):
        destino = empacotar.materializar(self.origem, self.projeto)
        self.assertEqual(destino, self.projeto / ".claude" / "rules" / "minha-guideline.md")
        self.assertEqual(destino.read_text(encoding="utf-8"), self.origem.read_text(encoding="utf-8"))

    def test_destino_existente_levanta_e_preserva_conteudo(self):
        empacotar.materializar(self.origem, self.projeto)
        destino = self.projeto / ".claude" / "rules" / "minha-guideline.md"
        conteudo_antes = destino.read_text(encoding="utf-8")

        with self.assertRaises(FileExistsError):
            empacotar.materializar(self.origem, self.projeto)
        self.assertEqual(destino.read_text(encoding="utf-8"), conteudo_antes)

    def test_origem_ausente_levanta_e_nao_escreve(self):
        ausente = self.raiz / "fonte" / "nao-existe.md"
        with self.assertRaises(FileNotFoundError):
            empacotar.materializar(ausente, self.projeto)
        self.assertFalse((self.projeto / ".claude" / "rules").exists())


if __name__ == "__main__":
    unittest.main()
