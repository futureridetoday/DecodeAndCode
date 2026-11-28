#!/usr/bin/env python3
"""Lint de formato de plano por porte — unidade 0001-13, e o formato 2 na subparte 2.2.05.

`plan_size` (`0001-12`) declara o porte; este módulo verifica que o plano obedece o que o porte dele
promete. A regra depende da versão do formato (`lib.formato`):

- **Formato 2** (codex, *Porte*, *Plano técnico*, *Independência entre planos*): todo plano tem
  `## Objetivo`, `## Histórias`, `## Independência` e `## Recursos` (a tabela de recursos do plano,
  que pode dizer que não há nenhum). O pequeno tem `## Tarefas` e nenhuma unidade; o médio tem
  `## Unidades` com exatamente uma linha numerada; o grande, com duas ou mais. A região de backlog é
  criada na aprovação (`scaffold.aprovar`), então o lint não a exige, e a recusa só no pequeno.
- **Formato 1**, o plano anterior ao redesign: a regra de antes — médio com `## Tarefas`, grande
  com `## Escopo` e `## Independência`, pequeno sem decomposição.

Segue o mesmo desenho de `lint_unidade.py`/`lint_skill.py`: só lê, devolve lista de problemas, nunca
levanta por conteúdo malformado — quem levanta por `plan_size` ausente ou fora do vocabulário é
`scaffold.aprovar` (`0001-12`), que é o gate de aprovação. Aqui, ausência ou valor inválido só entram
como problema na lista, porque este lint também roda sobre plano ainda no `_inbox`, antes da
aprovação existir.
"""

from __future__ import annotations

import re
from pathlib import Path

import lib
import porte
import regioes


def lint(plano: Path) -> list[str]:
    """Verifica se `plano` está no formato do porte que declara — lista vazia quando aprovado.

    `plan_size` ausente, vazio ou fora do vocabulário encerra a checagem ali: sem porte não há
    schema contra o qual conferir os demais blocos, e o problema devolvido nomeia exatamente isso.
    `plan_id` e `status` têm de existir no frontmatter (`plan_id: ""` vale num rascunho): é o que
    `scaffold.aprovar` escreve, e ele não cria campo.
    """
    try:
        plan_size = regioes.ler_campo(plano, "plan_size")
    except ValueError:
        return ["frontmatter ausente ou malformado — sem '---' de abertura e fechamento"]

    if not (plan_size and plan_size.strip()):
        return ["campo obrigatório ausente no frontmatter: plan_size"]

    plan_size = plan_size.strip()
    if plan_size not in lib.PLAN_SIZES_VALIDOS:
        return [f"plan_size fora do vocabulário {lib.PLAN_SIZES_VALIDOS}: {plan_size!r}"]

    problemas: list[str] = [
        f"campo obrigatório ausente no frontmatter: {campo}"
        for campo in ("plan_id", "status")
        if regioes.ler_campo(plano, campo) is None
    ]
    problemas.extend(_checar_tipo(plano))

    corpo = _corpo(plano.read_text(encoding="utf-8"))
    try:
        versao = lib.formato(plano)
    except ValueError:
        versao = None  # `_checar_tipo` já devolveu o problema do formato
    if versao == lib.FORMATO_ATUAL:
        problemas.extend(_checar_formato_atual(plano, corpo, plan_size))
        return problemas
    problemas.extend(_checar_independencia(corpo, plan_size))
    problemas.extend(_checar_decomposicao(corpo, plan_size))
    problemas.extend(_checar_backlog(plano, plan_size))
    return problemas


# Seções que todo plano do formato 2 tem, em qualquer porte (codex, *Plano técnico*).
SECOES_DO_FORMATO_ATUAL = ("Objetivo", "Histórias", "Independência", "Recursos")

_LINHA_NUMERADA = re.compile(r"(?m)^\|\s*\d+\s*\|")


def unidades_previstas(corpo: str) -> int | None:
    """Linhas numeradas da tabela em `## Unidades` — `None` quando a seção não existe."""
    m = re.search(r"(?m)^##\s+Unidades\s*$", corpo)
    if m is None:
        return None
    resto = corpo[m.end():]
    fim = re.search(r"(?m)^##\s", resto)
    return len(_LINHA_NUMERADA.findall(resto[: fim.start()] if fim else resto))


def secoes_exigidas(plano: Path) -> tuple[str, ...]:
    """As seções de todo plano do formato 2, ou as que um módulo declara para o tipo do plano.

    O plano mínimo da correção, por exemplo, traz o defeito no lugar das histórias (módulo `fix`).
    """
    plan_type = (regioes.ler_campo(plano, "plan_type") or "").strip(" \t\"'")
    for modulo in lib.modulos():
        if plan_type in modulo["plan_sections"]:
            return tuple(modulo["plan_sections"][plan_type])
    return SECOES_DO_FORMATO_ATUAL


