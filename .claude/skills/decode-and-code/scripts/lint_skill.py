#!/usr/bin/env python3
"""Lint de completude estrutural de um SKILL.md — unidade 0002-10.

Dá oráculo determinístico às cinco unidades da Fase 2 (11-15), que entregam
markdown, não código. Verifica só o que é objetivamente verificável: os 21
campos de frontmatter que as 11 skills do repositório já compartilham
(decisão D-02, não a tabela de recurso publicável do CLAUDE.md, que inclui
author_id e price), presença de modo pedido no corpo, e existência/permissão
dos caminhos citados. Não verifica se a skill funciona bem — distinção
deliberada.

`allowed-tools` não pode liberar `Bash` sem especificador (`P-14`): a skill pré-aprova o que lista
durante o turno, e `Bash` solto pré-aprova qualquer comando de shell — em todo projeto que instalar o
plugin. `Bash(*)` vale o mesmo que `Bash` solto e é recusado igual. Passa `Bash(<comando> *)`, que é o
que o `dc.py` pede.

O passo 6 ignora bloco de código e code span ao varrer link relativo — mesma
lição do scripts/move-md.py: documentação normativa cita caminho como
exemplo, e tratá-lo como link real produz falso positivo.
"""

from __future__ import annotations

import os
import re
from pathlib import Path

import regioes

# O conjunto presente em 11 de 11 skills do repositório (decisão D-02) — não
# a tabela de recurso publicável do CLAUDE.md, que inclui author_id e price
# e não é o que as skills reais declaram.
CAMPOS_FRONTMATTER = (
    "name",
    "description",
    "disable-model-invocation",
    "user-invocable",
    "allowed-tools",
    "effort",
    "context",
    "shell",
    "type",
    "project",
    "author",
    "created",
    "status",
    "version",
    "updated",
    "scope",
    "auto_load",
    "tags",
    "dependencies",
    "hub_id",
    "source",
)

# Interpretadores que dispensam bit de execução no script citado.
_INTERPRETES_RE = re.compile(r"\b(python3|python|bash|sh|zsh|node|npx)\b")

# Âncora que o Claude Code substitui, no corpo da skill, pelo diretório dela — no checkout e no
# plugin instalado (code.claude.com/docs/en/skills, *Available string substitutions*).
#
# Aceita `${CLAUDE_SKILL_DIR}/scripts/x.py` e `${CLAUDE_SKILL_DIR}/../<pasta>/scripts/x.py`: as três
# skills do método compartilham os scripts de uma pasta irmã, e a âncora com `..` resolve nela tanto
# no checkout quanto no pacote (`P-03` do plano `apply-plugin-review`). Um único `..`, para uma
# pasta irmã nomeada — não se aceita subir mais, nem `../..`.
#
# Aceita também `${CLAUDE_SKILL_DIR}/x.py`, direto na pasta da skill: é o atalho `dc.py` de cada skill
# (`P-14`), citado sem `..` porque a liberação de permissão casa o texto do comando.
_SKILL_DIR = "${CLAUDE_SKILL_DIR}"
_SCRIPT_RE = re.compile(
    re.escape(_SKILL_DIR) + r"/(?:(?:\.\./\w[\w.-]*/)?scripts/[^\s`)\"'<>]+|\w[\w-]*\.py)"
)

# `Bash` livre: o nome inteiro, sem `(` nem parte de outro nome — ou com o especificador `*` e mais nada,
# que casa qualquer comando e equivale a ele.
_BASH_LIVRE_RE = re.compile(r"(?<![\w(])Bash(?:(?![\w(])|\(\s*\*\s*\))")

# Abertura/fechamento de bloco de código — mesma marca do move-md.py.
_FENCE_RE = re.compile(r"^\s*(```|~~~)")

# [texto](destino) — mesma captura do move-md.py.
_LINK_RE = re.compile(r"(?<=\]\()([^)\s]+)(?=\))")


def lint(skill: Path, modos: list[str] | None = None) -> list[str]:
    """Verifica a completude estrutural de `skill` — lista vazia quando aprovada.

    Levanta `FileNotFoundError` se o arquivo não existe. Frontmatter ausente
    ou malformado entra na lista devolvida, não é exceção.
    """
    texto = skill.read_text(encoding="utf-8")
    corpo = _corpo(texto)

    problemas: list[str] = []
    problemas.extend(_checar_frontmatter(skill))
    problemas.extend(_checar_nome_e_descricao(skill))
    problemas.extend(_checar_bash_livre(skill))
    problemas.extend(_checar_modos(corpo, modos or []))
    problemas.extend(_checar_caminho_fixo(corpo))
    problemas.extend(_checar_scripts(skill, corpo))
    problemas.extend(_checar_links(skill, corpo))
    return problemas


