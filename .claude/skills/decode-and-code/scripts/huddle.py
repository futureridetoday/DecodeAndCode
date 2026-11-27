#!/usr/bin/env python3
"""Oráculo do huddle — fila do que ainda não foi decidido — unidade 0001-21.

Três funções, três papéis. `lint_arquivo` prova o invariante de despejo — o mesmo `H-XX` não pode
estar aberto e fechado ao mesmo tempo — e o vocabulário fechado de cinco tipos no cabeçalho de cada
entrada. `lint_relatorio` prova que o relatório de um dos três modos declara quantas entradas novas
houve, mesmo quando são zero (`L-08`) — é o que separa *conferi e não havia* de *nunca conferi*.
`iniciar` escreve o esqueleto vazio que quem instala o mecanismo recebe.

Os dois `lint_*` só leem, e devolvem lista vazia quando sãs — mesmo padrão de `lint_unidade.lint` e
`empacotar.verificar`. `iniciar` escreve **um** arquivo, e nunca sobre um existente: o `huddle.md`
de cada projeto é instância pura e não viaja no plugin — o mecanismo que cria um vazio, sim (`D-28`).

Não há arquivo de template (`D-20`): o esqueleto vive em `_CONTEUDO_INICIAL`, como
`porte._CONTEUDO_INICIAL` já faz para a tabela de porte — formato com uma fonte só, que é o
script, com o codex (*Huddle*) dizendo o que ele é.

O esqueleto de antes do redesign citava a norma e levava a tag `pre-norma`; `ESQUELETO_ANTERIOR`
guarda os trechos que mudaram, para a migração dos projetos (parte 2.4) os reconhecer e trocar.
"""

from __future__ import annotations

import re
import subprocess
import unicodedata
from datetime import date
from pathlib import Path

import lib
import regioes


def usuario(projeto: Path) -> str:
    """Identidade de quem está na sessão: `git config user.name` do projeto em kebab-case ASCII.

    É o nome do arquivo de huddle da pessoa (plano 0008, `D-02`). Levanta `ValueError` com o
    comando para configurar o nome quando ele falta, ou quando não sobra letra ASCII nenhuma.
    Duas pessoas com o mesmo nome compartilham arquivo (`L-06`).
    """
    saida = subprocess.run(
        ["git", "config", "user.name"], cwd=projeto, capture_output=True, text=True
    ).stdout.strip()
    ascii_ = unicodedata.normalize("NFKD", saida).encode("ascii", "ignore").decode("ascii")
    slug = re.sub(r"[^a-z0-9]+", "-", ascii_.lower()).strip("-")
    if not slug:
        motivo = "sem 'user.name' no git" if not saida else f"'user.name' sem letra ASCII: {saida!r}"
        raise ValueError(
            f"huddle: {motivo} — configure com: git config user.name \"Seu Nome\""
        )
    return slug


def caminho(projeto: Path, usuario: str) -> Path:
    """Arquivo de huddle da pessoa: `<projeto>/<plan_root>/system/huddle/<usuario>.md`."""
    return Path(projeto) / lib.config()["plan_root"] / "system" / "huddle" / f"{usuario}.md"

# Vocabulário fechado — mesmo padrão de `unit_type` e `plan_size`: recusa-se o valor que não é
# escolha nenhuma, nunca a escolha.
TIPOS = ("pergunta", "divergência", "padrão", "revisitar", "observação")

# Evidência — plano 0019, `D-07`: opcional, prefixo de um vocabulário fechado de cinco, as origens
# da `D-09` do `0018`; depois do prefixo, texto livre. Fica numa linha no fim do corpo da entrada.
EVIDENCIAS = ("E-XX", "L-XX", "bloqueio:", "gate:", "revisão:")
_EVIDENCIA_RE = re.compile(r"^(?:[EL]-\d+\b.*|(?:bloqueio|gate|revisão):[ \t]*\S.*)$")
_LINHA_EVIDENCIA_RE = re.compile(r"(?m)^Evidência:[ \t]*(.*?)[ \t]*$")

