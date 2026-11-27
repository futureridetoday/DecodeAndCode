#!/usr/bin/env python3
"""Ponto de entrada do hook `InstructionsLoaded` — loga o anúncio de cada instrução carregada.

Unidade 0001-05. `systemMessage` é descartado pelo Claude Code neste evento — medido em
2026-08-24 contra `code.claude.com/docs/en/hooks`: "Claude Code discards their JSON output
fields, such as systemMessage and continue. Use this event for audit logging, compliance
tracking, or observability." O canal é exatamente esse uso. Roda em todo carregamento de
instrução — nada de I/O além de uma escrita pequena, porque o custo se paga a cada carregamento.

Desde o plano 0018 (`D-05`) o anúncio vai para `.claude/log/eventos.jsonl` do projeto, com o
`session_id`, e não mais para um arquivo por sessão em `gettempdir()`, que sumia com a sessão. O
projeto vem de `CLAUDE_PROJECT_DIR`, como nos outros hooks; sem ele, ou em projeto sem bootstrap,
nada se escreve (`D-16`).
"""

from __future__ import annotations

import json
import os
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "skills" / "decode-and-code" / "scripts"))
import activation_notice  # noqa: E402
import eventos  # noqa: E402


def main() -> int:
    try:
        projeto = os.environ.get("CLAUDE_PROJECT_DIR")
        payload = json.loads(sys.stdin.read())
        anuncio = activation_notice.anunciar_instructions_loaded(payload)
        if projeto and anuncio:
            sessao = payload.get("session_id", "sem-sessao")
            eventos.registrar(Path(projeto), {"classe": "ativacao", "sessao": sessao, "anuncio": anuncio})
    except Exception:
        pass
    return 0


if __name__ == "__main__":
    sys.exit(main())
