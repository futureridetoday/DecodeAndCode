#!/usr/bin/env python3
"""Módulo comum dos scripts da skill dev-units.

Dá aos demais scripts uma origem confiável — a raiz do repositório e os caminhos
canônicos sob `docs/plan/` — sem depender de variável de ambiente nem do
diretório de trabalho de quem invoca. É módulo importado, não script executável.

`CLAUDE_PLUGIN_ROOT` não serve: medido vazio nos dois ambientes, e no browser
isso causou falha até o script ser localizado com `find`. `CLAUDE_PROJECT_DIR`
também não serve: é substituição literal feita no `hooks.json`, nunca variável
exportada no ambiente de uma sessão — inexistente para um script invocado por
Bash. Restam dois candidatos reais: `__file__` e `cwd`. `repo_root()` tenta
`__file__` primeiro e `cwd` só se o primeiro não resolver — ordem estritamente
aditiva: tudo que resolvia antes continua resolvendo do mesmo jeito, e o `cwd`
só entra em jogo onde hoje se levanta exceção (plugin instalado, cujo
`__file__` mora no diretório do pacote, não no do projeto).

Todo caminho devolvido é resolvido. `relpath` entre um caminho resolvido e outro
não-resolvido produz lixo quando há symlink no meio, e no macOS `/tmp` e `/var`
são symlinks — foi exatamente assim que o move-md quebrou.

A configuração (`config.json`, opcional, ao lado deste diretório `scripts/`) é
lida por `config()` e cacheada em módulo — arquivo do disco sobrepõe os defaults
embutidos, chave a chave. Ausente cai inteiramente nos defaults; malformado
levanta `ValueError` nomeando o arquivo e o campo.
"""

from __future__ import annotations

import json
from pathlib import Path

import regioes

_DEFAULTS = {
    "plan_root": "docs/plan",
    # Marcas da raiz. Só `.claude/` não bastaria: qualquer projeto pode ter uma.
    "root_markers": [".claude", "docs"],
    "move_script": "scripts/move-md.py",
    "runners": {".py": "scripts/test-python.sh", ".ts": "scripts/test-ts.sh"},
    # Identidade do próprio plugin (`D-14` do plano 0009): o pacote não leva o `marketplace.json`.
    # `empacotar.verificar` tira este `repo` do texto antes de procurar o nome do projeto (`DD-06`).
    "marketplace": {
        "name": "future-ride-today",
        "plugin": "decode-and-code",
        "source": {"source": "github", "repo": "futureridetoday/DecodeAndCode"},
    },
}

# Os defaults são a fonte única. `_find_repo_root` lê a versão resolvida pelo config,
# que pode sobrepô-los; esta constante é o valor embutido, não o efetivo.
ROOT_MARKERS = tuple(_DEFAULTS["root_markers"])

# Vocabulário fechado de `plan_size` (unidade 0001-12). Mora aqui, e não em quem o usa, porque
# tem dois leitores com papéis opostos — `scaffold.aprovar`, que é o gate e recusa, e
# `lint_plano.lint`, que só reporta. Duas cópias divergiriam em silêncio, e o sintoma seria o
# lint aprovando o que o gate recusa. Não é config: config se sobrepõe por projeto, e este
# vocabulário é do método (codex, *Porte*).
PLAN_SIZES_VALIDOS = ("pequeno", "médio", "grande")

# Versão do formato do plano (codex, *Plano* e *Plano anterior ao redesign*). Todo plano novo
# declara `format_version: 2`; plano sem o campo é anterior ao redesign e segue a regra de antes,
# onde está. Cada script que muda de regra com o redesign pergunta a versão por `formato`.
FORMATO_ANTERIOR = 1
FORMATO_ATUAL = 2
FORMATOS_VALIDOS = (FORMATO_ANTERIOR, FORMATO_ATUAL)

# Vocabulário fechado de `plan_type` por formato (plano 0012; codex, *Tipo*), com os mesmos dois
# leitores de `PLAN_SIZES_VALIDOS`. O tipo `norma` do formato anterior se chama `rule` no atual.
PLAN_TYPES_POR_FORMATO = {
    FORMATO_ANTERIOR: ("fix", "feature", "remove", "refactor", "norma", "chore", "spike"),
    FORMATO_ATUAL: ("fix", "feature", "remove", "refactor", "rule", "chore", "spike"),
}
PLAN_TYPES_VALIDOS = PLAN_TYPES_POR_FORMATO[FORMATO_ATUAL]

# Vocabulário fechado de `unit_type` por formato: o tipo que muda princípio, guideline ou
# guardrail é aceito pela aprovação, não por teste (codex, *Tipo*).
UNIT_TYPES_POR_FORMATO = {
    FORMATO_ANTERIOR: ("dev", "plan", "norma"),
    FORMATO_ATUAL: ("dev", "plan", "rule"),
}
# Os dois nomes do tipo aceito pela aprovação, um por formato.
TIPOS_DE_APROVACAO = ("norma", "rule")

# Os modos da norma, uma skill por modo — quem o prompt de orquestração cita (`handoff`).
MODOS = ("review-plan", "derive", "implement")

# As skills que viajam no pacote (`empacotar`): os três modos, o `intake`, que antecede o ciclo, o
# `huddle`, que conduz a conversa da pessoa (plano 0008), o `setup`, que conduz o primeiro uso
# (plano 0009), e o `rethink`, que revisa a norma depois de uma mudança de rumo (plano 0020) — sete
# skills, e as quatro últimas não são modo da norma. Acrescentar skill é editar só aqui.
SKILLS = MODOS + ("intake", "huddle", "setup", "rethink")

