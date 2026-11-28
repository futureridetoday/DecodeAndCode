#!/usr/bin/env python3
"""Gate de entrada do modo `code` (antes `implement`) — unidade 0002-06.

Recusa começar uma unidade que não sobrevive ao cold-start e devolve a lista
do que falta, para a correção voltar ao `derive` em vez de ser descoberta
pelo executor no meio do trabalho.

Três decisões do método moldam o comportamento: teste **declarado**, não
existente (decisão 15) — o campo `test` precisa estar presente, o arquivo que
ele aponta não; teto de **8 passos** na Sequência (decisão 1), acima disso a
unidade divide; e `unit_type` restrito ao vocabulário do formato da unidade
(`lib.UNIT_TYPES_POR_FORMATO`): `dev`, `plan` e `rule` no atual, `norma` no
lugar de `rule` no anterior ao redesign.

O tipo aceito pela aprovação (`rule`, ou `norma` no formato anterior) inverte a obrigatoriedade de `test`: unidade que entrega markdown
normativo não tem teste que prove que a prosa presta (`L-01`), então `test:`
passa a ser exigido **vazio**. A aprovação humana — `approved_by`/`approved_at`
— é o oráculo em seu lugar, mas é de **saída**: o humano a declara depois de
revisar a entrega, então quem a confere é `verificacao`, nunca este gate — aqui
ela recusaria toda unidade `norma` antes de existir entrega. A linha órfã `Último resultado`
(`L-22`) passa a ser recusada no corpo: ninguém a projetava, e ela sempre
mentia ao lado de um `state: verified` com data.

O gate verifica presença e forma, não coerência entre Contrato e Sequência —
isso é julgamento, fora do alcance de regex.

**Formato 2** (codex, *Definition of Ready*; subparte 2.2.08): a unidade traz os blocos de
`BLOCOS_DO_FORMATO_ATUAL` — a história, o critério de aceite (com o teste no `test:`), as tarefas,
os arquivos, as guidelines dos caminhos, os recursos, as decisões e lacunas que valem para ela e o
que espera das unidades de que depende. `core` e `module` deixam de ser exigidos: não há pasta por parte do
sistema. O teto de passos sai (D-06 do plano do redesign): a unidade não tem limite de tarefas. O
formato 1 segue com os blocos de antes, também sem o teto.
"""

from __future__ import annotations

import re
from pathlib import Path

import lib
import regioes

CAMPOS_FRONTMATTER = ("unit_id", "unit_type", "core", "module", "state")

BLOCOS_CORPO = (
    "Contrato",
    "Sequência",
    "Arquivos",
    "Dependências",
    "Normas aplicáveis",
    "Critério de aceite",
    "Verificação",
)

# Blocos do corpo da unidade no formato 2, na ordem em que o derive os escreve (codex, *Definition of
# Ready*). `Guidelines` é a tabela que `normas.resolver` lê, no lugar de *Normas aplicáveis*.
BLOCOS_DO_FORMATO_ATUAL = (
    "História",
    "Critério de aceite",
    "Tarefas",
    "Arquivos",
    "Guidelines",
    "Recursos",
    "Decisões e lacunas",
    "Depende de",
)
CAMPOS_DO_FORMATO_ATUAL = ("unit_id", "unit_type", "state")

# Onde mora a tabela de guidelines que `normas.resolver` lê, por formato.
SECAO_DE_GUIDELINES = {lib.FORMATO_ANTERIOR: "Normas aplicáveis", lib.FORMATO_ATUAL: "Guidelines"}

_UNIT_ID_RE = re.compile(r"^\d{4}-\d{2}$")
_PASSO_RE = re.compile(r"(?m)^\d+\.\s")
_CAMINHO_RE = re.compile(r"`[^`]*/[^`]*`")
_ULTIMO_RESULTADO_RE = re.compile(r"(?m)^Último resultado:")


