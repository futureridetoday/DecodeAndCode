#!/usr/bin/env python3
"""Medição de porte — unidade 0001-15.

Registra, no fechamento de um plano, o porte que o humano **declarou** ao lado do que o trabalho
**foi** — o dado que falta para o vocabulário de `pequeno`/`médio`/`grande` (0001-12) se corrigir
por evidência em vez de continuar por impressão.

`medir` só lê; `registrar` acrescenta uma linha a `docs/plan/system/porte-medido.md` e nunca
reescreve nenhuma — o oposto de toda outra escrita de script deste repositório, que é projeção
recalculada a partir da fonte. Sem marcadores de região de propósito: o fato que esta tabela
registra — quanto custou fechar este plano — só existe naquele instante, e recalculá-lo depois
daria outro número sobre o mesmo plano.

`_plan_size` duplica a normalização de `backlog._plan_size` (mesmo tratamento de aspas, mesmo
"ausente cai no grande") em vez de importá-la: `backlog.py` importa este módulo para chamar
`registrar` na transição, e o inverso criaria ciclo.

`Linhas alteradas` só tenta git quando há arquivos declarados (D-19 do plano) — fora do grande a
coluna sai `—`, sem disparar `subprocess`. Dentro do grande, o cálculo primeiro compara o caminho
do plano contra `lib.repo_root()`: plano fora do repositório — todo plano sintético de teste, sob
`tempfile` — cai direto em "sem commit de criação" **sem** chamar `subprocess`. É por isso que
nenhum teste da suíte que não mocka `lib.repo_root` corre o risco de invocar git de verdade. Os
testes que exercitam o caminho feliz e as três falhas mockam `lib.repo_root` a par de
`subprocess.run`, no mesmo padrão de `test_verificacao.py`.
"""

from __future__ import annotations

import re
import subprocess
from datetime import date
from pathlib import Path

import lib
import numeracao
import regioes

_ARQUIVOS_HEADING = re.compile(r"(?m)^##\s+Arquivos\s*$")
_TAREFAS_HEADING = re.compile(r"(?m)^##\s+Tarefas\s*$")
_PROXIMO_H2 = re.compile(r"(?m)^##\s")
_CAMINHO_RE = re.compile(r"`([^`]*/[^`]*)`")
_ITEM_TAREFA = re.compile(r"(?m)^-\s+\[( |x|X)\]\s+(.+?)\s*$")

_CONTEUDO_INICIAL = """\
---
# about
name: porte-medido
type: doc
project: DecodeAndCode
description: Tabela append-only do porte declarado contra o porte real de cada plano fechado — recalibra o vocabulário de pequeno/médio/grande com dado, não com impressão
tags: [decode-and-code, porte, medicao, instrumentacao]

# history
author: Bortoli
created: 2026-08-25
status: draft
version: 1.0.0
updated: ""

# system
scope: project
auto_load: false
dependencies: []
---

# Porte medido

> **Esta tabela é append-only.** `porte.registrar` acrescenta uma linha no instante em que um
> plano fecha — nunca reescreve, nunca recalcula uma linha existente. Não há marcadores de região
> aqui de propósito: toda outra escrita de script neste repositório é projeção, recalculada a
> partir da fonte a cada execução; esta tabela é o contrário — o fato que ela registra só existe
> naquele instante, e recalculá-lo depois daria outro número sobre o mesmo plano.

| Plano | Porte declarado | Unidades ou tarefas | Arquivos declarados | Linhas alteradas | Fechado em |
|---|---|---|---|---|---|
"""


def _arquivo_do_plano(alvo: Path) -> Path:
    """Mesma normalização de `backlog.projetar` — diretório (grande) ou arquivo (demais)."""
    alvo = Path(alvo).resolve()
    return alvo / f"{alvo.name}.md" if alvo.is_dir() else alvo


def _plan_size(arquivo_do_plano: Path) -> str | None:
    """Mesma normalização de `backlog._plan_size` — duplicada para não importar `backlog` (ciclo)."""
    bruto = regioes.ler_campo(arquivo_do_plano, "plan_size")
    if bruto is None:
        return None
    normalizado = bruto.strip(" \t\"'")
    return normalizado or None


def _secao(texto: str, heading: re.Pattern) -> str | None:
    """Conteúdo da seção `heading` até o próximo `## `, ou fim do texto — `None` se ausente."""
    inicio = heading.search(texto)
    if inicio is None:
        return None
    resto = texto[inicio.end() :]
    fim = _PROXIMO_H2.search(resto)
    return resto[: fim.start()] if fim else resto