_SECAO_RE = r"(?ms)^##\s+{}\s*$\n(.*?)(?=^##\s+|\Z)"
_CABECALHO_ENTRADA_RE = re.compile(
    r"(?m)^###\s+(H-\d+)\s*·\s*`([^`]*)`\s*·\s*\d{4}-\d{2}-\d{2}\s*·\s*.+$"
)
_LINHA_FECHADAS_RE = re.compile(r"(?m)^\|\s*(H-\d+)\s*\|")
_ENTRADA_RE = re.compile(
    r"(?ms)^###\s+(H-\d+)\s*·\s*`([^`]*)`\s*·\s*(\d{4}-\d{2}-\d{2})\s*·\s*(.+?)\s*$\n(.*?)(?=^###\s+|\Z)"
)


def evidencia_valida(valor: str) -> bool:
    """`valor` começa por um dos cinco prefixos de `EVIDENCIAS` e cabe numa linha (`D-07`)."""
    return "\n" not in valor and bool(_EVIDENCIA_RE.match(valor.strip()))


def _entradas(abertas: str) -> list[dict]:
    """Cada entrada de `## Abertas`: `{"id", "tipo", "data", "autor", "texto", "evidencia"}`.

    `evidencia` é o valor da última linha `Evidência:` do corpo, ou `""`; `texto` é o corpo inteiro.
    """
    lidas = []
    for m in _ENTRADA_RE.finditer(abertas):
        corpo = m.group(5).strip()
        linhas = _LINHA_EVIDENCIA_RE.findall(corpo)
        lidas.append({"id": m.group(1), "tipo": m.group(2), "data": m.group(3), "autor": m.group(4),
                      "texto": corpo, "evidencia": linhas[-1] if linhas else ""})
    return lidas


def _secao(texto: str, nome: str) -> str | None:
    """Conteúdo de `## nome` até o próximo `## ` ou o fim do texto — `None` se ausente."""
    padrao = re.compile(_SECAO_RE.format(re.escape(nome)))
    m = padrao.search(texto)
    return m.group(1) if m else None


def lint_arquivo(caminho: Path) -> list[str]:
    """Verifica `caminho` contra os invariantes do huddle — lista vazia quando são.

    Três coisas: cabeçalho de entrada bem formado (inclui o tipo dentro do vocabulário fechado),
    `H-XX` único dentro de `## Abertas`, e nenhum `H-XX` presente nas duas seções ao mesmo tempo —
    a regra de despejo.

    Levanta `FileNotFoundError` se `caminho` não existir (propagado de `Path.read_text`).
    Estrutura quebrada — seção ausente — entra na lista devolvida, nunca como exceção.
    """
    texto = Path(caminho).read_text(encoding="utf-8")

    abertas = _secao(texto, "Abertas")
    fechadas = _secao(texto, "Fechadas")

    problemas: list[str] = []
    if abertas is None:
        problemas.append("seção '## Abertas' ausente")
    if fechadas is None:
        problemas.append("seção '## Fechadas' ausente")
    if abertas is None or fechadas is None:
        return problemas

    problemas.extend(_checar_reminder_days(Path(caminho)))

    ids_fechadas = set(_LINHA_FECHADAS_RE.findall(fechadas))

    vistos: set[str] = set()
    for h_id, tipo in _CABECALHO_ENTRADA_RE.findall(abertas):
        if tipo not in TIPOS:
            problemas.append(f"{h_id}: tipo fora do vocabulário fechado {TIPOS} — {tipo!r}")
        if h_id in vistos:
            problemas.append(f"{h_id}: repetido em '## Abertas'")
        vistos.add(h_id)
        if h_id in ids_fechadas:
            problemas.append(
                f"{h_id}: presente em '## Abertas' e na tabela de '## Fechadas' — despejo violado"
            )

    for entrada in _entradas(abertas):
        for valor in _LINHA_EVIDENCIA_RE.findall(entrada["texto"]):
            if not evidencia_valida(valor):
                problemas.append(f"{entrada['id']}: evidência fora do vocabulário fechado {EVIDENCIAS} — {valor!r}")

    return problemas


