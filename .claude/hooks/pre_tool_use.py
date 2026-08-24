#!/usr/bin/env python3
"""Ponto de entrada do hook `PreToolUse` — liga stdin e stdout ao mecanismo, sem decidir nada.

Unidade 0001-04. Toda a decisão vive em `guardrail.decidir`; este arquivo só lê o payload
de stdin, resolve `.claude/guardrails.json` ao lado deste diretório, e escreve a resposta
no formato que o hook espera. Roda em toda chamada de ferramenta — nada de I/O além da
leitura do arquivo de regras, e nada de import pesado (norma, *Restrições conhecidas*).
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "skills" / "decode-and-code" / "scripts"))
import guardrail  # noqa: E402

REGRAS = Path(__file__).resolve().parent.parent / "guardrails.json"


def main() -> int:
    decisao, aviso = guardrail.decidir(sys.stdin.read(), REGRAS)
    if aviso:
        print(aviso, file=sys.stderr)
    if decisao is not None:
        json.dump(
            {
                "hookSpecificOutput": {
                    "hookEventName": "PreToolUse",
                    "permissionDecision": "deny",
                    "permissionDecisionReason": f"{decisao['regra']}: {decisao['mensagem']}",
                }
            },
            sys.stdout,
        )
    return 0


if __name__ == "__main__":
    sys.exit(main())
