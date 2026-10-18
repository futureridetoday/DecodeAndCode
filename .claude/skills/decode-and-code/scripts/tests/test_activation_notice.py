#!/usr/bin/env python3
"""Testes de `activation_notice` e dos dois hooks de anúncio de `.claude/hooks/` — unidade 0001-05.

Duas classes cobrem o mecanismo puro (`TestAnunciar*`), uma cobre a ausência de instância no
módulo (mesmo padrão de `test_guardrail.py`), e `TestHooksReais` roda os dois pontos de entrada de
verdade, via subprocesso com stdin/stdout/stderr — o oráculo que a norma pede: "o hook recusa o
caso proibido e deixa passar o permitido" vale aqui como "o hook anuncia o que deve e cala o que
não deve". Cada teste de hook real usa um `session_id` próprio (`uuid4`) para não colidir com
nenhuma sessão real nem com outro teste, e limpa o arquivo de log que criar.
"""

from __future__ import annotations

import json
import subprocess
import sys
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


class TestSemInstancia(unittest.TestCase):
    """`activation_notice.py` é mecanismo do plugin — não conhece nome de projeto nenhum."""

    def test_sem_termos_de_instancia_no_modulo(self):
        fonte = Path(activation_notice.__file__).read_text(encoding="utf-8")
        for termo in ("AmFlow", "Supabase", "hub-front"):
            with self.subTest(termo=termo):
                self.assertNotIn(termo, fonte)


class TestHooksReais(unittest.TestCase):
    """Os dois pontos de entrada de `.claude/hooks/`, rodados como o Claude Code os roda."""

    @classmethod
    def setUpClass(cls):
        cls.hooks = lib.repo_root() / ".claude" / "hooks"
        for nome in ("instructions_loaded.py", "subagent_start.py"):
            if not (cls.hooks / nome).is_file():
                raise unittest.SkipTest(f"hook não encontrado: {cls.hooks / nome}")

    def setUp(self):
        self._sessao = f"teste-{uuid.uuid4().hex}"
        self._log = Path(gettempdir()) / f"decode-and-code-activation-{self._sessao}.log"
        self.addCleanup(self._log.unlink, missing_ok=True)

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
