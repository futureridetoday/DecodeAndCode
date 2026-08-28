#!/usr/bin/env python3
"""Empacota o método num plugin instalável — unidade 0001-16.

`construir` lê sempre da árvore real (`lib.repo_root()`), nunca de um parâmetro de origem: o
plugin é o que este repositório produz de si mesmo, e origem configurável reabriria a pergunta
que a unidade fecha. `materializar` é a exceção — recebe a origem porque copia **uma** guideline
específica, não a árvore inteira.

Invariante 2 do `CLAUDE.md`: nada específico de projeto viaja no plugin. `construir` decide isso
por **exclusão de caminho** (`scripts/tests/`, `__pycache__`, `docs/`, `guardrails.json` — nenhum
dos quatro é fonte copiada); `verificar` decide por **busca de conteúdo** na árvore já construída —
o par que fecha o invariante nos dois sentidos.

`${CLAUDE_PLUGIN_ROOT}` é o que separa pacote de cópia: `hooks/hooks.json` reescreve a âncora
`${CLAUDE_PROJECT_DIR}/.claude/hooks` do `settings.json` para `${CLAUDE_PLUGIN_ROOT}/hooks`.
"""

from __future__ import annotations

import json
import re
import shutil
import subprocess
from pathlib import Path

import lib

_ANCORA_PROJETO = "${CLAUDE_PROJECT_DIR}/.claude/hooks"
_ANCORA_PLUGIN = "${CLAUDE_PLUGIN_ROOT}/hooks"

_PROJECT_RE = re.compile(r"(?m)^project:.*$")

_DESTINO_DEFAULT = "dist/decode-and-code"


def _resolver_destino(destino: Path | str) -> Path:
    """Relativo resolve contra a raiz do repositório; absoluto passa direto."""
    destino = Path(destino)
    return destino if destino.is_absolute() else (lib.repo_root() / destino)


def _fontes() -> dict[str, Path]:
    raiz = lib.repo_root()
    return {
        "manifesto": raiz / ".claude-plugin" / "plugin.json",
        "skill": raiz / ".claude" / "skills" / "decode-and-code",
        "hooks": raiz / ".claude" / "hooks",
        "settings": raiz / ".claude" / "settings.json",
        "agents": raiz / ".claude" / "agents",
        "norma": raiz / "docs" / "plan" / "system" / "modelo-dev-units.md",
    }


def construir(destino: Path | str = _DESTINO_DEFAULT) -> list[Path]:
    """Constrói a árvore do plugin em `destino`, sempre do zero. Devolve os caminhos escritos.

    Levanta `FileNotFoundError` nomeando a fonte ausente antes de escrever qualquer coisa —
    checagem completa primeiro, escrita depois.
    """
    destino = _resolver_destino(destino)
    fontes = _fontes()
    for nome, caminho in fontes.items():
        if not caminho.exists():
            raise FileNotFoundError(f"fonte ausente para {nome!r}: {caminho}")

    if destino.exists():
        shutil.rmtree(destino)
    destino.mkdir(parents=True)

    nome_plugin = json.loads(fontes["manifesto"].read_text(encoding="utf-8"))["name"]

    escritos: list[Path] = [_copiar_manifesto(fontes["manifesto"], destino)]
    escritos.extend(_copiar_skill(fontes["skill"], destino, nome_plugin))
    escritos.append(_copiar_norma(fontes["norma"], destino, nome_plugin))
    escritos.extend(_copiar_hooks(fontes["hooks"], destino))
    escritos.append(_escrever_hooks_json(fontes["settings"], destino))
    escritos.extend(_copiar_agentes(fontes["agents"], destino))
    return escritos


def _copiar_manifesto(origem: Path, destino: Path) -> Path:
    alvo = destino / ".claude-plugin" / "plugin.json"
    alvo.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(origem, alvo)
    return alvo


def _copiar_skill(origem: Path, destino: Path, nome_plugin: str) -> list[Path]:
    """Copia a skill inteira, exceto `scripts/tests/`, `__pycache__` e `.DS_Store`.

    `.DS_Store` entrou por medição, não por antecipação (`L-32`): a reconciliação da `0001-17`
    acusou um dentro da pasta da skill, e o pacote o levava — lixo do Finder da máquina que
    construiu. `verificar` não o pegava, porque não há nome de projeto dentro de um `.DS_Store`.
    A exclusão vive **só aqui**: ensinar `verificar` a recusar lixo criaria duas listas do mesmo
    fato (invariante 1). Lixo novo entra nesta lista quando for observado, nunca antes.
    """
    alvo = destino / "skills" / "decode-and-code"
    shutil.copytree(
        origem, alvo, ignore=shutil.ignore_patterns("__pycache__", "tests", ".DS_Store")
    )
    _declarar_o_plugin(alvo / "SKILL.md", nome_plugin)
    return [p for p in sorted(alvo.rglob("*")) if p.is_file()]


