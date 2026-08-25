#!/usr/bin/env python3
"""Ponto de entrada do hook `PostCompact` — nomeia rules com `paths:` que não voltaram.

Unidade 0001-05. `systemMessage` também é descartado neste evento — medido em 2026-08-24 contra
`code.claude.com/docs/en/hooks`: "Claude Code discards a PostCompact hook's systemMessage and
continue fields." O canal real é stderr com exit code 2: a mesma doc mostra este evento como
"Shows stderr to user only" para exit 2, e "PostCompact hooks have no decision control. They
can't affect the compaction result" — o exit 2 aqui não bloqueia nada, só exibe.

O estado — quais rules com `paths:` estavam ativas — vem do arquivo que `instructions_loaded.py`
mantém por sessão. É limpo depois do anúncio: o próximo ciclo de compactação começa vazio, e uma
rule que nunca mais for lida continua sendo nomeada a cada compactação seguinte, porque volta a
entrar no estado assim que `instructions_loaded.py` a vir carregar de novo.
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
        estado = Path(gettempdir()) / f"decode-and-code-rules-ativas-{sessao}.json"

        ativas_antes = activation_notice.ler_estado(estado)
        anuncio = activation_notice.anunciar_post_compact(ativas_antes, voltaram=[])
        activation_notice.limpar_estado(estado)

        if anuncio:
            print(anuncio, file=sys.stderr)
            return 2
    except Exception:
        pass
    return 0


if __name__ == "__main__":
    sys.exit(main())
