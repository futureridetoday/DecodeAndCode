#!/usr/bin/env python3
"""Testes de `empacotar.construir/verificar/materializar` — unidades 0001-16 e 0004-04.

Duas naturezas, e as duas são necessárias (`L-31`).

**Fonte sintética**, em `tempfile.TemporaryDirectory()` com `lib.repo_root` mockado — mesmo padrão
de `test_registry.py` e `test_scaffold.py` — para o **mecanismo**: manifesto, as quatro skills, a
pasta compartilhada com `scripts/tests/` e `__pycache__` para provar a exclusão, os três scripts de
desenvolvimento (`P-05`), quatro hooks e um `settings.json` com os quatro eventos e a âncora
`${CLAUDE_PROJECT_DIR}/.claude/hooks`.

**Fonte real**, em `TestPacoteRealEstaLimpo`, para a **instância**: constrói deste repositório e
exige `verificar() == []`. A primeira entrega tinha só a sintética, e ela respondia `[]` sobre uma
árvore montada para não conter marcador nenhum — enquanto o pacote real saía com o nome do projeto
no `SKILL.md` e dentro do `_CONTEUDO_INICIAL` de `porte.py`. Fixture prova o mecanismo, nunca a
instância; é a `L-28` num lugar novo, e a guideline `scripts.md` já normatiza a regra.

O `P-03` troca a skill única por três (`review-plan`, `derive`, `implement`) mais a pasta
compartilhada `decode-and-code/`, que guarda os scripts e não tem `SKILL.md`; os comandos saem do
pacote. O `P-06` converte o único agent na skill `intake` (`D-03`): o pacote passa a ter quatro
skills e nenhum `agents/`.

A `0004-04` acrescenta a norma-mecanismo e o `move-md` ao que `construir` leva. O `move-md` viaja
de graça — mora dentro da skill desde a `0004-04`, e `_copiar_skill` já copia a árvore inteira —,
então o caso que prova isso é contra o **repositório real** (`TestPacoteRealEstaLimpo`), não
fixture: é exatamente o arquivo que faltava quando `scaffold` morria no import. A norma tem fonte e
destino próprios (`docs/plan/system/modelo-dev-units.md` → `reference/`, dentro da skill do
pacote), e por isso `_montar_fonte` ganha o arquivo no caminho real que `empacotar._fontes` agora
declara.

O `P-05` enxuga o pacote: os scripts de desenvolvimento (`empacotar`, `reconciliar` e `lint_skill`;
o lint de agent saiu com o agent, no `P-06`) e os hooks `PostCompact` e `SubagentStart` ficam só
neste repositório (`D-02`: `InstructionsLoaded` viaja). Os testes que usam `lint_skill` importam o
do **checkout**, porque o do pacote deixou de existir.

O `P-10` tira do `SKILL.md` empacotado todo campo de frontmatter fora da documentação oficial
(`empacotar._so_campos_oficiais`): o mecanismo, em `TestSoCamposOficiais`, com texto sintético; a
instância, em `TestPacoteRealEstaLimpo`, contra as quatro skills reais.
"""

from __future__ import annotations

import json
import re
import shutil
import subprocess
import sys
import tempfile
import unittest
import zipfile
from pathlib import Path
from unittest import mock

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import empacotar
import lib
import lint_skill


NOMES_DAS_SKILLS = lib.SKILLS

# Os quatro hooks da fonte (evento → script) e os dois que viajam (`P-05`, `D-02`).
_HOOKS_DA_FONTE = {
    "PreToolUse": "pre_tool_use.py",
    "InstructionsLoaded": "instructions_loaded.py",
    "PostCompact": "post_compact.py",
    "SubagentStart": "subagent_start.py",
}
_EVENTOS_QUE_VIAJAM = {"PreToolUse", "InstructionsLoaded"}
_HOOKS_QUE_VIAJAM = {"pre_tool_use.py", "instructions_loaded.py"}


