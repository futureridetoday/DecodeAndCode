#!/usr/bin/env python3
"""Gate de entrada do modo `implement` — unidade 0002-06.

Recusa começar uma unidade que não sobrevive ao cold-start e devolve a lista
do que falta, para a correção voltar ao `derive` em vez de ser descoberta
pelo executor no meio do trabalho.

Três decisões da norma moldam o comportamento: teste **declarado**, não
existente (decisão 15) — o campo `test` precisa estar presente, o arquivo que
ele aponta não; teto de **8 passos** na Sequência (decisão 1), acima disso a
unidade divide; e `unit_type` restrito a `dev`, `plan` ou `norma` (decisão 28,
estendida pela unidade 0001-13).

`norma` inverte a obrigatoriedade de `test`: unidade que entrega markdown
normativo não tem teste que prove que a prosa presta (`L-01`), então `test:`
passa a ser exigido **vazio**, e a aprovação humana — `approved_by`/
`approved_at` — é o oráculo em seu lugar. A linha órfã `Último resultado`
(`L-22`) passa a ser recusada no corpo: ninguém a projetava, e ela sempre
mentia ao lado de um `state: verified` com data.

O gate verifica presença e forma, não coerência entre Contrato e Sequência —
isso é julgamento, fora do alcance de regex.
"""

from __future__ import annotations

import re
from pathlib import Path

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

TETO_PASSOS = 8
UNIT_TYPES_VALIDOS = ("dev", "plan", "norma")

_UNIT_ID_RE = re.compile(r"^\d{4}-\d{2}$")
_PASSO_RE = re.compile(r"(?m)^\d+\.\s")
_CAMINHO_RE = re.compile(r"`[^`]*/[^`]*`")
_ULTIMO_RESULTADO_RE = re.compile(r"(?m)^Último resultado:")


def lint(unidade: Path) -> list[str]:
    """Verifica se `unidade` sobrevive ao cold-start — lista vazia quando aprovada."""
    texto = unidade.read_text(encoding="utf-8")
    corpo = _corpo(texto)

    problemas: list[str] = []
    problemas.extend(_checar_frontmatter(unidade))
    problemas.extend(_checar_blocos(corpo))
    problemas.extend(_checar_sequencia(corpo))
    problemas.extend(_checar_criterio_aceite(corpo))
    problemas.extend(_checar_arquivos(corpo))
    problemas.extend(_checar_ultimo_resultado(corpo))
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
    obrigatório em `dev`/`plan`, exigido **vazio** em `norma`, que por sua vez exige
    `approved_by`/`approved_at` no lugar do teste.
    """
    try:
        valores = {
            chave: regioes.ler_campo(unidade, chave) for chave in CAMPOS_FRONTMATTER
        }
        test = regioes.ler_campo(unidade, "test")
    except ValueError:
        return ["frontmatter ausente ou malformado — sem '---' de abertura e fechamento"]

    problemas = [
        f"campo obrigatório ausente no frontmatter: {chave}"
        for chave, valor in valores.items()
        if not (valor and valor.strip())
    ]

    unit_id = valores.get("unit_id")
    if unit_id and unit_id.strip() and not _UNIT_ID_RE.match(unit_id.strip()):
        problemas.append(f"unit_id fora do formato NNNN-NN: {unit_id!r}")

    unit_type = valores.get("unit_type")
    unit_type_normalizado = unit_type.strip() if unit_type else ""
    unit_type_valido = unit_type_normalizado if unit_type_normalizado in UNIT_TYPES_VALIDOS else None
    if unit_type_normalizado and unit_type_valido is None:
        problemas.append(f"unit_type inválido, esperado {UNIT_TYPES_VALIDOS}: {unit_type!r}")

    problemas.extend(_checar_test(test, unit_type_valido))
    if unit_type_valido == "norma":
        problemas.extend(_checar_aprovacao_norma(unidade))

    return problemas


def _checar_test(test: str | None, unit_type: str | None) -> list[str]:
    """`test:` é obrigatório em `dev`/`plan`; em `norma` é exigido vazio — inverso do resto (`L-01`).

    Usa `_campo_vazio` dos dois lados — não o laço genérico de `_checar_frontmatter`, que não
    despe aspas e deixaria `test: ""` passar como preenchido em `dev`/`plan`.
    """
    if unit_type == "norma":
        if not _campo_vazio(test):
            return ["unit_type 'norma' exige test: vazio — markdown normativo não roda comando"]
        return []
    if _campo_vazio(test):
        return ["campo obrigatório ausente no frontmatter: test"]
    return []


def _checar_aprovacao_norma(unidade: Path) -> list[str]:
    """`norma` fecha por aprovação humana registrada, nunca por execução — o oráculo da `L-01`."""
    problemas = []
    if _campo_vazio(regioes.ler_campo(unidade, "approved_by")):
        problemas.append("unit_type 'norma' exige 'approved_by' preenchido")
    if _campo_vazio(regioes.ler_campo(unidade, "approved_at")):
        problemas.append("unit_type 'norma' exige 'approved_at' preenchido")
    return problemas


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
    if len(passos) > TETO_PASSOS:
        return [f"Sequência com {len(passos)} passos, acima do teto de {TETO_PASSOS}"]
    return []


def _checar_criterio_aceite(corpo: str) -> list[str]:
    """Exige ao menos uma frase — não só o cabeçalho."""
    secao = _secao(corpo, "Critério de aceite")
    if secao is None:
        return []
    if not secao.strip():
        return ["Critério de aceite sem conteúdo"]
    return []


def _checar_arquivos(corpo: str) -> list[str]:
    """Exige ao menos um caminho concreto (crase com '/') na tabela de Arquivos."""
    secao = _secao(corpo, "Arquivos")
    if secao is None:
        return []
    if not _CAMINHO_RE.search(secao):
        return ["tabela de Arquivos sem caminho concreto"]
    return []
