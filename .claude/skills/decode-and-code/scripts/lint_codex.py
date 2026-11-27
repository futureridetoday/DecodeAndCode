#!/usr/bin/env python3
"""Lints do codex — parte 1.4 do plano do redesign (`docs/codex/redesign-plan.md`).

Três lints, todos só de leitura, cada um devolvendo a lista de problemas (vazia quando aprova):

- `dependencia` (item 54 do inventário, regra 1 do guia): nenhum trecho do codex cita mecanismo —
  caminho, evento de hook, comando de barra, versão do Claude Code, nome de skill, script ou hook do
  DC em forma de identificador, ou nome do projeto.
- `repeticao` (item 55, invariante *uma fonte por fato*): nenhum trecho de `N` palavras do codex
  aparece repetido num alvo — as skills do DC e a foundation, ou os arquivos passados.
- `estrutura` (regras 2 e 7 do guia e a leitura por título): título único, seção que abre com
  *O que é* e fecha com *Ver também*, todo *Ver também* aponta para título que existe, e nenhuma
  seção passa do teto de linhas.

Por que nomes de skill e de script só contam em forma de identificador: medido em 2026-11-26, a
busca por palavra solta deu cerca de 200 falsos positivos no codex aprovado, porque `derive`,
`setup`, `rethink`, `huddle`, `porte`, `handoff` e `escopo` também são termos do método. Entre
crases, com extensão, num comando de barra, ou com `-` ou `_` no nome, o falso positivo some.

Por que `N = 6`: medido no mesmo dia contra as skills de então — 25 trechos com 4 palavras, 6 com
5, 2 com 6 e nenhum a partir de 7; com 6, o lint ainda pega a repetição real que a medição achou.

Os três rodam na suíte, e com ela no CI: estrutura e dependência sobre o codex, repetição sobre as
skills do DC, com a lista dos trechos conhecidos que ainda faltam sair (`REPETICOES_CONHECIDAS` no
teste).
"""

from __future__ import annotations

import argparse
import re
import sys
from dataclasses import dataclass
from pathlib import Path

CODEX_DIR = Path(__file__).resolve().parent.parent / "codex"
SKILLS_DIR = Path(__file__).resolve().parent.parent.parent

JANELA_PADRAO = 6
TETO_DE_LINHAS = 40

# Eventos de hook do Claude Code — o nome de um deles no codex é mecanismo, não método.
EVENTOS_DE_HOOK = (
    "PreToolUse", "PostToolUse", "PostToolUseFailure", "UserPromptSubmit", "Notification", "Stop",
    "SubagentStart", "SubagentStop", "PreCompact", "SessionStart", "SessionEnd",
    "InstructionsLoaded",
)

_PADROES_FIXOS = (
    ("caminho", re.compile(r"\.claude/|\$\{CLAUDE_\w*|\b[\w./-]+\.(?:py|sh|json|ya?ml|toml)\b")),
    ("evento de hook", re.compile(r"\b(?:" + "|".join(EVENTOS_DE_HOOK) + r")\b")),
    ("comando de barra", re.compile(r"(?<![\w<])/[a-z][\w-]*:[\w-]+")),
    ("versão", re.compile(r"\bClaude Code\b|\bv?\d+\.\d+\.\d+\b")),
)

_CODE_SPAN = re.compile(r"`([^`]+)`")
_ROTULO = re.compile(r"\*\*[^*]+:\*\*")
_VER_TAMBEM = "**Ver também:**"
_O_QUE_E = "**O que é:**"


@dataclass
class Secao:
    arquivo: Path
    titulo: str
    linha: int  # linha do título no arquivo, contando de 1
    linhas: list[str]  # do título até antes do próximo, sem as linhas vazias do fim


def _corpo(texto: str) -> tuple[list[str], int]:
    """Linhas do arquivo sem o frontmatter, e o deslocamento até a primeira delas."""
    linhas = texto.split("\n")
    if linhas and linhas[0].strip() == "---":
        for i in range(1, len(linhas)):
            if linhas[i].strip() == "---":
                return linhas[i + 1:], i + 1
    return linhas, 0


def secoes(arquivo: Path) -> list[Secao]:
    """As seções `## ` de um capítulo do codex, na ordem em que aparecem."""
    linhas, desloc = _corpo(arquivo.read_text(encoding="utf-8"))
    achadas: list[Secao] = []
    for i, linha in enumerate(linhas):
        if linha.startswith("## "):
            achadas.append(Secao(arquivo, linha[3:].strip(), desloc + i + 1, [linha]))
        elif achadas:
            achadas[-1].linhas.append(linha)
    for secao in achadas:
        while secao.linhas and not secao.linhas[-1].strip():
            secao.linhas.pop()
    return achadas


