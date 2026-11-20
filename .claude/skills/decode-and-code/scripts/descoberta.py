#!/usr/bin/env python3
"""Inventário do projeto para o setup — unidade 0009-02.

Lista, por uma tupla literal de globs, os arquivos que dizem a stack, o objetivo e as convenções do
projeto, com as primeiras 60 linhas de cada um, e à parte a norma que o projeto já tem. Só lê, e não
classifica nada: classificar é da skill `setup`.
"""

from __future__ import annotations

import json
import re
from pathlib import Path

import guardrail
import registry

LINHAS_DO_TRECHO = 60

FONTES = (
    "CLAUDE.md",
    ".claude/CLAUDE.md",
    "CLAUDE.local.md",
    "AGENTS.md",
    "README*",
    "CONTRIBUTING*",
    "package.json",
    "pyproject.toml",
    "tsconfig.json",
    "components.json",
    "tailwind.config.*",
    ".eslintrc*",
    "eslint.config.*",
    ".prettierrc*",
    "prettier.config.*",
    "biome.json",
    "biome.jsonc",
    "ruff.toml",
    ".ruff.toml",
    ".editorconfig",
    ".pre-commit-config.yaml",
    ".github/workflows/*.yml",
    ".gitlab-ci.yml",
    ".cursor/rules/**/*",
    ".cursorrules",
    ".windsurfrules",
    ".clinerules",
)


def _trecho(arquivo: Path) -> str:
    """As primeiras `LINHAS_DO_TRECHO` linhas; vazio se o arquivo não é legível como texto."""
    try:
        with arquivo.open(encoding="utf-8") as f:
            return "".join(f.readline() for _ in range(LINHAS_DO_TRECHO))
    except (OSError, UnicodeDecodeError):
        return ""


def _fontes(projeto: Path) -> list[dict]:
    vistos: set[Path] = set()
    achadas: list[dict] = []
    for padrao in FONTES:
        for arquivo in sorted(projeto.glob(padrao)):
            if arquivo in vistos or not arquivo.is_file():
                continue
            vistos.add(arquivo)
            achadas.append({"caminho": arquivo.relative_to(projeto).as_posix(), "trecho": _trecho(arquivo)})
    return achadas


def _guardrails(projeto: Path) -> tuple[list[str], str | None]:
    arquivo = projeto / ".claude" / "guardrails.json"
    if not arquivo.is_file():
        return [], None
    try:
        problemas = guardrail.lint_arquivo(arquivo)
    except (OSError, UnicodeDecodeError) as erro:
        return [], f"{arquivo.name} ilegível: {erro}"
    if problemas:
        return [], f"{arquivo.name} não passa no lint: {'; '.join(problemas)}"
    return [regra["nome"] for regra in json.loads(arquivo.read_text(encoding="utf-8"))["regras"]], None


def descobrir(projeto: Path) -> dict:
    """`{"fontes": [...], "existentes": {"guidelines", "principios", "guardrails", "aviso"}}`."""
    dir_rules = projeto / ".claude" / "rules"
    mds = sorted(dir_rules.glob("*.md")) if dir_rules.is_dir() else []
    guardrails, aviso = _guardrails(projeto)
    return {
        "fontes": _fontes(projeto),
        "existentes": {
            "guidelines": [p.stem for p in mds if registry._e_guideline(p)],
            "principios": [p.stem for p in mds if not registry._e_guideline(p)],
            "guardrails": guardrails,
            "aviso": aviso,
        },
    }


def formatar(resultado: dict) -> str:
    """O texto do `dc.py descobrir`: um bloco `### <caminho>` por fonte e `## Já existe` no fim.

    O trecho vai numa cerca mais longa que qualquer sequência de crases dele, para que os títulos
    e as cercas do próprio arquivo não se confundam com o `### <caminho>` (M3 do `0013`).
    """
    blocos = []
    for f in resultado["fontes"]:
        trecho = f["trecho"].rstrip()
        cerca = "`" * max(3, max((len(r) for r in re.findall(r"`+", trecho)), default=0) + 1)
        blocos.append(f"### {f['caminho']}\n{cerca}\n{trecho}\n{cerca}\n")
    e = resultado["existentes"]
    fim = ["## Já existe"]
    for rotulo, chave in (("Guidelines", "guidelines"), ("Princípios", "principios"), ("Guardrails", "guardrails")):
        fim.append(f"{rotulo}: {', '.join(e[chave]) if e[chave] else '(nenhum)'}")
    if e["aviso"]:
        fim.append(f"Aviso: {e['aviso']}")
    return "\n".join(blocos + fim)