def _corpo(texto: str) -> str:
    """Conteúdo após o frontmatter — o texto inteiro se não houver '---' de abertura."""
    linhas = texto.splitlines()
    if not linhas or linhas[0].strip() != "---":
        return texto
    for i in range(1, len(linhas)):
        if linhas[i].strip() == "---":
            return "\n".join(linhas[i + 1 :])
    return ""


def _checar_frontmatter(skill: Path) -> list[str]:
    """Exige a presença dos 21 campos — vazio ou não é o passo 2, não este."""
    try:
        valores = {chave: regioes.ler_campo(skill, chave) for chave in CAMPOS_FRONTMATTER}
    except ValueError:
        return ["frontmatter ausente ou malformado — sem '---' de abertura e fechamento"]

    return [
        f"campo obrigatório ausente no frontmatter: {chave}"
        for chave, valor in valores.items()
        if valor is None
    ]


def _checar_nome_e_descricao(skill: Path) -> list[str]:
    """`name` e `description` não vazios, e `name` igual ao diretório da skill."""
    try:
        nome = regioes.ler_campo(skill, "name")
        descricao = regioes.ler_campo(skill, "description")
    except ValueError:
        return []

    problemas = []
    if not (nome and nome.strip()):
        problemas.append("campo 'name' vazio")
    elif nome.strip() != skill.parent.name:
        problemas.append(
            f"'name' ({nome.strip()!r}) não corresponde ao diretório da skill ({skill.parent.name!r})"
        )

    if not (descricao and descricao.strip()):
        problemas.append("campo 'description' vazio")

    return problemas


def _texto_de_allowed_tools(skill: Path) -> str:
    """O que o frontmatter diz em `allowed-tools`, nos formatos string, lista em linha e lista em bloco.

    String e lista em linha (`[a, b]`) vêm na própria linha do campo; na lista em bloco a linha vem
    vazia e as ferramentas estão nos itens `- x` que a seguem. Vazio se o campo ou o frontmatter não
    existe — `_checar_frontmatter` é quem reclama disso.
    """
    linhas = skill.read_text(encoding="utf-8").splitlines()
    if not linhas or linhas[0].strip() != "---":
        return ""
    partes: list[str] = []
    em_lista = False
    for linha in linhas[1:]:
        if linha.strip() == "---":
            break
        if em_lista:
            if re.match(r"^\s+-\s", linha):
                partes.append(linha)
            elif linha.strip() and not linha.lstrip().startswith("#"):
                break
            continue
        m = re.match(r"^allowed-tools:\s*(.*)$", linha)
        if m:
            partes.append(m.group(1))
            em_lista = not m.group(1).strip()
    return "\n".join(partes)


def _checar_bash_livre(skill: Path) -> list[str]:
    """Recusa `Bash` sem especificador no `allowed-tools` — `P-14`.

    `Bash(...)` passa, com o comando que o especificador nomeia; só o nome solto e `Bash(*)` liberam
    tudo. O padrão exige que `Bash` não seja seguido de `(` nem de letra — salvo o `(*)` —, então
    `Bash(git *)` e `BashOutput` ficam de fora.
    """
    if _BASH_LIVRE_RE.search(_texto_de_allowed_tools(skill)):
        return [
            "allowed-tools libera 'Bash' sem especificador (ou só com '*') — qualquer comando de "
            "shell passaria sem pedir; use Bash(<comando> *)"
        ]
    return []


def _checar_modos(corpo: str, modos: list[str]) -> list[str]:
    """Cada modo pedido precisa aparecer citado em algum lugar do corpo."""
    return [f"modo não declarado no corpo: {modo}" for modo in modos if modo not in corpo]