def _checar_reminder_days(caminho: Path) -> list[str]:
    """`reminder_days`, quando presente, é inteiro maior ou igual a zero (plano 0008, `D-03`)."""
    try:
        valor = regioes.ler_campo(caminho, "reminder_days")
    except ValueError:
        return []  # sem frontmatter — o arquivo de antes do 0008 não tem o campo
    if valor is None or re.fullmatch(r"\d+", valor.strip()):
        return []
    return [f"reminder_days precisa ser inteiro maior ou igual a zero — {valor!r}"]


_LINHA_FECHO_COM_IDS_RE = re.compile(
    r"entradas novas no huddle:\s*(\d+)(?:\s*\(([^)]*)\))?"
)


def lint_relatorio(texto: str, arquivo: Path | None = None) -> list[str]:
    """Recusa a ausência da linha de fecho `entradas novas no huddle: N` — presente mesmo com
    `N` igual a zero (`L-08`): é o que separa *conferi e não havia* de *nunca conferi*.

    Com `arquivo` (plano 0008, T3), a linha também precisa listar os ids quando `N > 0` —
    `entradas novas no huddle: 2 (H-12, H-13)` —, `N` igual à quantidade de ids, e cada id em
    `## Abertas` de `arquivo` com a data de hoje no cabeçalho, para entrada antiga não passar como
    nova. Vale a última linha de fecho do texto.
    """
    linhas = list(_LINHA_FECHO_COM_IDS_RE.finditer(texto))
    if not linhas:
        return ["relatório sem a linha de fecho 'entradas novas no huddle: N' — obrigatória mesmo com N=0"]
    if arquivo is None:
        return []

    m = linhas[-1]
    n = int(m.group(1))
    ids = [i.strip() for i in (m.group(2) or "").split(",") if i.strip()]
    problemas: list[str] = []
    if n != len(ids):
        problemas.append(
            f"a linha de fecho declara {n} entrada(s) e lista {len(ids)} id(s) — "
            "exemplo: 'entradas novas no huddle: 2 (H-12, H-13)'"
        )

    # Sem o arquivo da pessoa, nenhuma entrada está aberta: N > 0 reprova, zero passa.
    abertas = (_secao(Path(arquivo).read_text(encoding="utf-8"), "Abertas") or "") if Path(arquivo).exists() else ""
    hoje = date.today().isoformat()
    datas = {
        h: d
        for h, d in re.findall(r"(?m)^###\s+(H-\d+)\s*·\s*`[^`]*`\s*·\s*(\d{4}-\d{2}-\d{2})", abertas)
    }
    for h_id in ids:
        if h_id not in datas:
            problemas.append(f"{h_id}: não está em '## Abertas' de {arquivo}")
        elif datas[h_id] != hoje:
            problemas.append(f"{h_id}: aberta em {datas[h_id]}, não hoje — entrada antiga não é nova")
    return problemas


_CONTEUDO_INICIAL = """\
---
# about
name: huddle
type: doc
project: {projeto}
description: Fila do que ainda não foi decidido — pauta da conversa recorrente entre a pessoa e Claude. Nada aqui é regra; entrada resolvida sai daqui e vai para o lugar certo
tags: [huddle, decode-and-code, pauta]

# history
author: ""
created: {criado}
status: draft
version: 0.1.0
updated: ""

{campos_da_pessoa}
# system
scope: project
auto_load: false
dependencies: []
---

# Huddle

**Nada aqui é regra.** Entrada aberta é coisa que espera decisão. Quando resolve, **sai** — para uma
decisão de plano, para o rethink ou um plano `rule`, que gravam princípio, guideline e guardrail, para
o feedback ao método, ou para o descarte com motivo — e deixa uma linha em `## Fechadas` com a data e
o destino.

O que o huddle é e quando se registra: o codex, seção *Huddle* (`dc.py codex Huddle`).

## Abertas

## Fechadas

| # | Tipo | Fechada em | Destino |
|---|---|---|---|
"""


