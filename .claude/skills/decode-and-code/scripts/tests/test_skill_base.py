#!/usr/bin/env python3
"""Teste da base das skills do método — unidades 0002-11 e `P-03`, e `P-06`.

Cobre o que `lint_skill.lint()` já verifica — frontmatter completo e o modo declarado no corpo — e
o que ele não vê: a topologia de `D-01`. São quatro skills — uma por modo e o `intake`, que antecede
o ciclo —, cada uma com o modelo e a invocação que pede; e `decode-and-code/` ficou só com o que
elas compartilham, sem `SKILL.md`. Comportamento de cada modo não é testado aqui — vive em
`test_modo_*`.

O `intake` (`P-06`, `D-03`) é o prompt de um subagent sem histórico, e o que ele carrega é caro:
a skill tem teto de tamanho, e a `description` também — ela entra em contexto em toda sessão.
"""

from __future__ import annotations

import sys
import textwrap
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import lib
import lint_skill
import regioes

SKILLS = lib.repo_root() / ".claude" / "skills"

# O `allowed-tools` das três (`P-14`, `D-05`): sem `Bash` solto, só o atalho `dc.py` da própria pasta da skill,
# nas duas grafias — com aspas e sem. A liberação casa o texto do comando, e o modelo às vezes tira as aspas.
# O valor é o texto do frontmatter como está — `ler_campo` não interpreta YAML, então a barra antes das
# aspas internas fica.
ALLOWED_TOOLS = (
    '"Read Write Edit Glob Grep Bash(python3 \\"${CLAUDE_SKILL_DIR}/dc.py\\" *) '
    'Bash(python3 ${CLAUDE_SKILL_DIR}/dc.py *)"'
)

# O `intake` pesquisa e grava esboço, então pede `WebFetch` restrito ao domínio da documentação do Claude
# Code — o único campo em que difere das outras três.
ALLOWED_TOOLS_INTAKE = (
    '"Read Write Edit Glob Grep WebFetch(domain:code.claude.com) '
    'Bash(python3 \\"${CLAUDE_SKILL_DIR}/dc.py\\" *) '
    'Bash(python3 ${CLAUDE_SKILL_DIR}/dc.py *)"'
)

# Tetos do `intake` (`P-06`): o `SKILL.md` inteiro em bytes, e a `description` em caracteres.
LIMITE_SKILL_MD_INTAKE = 4096
LIMITE_DESCRIPTION_INTAKE = 600

# Skill → modo que o corpo precisa citar. `model`, `disable-model-invocation` e `context` são o que
# a topologia decide: `derive` cria estrutura e move arquivos, então só se invoca de forma explícita;
# `implement` roda em fork. `agent` é `general-purpose` porque o nome curto de um agent do plugin
# não resolve numa skill de plugin e cai, sem aviso, no padrão (medido com Claude Code 2.1.300).
TOPOLOGIA = {
    "review-plan": {
        "modo": "review",
        "model": "opus",
        "disable-model-invocation": "false",
        "context": '""',
        "allowed-tools": ALLOWED_TOOLS,
    },
    "derive": {
        "modo": "derive",
        "model": "opus",
        "disable-model-invocation": "true",
        "context": '""',
        "allowed-tools": ALLOWED_TOOLS,
    },
    "implement": {
        "modo": "implement",
        "model": "sonnet",
        "allowed-tools": ALLOWED_TOOLS,
        "disable-model-invocation": "false",
        "context": "fork",
        "agent": "general-purpose",
        "background": "false",
    },
    "intake": {
        "modo": "intake",
        "model": "opus",
        "allowed-tools": ALLOWED_TOOLS_INTAKE,
        "disable-model-invocation": "false",
        "context": "fork",
        "agent": "general-purpose",
        "background": "false",
        "argument-hint": '"<pedido>"',
    },
}


def _descricao(skill: Path) -> str:
    """O texto do bloco `description: |` do frontmatter, sem a indentação — `ler_campo` só devolve o `|`."""
    linhas = skill.read_text(encoding="utf-8").splitlines()
    bloco: list[str] = []
    dentro = False
    for linha in linhas[1:]:
        if linha.strip() == "---":
            break
        if dentro:
            if linha.strip() and not linha.startswith(" "):
                break
            bloco.append(linha)
        elif linha.startswith("description:"):
            dentro = True
            resto = linha[len("description:") :].strip()
            if resto != "|":
                return resto
    return textwrap.dedent("\n".join(bloco)).strip()


class TestSkillBase(unittest.TestCase):
    def test_topologia_cobre_exatamente_as_skills_de_lib(self):
        """`TOPOLOGIA` é a especificação do D-01; `lib.SKILLS` é a lista de produção. Têm de coincidir."""
        self.assertEqual(set(TOPOLOGIA), set(lib.SKILLS))

    def test_cada_skill_aprova_com_o_proprio_modo(self):
        for nome, esperado in TOPOLOGIA.items():
            with self.subTest(skill=nome):
                self.assertEqual(lint_skill.lint(SKILLS / nome / "SKILL.md", modos=[esperado["modo"]]), [])

    def test_frontmatter_de_topologia(self):
        for nome, esperado in TOPOLOGIA.items():
            for campo, valor in esperado.items():
                if campo == "modo":
                    continue
                with self.subTest(skill=nome, campo=campo):
                    self.assertEqual(regioes.ler_campo(SKILLS / nome / "SKILL.md", campo), valor)

    def test_so_as_skills_em_fork_declaram_agent(self):
        for nome in ("review-plan", "derive"):
            with self.subTest(skill=nome):
                self.assertIsNone(regioes.ler_campo(SKILLS / nome / "SKILL.md", "agent"))

    def test_cada_skill_tem_o_atalho_dc_py(self):
        """`${CLAUDE_SKILL_DIR}/dc.py` precisa existir em cada pasta — é o que a regra de permissão casa.

        Que os quatro são idênticos e repassam argumentos e código de saída é de `test_dc.py`.
        """
        for nome in TOPOLOGIA:
            with self.subTest(skill=nome):
                self.assertTrue((SKILLS / nome / "dc.py").is_file())

    def test_skill_md_do_intake_cabe_no_teto_de_bytes(self):
        tamanho = len((SKILLS / "intake" / "SKILL.md").read_bytes())
        self.assertLessEqual(tamanho, LIMITE_SKILL_MD_INTAKE, f"{tamanho} bytes")

    def test_description_do_intake_cabe_no_teto_de_caracteres(self):
        descricao = _descricao(SKILLS / "intake" / "SKILL.md")
        self.assertTrue(descricao)
        self.assertLessEqual(len(descricao), LIMITE_DESCRIPTION_INTAKE, f"{len(descricao)} caracteres")

    def test_description_do_intake_tem_use_when_e_um_unico_exemplo(self):
        descricao = _descricao(SKILLS / "intake" / "SKILL.md")
        self.assertEqual(descricao.count("Use when"), 1)
        self.assertEqual(descricao.count("<example>"), 1)

    def test_pasta_compartilhada_nao_tem_skill_md(self):
        compartilhada = SKILLS / "decode-and-code"
        self.assertFalse((compartilhada / "SKILL.md").exists())
        self.assertTrue((compartilhada / "scripts").is_dir())
        self.assertTrue((compartilhada / "config.json").is_file())


if __name__ == "__main__":
    unittest.main()
