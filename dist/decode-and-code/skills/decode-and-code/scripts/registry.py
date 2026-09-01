#!/usr/bin/env python3
"""Registry de guidelines — liga e desliga sem edição manual, unidade 0001-10.

Desligar não é campo de frontmatter: o Claude Code carrega todo arquivo de `.claude/rules/`, e não
existe `enabled: false` que ele respeite. A única forma real de desativar é sair do diretório — por
isso `desligar` **move** o arquivo para `.claude/rules-off/`, e `ligar` devolve. O conteúdo nunca é
reescrito: a operação é `Path.rename`, byte-idêntico por construção, nunca leitura seguida de escrita.

Só guideline — rule com `paths:` — participa deste registry. Princípio não tem chave para desligar
(`D-01` do plano: guideline diz escopo de validade, não opcionalidade; princípio não é rejeitável, e
por isso `desligar` recusa com a razão). `ligar` sobre o que já está ligado é no-op silencioso — e
o mesmo vale para `desligar` sobre o que já está desligado, pela mesma lógica.

`registry.json` é projeção, nunca fonte — a verdade é onde o arquivo está no disco. `listar()` lê os
dois (disco e `registry.json`) e **reporta divergência** em vez de escolher um: arquivo movido à mão
para `rules-off/` aparece como desligado mesmo que o registry ainda diga o contrário, com o campo
`divergente` marcando o desacordo. `registry.json` só é reprojetado quando uma transição real
acontece — no-op não escreve nada, porque nada mudou para registrar.
"""

from __future__ import annotations

import json
from datetime import date
from pathlib import Path

import lib
import regioes


def _dir_rules() -> Path:
    return lib.repo_root() / ".claude" / "rules"


def _dir_off(dir_rules: Path) -> Path:
    """Diretório **irmão**, nunca subdiretório de `rules/`.

    Medido em 2026-08-24 com o instrumento da `0001-05`: um arquivo em `.claude/rules/_off/`
    **continua carregando** por `path_glob_match` — o matcher recursa para dentro do
    subdiretório, e mover para lá desligava no disco sem desligar em contexto (`L-26`).
    """
    return dir_rules.parent / "rules-off"


def _caminho_registry(dir_rules: Path) -> Path:
    return dir_rules / "registry.json"


def _e_guideline(arquivo: Path) -> bool:
    """`paths:` presente é guideline; ausente é princípio — mesmo corte de `rules.lint_guideline`."""
    return regioes.ler_campo(arquivo, "paths") is not None


def _guidelines_no_disco(dir_rules: Path) -> dict[str, str]:
    """Nome -> estado ('ligada'/'desligada') de cada guideline encontrada nos dois diretórios."""
    achadas = {p.stem: "ligada" for p in sorted(dir_rules.glob("*.md")) if _e_guideline(p)}
    achadas.update(
        {p.stem: "desligada" for p in sorted(_dir_off(dir_rules).glob("*.md")) if _e_guideline(p)}
    )
    return achadas


def _todos_os_nomes(dir_rules: Path) -> list[str]:
    """Todo `.md` dos dois diretórios, princípio ou guideline — o universo válido para `ligar`/`desligar`."""
    nomes = {p.stem for p in dir_rules.glob("*.md")}
    nomes |= {p.stem for p in _dir_off(dir_rules).glob("*.md")}
    return sorted(nomes)


def _localizar(dir_rules: Path, nome: str) -> Path | None:
    """Caminho de `<nome>.md` em `.claude/rules/` ou `rules-off/` — None se não existe em nenhum dos dois."""
    for pasta in (dir_rules, _dir_off(dir_rules)):
        candidato = pasta / f"{nome}.md"
        if candidato.is_file():
            return candidato
    return None


def _nome_desconhecido(dir_rules: Path, nome: str) -> ValueError:
    existentes = _todos_os_nomes(dir_rules)
    return ValueError(
        f"guideline desconhecida: {nome!r} — existem: {', '.join(existentes) or 'nenhuma'}"
    )