# Os trechos do esqueleto anterior ao redesign que mudaram, na forma exata em que foram gravados, e
# o texto que os substitui (2.4). A ordem importa: a migração troca um par por vez.
ESQUELETO_ANTERIOR = (
    (
        "Nada aqui é norma; entrada resolvida sai daqui e vai para o lugar de coisa resolvida",
        "Nada aqui é regra; entrada resolvida sai daqui e vai para o lugar certo",
    ),
    ("tags: [huddle, decode-and-code, pre-norma, pauta]", "tags: [huddle, decode-and-code, pauta]"),
    (
        "**Nada aqui é autoritativo.** Entrada aberta é coisa que espera decisão, não regra a seguir. Quando\n"
        "resolve, **sai** — para a norma, para uma guideline, ou para o `## Decisões` de um plano — e deixa\n"
        "uma linha em `## Fechadas` com a data e o destino.\n\n"
        "Formato, tipos, gatilhos e a regra de despejo: `<plan_root>/system/modelo-dev-units.md`, seção\n"
        "*Huddle*. Aqui não se duplica a norma; aqui se usa.\n",
        "**Nada aqui é regra.** Entrada aberta é coisa que espera decisão. Quando resolve, **sai** — para uma\n"
        "decisão de plano, para o rethink ou um plano `rule`, que gravam princípio, guideline e guardrail, para\n"
        "o feedback ao método, ou para o descarte com motivo — e deixa uma linha em `## Fechadas` com a data e\n"
        "o destino.\n\n"
        "O que o huddle é e quando se registra: o codex, seção *Huddle* (`dc.py codex Huddle`).\n",
    ),
)


def _campos_da_pessoa(owner: str) -> str:
    """Bloco do frontmatter que é do mecanismo por pessoa (plano 0008) — `iniciar` e `migrar`."""
    return f'# huddle\nowner: {owner}\nlast_huddle: ""\nreminder_days: 7\n'


def iniciar(destino: Path, projeto: Path | None = None, usuario: str | None = None) -> Path | None:
    """Escreve o esqueleto vazio em `destino` — devolve o caminho, ou `None` se já existir.

    Nunca sobrescreve: quem chama de novo sobre o mesmo `destino` não perde entrada nenhuma —
    `iniciar` só cria, nunca reescreve. `project` do frontmatter vem de `projeto.name` ou, sem
    `projeto`, de `lib.repo_root().name` — nunca hardcoded, para que o mecanismo, instalado noutro
    projeto, declare o projeto certo (invariante 2 do `CLAUDE.md`). `owner` é `usuario`, ou vazio.
    """
    destino = Path(destino)
    if destino.exists():
        return None

    nome_projeto = Path(projeto).name if projeto is not None else lib.repo_root().name
    destino.parent.mkdir(parents=True, exist_ok=True)
    destino.write_text(
        _CONTEUDO_INICIAL.format(
            projeto=nome_projeto,
            criado=date.today().isoformat(),
            campos_da_pessoa=_campos_da_pessoa(usuario or '""'),
        ),
        encoding="utf-8",
    )
    return destino


def _arquivo_unico(arquivo: Path) -> Path:
    """O huddle de projeto de antes do 0008: `<plan_root>/system/huddle.md`, irmão de `huddle/`."""
    return Path(arquivo).parent.parent / "huddle.md"


def _projeto_do_arquivo(arquivo: Path) -> Path:
    """`<projeto>` a partir de `<projeto>/<plan_root>/system/huddle/<usuario>.md`."""
    return Path(arquivo).parents[2 + len(Path(lib.config()["plan_root"]).parts)]


def _ids(texto: str) -> list[int]:
    abertas = _secao(texto, "Abertas") or ""
    fechadas = _secao(texto, "Fechadas") or ""
    ids = [h for h, _ in _CABECALHO_ENTRADA_RE.findall(abertas)] + _LINHA_FECHADAS_RE.findall(fechadas)
    return [int(h.split("-")[1]) for h in ids]


def _fim_da_secao(texto: str, nome: str) -> int:
    """Índice no texto onde termina o conteúdo de `## nome` — antes do próximo `## ` ou no fim."""
    m = re.compile(_SECAO_RE.format(re.escape(nome))).search(texto)
    if m is None:
        raise ValueError(f"seção '## {nome}' ausente")
    return m.end(1)