def _checar_teste_do_pequeno(plano: Path) -> list[str]:
    """No pequeno, a revisão declara o critério e o teste (codex, *Critério de aceite*): o plano traz
    `test`, `state` e `verified_at`, que o `verificar` projeta como numa unidade. `test` vazio só no
    tipo aceito pela aprovação (`rule`)."""
    campos = {c: regioes.ler_campo(plano, c) for c in ("test", "state", "verified_at")}
    problemas = [f"pequeno exige '{c}' no frontmatter, ainda que vazio" for c, v in campos.items() if v is None]
    plan_type = (regioes.ler_campo(plano, "plan_type") or "").strip(" \t\"'")
    test = (campos["test"] or "").strip(" \t\"'")
    if campos["test"] is not None and not test and plan_type not in lib.TIPOS_DE_APROVACAO:
        problemas.append("pequeno exige 'test' preenchido: o caminho do teste que verifica o critério")
    return problemas


def _checar_formato_atual(plano: Path, corpo: str, plan_size: str) -> list[str]:
    """As seções do formato 2 e a decomposição que o porte pede (codex, *Porte*)."""
    problemas = [f"formato 2 exige '## {s}'" for s in secoes_exigidas(plano) if not _tem_heading(corpo, s)]
    previstas = unidades_previstas(corpo)
    if plan_size == "pequeno":
        problemas.extend(_checar_teste_do_pequeno(plano))
        if not _tem_heading(corpo, "Tarefas"):
            problemas.append("pequeno exige '## Tarefas'")
        if previstas is not None:
            problemas.append("pequeno não tem unidade — tire '## Unidades' e deixe as tarefas no plano")
        if regioes.ler_regiao(plano, "backlog") is not None:
            problemas.append("pequeno não pode ter região de backlog — sem unidade, a projeção nunca escreveria ali")
        return problemas
    if previstas is None:
        problemas.append(f"{plan_size} exige '## Unidades', com uma linha numerada por unidade")
    elif plan_size == "médio" and previstas != 1:
        problemas.append(f"médio tem exatamente 1 unidade; '## Unidades' tem {previstas}")
    elif plan_size == "grande" and previstas < 2:
        problemas.append(f"grande tem duas ou mais unidades; '## Unidades' tem {previstas}")
    if plan_size == "grande":
        problemas.extend(_checar_prd_do_grande(plano, corpo))
    return problemas


# Seções `###` que a proposta do grande carrega dentro de `## Proposta` (codex, *Proposta*).
SECOES_DA_PROPOSTA_GRANDE = ("Métricas de sucesso", "Requisitos não funcionais e restrições", "Fases de entrega")
SECAO_DE_RESTRICOES = SECOES_DA_PROPOSTA_GRANDE[1]

_RESTRICAO_RE = re.compile(r"(?m)^\s*-\s*\**R-(\d{2})\b")
_CITACAO_RE = re.compile(r"\bR-(\d{2})\b")


def _secao_h2(corpo: str, nome: str) -> str | None:
    """Conteúdo de `## nome` até o próximo `## ` — `None` se ausente."""
    m = re.search(rf"(?ms)^##\s+{re.escape(nome)}\s*$\n(.*?)(?=^##\s|\Z)", corpo)
    return m.group(1) if m else None


def _subsecao(texto: str, titulo: str) -> str | None:
    """Conteúdo de `### titulo` até o próximo `###` ou `##` — `None` se ausente."""
    m = re.search(rf"(?ms)^###\s+{re.escape(titulo)}\s*$\n(.*?)(?=^#{{2,3}}\s|\Z)", texto)
    return m.group(1) if m else None


def restricoes_declaradas(plano: Path) -> set[str]:
    """Os `R-NN` declarados em `### Requisitos não funcionais e restrições` de `## Proposta`."""
    proposta = _secao_h2(_corpo(plano.read_text(encoding="utf-8")), "Proposta") or ""
    secao = _subsecao(proposta, SECAO_DE_RESTRICOES) or ""
    return {f"R-{n}" for n in _RESTRICAO_RE.findall(secao)}