def _montar_fonte(raiz: Path) -> None:
    """Escreve a árvore-fonte sintética sob `raiz` — o par completo que `construir` exige."""
    manifesto = raiz / ".claude" / "plugin.json"
    manifesto.parent.mkdir(parents=True, exist_ok=True)
    manifesto.write_text(
        json.dumps({"name": "exemplo", "version": "1.0.0"}, ensure_ascii=False), encoding="utf-8"
    )

    skills = raiz / ".claude" / "skills"
    for nome in NOMES_DAS_SKILLS:
        (skills / nome).mkdir(parents=True, exist_ok=True)
        # Um campo oficial e o bloco de rastreabilidade com o nome do repositório de origem: o build
        # precisa manter o primeiro e tirar o segundo (`P-10`).
        (skills / nome / "SKILL.md").write_text(
            f"---\n# ── nativos ──\nname: {nome}\n\n# ── amflow ──\nproject: {raiz.name}\n---\n# {nome} sintético\n",
            encoding="utf-8",
        )

    skill = skills / "decode-and-code"
    skill.mkdir(parents=True, exist_ok=True)
    (skill / "config.json").write_text("{}\n", encoding="utf-8")

    scripts = skill / "scripts"
    scripts.mkdir(parents=True, exist_ok=True)
    (scripts / "lib.py").write_text("# mecanismo\n", encoding="utf-8")
    (scripts / "move-md.py").write_text("# mecanismo — reescreve link markdown\n", encoding="utf-8")
    for nome in empacotar._SCRIPTS_DE_DESENVOLVIMENTO:
        (scripts / nome).write_text(f"# {nome} — só de quem desenvolve o método\n", encoding="utf-8")

    pycache = scripts / "__pycache__"
    pycache.mkdir(parents=True, exist_ok=True)
    (pycache / "lib.cpython-310.pyc").write_text("lixo de bytecode\n", encoding="utf-8")

    testes = scripts / "tests"
    testes.mkdir(parents=True, exist_ok=True)
    (testes / "test_lib.py").write_text("# prova daqui, não do método\n", encoding="utf-8")

    hooks = raiz / ".claude" / "hooks"
    hooks.mkdir(parents=True, exist_ok=True)
    for nome in _HOOKS_DA_FONTE.values():
        (hooks / nome).write_text(f"# {nome}\n", encoding="utf-8")

    settings = raiz / ".claude" / "settings.json"
    settings.write_text(
        json.dumps(
            {
                "hooks": {
                    evento: [
                        {
                            "matcher": "*",
                            "hooks": [
                                {
                                    "type": "command",
                                    "command": f'python3 "${{CLAUDE_PROJECT_DIR}}/.claude/hooks/{nome}"',
                                }
                            ],
                        }
                    ]
                    for evento, nome in _HOOKS_DA_FONTE.items()
                }
            }
        ),
        encoding="utf-8",
    )

    guardrails = raiz / ".claude" / "guardrails.json"
    guardrails.write_text(json.dumps({"rules": []}), encoding="utf-8")

    docs = raiz / "docs" / "plan" / "system"
    docs.mkdir(parents=True, exist_ok=True)
    (docs / "modelo-dev-units.md").write_text("# norma — mecanismo sintético\n", encoding="utf-8")


def _chaves_de_topo(skill_md: str) -> set[str]:
    """As chaves de topo do frontmatter de `skill_md` — oráculo próprio, não o de `empacotar`.

    Uma linha a cada vez, só as que começam em coluna zero com `chave:`; o que está indentado é
    continuação de um bloco, e o corpo depois do segundo `---` não entra.
    """
    linhas = skill_md.splitlines()
    fim = linhas.index("---", 1)
    return {m.group(1) for linha in linhas[1:fim] if (m := re.match(r"([\w-]+):", linha))}


