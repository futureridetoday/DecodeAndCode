#!/usr/bin/env python3
"""Os hooks `PreToolUse` e `InstructionsLoaded` gravando no log do projeto — plano 0018.

Rodados como subprocesso, os hooks de verdade da fonte, com `CLAUDE_PROJECT_DIR` num projeto
descartável: o que se afirma é o que o processo escreve, não a função interna.
"""

from __future__ import annotations

import json
import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import lib

HOOKS = lib.repo_root() / ".claude" / "hooks"
SEGREDO = "chave-que-nao-pode-ir-para-o-log"
REGRAS = {"regras": [{"nome": "sem-segredo", "ferramenta": "^Write$", "detector": "chave-que", "mensagem": "Não."}]}


class _Projeto(unittest.TestCase):
    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self._tmp.cleanup)
        self.p = Path(self._tmp.name).resolve()
        (self.p / ".claude").mkdir()
        (self.p / ".claude" / "guardrails.json").write_text(json.dumps(REGRAS), encoding="utf-8")
        (self.p / "docs" / "plan").mkdir(parents=True)
        (self.p / "docs" / "plan" / "_planos.md").write_text("x\n", encoding="utf-8")
        self.log = self.p / ".claude" / "log" / "eventos.jsonl"

    def rodar(self, hook: str, payload: dict) -> subprocess.CompletedProcess:
        return subprocess.run(
            [sys.executable, str(HOOKS / hook)],
            input=json.dumps(payload), capture_output=True, text=True, timeout=10,
            env={**os.environ, "CLAUDE_PROJECT_DIR": str(self.p)},
        )

    def eventos(self) -> list[dict]:
        return [json.loads(l) for l in self.log.read_text(encoding="utf-8").splitlines()]


class TestBloqueio(_Projeto):
    def test_bloqueio_vira_evento_sem_nada_do_tool_input(self):
        r = self.rodar("pre_tool_use.py", {"tool_name": "Write",
                                           "tool_input": {"file_path": "a.txt", "content": SEGREDO}})
        self.assertIn("deny", r.stdout)
        [evento] = self.eventos()
        self.assertEqual((evento["classe"], evento["regra"], evento["tool_name"]), ("bloqueio", "sem-segredo", "Write"))
        self.assertNotIn(SEGREDO, self.log.read_text(encoding="utf-8"))
        self.assertNotIn("a.txt", self.log.read_text(encoding="utf-8"))

    def test_chamada_liberada_nao_escreve(self):
        self.rodar("pre_tool_use.py", {"tool_name": "Write", "tool_input": {"file_path": "a.txt", "content": "ok"}})
        self.assertFalse(self.log.exists())


class TestAtivacao(_Projeto):
    PAYLOAD = {"session_id": "s1", "file_path": "/x/.claude/rules/ui.md", "load_reason": "path_glob_match"}

    def test_ativacao_vai_para_o_log_com_a_sessao(self):
        self.rodar("instructions_loaded.py", self.PAYLOAD)
        [evento] = self.eventos()
        self.assertEqual((evento["classe"], evento["sessao"]), ("ativacao", "s1"))
        self.assertIn("ui.md", evento["anuncio"])

    def test_hooks_simultaneos_nao_perdem_evento(self):
        """Medido em 2026-11-20: com ler-filtrar-reescrever, 4 a 6 de 10 hooks simultâneos sobreviviam."""
        processos = []
        for i in range(20):
            p = subprocess.Popen([sys.executable, str(HOOKS / "instructions_loaded.py")], stdin=subprocess.PIPE,
                                 text=True, env={**os.environ, "CLAUDE_PROJECT_DIR": str(self.p)})
            processos.append((p, json.dumps({**self.PAYLOAD, "file_path": f"/x/f{i}.md"})))
        for p, payload in processos:
            p.stdin.write(payload)
            p.stdin.close()
        for p, _ in processos:
            p.wait()
        self.assertEqual(len(self.eventos()), 20)

    def test_projeto_sem_bootstrap_nao_ganha_log(self):
        (self.p / "docs" / "plan" / "_planos.md").unlink()
        self.rodar("instructions_loaded.py", self.PAYLOAD)
        self.rodar("pre_tool_use.py", {"tool_name": "Write", "tool_input": {"content": SEGREDO}})
        self.assertFalse((self.p / ".claude" / "log").exists())


if __name__ == "__main__":
    unittest.main()
