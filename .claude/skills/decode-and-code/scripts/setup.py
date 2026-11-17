#!/usr/bin/env python3
"""Registro do setup do projeto — unidade 0009-01.

O setup guarda em `<plan_root>/system/setup.md`, versionado (`D-02` do plano 0009), o que o humano
confirmou (`## Perfil`) e o que decidiu sobre cada sugestão (`## Decisões`), mais a data de conclusão
no frontmatter. Um segundo setup lê `decididas` para não sugerir de novo o que já foi aceito ou
rejeitado, e o aviso de abertura lê `completed_at` para saber quando parar.

Sem arquivo de template: o esqueleto vive em `_CONTEUDO_INICIAL`, como em `huddle`. Toda função
valida antes de escrever — valor fora do vocabulário recusa com `ValueError` e o arquivo não muda.
"""

from __future__ import annotations

import re
from datetime import date
from pathlib import Path

import lib
import regioes

TIPOS = ("guideline", "guardrail", "princípio")
ORIGENS = ("stack", "decisão do time", "existente")
RESULTADOS = ("aceita", "rejeitada", "existente")

_SECAO_RE = r"(?ms)^##\s+{}\s*$\n(.*?)(?=^##\s+|\Z)"
_CHAVE_RE = re.compile(r"^[a-z0-9]+(-[a-z0-9]+)*$")
_DATA_RE = re.compile(r"^\d{4}-\d{2}-\d{2}$")
_LINHA_TABELA_RE = re.compile(r"(?m)^\|.*\|[ \t]*$\n?")
_CABECALHO_TABELA = "| chave | tipo | origem | resultado | destino ou motivo | data |"
_ROTULOS_PERFIL = ("Objetivo", "Escopo", "Stack", "Confirmado")

_CONTEUDO_INICIAL = """\
---
# about
name: setup
type: doc
project: {projeto}
description: O que o setup do projeto confirmou com o humano e o que ele decidiu sobre cada sugestão — para que um segundo setup não repita sugestão já decidida
tags: [setup, decode-and-code, registro]

# setup
completed_at: ""

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

# Setup

## Perfil

## Decisões

""" + _CABECALHO_TABELA + """
|---|---|---|---|---|---|
"""


def caminho(projeto: Path) -> Path:
    """Arquivo do setup: `<projeto>/<plan_root>/system/setup.md`."""
    return Path(projeto) / lib.config()["plan_root"] / "system" / "setup.md"


def iniciar(projeto: Path) -> Path | None:
    """Cria o esqueleto e devolve o caminho; `None` se o arquivo já existe — nunca sobrescreve."""
    destino = caminho(projeto)
    if destino.exists():
        return None
    destino.parent.mkdir(parents=True, exist_ok=True)
    destino.write_text(
        _CONTEUDO_INICIAL.format(projeto=Path(projeto).resolve().name, criado=date.today().isoformat()),
        encoding="utf-8",
    )
    return destino


def _secao_limites(texto: str, nome: str) -> tuple[int, int]:
    """`(inicio, fim)` do conteúdo de `## nome` — `ValueError` se a seção falta."""
    m = re.compile(_SECAO_RE.format(re.escape(nome))).search(texto)
    if m is None:
        raise ValueError(f"seção '## {nome}' ausente")
    return m.start(1), m.end(1)


def _linhas_da_tabela(texto: str) -> list[list[str]]:
    """Células de cada linha de dados de `## Decisões` — sem cabeçalho nem separador."""
    inicio, fim = _secao_limites(texto, "Decisões")
    linhas = [m.group(0).strip() for m in _LINHA_TABELA_RE.finditer(texto[inicio:fim])]
    dados = []
    for linha in linhas[2:]:
        celulas = [c.strip() for c in re.split(r"(?<!\\)\|", linha.strip("|"))]
        dados.append(celulas)
    return dados


def _limpo(valor: str) -> str:
    return " ".join(str(valor).split()).replace("|", "\\|")


def perfil(arquivo: Path, objetivo: str, escopo: str, stack: str, confirmacao: str) -> None:
    """Reescreve o corpo de `## Perfil` com as quatro linhas do perfil."""
    arquivo = Path(arquivo)
    atual = arquivo.read_text(encoding="utf-8")
    inicio, fim = _secao_limites(atual, "Perfil")
    valores = (objetivo, escopo, stack, confirmacao)
    faltando = [r for r, v in zip(_ROTULOS_PERFIL, valores) if not str(v).strip()]
    if faltando:
        raise ValueError(f"perfil sem {', '.join(faltando)}")
    corpo = "\n" + "".join(
        f"- **{r}:** {' '.join(str(v).split())}\n" for r, v in zip(_ROTULOS_PERFIL, valores)
    ) + "\n"
    arquivo.write_text(atual[:inicio] + corpo + atual[fim:], encoding="utf-8")


