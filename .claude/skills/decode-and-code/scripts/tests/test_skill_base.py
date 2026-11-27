#!/usr/bin/env python3
"""Teste da base das skills do método — unidades 0002-11 e `P-03`, e `P-06`.

Cobre o que `lint_skill.lint()` já verifica — frontmatter completo e o modo declarado no corpo — e
o que ele não vê: a topologia de `D-01`. São as skills de `lib.SKILLS` — uma por modo, o `decode`, que antecede
o ciclo, o `huddle`, o `setup` e o `rethink` —, cada uma com o modelo e a invocação que pede; e `decode-and-code/` ficou só com o que
elas compartilham, sem `SKILL.md`. O texto do corpo de cada modo não é testado: palavra no markdown
protege redação, não comportamento, e o que o corpo cita do `dc.py` é conferido por `test_dc.py`.

O `decode` (antes `intake`, `P-06`) roda na sessão, sem fork, porque conversa com o usuário: o tipo,
o objetivo e a proposta pedem a confirmação dele (codex, *Workflow* e *Decode*). A `description`
dele tem teto, porque entra em contexto em toda sessão, e o `SKILL.md` também.
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

# O `decode` confere schema de recurso do Claude Code, então pede `WebFetch` restrito ao domínio da
# documentação — o único campo em que difere das outras.
ALLOWED_TOOLS_DECODE = (
    '"Read Write Edit Glob Grep WebFetch(domain:code.claude.com) '
    'Bash(python3 \\"${CLAUDE_SKILL_DIR}/dc.py\\" *) '
    'Bash(python3 ${CLAUDE_SKILL_DIR}/dc.py *)"'
)

# Tetos do `decode` (`P-06`): o `SKILL.md` inteiro em bytes, e a `description` em caracteres.
LIMITE_SKILL_MD_DECODE = 6144
LIMITE_DESCRIPTION_DECODE = 600

# Skill → modo que o corpo precisa citar. `model`, `disable-model-invocation` e `context` são o que
# a topologia decide: `derive` cria estrutura e move arquivos, então só se invoca de forma explícita;
# `implement` roda em fork. `agent` é `general-purpose` porque o nome curto de um agent do plugin
# não resolve numa skill de plugin e cai, sem aviso, no padrão (medido com Claude Code 2.1.300).
# `None` é campo ausente: `context` só existe onde há fork (`P-10`, campo vazio não se declara).
TOPOLOGIA = {
    "review-plan": {
        "modo": "review",
        "model": "opus",
        "disable-model-invocation": "false",
        "context": None,
        "allowed-tools": ALLOWED_TOOLS,
    },
    "derive": {
        "modo": "derive",
        "model": "opus",
        "disable-model-invocation": "true",
        "context": None,
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
    # Subparte 2.2.06: o decode conversa com o usuário (tipo, objetivo, aprovação da proposta), e a
    # ferramenta de perguntas não existe em fork — por isso sem `context`.
    "decode": {
        "modo": "decode",
        "model": "opus",
        "allowed-tools": ALLOWED_TOOLS_DECODE,
        "disable-model-invocation": "false",
        "context": None,
        "background": "false",
        "argument-hint": '"<pedido>"',
    },
    # Plano 0008, T7: o huddle se abre quando a conversa acontece (`D-08` do `0001`), nunca por
    # iniciativa do modelo — por isso `disable-model-invocation: true`, como o `derive`.
    "huddle": {
        "modo": "huddle",
        "model": "opus",
        "disable-model-invocation": "true",
        "context": None,
        "allowed-tools": ALLOWED_TOOLS,
    },
    # Plano 0009, unidade 06: o setup conduz a conversa do primeiro uso. O modelo pode propô-lo depois
    # do aviso do SessionStart, e o primeiro passo é a confirmação; sem `context`, porque a ferramenta
    # de perguntas não existe em fork.
    "setup": {
        "modo": "setup",
        "model": "opus",
        "disable-model-invocation": "false",
        "context": None,
        "allowed-tools": ALLOWED_TOOLS,
    },
    # Plano 0020, tarefa 8: o rethink revisa a norma depois de uma mudança de rumo. Só a pessoa o
    # invoca (`D-07`), como o huddle; sem `context`, pela mesma razão do setup.
    "rethink": {
        "modo": "rethink",
        "model": "opus",
        "disable-model-invocation": "true",
        "context": None,
        "allowed-tools": ALLOWED_TOOLS,
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
        for nome in ("review-plan", "derive", "decode", "huddle", "setup", "rethink"):
            with self.subTest(skill=nome):
                self.assertIsNone(regioes.ler_campo(SKILLS / nome / "SKILL.md", "agent"))

    def test_cada_skill_tem_o_atalho_dc_py(self):
        """`${CLAUDE_SKILL_DIR}/dc.py` precisa existir em cada pasta — é o que a regra de permissão casa.

        Que os quatro são idênticos e repassam argumentos e código de saída é de `test_dc.py`.
        """
        for nome in TOPOLOGIA:
            with self.subTest(skill=nome):
                self.assertTrue((SKILLS / nome / "dc.py").is_file())

    def test_skill_md_do_decode_cabe_no_teto_de_bytes(self):
        tamanho = len((SKILLS / "decode" / "SKILL.md").read_bytes())
        self.assertLessEqual(tamanho, LIMITE_SKILL_MD_DECODE, f"{tamanho} bytes")

    def test_description_do_decode_cabe_no_teto_de_caracteres(self):
        descricao = _descricao(SKILLS / "decode" / "SKILL.md")
        self.assertTrue(descricao)
        self.assertLessEqual(len(descricao), LIMITE_DESCRIPTION_DECODE, f"{len(descricao)} caracteres")

    def test_description_do_decode_tem_use_when_e_um_unico_exemplo(self):
        descricao = _descricao(SKILLS / "decode" / "SKILL.md")
        self.assertEqual(descricao.count("Use when"), 1)
        self.assertEqual(descricao.count("<example>"), 1)

    def test_pasta_compartilhada_nao_tem_skill_md(self):
        compartilhada = SKILLS / "decode-and-code"
        self.assertFalse((compartilhada / "SKILL.md").exists())
        self.assertTrue((compartilhada / "scripts").is_dir())
        self.assertTrue((compartilhada / "config.json").is_file())


if __name__ == "__main__":
    unittest.main()