def _declarar_o_plugin(skill_md: Path, nome_plugin: str) -> None:
    """`project:` do frontmatter passa a declarar o **plugin**, não o repositório que o produziu.

    A fonte continua declarando o repositório que a produziu, que é o correto para um artefato
    deste projeto (padrão de frontmatter, `CLAUDE.md` global). O que não pode é a cópia distribuída
    chegar em outro projeto declarando o nosso — é o defeito que o `huddle.md` teve, e a reescrita
    aqui é a mesma classe da âncora de hook: derivado se corrige no build, fonte permanece honesta.
    """
    texto = skill_md.read_text(encoding="utf-8")
    skill_md.write_text(_PROJECT_RE.sub(f"project: {nome_plugin}", texto, count=1), encoding="utf-8")


def _copiar_norma(origem: Path, destino: Path, nome_plugin: str) -> Path:
    """Leva a norma-mecanismo para `reference/`, ao lado da skill — unidade `0004-04`.

    `bootstrap.iniciar` materializa de lá quando o método roda de um pacote instalado (a skill já
    cita `<plan_root>/system/modelo-dev-units.md`, e sem isto o projeto que instala não tem a fonte
    que os três modos citam — `L-31` do plano `0001`). Fica fora de `docs/`, que `construir` nunca
    copia (invariante 2): é **um** arquivo nomeado, o operativo que a `0004-03` já separou do
    registro deste projeto, não a árvore inteira de `docs/plan`.

    `project:` do frontmatter passa pela mesma reescrita que `SKILL.md` já recebe
    (`_declarar_o_plugin`) — sem ela, a cópia distribuída declara no próprio frontmatter o nome do
    repositório que a produziu, e `verificar` acusa: a mesma classe de vazamento da `L-31`, medida
    nesta unidade num arquivo que ainda não existia quando aquela lacuna foi escrita.
    """
    alvo = destino / "skills" / "decode-and-code" / "reference" / origem.name
    alvo.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(origem, alvo)
    _declarar_o_plugin(alvo, nome_plugin)
    return alvo


def _copiar_hooks(origem: Path, destino: Path) -> list[Path]:
    alvo = destino / "hooks"
    alvo.mkdir(parents=True, exist_ok=True)
    escritos = []
    for hook in sorted(origem.glob("*.py")):
        copia = alvo / hook.name
        shutil.copy2(hook, copia)
        escritos.append(copia)
    return escritos


def _copiar_agentes(origem: Path, destino: Path) -> list[Path]:
    """Copia `.claude/agents/*.md` para `agents/` do pacote — mesmo formato de `_copiar_hooks` (`D-27`)."""
    alvo = destino / "agents"
    alvo.mkdir(parents=True, exist_ok=True)
    escritos = []
    for agente in sorted(origem.glob("*.md")):
        copia = alvo / agente.name
        shutil.copy2(agente, copia)
        escritos.append(copia)
    return escritos


def _escrever_hooks_json(settings: Path, destino: Path) -> Path:
    """Gera `hooks/hooks.json` a partir do bloco `hooks` de `settings.json`, âncora trocada."""
    dados = json.loads(settings.read_text(encoding="utf-8"))
    bloco = {"hooks": dados.get("hooks", {})}
    texto = json.dumps(bloco, ensure_ascii=False, indent=2).replace(_ANCORA_PROJETO, _ANCORA_PLUGIN)

    alvo = destino / "hooks" / "hooks.json"
    alvo.parent.mkdir(parents=True, exist_ok=True)
    alvo.write_text(texto + "\n", encoding="utf-8")
    return alvo


