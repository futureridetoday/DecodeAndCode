#!/usr/bin/env python3
"""Testes de `activation_notice` e dos três hooks de `.claude/hooks/` — unidade 0001-05.

Quatro classes cobrem o mecanismo puro (`TestAnunciar*`, `TestEstado`), uma cobre a ausência de
instância no módulo (mesmo padrão de `test_guardrail.py`), e `TestHooksReais` roda os três pontos
de entrada de verdade, via subprocesso com stdin/stdout/stderr — o oráculo que a norma pede: "o
hook recusa o caso proibido e deixa passar o permitido" vale aqui como "o hook anuncia o que deve
e cala o que não deve". Cada teste de hook real usa um `session_id` próprio (`uuid4`) para não
colidir com nenhuma sessão real nem com outro teste, e limpa os arquivos de estado/log que criar.
"""

from __future__ import annotations

import json
import subprocess
import sys
import tempfile
import unittest
import uuid
from pathlib import Path
from tempfile import gettempdir

sys.path.insert(0, str(Path(__file__).resolve().parent))
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import activation_notice
import lib


class TestAnunciarInstructionsLoaded(unittest.TestCase):
    def test_payload_completo_produz_anuncio_com_arquivo_e_load_reason(self):
        anuncio = activation_notice.anunciar_instructions_loaded(
            {"file_path": "/repo/.claude/rules/exemplo.md", "load_reason": "path_glob_match"}
        )
        self.assertIn("/repo/.claude/rules/exemplo.md", anuncio)
        self.assertIn("path_glob_match", anuncio)

    def test_load_reason_bruto_nao_e_traduzido(self):
        for motivo in ("session_start", "path_glob_match", "compact", "nested_traversal", "include"):
            with self.subTest(motivo=motivo):
                anuncio = activation_notice.anunciar_instructions_loaded(
                    {"file_path": "/repo/CLAUDE.md", "load_reason": motivo}
                )
                self.assertIn(motivo, anuncio)

    def test_sem_file_path_produz_silencio(self):
        self.assertIsNone(
            activation_notice.anunciar_instructions_loaded({"load_reason": "session_start"})
        )

    def test_sem_load_reason_produz_silencio(self):
        self.assertIsNone(
            activation_notice.anunciar_instructions_loaded({"file_path": "/repo/CLAUDE.md"})
        )

    def test_payload_vazio_produz_silencio_nunca_mensagem_vazia(self):
        anuncio = activation_notice.anunciar_instructions_loaded({})
        self.assertIsNone(anuncio)


class TestRuleComPaths(unittest.TestCase):
    def test_globs_presente_devolve_file_path(self):
        caminho = activation_notice.rule_com_paths(
            {
                "file_path": "/repo/.claude/rules/hub-front.md",
                "load_reason": "path_glob_match",
                "globs": ["hub/app/**"],
            }
        )
        self.assertEqual(caminho, "/repo/.claude/rules/hub-front.md")

    def test_sem_globs_devolve_none(self):
        self.assertIsNone(
            activation_notice.rule_com_paths({"file_path": "/repo/CLAUDE.md", "load_reason": "session_start"})
        )

    def test_globs_vazia_devolve_none(self):
        self.assertIsNone(
            activation_notice.rule_com_paths(
                {"file_path": "/repo/.claude/rules/x.md", "load_reason": "path_glob_match", "globs": []}
            )
        )


class TestAnunciarPostCompact(unittest.TestCase):
    def test_nomeia_o_que_nao_voltou(self):
        anuncio = activation_notice.anunciar_post_compact(
            ativas_antes=["a.md", "b.md"], voltaram=["a.md"]
        )
        self.assertIn("b.md", anuncio)
        self.assertNotIn("a.md", anuncio)

    def test_silencio_quando_todas_voltaram(self):
        self.assertIsNone(
            activation_notice.anunciar_post_compact(ativas_antes=["a.md"], voltaram=["a.md"])
        )

    def test_silencio_quando_nao_havia_nenhuma_ativa(self):
        self.assertIsNone(activation_notice.anunciar_post_compact(ativas_antes=[], voltaram=[]))


