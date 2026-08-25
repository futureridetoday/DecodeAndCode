#!/usr/bin/env python3
"""Oráculo de verificação — projeta `state` e `verified_at`, unidade 0002-08.

Lê o teste que a unidade declara no frontmatter, roda pelo runner da
extensão e escreve o estado derivado de volta — nunca o corpo (decisão 13).
Teste declarado mas inexistente no disco não é erro: é o caso normal de
unidade nova, e resulta em `spec` (decisão 15).

A escolha do runner vem do mapa `runners` do config — cada extensão de teste
aponta para o script que a roda, caminho relativo à raiz do repositório. O
caminho do teste declarado é passado por inteiro ao runner, sem reduzir ao
diretório-pacote — granularidade de arquivo, não de pacote (unidade 0005-02; a
redução a pacote era a imprecisão aceita pela norma, lacuna L-05 do plano 0002).

Timeout conta como falha (`spec`), nunca como exceção: o objetivo do timeout
é só impedir que um teste interativo trave a verificação, não distinguir
esse caso de qualquer outro jeito de o teste não provar que passa.

`unit_type: norma` (unidade 0001-13) ramifica antes de qualquer coisa acima: markdown normativo não
tem `test` — o campo é exigido **vazio** — então o oráculo não pode ser "rodar o teste declarado".
`_verificar_norma` fecha por `lint_unidade` limpo somado à aprovação humana registrada
(`approved_by`/`approved_at`), sem executar `subprocess` nenhum, e copia `approved_at` para
`verified_at`: o fato verificado é a aprovação, e rodar o gate de novo amanhã não pode mover a data
de um fato que não mudou.
"""

from __future__ import annotations

import os
import re
import subprocess
from datetime import date
from pathlib import Path

import lib
import lint_unidade
import regioes

# Generoso o bastante para uma suíte real (inclui o cold start do vitest);
# existe só para não travar em teste interativo, não é orçamento de performance.
TIMEOUT_SEGUNDOS = 120

# Sentinela contra reentrância. Esta unidade é a única do plano capaz de se
# auto-invocar: verificar() reduz o teste ao pacote e roda a suíte inteira, e o
# teste desta unidade vive nessa suíte. Uma chamada real lá dentro reentra sem
# fim — aconteceu em 2026-07-25 e produziu 763 processos órfãos, porque
# subprocess.kill() mata só o filho direto e o timeout não alcança a árvore.
# O ambiente do subprocesso carrega a marca; reentrar levanta em vez de rodar.
SENTINELA_REENTRANCIA = "DECODE_AND_CODE_VERIFICACAO_EM_CURSO"


def verificar(unidade: Path, dry_run: bool = False) -> tuple[str, bool]:
    """Deriva o estado de `unidade` a partir do teste que ela declara.

    `unit_type: norma` desvia para `_verificar_norma` antes da checagem de `test` abaixo — norma
    exige `test` vazio, então a regra "sem test declarado, levanta" não se aplica a ela.

    Levanta `ValueError` se o frontmatter não declara `test`, para `dev`/`plan`. Em `dry_run`,
    roda o teste e devolve o estado sem escrever nada — o segundo valor da
    tupla é sempre `False` nesse caso. `verified` exige exit code zero **e**
    texto capturado sem sinal de skip ou zero-teste — exit code zero sozinho
    não distingue "passou" de "não rodou" (plano 0005, F1-F3).
    """
    unit_type = regioes.ler_campo(unidade, "unit_type")
    if unit_type and unit_type.strip() == "norma":
        return _verificar_norma(unidade, dry_run)

    test_declarado = regioes.ler_campo(unidade, "test")
    if not test_declarado or not test_declarado.strip():
        raise ValueError(f"unidade não declara 'test' — {unidade}")

    raiz = lib.repo_root()
    caminho_teste = (raiz / test_declarado.strip()).resolve()

    if caminho_teste.is_file():
        codigo, saida = _executar(caminho_teste, raiz)
        estado = "verified" if codigo == 0 and not _execucao_incompleta(saida) else "spec"
    else:
        estado = "spec"

    if dry_run:
        return estado, False

    verified_at = date.today().isoformat() if estado == "verified" else '""'
    escreveu = regioes.escrever_campos(
        unidade, {"state": estado, "verified_at": verified_at}
    )
    return estado, escreveu


