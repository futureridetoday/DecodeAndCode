#!/usr/bin/env python3
"""Lint de formato de plano por porte — unidade 0001-13, e o formato 2 na subparte 2.2.05.

`plan_size` (`0001-12`) declara o porte; este módulo verifica que o plano obedece o que o porte dele
promete. A regra depende da versão do formato (`lib.formato`):

- **Formato 2** (codex, *Porte*, *Plano técnico*, *Independência entre planos*): todo plano tem
  `## Objetivo`, `## Histórias`, `## Independência` e `## Recursos` (a tabela de recursos do plano,
  que pode dizer que não há nenhum). O pequeno tem `## Tarefas` e nenhuma unidade; o médio tem
  `## Unidades` com exatamente uma linha numerada; o grande, com duas ou mais. A região de backlog é
  criada na aprovação (`scaffold.aprovar`), então o lint não a exige, e a recusa só no pequeno.
- **Formato 1**, o plano anterior ao redesign: a regra de antes — médio com `## Tarefas`, grande
  com `## Escopo` e `## Independência`, pequeno sem decomposição.

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
    `plan_id` e `status` têm de existir no frontmatter (`plan_id: ""` vale num rascunho): é o que
    `scaffold.aprovar` escreve, e ele não cria campo.
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

    problemas: list[str] = [
        f"campo obrigatório ausente no frontmatter: {campo}"
        for campo in ("plan_id", "status")
        if regioes.ler_campo(plano, campo) is None
    ]
    problemas.extend(_checar_tipo(plano))

    corpo = _corpo(plano.read_text(encoding="utf-8"))
    try:
        versao = lib.formato(plano)
    except ValueError:
        versao = None  # `_checar_tipo` já devolveu o problema do formato
    if versao == lib.FORMATO_ATUAL:
        problemas.extend(_checar_formato_atual(plano, corpo, plan_size))
        return problemas
    problemas.extend(_checar_independencia(corpo, plan_size))
    problemas.extend(_checar_decomposicao(corpo, plan_size))
    problemas.extend(_checar_backlog(plano, plan_size))
    return problemas


# Seções que todo plano do formato 2 tem, em qualquer porte (codex, *Plano técnico*).
SECOES_DO_FORMATO_ATUAL = ("Objetivo", "Histórias", "Independência", "Recursos")

_LINHA_NUMERADA = re.compile(r"(?m)^\|\s*\d+\s*\|")


def unidades_previstas(corpo: str) -> int | None:
    """Linhas numeradas da tabela em `## Unidades` — `None` quando a seção não existe."""
    m = re.search(r"(?m)^##\s+Unidades\s*$", corpo)
    if m is None:
        return None
    resto = corpo[m.end():]
    fim = re.search(r"(?m)^##\s", resto)
    return len(_LINHA_NUMERADA.findall(resto[: fim.start()] if fim else resto))


def _checar_formato_atual(plano: Path, corpo: str, plan_size: str) -> list[str]:
    """As seções do formato 2 e a decomposição que o porte pede (codex, *Porte*)."""
    problemas = [f"formato 2 exige '## {s}'" for s in SECOES_DO_FORMATO_ATUAL if not _tem_heading(corpo, s)]
    previstas = unidades_previstas(corpo)
    if plan_size == "pequeno":
        if not _tem_heading(corpo, "Tarefas"):
            problemas.append("pequeno exige '## Tarefas'")
        if previstas is not None:
            problemas.append("pequeno não tem unidade — tire '## Unidades' e deixe as tarefas no plano")
        if regioes.ler_regiao(plano, "backlog") is not None:
            problemas.append("pequeno não pode ter região de backlog — sem unidade, a projeção nunca escreveria ali")
        return problemas
    if previstas is None:
        problemas.append(f"{plan_size} exige '## Unidades', com uma linha numerada por unidade")
    elif plan_size == "médio" and previstas != 1:
        problemas.append(f"médio tem exatamente 1 unidade; '## Unidades' tem {previstas}")
    elif plan_size == "grande" and previstas < 2:
        problemas.append(f"grande tem duas ou mais unidades; '## Unidades' tem {previstas}")
    return problemas


def _checar_tipo(plano: Path) -> list[str]:
    """`plan_type` ausente, vazio ou fora do vocabulário do formato — sem encerrar as demais checagens.

    O vocabulário é o da versão do formato do plano (`lib.formato`): `rule` no atual, `norma` no
    anterior ao redesign (codex, *Plano anterior ao redesign*).

    Ao contrário de `plan_size`, o tipo não muda o schema do porte, então os outros blocos seguem
    conferidos. Aspas são despidas como em `scaffold.aprovar`, para lint e gate concordarem.
    """
    try:
        versao = lib.formato(plano)
    except ValueError as erro:
        return [str(erro)]
    tipos = lib.PLAN_TYPES_POR_FORMATO[versao]
    plan_type = (regioes.ler_campo(plano, "plan_type") or "").strip(" \t\"'")
    if not plan_type:
        return ["campo obrigatório ausente no frontmatter: plan_type"]
    if plan_type not in tipos:
        return [f"plan_type fora do vocabulário {tipos} do formato {versao}: {plan_type!r}"]
    return []


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
