#!/usr/bin/env python3
"""Mecanismo de anúncio de ativação — hooks `InstructionsLoaded`, `PostCompact` e `SubagentStart`.

Unidade 0001-05. Nomeia arquivo, `load_reason` e momento — nunca copia conteúdo. Uma função por
evento, sem ramificação aninhada; qual canal cada anúncio sai (log, stderr, silêncio) é decisão de
cada ponto de entrada em `.claude/hooks/`, nunca deste módulo.

O canal saiu diferente do desenhado: o passo 1 desta unidade previa `systemMessage`, mas a doc
oficial (`code.claude.com/docs/en/hooks`, lida em 2026-08-24) afirma, para os dois eventos que
mais importam aqui, que o campo é descartado —
"Claude Code discards their JSON output fields, such as systemMessage and continue" para
`InstructionsLoaded`, e a mesma frase, com "a PostCompact hook's", para `PostCompact`. A troca de
canal está registrada como decisão no corpo da unidade e como `L-25` no plano.

Path-scoped rules (`payload["globs"]` não vazio) precisam de estado entre o `InstructionsLoaded`
que as carrega e o `PostCompact` que verifica se voltaram — os dois eventos não compartilham
payload. `ler_estado`/`registrar_estado`/`limpar_estado` são esse estado, um arquivo por sessão
(`session_id`), fora do repositório: é dado de execução, não artefato do projeto.

Falha aberta e silenciosa por construção: as quatro funções de anúncio nunca levantam — payload
malformado ou fora de escopo devolve `None`, e quem chama decide não escrever nada.

`relatorio` (unidade 0001-11) lê o log de uma sessão já escrita — o mesmo arquivo que
`instructions_loaded.py` grava — e devolve o veredito por linha que a `L-27` cobrava como
procedimento e não como artefato: escopo não respeitado, guideline desligada que continua
carregando (`L-26`), e a colisão de escopo entre duas rules com `paths:` (`L-05`). Só leitura, e
reaproveita `rules._entradas_de_paths` para não duplicar a leitura de glob.
"""

from __future__ import annotations

import json
import re
from pathlib import Path

import lib
import regioes
import rules


def anunciar_instructions_loaded(payload: dict) -> str | None:
    """Nomeia `file_path` e `load_reason`, brutos — `None` se algum dos dois faltar.

    O valor de `load_reason` não é traduzido nem agrupado: é o que serve para depurar rule com
    `paths:` (`session_start`, `path_glob_match`, `compact`, `nested_traversal`, `include`).
    """
    caminho = payload.get("file_path")
    motivo = payload.get("load_reason")
    if not caminho or not motivo:
        return None
    return f"instrução carregada: {caminho} (load_reason={motivo})"


def rule_com_paths(payload: dict) -> str | None:
    """`file_path` de um load com `globs` presente — só existe para rule com `paths:`.

    `None` quando `globs` está ausente ou vazio: é o sinal de que este load não é de uma rule com
    escopo de arquivo, e por isso não entra no estado que o `PostCompact` compara.
    """
    if not payload.get("globs"):
        return None
    return payload.get("file_path") or None


def anunciar_post_compact(ativas_antes: list[str], voltaram: list[str]) -> str | None:
    """Nomeia o que está em `ativas_antes` e não em `voltaram` — `None` se não sobrar nada.

    A perda continua a mesma (rule com `paths:` só recarrega quando um arquivo que casa o glob é
    lido de novo); o que muda é que ela deixa de ser silenciosa.
    """
    perdidas = [caminho for caminho in ativas_antes if caminho not in voltaram]
    if not perdidas:
        return None
    linhas = "\n".join(f"  - {caminho}" for caminho in perdidas)
    return f"rules com paths: ativas antes da compactação e ainda não recarregadas:\n{linhas}"


def anunciar_subagent_start(payload: dict) -> str | None:
    """Nomeia `agent_type` e `agent_id` — `None` se algum dos dois faltar."""
    tipo = payload.get("agent_type")
    id_agente = payload.get("agent_id")
    if not tipo or not id_agente:
        return None
    return f"subagente iniciado: {tipo} ({id_agente})"