def _checar_prd_do_grande(plano: Path, corpo: str) -> list[str]:
    """As três seções da proposta, o teste do plano inteiro e o dono de cada `R-NN` (codex, *Proposta*)."""
    proposta = _secao_h2(corpo, "Proposta")
    problemas = []
    for titulo in SECOES_DA_PROPOSTA_GRANDE:
        if proposta is None or _subsecao(proposta, titulo) is None:
            problemas.append(f"grande exige '### {titulo}' dentro de '## Proposta'")
    teste = _secao_h2(corpo, "Teste do plano inteiro")
    if teste is None:
        problemas.append("grande exige '## Teste do plano inteiro'")
    problemas.extend(_checar_donos(plano, teste or ""))
    return problemas


def _checar_donos(plano: Path, teste_inteiro: str) -> list[str]:
    """Cada `R-NN` declarado tem dono: o critério de uma unidade ou o teste do plano inteiro.

    Só roda com o plano em `<NNNN-nome>/<NNNN-nome>.md` e unidades na pasta; antes do derive não há o
    que conferir."""
    if plano.name != f"{plano.parent.name}.md":
        return []
    unidades = porte._listar_unidades(plano.parent)
    if not unidades:
        return []
    donos = set(_CITACAO_RE.findall(teste_inteiro))
    for unidade in unidades:
        criterio = _secao_h2(_corpo(unidade.read_text(encoding="utf-8")), "Critério de aceite") or ""
        donos.update(_CITACAO_RE.findall(criterio))
    return [
        f"{r} não tem dono: nenhum '## Critério de aceite' de unidade nem '## Teste do plano inteiro' a cita"
        for r in sorted(restricoes_declaradas(plano))
        if r[2:] not in donos
    ]


def _checar_tipo(plano: Path) -> list[str]:
    """`plan_type` ausente, vazio ou fora do vocabulário do formato — sem encerrar as demais checagens.

    O vocabulário é o da versão do formato do plano (`lib.formato`): `rule` no atual, `norma` no
    anterior ao redesign (codex, *Plano anterior ao redesign*).

    Ao contrário de `plan_size`, o tipo não muda o schema do porte, então os outros blocos seguem
    conferidos. Aspas são despidas como em `scaffold.aprovar`, para lint e gate concordarem.
    """
    try:
        versao = lib.formato(plano)
    except ValueError as erro:
        return [str(erro)]
    tipos = lib.PLAN_TYPES_POR_FORMATO[versao]
    plan_type = (regioes.ler_campo(plano, "plan_type") or "").strip(" \t\"'")
    if not plan_type:
        return ["campo obrigatório ausente no frontmatter: plan_type"]
    if plan_type not in tipos:
        return [f"plan_type fora do vocabulário {tipos} do formato {versao}: {plan_type!r}"]
    return []


def _corpo(texto: str) -> str:
    """Conteúdo após o frontmatter — o texto inteiro se não houver '---' de abertura."""
    linhas = texto.splitlines()
    if not linhas or linhas[0].strip() != "---":
        return texto
    for i in range(1, len(linhas)):
        if linhas[i].strip() == "---":
            return "\n".join(linhas[i + 1 :])
    return ""


def _tem_heading(corpo: str, nome: str) -> bool:
    return bool(re.search(rf"(?m)^##\s+{re.escape(nome)}\s*$", corpo))


def _checar_independencia(corpo: str, plan_size: str) -> list[str]:
    """`pequeno` recusa a seção; `grande` exige; `médio` dispensa — não checado nos dois sentidos."""
    tem = _tem_heading(corpo, "Independência")
    if plan_size == "pequeno" and tem:
        return ["pequeno não pode ter '## Independência' — porte sem decomposição não tem o que dividir"]
    if plan_size == "grande" and not tem:
        return ["grande exige '## Independência'"]
    return []


def _checar_decomposicao(corpo: str, plan_size: str) -> list[str]:
    """`médio` exige `## Tarefas`; `grande` exige `## Escopo`; `pequeno` não tem decomposição a checar."""
    if plan_size == "médio" and not _tem_heading(corpo, "Tarefas"):
        return ["médio exige '## Tarefas'"]
    if plan_size == "grande" and not _tem_heading(corpo, "Escopo"):
        return ["grande exige '## Escopo'"]
    return []


def _checar_backlog(plano: Path, plan_size: str) -> list[str]:
    """`pequeno` recusa a região; `médio` e `grande` exigem — projeção precisa ter onde escrever."""
    tem = regioes.ler_regiao(plano, "backlog") is not None
    if plan_size == "pequeno" and tem:
        return ["pequeno não pode ter região de backlog — sem decomposição, a projeção nunca escreveria ali"]
    if plan_size in ("médio", "grande") and not tem:
        return [f"{plan_size} exige região de backlog"]
    return []