_config_cache: dict | None = None


def formato(caminho: Path) -> int:
    """Versão do formato de um plano ou de uma unidade — `FORMATO_ANTERIOR` quando não declara.

    A unidade herda a versão do plano: vale o campo dela, se houver, e senão o do arquivo do plano
    na mesma pasta (`<pasta>/<pasta>.md`). Valor fora de `FORMATOS_VALIDOS` levanta `ValueError`
    com o caminho, porque ler um plano pela regra errada é pior que parar.
    """
    candidatos = [caminho]
    plano_da_pasta = caminho.parent / f"{caminho.parent.name}.md"
    if plano_da_pasta != caminho:
        candidatos.append(plano_da_pasta)
    for candidato in candidatos:
        if not candidato.is_file():
            continue
        try:
            valor = regioes.ler_campo(candidato, "format_version")
        except ValueError:
            continue
        valor = (valor or "").strip(" \t\"'")
        if not valor:
            continue
        if not valor.isdigit() or int(valor) not in FORMATOS_VALIDOS:
            raise ValueError(
                f"format_version fora de {FORMATOS_VALIDOS}: {valor!r} em {candidato}"
            )
        return int(valor)
    return FORMATO_ANTERIOR


def _config_path() -> Path:
    """`config.json` na raiz da skill — irmão de `scripts/`, não da raiz do repositório."""
    return Path(__file__).resolve().parent.parent / "config.json"


def config() -> dict:
    """Config resolvida: `config.json` do disco sobreposto aos defaults embutidos — cacheada em módulo."""
    global _config_cache
    if _config_cache is not None:
        return _config_cache

    resolvido = dict(_DEFAULTS)
    caminho = _config_path()
    if caminho.is_file():
        try:
            do_disco = json.loads(caminho.read_text(encoding="utf-8"))
        except json.JSONDecodeError as erro:
            raise ValueError(f"{caminho} malformado — JSON inválido: {erro}") from erro
        if not isinstance(do_disco, dict):
            raise ValueError(f"{caminho} malformado — a raiz precisa ser um objeto")
        for chave, valor in do_disco.items():
            if chave not in _DEFAULTS:
                raise ValueError(f"{caminho} malformado — campo desconhecido: {chave!r}")
            resolvido[chave] = valor

    _config_cache = resolvido
    return resolvido


def _home() -> Path:
    """Home do usuário — em função própria para que o teste possa trocá-la."""
    return Path.home().resolve()


def _find_repo_root(start: Path) -> Path:
    """Sobe a partir de `start` até o diretório que contém todas as marcas do config.

    A home **nunca** é candidata. Plugin instalado mora sob `~/.claude/`, e o
    passeio a partir do `__file__` passa por `~` — que já tem `.claude/` em toda
    máquina com Claude Code, e basta um `~/docs` para casar. Sem esta guarda,
    `repo_root()` devolveria a home em silêncio em vez de cair para o `cwd` e
    achar o projeto de verdade. Medido em 2026-08-28; é a `L-03` do plano `0004`.
    """
    marcadores = config()["root_markers"]
    lar = _home()
    for candidate in (start, *start.parents):
        if candidate == lar:
            continue
        if all((candidate / marker).is_dir() for marker in marcadores):
            return candidate

    marcas = " e ".join(f"{marker}/" for marker in marcadores)
    raise RuntimeError(
        f"raiz do repositório não localizada a partir de {start} — "
        f"nenhum diretório acima contém {marcas} "
        f"(a home, {lar}, é excluída por construção)."
    )


def repo_root() -> Path:
    """Raiz do projeto onde o método opera.

    Tenta `__file__` primeiro — é o que resolve o checkout deste repositório e o
    que a suíte assume ao trocar de `cwd` num teste. Só se isso não resolver —
    plugin instalado, cujo `__file__` mora no diretório do pacote — tenta o
    `cwd`, que dentro do projeto que instalou o método contém as marcas.
    """
    origem_arquivo = Path(__file__).resolve().parent
    try:
        return _find_repo_root(origem_arquivo)
    except RuntimeError:
        pass

    origem_cwd = Path.cwd().resolve()
    try:
        return _find_repo_root(origem_cwd)
    except RuntimeError:
        pass

    marcas = " e ".join(f"{marker}/" for marker in config()["root_markers"])
    raise RuntimeError(
        f"raiz do repositório não localizada — nem a partir do código "
        f"({origem_arquivo}), nem do diretório de trabalho ({origem_cwd}) "
        f"há um diretório acima que contenha {marcas} "
        f"(a home, {_home()}, é excluída por construção). "
        f"Num projeto novo, rode `dc.py bootstrap` no diretório do projeto."
    )


def plan_root() -> Path:
    """Onde vivem planos, unidades e normativa — caminho resolvido pelo config."""
    return (repo_root() / config()["plan_root"]).resolve()


def planos_md() -> Path:
    """`_planos.md` — tabela dos planos aprovados, fonte da numeração."""
    return (plan_root() / "_planos.md").resolve()


def inbox() -> Path:
    """`_inbox/` — planos aguardando revisão e aprovação."""
    return (plan_root() / "_inbox").resolve()


def core_dir(core: str) -> Path:
    """Diretório de um core sob `docs/plan/` — o nome vem do frontmatter do plano."""
    if not core.strip():
        raise ValueError("nome de core vazio")
    if "/" in core or "\\" in core:
        raise ValueError(
            f"nome de core não pode conter separador de caminho — {core!r}"
        )
    return (plan_root() / core).resolve()