class TestAnunciarSubagentStart(unittest.TestCase):
    def test_payload_completo_nomeia_tipo_e_id(self):
        anuncio = activation_notice.anunciar_subagent_start(
            {"agent_type": "Explore", "agent_id": "agent-abc123"}
        )
        self.assertIn("Explore", anuncio)
        self.assertIn("agent-abc123", anuncio)

    def test_sem_agent_type_produz_silencio(self):
        self.assertIsNone(activation_notice.anunciar_subagent_start({"agent_id": "agent-abc123"}))

    def test_sem_agent_id_produz_silencio(self):
        self.assertIsNone(activation_notice.anunciar_subagent_start({"agent_type": "Explore"}))


class TestEstado(unittest.TestCase):
    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self._tmp.cleanup)
        self.estado = Path(self._tmp.name) / "rules-ativas.json"

    def test_ler_estado_inexistente_devolve_lista_vazia(self):
        self.assertEqual(activation_notice.ler_estado(self.estado), [])

    def test_registrar_acrescenta_sem_duplicar(self):
        activation_notice.registrar_estado(self.estado, "a.md")
        activation_notice.registrar_estado(self.estado, "b.md")
        activation_notice.registrar_estado(self.estado, "a.md")
        self.assertEqual(activation_notice.ler_estado(self.estado), ["a.md", "b.md"])

    def test_limpar_reseta_para_lista_vazia(self):
        activation_notice.registrar_estado(self.estado, "a.md")
        activation_notice.limpar_estado(self.estado)
        self.assertEqual(activation_notice.ler_estado(self.estado), [])

    def test_ler_estado_corrompido_devolve_lista_vazia(self):
        self.estado.write_text("isto não é json", encoding="utf-8")
        self.assertEqual(activation_notice.ler_estado(self.estado), [])


class TestSemInstancia(unittest.TestCase):
    """`activation_notice.py` é mecanismo do plugin — não conhece nome de projeto nenhum."""

    def test_sem_termos_de_instancia_no_modulo(self):
        fonte = Path(activation_notice.__file__).read_text(encoding="utf-8")
        for termo in ("AmFlow", "Supabase", "hub-front"):
            with self.subTest(termo=termo):
                self.assertNotIn(termo, fonte)