def _checar_caminho_fixo(corpo: str) -> list[str]:
    """Recusa `.claude/skills/<qualquer nome>/` no corpo — `P-01` do plano `apply-plugin-review`.

    O caminho só existe no checkout que contém a skill. Instalada como plugin, ela mora no
    diretório do plugin, e o modelo que segue o caminho fixo não acha o script — medido em
    2026-10-15 com `claude --plugin-dir` num projeto vazio: `ls` sobre o caminho citado devolveu
    `No such file or directory`, e o mesmo citado por `${CLAUDE_SKILL_DIR}` resolveu.

    **Qualquer nome, não só o da própria skill** (`P-03`): com os scripts numa pasta irmã, o caminho
    fixo da irmã é a mesma armadilha — existe no checkout e some no plugin instalado. A irmã se cita
    por `${CLAUDE_SKILL_DIR}/../<pasta>/`.
    """
    padrao = re.compile(r"\.claude/skills/[^/\s`)\"'<>]+/[^\s`)\"'<>]*")
    return [
        f"caminho fixo não resolve no plugin instalado — use {_SKILL_DIR}/: {caminho}"
        for caminho in sorted(set(padrao.findall(corpo)))
    ]


def _caminhos_de_scripts(corpo: str) -> dict[str, list[str]]:
    """Caminhos citados sob `${CLAUDE_SKILL_DIR}/scripts/` ou `${CLAUDE_SKILL_DIR}/../<pasta>/scripts/`,
    com o texto que precede cada um na linha.

    Só conta a âncora `${CLAUDE_SKILL_DIR}` — é a única citação que resolve tanto no checkout
    quanto no plugin instalado. Uma citação nua como `scripts/x.py`, ou `./scripts/x.py`, é
    ambígua: pode ser de outro diretório de trabalho (o `cd hub` que precede
    `./scripts/new-migration.sh` em hub-env/SKILL.md aponta para `hub/scripts/`, não para o
    `scripts/` da própria skill nem o da raiz do repositório) e não é checável sem interpretar o
    shell ao redor.
    """
    encontrados: dict[str, list[str]] = {}
    for linha in corpo.split("\n"):
        for m in _SCRIPT_RE.finditer(linha):
            prefixo = linha[: m.start()]
            encontrados.setdefault(m.group(0), []).append(prefixo)
    return encontrados


def _checar_scripts(skill: Path, corpo: str) -> list[str]:
    """Existência em disco (passo 4) e bit de execução ou interpretador explícito (passo 5).

    Resolve contra o diretório da própria skill — o mesmo que `${CLAUDE_SKILL_DIR}` vira em sessão —,
    seguindo o `..` quando a citação aponta para a pasta irmã, e por isso vale igual para a fonte e
    para a cópia empacotada.
    """
    problemas: list[str] = []
    for caminho, prefixos in _caminhos_de_scripts(corpo).items():
        alvo = (skill.parent / caminho.removeprefix(_SKILL_DIR + "/")).resolve()
        if not alvo.is_file():
            problemas.append(f"script citado não existe: {caminho}")
            continue

        executavel = os.access(alvo, os.X_OK)
        interpretado = any(_INTERPRETES_RE.search(prefixo) for prefixo in prefixos)
        if not executavel and not interpretado:
            problemas.append(
                f"script sem bit de execução e sem interpretador explícito: {caminho}"
            )
    return problemas


def _links_do_corpo(corpo: str) -> list[str]:
    """Destinos de `[texto](destino)` fora de bloco de código e de code span.

    Mesma lógica do scripts/move-md.py: bloco delimitado por crase ou til
    tripla é pulado inteiro, e dentro de uma linha só os trechos de índice
    par (fora de crase simples) são varridos.
    """
    destinos: list[str] = []
    dentro_de_bloco = False
    for linha in corpo.split("\n"):
        if _FENCE_RE.match(linha):
            dentro_de_bloco = not dentro_de_bloco
            continue
        if dentro_de_bloco:
            continue
        partes = linha.split("`")
        for i in range(0, len(partes), 2):
            destinos.extend(_LINK_RE.findall(partes[i]))
    return destinos


def _e_relativo(destino: str) -> bool:
    """URL, âncora da própria página e caminho absoluto não dependem de onde a skill vive."""
    if not destino or destino.startswith(("#", "/", "http://", "https://", "mailto:")):
        return False
    return "://" not in destino


def _checar_links(skill: Path, corpo: str) -> list[str]:
    """Cada link relativo precisa resolver a partir do diretório da própria skill."""
    problemas = []
    for destino in _links_do_corpo(corpo):
        if not _e_relativo(destino):
            continue
        caminho = destino.split("#", 1)[0]
        alvo = (skill.parent / caminho).resolve()
        if not alvo.exists():
            problemas.append(f"link não resolve: {destino}")
    return problemas
