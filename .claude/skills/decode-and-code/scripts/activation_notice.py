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
"""

from __future__ import annotations

import json
from pathlib import Path


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