def _listar_unidades(dir_plano: Path) -> list[Path]:
    """Arquivos `NN-*.md` do diretório do plano, exceto o do próprio plano — mesmo padrão de
    `numeracao.proxima_unidade`."""
    arquivo_do_plano = f"{dir_plano.name}.md"
    return [
        item
        for item in dir_plano.iterdir()
        if item.is_file()
        and item.name != arquivo_do_plano
        and numeracao.PADRAO_ARQUIVO_UNIDADE.match(item.name)
    ]


def _arquivos_de_unidade(caminho: Path) -> list[str]:
    """Caminhos entre crase com `/` na seção `## Arquivos` de uma unidade — vazio se a seção não existir."""
    bloco = _secao(caminho.read_text(encoding="utf-8"), _ARQUIVOS_HEADING)
    return _CAMINHO_RE.findall(bloco) if bloco else []


def _arquivos_declarados(unidades: list[Path]) -> list[str]:
    """União deduplicada e ordenada dos caminhos de `## Arquivos` de todas as unidades."""
    vistos: set[str] = set()
    for unidade in unidades:
        vistos.update(_arquivos_de_unidade(unidade))
    return sorted(vistos)


def _contar_tarefas(arquivo_do_plano: Path) -> int:
    """Itens de `## Tarefas` — mesma extração de `backlog._tarefas`, sem o texto de cada item."""
    bloco = _secao(arquivo_do_plano.read_text(encoding="utf-8"), _TAREFAS_HEADING)
    return len(_ITEM_TAREFA.findall(bloco)) if bloco else 0


def _int_ou_zero(valor: str) -> int:
    """`git diff --numstat` usa `-` para arquivo binário — conta como zero, nunca levanta."""
    valor = valor.strip()
    return int(valor) if valor.isdigit() else 0


def _commit_de_criacao(caminho_relativo: Path, raiz: Path) -> tuple[str | None, str | None]:
    """Primeiro commit que adicionou `caminho_relativo` — `(None, motivo)` se não houver.

    **Sem `--reverse`, e é o defeito que a `L-28` registra.** O git responde `--follow` somado a
    `--reverse` com saída vazia quando o arquivo foi movido — e todo plano é movido do `_inbox`
    pelo `derive`, então a combinação devolvia "plano sem commit de criação" para **todo** plano
    versionado. `--follow` fica: é ele que atravessa o move e acha a criação; sem ele o comando
    acha o commit que *moveu* o plano, que é outro intervalo.

    Sem `--reverse` a saída vem do mais novo para o mais antigo, então a criação é a **última**
    linha — um arquivo criado, apagado e recriado produz dois commits `A`, e o que interessa é o
    primeiro. Os dois casos rodam contra git real em `TestComandoContraGitReal`.

    Pode levantar `FileNotFoundError` quando o comando `git` não existe — deixada para o chamador
    tratar junto da mesma falha do segundo comando.
    """
    resultado = subprocess.run(
        [
            "git", "log", "--follow", "--diff-filter=A", "--format=%H",
            "--", caminho_relativo.as_posix(),
        ],
        cwd=raiz,
        capture_output=True,
    )
    if resultado.returncode != 0:
        return None, "git falhou"
    linhas = resultado.stdout.decode("utf-8", errors="replace").splitlines()
    if not linhas:
        return None, "plano sem commit de criação"
    return linhas[-1].strip(), None


def _linhas_alteradas(arquivo_do_plano: Path, caminhos: list[str]) -> tuple[int | None, str | None]:
    """`git diff --numstat` do commit de criação até `HEAD`, restrito a `caminhos` (D-19).

    Só é chamada quando `caminhos` não é vazio — fora do grande a coluna é `—`, não `não medido`
    (D-19: "fora do porte grande não há unidade e portanto não há caminho declarado").
    """
    raiz = lib.repo_root()
    try:
        relativo = arquivo_do_plano.relative_to(raiz)
    except ValueError:
        return None, "plano sem commit de criação"

    try:
        commit, motivo = _commit_de_criacao(relativo, raiz)
    except FileNotFoundError:
        return None, "comando git não encontrado"
    if motivo:
        return None, motivo

    try:
        resultado = subprocess.run(
            ["git", "diff", "--numstat", commit, "HEAD", "--", *caminhos],
            cwd=raiz,
            capture_output=True,
        )
    except FileNotFoundError:
        return None, "comando git não encontrado"
    if resultado.returncode != 0:
        return None, "git falhou"

    saida = resultado.stdout.decode("utf-8", errors="replace")
    total = sum(_int_ou_zero(parte) for linha in saida.splitlines() for parte in linha.split("\t")[:2])
    return total, None