def _escrever_pacote_minimo(raiz: Path, comando: str) -> None:
    """Pacote de plugin mínimo que o validador oficial aceita sem aviso próprio — `P-08`.

    Manifesto com `description` e `author` (sem eles o `--strict` reprova pelo manifesto) e um
    `hooks/hooks.json` com um único comando, o que o teste varia.
    """
    manifesto = raiz / ".claude-plugin" / "plugin.json"
    manifesto.parent.mkdir(parents=True)
    manifesto.write_text(
        json.dumps(
            {
                "name": "minimo",
                "version": "1.0.0",
                "description": "pacote sintético para o teste do validador",
                "author": {"name": "teste"},
            }
        ),
        encoding="utf-8",
    )

    hooks = raiz / "hooks"
    hooks.mkdir()
    (hooks / "hooks.json").write_text(
        json.dumps(
            {"hooks": {"PreToolUse": [{"matcher": "*", "hooks": [{"type": "command", "command": comando}]}]}}
        ),
        encoding="utf-8",
    )


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

    def test_manifesto_e_as_quatro_skills_presentes(self):
        empacotar.construir(self.destino)
        self.assertTrue((self.destino / ".claude-plugin" / "plugin.json").is_file())
        for nome in NOMES_DAS_SKILLS:
            with self.subTest(skill=nome):
                self.assertTrue((self.destino / "skills" / nome / "SKILL.md").is_file())

    def test_pasta_compartilhada_tem_scripts_e_config_e_nao_tem_skill_md(self):
        empacotar.construir(self.destino)
        compartilhada = self.destino / "skills" / "decode-and-code"
        self.assertFalse((compartilhada / "SKILL.md").exists())
        self.assertTrue((compartilhada / "scripts" / "lib.py").is_file())
        self.assertTrue((compartilhada / "config.json").is_file())

    def test_skills_perdem_o_bloco_de_rastreabilidade_e_o_nome_do_repositorio(self):
        """`P-10` — o `SKILL.md` empacotado fica com o campo oficial e sem o que a fonte guarda para si."""
        empacotar.construir(self.destino)
        for nome in NOMES_DAS_SKILLS:
            with self.subTest(skill=nome):
                texto = (self.destino / "skills" / nome / "SKILL.md").read_text(encoding="utf-8")
                self.assertEqual(texto, f"---\n# ── nativos ──\nname: {nome}\n---\n# {nome} sintético\n")
                self.assertNotIn(self.raiz.name, texto)

    def test_so_as_quatro_skills_e_a_compartilhada_viajam(self):
        """Uma skill de desenvolvimento do repositório não vaza: a lista é explícita, não `skills/*`."""
        so_de_desenvolvimento = self.raiz / ".claude" / "skills" / "so-de-desenvolvimento"
        so_de_desenvolvimento.mkdir()
        (so_de_desenvolvimento / "SKILL.md").write_text("# fica de fora\n", encoding="utf-8")

        empacotar.construir(self.destino)
        viajaram = {p.name for p in (self.destino / "skills").iterdir()}
        self.assertEqual(viajaram, {"decode-and-code", *NOMES_DAS_SKILLS})

    def test_fonte_de_skill_ausente_levanta_antes_de_escrever(self):
        (self.raiz / ".claude" / "skills" / "derive" / "SKILL.md").unlink()
        (self.raiz / ".claude" / "skills" / "derive").rmdir()

        with self.assertRaises(FileNotFoundError):
            empacotar.construir(self.destino)
        self.assertFalse(self.destino.exists())

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

    def test_so_os_dois_hooks_que_viajam_sao_copiados(self):
        """`P-05` — `hooks/` leva os scripts dos dois eventos que ficam, mais o `hooks.json`."""
        empacotar.construir(self.destino)
        copiados = {p.name for p in (self.destino / "hooks").iterdir()}
        self.assertEqual(copiados, {*_HOOKS_QUE_VIAJAM, "hooks.json"})

    def test_scripts_de_desenvolvimento_nao_viajam_na_pasta_compartilhada(self):
        """`P-05` — o `empacotar`, o `reconciliar` e o `lint_skill` só servem a quem desenvolve."""
        empacotar.construir(self.destino)
        scripts = self.destino / "skills" / "decode-and-code" / "scripts"
        for nome in empacotar._SCRIPTS_DE_DESENVOLVIMENTO:
            with self.subTest(script=nome):
                self.assertFalse((scripts / nome).exists())
        self.assertEqual({p.name for p in scripts.iterdir()}, {"lib.py", "move-md.py"})

    def test_a_exclusao_dos_scripts_de_desenvolvimento_e_so_da_pasta_compartilhada(self):
        """Uma skill que tenha um arquivo com um desses nomes não o perde em silêncio."""
        da_skill = self.raiz / ".claude" / "skills" / NOMES_DAS_SKILLS[0] / "lint_skill.py"
        da_skill.write_text("# parte da skill, não da pasta compartilhada\n", encoding="utf-8")

        empacotar.construir(self.destino)
        self.assertTrue((self.destino / "skills" / NOMES_DAS_SKILLS[0] / "lint_skill.py").is_file())

    def test_hook_citado_no_settings_sem_fonte_levanta_antes_de_escrever(self):
        (self.raiz / ".claude" / "hooks" / "instructions_loaded.py").unlink()

        with self.assertRaises(FileNotFoundError):
            empacotar.construir(self.destino)
        self.assertFalse(self.destino.exists())

    def test_pacote_nao_tem_agents_nem_quando_a_fonte_tem(self):
        """`P-06` — o único agent virou a skill `intake`; o pacote não copia agent de lugar nenhum."""
        agents = self.raiz / ".claude" / "agents"
        agents.mkdir()
        (agents / "qualquer.md").write_text("# agent que não viaja\n", encoding="utf-8")

        empacotar.construir(self.destino)
        self.assertFalse((self.destino / "agents").exists())
        self.assertEqual([], [str(p) for p in self.destino.rglob("qualquer.md")])

    def test_pacote_nao_tem_commands(self):
        """`P-03` — os comandos viraram skills, e `commands/` deixou de ser fonte e de ser destino."""
        empacotar.construir(self.destino)
        self.assertFalse((self.destino / "commands").exists())

    def test_hooks_json_so_os_dois_eventos_que_viajam_e_ancora_trocada(self):
        empacotar.construir(self.destino)

        eventos_settings = set(json.loads((self.raiz / ".claude" / "settings.json").read_text())["hooks"])
        self.assertEqual(eventos_settings, set(_HOOKS_DA_FONTE), "a fonte continua com os quatro")

        conteudo = (self.destino / "hooks" / "hooks.json").read_text(encoding="utf-8")
        eventos_gerados = set(json.loads(conteudo)["hooks"])

        self.assertEqual(eventos_gerados, _EVENTOS_QUE_VIAJAM)
        self.assertNotIn("CLAUDE_PROJECT_DIR", conteudo)
        self.assertIn("${CLAUDE_PLUGIN_ROOT}/hooks/pre_tool_use.py", conteudo)
        self.assertIn("${CLAUDE_PLUGIN_ROOT}/hooks/instructions_loaded.py", conteudo)

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

    def test_norma_entra_em_reference_dentro_da_skill(self):
        """`0004-04` — `construir` leva a norma-mecanismo para `reference/`, ao lado da skill."""
        empacotar.construir(self.destino)
        alvo = self.destino / "skills" / "decode-and-code" / "reference" / "modelo-dev-units.md"
        self.assertTrue(alvo.is_file())
        self.assertEqual(alvo.read_text(encoding="utf-8"), "# norma — mecanismo sintético\n")

    def test_move_md_viaja_dentro_do_scripts_da_skill(self):
        """`0004-04` — o `move-md` mora na skill e `_copiar_skill` já o leva, sem função própria."""
        empacotar.construir(self.destino)
        alvo = self.destino / "skills" / "decode-and-code" / "scripts" / "move-md.py"
        self.assertTrue(alvo.is_file())

    def test_fonte_norma_ausente_levanta_antes_de_escrever(self):
        (self.raiz / "docs" / "plan" / "system" / "modelo-dev-units.md").unlink()

        with self.assertRaises(FileNotFoundError):
            empacotar.construir(self.destino)
        self.assertFalse(self.destino.exists())


