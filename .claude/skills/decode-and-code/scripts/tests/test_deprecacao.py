#!/usr/bin/env python3
"""Teste da deprecação da `plan-dev-units` — unidade 0002-15.

O que dá valor ao teste é o par do critério de aceite: o diretório da skill
antiga deixou de existir, e nenhuma das duas referências vivas que o plano
aponta (0002-dev-units.md, seção Backlog) — `digital-twin-product/SKILL.md` e
a seção *Referências* de `modelo-dev-units.md` — ainda cita `plan-dev-units`.

A checagem de `modelo-dev-units.md` é escopada à seção `## Referências` — a
mesma que a Sequência da unidade nomeia (passo 4) —, não ao arquivo inteiro:
a norma também documenta a decisão de substituição no heading "Skill
`dev-units` — substitui `plan-dev-units`" (seção *Camada de execução*), que
cita o nome antigo de propósito e não é uma referência viva a atualizar.

O critério de aceite da unidade, lido ao pé da letra ("grep -rn 'plan-dev-units'
fora de legacy/, worktrees e docs/mvp/ não retorna nada"), também alcançaria
menções históricas dentro de `docs/plan/builder/0002-dev-units/` (o plano, esta
própria unidade, `11-skill-base.md`) e a nota de linhagem em
`dev-units/SKILL.md` ("Skill substituída: ... removida pela unidade 0002-15").
Nenhuma delas é referência viva — são registro permanente da intenção que gerou
as unidades (modelo-dev-units.md, seção *Plano e módulo são eixos diferentes*)
— e o próprio plano já restringe expressamente o alvo às duas referências
verificadas aqui. Por isso o teste não varre o repositório inteiro.
"""

from __future__ import annotations

import re
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import lib

ALVO = "plan-dev-units"

SKILL_ANTIGA = lib.repo_root() / ".claude" / "skills" / "plan-dev-units"
DIGITAL_TWIN_PRODUCT = (
    lib.repo_root() / ".claude" / "skills" / "digital-twin-product" / "SKILL.md"
)
MODELO_DEV_UNITS = lib.repo_root() / "docs" / "plan" / "system" / "modelo-dev-units.md"


def _secao(texto: str, nome: str) -> str:
    """Conteúdo de `## nome` até o próximo heading `## ` ou o fim do arquivo."""
    padrao = re.compile(rf"(?ms)^##\s+{re.escape(nome)}\s*$\n(.*?)(?=^##\s+|\Z)")
    m = padrao.search(texto)
    assert m, f"seção {nome!r} não encontrada em {MODELO_DEV_UNITS}"
    return m.group(1)


class TestDeprecacaoPlanDevUnits(unittest.TestCase):
    def test_diretorio_da_skill_antiga_nao_existe_mais(self):
        self.assertFalse(SKILL_ANTIGA.exists())

    def test_digital_twin_product_nao_cita_mais_a_skill_antiga(self):
        texto = DIGITAL_TWIN_PRODUCT.read_text(encoding="utf-8")
        self.assertNotIn(ALVO, texto)

    def test_secao_referencias_do_modelo_nao_aponta_mais_a_skill_antiga(self):
        texto = MODELO_DEV_UNITS.read_text(encoding="utf-8")
        secao = _secao(texto, "Referências")
        self.assertNotIn(ALVO, secao)


if __name__ == "__main__":
    unittest.main()
