#!/usr/bin/env python3
"""Migração dos projetos que já usam o DC para o codex — parte 2.4 do plano do redesign.

Antes do redesign, o DC gravava no projeto, a partir da norma (mapa da migração, lista 6): a cópia
`<plan_root>/system/modelo-dev-units.md`, o esqueleto do huddle que a citava, e as unidades e o
handoff dos planos que a citavam. Depois dele, nada no projeto pode repetir ou contradizer o codex
(codex, *Invariante*), e o codex nunca é copiado (*Restrição fundamental*).

`pendencias` só lê. `aplicar` faz uma coisa por vez, e só as duas que o mapa manda fazer com o sim
da pessoa: apagar a cópia da norma (`norma`) e trocar os trechos antigos do huddle pelo texto novo
(`huddle`, pelos pares de `huddle.ESQUELETO_ANTERIOR`). Os planos abertos que citam a norma só se
listam: o plano anterior ao redesign é atualizado quando a pessoa o leva à revisão, ao derive ou ao
code (codex, *Plano anterior ao redesign*), nunca por esta migração.

O projeto chega por parâmetro, como no `bootstrap`: o hook de abertura roda fora do projeto.
"""

from __future__ import annotations

from pathlib import Path
from typing import NamedTuple

import huddle
import lib
import rethink

NOME_DA_COPIA = "modelo-dev-units.md"
ITENS = ("norma", "huddle")


class Pendencias(NamedTuple):
    norma: Path | None
    huddles: list[Path]
    planos: list[Path]

    def vazias(self) -> bool:
        return self.norma is None and not self.huddles and not self.planos


def _raiz(projeto: Path) -> Path:
    return Path(projeto) / lib.config()["plan_root"]


def _arquivos_de_huddle(raiz: Path) -> list[Path]:
    pasta = raiz / "system" / "huddle"
    arquivos = sorted(pasta.glob("*.md")) if pasta.is_dir() else []
    unico = raiz / "system" / "huddle.md"
    return arquivos + ([unico] if unico.is_file() else [])


def citacoes(arquivo: Path) -> list[tuple[int, str]]:
    """As linhas de `arquivo` que ainda citam a cópia da norma, como `(número, texto)`.

    É o que sobra quando o huddle foi escrito com texto próprio, que nenhum par de
    `huddle.ESQUELETO_ANTERIOR` casa (E-03 do teste final do DC 3.0): a troca automática não o
    alcança, e quem edita é a pessoa — por isso a lista mostra o lugar exato.
    """
    nome = NOME_DA_COPIA.removesuffix(".md")
    linhas = Path(arquivo).read_text(encoding="utf-8").splitlines()
    return [(n, linha) for n, linha in enumerate(linhas, start=1) if nome in linha]


def _tem_esqueleto_antigo(arquivo: Path) -> bool:
    """O huddle ainda tem um trecho antigo conhecido, ou ainda cita a norma por outro texto."""
    texto = arquivo.read_text(encoding="utf-8")
    return any(antigo in texto for antigo, _ in huddle.ESQUELETO_ANTERIOR) or bool(citacoes(arquivo))


def pendencias(projeto: Path) -> Pendencias:
    """O que o projeto ainda tem do método anterior. Só lê."""
    raiz = _raiz(projeto)
    copia = raiz / "system" / NOME_DA_COPIA
    return Pendencias(
        norma=copia if copia.is_file() else None,
        huddles=[a for a in _arquivos_de_huddle(raiz) if _tem_esqueleto_antigo(a)],
        planos=rethink.planos_que_citam(NOME_DA_COPIA.removesuffix(".md"), raiz, com_handoff=True),
    )


def aplicar(projeto: Path, item: str) -> list[Path]:
    """Aplica um item da migração e devolve os caminhos tocados — vazio quando não havia o que fazer.

    `norma` apaga a cópia; `huddle` troca, em cada arquivo de huddle, os trechos antigos pelos
    novos, sem tocar em entrada nenhuma. Item fora de `ITENS` levanta `ValueError`, sem tocar nada.
    """
    if item not in ITENS:
        raise ValueError(f"item da migração fora de {ITENS}: {item!r} — os planos só se listam")
    p = pendencias(projeto)
    if item == "norma":
        if p.norma is None:
            return []
        p.norma.unlink()
        return [p.norma]
    tocados = []
    for arquivo in p.huddles:
        antes = arquivo.read_text(encoding="utf-8")
        texto = antes
        for antigo, novo in huddle.ESQUELETO_ANTERIOR:
            texto = texto.replace(antigo, novo)
        # Citação com texto próprio não se troca: continua em `pendencias`, com as linhas por
        # `citacoes`, até a pessoa editar.
        if texto != antes:
            arquivo.write_text(texto, encoding="utf-8")
            tocados.append(arquivo)
    return tocados


def aviso_pendente(projeto: Path) -> bool:
    """Há o que o setup resolve: a cópia da norma ou um huddle que ainda a cita.

    Os planos abertos ficam de fora de propósito (E-01 do teste final do DC 3.0): só se atualizam
    na revisão, no derive ou no code, e um aviso de abertura por causa deles mandaria ao setup sem
    nada que ele pudesse fazer. O `migrar` continua a listá-los.
    """
    p = pendencias(projeto)
    return p.norma is not None or bool(p.huddles)