class TestSoCamposOficiais(unittest.TestCase):
    """`P-10` — o mecanismo que tira do frontmatter o que a documentação oficial não lista."""

    ENTRADA = (
        "---\n"
        "# ── claude code — campos nativos ──\n"
        "name: exemplo\n"
        "description: |\n"
        "  Primeiro parágrafo.\n"
        "\n"
        "  type: dentro do bloco, indentado — não é campo.\n"
        "\n"
        "model: opus\n"
        "allowed-tools: \"Read\"\n"
        "\n"
        "# ── amflow — rastreabilidade ──\n"
        "type: skill\n"
        "project: Exemplo\n"
        "tags: [a, b]\n"
        "dependencies:\n"
        "  - um\n"
        "  - dois\n"
        "scope:\n"
        "- tres\n"
        "\n"
        "hub_id: \"\"\n"
        "source: local\n"
        "---\n"
        "\n"
        "# Corpo\n"
        "\n"
        "type: no corpo, intocado\n"
        "---\n"
    )

    def test_tira_chave_continuacao_e_comentario_do_bloco_nao_oficial(self):
        esperado = (
            "---\n"
            "# ── claude code — campos nativos ──\n"
            "name: exemplo\n"
            "description: |\n"
            "  Primeiro parágrafo.\n"
            "\n"
            "  type: dentro do bloco, indentado — não é campo.\n"
            "\n"
            "model: opus\n"
            "allowed-tools: \"Read\"\n"
            "---\n"
            "\n"
            "# Corpo\n"
            "\n"
            "type: no corpo, intocado\n"
            "---\n"
        )
        self.assertEqual(empacotar._so_campos_oficiais(self.ENTRADA), esperado)

    def test_campo_oficial_vazio_ou_nao_continua_onde_esta(self):
        entrada = '---\nname: a\neffort: ""\ncontext: fork\n---\ncorpo\n'
        self.assertEqual(empacotar._so_campos_oficiais(entrada), entrada)

    def test_sem_frontmatter_fechado_volta_igual(self):
        for texto in ("", "# só corpo\n", "---\ntype: skill\n", "type: skill\n---\n"):
            with self.subTest(texto=texto):
                self.assertEqual(empacotar._so_campos_oficiais(texto), texto)


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

    def test_as_quatro_skills_empacotadas_so_declaram_campos_oficiais(self):
        """`P-10` — as chaves do `SKILL.md` empacotado são as da fonte que a lista oficial reconhece.

        Nem a mais (o bloco de rastreabilidade não viaja), nem a menos (nada oficial se perde). O corpo
        depois do frontmatter sai idêntico.
        """
        with tempfile.TemporaryDirectory() as tmp:
            destino = Path(tmp) / "pkg"
            empacotar.construir(destino)

            for nome in NOMES_DAS_SKILLS:
                with self.subTest(skill=nome):
                    fonte = (lib.repo_root() / ".claude" / "skills" / nome / "SKILL.md").read_text(encoding="utf-8")
                    empacotado = (destino / "skills" / nome / "SKILL.md").read_text(encoding="utf-8")

                    chaves_da_fonte = _chaves_de_topo(fonte)
                    chaves = _chaves_de_topo(empacotado)
                    self.assertLessEqual(chaves, empacotar._CAMPOS_OFICIAIS)
                    self.assertEqual(chaves, chaves_da_fonte & empacotar._CAMPOS_OFICIAIS)
                    # Contra um erro na própria lista: o que toda skill do método declara tem de sobreviver.
                    self.assertLessEqual({"name", "description", "model", "allowed-tools"}, chaves)
                    self.assertEqual(lint_skill._corpo(empacotado), lint_skill._corpo(fonte))

    def test_skills_empacotadas_citam_scripts_que_existem_no_pacote(self):
        """`P-01` e `P-03` — lint sobre a cópia empacotada, não sobre a fonte.

        `lint_skill` resolve `${CLAUDE_SKILL_DIR}/../decode-and-code/scripts/` contra o diretório da
        skill que recebe, então aqui prova que cada script citado viaja na pasta irmã, que o `..`
        resolve dentro do pacote, e que nenhum caminho fixo sobrou. O que o lint pode acusar é só a
        falta do bloco de rastreabilidade, que o pacote não leva (`P-10`): campo oficial ausente ainda
        reprova.
        """
        ausentes_do_pacote = {
            f"campo obrigatório ausente no frontmatter: {campo}"
            for campo in lint_skill.CAMPOS_FRONTMATTER
            if campo not in empacotar._CAMPOS_OFICIAIS
        }
        with tempfile.TemporaryDirectory() as tmp:
            destino = Path(tmp) / "pkg"
            empacotar.construir(destino)

            for nome in NOMES_DAS_SKILLS:
                with self.subTest(skill=nome):
                    skill = destino / "skills" / nome / "SKILL.md"
                    self.assertIn(
                        "${CLAUDE_SKILL_DIR}/../decode-and-code/scripts/", skill.read_text(encoding="utf-8")
                    )
                    self.assertEqual([p for p in lint_skill.lint(skill) if p not in ausentes_do_pacote], [])

    def test_pasta_compartilhada_do_pacote_real_nao_tem_skill_md(self):
        with tempfile.TemporaryDirectory() as tmp:
            destino = Path(tmp) / "pkg"
            empacotar.construir(destino)

            compartilhada = destino / "skills" / "decode-and-code"
            self.assertFalse((compartilhada / "SKILL.md").exists())
            self.assertTrue((compartilhada / "scripts").is_dir())
            self.assertTrue((compartilhada / "config.json").is_file())
            self.assertEqual(
                {p.name for p in (destino / "skills").iterdir()}, {"decode-and-code", *NOMES_DAS_SKILLS}
            )

    def test_pacote_real_tem_o_intake_e_nenhum_agent(self):
        """`P-06` e `D-03` — o `intake` viaja como skill, com o atalho `dc.py`; não há `agents/`."""
        with tempfile.TemporaryDirectory() as tmp:
            destino = Path(tmp) / "pkg"
            empacotar.construir(destino)

            self.assertTrue((destino / "skills" / "intake" / "SKILL.md").is_file())
            self.assertTrue((destino / "skills" / "intake" / "dc.py").is_file())
            self.assertFalse((destino / "agents").exists())
            self.assertEqual(empacotar.verificar(destino), [])

    def test_norma_e_move_md_presentes_no_pacote_real_e_verificar_continua_limpo(self):
        """Critério de aceite da `0004-04` — contra o repositório real, não fixture (`L-31`)."""
        with tempfile.TemporaryDirectory() as tmp:
            destino = Path(tmp) / "pkg"
            empacotar.construir(destino)

            norma = destino / "skills" / "decode-and-code" / "reference" / "modelo-dev-units.md"
            move_md = destino / "skills" / "decode-and-code" / "scripts" / "move-md.py"
            self.assertTrue(norma.is_file())
            self.assertTrue(move_md.is_file())
            self.assertIn("Modelo dev-units", norma.read_text(encoding="utf-8"))
            self.assertEqual(empacotar.verificar(destino), [])

    def test_hooks_json_gerado_cita_o_plugin_root_entre_aspas(self):
        """`P-08` — contra o `settings.json` real (`L-31`), sem precisar do `claude`.

        O validador acusa `${CLAUDE_PLUGIN_ROOT}` sem aspas, e o aviso nasce na fonte: o build só
        troca a âncora (`_escrever_hooks_json`), então as aspas do `settings.json` atravessam
        intactas. Este caso prende o que `validar` só pega quando o `claude` está instalado — e o
        teste vizinho de `TestValidarPelaFerramentaOficial` pula sem ele.
        """
        placeholder = "${CLAUDE_PLUGIN_ROOT}"
        with tempfile.TemporaryDirectory() as tmp:
            destino = Path(tmp) / "pkg"
            empacotar.construir(destino)

            eventos = json.loads((destino / "hooks" / "hooks.json").read_text(encoding="utf-8"))["hooks"]
            comandos = [
                hook["command"] for grupos in eventos.values() for grupo in grupos for hook in grupo["hooks"]
            ]

            ocorrencias = 0
            for comando in comandos:
                posicao = comando.find(placeholder)
                while posicao != -1:
                    ocorrencias += 1
                    with self.subTest(comando=comando):
                        # Entre aspas duplas: número ímpar de `"` antes, e uma que fecha depois.
                        self.assertEqual(comando[:posicao].count('"') % 2, 1, comando)
                        self.assertIn('"', comando[posicao + len(placeholder) :], comando)
                    posicao = comando.find(placeholder, posicao + 1)
            self.assertGreater(ocorrencias, 0, "nenhum comando cita o placeholder — o caso ficaria vácuo")

    def test_pacote_real_sem_commands_e_verificar_continua_limpo(self):
        """`P-03` — contra o repositório real, não fixture (`L-31`): nenhum `commands/` no pacote."""
        with tempfile.TemporaryDirectory() as tmp:
            destino = Path(tmp) / "pkg"
            empacotar.construir(destino)

            self.assertFalse((destino / "commands").exists())
            self.assertEqual(empacotar.verificar(destino), [])


