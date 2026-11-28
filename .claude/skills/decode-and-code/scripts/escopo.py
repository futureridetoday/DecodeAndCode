#!/usr/bin/env python3
"""O plugin no escopo do projeto — unidade 0009-03.

`habilitar` acrescenta ao `<projeto>/.claude/settings.json` o `enabledPlugins` e o
`extraKnownMarketplaces` do próprio plugin (`D-09` do plano 0009), para que quem clonar o projeto
trabalhe com as mesmas guidelines e guardrails. O marketplace vem do `config.json` do pacote
(`D-14`): o pacote não leva o `marketplace.json`. Toda outra chave do arquivo fica como estava; JSON
inválido recusa com `ValueError` e o arquivo não muda. Habilitar no projeto não baixa nada — cada
colega instala uma vez por clone (`L-07`); a explicação é da skill, esta unidade só escreve.
"""

from __future__ import annotations

import json
from pathlib import Path

import lib


def _arquivo(projeto: Path) -> Path:
    return Path(projeto) / ".claude" / "settings.json"


def _ler(arquivo: Path) -> dict:
    if not arquivo.is_file():
        return {}
    try:
        dados = json.loads(arquivo.read_text(encoding="utf-8"))
    except json.JSONDecodeError as erro:
        raise ValueError(f"{arquivo} malformado — JSON inválido: {erro}") from erro
    if not isinstance(dados, dict):
        raise ValueError(f"{arquivo} malformado — a raiz precisa ser um objeto")
    return dados


def _secao(dados: dict, chave: str, arquivo: Path) -> dict:
    valor = dados.get(chave, {})
    if not isinstance(valor, dict):
        raise ValueError(f"{arquivo} malformado — {chave} precisa ser um objeto")
    return valor


def estado(projeto: Path) -> dict:
    """`{"habilitado", "marketplace"}` — o que já está no `settings.json` do projeto.

    `habilitado` tem três valores: `"true"`, `"false"` e `"ausente"`. O `false` presente é escolha
    de quem mantém o projeto, e no teste final do DC 3.0 (E-06) a saída booleana o confundia com a
    chave ausente — e o `--aplicar` o trocava por `true`.
    """
    arquivo = _arquivo(projeto)
    dados = _ler(arquivo)
    mk = lib.config()["marketplace"]
    chave = f"{mk['plugin']}@{mk['name']}"
    return {
        "habilitado": {True: "true", False: "false", None: "ausente"}.get(
            _secao(dados, "enabledPlugins", arquivo).get(chave), "ausente"
        ),
        "marketplace": mk["name"] in _secao(dados, "extraKnownMarketplaces", arquivo),
    }


def habilitar(projeto: Path) -> bool:
    """Acrescenta o que falta; `True` se escreveu, `False` se não havia o que acrescentar.

    Só acrescenta: a chave do plugin com `false` fica como está (E-06).
    """
    arquivo = _arquivo(projeto)
    dados = _ler(arquivo)
    mk = lib.config()["marketplace"]
    chave = f"{mk['plugin']}@{mk['name']}"
    plugins = _secao(dados, "enabledPlugins", arquivo)
    marketplaces = _secao(dados, "extraKnownMarketplaces", arquivo)
    if chave in plugins and mk["name"] in marketplaces:
        return False

    dados["enabledPlugins"] = {**plugins, chave: plugins.get(chave, True)}
    dados["extraKnownMarketplaces"] = {**marketplaces, mk["name"]: marketplaces.get(mk["name"], {"source": mk["source"]})}
    arquivo.parent.mkdir(parents=True, exist_ok=True)
    arquivo.write_text(json.dumps(dados, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return True