def ler_estado(estado: Path) -> list[str]:
    """Lista de rules com `paths:` ativas — vazia se o arquivo não existir ou vier corrompido."""
    try:
        return json.loads(estado.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return []


def registrar_estado(estado: Path, file_path: str) -> None:
    """Acrescenta `file_path` à lista de rules ativas da sessão, sem duplicar."""
    ativas = ler_estado(estado)
    if file_path not in ativas:
        ativas.append(file_path)
    estado.write_text(json.dumps(ativas), encoding="utf-8")


def limpar_estado(estado: Path) -> None:
    """Reseta o estado depois do anúncio de `PostCompact` — o próximo ciclo começa vazio."""
    estado.write_text("[]", encoding="utf-8")


_LINHA_LOG_RE = re.compile(r"^instrução carregada: (?P<caminho>.+) \(load_reason=(?P<motivo>[^)]+)\)$")


def relatorio(caminho_log: Path) -> list[str]:
    """Lê o log de ativação de uma sessão e devolve uma linha por instrução, com o veredito.

    Levanta `FileNotFoundError` se `caminho_log` não existir — comportamento nativo de
    `Path.read_text`. Linha que não casa o formato de `anunciar_instructions_loaded` entra
    marcada como ilegível, nunca derruba a leitura das demais. Só leitura: sinaliza os três casos
    da norma, seção *Validar a ativação*, nunca corrige nada que encontrar.
    """
    linhas = [l for l in Path(caminho_log).read_text(encoding="utf-8").splitlines() if l.strip()]
    analisadas = [(_LINHA_LOG_RE.match(linha), linha) for linha in linhas]

    caminhos_com_paths = sorted(
        {
            m.group("caminho")
            for m, _ in analisadas
            if m and _paths_do_arquivo(m.group("caminho")) is not None
        }
    )
    colididos = _colisoes(caminhos_com_paths)

    saida = []
    for m, linha_original in analisadas:
        if m is None:
            saida.append(f"linha ilegível, marcada: {linha_original!r}")
            continue
        caminho, motivo = m.group("caminho"), m.group("motivo")
        saida.append(f"{caminho} (load_reason={motivo}) — {_veredito(caminho, motivo, colididos)}")
    return saida


def _veredito(caminho: str, motivo: str, colididos: set[str]) -> str:
    """Os três sinais da norma — nenhum, um ou vários, concatenados; `'ok'` quando nenhum aplica."""
    sinais = []
    if motivo == "session_start" and _paths_do_arquivo(caminho) is not None:
        sinais.append("rule com paths: carregada por session_start — escopo não respeitado")
    fora = _fora_do_lugar(caminho)
    if fora:
        sinais.append(fora)
    if caminho in colididos:
        sinais.append("casa o mesmo arquivo que outra rule com paths: ativa nesta sessão (L-05)")
    return "; ".join(sinais) if sinais else "ok"


def _fora_do_lugar(caminho: str) -> str | None:
    """Sinal para norma carregando de onde não deveria — as duas formas da `L-26`.

    A primeira é o destino de `desligar`: carregar de `rules-off/` significa que desligar não
    desligou. A segunda é a forma **histórica**, e é a que motivou toda esta unidade — um `.md`
    em **subdiretório** de `rules/`, que o matcher alcança por recursão. `auditar_arvore` a pega
    estruturalmente, mas só quando alguém roda a suíte; aqui ela é pega em sessão, que é quando
    o dano acontece. Cobrir só o destino corrigido deixava o instrumento cego para o defeito que
    ele existe para ver — conferido em 2026-08-25 contra o log real da falha.
    """
    normalizado = caminho.replace("\\", "/")
    if "/.claude/rules-off/" in normalizado:
        return "caminho sob rules-off/ — desligar não desligou (L-26)"

    marca = "/.claude/rules/"
    if marca in normalizado and "/" in normalizado.split(marca, 1)[1]:
        return "caminho em subdiretório de rules/ — subdiretório carrega, não desliga (L-26)"
    return None


def _paths_do_arquivo(caminho: str) -> list[str] | None:
    """Entradas de `paths:` do arquivo em `caminho` — `None` se ausente ou o arquivo não pôde ser
    lido (movido, apagado, ou de outra árvore que não a atual)."""
    try:
        valor = regioes.ler_campo(Path(caminho), "paths")
    except (OSError, ValueError):
        return None
    if valor is None:
        return None
    return rules._entradas_de_paths(valor) or []


def _colisoes(caminhos_com_paths: list[str]) -> set[str]:
    """Caminhos cujo escopo casa, no disco real, ao menos um arquivo que outro também casa —
    a condição de colisão da `L-05`, verificada contra `lib.repo_root()`, nunca simulada."""
    raiz = lib.repo_root()
    casados_por_caminho: dict[str, set[Path]] = {}
    for caminho in caminhos_com_paths:
        casados: set[Path] = set()
        for entrada in _paths_do_arquivo(caminho) or []:
            try:
                casados |= set(raiz.glob(entrada))
            except (ValueError, NotImplementedError):
                continue
        if casados:
            casados_por_caminho[caminho] = casados

    colididos: set[str] = set()
    itens = list(casados_por_caminho.items())
    for i, (caminho_a, casados_a) in enumerate(itens):
        for caminho_b, casados_b in itens[i + 1 :]:
            if casados_a & casados_b:
                colididos.add(caminho_a)
                colididos.add(caminho_b)
    return colididos