class TestPacoteEnxuto(unittest.TestCase):
    """`P-05` e `D-02` — o que o pacote **real** não leva, e a prova de que nada faz falta.

    O sintético (`TestConstruir`) prova o mecanismo; só o repositório real diz que os três
    scripts de desenvolvimento e os dois hooks de anúncio podem sair (`L-31`).
    """

    def test_pacote_real_sem_os_tres_scripts_de_desenvolvimento(self):
        with tempfile.TemporaryDirectory() as tmp:
            destino = Path(tmp) / "pkg"
            empacotar.construir(destino)

            scripts = destino / "skills" / "decode-and-code" / "scripts"
            for nome in ("empacotar.py", "reconciliar.py", "lint_skill.py"):
                with self.subTest(script=nome):
                    self.assertFalse((scripts / nome).exists())
            self.assertTrue((scripts / "dc.py").is_file())
            self.assertEqual(empacotar.verificar(destino), [])

    def test_hooks_json_real_tem_so_os_dois_eventos_e_hooks_so_os_dois_scripts(self):
        with tempfile.TemporaryDirectory() as tmp:
            destino = Path(tmp) / "pkg"
            empacotar.construir(destino)

            fonte = json.loads((lib.repo_root() / ".claude" / "settings.json").read_text(encoding="utf-8"))
            self.assertEqual(set(fonte["hooks"]), set(_HOOKS_DA_FONTE), "a fonte continua com os quatro")

            hooks_json = json.loads((destino / "hooks" / "hooks.json").read_text(encoding="utf-8"))["hooks"]
            self.assertEqual(set(hooks_json), _EVENTOS_QUE_VIAJAM)
            self.assertEqual({p.name for p in (destino / "hooks").glob("*.py")}, _HOOKS_QUE_VIAJAM)
            self.assertEqual(
                {p.name for p in (destino / "hooks").iterdir()}, {*_HOOKS_QUE_VIAJAM, "hooks.json"}
            )

    def test_cada_comando_do_hooks_json_aponta_para_um_script_do_pacote(self):
        """Uma fonte só: o `hooks/` do pacote sai dos comandos do `hooks.json`, nunca de lista à parte."""
        with tempfile.TemporaryDirectory() as tmp:
            destino = Path(tmp) / "pkg"
            empacotar.construir(destino)

            hooks_json = json.loads((destino / "hooks" / "hooks.json").read_text(encoding="utf-8"))["hooks"]
            citados = set()
            for grupos in hooks_json.values():
                for grupo in grupos:
                    for hook in grupo["hooks"]:
                        citados.update(re.findall(r"\$\{CLAUDE_PLUGIN_ROOT\}/hooks/([\w.-]+\.py)", hook["command"]))
            self.assertEqual(citados, {p.name for p in (destino / "hooks").glob("*.py")})

    def test_todo_script_e_hook_do_pacote_importa_sem_os_tres(self):
        """Nenhum runtime nem hook importa o que saiu — executado de verdade, não lido por `grep`.

        Subprocesso novo, `-I` e `cwd` sem projeto: `import` aqui devolveria o módulo já carregado
        da fonte, que tem os três ao lado. Os hooks entram por caminho, porque `hooks/` não está
        no `sys.path` — e o `sys.path.insert` de cada um aponta para o pacote, não para a fonte.
        """
        codigo = (
            "import importlib, importlib.util, sys\n"
            "from pathlib import Path\n"
            "pacote = Path(sys.argv[1])\n"
            "scripts = pacote / 'skills' / 'decode-and-code' / 'scripts'\n"
            "sys.path.insert(0, str(scripts))\n"
            "for arquivo in sorted(scripts.glob('*.py')):\n"
            "    if '-' not in arquivo.stem:\n"
            "        importlib.import_module(arquivo.stem)\n"
            "for arquivo in sorted((pacote / 'hooks').glob('*.py')):\n"
            "    spec = importlib.util.spec_from_file_location('hook_' + arquivo.stem, arquivo)\n"
            "    spec.loader.exec_module(importlib.util.module_from_spec(spec))\n"
            "print('importou')\n"
        )
        with tempfile.TemporaryDirectory() as tmp_pacote, tempfile.TemporaryDirectory() as tmp_cwd:
            destino = Path(tmp_pacote) / "pkg"
            empacotar.construir(destino)

            resultado = subprocess.run(
                [sys.executable, "-I", "-c", codigo, str(destino)],
                cwd=Path(tmp_cwd).resolve(),
                capture_output=True,
                text=True,
            )

            self.assertEqual(resultado.returncode, 0, resultado.stdout + resultado.stderr)
            self.assertIn("importou", resultado.stdout)


