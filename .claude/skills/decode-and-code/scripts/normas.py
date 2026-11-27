#!/usr/bin/env python3
"""Conteúdo das normas que uma unidade cita — `L-08` do plano `apply-plugin-review`.

A tabela `## Normas aplicáveis` é referência, nunca cópia, e mandar o executor (hoje o `code`) abri-las não
bastou: medido, o subagent abriu 0 de 3 seções numa rodada e um `grep` de 23 linhas nas outras. A
instrução em markdown não estabiliza; o script entrega o trecho, e a skill só o roda.

`resolver` lê cada linha de dados da tabela e acha o que ela aponta. Três formas na coluna *Onde*
resolvem — as que as unidades reais usam —, e o resto vai para as não resolvidas, com o motivo:

- `[texto](caminho), seção *X*` — o `seção` é opcional (`[texto](caminho), *X*`);
- `[texto](caminho), seção de mesmo nome` — *X* é o texto da primeira coluna;
- `mesma seção …` — repete arquivo e seção da linha anterior, se ela resolveu.

A seção é o primeiro título, de qualquer nível, cujo texto **começa** com *X*. O `3. ` que a norma de antes do
redesign punha diante de alguns títulos não conta — as unidades citam *Camada normativa*, não *3. Camada
normativa*. O trecho vai do título até o próximo de nível igual ou maior, e os subtítulos entram.

Não chegam ao executor, e vão para as não resolvidas: linha sem link, link sem seção reconhecida
(`[texto](caminho)` solto, ou só o id de uma decisão, que é linha de tabela e não título), arquivo
ausente e seção inexistente. É ele que as relata como insuficiência da unidade. Quando o alvo
ausente está em `.claude/archive/` (plano 0020), o motivo passa a ser "arquivada em <data> por
<quem>: <motivo>", para o arquivamento não parecer link quebrado.

Reaproveita `lint_unidade._corpo` e `_secao`: o frontmatter fora, e `## Normas aplicáveis` lida do mesmo
jeito que o gate de entrada a lê. Título dentro de cerca de código não conta — documento de regras
exemplifica cabeçalhos em blocos de código, e um `###` de exemplo encerraria a seção antes da hora.
"""

from __future__ import annotations

import json
import os
import re
from pathlib import Path
from typing import NamedTuple

import lib
import lint_unidade
import regioes
import registry
import rules

_TITULO_RE = re.compile(r"^(#{1,6})\s+(.*?)\s*$")
_NUMERACAO_RE = re.compile(r"^\d+\.\s+")
_CERCA_RE = re.compile(r"^\s*(```|~~~)")
_SEPARADOR_RE = re.compile(r"^\|[\s:|-]+$")
_LINK_RE = re.compile(r"\[[^\]]*\]\(([^)\s]+)\)")
_SECAO_RE = re.compile(r",\s*(?:seção\s+(?P<igual>de mesmo nome)|(?:seção\s+)?\*(?P<nome>[^*]+)\*)")
_MESMA_SECAO_RE = re.compile(r"^mesma seção\b")


class Entrada(NamedTuple):
    """Uma linha resolvida: o arquivo (caminho resolvido), o título achado e o trecho dele."""

    arquivo: Path
    secao: str
    trecho: str


class NaoResolvida(NamedTuple):
    """Uma linha que não chegou ao conteúdo: o texto dela na tabela e o motivo."""

    linha: str
    motivo: str


def resolver(unidade: Path) -> tuple[list[Entrada], list[NaoResolvida]]:
    """Entradas resolvidas e não resolvidas da tabela de guidelines, na ordem dela.

    A tabela é `## Normas aplicáveis` no formato 1 e `## Guidelines` no formato 2
    (`lint_unidade.SECAO_DE_GUIDELINES`); as linhas têm a mesma forma nos dois.

    Levanta `FileNotFoundError` se `unidade` não existir (propagado de `Path.read_text`) e
    `ValueError` se ela não tem a seção. Uma linha ruim nunca levanta: entra nas não resolvidas.
    """
    unidade = Path(unidade).resolve()
    corpo = lint_unidade._corpo(unidade.read_text(encoding="utf-8"))
    nome = lint_unidade.SECAO_DE_GUIDELINES[lib.formato(unidade)]
    secao = lint_unidade._secao(corpo, nome)
    if secao is None:
        raise ValueError(f"{unidade} não tem a seção '## {nome}'")

    resolvidas: list[Entrada] = []
    nao_resolvidas: list[NaoResolvida] = []
    anterior: tuple[Path, str] | None = None  # alvo da linha anterior, se ela resolveu
    for linha in _linhas_de_dados(secao):
        alvo = _alvo(linha, unidade.parent, anterior)
        achado = _buscar(*alvo) if isinstance(alvo, tuple) else alvo
        if isinstance(achado, str) and isinstance(alvo, tuple):
            achado = _arquivada(*alvo) or achado
        if isinstance(achado, str):
            nao_resolvidas.append(NaoResolvida(linha, achado))
            anterior = None
        else:
            resolvidas.append(Entrada(alvo[0], *achado))
            anterior = alvo
    return resolvidas, nao_resolvidas


