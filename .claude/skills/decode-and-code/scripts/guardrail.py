#!/usr/bin/env python3
"""Mecanismo de guardrail — hook `PreToolUse` que casa ferramenta e inspeciona conteúdo.

Unidade 0001-04. Lê o payload do hook, resolve `tool_name` contra o regex de `ferramenta`
de cada regra e aplica o `detector` — outro regex — ao conteúdo de `tool_input` das que
casarem. A primeira regra cujos dois regex casam decide a recusa; nenhuma casando, libera.

Regra é dado, não código: `nome`, `ferramenta`, `detector` e `mensagem`, carregados de um
JSON externo (`.claude/guardrails.json` no projeto que instala). Este módulo não conhece o
nome de nenhum serviço, tabela ou projeto — só a forma de uma regra. A instância que dá
função à camada vive no arquivo de regras, nunca aqui (invariante 2 do `CLAUDE.md`: nada
específico de projeto viaja no plugin).

Falha aberta por construção: `decidir` — o único ponto que o hook chama — nunca levanta.
Payload ilegível, arquivo de regras ausente ou regra malformada viram liberação, com o
motivo devolvido para quem chama avisar em stderr. Guardrail que trava o trabalho por
defeito próprio é obstáculo, não a proteção que o guardrail promete (codex, *Guardrail*).
"""

from __future__ import annotations

import json
import re
import tempfile
from pathlib import Path


def _avaliar(payload: dict, regras: list[dict]) -> dict | None:
    """Primeira regra cuja `ferramenta` casa `tool_name` e cujo `detector` casa o conteúdo.

    Devolve `{"regra": nome, "mensagem": mensagem}` na recusa, `None` na liberação. Regra
    com `ferramenta`/`detector` que não compila como regex levanta `re.error` — cabe a
    `decidir`, não a esta função, transformar isso em liberação.
    """
    tool_name = payload.get("tool_name", "")
    # `old_string` é o que o `Edit` tira do arquivo, não o que a escrita contém (`D-11` do `0009`).
    conteudo = "\n".join(
        valor for chave, valor in payload.get("tool_input", {}).items()
        if isinstance(valor, str) and chave != "old_string"
    )
    for regra in regras:
        if re.search(regra["ferramenta"], tool_name) and re.search(regra["detector"], conteudo):
            return {"regra": regra["nome"], "mensagem": regra["mensagem"]}
    return None


def decidir(payload_bruto: str, regras_caminho: Path) -> tuple[dict | None, str | None]:
    """Ponto único que o hook chama — nunca levanta. Devolve `(decisão, aviso)`.

    `decisão` é o dict de recusa, ou `None` quando libera. `aviso` é a mensagem para stderr
    quando a falha abriu o guardrail — payload malformado, arquivo de regras ausente, ou
    regra que levantou —, e `None` quando nada de anormal aconteceu.
    """
    try:
        payload = json.loads(payload_bruto)
        regras = json.loads(regras_caminho.read_text(encoding="utf-8"))["regras"]
        return _avaliar(payload, regras), None
    except Exception as erro:
        return None, f"guardrail: falha aberta, liberando — {erro!r}"


CHAVES_DA_REGRA = ("nome", "ferramenta", "detector", "mensagem")


