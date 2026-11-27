#!/usr/bin/env python3
"""Atalho do `dc.py` compartilhado — `P-14` do plano `apply-plugin-review`.

A liberação do `allowed-tools` casa o **texto** do comando. Com o caminho
`skill/../decode-and-code/scripts/dc.py` o modelo o normaliza antes de rodar (tira o `..`), e a regra
deixa de casar — medido em sessão real: 11 recusas nas três skills. Este arquivo mora na pasta de
cada skill, então o comando é `${CLAUDE_SKILL_DIR}/dc.py`, sem `..` para normalizar.

Só executa o `dc.py` da pasta compartilhada, com o mesmo `argv`, o mesmo stdin e o mesmo código de
saída; a lógica não mora aqui. As cópias, uma por skill do método, são idênticas, e
um teste confere.
"""

import runpy
from pathlib import Path

runpy.run_path(
    str(Path(__file__).resolve().parent.parent / "decode-and-code" / "scripts" / "dc.py"),
    run_name="__main__",
)
