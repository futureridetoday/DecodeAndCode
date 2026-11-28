#!/usr/bin/env python3
"""Hook `SessionStart` (matcher `startup`) — propõe o setup pendente, a migração para o codex e o huddle atrasado.

Planos 0008, T6, e 0009-05. Sem `setup.md` concluído (ausente, ou `completed_at` vazio), propõe
`/decode-and-code:setup` e só isso — um aviso por vez, e a checagem vem antes de `huddle.usuario`,
porque projeto recém-aberto pode não ter `docs/`, `.claude/` nem `user.name`. Com o setup
concluído, lê o arquivo de huddle de quem abre a sessão e, com entrada aberta e `reminder_days`
dias ou mais desde `last_huddle` (ou `created`), avisa do huddle. Em ambos devolve `systemMessage`
para a pessoa e `additionalContext` para o modelo. Com o setup concluído e algo do método anterior
ainda no projeto (`migracao.pendencias`, parte 2.4 do redesign), avisa também da migração. Nunca escreve, e fica em silêncio em qualquer outro caso e em qualquer erro: um
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
import eventos  # noqa: E402
import huddle  # noqa: E402
import migracao  # noqa: E402
import setup  # noqa: E402

LEMBRETE_PADRAO = 7


def _setup_pendente(projeto: Path) -> bool:
    arquivo = setup.caminho(projeto)
    if not arquivo.is_file():
        return True
    return not huddle._campo_sem_aspas(arquivo, "completed_at")


def _aviso_setup(projeto: Path) -> dict:
    try:
        anterior = migracao.aviso_pendente(projeto)
    except Exception:
        anterior = False
    if anterior:
        # Projeto que já usava o método antes do setup existir (E-01 do teste final do DC 3.0).
        return {
            "systemMessage": (
                "Este projeto usa o método anterior do decode-and-code, que trocou a norma pelo codex. "
                "Rode /decode-and-code:setup: ele começa pela migração, item por item, com o seu sim."
            ),
            "hookSpecificOutput": {
                "hookEventName": "SessionStart",
                "additionalContext": (
                    "O projeto tem o que o método anterior gravou (dc.py migrar lista) e ainda não fez o "
                    "setup. Proponha /decode-and-code:setup, que começa pela migração; nada se apaga "
                    "sem o sim da pessoa."
                ),
            },
        }
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


def _aviso_huddle(projeto: Path, hoje: date) -> tuple[str, str] | None:
    """`(systemMessage, additionalContext)` do huddle atrasado, ou `None`."""
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

    return (
        f"Huddle: {abertas} entrada(s) aberta(s), último huddle há {dias} dias. "
        "Rode /decode-and-code:huddle.",
        f"O huddle da pessoa desta sessão tem {abertas} entrada(s) aberta(s) e o último foi há "
        f"{dias} dias. Se fizer sentido, sugira /decode-and-code:huddle.",
    )


def _aviso_migracao(projeto: Path) -> tuple[str, str] | None:
    """O que o projeto ainda tem do método anterior ao codex (parte 2.4 do redesign), ou `None`."""
    if not migracao.aviso_pendente(projeto):
        return None
    return (
        "O decode-and-code trocou a norma pelo codex, e este projeto ainda tem o que o método anterior "
        "gravou. Rode /decode-and-code:setup para migrar, item por item, com o seu sim.",
        "O projeto tem pendências da migração para o codex (dc.py migrar as lista): a cópia da norma ou "
        "um huddle que ainda a cita. Proponha /decode-and-code:setup, "
        "que conduz a migração; nada se apaga sem o sim da pessoa.",
    )


def _aviso_erros(projeto: Path, hoje: date) -> tuple[str, str] | None:
    """Os `E-XX` do log sem resolução há `eventos.ALARME_DIAS` dias ou mais (plano 0018, `D-08`)."""
    ids = eventos.atrasados(projeto, hoje)
    if not ids:
        return None
    lista = ", ".join(ids)
    return (
        f"Log: {len(ids)} erro(s) do método sem resolução há {eventos.ALARME_DIAS} dias ou mais ({lista}).",
        f"Há {len(ids)} erro(s) do decode-and-code em .claude/log/erros/ sem resolução há "
        f"{eventos.ALARME_DIAS} dias ou mais ({lista}). Sugira olhá-los e resolvê-los com dc.py log-resolver.",
    )


def aviso(projeto: Path, hoje: date) -> dict | None:
    """O JSON do hook, ou `None` quando não há o que lembrar. Pode levantar — `main` silencia.

    O setup pendente vem sozinho, como antes; depois dele, o huddle atrasado e os `E-XX` atrasados
    do log saem juntos, cada um quando há o que dizer.
    """
    if _setup_pendente(projeto):
        return _aviso_setup(projeto)
    try:
        parte_huddle = _aviso_huddle(projeto, hoje)
    except Exception:
        parte_huddle = None  # sem `user.name` ou huddle ilegível: o alarme do log ainda sai
    try:
        parte_migracao = _aviso_migracao(projeto)
    except Exception:
        parte_migracao = None  # aviso que falha não trava a abertura
    partes = [parte for parte in (parte_migracao, parte_huddle, _aviso_erros(projeto, hoje)) if parte]
    if not partes:
        return None
    return {
        "systemMessage": " ".join(mensagem for mensagem, _ in partes),
        "hookSpecificOutput": {
            "hookEventName": "SessionStart",
            "additionalContext": " ".join(contexto for _, contexto in partes),
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