_CAMPOS_ARQUIVADO = ("archived_at", "archived_by", "reason")
_CAMPO_DE_SECAO_RE = r"(?m)^\*\*{}:\*\* (.+)$"


def _arquivada(arquivo: Path, nome: str) -> str | None:
    """Motivo "arquivada em <data> por <quem>: <motivo>" quando o alvo ausente está no arquivo.

    Plano 0020, tarefa 5. Só para o que vive em `.claude/rules/`: a contraparte é
    `.claude/archive/rules/<mesmo nome>`. Guideline arquivada é o arquivo inteiro, com os três campos
    no frontmatter; princípio arquivado é uma seção de `principles.md`, com os três campos em linhas
    `**campo:**`. None quando não há contraparte arquivada — o motivo de antes fica.
    """
    if arquivo.parent.name != "rules" or arquivo.parent.parent.name != ".claude":
        return None
    arquivado = arquivo.parent.parent / "archive" / "rules" / arquivo.name
    if not arquivado.is_file():
        return None

    if not arquivo.is_file() and registry._e_guideline(arquivado):
        try:
            campos = [json.loads(regioes.ler_campo(arquivado, c) or "null") for c in _CAMPOS_ARQUIVADO]
        except (ValueError, json.JSONDecodeError):
            return None
    else:
        achado = _buscar(arquivado, nome)
        if not isinstance(achado, tuple):
            return None
        casados = [re.search(_CAMPO_DE_SECAO_RE.format(c), achado[1]) for c in _CAMPOS_ARQUIVADO]
        campos = [m[1].strip() if m else None for m in casados]
    if not all(campos):
        return None
    data, autor, motivo = campos
    return f"arquivada em {data} por {autor}: {motivo}"


def _linhas_de_dados(secao: str) -> list[str]:
    """Linhas da tabela sem o cabeçalho (a primeira) nem o separador `|---|---|`."""
    tabela = [linha.strip() for linha in secao.splitlines() if linha.strip().startswith("|")]
    return [linha for linha in tabela[1:] if not _SEPARADOR_RE.match(linha)]


def _alvo(linha: str, base: Path, anterior: tuple[Path, str] | None) -> tuple[Path, str] | str:
    """`(arquivo, nome da seção)` que a linha cita — ou o motivo, `str`, de não haver como saber."""
    celulas = [celula.strip() for celula in linha.strip("|").split("|", 1)]
    onde = celulas[1] if len(celulas) > 1 else ""

    if _MESMA_SECAO_RE.match(onde):
        return anterior or "'mesma seção' sem linha anterior resolvida"
    link = _LINK_RE.search(onde)
    if link is None:
        return "sem link para o arquivo"
    secao = _SECAO_RE.match(onde, link.end())
    if secao is None:
        return "link sem seção reconhecida"
    nome = celulas[0].strip("*").strip() if secao["igual"] else secao["nome"].strip()
    return (base / link[1]).resolve(), nome


def _buscar(arquivo: Path, nome: str) -> tuple[str, str] | str:
    """`(título, trecho)` da primeira seção de `arquivo` que começa com `nome` — ou o motivo, `str`."""
    if not arquivo.is_file():
        return "arquivo ausente"
    linhas = lint_unidade._corpo(arquivo.read_text(encoding="utf-8")).splitlines()

    em_cerca = False
    inicio: int | None = None
    nivel = 0
    titulo = ""
    for i, linha in enumerate(linhas):
        if _CERCA_RE.match(linha):
            em_cerca = not em_cerca
            continue
        achado = None if em_cerca else _TITULO_RE.match(linha)
        if achado is None:
            continue
        if inicio is None:
            if _NUMERACAO_RE.sub("", achado[2]).startswith(nome):
                inicio, nivel, titulo = i, len(achado[1]), achado[2]
        elif len(achado[1]) <= nivel:
            return titulo, "\n".join(linhas[inicio:i]).rstrip()
    if inicio is None:
        return f"seção não encontrada: {nome}"
    return titulo, "\n".join(linhas[inicio:]).rstrip()


