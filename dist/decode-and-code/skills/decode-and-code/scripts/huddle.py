#!/usr/bin/env python3
"""Oráculo do huddle — fila do que ainda não foi decidido — unidade 0001-21.

Três funções, três papéis. `lint_arquivo` prova o invariante de despejo — o mesmo `H-XX` não pode
estar aberto e fechado ao mesmo tempo — e o vocabulário fechado de cinco tipos no cabeçalho de cada
entrada. `lint_relatorio` prova que o relatório de um dos três modos declara quantas entradas novas
houve, mesmo quando são zero (`L-08`) — é o que separa *conferi e não havia* de *nunca conferi*.
`iniciar` escreve o esqueleto vazio que quem instala o mecanismo recebe.

Os dois `lint_*` só leem, e devolvem lista vazia quando sãs — mesmo padrão de `lint_unidade.lint` e
`empacotar.verificar`. `iniciar` escreve **um** arquivo, e nunca sobre um existente: o `huddle.md`
de cada projeto é instância pura e não viaja no plugin — o mecanismo que cria um vazio, sim (`D-28`).

Não há arquivo de template (`D-20`): o esqueleto vive em `_CONTEUDO_INICIAL`, como
`porte._CONTEUDO_INICIAL` já faz para a tabela de porte — formato com uma fonte só, que é o
script, com a norma descrevendo-o em prosa.
"""

from __future__ import annotations

import re
from datetime import date
from pathlib import Path

import lib

# Vocabulário fechado — mesmo padrão de `unit_type` e `plan_size`: recusa-se o valor que não é
# escolha nenhuma, nunca a escolha.
TIPOS = ("pergunta", "divergência", "padrão", "revisitar", "observação")

_SECAO_RE = r"(?ms)^##\s+{}\s*$\n(.*?)(?=^##\s+|\Z)"
_CABECALHO_ENTRADA_RE = re.compile(
    r"(?m)^###\s+(H-\d+)\s*·\s*`([^`]*)`\s*·\s*\d{4}-\d{2}-\d{2}\s*·\s*.+$"
)
_LINHA_FECHADAS_RE = re.compile(r"(?m)^\|\s*(H-\d+)\s*\|")
_LINHA_FECHO_RE = re.compile(r"entradas novas no huddle:\s*\d+")


def _secao(texto: str, nome: str) -> str | None:
    """Conteúdo de `## nome` até o próximo `## ` ou o fim do texto — `None` se ausente."""
    padrao = re.compile(_SECAO_RE.format(re.escape(nome)))
    m = padrao.search(texto)
    return m.group(1) if m else None


def lint_arquivo(caminho: Path) -> list[str]:
    """Verifica `caminho` contra os invariantes do huddle — lista vazia quando são.

    Três coisas: cabeçalho de entrada bem formado (inclui o tipo dentro do vocabulário fechado),
    `H-XX` único dentro de `## Abertas`, e nenhum `H-XX` presente nas duas seções ao mesmo tempo —
    a regra de despejo.

    Levanta `FileNotFoundError` se `caminho` não existir (propagado de `Path.read_text`).
    Estrutura quebrada — seção ausente — entra na lista devolvida, nunca como exceção.
    """
    texto = Path(caminho).read_text(encoding="utf-8")

    abertas = _secao(texto, "Abertas")
    fechadas = _secao(texto, "Fechadas")

    problemas: list[str] = []
    if abertas is None:
        problemas.append("seção '## Abertas' ausente")
    if fechadas is None:
        problemas.append("seção '## Fechadas' ausente")
    if abertas is None or fechadas is None:
        return problemas

    ids_fechadas = set(_LINHA_FECHADAS_RE.findall(fechadas))

    vistos: set[str] = set()
    for h_id, tipo in _CABECALHO_ENTRADA_RE.findall(abertas):
        if tipo not in TIPOS:
            problemas.append(f"{h_id}: tipo fora do vocabulário fechado {TIPOS} — {tipo!r}")
        if h_id in vistos:
            problemas.append(f"{h_id}: repetido em '## Abertas'")
        vistos.add(h_id)
        if h_id in ids_fechadas:
            problemas.append(
                f"{h_id}: presente em '## Abertas' e na tabela de '## Fechadas' — despejo violado"
            )

    return problemas


def lint_relatorio(texto: str) -> list[str]:
    """Recusa a ausência da linha de fecho `entradas novas no huddle: N` — presente mesmo com
    `N` igual a zero (`L-08`): é o que separa *conferi e não havia* de *nunca conferi*."""
    if _LINHA_FECHO_RE.search(texto):
        return []
    return ["relatório sem a linha de fecho 'entradas novas no huddle: N' — obrigatória mesmo com N=0"]


_CONTEUDO_INICIAL = """\
---
# about
name: huddle
type: doc
project: {projeto}
description: Fila do que ainda não foi decidido — pauta da conversa recorrente entre o humano e o modelo. Nada aqui é norma; entrada resolvida sai daqui e vai para o lugar de coisa resolvida
tags: [huddle, decode-and-code, pre-norma, pauta]

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

# Huddle

**Nada aqui é autoritativo.** Entrada aberta é coisa que espera decisão, não regra a seguir. Quando
resolve, **sai** — para a norma, para uma guideline, ou para o `## Decisões` de um plano — e deixa
uma linha em `## Fechadas` com a data e o destino.

Formato, tipos, gatilhos e a regra de despejo: `<plan_root>/system/modelo-dev-units.md`, seção
*Huddle*. Aqui não se duplica a norma; aqui se usa.

## Abertas

## Fechadas

| # | Tipo | Fechada em | Destino |
|---|---|---|---|
"""


def iniciar(destino: Path) -> Path | None:
    """Escreve o esqueleto vazio em `destino` — devolve o caminho, ou `None` se já existir.

    Nunca sobrescreve: quem chama de novo sobre o mesmo `destino` não perde entrada nenhuma —
    `iniciar` só cria, nunca reescreve. `project` do frontmatter vem de `lib.repo_root().name`,
    nunca hardcoded, para que o mecanismo, instalado noutro projeto, declare o projeto certo
    (invariante 2 do `CLAUDE.md`).
    """
    destino = Path(destino)
    if destino.exists():
        return None

    destino.parent.mkdir(parents=True, exist_ok=True)
    destino.write_text(
        _CONTEUDO_INICIAL.format(projeto=lib.repo_root().name, criado=date.today().isoformat()),
        encoding="utf-8",
    )
    return destino