class TestHooksReais(unittest.TestCase):
    """Os três pontos de entrada de `.claude/hooks/`, rodados como o Claude Code os roda."""

    @classmethod
    def setUpClass(cls):
        cls.hooks = lib.repo_root() / ".claude" / "hooks"
        for nome in ("instructions_loaded.py", "post_compact.py", "subagent_start.py"):
            if not (cls.hooks / nome).is_file():
                raise unittest.SkipTest(f"hook não encontrado: {cls.hooks / nome}")

    def setUp(self):
        self._sessao = f"teste-{uuid.uuid4().hex}"
        self._log = Path(gettempdir()) / f"decode-and-code-activation-{self._sessao}.log"
        self._estado = Path(gettempdir()) / f"decode-and-code-rules-ativas-{self._sessao}.json"
        self.addCleanup(self._log.unlink, missing_ok=True)
        self.addCleanup(self._estado.unlink, missing_ok=True)

    def _rodar(self, script: str, payload: dict) -> subprocess.CompletedProcess:
        return subprocess.run(
            [sys.executable, str(self.hooks / script)],
            input=json.dumps(payload),
            capture_output=True,
            text=True,
            timeout=10,
        )

    # -- instructions_loaded.py --------------------------------------------------

    def test_instructions_loaded_grava_anuncio_no_log_da_sessao(self):
        resultado = self._rodar(
            "instructions_loaded.py",
            {
                "session_id": self._sessao,
                "hook_event_name": "InstructionsLoaded",
                "file_path": "/repo/CLAUDE.md",
                "load_reason": "session_start",
            },
        )
        self.assertEqual(resultado.returncode, 0)
        self.assertEqual(resultado.stdout, "")
        self.assertIn("/repo/CLAUDE.md", self._log.read_text(encoding="utf-8"))

    def test_instructions_loaded_com_globs_registra_estado(self):
        resultado = self._rodar(
            "instructions_loaded.py",
            {
                "session_id": self._sessao,
                "hook_event_name": "InstructionsLoaded",
                "file_path": "/repo/.claude/rules/hub-front.md",
                "load_reason": "path_glob_match",
                "globs": ["hub/app/**"],
            },
        )
        self.assertEqual(resultado.returncode, 0)
        self.assertEqual(
            activation_notice.ler_estado(self._estado), ["/repo/.claude/rules/hub-front.md"]
        )

    def test_instructions_loaded_fora_do_escopo_nao_cria_log(self):
        resultado = self._rodar(
            "instructions_loaded.py",
            {"session_id": self._sessao, "hook_event_name": "InstructionsLoaded"},
        )
        self.assertEqual(resultado.returncode, 0)
        self.assertFalse(self._log.exists())

    def test_instructions_loaded_payload_malformado_nao_quebra(self):
        resultado = subprocess.run(
            [sys.executable, str(self.hooks / "instructions_loaded.py")],
            input="isto não é json",
            capture_output=True,
            text=True,
            timeout=10,
        )
        self.assertEqual(resultado.returncode, 0)
        self.assertEqual(resultado.stdout, "")

    # -- post_compact.py ----------------------------------------------------------

    def test_post_compact_nomeia_o_que_nao_voltou_e_limpa_o_estado(self):
        activation_notice.registrar_estado(self._estado, "/repo/.claude/rules/hub-front.md")
        activation_notice.registrar_estado(self._estado, "/repo/.claude/rules/data-arch.md")

        resultado = self._rodar(
            "post_compact.py",
            {"session_id": self._sessao, "hook_event_name": "PostCompact", "trigger": "auto"},
        )

        self.assertEqual(resultado.returncode, 2)
        self.assertIn("hub-front.md", resultado.stderr)
        self.assertIn("data-arch.md", resultado.stderr)
        self.assertEqual(activation_notice.ler_estado(self._estado), [])

    def test_post_compact_sem_estado_produz_silencio(self):
        resultado = self._rodar(
            "post_compact.py",
            {"session_id": self._sessao, "hook_event_name": "PostCompact", "trigger": "manual"},
        )
        self.assertEqual(resultado.returncode, 0)
        self.assertEqual(resultado.stderr, "")

    def test_post_compact_payload_malformado_nao_quebra(self):
        resultado = subprocess.run(
            [sys.executable, str(self.hooks / "post_compact.py")],
            input="isto não é json",
            capture_output=True,
            text=True,
            timeout=10,
        )
        self.assertEqual(resultado.returncode, 0)

    # -- subagent_start.py ---------------------------------------------------------

    def test_subagent_start_anuncia_por_stderr(self):
        resultado = self._rodar(
            "subagent_start.py",
            {
                "session_id": self._sessao,
                "hook_event_name": "SubagentStart",
                "agent_id": "agent-abc123",
                "agent_type": "Explore",
            },
        )
        self.assertEqual(resultado.returncode, 2)
        self.assertIn("Explore", resultado.stderr)
        self.assertIn("agent-abc123", resultado.stderr)

    def test_subagent_start_sem_campos_produz_silencio(self):
        resultado = self._rodar(
            "subagent_start.py", {"session_id": self._sessao, "hook_event_name": "SubagentStart"}
        )
        self.assertEqual(resultado.returncode, 0)
        self.assertEqual(resultado.stderr, "")

    def test_subagent_start_payload_malformado_nao_quebra(self):
        resultado = subprocess.run(
            [sys.executable, str(self.hooks / "subagent_start.py")],
            input="isto não é json",
            capture_output=True,
            text=True,
            timeout=10,
        )
        self.assertEqual(resultado.returncode, 0)


if __name__ == "__main__":
    unittest.main()
