#!/usr/bin/env python3
"""Ponto de entrada do hook `PreToolUse` — liga stdin e stdout ao mecanismo, sem decidir nada.

Unidade 0001-04. Toda a decisão vive em `guardrail.decidir`; este arquivo só lê o payload
de stdin, resolve `.claude/guardrails.json` do projeto que iniciou a sessão, e escreve a
resposta no formato que o hook espera. Roda em toda chamada de ferramenta — nada de I/O além
da leitura do arquivo de regras, e nada de import pesado (norma, *Restrições conhecidas*).

`CLAUDE_PROJECT_DIR`, não `__file__`. Medido em 2026-09-04 contra o pacote instalado num
projeto consumidor (AmFlow): `Path(__file__).resolve().parent.parent` acerta rodando da
fonte — `.claude/hooks/` fica dois níveis abaixo de `.claude/`, onde `guardrails.json`
também mora —, mas erra empacotado: `empacotar._copiar_hooks` escreve `hooks/` sem o
prefixo `.claude/` (irmã de `skills/`, `agents/`; `_escrever_hooks_json` documenta a troca
de âncora). `parent.parent` a partir do hook instalado cai na raiz da versão do plugin,
comum a qualquer projeto que instale a mesma versão — o oposto do que `guardrail.py`
declara ("a instância vive no `guardrails.json` do projeto que instala, e é só ela que não
viaja no plugin"). `CLAUDE_PROJECT_DIR` resolve os dois casos pelo mesmo caminho: descreve o
processo do hook, não a posição do arquivo no disco.

Não contradiz `lib.py` ("`CLAUDE_PROJECT_DIR`... inexistente para um script invocado por
Bash") — mede outro processo. `lib.repo_root()` serve script que Claude chama via Bash
(`rules.py`, `registry.py`...), onde a variável de fato não chega. Este arquivo é hook — o
dispatcher do Claude Code invoca o processo diretamente —, e a doc oficial
(`code.claude.com/docs/en/hooks`, *Exec form and shell form*) é explícita: hook, servidor
MCP stdio e LSP de plugin recebem a variável no ambiente do processo; comando de Bash, não.
"""

from __future__ import annotations

import json
import os
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "skills" / "decode-and-code" / "scripts"))
import guardrail  # noqa: E402

REGRAS = Path(os.environ.get("CLAUDE_PROJECT_DIR", "")) / ".claude" / "guardrails.json"


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