def _verificar_norma(unidade: Path, dry_run: bool) -> tuple[str, bool]:
    """Oráculo de `unit_type: norma` — estrutura válida somada a aprovação humana, sem rodar nada.

    `lint_unidade.lint` já cobre a aprovação: uma `norma` sem `approved_by`/`approved_at`
    preenchidos não passa no lint, então "lint limpo" e "aprovação declarada" são a mesma condição,
    nunca duas checagens independentes. `verified_at` copia `approved_at` — nunca `date.today()` —
    porque o fato verificado é a aprovação do humano, não a data em que o script rodou.
    """
    estado = "verified" if not lint_unidade.lint(unidade) else "spec"

    if dry_run:
        return estado, False

    verified_at = regioes.ler_campo(unidade, "approved_at") if estado == "verified" else '""'
    escreveu = regioes.escrever_campos(
        unidade, {"state": estado, "verified_at": verified_at}
    )
    return estado, escreveu


def _executar(caminho_teste: Path, raiz: Path) -> tuple[int, str]:
    """Código de saída e texto (stdout+stderr) do teste — timeout devolve falha e texto vazio.

    Recusa executar se já houver verificação em curso: é aqui que a recursão
    nasceria, e não em `verificar()`. A distinção importa — checar antes faria
    todo teste que chama `verificar()` com subprocesso mockado quebrar quando a
    própria suíte roda dentro de uma verificação, e a unidade jamais poderia
    ser promovida.

    O texto devolvido é o que `verificar()` casa contra os sinais de skip e
    zero-teste — hoje descartado depois do exit code (plano 0005, L-05 do 0004).
    """
    if os.environ.get(SENTINELA_REENTRANCIA):
        raise RuntimeError(
            f"execução de teste aninhada recusada — {caminho_teste}. Já há uma "
            "verificação em curso, e reentrar na suíte recursa sem que timeout "
            "ou kill contenham a árvore. Em teste, mocke subprocess.run."
        )

    comando, cwd = _comando(caminho_teste, raiz)
    ambiente = {**os.environ, SENTINELA_REENTRANCIA: "1"}
    try:
        resultado = subprocess.run(
            comando,
            cwd=cwd,
            timeout=TIMEOUT_SEGUNDOS,
            capture_output=True,
            env=ambiente,
        )
    except subprocess.TimeoutExpired:
        return 1, ""
    saida = resultado.stdout.decode("utf-8", errors="replace") + resultado.stderr.decode(
        "utf-8", errors="replace"
    )
    return resultado.returncode, saida


_SKIPPED_RE = re.compile(r"skipped=(\d+)")
_RAN_ZERO_RE = re.compile(r"(?m)^Ran 0 tests")
# `vitest` escreve "N skipped", sem `=`, na linha de resumo que começa com
# "Tests". Ancorado nessa linha para não casar "N skipped" solto no corpo da
# saída — nome de teste como "returns 5 skipped items" não pode bloquear
# unidade sadia (plano 0006, medição de 2026-08-12).
_VITEST_SKIPPED_RE = re.compile(r"(?m)^[ \t]*Tests\b.*?(\d+) skipped")


def _execucao_incompleta(saida: str) -> bool:
    """Verdadeiro quando `saida` mostra skip (>0) ou zero teste rodado — sinais F1-F3 do plano 0005.

    Cobre os dois runners que o modelo despacha: `unittest`/`test-python.sh`
    (`skipped=N`, `Ran 0 tests`) e `vitest` (`N skipped` na linha de resumo,
    sem `=`) — a extensão que fecha a L-01 do plano 0005 (plano 0006). Zero
    teste no `vitest` já cai no mesmo padrão de skip (`N skipped (N)`), sem
    precisar de regra equivalente a `Ran 0 tests`.
    """
    skip = _SKIPPED_RE.search(saida)
    if skip and int(skip.group(1)) > 0:
        return True
    skip_vitest = _VITEST_SKIPPED_RE.search(saida)
    if skip_vitest and int(skip_vitest.group(1)) > 0:
        return True
    return bool(_RAN_ZERO_RE.search(saida))


def _comando(caminho_teste: Path, raiz: Path) -> tuple[list[str], Path]:
    """Runner pela extensão do teste, resolvido pelo mapa `runners` do config.

    `ValueError` se a extensão não tiver runner declarado. O runner sempre
    roda a partir da raiz do repositório, com o caminho do teste relativo a
    ela — um único mecanismo para qualquer extensão que o config declarar.
    """
    runner = lib.config()["runners"].get(caminho_teste.suffix)
    if runner is None:
        raise ValueError(f"extensão de teste sem runner declarado — {caminho_teste}")
    comando = [str(raiz / runner), str(caminho_teste.relative_to(raiz))]
    return comando, raiz
