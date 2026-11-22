#!/usr/bin/env python3
"""Histórico do `rethink` — plano 0020, tarefa 6.

O `rethink` revisa princípios, guidelines e guardrails depois de uma mudança de rumo, e guarda em
`<plan_root>/system/rethink.md`, versionado (`D-12` do plano), o que mudou e o que a pessoa decidiu
sobre cada item: uma seção por `rethink`, uma linha por decisão. `start` abre a seção; `record`
acrescenta a linha na hora de cada decisão, para que a conversa interrompida não perca o que já foi
decidido (norma, seção *Rethink → O histórico*).

Sem arquivo de template: o esqueleto vive em `_CONTEUDO_INICIAL`, como em `setup`. O arquivo só
recebe acréscimo, nada o carrega em contexto e nenhum hook o lê. Toda função valida antes de
escrever — valor fora do vocabulário recusa com `ValueError` e o arquivo não muda.
"""

from __future__ import annotations

import re
from datetime import date
from pathlib import Path

import lib
from setup import _limpo

CAMADAS = ("princípio", "guideline", "guardrail")
DECISOES = ("mantido", "editado", "arquivado", "restaurado", "criado", "rejeitado")
# O `archive` exige motivo; a linha do histórico não pode ficar sem o que o comando exigiu.
DECISOES_COM_MOTIVO = ("arquivado",)

_CABECALHO_TABELA = "| camada | nome | decisão | motivo |\n|---|---|---|---|\n"
_SECAO_RE = re.compile(r"(?m)^##[ \t]+\S")

_CONTEUDO_INICIAL = """\
---
# about
name: rethink
type: doc
project: {projeto}
description: O que mudou em cada rethink do projeto e o que a pessoa decidiu sobre cada princípio, guideline e guardrail — escrito só por dc.py rethink-start e rethink-record
tags: [rethink, decode-and-code, registro]

# history
author: ""
created: {criado}
status: draft
version: 0.1.0
updated: ""

# system
scope: project
auto_load: false
dependencies: []
---

# Rethink
"""


def caminho(projeto: Path) -> Path:
    """Arquivo do histórico: `<projeto>/<plan_root>/system/rethink.md`."""
    return Path(projeto) / lib.config()["plan_root"] / "system" / "rethink.md"


def start(projeto: Path, mudanca: str, autor: str, data: str | None = None) -> Path:
    """Abre uma seção `## <data> · <autor>` com o que mudou e a tabela vazia; cria o arquivo se falta.

    Levanta `ValueError`, sem escrever, se a mudança ou o autor é vazio. Devolve o caminho.
    """
    mudanca, autor = " ".join(mudanca.split()), " ".join(autor.split())
    if not mudanca:
        raise ValueError("rethink sem o que mudou")
    if not autor:
        raise ValueError("rethink sem quem decide (git config user.name)")
    data = data or date.today().isoformat()

    destino = caminho(projeto)
    if destino.exists():
        atual = destino.read_text(encoding="utf-8")
    else:
        atual = _CONTEUDO_INICIAL.format(projeto=Path(projeto).resolve().name, criado=date.today().isoformat())
    secao = f"## {data} · {autor}\n\n**O que mudou:** {mudanca}\n\n{_CABECALHO_TABELA}"
    destino.parent.mkdir(parents=True, exist_ok=True)
    destino.write_text(atual.rstrip("\n") + "\n\n" + secao, encoding="utf-8")
    return destino


def record(projeto: Path, camada: str, nome: str, decisao: str, motivo: str) -> None:
    """Acrescenta `| camada | nome | decisão | motivo |` à última seção aberta por `start`.

    Recusa com `ValueError`, sem escrever, camada ou decisão fora do vocabulário, nome vazio, motivo
    vazio em `DECISOES_COM_MOTIVO`, ou histórico sem seção aberta. Motivo vazio nas demais vira `—`.
    """
    if camada not in CAMADAS:
        raise ValueError(f"camada fora do vocabulário fechado {CAMADAS}: {camada!r}")
    if decisao not in DECISOES:
        raise ValueError(f"decisão fora do vocabulário fechado {DECISOES}: {decisao!r}")
    nome, motivo = _limpo(nome), _limpo(motivo)
    if not nome:
        raise ValueError("decisão sem o nome do item")
    if decisao in DECISOES_COM_MOTIVO and not motivo:
        raise ValueError(f"decisão {decisao!r} exige motivo")

    destino = caminho(projeto)
    atual = destino.read_text(encoding="utf-8") if destino.exists() else ""
    if not _SECAO_RE.search(atual):
        raise ValueError("histórico sem seção aberta: rode rethink-start antes")
    linha = f"| {camada} | {nome} | {decisao} | {motivo or '—'} |\n"
    destino.write_text(atual.rstrip("\n") + "\n" + linha, encoding="utf-8")