def abrir(arquivo: Path, tipo: str, texto: str, autor: str, evidencia: str | None = None) -> str:
    """Acrescenta uma entrada no fim de `## Abertas` e devolve o `H-XX` dela.

    Próximo id = maior `H-XX` de `## Abertas` e `## Fechadas` + 1; data de hoje. Cria o arquivo por
    `iniciar` se faltar. Com `evidencia`, o corpo termina numa linha `Evidência: <origem>` — no fim,
    para a pauta seguir mostrando a primeira linha do texto (plano 0019, `D-07`). Recusa com
    `ValueError`, sem escrever, tipo fora de `TIPOS`, evidência fora de `EVIDENCIAS` ou enquanto
    existir o arquivo único de projeto — o primeiro registro partiria o huddle em dois.
    """
    arquivo = Path(arquivo)
    if tipo not in TIPOS:
        raise ValueError(f"tipo fora do vocabulário fechado {TIPOS}: {tipo!r}")
    if evidencia is not None and not evidencia_valida(evidencia):
        raise ValueError(f"evidência fora do vocabulário fechado {EVIDENCIAS}: {evidencia!r}")
    if _arquivo_unico(arquivo).exists():
        raise ValueError(
            f"{_arquivo_unico(arquivo)} ainda existe — rode `dc.py huddle-migrar` antes de registrar"
        )
    if not arquivo.exists():
        iniciar(arquivo, projeto=_projeto_do_arquivo(arquivo), usuario=arquivo.stem)

    atual = arquivo.read_text(encoding="utf-8")
    h_id = f"H-{max(_ids(atual), default=0) + 1:02d}"
    corpo = texto.strip() + (f"\n\nEvidência: {evidencia.strip()}" if evidencia is not None else "")
    entrada = f"### {h_id} · `{tipo}` · {date.today().isoformat()} · {autor}\n\n{corpo}\n\n"
    fim = _fim_da_secao(atual, "Abertas")
    antes = atual[:fim]
    if not antes.endswith("\n\n"):
        antes = antes.rstrip("\n") + "\n\n"
    arquivo.write_text(antes + entrada + atual[fim:], encoding="utf-8")
    return h_id


def entrada(arquivo: Path, h_id: str) -> dict:
    """A entrada aberta `h_id`, como em `_entradas` — `ValueError` se ela não está aberta."""
    abertas = _secao(Path(arquivo).read_text(encoding="utf-8"), "Abertas") or ""
    for lida in _entradas(abertas):
        if lida["id"] == h_id:
            return lida
    raise ValueError(f"{h_id} não está em '## Abertas'")


def fechar(arquivo: Path, h_id: str, destino: str) -> None:
    """Tira `h_id` de `## Abertas` e acrescenta a linha no fim da tabela de `## Fechadas`, com a
    data de hoje e o destino. Recusa com `ValueError`, sem escrever, id que não está aberto."""
    arquivo = Path(arquivo)
    atual = arquivo.read_text(encoding="utf-8")
    m_abertas = re.compile(_SECAO_RE.format("Abertas")).search(atual)
    if m_abertas is None:
        raise ValueError("seção '## Abertas' ausente")

    entrada_re = re.compile(
        rf"(?ms)^###\s+{re.escape(h_id)}\s*·\s*`([^`]*)`.*?(?=^###\s+|\Z)"
    )
    m = entrada_re.search(m_abertas.group(1))
    if m is None:
        raise ValueError(f"{h_id} não está em '## Abertas'")
    tipo = m.group(1)
    inicio = m_abertas.start(1) + m.start()
    fim = m_abertas.start(1) + m.end()
    sem_entrada = atual[:inicio] + atual[fim:]

    m_fechadas = re.compile(_SECAO_RE.format("Fechadas")).search(sem_entrada)
    if m_fechadas is None:
        raise ValueError("seção '## Fechadas' ausente")
    corpo = m_fechadas.group(1)
    linhas_tabela = [m_l for m_l in re.finditer(r"(?m)^\|.*\|[ \t]*$\n?", corpo)]
    if not linhas_tabela:
        raise ValueError("'## Fechadas' sem tabela")
    destino_limpo = " ".join(destino.split()).replace("|", "\\|")
    linha = f"| {h_id} | `{tipo}` | {date.today().isoformat()} | {destino_limpo} |\n"
    ponto = m_fechadas.start(1) + linhas_tabela[-1].end()
    if not sem_entrada[:ponto].endswith("\n"):
        linha = "\n" + linha
    arquivo.write_text(sem_entrada[:ponto] + linha + sem_entrada[ponto:], encoding="utf-8")


