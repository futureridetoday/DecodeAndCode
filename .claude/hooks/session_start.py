#!/usr/bin/env python3
"""Hook `SessionStart` (matcher `startup`) — propõe o setup pendente e lembra do huddle atrasado.

Planos 0008, T6, e 0009-05. Sem `setup.md` concluído (ausente, ou `completed_at` vazio), propõe
`/decode-and-code:setup` e só isso — um aviso por vez, e a checagem vem antes de `huddle.usuario`,
porque projeto recém-aberto pode não ter `docs/`, `.claude/` nem `user.name`. Com o setup
concluído, lê o arquivo de huddle de quem abre a sessão e, com entrada aberta e `reminder_days`
dias ou mais desde `last_huddle` (ou `created`), avisa do huddle. Em ambos devolve `systemMessage`
para a pessoa e `additionalContext` para o modelo. Nunca escreve, e fica em silêncio em qualquer outro caso e em qualquer erro: um
lembrete que trava a abertura da sessão é pior que nenhum.

O projeto vem de `CLAUDE_PROJECT_DIR`, nunca de `lib.repo_root()` — a mesma razão do
`pre_tool_use.py`: empacotado, o hook mora no diretório do plugin, não no projeto. Importa só
`lib` (para `plan_root`) e `huddle` (identidade e caminho). O único subprocesso é o
`git config user.name` de `huddle.usuario`.
"""

from __future__ import annotations

import json
import os
import re
import sys
from datetime import date
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "skills" / "decode-and-code" / "scripts"))
import huddle  # noqa: E402
import setup  # noqa: E402

LEMBRETE_PADRAO = 7


def _setup_pendente(projeto: Path) -> bool:
    arquivo = setup.caminho(projeto)
    if not arquivo.is_file():
        return True
    return not huddle._campo_sem_aspas(arquivo, "completed_at")


def _aviso_setup() -> dict:
    return {
        "systemMessage": "Setup do decode-and-code pendente neste projeto. Rode /decode-and-code:setup.",
        "hookSpecificOutput": {
            "hookEventName": "SessionStart",
            "additionalContext": (
                "O setup do decode-and-code ainda não foi feito neste projeto. Proponha à pessoa "
                "/decode-and-code:setup; a skill começa pela confirmação dela, então não inicie "
                "sem o sim."
            ),
        },
    }


def aviso(projeto: Path, hoje: date) -> dict | None:
    """O JSON do hook, ou `None` quando não há o que lembrar. Pode levantar — `main` silencia."""
    if _setup_pendente(projeto):
        return _aviso_setup()

    arquivo = huddle.caminho(projeto, huddle.usuario(projeto))
    if not arquivo.is_file():
        return None

    abertas = len(huddle._CABECALHO_ENTRADA_RE.findall(huddle._secao(arquivo.read_text(encoding="utf-8"), "Abertas") or ""))
    if not abertas:
        return None

    lembrete = huddle._campo_sem_aspas(arquivo, "reminder_days")
    dias_lembrete = int(lembrete) if re.fullmatch(r"\d+", lembrete) else LEMBRETE_PADRAO
    if dias_lembrete == 0:
        return None

    desde = huddle._campo_sem_aspas(arquivo, "last_huddle") or huddle._campo_sem_aspas(arquivo, "created")
    dias = (hoje - date.fromisoformat(desde)).days
    if dias < dias_lembrete:
        return None

    texto = (
        f"Huddle: {abertas} entrada(s) aberta(s), último huddle há {dias} dias. "
        "Rode /decode-and-code:huddle."
    )
    return {
        "systemMessage": texto,
        "hookSpecificOutput": {
            "hookEventName": "SessionStart",
            "additionalContext": (
                f"O huddle da pessoa desta sessão tem {abertas} entrada(s) aberta(s) e o último foi há "
                f"{dias} dias. Se fizer sentido, sugira /decode-and-code:huddle."
            ),
        },
    }


def main() -> int:
    try:
        projeto = os.environ.get("CLAUDE_PROJECT_DIR")
        if projeto:
            saida = aviso(Path(projeto), date.today())
            if saida:
                json.dump(saida, sys.stdout, ensure_ascii=False)
    except Exception:
        pass  # silêncio em qualquer erro, por construção
    return 0


if __name__ == "__main__":
    sys.exit(main())
