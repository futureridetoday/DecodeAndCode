#!/usr/bin/env python3
"""Inventário do projeto para o setup — unidade 0009-02.

Lista, por uma tupla literal de globs, os arquivos que dizem a stack, o objetivo e as convenções do
projeto, com as primeiras 60 linhas de cada um, e à parte os princípios, guidelines e guardrails que
o projeto já tem. Só lê, e não classifica nada: classificar é da skill `setup`.
"""

from __future__ import annotations

import json
import re
from pathlib import Path

import guardrail
import lib
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


_BLOCO_YAML = ("|", "|-", "|+", ">", ">-", ">+")


def _frontmatter(arquivo: Path) -> list[str]:
    """Linhas entre os dois `---` do topo; vazio sem frontmatter ou arquivo ilegível."""
    try:
        linhas = arquivo.read_text(encoding="utf-8").splitlines()
    except (OSError, UnicodeDecodeError):
        return []
    if not linhas or linhas[0].strip() != "---":
        return []
    for i in range(1, len(linhas)):
        if linhas[i].strip() == "---":
            return linhas[1:i]
    return []


def _campo(linhas: list[str], chave: str) -> str:
    """Valor de `chave` no frontmatter numa linha só. Bloco `|`/`>` vale até o primeiro parágrafo."""
    for i, linha in enumerate(linhas):
        if not linha.startswith(f"{chave}:"):
            continue
        valor = linha[len(chave) + 1 :].strip()
        if valor not in _BLOCO_YAML:
            return valor.strip("\"'")
        partes: list[str] = []
        for seguinte in linhas[i + 1 :]:
            if seguinte.strip() and not seguinte[:1].isspace():
                break
            if not seguinte.strip():
                if partes:
                    break
                continue
            partes.append(seguinte.strip())
        return " ".join(partes)
    return ""


def _recurso(tipo: str, arquivo: Path, nome_padrao: str) -> dict:
    linhas = _frontmatter(arquivo)
    return {"tipo": tipo, "nome": _campo(linhas, "name") or nome_padrao, "descricao": _campo(linhas, "description")}


def _recursos(projeto: Path) -> list[dict]:
    """Skills, commands e agents do projeto, com nome e `description`, e os servidores de `.mcp.json`.

    Plano 0017. Sem trecho: o que importa ao setup é saber que o recurso existe e quando vale. As
    skills do próprio método (`lib.SKILLS`) ficam fora. Arquivo ilegível vira descrição vazia,
    `.mcp.json` malformado vira lista vazia — nunca exceção.
    """
    claude = projeto / ".claude"
    achados = [
        _recurso("skill", arquivo, arquivo.parent.name)
        for arquivo in sorted(claude.glob("skills/*/SKILL.md"))
        if arquivo.parent.name not in lib.skills_do_pacote()
    ]
    dir_commands = claude / "commands"
    achados += [
        _recurso("command", arquivo, ":".join(arquivo.relative_to(dir_commands).with_suffix("").parts))
        for arquivo in sorted(dir_commands.glob("**/*.md"))
        if arquivo.is_file()
    ]
    achados += [_recurso("agent", arquivo, arquivo.stem) for arquivo in sorted(claude.glob("agents/*.md"))]
    try:
        servidores = json.loads((projeto / ".mcp.json").read_text(encoding="utf-8")).get("mcpServers", {})
    except (OSError, UnicodeDecodeError, ValueError, AttributeError):
        servidores = {}
    if isinstance(servidores, dict):
        achados += [{"tipo": "mcp", "nome": nome, "descricao": ""} for nome in sorted(servidores)]
    return achados


def descobrir(projeto: Path) -> dict:
    """`{"fontes": [...], "recursos": [...], "existentes": {"guidelines", "principios", "guardrails", "aviso"}}`."""
    dir_rules = projeto / ".claude" / "rules"
    mds = sorted(dir_rules.glob("*.md")) if dir_rules.is_dir() else []
    guardrails, aviso = _guardrails(projeto)
    return {
        "fontes": _fontes(projeto),
        "recursos": _recursos(projeto),
        "existentes": {
            "guidelines": [p.stem for p in mds if registry._e_guideline(p)],
            "principios": [p.stem for p in mds if not registry._e_guideline(p)],
            "guardrails": guardrails,
            "aviso": aviso,
        },
    }


def formatar(resultado: dict) -> str:
    """O texto do `dc.py descobrir`: um bloco `### <caminho>` por fonte, `## Recursos do projeto` e
    `## Já existe` no fim.

    O trecho vai numa cerca mais longa que qualquer sequência de crases dele, para que os títulos
    e as cercas do próprio arquivo não se confundam com o `### <caminho>` (M3 do `0013`).
    """
    blocos = []
    for f in resultado["fontes"]:
        trecho = f["trecho"].rstrip()
        cerca = "`" * max(3, max((len(r) for r in re.findall(r"`+", trecho)), default=0) + 1)
        blocos.append(f"### {f['caminho']}\n{cerca}\n{trecho}\n{cerca}\n")
    recursos = ["## Recursos do projeto"]
    for r in resultado.get("recursos", []):
        recursos.append(f"- {r['tipo']} `{r['nome']}`" + (f" — {r['descricao']}" if r["descricao"] else ""))
    if len(recursos) == 1:
        recursos.append("(nenhum)")
    e = resultado["existentes"]
    fim = recursos + ["", "## Já existe"]
    for rotulo, chave in (("Guidelines", "guidelines"), ("Rules que carregam sempre", "principios"), ("Guardrails", "guardrails")):
        fim.append(f"{rotulo}: {', '.join(e[chave]) if e[chave] else '(nenhum)'}")
    if e["aviso"]:
        fim.append(f"Aviso: {e['aviso']}")
    return "\n".join(blocos + fim)
