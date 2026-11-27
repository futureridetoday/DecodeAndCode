#!/usr/bin/env python3
"""Foundation do projeto — subparte 2.2.11 do redesign (K-10).

Codex, *Foundation*: o que o projeto registra para o DC trabalhar como alguém do time e que não tem
outro lugar — o padrão de código e o mapa de recursos do projeto. Mora em
`<plan_root>/system/foundation.md` (*Raiz dos planos*). O setup a escreve; o rethink e os planos a
mudam; sempre com o sim do usuário, e é por isso que cada operação daqui grava uma coisa só, que a
skill mostrou antes.

O arquivo tem duas regiões, projeção do que estas operações gravam: `padrao`, o texto do padrão de
código (ou a frase que o cita num recurso do projeto, quando ele já mora num), e `recursos`, a
tabela do mapa. Fora das regiões o arquivo é de quem o escreve. O mapa nunca guarda conteúdo, linha
ou versão do recurso, só o nome e os campos de `CAMPOS_DO_RECURSO` (*Mapa de recursos do projeto*).
"""

from __future__ import annotations

from pathlib import Path

import lib
import regioes

ETAPAS = ("decode", "revisão", "derive", "code", "fora do workflow")
ESCOPOS = ("projeto", "pessoal")
TIPOS = ("skill", "command", "agent", "mcp", "instrução", "outro")
CAMPOS_DO_RECURSO = ("nome", "tipo", "etapa", "so_usuario", "escopo", "permissao")

_CABECALHO = "| Recurso | Tipo | Etapa | Só o usuário chama | Escopo | Permissão de uso |\n|---|---|---|---|---|---|\n"

_CONTEUDO_INICIAL = """\
---
# about
name: foundation
type: doc
project: {projeto}
description: Foundation do projeto para o decode-and-code — o padrão de código e o mapa de recursos que o DC pode usar
tags: [decode-and-code, foundation]

# history
author: ""
created: ""
status: stable
version: 1.0.0
updated: ""

# system
scope: project
auto_load: false
dependencies: []
---

# Foundation

O que o DC precisa saber deste projeto e que não tem outro lugar. Princípios, guidelines,
guardrails, planos e huddle continuam onde estão. As regiões abaixo são gravadas pelo `dc.py`, com
o sim de quem usa; não se editam à mão.

## Padrão de código

<!-- padrao:start -->
(ainda não registrado)
<!-- padrao:end -->

## Mapa de recursos do projeto

<!-- recursos:start -->
{cabecalho}<!-- recursos:end -->
"""


def caminho() -> Path:
    return lib.plan_root() / "system" / "foundation.md"


def iniciar(projeto: Path | None = None) -> Path | None:
    """Cria o arquivo vazio, se ainda não existe — devolve o caminho criado, ou `None`. Idempotente."""
    alvo = caminho()
    if alvo.exists():
        return None
    alvo.parent.mkdir(parents=True, exist_ok=True)
    nome = (projeto or lib.repo_root()).name
    alvo.write_text(_CONTEUDO_INICIAL.format(projeto=nome, cabecalho=_CABECALHO), encoding="utf-8")
    return alvo


def escrever_padrao(texto: str) -> bool:
    """Grava o padrão de código (ou a citação do recurso onde ele mora). Devolve se gravou."""
    if not texto.strip():
        raise ValueError("padrão de código vazio")
    iniciar()
    return regioes.escrever_regiao(caminho(), "padrao", "\n" + texto.strip() + "\n")


def mapa() -> list[dict]:
    """O mapa de recursos, uma entrada por linha da tabela — vazio quando não há foundation."""
    alvo = caminho()
    if not alvo.is_file():
        return []
    miolo = regioes.ler_regiao(alvo, "recursos") or ""
    linhas = [l for l in miolo.splitlines() if l.startswith("|")][2:]
    entradas = []
    for linha in linhas:
        celulas = [c.strip().strip("`") for c in linha.strip().strip("|").split("|")]
        entradas.append(dict(zip(CAMPOS_DO_RECURSO, celulas)))
    return entradas


def _validar(recurso: dict) -> dict:
    faltam = [c for c in CAMPOS_DO_RECURSO if not str(recurso.get(c, "")).strip()]
    if faltam:
        raise ValueError(f"recurso sem {', '.join(faltam)}")
    limpo = {c: str(recurso[c]).strip() for c in CAMPOS_DO_RECURSO}
    for campo, vocabulario in (("tipo", TIPOS), ("etapa", ETAPAS), ("escopo", ESCOPOS),
                               ("so_usuario", ("sim", "não")), ("permissao", ("sim", "não"))):
        if limpo[campo] not in vocabulario:
            raise ValueError(f"{campo} fora do vocabulário {vocabulario}: {limpo[campo]!r}")
    if "|" in limpo["nome"]:
        raise ValueError(f"nome de recurso com '|': {limpo['nome']!r}")
    return limpo


def _gravar(entradas: list[dict]) -> bool:
    corpo = "".join(
        f"| `{e['nome']}` | {e['tipo']} | {e['etapa']} | {e['so_usuario']} | {e['escopo']} | {e['permissao']} |\n"
        for e in sorted(entradas, key=lambda e: e["nome"])
    )
    return regioes.escrever_regiao(caminho(), "recursos", "\n" + _CABECALHO + corpo)


def registrar_recurso(recurso: dict) -> bool:
    """Inclui ou atualiza, pelo nome, um recurso no mapa. Valida antes de escrever qualquer coisa."""
    novo = _validar(recurso)
    iniciar()
    entradas = [e for e in mapa() if e["nome"] != novo["nome"]] + [novo]
    return _gravar(entradas)


def retirar_recurso(nome: str) -> bool:
    """Tira o recurso do mapa (rethink). `ValueError` se ele não está lá."""
    entradas = mapa()
    restantes = [e for e in entradas if e["nome"] != nome.strip()]
    if len(restantes) == len(entradas):
        raise ValueError(f"recurso fora do mapa: {nome!r}")
    return _gravar(restantes)