def capitulos(codex_dir: Path | list[Path]) -> list[Path]:
    """Os capítulos de uma pasta do codex, ou de várias — o núcleo e o capítulo de cada módulo."""
    pastas = codex_dir if isinstance(codex_dir, list) else [codex_dir]
    return sorted((c for p in pastas for c in p.glob("*.md")), key=lambda c: (str(c.parent), c.name))


def pastas_do_codex() -> list[Path]:
    """O núcleo e o capítulo de cada módulo presente: os lints conferem os dois juntos, porque o
    capítulo do módulo cita títulos do núcleo em *Ver também*."""
    import lib

    return [CODEX_DIR] + [m["path"] / "codex" for m in lib.modulos() if (m["path"] / "codex").is_dir()]


def _ver_tambem(secao: Secao) -> list[str] | None:
    """Os títulos citados em *Ver também*, ou `None` quando a seção não tem o campo."""
    texto = " ".join(secao.linhas)
    if _VER_TAMBEM not in texto:
        return None
    lista = texto.split(_VER_TAMBEM, 1)[1].strip().rstrip(".")
    return [t.strip() for t in lista.split(",") if t.strip()]


# --- estrutura ---------------------------------------------------------------------------------


def lint_estrutura(codex_dir: Path | list[Path], teto: int = TETO_DE_LINHAS) -> list[str]:
    todas = [s for cap in capitulos(codex_dir) for s in secoes(cap)]
    titulos: dict[str, Secao] = {}
    problemas: list[str] = []
    for s in todas:
        onde = f"{s.arquivo.name}:{s.linha}"
        if s.titulo in titulos:
            primeira = titulos[s.titulo]
            problemas.append(
                f"{onde}: título repetido, {s.titulo!r} já está em "
                f"{primeira.arquivo.name}:{primeira.linha}"
            )
        else:
            titulos[s.titulo] = s
        if len(s.linhas) > teto:
            problemas.append(f"{onde}: {s.titulo!r} tem {len(s.linhas)} linhas, acima do teto de {teto}")
        primeira_util = next((l for l in s.linhas[1:] if l.strip()), "")
        if not primeira_util.startswith(_O_QUE_E):
            problemas.append(f"{onde}: {s.titulo!r} não abre com {_O_QUE_E}")
    for s in todas:
        refs = _ver_tambem(s)
        onde = f"{s.arquivo.name}:{s.linha}"
        if refs is None:
            problemas.append(f"{onde}: {s.titulo!r} não tem {_VER_TAMBEM}")
            continue
        for ref in refs:
            if ref not in titulos:
                problemas.append(f"{onde}: {s.titulo!r} cita em Ver também um título que não existe: {ref!r}")
    return problemas


# --- dependência -------------------------------------------------------------------------------


def nomes_de_mecanismo(skills_dir: Path) -> set[str]:
    """Nomes de skill, script e hook do DC, lidos do disco — sem lista mantida à mão.

    No repositório, as skills ficam em `.claude/skills/` e os hooks em `.claude/hooks/`; no plugin
    instalado, em `skills/` e `hooks/` — nos dois casos, os hooks são irmãos da pasta das skills.
    """
    nomes = {p.parent.name for p in skills_dir.glob("*/SKILL.md")}
    nomes |= {p.stem for p in skills_dir.glob("*/scripts/*.py")}
    nomes |= {p.stem for p in (skills_dir.parent / "hooks").glob("*.py")}
    return nomes


def nomes_de_projeto(raiz: Path | None, repo: str | None) -> set[str]:
    """O nome da pasta do projeto e o do repositório declarado — os dois, quando houver."""
    nomes = set()
    if raiz is not None:
        nomes.add(raiz.name)
    if repo:
        nomes.add(repo.rsplit("/", 1)[-1])
    return {n for n in nomes if n}


def _achados_na_linha(linha: str, nomes: set[str], projetos: set[str]) -> list[tuple[str, str]]:
    achados = [(tipo, m.group(0)) for tipo, padrao in _PADROES_FIXOS for m in padrao.finditer(linha)]
    for span in _CODE_SPAN.findall(linha):
        for token in re.split(r"[\s/]+", span.strip()):
            base = token[:-3] if token.endswith(".py") else token
            if base in nomes:
                achados.append(("nome de skill, script ou hook", token))
    for nome in sorted(nomes):
        if ("-" in nome or "_" in nome) and re.search(rf"(?<![\w-]){re.escape(nome)}(?![\w-])", linha):
            achados.append(("nome de skill, script ou hook", nome))
    for projeto in sorted(projetos):
        if re.search(rf"\b{re.escape(projeto)}\b", linha):
            achados.append(("nome do projeto", projeto))
    vistos: set[tuple[str, str]] = set()
    return [a for a in achados if not (a in vistos or vistos.add(a))]