def _marcadores_instancia() -> tuple[str, ...]:
    """O nome do repositório que produziu o pacote — lido de `lib.repo_root()`, nunca hardcoded.

    **A lista tinha quatro marcadores e três eram falso positivo** (`L-31`, medido em 2026-08-26
    construindo do repositório real): `guardrails.json` acusava `guardrail.py` e o hook, que
    **precisam** nomear o arquivo que leem; `docs/plan` acusava o default de `lib.py` e do
    `config.json`, que é justamente a configurabilidade que a `0001-01` entregou; e
    `CLAUDE_PROJECT_DIR` acusava a constante `_ANCORA_PROJETO` deste módulo — o verificador
    reprovando o código que faz a substituição.

    Sobra o que é instância por definição: **nome de projeto**. Nome de arquivo que o mecanismo lê
    e caminho default que o mecanismo resolve são mecanismo, não instância.
    """
    return (lib.repo_root().name,)


def _ancora_de_projeto(destino: Path) -> list[str]:
    """`${CLAUDE_PROJECT_DIR}` dentro de `hooks/` — onde a âncora errada quebra de verdade.

    Fora de `hooks/` a string é dado (a constante que orienta a troca); dentro dela é um hook que
    vai procurar o próprio código na árvore de quem instalou. É o mesmo erro de quadro de
    referência da `L-24`: ancorar a busca onde ela significa alguma coisa, nunca no texto inteiro.
    """
    pasta = destino / "hooks"
    problemas = []
    for arquivo in sorted(pasta.rglob("*")) if pasta.is_dir() else []:
        if arquivo.is_file() and "CLAUDE_PROJECT_DIR" in _texto(arquivo):
            problemas.append(f"{arquivo.relative_to(destino)}: âncora 'CLAUDE_PROJECT_DIR' em hooks/")
    return problemas


def _texto(arquivo: Path) -> str:
    """Conteúdo textual, ou vazio quando o arquivo é binário — nunca levanta."""
    try:
        return arquivo.read_text(encoding="utf-8")
    except (UnicodeDecodeError, ValueError):
        return ""


def verificar(destino: Path | str = _DESTINO_DEFAULT) -> list[str]:
    """Percorre `destino` e devolve um problema por ocorrência de instância do projeto de origem.

    Lista vazia quando o pacote está limpo — mesmo padrão de `lint_*`.
    """
    destino = _resolver_destino(destino)
    marcadores = _marcadores_instancia()

    problemas = []
    for arquivo in sorted(destino.rglob("*")):
        if not arquivo.is_file():
            continue
        texto = _texto(arquivo)
        for marcador in marcadores:
            if marcador in texto:
                problemas.append(f"{arquivo.relative_to(destino)}: ocorrência de {marcador!r}")
    problemas.extend(_ancora_de_projeto(destino))
    return problemas


def validar(destino: Path | str = _DESTINO_DEFAULT) -> list[str]:
    """`claude plugin validate` sobre o pacote — lista de problemas, vazia quando aprova.

    **Par de `verificar`, e mede outra coisa.** `verificar` recusa instância do projeto de origem;
    este confere a **estrutura** contra a ferramenta oficial, que conhece o formato do manifesto e
    dos componentes. Ter só o nosso era conhecer só metade.

    Caracterizado contra o binário real em 2026-08-27, antes de escrito (`scripts.md`, *Comando
    externo*): o sinal é o **returncode** — `0` aprova, `1` reprova —, a mensagem sai inteira em
    `stdout`, e `stderr` fica vazio nos três casos medidos (pacote válido, diretório sem manifesto,
    caminho inexistente).

    Binário ausente **não levanta**: devolve o problema dizendo isso. Quem instala o método pode
    não ter o `claude` no `PATH`, e um gate que estoura nessa condição vira gate que se desliga.
    """
    destino = _resolver_destino(destino)
    try:
        resultado = subprocess.run(
            ["claude", "plugin", "validate", str(destino)], capture_output=True
        )
    except FileNotFoundError:
        return ["claude não encontrado no PATH — validação oficial não executada"]

    if resultado.returncode == 0:
        return []
    saida = resultado.stdout.decode("utf-8", errors="replace").strip()
    return [f"claude plugin validate reprovou: {saida}"]


def materializar(origem: Path, projeto: Path) -> Path:
    """Copia a guideline `origem` para `<projeto>/.claude/rules/`. Devolve o caminho escrito.

    Levanta `FileNotFoundError` se `origem` não existir, e `FileExistsError` se o destino já
    existir — nos dois casos, nada é escrito.
    """
    origem = Path(origem)
    if not origem.is_file():
        raise FileNotFoundError(f"origem ausente: {origem}")

    destino = Path(projeto) / ".claude" / "rules" / origem.name
    if destino.exists():
        raise FileExistsError(f"destino já existe — materializar não sobrescreve: {destino}")

    destino.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(origem, destino)
    return destino