def _origem_valida(origem: str) -> bool:
    return origem in ORIGENS or (origem.startswith("arquivo ") and bool(origem[len("arquivo "):].strip()))


def registrar(arquivo: Path, chave: str, tipo: str, origem: str, resultado: str, detalhe: str) -> None:
    """Acrescenta uma linha no fim da tabela de `## Decisões`, com a data de hoje.

    Recusa com `ValueError`, sem escrever, valor fora do vocabulário, chave que não é kebab-case
    ASCII, chave já registrada ou detalhe vazio.
    """
    arquivo = Path(arquivo)
    if not _CHAVE_RE.match(chave):
        raise ValueError(f"chave fora de kebab-case ASCII: {chave!r}")
    if tipo not in TIPOS:
        raise ValueError(f"tipo fora do vocabulário fechado {TIPOS}: {tipo!r}")
    if not _origem_valida(origem):
        raise ValueError(f"origem fora do vocabulário fechado {ORIGENS} ou 'arquivo <caminho>': {origem!r}")
    if resultado not in RESULTADOS:
        raise ValueError(f"resultado fora do vocabulário fechado {RESULTADOS}: {resultado!r}")
    if not str(detalhe).strip():
        raise ValueError("detalhe vazio — diga o destino ou o motivo")

    atual = arquivo.read_text(encoding="utf-8")
    if chave in decididas(arquivo):
        raise ValueError(f"chave já registrada: {chave!r}")
    inicio, fim = _secao_limites(atual, "Decisões")
    tabela = list(_LINHA_TABELA_RE.finditer(atual[inicio:fim]))
    if not tabela:
        raise ValueError("'## Decisões' sem tabela")
    linha = (
        f"| {chave} | {tipo} | {_limpo(origem)} | {resultado} | {_limpo(detalhe)}"
        f" | {date.today().isoformat()} |\n"
    )
    ponto = inicio + tabela[-1].end()
    if not atual[:ponto].endswith("\n"):
        linha = "\n" + linha
    arquivo.write_text(atual[:ponto] + linha + atual[ponto:], encoding="utf-8")


def decididas(arquivo: Path) -> list[str]:
    """As chaves da tabela de `## Decisões`, na ordem."""
    texto = Path(arquivo).read_text(encoding="utf-8")
    return [celulas[0] for celulas in _linhas_da_tabela(texto) if celulas]


def concluir(arquivo: Path, data: str) -> None:
    """Grava `completed_at`. Recusa com `ValueError` data que não é `AAAA-MM-DD`."""
    if not _DATA_RE.match(data):
        raise ValueError(f"data fora de AAAA-MM-DD: {data!r}")
    regioes.escrever_campos(Path(arquivo), {"completed_at": data})


def lint(arquivo: Path) -> list[str]:
    """Problemas do arquivo; lista vazia quando está são."""
    arquivo = Path(arquivo)
    texto = arquivo.read_text(encoding="utf-8")
    problemas: list[str] = []

    for nome in ("Perfil", "Decisões"):
        if re.compile(_SECAO_RE.format(re.escape(nome))).search(texto) is None:
            problemas.append(f"seção '## {nome}' ausente")

    try:
        completed = regioes.ler_campo(arquivo, "completed_at")
    except ValueError as erro:
        completed = None
        problemas.append(str(erro))
    else:
        if completed is None:
            problemas.append("campo 'completed_at' ausente")
        else:
            valor = completed.strip().strip('"').strip("'")
            if valor and not _DATA_RE.match(valor):
                problemas.append(f"completed_at fora de AAAA-MM-DD: {valor!r}")

    if re.compile(_SECAO_RE.format("Decisões")).search(texto) is not None:
        vistas: set[str] = set()
        for celulas in _linhas_da_tabela(texto):
            if len(celulas) != 6:
                problemas.append(f"linha de decisão com {len(celulas)} células em vez de 6: {celulas}")
                continue
            chave, tipo, origem, resultado, _, data = celulas
            if not _CHAVE_RE.match(chave):
                problemas.append(f"chave fora de kebab-case ASCII: {chave!r}")
            if chave in vistas:
                problemas.append(f"chave repetida: {chave!r}")
            vistas.add(chave)
            if tipo not in TIPOS:
                problemas.append(f"{chave}: tipo fora do vocabulário: {tipo!r}")
            if not _origem_valida(origem):
                problemas.append(f"{chave}: origem fora do vocabulário: {origem!r}")
            if resultado not in RESULTADOS:
                problemas.append(f"{chave}: resultado fora do vocabulário: {resultado!r}")
            if not _DATA_RE.match(data):
                problemas.append(f"{chave}: data fora de AAAA-MM-DD: {data!r}")
    return problemas
