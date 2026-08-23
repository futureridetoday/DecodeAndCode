#!/usr/bin/env bash
# Roda os testes Python do DecodeAndCode com unittest (stdlib).
#
# Exige Python 3.10 — a versão do Cowork. Passar aqui é o que comprova que a
# sintaxe usada roda na VM. Ver .claude/CLAUDE.md, seção Linguagem.
#
# Uso:
#   ./scripts/test-python.sh            todos os diretórios declarados
#   ./scripts/test-python.sh <dir>      apenas um diretório

set -uo pipefail

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"

# Diretórios com testes. Escopo explícito: discover a partir da raiz varreria
# node_modules/ e qualquer cópia. Adicionar aqui ao criar um novo pacote de
# scripts — `unittest discover` não desce em diretório com hífen, então pacote
# nomeado assim precisa vir listado, nunca por varredura do pai.
TEST_DIRS=(
  "scripts"
  ".claude/skills/decode-and-code/scripts"
)

readonly REQUIRED_MINOR=10

find_python() {
  # Preferir o interpretador versionado; aceitar python3 apenas se for 3.10.
  for candidate in python3.10 python3; do
    local bin
    bin="$(command -v "$candidate" 2>/dev/null)" || continue
    if "$bin" -c "import sys; sys.exit(0 if sys.version_info[:2] == (3, $REQUIRED_MINOR) else 1)" 2>/dev/null; then
      echo "$bin"
      return 0
    fi
  done
  return 1
}

if ! PYTHON="$(find_python)"; then
  echo "erro: Python 3.$REQUIRED_MINOR não encontrado." >&2
  echo "" >&2
  echo "Verificamos em 3.$REQUIRED_MINOR porque é a versão do Cowork (3.10.12)." >&2
  echo "No macOS o python3 do sistema é 3.9 e não se atualiza — instale ao lado:" >&2
  echo "" >&2
  echo "  brew install python@3.$REQUIRED_MINOR" >&2
  echo "" >&2
  echo "Não troque o python3 global: afeta outros projetos." >&2
  exit 1
fi

echo "interpretador: $PYTHON ($("$PYTHON" --version 2>&1))"

if [ $# -gt 0 ]; then
  TEST_DIRS=("$@")
fi

failed=0
ran=0

for dir in "${TEST_DIRS[@]}"; do
  target="$REPO_ROOT/$dir"

  if [ -f "$target" ]; then
    # Alvo-arquivo: discover restrito a ele — -s no diretório que o contém,
    # -p no nome exato do arquivo (nunca o padrão test_*.py). -t aponta para
    # o pacote — o pai de "tests", quando é esse o nome do diretório que
    # contém o arquivo — do jeito que já funciona hoje para import relativo
    # (import lib/regioes/verificacao).
    dir_teste="$(dirname "$target")"
    padrao="$(basename "$target")"
    if [ "$(basename "$dir_teste")" = "tests" ]; then
      pacote_dir="$(dirname "$dir_teste")"
      inicio="tests"
    else
      pacote_dir="$dir_teste"
      inicio="."
    fi
    encontrados=1
  elif [ -d "$target" ]; then
    # Sem arquivo de teste, não há o que rodar — não é falha.
    encontrados="$(find "$target" -name 'test_*.py' -type f | wc -l | tr -d ' ')"
    if [ "$encontrados" -eq 0 ]; then
      echo "sem testes: $dir"
      continue
    fi
    pacote_dir="$target"
    inicio="."
    padrao="test_*.py"
  else
    echo "aviso: alvo declarado não existe — $dir" >&2
    failed=1
    continue
  fi

  echo ""
  echo "── $dir ──────────────────────────────────────────"
  # cd no pacote para que o discover resolva os imports relativos a ele.
  saida="$( (cd "$pacote_dir" && "$PYTHON" -m unittest discover -s "$inicio" -p "$padrao" -t . -v) 2>&1 )"
  status=$?
  echo "$saida"

  # Guarda contra verde falso: o discover só desce em diretório que seja pacote.
  # Sem __init__.py ele coleta zero testes e sai com sucesso — o pior caso, porque
  # nada roda e o CI fica verde. Se há arquivo de teste no disco, tem de rodar.
  if echo "$saida" | grep -qE '^Ran 0 tests'; then
    echo "erro: $encontrados arquivo(s) de teste em $dir, mas o discover coletou 0." >&2
    echo "      falta __init__.py no diretório de testes?" >&2
    failed=1
    continue
  fi

  if [ "$status" -eq 0 ]; then
    ran=$((ran + 1))
  else
    failed=1
  fi
done

echo ""
if [ "$failed" -ne 0 ]; then
  echo "FALHOU"
  exit 1
fi

echo "OK — $ran diretório(s) verificado(s)"