class TestEmpacotarZip(unittest.TestCase):
    """`empacotar_zip` sobre o pacote real — par de `TestPacoteRealEstaLimpo` para o zip.

    `verificar`/`validar` sintéticos já têm caso próprio (`TestVerificar`,
    `TestValidarPelaFerramentaOficial`); aqui o alvo é o que só existe depois do zip: o conteúdo do
    archive, o gate que veste os dois antes de escrevê-lo, e o determinismo do hash.
    """

    def _construir_e_zipar(self, tmp: str):
        """`None` quando `claude` está ausente — `empacotar_zip` recusa, sem exceção, sem zip."""
        destino = Path(tmp) / "pkg"
        empacotar.construir(destino)
        if shutil.which("claude") is None:
            with self.assertRaises(RuntimeError):
                empacotar.empacotar_zip(destino)
            return None
        caminho_zip, sha256 = empacotar.empacotar_zip(destino)
        self.addCleanup(lambda: caminho_zip.unlink(missing_ok=True))
        return destino, caminho_zip, sha256

    def test_zip_contem_manifesto_no_nivel_zero_e_parseavel(self):
        with tempfile.TemporaryDirectory() as tmp:
            resultado = self._construir_e_zipar(tmp)
            if resultado is None:
                return
            _, caminho_zip, _ = resultado

            with zipfile.ZipFile(caminho_zip) as zf:
                self.assertIn(".claude-plugin/plugin.json", zf.namelist())
                manifesto = json.loads(zf.read(".claude-plugin/plugin.json"))
            self.assertEqual(manifesto["name"], "decode-and-code")

    def test_verificar_e_validar_ficam_limpos_sobre_o_staging_do_zip(self):
        with tempfile.TemporaryDirectory() as tmp:
            resultado = self._construir_e_zipar(tmp)
            if resultado is None:
                return
            destino, _, _ = resultado
            self.assertEqual(empacotar.verificar(destino), [])
            self.assertEqual(empacotar.validar(destino), [])

    def test_sha256_tem_64_hex_e_e_igual_entre_duas_construcoes(self):
        with tempfile.TemporaryDirectory() as tmp1, tempfile.TemporaryDirectory() as tmp2:
            resultado1 = self._construir_e_zipar(tmp1)
            if resultado1 is None:
                return
            _, zip1, sha1 = resultado1
            self.assertRegex(sha1, r"^[0-9a-f]{64}$")
            conteudo1 = zip1.read_bytes()

            _, zip2, sha2 = self._construir_e_zipar(tmp2)
            self.assertEqual(sha1, sha2)
            self.assertEqual(conteudo1, zip2.read_bytes())

    def test_nao_escreve_zip_se_verificar_ou_validar_reprovarem(self):
        """Confere preservação, nunca ausência — `esperado` é o caminho real de release
        (`lib.repo_root()`, versão do `plugin.json`), e pode já existir de um build anterior. Um
        `assertFalse(esperado.exists())` reprovaria (e o cleanup apagaria) um zip legítimo que já
        estivesse lá; o gate provado aqui é que a chamada reprovada não o toca, exista ele ou não.
        """
        with tempfile.TemporaryDirectory() as tmp:
            destino = Path(tmp) / "pkg"
            empacotar.construir(destino)
            versao = json.loads(
                (destino / ".claude-plugin" / "plugin.json").read_text(encoding="utf-8")
            )["version"]
            esperado = lib.repo_root() / f"decode-and-code-{versao}.zip"
            conteudo_antes = esperado.read_bytes() if esperado.exists() else None

            with mock.patch.object(empacotar, "validar", return_value=["forçado para o teste"]):
                with self.assertRaises(RuntimeError):
                    empacotar.empacotar_zip(destino)

            if conteudo_antes is None:
                self.assertFalse(esperado.exists(), "gate reprovado não deveria criar o zip")
            else:
                self.assertEqual(
                    esperado.read_bytes(), conteudo_antes, "gate reprovado não deveria tocar um zip preexistente"
                )