def lint_arquivo(caminho: Path) -> list[str]:
    """Verifica se `caminho` é um arquivo de regras que `decidir` consegue usar — lista vazia
    quando aprovado (plano 0007, T3).

    Fecha a falha aberta antes que ela aconteça: regra malformada desliga a si mesma e todas as
    seguintes, porque `decidir` libera em qualquer exceção. Levanta `FileNotFoundError` se o
    arquivo não existe, como `rules.lint_rule`.
    """
    texto = caminho.read_text(encoding="utf-8")
    try:
        dados = json.loads(texto)
    except json.JSONDecodeError as erro:
        return [f"JSON inválido: {erro}"]
    if not isinstance(dados, dict) or not isinstance(dados.get("regras"), list):
        return ["o arquivo precisa ser um objeto com 'regras' como lista"]

    problemas: list[str] = []
    vistos: set[str] = set()
    for i, regra in enumerate(dados["regras"], start=1):
        if not isinstance(regra, dict):
            problemas.append(f"regra {i}: não é objeto")
            continue
        for chave in CHAVES_DA_REGRA:
            valor = regra.get(chave)
            if not (isinstance(valor, str) and valor.strip()):
                problemas.append(f"regra {i}: '{chave}' ausente, vazio ou não é texto")
            elif chave in ("ferramenta", "detector"):
                try:
                    re.compile(valor)
                except re.error as erro:
                    problemas.append(f"regra {i}: '{chave}' não compila como regex — {erro}")
        nome = regra.get("nome")
        if isinstance(nome, str) and nome.strip():
            if nome in vistos:
                problemas.append(f"regra {i}: nome repetido {nome!r}")
            vistos.add(nome)
    return problemas


def _provar(regra: dict, proibido: dict, permitido: dict) -> None:
    """`ValueError` se `regra`, avaliada **sozinha** (`D-03`), não nega `proibido` ou nega `permitido`."""
    with tempfile.TemporaryDirectory() as tmp:
        sozinha = Path(tmp) / "candidata.json"
        sozinha.write_text(json.dumps({"regras": [regra]}, ensure_ascii=False), encoding="utf-8")
        problemas = lint_arquivo(sozinha)
        if problemas:
            raise ValueError("regra malformada: " + "; ".join(problemas))

        negado, aviso = decidir(json.dumps(proibido), sozinha)
        if aviso or not negado or negado.get("regra") != regra["nome"]:
            raise ValueError(f"a regra {regra['nome']!r} não nega o caso proibido")
        liberado, aviso = decidir(json.dumps(permitido), sozinha)
        if aviso or liberado:
            raise ValueError(f"a regra {regra['nome']!r} nega o caso permitido")


def _ler(arquivo: Path) -> dict:
    """Conteúdo de um arquivo de regras que passa em `lint_arquivo` — `{"regras": []}` se falta."""
    if not arquivo.exists():
        return {"regras": []}
    problemas = lint_arquivo(arquivo)
    if problemas:
        raise ValueError(f"{arquivo} já está malformado: " + "; ".join(problemas))
    return json.loads(arquivo.read_text(encoding="utf-8"))


def _gravar(arquivo: Path, dados: dict) -> None:
    """Grava `dados` em `arquivo` só se o resultado passar em `lint_arquivo`."""
    texto = json.dumps(dados, ensure_ascii=False, indent=2) + "\n"
    with tempfile.TemporaryDirectory() as tmp:
        resultado = Path(tmp) / "guardrails.json"
        resultado.write_text(texto, encoding="utf-8")
        problemas = lint_arquivo(resultado)
        if problemas:
            raise ValueError("resultado reprovado: " + "; ".join(problemas))
    arquivo.parent.mkdir(parents=True, exist_ok=True)
    arquivo.write_text(texto, encoding="utf-8")


def _arquivo_morto(raiz: Path) -> Path:
    """`.claude/archive/guardrails.json` — o hook só lê `.claude/guardrails.json` (plano 0020)."""
    return raiz / ".claude" / "archive" / "guardrails.json"