def lint(unidade: Path) -> list[str]:
    """Verifica se `unidade` sobrevive ao cold-start — lista vazia quando aprovada."""
    texto = unidade.read_text(encoding="utf-8")
    corpo = _corpo(texto)
    try:
        atual = lib.formato(unidade) == lib.FORMATO_ATUAL
    except ValueError:
        atual = False  # `_checar_frontmatter` devolve o problema do formato

    problemas: list[str] = []
    problemas.extend(_checar_frontmatter(unidade))
    if atual:
        problemas.extend(_checar_blocos_do_formato_atual(corpo))
        problemas.extend(_checar_tarefas(corpo))
    else:
        problemas.extend(_checar_blocos(corpo))
        problemas.extend(_checar_sequencia(corpo))
    problemas.extend(_checar_criterio_aceite(corpo))
    problemas.extend(_checar_arquivos(corpo))
    problemas.extend(_checar_ultimo_resultado(corpo))
    problemas.extend(_checar_normas(unidade, corpo))
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


def _campo_vazio(valor: str | None) -> bool:
    """Mesmo padrão de `scaffold._campo_vazio` — `""` do frontmatter também é vazio."""
    if valor is None:
        return True
    return valor.strip(" \t\"'") == ""


def _checar_frontmatter(unidade: Path) -> list[str]:
    """Exige os campos do cold-start; formato de `unit_id`/`unit_type` só quando declarados.

    `test` sai do laço genérico: sua obrigatoriedade depende de `unit_type` (unidade 0001-13) —
    obrigatório em `dev`/`plan`, exigido **vazio** em `norma`. A aprovação da `norma` não entra
    aqui: é gate de saída, conferido por `verificacao`.
    """
    try:
        atual = lib.formato(unidade) == lib.FORMATO_ATUAL
    except ValueError:
        atual = False
    campos = CAMPOS_DO_FORMATO_ATUAL if atual else CAMPOS_FRONTMATTER
    try:
        valores = {
            chave: regioes.ler_campo(unidade, chave) for chave in campos
        }
        test = regioes.ler_campo(unidade, "test")
    except ValueError:
        return ["frontmatter ausente ou malformado — sem '---' de abertura e fechamento"]

    problemas = [
        f"campo obrigatório ausente no frontmatter: {chave}"
        for chave, valor in valores.items()
        if not (valor and valor.strip())
    ]
    if atual:
        # a aprovação da entrega (P7) grava estes dois; a linha tem de existir, ainda que vazia
        problemas += [
            f"campo ausente no frontmatter, ainda que vazio: {chave}"
            for chave in ("approved_by", "approved_at", "verified_at")
            if regioes.ler_campo(unidade, chave) is None
        ]

    unit_id = valores.get("unit_id")
    if unit_id and unit_id.strip() and not _UNIT_ID_RE.match(unit_id.strip()):
        problemas.append(f"unit_id fora do formato NNNN-NN: {unit_id!r}")

    try:
        tipos = lib.UNIT_TYPES_POR_FORMATO[lib.formato(unidade)]
    except ValueError as erro:
        return problemas + [str(erro)]
    unit_type = valores.get("unit_type")
    unit_type_normalizado = unit_type.strip() if unit_type else ""
    unit_type_valido = unit_type_normalizado if unit_type_normalizado in tipos else None
    if unit_type_normalizado and unit_type_valido is None:
        problemas.append(f"unit_type inválido, esperado {tipos}: {unit_type!r}")

    problemas.extend(_checar_test(test, unit_type_valido))

    return problemas


def _checar_test(test: str | None, unit_type: str | None) -> list[str]:
    """`test:` é obrigatório em `dev`/`plan`; em `norma` é exigido vazio — inverso do resto (`L-01`).

    Usa `_campo_vazio` dos dois lados — não o laço genérico de `_checar_frontmatter`, que não
    despe aspas e deixaria `test: ""` passar como preenchido em `dev`/`plan`.
    """
    if unit_type in lib.TIPOS_DE_APROVACAO:
        if not _campo_vazio(test):
            return [f"unit_type {unit_type!r} exige test: vazio — markdown normativo não roda comando"]
        return []
    if _campo_vazio(test):
        return ["campo obrigatório ausente no frontmatter: test"]
    return []


