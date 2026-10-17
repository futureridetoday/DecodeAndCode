#!/usr/bin/env python3
"""Runner de teste Python do pacote — o que roda quando o projeto não tem `scripts/test-python.sh`.

Recebe o caminho de um arquivo de teste, relativo ao cwd (a raiz do projeto), e
reproduz o ramo "alvo-arquivo" do `scripts/test-python.sh` deste repositório: o
`unittest discover` é restrito ao arquivo, com `-s` no diretório que o contém.
Se esse diretório se chama `tests`, o pacote é o pai dele e o início é `tests`;
senão o pacote é o próprio diretório. `tests` sem `__init__.py` (layout comum fora deste
repositório) roda com `-t tests`, porque o `discover` recusa início não importável. O `discover` roda com cwd no pacote, para
resolver import relativo a ele — não exige o teste importável da raiz (L-01).

Repassa a saída e o código de saída do `unittest`. Só stdlib, Python 3.10.

Uso: runner_python.py <caminho/do/test_x.py>
"""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path


def main(argv: list[str]) -> int:
    if len(argv) != 1:
        print("uso: runner_python.py <caminho/do/arquivo_de_teste.py>", file=sys.stderr)
        return 2
    teste = Path(argv[0]).resolve()
    if not teste.is_file():
        print(f"erro: arquivo de teste não existe — {argv[0]}", file=sys.stderr)
        return 2
    dir_teste = teste.parent
    if dir_teste.name == "tests":
        # Sem `__init__.py`, `tests` não é importável como pacote: o topo vira o próprio
        # `tests`, e o cwd no pai ainda resolve o import do código testado.
        pacote, inicio = dir_teste.parent, "tests"
        topo = "." if (dir_teste / "__init__.py").exists() else "tests"
    else:
        pacote, inicio, topo = dir_teste, ".", "."
    resultado = subprocess.run(
        [sys.executable, "-m", "unittest", "discover", "-s", inicio, "-p", teste.name, "-t", topo, "-v"],
        cwd=pacote,
    )
    return resultado.returncode


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