def adicionar(raiz: Path, regra: dict, proibido: dict, permitido: dict, replace: bool = False) -> Path:
    """Acrescenta `regra` a `<raiz>/.claude/guardrails.json` só se ela se provar pelo par.

    A regra candidata é avaliada **sozinha** (`D-03`): `decidir` precisa negar `proibido` com a
    própria regra e liberar `permitido`. Avaliada junto das existentes, uma regra anterior que já
    negasse o caso faria a prova passar sem a candidata casar nada. `proibido` e `permitido` têm a
    forma do payload do hook (`tool_name`, `tool_input`). Cria o arquivo se faltar. Levanta
    `ValueError` — sem escrever nada — para regra malformada, prova que falha, nome repetido, nome
    arquivado (plano 0020, nome reservado) ou arquivo existente que não passa em `lint_arquivo`.
    Devolve o caminho do arquivo.

    Com `replace=True` (plano 0020), a regra com o mesmo nome precisa existir, e a nova toma o
    lugar dela na lista, só depois de se provar pelo par.
    """
    arquivo = raiz / ".claude" / "guardrails.json"
    _provar(regra, proibido, permitido)
    dados = _ler(arquivo)
    posicao = next((i for i, r in enumerate(dados["regras"]) if r["nome"] == regra["nome"]), None)
    if replace:
        if posicao is None:
            raise ValueError(f"regra {regra['nome']!r} não existe para substituir")
        dados["regras"][posicao] = regra
    else:
        if posicao is not None:
            raise ValueError(f"já existe regra com o nome {regra['nome']!r}")
        if any(r.get("nome") == regra["nome"] for r in _ler(_arquivo_morto(raiz))["regras"]):
            raise ValueError(f"regra arquivada, o nome fica reservado: {regra['nome']!r}")
        dados["regras"].append(regra)
    _gravar(arquivo, dados)
    return arquivo


_CAMPOS_DO_ARQUIVAMENTO = ("archived_at", "archived_by", "reason")


def archive(raiz: Path, nome: str, motivo: str, autor: str, data: str | None = None) -> Path:
    """Move a regra `nome` de `.claude/guardrails.json` para `.claude/archive/guardrails.json`.

    Plano 0020. Ganha `archived_at`, `archived_by` e `reason`; o par proibido/permitido não vai,
    porque o `guardrails.json` não o guarda. Levanta `ValueError`, sem escrever, para nome
    desconhecido, motivo ou autor vazio. Devolve o caminho do arquivo de arquivo.
    """
    from rules import _campos_do_arquivamento  # fora do topo: o hook importa este módulo

    data, autor, motivo = _campos_do_arquivamento(motivo, autor, data)
    arquivo = raiz / ".claude" / "guardrails.json"
    dados = _ler(arquivo)
    regra = next((r for r in dados["regras"] if r["nome"] == nome), None)
    if regra is None:
        existentes = ", ".join(r["nome"] for r in dados["regras"]) or "nenhuma"
        raise ValueError(f"regra desconhecida: {nome!r} — existem: {existentes}")

    morto = _arquivo_morto(raiz)
    arquivadas = _ler(morto)
    arquivadas["regras"].append({**regra, "archived_at": data, "archived_by": autor, "reason": motivo})
    dados["regras"].remove(regra)
    _gravar(morto, arquivadas)
    _gravar(arquivo, dados)
    return morto


def restore(raiz: Path, nome: str, proibido: dict, permitido: dict) -> Path:
    """Devolve a regra arquivada `nome` ao `.claude/guardrails.json`, sem os três campos.

    Plano 0020. O arquivado não guarda o par, então a regra volta só depois de se provar por um par
    novo, como no `adicionar`. Levanta `ValueError` se não está arquivada, se o nome está ocupado
    ou se a prova falha — e o arquivo de arquivo fica como estava. Devolve o caminho do arquivo.
    """
    morto = _arquivo_morto(raiz)
    arquivadas = _ler(morto)
    guardada = next((r for r in arquivadas["regras"] if r.get("nome") == nome), None)
    if guardada is None:
        raise ValueError(f"regra {nome!r} não está arquivada")
    regra = {k: v for k, v in guardada.items() if k not in _CAMPOS_DO_ARQUIVAMENTO}
    _provar(regra, proibido, permitido)

    arquivo = raiz / ".claude" / "guardrails.json"
    dados = _ler(arquivo)
    if any(r["nome"] == nome for r in dados["regras"]):
        raise ValueError(f"já existe regra com o nome {nome!r}")
    dados["regras"].append(regra)
    arquivadas["regras"].remove(guardada)
    _gravar(arquivo, dados)
    _gravar(morto, arquivadas)
    return arquivo
