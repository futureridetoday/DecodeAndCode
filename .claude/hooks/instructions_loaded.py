#!/usr/bin/env python3
"""Ponto de entrada do hook `InstructionsLoaded` — loga o anúncio de cada instrução carregada.

Unidade 0001-05. `systemMessage` é descartado pelo Claude Code neste evento — medido em
2026-08-24 contra `code.claude.com/docs/en/hooks`: "Claude Code discards their JSON output
fields, such as systemMessage and continue. Use this event for audit logging, compliance
tracking, or observability." O canal é exatamente esse uso: um arquivo de log por sessão, fora
do repositório. Roda em todo carregamento de instrução — nada de I/O além de uma escrita de
arquivo pequena (norma, *Restrições conhecidas*).
"""

from __future__ import annotations

import json
import sys
from pathlib import Path
from tempfile import gettempdir

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "skills" / "decode-and-code" / "scripts"))
import activation_notice  # noqa: E402


def main() -> int:
    try:
        payload = json.loads(sys.stdin.read())
        sessao = payload.get("session_id", "sem-sessao")

        anuncio = activation_notice.anunciar_instructions_loaded(payload)
        if anuncio:
            log = Path(gettempdir()) / f"decode-and-code-activation-{sessao}.log"
            with log.open("a", encoding="utf-8") as arquivo:
                arquivo.write(anuncio + "\n")
    except Exception:
        pass
    return 0


if __name__ == "__main__":
    sys.exit(main())