def lint_dependencia(codex_dir: Path | list[Path], nomes: set[str], projetos: set[str]) -> list[str]:
    problemas = []
    for cap in capitulos(codex_dir):
        linhas, desloc = _corpo(cap.read_text(encoding="utf-8"))
        for i, linha in enumerate(linhas):
            for tipo, trecho in _achados_na_linha(linha, nomes, projetos):
                problemas.append(f"{cap.name}:{desloc + i + 1}: {tipo}: {trecho!r}")
    return problemas


# --- repetição ---------------------------------------------------------------------------------


def _palavras(linhas: list[str], primeira: int) -> list[tuple[str, int]]:
    """Palavras normalizadas, cada uma com a linha de onde veio; rótulo de campo não conta."""
    saida = []
    for i, linha in enumerate(linhas):
        texto = _ROTULO.sub(" ", linha).lower()
        texto = re.sub(r"[`*_>|#\[\]()\"“”]", " ", texto)
        for palavra in re.findall(r"[\w<>/-]+(?:\.\w+)*", texto):
            saida.append((palavra, primeira + i))
    return saida


def lint_repeticao(codex_dir: Path | list[Path], alvos: list[Path], janela: int = JANELA_PADRAO) -> list[str]:
    origem: dict[tuple[str, ...], str] = {}
    for cap in capitulos(codex_dir):
        for s in secoes(cap):
            corpo = [l for l in s.linhas[1:] if not l.startswith(_VER_TAMBEM)]
            palavras = [p for p, _ in _palavras(corpo, 0)]
            for i in range(len(palavras) - janela + 1):
                origem.setdefault(tuple(palavras[i:i + janela]), f"{cap.name}, {s.titulo}")
    problemas = []
    for alvo in alvos:
        linhas, desloc = _corpo(alvo.read_text(encoding="utf-8"))
        palavras = _palavras(linhas, desloc + 1)
        i = 0
        while i <= len(palavras) - janela:
            chave = tuple(p for p, _ in palavras[i:i + janela])
            if chave not in origem:
                i += 1
                continue
            # estende o trecho enquanto a janela seguinte também vem do codex
            fim = i + janela
            while fim < len(palavras) and tuple(p for p, _ in palavras[fim - janela + 1:fim + 1]) in origem:
                fim += 1
            trecho = " ".join(p for p, _ in palavras[i:fim])
            problemas.append(f"{alvo}:{palavras[i][1]}: repete o codex ({origem[chave]}): {trecho!r}")
            i = fim
    return problemas


def alvos_padrao(skills_dir: Path, plan_root: Path | None) -> list[Path]:
    """As skills do DC e a foundation, quando ela existir."""
    alvos = sorted(skills_dir.glob("*/SKILL.md"))
    if plan_root is not None:
        alvos += sorted((plan_root / "system").glob("foundation*.md"))
    return alvos


# --- linha de comando --------------------------------------------------------------------------


def _contexto_do_projeto() -> tuple[Path | None, str | None, Path | None]:
    """Raiz, repositório declarado e raiz dos planos — `None` no que não se resolve."""
    sys.path.insert(0, str(Path(__file__).resolve().parent))
    try:
        import lib

        raiz = lib.repo_root()
        repo = (lib.config().get("marketplace") or {}).get("source", {}).get("repo")
        return raiz, repo, lib.plan_root()
    except (RuntimeError, ValueError, ImportError):
        return None, None, None


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Lints do codex do decode-and-code.")
    parser.add_argument("lint", choices=("dependencia", "repeticao", "estrutura", "todos"))
    parser.add_argument("alvos", nargs="*", type=Path, help="arquivos para o lint de repetição")
    parser.add_argument("--janela", type=int, default=JANELA_PADRAO)
    args = parser.parse_args(argv)

    raiz, repo, plan_root = _contexto_do_projeto()
    problemas: list[str] = []
    if args.lint in ("estrutura", "todos"):
        problemas += lint_estrutura(pastas_do_codex())
    if args.lint in ("dependencia", "todos"):
        problemas += lint_dependencia(pastas_do_codex(), nomes_de_mecanismo(SKILLS_DIR), nomes_de_projeto(raiz, repo))
    if args.lint in ("repeticao", "todos"):
        alvos = args.alvos or alvos_padrao(SKILLS_DIR, plan_root)
        problemas += lint_repeticao(pastas_do_codex(), alvos, args.janela)

    for problema in problemas:
        print(problema)
    if not problemas:
        print(f"lint {args.lint}: ok")
    return 1 if problemas else 0


if __name__ == "__main__":
    sys.exit(main())