def medir(alvo: Path) -> dict:
    """Porte declarado contra o porte real de `alvo` — o mesmo `alvo` que `backlog.projetar` aceita.

    `unidades_ou_tarefas` e `arquivos_declarados` saem `None` no pequeno; só `arquivos_declarados`
    sai `None` no médio — nenhum dos dois tem unidade para ler `## Arquivos` (D-19).
    `linhas_alteradas` só é tentado quando há arquivos declarados. Sem eles, o motivo separa dois
    estados que não são a mesma coisa: `arquivos is None` (pequeno e médio, que não têm unidade)
    fica com `motivo_nao_medido` também `None` — o sinal de "não se aplica", que sai `—` na
    tabela; lista **vazia** é um plano grande que declarou zero caminho, e sai
    `nenhum caminho declarado`. Colapsar os dois imprimia a string `não medido (None)` numa tabela
    que é append-only e portanto não se corrige reprojetando (`L-28`). Falha de
    git (comando ausente, git sem responder, ou plano sem commit de criação) devolve
    `(None, motivo)`, nunca zero e nunca exceção — a única exceção real é frontmatter estrutural
    quebrado, que `regioes.ler_campo` já levanta antes de chegar aqui.
    """
    arquivo_do_plano = _arquivo_do_plano(alvo)
    dir_plano = arquivo_do_plano.parent

    plan_size = _plan_size(arquivo_do_plano)

    if plan_size == "pequeno":
        quantidade, arquivos = None, None
    elif plan_size == "médio":
        quantidade, arquivos = _contar_tarefas(arquivo_do_plano), None
    else:
        unidades = _listar_unidades(dir_plano)
        quantidade = len(unidades)
        arquivos = _arquivos_declarados(unidades)

    if arquivos:
        linhas, motivo = _linhas_alteradas(arquivo_do_plano, arquivos)
    elif arquivos is None:
        linhas, motivo = None, None
    else:
        linhas, motivo = None, "nenhum caminho declarado"

    return {
        "href": arquivo_do_plano.relative_to(lib.plan_root()).as_posix(),
        "nome": arquivo_do_plano.stem,
        "porte_declarado": plan_size or "não declarado",
        "unidades_ou_tarefas": quantidade,
        "arquivos_declarados": arquivos,
        "linhas_alteradas": linhas,
        "motivo_nao_medido": motivo,
        "fechado_em": date.today().isoformat(),
    }


def _celula_linhas(arquivos: list[str] | None, linhas: int | None, motivo: str | None) -> str:
    if arquivos is None:
        return "—"
    if linhas is not None:
        return str(linhas)
    return f"não medido ({motivo})"


def _linha_tabela(medicao: dict, href: str) -> str:
    unidades = medicao["unidades_ou_tarefas"]
    celula_unidades = "—" if unidades is None else str(unidades)

    arquivos = medicao["arquivos_declarados"]
    celula_arquivos = "não declarado" if arquivos is None else str(len(arquivos))

    celula_linhas = _celula_linhas(arquivos, medicao["linhas_alteradas"], medicao["motivo_nao_medido"])

    return (
        f"| [{medicao['nome']}]({href}) | {medicao['porte_declarado']} | {celula_unidades} |"
        f" {celula_arquivos} | {celula_linhas} | {medicao['fechado_em']} |\n"
    )


def registrar(alvo: Path) -> str | None:
    """Acrescenta a linha de `medir(alvo)` a `porte-medido.md` — `None`, sem escrever, se já existe.

    Checa a linha existente **antes** de medir: um plano já registrado não dispara `medir` de novo,
    então uma segunda chamada não chama `subprocess` nenhuma vez — não só não escreve.

    Cria o arquivo com frontmatter e cabeçalho na primeira chamada, caso ainda não exista — o
    projeto real já o tem versionado; o bootstrap aqui é para quem instala o mecanismo sem o dado
    (teste incluso), e nunca reescreve uma linha já gravada.
    """
    arquivo_do_plano = _arquivo_do_plano(alvo)
    href = f"../{arquivo_do_plano.relative_to(lib.plan_root()).as_posix()}"

    caminho = lib.plan_root() / "system" / "porte-medido.md"
    if not caminho.is_file():
        caminho.parent.mkdir(parents=True, exist_ok=True)
        caminho.write_text(_CONTEUDO_INICIAL, encoding="utf-8")

    texto = caminho.read_text(encoding="utf-8")
    if f"]({href})" in texto:
        return None

    linha = _linha_tabela(medir(arquivo_do_plano), href)
    texto = texto if texto.endswith("\n") else texto + "\n"
    caminho.write_text(texto + linha, encoding="utf-8")
    return linha
