#!/usr/bin/env python3
"""Fixtures sintéticos para a suíte — unidade 0001-02.

Os cinco construtores (`plano`, `unidade`, `skill`, `planos_md`, `rule`) escrevem artefatos
válidos num diretório dado — sempre um `tempfile.TemporaryDirectory()` de quem chama. Nenhum lê ou
grava caminho real do repositório, e nenhum argumento inválido escreve arquivo antes de
levantar `ValueError`.

`UNIDADE_VALIDA` continua exportada como constante — antes inline em `test_lint_unidade.py`
— porque `TestGateDeEntrada` naquele arquivo muta o texto por `.replace()` direto, e precisa
de uma string fixa, não de uma chamada de função.
"""

from __future__ import annotations

import re
from pathlib import Path

_UNIT_ID_RE = re.compile(r"^\d{4}-\d{2}$")

_UNIDADE_TEMPLATE = """\
---
name: exemplo
type: unit
project: DecodeAndCode
description: unidade sintética para teste do lint
tags: []

core: {core}
module: {module}
block: ""
owner: {core}
unit_id: {unit_id}
unit_type: dev

state: {state}
test: {test}
verified_at: {verified_at}

author: Teste
created: 2026-07-25
status: draft
version: 1.0.0
updated: ""

scope: project
auto_load: false
dependencies: []
---

# {unit_id} — {titulo}

**Responsabilidade:** {responsabilidade}

## Contrato

| Campo | Detalhe |
|---|---|
| Entrada | Nenhuma |

## Sequência

1. Primeiro passo
2. Segundo passo
3. Terceiro passo

## Arquivos

| Arquivo | Papel |
|---|---|
| `caminho/para/arquivo.py` | Criar |

## Dependências

Nenhuma.

## Normas aplicáveis

| Norma | Onde |
|---|---|
| Exemplo | em algum lugar |

## Critério de aceite

> O teste passa.

## Verificação

| Item | Valor |
|---|---|
| Teste | {test} |
"""


def _texto_unidade(
    *,
    unit_id: str = "0009-01",
    core: str = "builder",
    module: str = "dev-units",
    state: str = "spec",
    test: str = "caminho/para/test_exemplo.py",
    verified_at: str = '""',
    titulo: str = "Unidade sintética",
    responsabilidade: str = "existir só para o teste do lint.",
) -> str:
    if not _UNIT_ID_RE.match(unit_id):
        raise ValueError(f"fixtures.unidade: unit_id fora do formato NNNN-NN — {unit_id!r}")
    return _UNIDADE_TEMPLATE.format(
        unit_id=unit_id,
        core=core,
        module=module,
        state=state,
        test=test,
        verified_at=verified_at,
        titulo=titulo,
        responsabilidade=responsabilidade,
    )


# Fixa — mesmos valores usados por `TestGateDeEntrada` (test_lint_unidade.py) para mutação
# por `.replace()`. Mudar um default acima muda este texto: mantenha os dois em mente juntos.
UNIDADE_VALIDA = _texto_unidade()


def unidade(
    dir: Path,
    *,
    nome: str = "01-exemplo.md",
    unit_id: str = "0009-01",
    core: str = "builder",
    module: str = "dev-units",
    state: str = "spec",
    test: str = "caminho/para/test_exemplo.py",
    verified_at: str = '""',
    titulo: str = "Unidade sintética",
    responsabilidade: str = "existir só para o teste do lint.",
) -> Path:
    """Escreve `<dir>/<nome>` — uma unidade que aprova em `lint_unidade.lint()`. Devolve o caminho.

    Levanta `ValueError` se `unit_id` não está no formato `NNNN-NN`, antes de escrever
    qualquer arquivo.
    """
    texto = _texto_unidade(
        unit_id=unit_id,
        core=core,
        module=module,
        state=state,
        test=test,
        verified_at=verified_at,
        titulo=titulo,
        responsabilidade=responsabilidade,
    )
    alvo = Path(dir) / nome
    alvo.parent.mkdir(parents=True, exist_ok=True)
    alvo.write_text(texto, encoding="utf-8")
    return alvo


_SKILL_TEMPLATE = """\
---
name: {nome}
description: Descrição de teste para o lint.
disable-model-invocation: false
user-invocable: true

allowed-tools: "Read"

effort: low
context: ""
shell: bash

type: skill
project: DecodeAndCode
author: Teste
created: 2026-08-24
status: draft
version: 1.0.0
updated: ""
scope: project
auto_load: false
tags: []
dependencies: []

hub_id: ""
source: local
---

# {nome}

{corpo}
"""


def skill(
    dir: Path,
    *,
    nome: str = "skill-sintetica",
    corpo: str = "Corpo de teste para o lint.",
) -> Path:
    """Escreve `<dir>/<nome>/SKILL.md` — uma skill que aprova em `lint_skill.lint()`. Devolve o caminho.

    Levanta `ValueError` se `nome` for vazio ou contiver separador de caminho, antes de
    escrever qualquer arquivo.
    """
    if not nome.strip() or "/" in nome or "\\" in nome:
        raise ValueError(f"fixtures.skill: nome inválido — {nome!r}")

    pasta = Path(dir) / nome
    pasta.mkdir(parents=True, exist_ok=True)
    alvo = pasta / "SKILL.md"
    alvo.write_text(_SKILL_TEMPLATE.format(nome=nome, corpo=corpo), encoding="utf-8")
    return alvo