def _ler_registry(caminho: Path) -> dict:
    if not caminho.is_file():
        return {}
    try:
        dados = json.loads(caminho.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return {}
    return dados if isinstance(dados, dict) else {}


def _reprojetar(dir_rules: Path, transicionada: str) -> None:
    """Reescreve `registry.json` por inteiro — uma entrada por guideline conhecida no disco agora.

    Preserva a data de transição de quem não mudou nesta chamada; só `transicionada`, e qualquer
    guideline nunca vista antes, recebe a data de hoje.
    """
    guidelines = _guidelines_no_disco(dir_rules)
    anterior = _ler_registry(_caminho_registry(dir_rules))
    hoje = date.today().isoformat()

    novo = {}
    for nome, estado in guidelines.items():
        registrada = anterior.get(nome)
        tinha_data = isinstance(registrada, dict) and "atualizado_em" in registrada
        data = registrada["atualizado_em"] if tinha_data and nome != transicionada else hoje
        novo[nome] = {"estado": estado, "atualizado_em": data}

    texto = json.dumps(novo, ensure_ascii=False, indent=2, sort_keys=True) + "\n"
    _caminho_registry(dir_rules).write_text(texto, encoding="utf-8")


def listar() -> list[dict]:
    """Guidelines conhecidas com o estado derivado do disco — nunca do `registry.json`.

    Cada entrada: `{"nome", "estado", "divergente"}`. `divergente` é `True` quando o `registry.json`
    registra um estado diferente do que o disco mostra agora — sinal de arquivo movido à mão.
    """
    dir_rules = _dir_rules()
    guidelines = _guidelines_no_disco(dir_rules)
    registrado = _ler_registry(_caminho_registry(dir_rules))

    saida = []
    for nome, estado in sorted(guidelines.items()):
        entrada = registrado.get(nome)
        estado_registrado = entrada.get("estado") if isinstance(entrada, dict) else None
        divergente = estado_registrado is not None and estado_registrado != estado
        saida.append({"nome": nome, "estado": estado, "divergente": divergente})
    return saida


def ligar(nome: str) -> Path:
    """Move `<nome>` de volta para `.claude/rules/` — no-op se já estiver lá. Devolve o caminho final.

    Levanta `ValueError` nomeando o que existe, sem escrever nada, se `nome` não for encontrado em
    nenhum dos dois diretórios.
    """
    dir_rules = _dir_rules()
    origem = _localizar(dir_rules, nome)
    if origem is None:
        raise _nome_desconhecido(dir_rules, nome)

    destino = dir_rules / origem.name
    if origem == destino:
        return destino

    origem.rename(destino)
    _reprojetar(dir_rules, nome)
    return destino


def desligar(nome: str) -> Path:
    """Move `<nome>` para `.claude/rules-off/` — no-op se já estiver lá. Devolve o caminho final.

    Recusa com `ValueError` se `nome` for princípio — rule sem `paths:` não tem chave para desligar
    (`D-01`: guideline diz escopo de validade; princípio não é rejeitável). Levanta `ValueError`
    nomeando o que existe se `nome` não for encontrado. Nos dois casos, nada é escrito.
    """
    dir_rules = _dir_rules()
    origem = _localizar(dir_rules, nome)
    if origem is None:
        raise _nome_desconhecido(dir_rules, nome)
    if not _e_guideline(origem):
        raise ValueError(
            f"{nome!r} é princípio, sem 'paths:' — princípio não é rejeitável (D-01) e por isso "
            "não tem chave para desligar"
        )

    destino = _dir_off(dir_rules) / origem.name
    if origem == destino:
        return destino

    destino.parent.mkdir(parents=True, exist_ok=True)
    origem.rename(destino)
    _reprojetar(dir_rules, nome)
    return destino
