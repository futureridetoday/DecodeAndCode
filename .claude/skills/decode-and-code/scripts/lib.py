#!/usr/bin/env python3
"""Módulo comum dos scripts da skill dev-units.

Dá aos demais scripts uma origem confiável — a raiz do repositório e os caminhos
canônicos sob `docs/plan/` — sem depender de variável de ambiente nem do
diretório de trabalho de quem invoca. É módulo importado, não script executável.

`CLAUDE_PLUGIN_ROOT` não serve: medido vazio nos dois ambientes, e no browser
isso causou falha até o script ser localizado com `find`. Auto-localização por
`__file__` é o padrão adotado.

Todo caminho devolvido é resolvido. `relpath` entre um caminho resolvido e outro
não-resolvido produz lixo quando há symlink no meio, e no macOS `/tmp` e `/var`
são symlinks — foi exatamente assim que o move-md quebrou.

A configuração (`config.json`, opcional, ao lado deste diretório `scripts/`) é
lida por `config()` e cacheada em módulo — arquivo do disco sobrepõe os defaults
embutidos, chave a chave. Ausente cai inteiramente nos defaults; malformado
levanta `ValueError` nomeando o arquivo e o campo.
"""

from __future__ import annotations

import json
from pathlib import Path

_DEFAULTS = {
    "plan_root": "docs/plan",
    # Marcas da raiz. Só `.claude/` não bastaria: qualquer projeto pode ter uma.
    "root_markers": [".claude", "docs"],
    "move_script": "scripts/move-md.py",
    "runners": {".py": "scripts/test-python.sh"},
}

# Os defaults são a fonte única. `_find_repo_root` lê a versão resolvida pelo config,
# que pode sobrepô-los; esta constante é o valor embutido, não o efetivo.
ROOT_MARKERS = tuple(_DEFAULTS["root_markers"])

_config_cache: dict | None = None


def _config_path() -> Path:
    """`config.json` na raiz da skill — irmão de `scripts/`, não da raiz do repositório."""
    return Path(__file__).resolve().parent.parent / "config.json"


def config() -> dict:
    """Config resolvida: `config.json` do disco sobreposto aos defaults embutidos — cacheada em módulo."""
    global _config_cache
    if _config_cache is not None:
        return _config_cache

    resolvido = dict(_DEFAULTS)
    caminho = _config_path()
    if caminho.is_file():
        try:
            do_disco = json.loads(caminho.read_text(encoding="utf-8"))
        except json.JSONDecodeError as erro:
            raise ValueError(f"{caminho} malformado — JSON inválido: {erro}") from erro
        if not isinstance(do_disco, dict):
            raise ValueError(f"{caminho} malformado — a raiz precisa ser um objeto")
        for chave, valor in do_disco.items():
            if chave not in _DEFAULTS:
                raise ValueError(f"{caminho} malformado — campo desconhecido: {chave!r}")
            resolvido[chave] = valor

    _config_cache = resolvido
    return resolvido


def _find_repo_root(start: Path) -> Path:
    """Sobe a partir de `start` até o diretório que contém todas as marcas do config."""
    marcadores = config()["root_markers"]
    for candidate in (start, *start.parents):
        if all((candidate / marker).is_dir() for marker in marcadores):
            return candidate

    marcas = " e ".join(f"{marker}/" for marker in marcadores)
    raise RuntimeError(
        f"raiz do repositório não localizada a partir de {start} — "
        f"nenhum diretório acima contém {marcas}."
    )


def repo_root() -> Path:
    """Raiz do repositório, achada a partir deste arquivo — nunca do cwd."""
    return _find_repo_root(Path(__file__).resolve().parent)


def plan_root() -> Path:
    """Onde vivem planos, unidades e normativa — caminho resolvido pelo config."""
    return (repo_root() / config()["plan_root"]).resolve()


def planos_md() -> Path:
    """`_planos.md` — tabela dos planos aprovados, fonte da numeração."""
    return (plan_root() / "_planos.md").resolve()


def inbox() -> Path:
    """`_inbox/` — planos aguardando revisão e aprovação."""
    return (plan_root() / "_inbox").resolve()


def core_dir(core: str) -> Path:
    """Diretório de um core sob `docs/plan/` — o nome vem do frontmatter do plano."""
    if not core.strip():
        raise ValueError("nome de core vazio")
    if "/" in core or "\\" in core:
        raise ValueError(
            f"nome de core não pode conter separador de caminho — {core!r}"
        )
    return (plan_root() / core).resolve()