_PLANO_TEMPLATE = """\
---
name: {nome}
type: plan
project: DecodeAndCode
plan_id: "{numero}"
core: {core}
module: {module}
block: ""
status: {status}
---

# {numero} — Plano sintético
{escopo}
Texto antes do backlog — precisa sobreviver à projeção.

## Backlog

<!-- backlog:start -->
<!-- backlog:end -->

Texto depois do backlog — também precisa sobreviver.
"""


def _bloco_escopo(previstas: int | None) -> str:
    """`## Escopo` com `previstas` linhas numeradas — vazio quando `previstas` é `None`."""
    if previstas is None:
        return ""
    linhas = "\n".join(f"| {i:02d} | unidade-{i:02d} | sintética |" for i in range(1, previstas + 1))
    return f"\n## Escopo\n\n| # | Unidade | Responsabilidade |\n|---|---|---|\n{linhas}\n"


def plano(
    dir: Path,
    *,
    core: str = "builder",
    nome: str = "exemplo",
    numero: str = "0009",
    module: str | None = None,
    status: str = "approved",
    previstas: int | None = None,
) -> Path:
    """Escreve `<dir>/<core>/<numero>-<nome>/<numero>-<nome>.md` — devolve o diretório do plano.

    A mesma forma que `backlog.projetar()` espera como argumento. `previstas`, quando dado,
    escreve uma seção `## Escopo` com esse tanto de linhas numeradas — o que `backlog._contar_previstas`
    lê. `None` (o default) escreve o plano sem `## Escopo`, para os testes de escopo ilegível.
    Levanta `ValueError` se `core` ou `nome` forem vazios, antes de escrever qualquer arquivo.
    """
    if not core.strip():
        raise ValueError("fixtures.plano: 'core' vazio")
    if not nome.strip():
        raise ValueError("fixtures.plano: 'nome' vazio")

    module = module or nome
    dir_plano = Path(dir) / core / f"{numero}-{nome}"
    dir_plano.mkdir(parents=True, exist_ok=True)
    texto = _PLANO_TEMPLATE.format(
        nome=nome, numero=numero, core=core, module=module, status=status, escopo=_bloco_escopo(previstas)
    )
    (dir_plano / f"{numero}-{nome}.md").write_text(texto, encoding="utf-8")
    return dir_plano


_CABECALHO_PLANOS = (
    "| # | Plano | Core | Módulo | Origem | Situação | Aprovado |\n|---|---|---|---|---|---|---|\n"
)

_LINHA_PLANOS_PADRAO = (
    "| 0009 | [exemplo](builder/0009-exemplo/0009-exemplo.md) | builder | exemplo"
    " | — | em desenvolvimento | 2026-08-24 |\n"
)


def planos_md(dir: Path, *, linhas: list[str] | None = None) -> Path:
    """Escreve `<dir>/_planos.md` com a região `planos` — devolve o caminho.

    `linhas` são linhas de tabela já formatadas, cada uma terminada em `\\n`; o default é uma
    linha sintética só. Levanta `ValueError` se alguma linha não começar com `|`, antes de
    escrever qualquer arquivo.
    """
    linhas = linhas if linhas is not None else [_LINHA_PLANOS_PADRAO]
    for linha in linhas:
        if not linha.startswith("|"):
            raise ValueError(f"fixtures.planos_md: linha não começa com '|' — {linha!r}")

    alvo = Path(dir) / "_planos.md"
    miolo = "\n" + _CABECALHO_PLANOS + "".join(linhas)
    alvo.write_text(f"<!-- planos:start -->\n{miolo}<!-- planos:end -->\n", encoding="utf-8")
    return alvo


_RULE_TEMPLATE = """\
---
name: {nome}
description: {descricao}
{paths_linha}---

{corpo}
"""


def _texto_rule(
    *,
    nome: str = "regra-sintetica",
    descricao: str = "Descrição de teste para o lint de rule.",
    paths: list[str] | None = None,
    corpo: str = "Corpo de teste para o lint de rule.",
) -> str:
    paths_linha = ""
    if paths is not None:
        entradas = ", ".join(f'"{p}"' for p in paths)
        paths_linha = f"paths: [{entradas}]\n"
    return _RULE_TEMPLATE.format(nome=nome, descricao=descricao, paths_linha=paths_linha, corpo=corpo)


# Fixa — mesmos valores usados para mutação por `.replace()` nos testes de rule, no mesmo
# padrão de UNIDADE_VALIDA.
RULE_VALIDA = _texto_rule()

# Variante com paths: presente e válido — para os testes específicos de guideline.
RULE_COM_PATHS_VALIDA = _texto_rule(paths=["hub/app/**", "hub/lib/**"])


def rule(
    dir: Path,
    *,
    nome: str = "regra-sintetica",
    descricao: str = "Descrição de teste para o lint de rule.",
    paths: list[str] | None = None,
    corpo: str = "Corpo de teste para o lint de rule.",
) -> Path:
    """Escreve `<dir>/<nome>.md` — uma rule que aprova em `rules.lint_rule()`. Devolve o caminho.

    `paths=None` (o default) escreve sem a linha `paths:` — princípio. Uma lista escreve
    `paths: [...]` — guideline. Levanta `ValueError` se `nome` for vazio ou contiver separador
    de caminho, antes de escrever qualquer arquivo.
    """
    if not nome.strip() or "/" in nome or "\\" in nome:
        raise ValueError(f"fixtures.rule: nome inválido — {nome!r}")

    texto = _texto_rule(nome=nome, descricao=descricao, paths=paths, corpo=corpo)
    alvo = Path(dir) / f"{nome}.md"
    alvo.parent.mkdir(parents=True, exist_ok=True)
    alvo.write_text(texto, encoding="utf-8")
    return alvo
