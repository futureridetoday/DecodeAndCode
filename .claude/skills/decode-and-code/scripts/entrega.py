#!/usr/bin/env python3
"""Gate de entrada do code e aprovação da entrega (P7) — subparte 2.2.09 do redesign (K-06).

Codex, *Code*: o code só começa com o critério de aceite e o teste declarados, e, no médio e no
grande, cada unidade só roda depois da aprovação da anterior. *Aprovação*: cada entrega é aprovada
pelo usuário junto com o teste (P7). Este módulo é o lado determinístico das duas regras; o que é
julgamento — se a entrega anterior divergiu do que a unidade espera — fica na skill.

`entrada` aceita a unidade (médio e grande) ou o plano pequeno, que não tem unidade e cujas tarefas
o code executa na mesma sessão. No formato 1 vale só o lint da unidade, como antes do redesign.

`aprovar` grava a aprovação do usuário, e só ela: o teste continua sendo quem projeta `state`
(`verificacao`). Por isso a unidade `dev` ou `plan` só se aprova com `state: verified` — aprovar o
que o teste não passou seria aprovar sem P7. A unidade `rule` é o inverso: a aprovação é o aceite
(codex, *Tipo*), e o `verificar` a fecha depois. O plano pequeno se aprova com todas as tarefas
marcadas e o teste que ele declara verde (`verificar` sobre o próprio plano), e a aprovação dele é a
aprovação final: grava `status: done`.
"""

from __future__ import annotations

from datetime import date
from pathlib import Path

import backlog
import lib
import lint_plano
import lint_unidade
import numeracao
import porte
import regioes


def _limpo(valor: str | None) -> str:
    return (valor or "").strip(" \t\"'")


def _e_plano_pequeno(alvo: Path) -> bool:
    return not numeracao.PADRAO_ARQUIVO_UNIDADE.match(alvo.name) and _limpo(
        regioes.ler_campo(alvo, "plan_size")
    ) == "pequeno"


def _anteriores(unidade: Path) -> list[Path]:
    """As unidades do mesmo plano com `nn` menor — a ordem do handoff é a dos números."""
    nn = numeracao.PADRAO_ARQUIVO_UNIDADE.match(unidade.name)
    return sorted(
        u for u in porte._listar_unidades(unidade.parent)
        if numeracao.PADRAO_ARQUIVO_UNIDADE.match(u.name).group(1) < nn.group(1)
    )


def entrada(alvo: Path) -> list[str]:
    """Problemas que impedem o code de começar sobre `alvo` — lista vazia quando pode começar."""
    alvo = Path(alvo).resolve()
    if _e_plano_pequeno(alvo):
        problemas = []
        if lib.formato(alvo) != lib.FORMATO_ATUAL:
            problemas.append("plano pequeno do formato 1: a revisão o atualiza antes do code")
        if not _limpo(regioes.ler_campo(alvo, "plan_id")):
            problemas.append("plano sem número: a revisão o aprova (P4) antes do code")
        return problemas + lint_plano.lint(alvo)

    if not numeracao.PADRAO_ARQUIVO_UNIDADE.match(alvo.name):
        return [f"o code recebe uma unidade (NN-*.md) ou um plano pequeno: {alvo.name}"]
    problemas = lint_unidade.lint(alvo)
    if lib.formato(alvo) != lib.FORMATO_ATUAL:
        return problemas
    for anterior in _anteriores(alvo):
        if not _limpo(regioes.ler_campo(anterior, "approved_at")):
            unit_id = _limpo(regioes.ler_campo(anterior, "unit_id")) or anterior.stem
            problemas.append(f"a unidade anterior {unit_id} ainda não teve a entrega aprovada (P7)")
    return problemas


def aprovar(alvo: Path, por: str, data: str | None = None) -> Path:
    """Grava a aprovação do usuário sobre a entrega de `alvo` e devolve o caminho escrito.

    Levanta `ValueError`, sem escrever nada, se `por` está vazio, se a data não é ISO, se o alvo é
    do formato 1, se a unidade `dev`/`plan` não está `verified`, ou se o plano pequeno tem tarefa
    por marcar.
    """
    alvo = Path(alvo).resolve()
    if not por.strip():
        raise ValueError("a aprovação precisa de quem aprova")
    data = data or date.today().isoformat()
    date.fromisoformat(data)
    if lib.formato(alvo) != lib.FORMATO_ATUAL:
        raise ValueError(f"aprovação de entrega é do formato 2; {alvo.name} é do formato 1")

    if _e_plano_pequeno(alvo):
        tarefas = backlog._tarefas(alvo.read_text(encoding="utf-8"))
        if not tarefas:
            raise ValueError(f"plano pequeno sem '## Tarefas': {alvo}")
        abertas = [texto for feita, texto in tarefas if not feita]
        if abertas:
            raise ValueError(f"tarefas por marcar antes da aprovação: {'; '.join(abertas)}")
        plan_type = _limpo(regioes.ler_campo(alvo, "plan_type"))
        state = _limpo(regioes.ler_campo(alvo, "state"))
        if plan_type not in lib.TIPOS_DE_APROVACAO and state != "verified":
            raise ValueError(f"a entrega só se aprova com o teste verde (state: verified); está {state!r}")
        regioes.escrever_campos(alvo, {"status": "done"})
        return alvo

    unit_type = _limpo(regioes.ler_campo(alvo, "unit_type"))
    state = _limpo(regioes.ler_campo(alvo, "state"))
    if unit_type not in lib.TIPOS_DE_APROVACAO and state != "verified":
        raise ValueError(f"a entrega só se aprova com o teste verde (state: verified); está {state!r}")
    regioes.escrever_campos(alvo, {"approved_by": por.strip(), "approved_at": data})
    return alvo
