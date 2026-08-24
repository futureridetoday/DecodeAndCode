#!/usr/bin/env python3
"""Mecanismo de guardrail — hook `PreToolUse` que casa ferramenta e inspeciona conteúdo.

Unidade 0001-04. Lê o payload do hook, resolve `tool_name` contra o regex de `ferramenta`
de cada regra e aplica o `detector` — outro regex — ao conteúdo de `tool_input` das que
casarem. A primeira regra cujos dois regex casam decide a recusa; nenhuma casando, libera.

Regra é dado, não código: `nome`, `ferramenta`, `detector` e `mensagem`, carregados de um
JSON externo (`.claude/guardrails.json` no projeto que instala). Este módulo não conhece o
nome de nenhum serviço, tabela ou projeto — só a forma de uma regra. A instância que dá
função à camada vive no arquivo de regras, nunca aqui (invariante 2 do `CLAUDE.md`: nada
específico de projeto viaja no plugin).

Falha aberta por construção: `decidir` — o único ponto que o hook chama — nunca levanta.
Payload ilegível, arquivo de regras ausente ou regra malformada viram liberação, com o
motivo devolvido para quem chama avisar em stderr. Guardrail que trava o trabalho por
defeito próprio é o obstáculo que a norma manda evitar, não a proteção que ela pede.
"""

from __future__ import annotations

import json
import re
from pathlib import Path


def _avaliar(payload: dict, regras: list[dict]) -> dict | None:
    """Primeira regra cuja `ferramenta` casa `tool_name` e cujo `detector` casa o conteúdo.

    Devolve `{"regra": nome, "mensagem": mensagem}` na recusa, `None` na liberação. Regra
    com `ferramenta`/`detector` que não compila como regex levanta `re.error` — cabe a
    `decidir`, não a esta função, transformar isso em liberação.
    """
    tool_name = payload.get("tool_name", "")
    conteudo = "\n".join(
        valor for valor in payload.get("tool_input", {}).values() if isinstance(valor, str)
    )
    for regra in regras:
        if re.search(regra["ferramenta"], tool_name) and re.search(regra["detector"], conteudo):
            return {"regra": regra["nome"], "mensagem": regra["mensagem"]}
    return None


def decidir(payload_bruto: str, regras_caminho: Path) -> tuple[dict | None, str | None]:
    """Ponto único que o hook chama — nunca levanta. Devolve `(decisão, aviso)`.

    `decisão` é o dict de recusa, ou `None` quando libera. `aviso` é a mensagem para stderr
    quando a falha abriu o guardrail — payload malformado, arquivo de regras ausente, ou
    regra que levantou —, e `None` quando nada de anormal aconteceu.
    """
    try:
        payload = json.loads(payload_bruto)
        regras = json.loads(regras_caminho.read_text(encoding="utf-8"))["regras"]
        return _avaliar(payload, regras), None
    except Exception as erro:
        return None, f"guardrail: falha aberta, liberando — {erro!r}"
