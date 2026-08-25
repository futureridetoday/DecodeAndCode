#!/usr/bin/env python3
"""Lint de invariantes de rule e guideline — unidades 0001-03 e 0001-09.

Dá oráculo estrutural a `.claude/rules/*.md`: afirma que o arquivo é uma rule bem formada e que
`paths:`, quando declarado, compila como glob — nunca julga se o conteúdo normativo é o certo
(`L-01` do plano — isso é humano). Mesmo padrão de `lint_unidade.lint` e `lint_skill.lint`: lista
vazia quando aprovada, frontmatter malformado vira problema na lista, nunca exceção.

`paths:` ausente é princípio; presente, cada entrada precisa compilar via `fnmatch.translate` +
`re.compile` — é a única diferença mecânica entre as duas camadas (norma, seção *Não inventar
ativação*). A validação por regex de lista (`[...]`) é deliberada: `regioes.ler_campo` não
interpreta YAML, e o formato inline já é o que o resto do frontmatter deste repositório usa
(`tags: [...]`, `dependencies: []`).

`lint_guideline` estende `lint_rule` para o caso em que `paths:` é obrigatório, não opcional: uma
guideline sem escopo, ou com escopo que não casa nada no disco, aprova a forma e nunca ativa — a
falha silenciosa que a norma nomeia em *Ativação silenciosa é o modo de falha da própria camada*.
Casamento contra o disco usa `Path.glob` a partir de `lib.repo_root()`, nunca fixture.
"""

from __future__ import annotations

import fnmatch
import re
from pathlib import Path

import lib
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


def lint_guideline(path: Path) -> list[str]:
    """Verifica se `path` é uma guideline válida — lista vazia quando aprovada.

    Estende `lint_rule` com o que só faz sentido quando `paths:` é obrigatório: presente,
    não vazio, e casando ao menos um arquivo que existe no repositório. Formato de lista e
    compilação de glob já são responsabilidade de `lint_rule` — aqui não se repete.

    Mesmo contrato de `lint_rule`: levanta `FileNotFoundError` se `path` não existe.
    """
    problemas = lint_rule(path)
    problemas.extend(_checar_paths_guideline(path))
    return problemas


def _checar_paths_guideline(path: Path) -> list[str]:
    """`paths:` ausente ou vazio reprova; presente, ao menos uma entrada precisa casar
    arquivo real — checado por `Path.glob` a partir de `lib.repo_root()`, contra o disco."""
    try:
        valor = regioes.ler_campo(path, "paths")
    except ValueError:
        return []  # frontmatter malformado — já reportado por lint_rule

    if valor is None:
        return ["guideline sem 'paths:' — isso é princípio, não guideline"]

    entradas = _entradas_de_paths(valor)
    if entradas is None:
        return []  # formato de lista inválido — já reportado por lint_rule
    if not entradas:
        return ["'paths:' presente e vazio — guideline sem escopo"]

    raiz = lib.repo_root()
    for entrada in entradas:
        try:
            if any(raiz.glob(entrada)):
                return []
        except (ValueError, NotImplementedError):
            continue  # glob que não compila — já reportado por lint_rule

    return [f"'paths:' não casa nenhum arquivo existente no repositório: {entradas!r}"]