class TestScaffoldImportaDoPacote(unittest.TestCase):
    """Critério de aceite da `0004-04`: `scaffold` é o único dos 20 módulos que não importava a
    partir de um pacote instalado — o `move-md` ausente era a causa (`config.json`, `move_script`,
    resolvido contra a raiz do **projeto**, que um pacote solto não tem).

    O caso precisa rodar **fora deste processo**: `scaffold` já está importado no `sys.modules` de
    quem roda a suíte, e um `import scaffold` aqui devolveria o módulo já carregado, não provaria
    nada sobre o pacote. Um subprocesso novo, com `cwd` num diretório sem `.claude/` nem `docs/` ao
    redor, é o que reproduz "scripts fora de qualquer projeto" — a condição medida em 2026-08-27 com
    `claude --plugin-dir` a partir de `/tmp`.
    """

    def test_scaffold_importa_com_scripts_fora_de_qualquer_projeto(self):
        with tempfile.TemporaryDirectory() as tmp_pacote, tempfile.TemporaryDirectory() as tmp_cwd:
            destino = Path(tmp_pacote) / "pkg"
            empacotar.construir(destino)
            scripts_dir = destino / "skills" / "decode-and-code" / "scripts"

            cwd_sem_projeto = Path(tmp_cwd).resolve()
            self.assertFalse((cwd_sem_projeto / ".claude").exists())
            self.assertFalse((cwd_sem_projeto / "docs").exists())

            codigo = (
                "import sys\n"
                "sys.path.insert(0, sys.argv[1])\n"
                "import scaffold\n"
                "print('importou')\n"
            )
            resultado = subprocess.run(
                [sys.executable, "-c", codigo, str(scripts_dir)],
                cwd=cwd_sem_projeto,
                capture_output=True,
                text=True,
            )

            self.assertEqual(
                resultado.returncode, 0, resultado.stdout + resultado.stderr
            )
            self.assertIn("importou", resultado.stdout)


