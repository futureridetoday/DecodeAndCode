#!/usr/bin/env python3
"""Lint de invariantes de rule — unidade 0001-03.

Dá oráculo estrutural a `.claude/rules/*.md`: afirma que o arquivo é uma rule bem formada e que
`paths:`, quando declarado, compila como glob — nunca julga se o conteúdo normativo é o certo
(`L-01` do plano — isso é humano). Mesmo padrão de `lint_unidade.lint` e `lint_skill.lint`: lista
vazia quando aprovada, frontmatter malformado vira problema na lista, nunca exceção.

`paths:` ausente é princípio; presente, cada entrada precisa compilar via `fnmatch.translate` +
`re.compile` — é a única diferença mecânica entre as duas camadas (norma, seção *Não inventar
ativação*). A validação por regex de lista (`[...]`) é deliberada: `regioes.ler_campo` não
interpreta YAML, e o formato inline já é o que o resto do frontmatter deste repositório usa
(`tags: [...]`, `dependencies: []`).
"""

from __future__ import annotations

import fnmatch
import re
from pathlib import Path

import regioes

CAMPOS_FRONTMATTER = ("name", "description")

_PATHS_LISTA_RE = re.compile(r"^\[(.*)\]$", re.DOTALL)


def lint_rule(path: Path) -> list[str]:
    """Verifica se `path` é uma rule bem formada — lista vazia quando aprovada.

    Levanta `FileNotFoundError` se o caminho não existe. Frontmatter ausente ou malformado entra
    na lista devolvida, nunca é exceção.
    """
    texto = path.read_text(encoding="utf-8")
    corpo = _corpo(texto)

    problemas: list[str] = []
    problemas.extend(_checar_frontmatter(path))
    problemas.extend(_checar_paths(path))
    problemas.extend(_checar_corpo(corpo))
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


def _checar_frontmatter(path: Path) -> list[str]:
    """Exige `name` e `description` não vazios — malformado devolve problema, não exceção."""
    try:
        valores = {chave: regioes.ler_campo(path, chave) for chave in CAMPOS_FRONTMATTER}
    except ValueError:
        return ["frontmatter ausente ou malformado — sem '---' de abertura e fechamento"]

    return [
        f"campo obrigatório ausente ou vazio no frontmatter: {chave}"
        for chave, valor in valores.items()
        if not (valor and valor.strip())
    ]


def _entradas_de_paths(valor: str) -> list[str] | None:
    """Entradas de `paths: [...]` — None se a sintaxe não é uma lista `[...]`."""
    m = _PATHS_LISTA_RE.match(valor.strip())
    if m is None:
        return None
    miolo = m.group(1).strip()
    if not miolo:
        return []
    return [pedaco.strip().strip('"').strip("'") for pedaco in miolo.split(",")]


def _checar_paths(path: Path) -> list[str]:
    """`paths:` ausente é princípio, sem problema; presente exige lista de globs válidos."""
    try:
        valor = regioes.ler_campo(path, "paths")
    except ValueError:
        return []
    if valor is None:
        return []

    entradas = _entradas_de_paths(valor)
    if entradas is None:
        return [f"paths não está no formato de lista '[...]': {valor!r}"]

    problemas = []
    for entrada in entradas:
        try:
            re.compile(fnmatch.translate(entrada))
        except re.error as erro:
            problemas.append(f"paths contém glob inválido {entrada!r}: {erro}")
    return problemas


def _checar_corpo(corpo: str) -> list[str]:
    """Corpo vazio abaixo do frontmatter é falha silenciosa — a rule carrega e não diz nada."""
    if not corpo.strip():
        return ["corpo vazio — rule carrega e não diz nada"]
    return []
