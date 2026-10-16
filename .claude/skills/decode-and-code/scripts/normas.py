#!/usr/bin/env python3
"""Conteúdo das normas que uma unidade cita — `L-08` do plano `apply-plugin-review`.

A tabela `## Normas aplicáveis` é referência, nunca cópia, e mandar o `implement` abri-las não
bastou: medido, o subagent abriu 0 de 3 seções numa rodada e um `grep` de 23 linhas nas outras. A
instrução em markdown não estabiliza; o script entrega o trecho, e a skill só o roda.

`resolver` lê cada linha de dados da tabela e acha o que ela aponta. Três formas na coluna *Onde*
resolvem — as que as unidades reais usam —, e o resto vai para as não resolvidas, com o motivo:

- `[texto](caminho), seção *X*` — o `seção` é opcional (`[texto](caminho), *X*`);
- `[texto](caminho), seção de mesmo nome` — *X* é o texto da primeira coluna;
- `mesma seção …` — repete arquivo e seção da linha anterior, se ela resolveu.

A seção é o primeiro título, de qualquer nível, cujo texto **começa** com *X*. O `3. ` que a norma
põe diante de alguns títulos não conta — as unidades citam *Camada normativa*, não *3. Camada
normativa*. O trecho vai do título até o próximo de nível igual ou maior, e os subtítulos entram.

Não chegam ao executor, e vão para as não resolvidas: linha sem link, link sem seção reconhecida
(`[texto](caminho)` solto, ou só o id de uma decisão, que é linha de tabela e não título), arquivo
ausente e seção inexistente. É ele que as relata como insuficiência da unidade.

Reaproveita `lint_unidade._corpo` e `_secao`: o frontmatter fora, e `## Normas aplicáveis` lida do mesmo
jeito que o gate de entrada a lê. Título dentro de cerca de código não conta — a norma exemplifica
cabeçalhos em blocos de código, e um `###` de exemplo encerraria a seção antes da hora.
"""

from __future__ import annotations

import re
from pathlib import Path
from typing import NamedTuple

import lint_unidade

_TITULO_RE = re.compile(r"^(#{1,6})\s+(.*?)\s*$")
_NUMERACAO_RE = re.compile(r"^\d+\.\s+")
_CERCA_RE = re.compile(r"^\s*(```|~~~)")
_SEPARADOR_RE = re.compile(r"^\|[\s:|-]+$")
_LINK_RE = re.compile(r"\[[^\]]*\]\(([^)\s]+)\)")
_SECAO_RE = re.compile(r",\s*(?:seção\s+(?P<igual>de mesmo nome)|(?:seção\s+)?\*(?P<nome>[^*]+)\*)")
_MESMA_SECAO_RE = re.compile(r"^mesma seção\b")


class Entrada(NamedTuple):
    """Uma linha resolvida: o arquivo (caminho resolvido), o título achado e o trecho dele."""

    arquivo: Path
    secao: str
    trecho: str


class NaoResolvida(NamedTuple):
    """Uma linha que não chegou ao conteúdo: o texto dela na tabela e o motivo."""

    linha: str
    motivo: str


def resolver(unidade: Path) -> tuple[list[Entrada], list[NaoResolvida]]:
    """Entradas resolvidas e não resolvidas de `## Normas aplicáveis`, na ordem da tabela.

    Levanta `FileNotFoundError` se `unidade` não existir (propagado de `Path.read_text`) e
    `ValueError` se ela não tem a seção. Uma linha ruim nunca levanta: entra nas não resolvidas.
    """
    unidade = Path(unidade).resolve()
    corpo = lint_unidade._corpo(unidade.read_text(encoding="utf-8"))
    secao = lint_unidade._secao(corpo, "Normas aplicáveis")
    if secao is None:
        raise ValueError(f"{unidade} não tem a seção '## Normas aplicáveis'")

    resolvidas: list[Entrada] = []
    nao_resolvidas: list[NaoResolvida] = []
    anterior: tuple[Path, str] | None = None  # alvo da linha anterior, se ela resolveu
    for linha in _linhas_de_dados(secao):
        alvo = _alvo(linha, unidade.parent, anterior)
        achado = _buscar(*alvo) if isinstance(alvo, tuple) else alvo
        if isinstance(achado, str):
            nao_resolvidas.append(NaoResolvida(linha, achado))
            anterior = None
        else:
            resolvidas.append(Entrada(alvo[0], *achado))
            anterior = alvo
    return resolvidas, nao_resolvidas


def _linhas_de_dados(secao: str) -> list[str]:
    """Linhas da tabela sem o cabeçalho (a primeira) nem o separador `|---|---|`."""
    tabela = [linha.strip() for linha in secao.splitlines() if linha.strip().startswith("|")]
    return [linha for linha in tabela[1:] if not _SEPARADOR_RE.match(linha)]


def _alvo(linha: str, base: Path, anterior: tuple[Path, str] | None) -> tuple[Path, str] | str:
    """`(arquivo, nome da seção)` que a linha cita — ou o motivo, `str`, de não haver como saber."""
    celulas = [celula.strip() for celula in linha.strip("|").split("|", 1)]
    onde = celulas[1] if len(celulas) > 1 else ""

    if _MESMA_SECAO_RE.match(onde):
        return anterior or "'mesma seção' sem linha anterior resolvida"
    link = _LINK_RE.search(onde)
    if link is None:
        return "sem link para o arquivo"
    secao = _SECAO_RE.match(onde, link.end())
    if secao is None:
        return "link sem seção reconhecida"
    nome = celulas[0].strip("*").strip() if secao["igual"] else secao["nome"].strip()
    return (base / link[1]).resolve(), nome


def _buscar(arquivo: Path, nome: str) -> tuple[str, str] | str:
    """`(título, trecho)` da primeira seção de `arquivo` que começa com `nome` — ou o motivo, `str`."""
    if not arquivo.is_file():
        return "arquivo ausente"
    linhas = lint_unidade._corpo(arquivo.read_text(encoding="utf-8")).splitlines()

    em_cerca = False
    inicio: int | None = None
    nivel = 0
    titulo = ""
    for i, linha in enumerate(linhas):
        if _CERCA_RE.match(linha):
            em_cerca = not em_cerca
            continue
        achado = None if em_cerca else _TITULO_RE.match(linha)
        if achado is None:
            continue
        if inicio is None:
            if _NUMERACAO_RE.sub("", achado[2]).startswith(nome):
                inicio, nivel, titulo = i, len(achado[1]), achado[2]
        elif len(achado[1]) <= nivel:
            return titulo, "\n".join(linhas[inicio:i]).rstrip()
    if inicio is None:
        return f"seção não encontrada: {nome}"
    return titulo, "\n".join(linhas[inicio:]).rstrip()