class TestValidarPelaFerramentaOficial(unittest.TestCase):
    """O par de `verificar`: um recusa instância, o outro confere estrutura contra o validador
    oficial. Caracterizado contra o binário real antes de escrito — o sinal é o returncode, a
    mensagem sai em stdout, e stderr fica vazio."""

    def test_pacote_real_passa_e_pacote_quebrado_reprova(self):
        """O caso contra a instância, com o braço contrário junto.

        Sem os dois o gate seria vácuo: a primeira tentativa de quebrar o pacote foi apagar o
        manifesto, e ele **continuou válido** — a doc diz que plugin precisa de manifesto **ou** de
        componentes, e o nosso tem `skills/` e `hooks/`. `name` ausente reprova de
        verdade, medido em 2026-08-27.

        Sem `claude` no `PATH`, afirma a degradação declarada. As duas pontas são comportamento
        real; nenhuma é skip.
        """
        with tempfile.TemporaryDirectory() as tmp:
            destino = Path(tmp) / "pkg"
            empacotar.construir(destino)

            if shutil.which("claude") is None:
                self.assertEqual(
                    empacotar.validar(destino),
                    ["claude não encontrado no PATH — validação oficial não executada"],
                )
                return

            self.assertEqual(empacotar.validar(destino), [])

            (destino / ".claude-plugin" / "plugin.json").write_text(
                json.dumps({"description": "sem name"}), encoding="utf-8"
            )
            self.assertTrue(empacotar.validar(destino), "manifesto sem 'name' devia reprovar")

    @unittest.skipUnless(shutil.which("claude"), "claude ausente do PATH — a validação real não roda")
    def test_aviso_de_plugin_root_sem_aspas_reprova_pela_ferramenta_de_verdade(self):
        """`P-08` — o **comando** montado, não a saída: só a ferramenta real responde à flag.

        Sem `--strict` o binário sai com `0` sobre aviso ("Validation passed with warnings") e
        `validar` devolvia `[]` — os quatro avisos de `${CLAUDE_PLUGIN_ROOT}` sem aspas passaram
        calados até 2026-10-15 (`scripts.md`, *Comando externo*). Mock de `subprocess.run` não pega
        isso: devolveria o que mandassem, com a flag ou sem ela.

        O pacote é mínimo e **o manifesto leva `description` e `author`** — medido: sem eles o
        `--strict` já reprova pelo manifesto, e o braço das aspas deixaria de provar que a única
        diferença entre os dois pacotes é a aspa. É o braço contrário que impede o gate vácuo.
        """
        with tempfile.TemporaryDirectory() as tmp:
            sem_aspas = Path(tmp) / "sem-aspas"
            com_aspas = Path(tmp) / "com-aspas"
            _escrever_pacote_minimo(sem_aspas, "python3 ${CLAUDE_PLUGIN_ROOT}/hooks/x.py")
            _escrever_pacote_minimo(com_aspas, 'python3 "${CLAUDE_PLUGIN_ROOT}/hooks/x.py"')

            problemas = empacotar.validar(sem_aspas)
            self.assertEqual(len(problemas), 1, problemas)
            self.assertIn("${CLAUDE_PLUGIN_ROOT} without quotes", problemas[0])

            self.assertEqual(empacotar.validar(com_aspas), [])

    def test_returncode_um_vira_problema_com_a_saida(self):
        saida = b"Validating...\n\xe2\x9c\x98 Found 1 error:\n  no manifest"
        with mock.patch.object(empacotar.subprocess, "run") as run:
            run.return_value.returncode = 1
            run.return_value.stdout = saida

            problemas = empacotar.validar("/qualquer")

        self.assertEqual(len(problemas), 1)
        self.assertIn("Found 1 error", problemas[0])

    def test_binario_ausente_devolve_problema_em_vez_de_levantar(self):
        with mock.patch.object(empacotar.subprocess, "run", side_effect=FileNotFoundError):
            problemas = empacotar.validar("/qualquer")

        self.assertEqual(problemas, ["claude não encontrado no PATH — validação oficial não executada"])


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
