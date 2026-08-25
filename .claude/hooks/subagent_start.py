#!/usr/bin/env python3
"""Ponto de entrada do hook `SubagentStart` — anuncia por stderr, o canal que este evento aceita.

Unidade 0001-05. A doc (`code.claude.com/docs/en/hooks`, 2026-08-24) mostra este evento como "No"
para bloqueio e "Shows stderr to user only" para exit code 2 — sem afetar a criação do subagente,
e a mensagem aparece no transcript do próprio subagente, não no da conversa principal.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "skills" / "decode-and-code" / "scripts"))
import activation_notice  # noqa: E402


def main() -> int:
    try:
        payload = json.loads(sys.stdin.read())
        anuncio = activation_notice.anunciar_subagent_start(payload)
        if anuncio:
            print(anuncio, file=sys.stderr)
            return 2
    except Exception:
        pass
    return 0


if __name__ == "__main__":
    sys.exit(main())