def _checar_ultimo_resultado(corpo: str) -> list[str]:
    """Recusa a linha órfã (`L-22`): ninguém a projeta, e ela sempre mente ao lado de `state`."""
    if _ULTIMO_RESULTADO_RE.search(corpo):
        return ["linha órfã 'Último resultado' não pode estar no corpo — state/verified_at já cobrem isso (L-22)"]
    return []


def _checar_blocos(corpo: str) -> list[str]:
    """Exige a presença de cada bloco — Responsabilidade é texto em negrito, os demais são headings."""
    problemas = []
    if not re.search(r"(?m)^\*\*Responsabilidade:\*\*", corpo):
        problemas.append("bloco ausente: Responsabilidade")

    for bloco in BLOCOS_CORPO:
        if not re.search(rf"(?m)^##\s+{re.escape(bloco)}\s*$", corpo):
            problemas.append(f"bloco ausente: {bloco}")

    return problemas


def _secao(corpo: str, nome: str) -> str | None:
    """Conteúdo de `## nome` até o próximo heading `## ` ou o fim do corpo — None se ausente."""
    padrao = re.compile(rf"(?ms)^##\s+{re.escape(nome)}\s*$\n(.*?)(?=^##\s+|\Z)")
    m = padrao.search(corpo)
    return m.group(1) if m else None


def _checar_sequencia(corpo: str) -> list[str]:
    """Ausente já é reportada por `_checar_blocos`; aqui cobre vazia e acima do teto."""
    secao = _secao(corpo, "Sequência")
    if secao is None:
        return []

    passos = _PASSO_RE.findall(secao)
    if not passos:
        return ["Sequência sem passos numerados"]
    return []


def _checar_blocos_do_formato_atual(corpo: str) -> list[str]:
    """Cada bloco da Definition of Ready como heading `## `, presente e com conteúdo."""
    problemas = []
    for bloco in BLOCOS_DO_FORMATO_ATUAL:
        secao = _secao(corpo, bloco)
        if secao is None:
            problemas.append(f"bloco ausente: {bloco}")
        elif not secao.strip():
            problemas.append(f"bloco sem conteúdo: {bloco}")
    return problemas


_ITEM_RE = re.compile(r"(?m)^\s*(?:-|\d+\.)\s+\S")


def _checar_tarefas(corpo: str) -> list[str]:
    """Ao menos uma tarefa, em lista; sem teto (D-06)."""
    secao = _secao(corpo, "Tarefas")
    if secao is not None and secao.strip() and not _ITEM_RE.search(secao):
        return ["Tarefas sem item de lista"]
    return []


def _checar_criterio_aceite(corpo: str) -> list[str]:
    """Exige ao menos uma frase — não só o cabeçalho."""
    secao = _secao(corpo, "Critério de aceite")
    if secao is None:
        return []
    if not secao.strip():
        return ["Critério de aceite sem conteúdo"]
    return []


def _checar_normas(unidade: Path, corpo: str) -> list[str]:
    """Um problema por citação de *Normas aplicáveis* que `normas.resolver` não resolve.

    O gate de entrada não pode aprovar norma que não chega ao executor. Seção ausente já é
    reportada por `_checar_blocos`. Import local: `normas` importa este módulo.
    """
    try:
        nome = SECAO_DE_GUIDELINES[lib.formato(unidade)]
    except ValueError:
        return []
    if _secao(corpo, nome) is None:
        return []
    import normas

    _, nao_resolvidas = normas.resolver(unidade)
    rotulo = "guideline" if nome == "Guidelines" else "norma aplicável"
    return [f"{rotulo} não resolve ({n.motivo}): {n.linha}" for n in nao_resolvidas]


def _checar_arquivos(corpo: str) -> list[str]:
    """Exige ao menos um caminho concreto (crase com '/') na tabela de Arquivos."""
    secao = _secao(corpo, "Arquivos")
    if secao is None:
        return []
    if not _CAMINHO_RE.search(secao):
        return ["tabela de Arquivos sem caminho concreto"]
    return []
