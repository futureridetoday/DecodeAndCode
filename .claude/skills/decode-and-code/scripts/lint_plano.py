#!/usr/bin/env python3
"""Lint de formato de plano por porte — unidade 0001-13.

Hoje existe **um** formato de plano, e ele cobra de uma correção de oito linhas a mesma estrutura
que cobra de um plano de vinte unidades (`B-01`). `plan_size` (`0001-12`) já declara o porte; este
módulo é o que verifica que o plano obedece o que o porte dele promete — a tabela de
*O que cada porte carrega* na norma (`modelo-dev-units.md`).

Segue o mesmo desenho de `lint_unidade.py`/`lint_skill.py`: só lê, devolve lista de problemas, nunca
levanta por conteúdo malformado — quem levanta por `plan_size` ausente ou fora do vocabulário é
`scaffold.aprovar` (`0001-12`), que é o gate de aprovação. Aqui, ausência ou valor inválido só entram
como problema na lista, porque este lint também roda sobre plano ainda no `_inbox`, antes da
aprovação existir.
"""

from __future__ import annotations

import re
from pathlib import Path

import lib
import regioes


def lint(plano: Path) -> list[str]:
    """Verifica se `plano` está no formato do porte que declara — lista vazia quando aprovado.

    `plan_size` ausente, vazio ou fora do vocabulário encerra a checagem ali: sem porte não há
    schema contra o qual conferir os demais blocos, e o problema devolvido nomeia exatamente isso.
    """
    try:
        plan_size = regioes.ler_campo(plano, "plan_size")
    except ValueError:
        return ["frontmatter ausente ou malformado — sem '---' de abertura e fechamento"]

    if not (plan_size and plan_size.strip()):
        return ["campo obrigatório ausente no frontmatter: plan_size"]

    plan_size = plan_size.strip()
    if plan_size not in lib.PLAN_SIZES_VALIDOS:
        return [f"plan_size fora do vocabulário {lib.PLAN_SIZES_VALIDOS}: {plan_size!r}"]

    corpo = _corpo(plano.read_text(encoding="utf-8"))
    problemas: list[str] = []
    problemas.extend(_checar_independencia(corpo, plan_size))
    problemas.extend(_checar_decomposicao(corpo, plan_size))
    problemas.extend(_checar_backlog(plano, plan_size))
    return problemas


def _corpo(texto: str) -> str:
    """Conteúdo após o frontmatter — o texto inteiro se não houver '---' de abertura."""
    linhas = texto.splitlines()
    if not linhas or linhas[0].strip() != "---":
        return texto
    for i in range(1, len(linhas)):
        if linhas[i].strip() == "---":
            return "\n".join(linhas[i + 1 :])
    return ""


def _tem_heading(corpo: str, nome: str) -> bool:
    return bool(re.search(rf"(?m)^##\s+{re.escape(nome)}\s*$", corpo))


def _checar_independencia(corpo: str, plan_size: str) -> list[str]:
    """`pequeno` recusa a seção; `grande` exige; `médio` dispensa — não checado nos dois sentidos."""
    tem = _tem_heading(corpo, "Independência")
    if plan_size == "pequeno" and tem:
        return ["pequeno não pode ter '## Independência' — porte sem decomposição não tem o que dividir"]
    if plan_size == "grande" and not tem:
        return ["grande exige '## Independência'"]
    return []


def _checar_decomposicao(corpo: str, plan_size: str) -> list[str]:
    """`médio` exige `## Tarefas`; `grande` exige `## Escopo`; `pequeno` não tem decomposição a checar."""
    if plan_size == "médio" and not _tem_heading(corpo, "Tarefas"):
        return ["médio exige '## Tarefas'"]
    if plan_size == "grande" and not _tem_heading(corpo, "Escopo"):
        return ["grande exige '## Escopo'"]
    return []


def _checar_backlog(plano: Path, plan_size: str) -> list[str]:
    """`pequeno` recusa a região; `médio` e `grande` exigem — projeção precisa ter onde escrever."""
    tem = regioes.ler_regiao(plano, "backlog") is not None
    if plan_size == "pequeno" and tem:
        return ["pequeno não pode ter região de backlog — sem decomposição, a projeção nunca escreveria ali"]
    if plan_size in ("médio", "grande") and not tem:
        return [f"{plan_size} exige região de backlog"]
    return []
