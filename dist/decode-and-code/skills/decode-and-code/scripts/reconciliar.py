#!/usr/bin/env python3
"""Reconcilia duas cópias do método por conteúdo — unidade 0001-17.

Só lê: nenhuma função deste módulo escreve na origem, na cópia, ou em disco algum. Atualizar
consumidor é decisão de quem mantém a cópia, não deste script (invariante 2 do `CLAUDE.md`).

`_componentes` varre a árvore inteira de `dir_skill` — `SKILL.md`, `config.json`, `scripts/` e
`scripts/tests/` inclusive —, ignorando só `__pycache__`. Diferente de `empacotar._copiar_skill`
(unidade 0001-16), que exclui `tests/` de propósito porque empacota um artefato limpo para
distribuir: aqui o objetivo é o oposto, medir o que **de fato** diverge entre duas cópias
instaladas, e uma cópia que forkou os próprios testes é sinal que quem mantém precisa ver, não
ruído a esconder.

Versão declarada nunca é veredito. Medido em 2026-08-26: os dois `SKILL.md` — este repositório e
`AmFlow:.claude/skills/dev-units` — declaram `version: 1.0.0`, e ainda assim seis dos nove scripts
compartilhados divergem. Uma reconciliação que confiasse na versão diria "em dia" e estaria errada
em seis de nove; `relatorio` imprime a versão só como contexto, e o veredito de cada componente
vem sempre do SHA-256.
"""

from __future__ import annotations

import hashlib
from pathlib import Path

import regioes


def _componentes(dir_skill: Path) -> dict[str, str]:
    """Mapa `nome relativo → SHA-256` dos arquivos de `dir_skill`, ignorando `__pycache__`.

    Levanta `FileNotFoundError` se `dir_skill` não for diretório — checagem antes de qualquer
    trabalho, mesmo contrato de fonte ausente que `empacotar.construir` já usa.
    """
    dir_skill = Path(dir_skill)
    if not dir_skill.is_dir():
        raise FileNotFoundError(f"diretório de skill ausente: {dir_skill}")

    return {
        caminho.relative_to(dir_skill).as_posix(): hashlib.sha256(caminho.read_bytes()).hexdigest()
        for caminho in sorted(dir_skill.rglob("*"))
        if caminho.is_file() and "__pycache__" not in caminho.relative_to(dir_skill).parts
    }


def _veredito(sha_origem: str | None, sha_copia: str | None) -> str:
    """Um dos quatro veredictos — o lado sem o arquivo é o que aponta `só na origem`/`só na cópia`."""
    if sha_origem is None:
        return "só na cópia"
    if sha_copia is None:
        return "só na origem"
    return "idêntico" if sha_origem == sha_copia else "divergente"


def comparar(origem: Path, copia: Path) -> list[dict[str, str | None]]:
    """Compara duas árvores de skill por conteúdo — uma entrada por componente, ordenada por nome.

    Cada item é `{componente, veredito, sha_origem, sha_copia}`; o lado que não tem o arquivo
    carrega `None` no próprio SHA.
    """
    mapa_origem = _componentes(origem)
    mapa_copia = _componentes(copia)

    return [
        {
            "componente": nome,
            "veredito": _veredito(mapa_origem.get(nome), mapa_copia.get(nome)),
            "sha_origem": mapa_origem.get(nome),
            "sha_copia": mapa_copia.get(nome),
        }
        for nome in sorted(set(mapa_origem) | set(mapa_copia))
    ]


def _versao(dir_skill: Path) -> str:
    """Versão declarada no `SKILL.md` de `dir_skill` — `não declarada` quando o arquivo ou o campo falta."""
    skill_md = Path(dir_skill) / "SKILL.md"
    if not skill_md.is_file():
        return "não declarada"
    valor = regioes.ler_campo(skill_md, "version")
    return valor.strip() if valor and valor.strip() else "não declarada"


def relatorio(origem: Path, copia: Path) -> list[str]:
    """Uma linha por componente, mais a linha de versão dos dois lados — versão é contexto, nunca veredito."""
    linha_versao = (
        f"versão declarada — origem: {_versao(origem)}, cópia: {_versao(copia)} "
        "(contexto: versão igual não implica conteúdo igual)"
    )
    linhas_componentes = [f"{item['componente']}: {item['veredito']}" for item in comparar(origem, copia)]
    return [linha_versao, *linhas_componentes]
