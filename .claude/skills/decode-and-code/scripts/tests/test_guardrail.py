#!/usr/bin/env python3
"""Testes de `guardrail` e do hook `pre_tool_use.py` — unidade 0001-04.

O critério de aceite pede duas coisas de naturezas diferentes, e a suíte separa por classe.
`TestHookReal` roda `.claude/hooks/pre_tool_use.py` de verdade, via subprocesso com stdin/stdout,
contra a regra real de `.claude/guardrails.json` — é o oráculo que a norma pede para esta unidade:
"o hook recusa o caso proibido e deixa passar o permitido", não só a função interna. Os quatro
casos são os de `## Fixtures` na unidade, com a procedência que ela documenta: o primeiro é
verbatim de um incidente real do AmFlow; os outros três são autorais, porque o acervo não
registra nenhum `SELECT` de diagnóstico (`L-20`). `TestFalhaAberta` cobre os três jeitos de a
entrada estar quebrada, direto contra `guardrail.decidir` — mais barato que subir um processo
para cada um. `TestMecanismoSemInstancia` verifica por texto que `guardrail.py` não sabe o nome
de nenhum serviço, tabela ou projeto — a fronteira mecanismo/instância é o ponto central da
unidade, e fica verificável em vez de só declarada.
"""

from __future__ import annotations

import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import guardrail
import lib

# Caso 1 — verbatim de AmFlow:docs/plan/_inbox/notification-fk.md:80-86, o incidente que
# escolhe a regra (D-02 do plano). Recusado.
_DDL_DO_INCIDENTE = """\
alter table public.notifications
  drop constraint if exists notifications_hub_id_fkey;

alter table public.notifications
  add constraint notifications_hub_id_fkey
  foreign key (hub_id) references public.resources (hub_id);
"""

# Caso 2 — autoral (L-20: o acervo não registra nenhum SELECT de diagnóstico). O diagnóstico
# natural da mesma constraint do caso 1. Liberado.
_SELECT_DIAGNOSTICO = """\
select conname, pg_get_constraintdef(oid)
from pg_constraint
where conrelid = 'public.notifications'::regclass;
"""

# Caso 3 — autoral, o caso anti-substring: contém os verbos de DDL como substring — em coluna
# (created_at) e em literal ('alter') — sem ser DDL. Liberado; casar substring reprovaria este.
_SELECT_ANTI_SUBSTRING = """\
select id, created_at
from public.notifications
where note ilike '%alter%';
"""

# Caso 4 — o mesmo DDL do caso 1, agora escrito num arquivo de migration em vez de executado
# por execute_sql. Liberado: prova que a regra é sobre canal, não sobre o statement.
_CAMINHO_MIGRATION = "supabase/migrations/20260812120000_fix_notifications_hub_id_fkey.sql"


class TestHookReal(unittest.TestCase):
    """Os quatro casos de `## Fixtures`, rodados contra o hook e a regra reais do repositório."""

    @classmethod
    def setUpClass(cls):
        cls.hook = lib.repo_root() / ".claude" / "hooks" / "pre_tool_use.py"
        if not cls.hook.is_file():
            raise unittest.SkipTest(f"hook não encontrado: {cls.hook}")

    def _rodar(self, tool_name: str, tool_input: dict) -> subprocess.CompletedProcess:
        payload = json.dumps({"tool_name": tool_name, "tool_input": tool_input})
        return subprocess.run(
            [sys.executable, str(self.hook)],
            input=payload,
            capture_output=True,
            text=True,
            timeout=10,
        )

    def test_ddl_do_incidente_via_execute_sql_e_recusado(self):
        resultado = self._rodar("mcp__supabase__execute_sql", {"query": _DDL_DO_INCIDENTE})
        self.assertEqual(resultado.returncode, 0)
        saida = json.loads(resultado.stdout)
        decisao = saida["hookSpecificOutput"]
        self.assertEqual(decisao["permissionDecision"], "deny")
        self.assertIn("migration", decisao["permissionDecisionReason"])

    def test_select_diagnostico_e_liberado(self):
        resultado = self._rodar("mcp__supabase__execute_sql", {"query": _SELECT_DIAGNOSTICO})
        self.assertEqual(resultado.returncode, 0)
        self.assertEqual(resultado.stdout.strip(), "")

    def test_select_anti_substring_e_liberado(self):
        resultado = self._rodar("mcp__supabase__execute_sql", {"query": _SELECT_ANTI_SUBSTRING})
        self.assertEqual(resultado.returncode, 0)
        self.assertEqual(resultado.stdout.strip(), "")

    def test_mesmo_ddl_escrito_em_arquivo_de_migration_e_liberado(self):
        resultado = self._rodar(
            "Write", {"file_path": _CAMINHO_MIGRATION, "content": _DDL_DO_INCIDENTE}
        )
        self.assertEqual(resultado.returncode, 0)
        self.assertEqual(resultado.stdout.strip(), "")


class TestFalhaAberta(unittest.TestCase):
    """Payload malformado, regras ausentes e regra que levanta — todos liberam, nunca bloqueiam."""

    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self._tmp.cleanup)
        self.dir = Path(self._tmp.name)

    def _payload_valido(self) -> str:
        return json.dumps({"tool_name": "Bash", "tool_input": {"command": "echo oi"}})

    def test_payload_malformado_libera_e_avisa(self):
        regras = self.dir / "guardrails.json"
        regras.write_text(json.dumps({"regras": []}), encoding="utf-8")

        decisao, aviso = guardrail.decidir("isto não é json", regras)

        self.assertIsNone(decisao)
        self.assertIsNotNone(aviso)

    def test_arquivo_de_regras_ausente_libera_e_avisa(self):
        regras = self.dir / "nao-existe.json"

        decisao, aviso = guardrail.decidir(self._payload_valido(), regras)

        self.assertIsNone(decisao)
        self.assertIsNotNone(aviso)

    def test_regra_que_levanta_excecao_libera_e_avisa(self):
        regras = self.dir / "guardrails.json"
        regras.write_text(
            json.dumps(
                {
                    "regras": [
                        {
                            "nome": "quebrada",
                            "ferramenta": "(",  # regex inválido — não compila
                            "detector": ".*",
                            "mensagem": "nunca alcançada",
                        }
                    ]
                }
            ),
            encoding="utf-8",
        )

        decisao, aviso = guardrail.decidir(self._payload_valido(), regras)

        self.assertIsNone(decisao)
        self.assertIsNotNone(aviso)


class TestMecanismoSemInstancia(unittest.TestCase):
    """`guardrail.py` conhece a forma de uma regra, nunca o nome de um serviço ou projeto."""

    def test_sem_termos_de_instancia_no_modulo(self):
        fonte = Path(guardrail.__file__).read_text(encoding="utf-8")
        for termo in ("Supabase", "supabase", "notifications", "AmFlow", "DecodeAndCode"):
            with self.subTest(termo=termo):
                self.assertNotIn(termo, fonte)


if __name__ == "__main__":
    unittest.main()
