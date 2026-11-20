#!/usr/bin/env python3
"""Teste declarado da unidade 0009-02 — `descoberta.py`, o inventário do projeto para o setup."""

from __future__ import annotations

import json
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import descoberta

GUIDELINE = "---\nname: g\ndescription: quando toca src\npaths:\n  - 'src/**'\n---\n# g\n"
PRINCIPIO = "---\nname: p\ndescription: sempre\n---\n# p\n"
REGRAS = {"regras": [{"nome": "sem-env", "ferramenta": "Write", "detector": "process\\.env", "mensagem": "m"}]}


class TestDescobrir(unittest.TestCase):
    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self._tmp.cleanup)
        self.p = Path(self._tmp.name).resolve()
        (self.p / ".claude" / "rules").mkdir(parents=True)
        (self.p / ".claude" / "CLAUDE.md").write_text("\n".join(f"l{i}" for i in range(100)), encoding="utf-8")
        (self.p / "components.json").write_text("{}", encoding="utf-8")
        (self.p / "src").mkdir()
        (self.p / "src" / "app.ts").write_text("x", encoding="utf-8")
        (self.p / ".claude" / "rules" / "g.md").write_text(GUIDELINE, encoding="utf-8")
        (self.p / ".claude" / "rules" / "p.md").write_text(PRINCIPIO, encoding="utf-8")
        self.guardrails = self.p / ".claude" / "guardrails.json"
        self.guardrails.write_text(json.dumps(REGRAS), encoding="utf-8")

    def test_fontes_so_as_da_tupla_com_trecho_limitado(self):
        r = descoberta.descobrir(self.p)
        self.assertEqual([f["caminho"] for f in r["fontes"]], [".claude/CLAUDE.md", "components.json"])
        self.assertEqual(len(r["fontes"][0]["trecho"].splitlines()), 60)

    def test_existentes(self):
        e = descoberta.descobrir(self.p)["existentes"]
        self.assertEqual((e["guidelines"], e["principios"], e["guardrails"], e["aviso"]), (["g"], ["p"], ["sem-env"], None))

    def test_guardrails_malformado_vira_aviso_sem_excecao(self):
        self.guardrails.write_text("{nao e json", encoding="utf-8")
        e = descoberta.descobrir(self.p)["existentes"]
        self.assertEqual(e["guardrails"], [])
        self.assertTrue(e["aviso"])

    def test_arquivo_ilegivel_vira_trecho_vazio(self):
        (self.p / "README.md").write_bytes(b"\xff\xfe\x00\xff")
        r = descoberta.descobrir(self.p)
        readme = next(f for f in r["fontes"] if f["caminho"] == "README.md")
        self.assertEqual(readme["trecho"], "")

    def test_sem_duplicata_e_glob_recursivo(self):
        (self.p / ".cursor" / "rules" / "sub").mkdir(parents=True)
        (self.p / ".cursor" / "rules" / "sub" / "a.mdc").write_text("a", encoding="utf-8")
        caminhos = [f["caminho"] for f in descoberta.descobrir(self.p)["fontes"]]
        self.assertIn(".cursor/rules/sub/a.mdc", caminhos)
        self.assertEqual(len(caminhos), len(set(caminhos)))

    def test_projeto_vazio(self):
        with tempfile.TemporaryDirectory() as d:
            r = descoberta.descobrir(Path(d))
        self.assertEqual(r["fontes"], [])
        self.assertEqual(r["existentes"], {"guidelines": [], "principios": [], "guardrails": [], "aviso": None})

    def test_formatar(self):
        texto = descoberta.formatar(descoberta.descobrir(self.p))
        self.assertIn("### components.json", texto)
        self.assertIn("## Já existe", texto)
        self.assertIn("Guardrails: sem-env", texto)

    def test_formatar_cerca_o_trecho_e_o_titulo_dele_fica_dentro(self):
        # M3 do 0013: `### <caminho>` colidia com os títulos do próprio trecho (`L-12` do 0009).
        trecho = "# Projeto\n\n### Uso\n\n```bash\nnpm run dev\n```\n"
        texto = descoberta.formatar({
            "fontes": [{"caminho": "README.md", "trecho": trecho}],
            "existentes": {"guidelines": [], "principios": [], "guardrails": [], "aviso": None},
        })
        self.assertIn("### README.md\n````\n# Projeto", texto)
        abre = texto.index("````\n")
        fecha = texto.index("\n````\n", abre + 1)
        self.assertLess(abre, texto.index("### Uso"))
        self.assertLess(texto.index("### Uso"), fecha)
        self.assertLess(texto.index("```bash"), fecha)


if __name__ == "__main__":
    unittest.main()
