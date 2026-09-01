#!/usr/bin/env python3
"""Lint de uma definição de agente — unidade 0001-19.

Dá oráculo estrutural às unidades `19` e `20`, que entregam definição de agente, não código
livre — mesma família de `lint_unidade`, `lint_plano` e `lint_skill`. Verifica só o que é
objetivamente verificável: os quatro invariantes medidos em 2026-08-26 nos 34 agentes instalados
nesta máquina (unidade 0001-19). Não verifica se o agente é bom, nem se o `skills:` declarado
realmente entra em contexto — carregamento é comportamento de sessão, e ninguém o observou; o que
dá para verificar é que a skill nomeada existe em disco.

`tools:` não tem granularidade de caminho — é lista de nomes de ferramenta, sem qualquer expressão
de path (mesma medição). Escopo de escrita é declaração no corpo do agente, e este lint não finge
verificar o que só um guardrail do projeto que instala pode impor (`D-07`).
"""

from __future__ import annotations

import re
from pathlib import Path

import lib
import regioes

# As seis chaves nativas medidas nos agentes reais — bookkeeping de projeto (`type`, `project`,
# `author`...) não entra aqui: agente não é skill nem unidade, e frontmatter de agente é só o que
# o Claude Code lê.
CAMPOS_NATIVOS = ("name", "description", "tools", "model", "skills", "color")

# Nunca pode aparecer, mesmo que `CAMPOS_NATIVOS` cresça um dia — a recusa não pode depender de
# omissão incidental na outra lista, ou volta pela mesma porta (mesma classe da L-22, em
# `lint_unidade`). `memory`: D-06 — memória entre execuções corrói o cold-start como critério de
# suficiência da unidade.
CAMPOS_RECUSADOS = ("memory",)

# Medido em 2026-08-26 nos agentes instalados nesta máquina — únicos valores reais em uso.
MODELOS_VALIDOS = ("sonnet", "opus", "haiku", "inherit")

_CAMPO_RE = re.compile(r"(?m)^([A-Za-z_][A-Za-z0-9_-]*):")


def lint(caminho: Path) -> list[str]:
    """Verifica os invariantes de uma definição de agente — lista vazia quando sã.

    Quatro medidos em 2026-08-26 nos 34 agentes desta máquina (unidade 0001-19), mais a recusa
    dedicada de `CAMPOS_RECUSADOS` (D-06, unidade 0001-20) — essa não vem de medição, nenhum dos
    34 agentes declara `memory`.

    Levanta `FileNotFoundError` se o arquivo não existe — propagado por `Path.read_text`.
    Frontmatter ausente ou malformado entra na lista devolvida, nunca como exceção.
    """
    texto = caminho.read_text(encoding="utf-8")

    problemas: list[str] = []
    problemas.extend(_checar_campos_nativos(texto))
    problemas.extend(_checar_campos_recusados(texto))
    problemas.extend(_checar_model(caminho))
    problemas.extend(_checar_skills(caminho))
    problemas.extend(_checar_tools(caminho))
    return problemas


def _frontmatter(texto: str) -> str | None:
    """Miolo entre os dois '---' — None se ausente ou sem par de fechamento.

    Bloco literal (`description: |`) some sozinho: suas linhas de continuação vêm indentadas por
    convenção, e `_CAMPO_RE` só casa chave que começa na coluna zero.
    """
    linhas = texto.splitlines()
    if not linhas or linhas[0].strip() != "---":
        return None
    for i in range(1, len(linhas)):
        if linhas[i].strip() == "---":
            return "\n".join(linhas[1:i])
    return None


def _checar_campos_nativos(texto: str) -> list[str]:
    """Cada chave de primeira coluna no frontmatter precisa estar em `CAMPOS_NATIVOS`."""
    miolo = _frontmatter(texto)
    if miolo is None:
        return ["frontmatter ausente ou malformado — sem '---' de abertura e fechamento"]

    return [
        f"campo não-nativo declarado no frontmatter: {chave}"
        for chave in _CAMPO_RE.findall(miolo)
        if chave not in CAMPOS_NATIVOS
    ]


def _checar_campos_recusados(texto: str) -> list[str]:
    """Nenhuma chave de `CAMPOS_RECUSADOS` pode aparecer — checagem dedicada, não incidental.

    Roda mesmo já coberta por `_checar_campos_nativos` hoje: o que garante que a recusa sobrevive
    é não depender de `memory` continuar fora de `CAMPOS_NATIVOS` só por omissão.
    """
    miolo = _frontmatter(texto)
    if miolo is None:
        return []

    return [
        f"campo recusado no frontmatter de qualquer agente: {chave} (D-06)"
        for chave in _CAMPO_RE.findall(miolo)
        if chave in CAMPOS_RECUSADOS
    ]


def _checar_model(caminho: Path) -> list[str]:
    """`model:` obrigatório, restrito ao vocabulário medido em uso real."""
    valor = regioes.ler_campo(caminho, "model")
    if not (valor and valor.strip()):
        return ["campo obrigatório ausente no frontmatter: model"]
    if valor.strip() not in MODELOS_VALIDOS:
        return [f"model fora do vocabulário {MODELOS_VALIDOS}: {valor!r}"]
    return []


def _lista(valor: str) -> list[str]:
    """`[a, b]` ou `a, b` — mesma forma solta que `tools:` já usa nos agentes reais."""
    despido = valor.strip().strip("[]")
    return [item.strip().strip("\"'") for item in despido.split(",") if item.strip()]


def _checar_skills(caminho: Path) -> list[str]:
    """Cada nome em `skills:` precisa existir como diretório sob `.claude/skills/`."""
    valor = regioes.ler_campo(caminho, "skills")
    if not (valor and valor.strip()):
        return []

    raiz_skills = lib.repo_root() / ".claude" / "skills"
    return [
        f"skills nomeia skill que não existe em disco: {nome}"
        for nome in _lista(valor)
        if not (raiz_skills / nome).is_dir()
    ]


def _checar_tools(caminho: Path) -> list[str]:
    """`tools:` obrigatório e não vazio — ausente concede o conjunto inteiro por default."""
    valor = regioes.ler_campo(caminho, "tools")
    if not (valor and valor.strip()):
        return ["campo obrigatório ausente no frontmatter: tools"]
    return []
