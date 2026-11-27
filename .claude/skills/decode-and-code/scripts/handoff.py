#!/usr/bin/env python3
"""Handoff gravado pelo `derive` — plano 0003, e o formato do codex na subparte 2.2.08.

O `derive` terminava entregando estrutura, unidades e backlog, e nada que dissesse como conduzir a
execução daquilo. `gerar` grava `_handoff.md` na pasta do plano, no médio e no grande (codex,
*Handoff*): a ordem das unidades, a situação de cada uma, derivada do `state` que o teste projeta, e
as seções do codex que o code lê, citadas pelo título (`SECOES_DO_CODE`) — nunca copiadas. Um
esqueleto só, para todo plano: o do formato 1, que citava a norma, saiu com ela (parte 2.3).

**Divisão entre script e julgamento, a mesma do resto do método.** Aqui vive o esqueleto e o que se
mede sem opinar — o commit e a situação de cada unidade. A fila, as pendências do usuário e a
sugestão de por onde começar chegam por parâmetro, porque são julgamento de quem deriva.

O arquivo é **projeção**, regerada a cada `derive`. O prefixo `_` o mantém fora de
`numeracao.PADRAO_ARQUIVO_UNIDADE`, que é o que conta unidades aqui e em `porte`.
"""

from __future__ import annotations

import subprocess
from datetime import date
from pathlib import Path

import lib
import porte
import regioes

NOME_ARQUIVO = "_handoff.md"

# As seções do codex que a sessão de cada unidade lê, pelo título (codex, *Handoff*). A skill do code
# cita a mesma lista, e o teste confere que as duas não divergem.
SECOES_DO_CODE = (
    "Code",
    "Unidade",
    "Entrega",
    "Critério de aceite",
    "Teste",
    "Lacuna",
    "Cold-start",
    "Huddle",
    "Guardrail",
    "Recurso do projeto",
)

# A situação de uma unidade derivada do `state` que o teste projeta (codex, *Teste*).
_SITUACAO = {"verified": "verificada"}

_ESQUELETO_ATUAL = """\
# Handoff — plano {plano}

Este arquivo leva o plano a uma sessão nova e conduz o code das unidades, uma por vez, na ordem da
fila. É projeção: o derive o regera, e edição à mão se perde.

## Como executar cada unidade

`/decode-and-code:code <unidade>`, uma por vez, na ordem da fila. A próxima só começa depois de o
usuário aprovar a entrega da anterior (P7). {fecho}

## O que a sessão de cada unidade lê

A unidade e estas seções do codex, pelo título — `dc.py codex` as imprime:

{secoes}

## Situação, derivada do teste

Gerado em {gerado_em}, sobre o commit `{commit}`. Se divergir do que você medir, vale a medição.

| Unidade | Situação |
|---|---|
{situacao}

## A fila

{fila}

## Pendências do usuário

{pendencias}

## Onde eu começaria, e por quê

{sugestao}

> Sugestão registrada, não decisão. Quem escolhe a ordem é o usuário.

## O plano

`{plano_md}`
"""


def _situacao(dir_plano: Path) -> str:
    """Uma linha por unidade, na ordem do nome, com a situação lida do `state` — nunca digitada."""
    linhas = []
    for unidade in sorted(porte._listar_unidades(dir_plano), key=lambda u: u.name):
        unit_id = (regioes.ler_campo(unidade, "unit_id") or unidade.stem).strip(" \t\"'")
        state = (regioes.ler_campo(unidade, "state") or "").strip(" \t\"'")
        linhas.append(f"| {unit_id} | {_SITUACAO.get(state, 'por fazer')} |")
    return "\n".join(linhas) or "| — | nenhuma unidade derivada |"


def _commit() -> str:
    """`HEAD` abreviado — `desconhecido` quando git não responde, nunca exceção."""
    try:
        r = subprocess.run(
            ["git", "rev-parse", "--short", "HEAD"],
            cwd=lib.repo_root(),
            capture_output=True,
        )
    except FileNotFoundError:
        return "desconhecido"
    if r.returncode != 0:
        return "desconhecido"
    return r.stdout.decode("utf-8", errors="replace").strip() or "desconhecido"


def _relativo(caminho: Path, raiz: Path) -> str:
    """Caminho relativo à raiz quando ele está dentro dela; absoluto quando não está.

    `Path.relative_to` levanta `ValueError` para caminho de fora, e o prompt não é lugar de
    exceção obscura — mesma guarda que `porte._linhas_alteradas` usa pelo mesmo motivo. Medido em
    2026-08-27: o caso contra o plano real, que trabalha sobre uma cópia em `tempfile`, quebrava
    aqui antes de escrever qualquer coisa.
    """
    try:
        return caminho.relative_to(raiz).as_posix()
    except ValueError:
        return caminho.as_posix()


def gerar(dir_plano: Path, *, fila: str, pendencias: str, sugestao: str) -> Path:
    """Grava `_handoff.md` em `dir_plano` e devolve o caminho. Sobrescreve — é projeção.

    `fila`, `pendencias` e `sugestao` são julgamento de quem deriva, e chegam prontos: o script
    não tem como decidir dependência entre unidades nem o que é pendência do humano.

    Levanta `FileNotFoundError` se `dir_plano` não existir ou não tiver o arquivo do plano — o
    handoff só faz sentido para o médio e o grande, que têm pasta própria.
    """
    dir_plano = Path(dir_plano)
    plano_md = dir_plano / f"{dir_plano.name}.md"
    if not plano_md.is_file():
        raise FileNotFoundError(f"plano não encontrado para handoff: {plano_md}")

    raiz = lib.repo_root()

    grande = (regioes.ler_campo(plano_md, "plan_size") or "").strip(" \t\"'") == "grande"
    texto = _ESQUELETO_ATUAL.format(
        plano=dir_plano.name,
        fecho=(
            "Depois da última, o teste do plano inteiro (P8) e a aprovação final."
            if grande
            else "A aprovação da entrega única é a aprovação final."
        ),
        secoes="\n".join(f"- *{titulo}*" for titulo in SECOES_DO_CODE),
        gerado_em=date.today().isoformat(),
        commit=_commit(),
        situacao=_situacao(dir_plano),
        fila=fila.strip(),
        pendencias=pendencias.strip(),
        sugestao=sugestao.strip(),
        plano_md=_relativo(plano_md, raiz),
    )

    alvo = dir_plano / NOME_ARQUIVO
    alvo.write_text(texto, encoding="utf-8")
    return alvo