def concluir(arquivo: Path, data: str) -> None:
    """Grava `last_huddle` — a data em que o huddle da pessoa aconteceu (`D-08`)."""
    regioes.escrever_campos(Path(arquivo), {"last_huddle": data})


_MAX_COMMITS = 50


def _campo_sem_aspas(arquivo: Path, chave: str) -> str:
    valor = regioes.ler_campo(arquivo, chave) or ""
    return valor.strip().strip('"').strip("'")


def pauta(arquivo: Path, desde: str | None = None) -> dict:
    """O que a conversa percorre: abertas da pessoa e os commits desde o último huddle.

    `desde` padrão é `last_huddle`, ou `created` se vazio; conta desde o início do dia — data sem
    hora, o git a lê como o mesmo dia na hora atual e perde os commits da manhã. No máximo 50 commits, com a contagem dos
    omitidos. Sem git, lista vazia e `aviso` — nunca exceção. Devolve
    `{"abertas", "desde", "commits", "omitidos", "aviso"}`; cada aberta é `{"id", "tipo", "data",
    "autor", "texto"}`.
    """
    arquivo = Path(arquivo)
    texto = arquivo.read_text(encoding="utf-8")
    desde = desde or _campo_sem_aspas(arquivo, "last_huddle") or _campo_sem_aspas(arquivo, "created")

    abertas = [
        {chave: valor for chave, valor in lida.items() if chave != "evidencia"}
        for lida in _entradas(_secao(texto, "Abertas") or "")
    ]

    commits: list[str] = []
    aviso = None
    try:
        r = subprocess.run(
            ["git", "log", "--oneline", f"--since={desde} 00:00:00"],
            cwd=arquivo.parent, capture_output=True, text=True,
        )
        if r.returncode != 0:
            aviso = f"git log falhou: {r.stderr.strip()}"
        else:
            commits = [l for l in r.stdout.splitlines() if l.strip()]
    except OSError as erro:
        aviso = f"git indisponível: {erro}"

    return {
        "abertas": abertas,
        "desde": desde,
        "commits": commits[:_MAX_COMMITS],
        "omitidos": max(0, len(commits) - _MAX_COMMITS),
        "aviso": aviso,
    }


def migrar(projeto: Path, usuario: str) -> Path | None:
    """Move o huddle único de projeto para o arquivo da pessoa, por `git mv`, e acrescenta ao
    frontmatter os campos do mecanismo (`D-13`: exceção declarada a `regioes.escrever_campos` —
    os três campos são do mecanismo, e a migração só roda quando o humano a chama).

    Sem o arquivo antigo, não faz nada e devolve `None`. Recusa com `FileExistsError` se o destino
    já existir. Campo que o arquivo já tenha não é duplicado.
    """
    projeto = Path(projeto)
    destino = caminho(projeto, usuario)
    antigo = _arquivo_unico(destino)
    if not antigo.exists():
        return None
    if destino.exists():
        raise FileExistsError(f"{destino} já existe — a migração não junta arquivos")

    destino.parent.mkdir(parents=True, exist_ok=True)
    subprocess.run(
        ["git", "mv", str(antigo), str(destino)], cwd=projeto, check=True, capture_output=True
    )

    linhas = destino.read_text(encoding="utf-8").splitlines(keepends=True)
    _, fim = regioes._limites_frontmatter(linhas, destino)
    presentes = {l.split(":", 1)[0] for l in linhas[1:fim] if ":" in l}
    bloco = [
        l for l in _campos_da_pessoa(usuario).splitlines(keepends=True)
        if l.split(":", 1)[0] not in presentes
    ]
    if bloco and bloco != ["# huddle\n"]:
        sistema = next((i for i in range(1, fim) if linhas[i].strip() == "# system"), fim)
        linhas[sistema:sistema] = bloco + ["\n"]
        destino.write_text("".join(linhas), encoding="utf-8")
    return destino