def secoes(arquivo: Path, nomes: tuple[str, ...]) -> list[tuple[str, str]]:
    """`(título, trecho)` de cada seção de `nomes`, na ordem dela — `ValueError` nomeando as que faltam."""
    achados = [_buscar(arquivo, nome) for nome in nomes]
    faltam = [nome for nome, achado in zip(nomes, achados) if not isinstance(achado, tuple)]
    if faltam:
        raise ValueError(f"seções ausentes em {arquivo}: {', '.join(faltam)}")
    return achados


def codex_dir() -> Path:
    """A pasta do codex, na pasta compartilhada das skills — a mesma no checkout e no pacote."""
    return Path(__file__).resolve().parent.parent / "codex"


def procedimentos_dir() -> Path:
    """A pasta dos procedimentos compartilhados entre skills, ao lado do codex e fora dele."""
    return Path(__file__).resolve().parent.parent / "procedures"


def pastas_do_codex() -> list[Path]:
    """O núcleo do codex e o capítulo de cada módulo presente (`lib.modulos`)."""
    import lib

    return [codex_dir()] + [m["path"] / "codex" for m in lib.modulos() if (m["path"] / "codex").is_dir()]


def secao_do_codex(titulo: str, pasta: Path | None = None) -> tuple[Path, str]:
    """`(arquivo, trecho)` da seção `## <titulo>` do codex — título exato, que no codex é único.

    O trecho vai do título até a próxima seção de mesmo nível. Levanta `ValueError` nomeando o
    título quando nenhum capítulo o tem: o codex nunca é copiado ao projeto (codex, *Restrição
    fundamental*), e quem lê é o pacote, então a falta é defeito do pacote, não do projeto.
    """
    pastas = [pasta] if pasta else pastas_do_codex()
    for capitulo in sorted(c for p in pastas for c in p.glob("*.md")):
        linhas = capitulo.read_text(encoding="utf-8").split("\n")
        for i, linha in enumerate(linhas):
            if linha.rstrip() == f"## {titulo}":
                fim = next(
                    (j for j in range(i + 1, len(linhas)) if linhas[j].startswith("## ")), len(linhas)
                )
                return capitulo, "\n".join(linhas[i:fim]).rstrip()
    raise ValueError(f"seção ausente no codex ({', '.join(map(str, pastas))}): {titulo}")


class Aplicavel(NamedTuple):
    """Uma guideline cujo `paths:` casa um arquivo da unidade: a linha pronta, ou o aviso de por que não."""

    nome: str
    linha: str
    aviso: str


def aplicaveis(unidade: Path, raiz: Path) -> list[Aplicavel]:
    """Guidelines de `<raiz>/.claude/rules/` que valem para os arquivos da tabela *Arquivos* da unidade.

    Plano 0017, `L-03` da revisão. Os caminhos são os entre crases com `/` — os mesmos que o gate de
    entrada exige —, sem o `:linha` do fim, e casam como texto (`rules.casa_caminho`), porque o
    arquivo pode ainda não existir. Padrão fora do subconjunto que o `criar-guideline` grava não
    entra no casamento; a guideline que só tem padrões assim volta com `aviso`. Para a que casa, a
    `linha` é a de *Normas aplicáveis*, com o link relativo à unidade e o primeiro título do corpo
    como seção; sem título, volta com `aviso`, porque a citação não resolveria.
    """
    secao = lint_unidade._secao(lint_unidade._corpo(unidade.read_text(encoding="utf-8")), "Arquivos") or ""
    caminhos = [re.sub(r":\d+$", "", c.strip("`").removeprefix("./")) for c in lint_unidade._CAMINHO_RE.findall(secao)]

    dir_rules = raiz / ".claude" / "rules"
    achadas: list[Aplicavel] = []
    for regra in sorted(dir_rules.glob("*.md")) if dir_rules.is_dir() else []:
        if not registry._e_guideline(regra):
            continue
        padroes = rules._entradas_de_paths(regioes.ler_campo(regra, "paths") or "") or []
        validos = [p for p in padroes if rules._problema_de_padrao(p) is None]
        if not validos:
            if padroes:
                achadas.append(Aplicavel(regra.stem, "", f"nenhum padrão no subconjunto do criar-guideline: {padroes!r}"))
            continue
        if not any(rules.casa_caminho(p, c) for p in validos for c in caminhos):
            continue
        titulo = next(
            (m[2] for m in map(_TITULO_RE.match, lint_unidade._corpo(regra.read_text(encoding="utf-8")).splitlines()) if m),
            None,
        )
        if titulo is None:
            achadas.append(Aplicavel(regra.stem, "", "a guideline não tem título para a citação resolver"))
            continue
        link = Path(os.path.relpath(regra.resolve(), unidade.resolve().parent)).as_posix()
        achadas.append(Aplicavel(regra.stem, f"| {titulo} | [{regra.stem}]({link}), seção *{titulo}* |", ""))
    return achadas
