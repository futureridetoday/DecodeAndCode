#!/usr/bin/env python3
"""Fixtures sintéticos para a suíte — unidades 0001-02, 0001-11 e 0001-13.

Os seis construtores (`plano`, `unidade`, `skill`, `planos_md`, `rule`, `log_ativacao`) escrevem
artefatos válidos num diretório dado — sempre um `tempfile.TemporaryDirectory()` de quem chama.
Nenhum lê ou grava caminho real do repositório, e nenhum argumento inválido escreve arquivo antes
de levantar `ValueError`.

`UNIDADE_VALIDA` continua exportada como constante — antes inline em `test_lint_unidade.py`
— porque `TestGateDeEntrada` naquele arquivo muta o texto por `.replace()` direto, e precisa
de uma string fixa, não de uma chamada de função.

`unidade()` ganhou `unit_type`/`approved_by`/`approved_at` (0001-13). O par de aprovação só é
**emitido quando tem valor** — com os defaults, a saída é byte a byte a de antes da 0001-13, o que
foi conferido comparando os dois textos, e não pela suíte verde: verde diz que nenhum teste quebrou,
nunca que a saída é a mesma. `plano()` ganhou `tarefas`/`independencia`/`com_backlog` pelo
mesmo motivo: default idêntico ao comportamento anterior (backlog sempre presente, os outros dois
blocos sempre ausentes), e as três portas só divergem do texto de hoje quando o teste de
`lint_plano` pede explicitamente um plano de porte `médio` ou `grande` bem formado.

`plano()` ganhou `com_diretorio` (0001-14), default `True` — mesmo raciocínio: todo chamador
existente pede a forma de diretório (é o que `test_backlog.py`, `test_situacao.py` e
`test_lint_plano.py` já esperavam antes desta unidade, com `_arquivo(dir_plano)` compondo
`dir_plano / f"{dir_plano.name}.md"`), e nenhum precisa mudar. `com_diretorio=False` é o que
produz a forma **real** de pequeno e médio — `<dir>/<core>/<numero>-<nome>.md`, sem subpasta —,
usada só pelos testes que exercitam essa forma diretamente (`test_derive_por_porte.py`); a
função devolve o **arquivo**, não um diretório, porque não há diretório nenhum para devolver.

O default de `plan_size` é `grande` desde a revisão de 2026-08-25 — antes era `pequeno`, herdado de
quando o campo não tinha efeito. Com `com_diretorio=True` e região de backlog, `pequeno` produzia um
artefato que o próprio `lint_plano` recusa (*"pequeno não pode ter região de backlog"*): a `L-21`
dentro do arquivo escrito para impedi-la. Foi o que forçou `backlog.projetar` a ramificar pela forma
em vez do campo, e é o que a correção desfez.

**O default continua incompleto de propósito, e isso é diferente de contraditório.** `## Escopo` e
`## Independência` só aparecem quando pedidos, porque `test_backlog.py` e `test_situacao.py`
exercitam justamente o caminho do escopo ilegível. Falta de bloco é o caso sob teste; porte que
contradiz a própria forma era defeito.
"""

from __future__ import annotations

import re
from pathlib import Path

_UNIT_ID_RE = re.compile(r"^\d{4}-\d{2}$")


def _bloco_aprovacao(approved_by: str, approved_at: str) -> str:
    """As duas linhas de aprovação, ou nada quando nenhuma das duas tem valor.

    Condicional, e não fixo: `dev` não usa os campos, e emiti-los vazios faria o fixture default
    modelar uma unidade que **nenhuma das reais tem** — a `L-21` nascendo dentro do arquivo que
    existe para consolidar formato. Corrigido na revisão de 2026-08-25, depois de a saída ser
    comparada com a de antes da `0001-13`; a suíte estava verde nos dois casos.

    Basta **uma** delas ter valor para as duas saírem: é assim que o lint consegue apontar a que
    falta, e é o que os testes de `norma` sem `approved_by` exercitam.
    """
    if not (approved_by.strip(" \t\"'") or approved_at.strip(" \t\"'")):
        return ""
    return f"\napproved_by: {approved_by}\napproved_at: {approved_at}"


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
unit_type: {unit_type}{aprovacao}

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
    unit_type: str = "dev",
    approved_by: str = '""',
    approved_at: str = '""',
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
        unit_type=unit_type,
        aprovacao=_bloco_aprovacao(approved_by, approved_at),
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
    unit_type: str = "dev",
    approved_by: str = '""',
    approved_at: str = '""',
    state: str = "spec",
    test: str = "caminho/para/test_exemplo.py",
    verified_at: str = '""',
    titulo: str = "Unidade sintética",
    responsabilidade: str = "existir só para o teste do lint.",
) -> Path:
    """Escreve `<dir>/<nome>` — uma unidade que aprova em `lint_unidade.lint()`. Devolve o caminho.

    `unit_type="norma"` (0001-13) pede `test=""` e `approved_by`/`approved_at` preenchidos — quem
    chama compõe isso explicitamente; o default aqui continua sendo uma unidade `dev` comum.
    Levanta `ValueError` se `unit_id` não está no formato `NNNN-NN`, antes de escrever
    qualquer arquivo.
    """
    texto = _texto_unidade(
        unit_id=unit_id,
        core=core,
        module=module,
        unit_type=unit_type,
        approved_by=approved_by,
        approved_at=approved_at,
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
plan_size: {plan_size}
approved_by: {approved_by}
approved_at: {approved_at}
---

# {numero} — Plano sintético
{escopo}{tarefas}{independencia}
Texto antes do backlog — precisa sobreviver à projeção.
{backlog}
Texto depois do backlog — também precisa sobreviver.
"""


def _bloco_escopo(previstas: int | None) -> str:
    """`## Escopo` com `previstas` linhas numeradas — vazio quando `previstas` é `None`."""
    if previstas is None:
        return ""
    linhas = "\n".join(f"| {i:02d} | unidade-{i:02d} | sintética |" for i in range(1, previstas + 1))
    return f"\n## Escopo\n\n| # | Unidade | Responsabilidade |\n|---|---|---|\n{linhas}\n"


def _bloco_tarefas(tarefas: bool) -> str:
    """`## Tarefas` — decomposição do porte `médio` (`lint_plano`, unidade 0001-13)."""
    if not tarefas:
        return ""
    return "\n## Tarefas\n\n- [ ] Tarefa sintética\n"


def _bloco_independencia(independencia: bool) -> str:
    """`## Independência` — exigida no porte `grande`, recusada no `pequeno` (`lint_plano`)."""
    if not independencia:
        return ""
    return "\n## Independência\n\nTexto de independência sintético.\n"


def _bloco_backlog(com_backlog: bool) -> str:
    """Região de backlog — exigida em `médio`/`grande`, recusada em `pequeno` (`lint_plano`)."""
    if not com_backlog:
        return ""
    return "\n## Backlog\n\n<!-- backlog:start -->\n<!-- backlog:end -->\n"


def plano(
    dir: Path,
    *,
    core: str = "builder",
    nome: str = "exemplo",
    numero: str = "0009",
    module: str | None = None,
    status: str = "approved",
    previstas: int | None = None,
    plan_size: str = "grande",
    approved_by: str = "Teste",
    approved_at: str = "2026-07-25",
    tarefas: bool = False,
    independencia: bool = False,
    com_backlog: bool = True,
    com_diretorio: bool = True,
) -> Path:
    """Escreve o plano sintético — devolve o diretório do plano, ou o arquivo `.md` direto.

    `com_diretorio=True` (o default) escreve `<dir>/<core>/<numero>-<nome>/<numero>-<nome>.md` e
    devolve o **diretório** — a mesma forma que todo chamador anterior à 0001-14 já espera de
    `backlog.projetar()`. `com_diretorio=False` escreve `<dir>/<core>/<numero>-<nome>.md`, sem
    subpasta, e devolve o **arquivo** — a forma real de pequeno e médio (unidade 0001-14).

    `previstas`, quando dado, escreve uma seção `## Escopo` com esse tanto de linhas numeradas —
    o que `backlog._contar_previstas` lê. `None` (o default) escreve o plano sem `## Escopo`, para
    os testes de escopo ilegível. `plan_size`/`approved_by`/`approved_at` vêm com default válido
    (`lib.PLAN_SIZES_VALIDOS` e data ISO), para que quem chama sem se importar com aprovação
    continue construindo plano válido.

    `tarefas`/`independencia`/`com_backlog` (0001-13) controlam, respectivamente, `## Tarefas`,
    `## Independência` e a região de backlog — os três blocos que `lint_plano.lint` varia por
    porte. Default (`False`, `False`, `True`) reproduz o texto de antes desses três parâmetros
    existirem; para montar um plano bem formado num porte específico, quem chama passa a
    combinação que a tabela de portes da norma pede — ex. `plan_size="grande"`, `previstas=1`,
    `independencia=True`.

    Levanta `ValueError` se `core` ou `nome` forem vazios, antes de escrever qualquer arquivo.
    """
    if not core.strip():
        raise ValueError("fixtures.plano: 'core' vazio")
    if not nome.strip():
        raise ValueError("fixtures.plano: 'nome' vazio")

    module = module or nome
    texto = _PLANO_TEMPLATE.format(
        nome=nome,
        numero=numero,
        core=core,
        module=module,
        status=status,
        escopo=_bloco_escopo(previstas),
        plan_size=plan_size,
        approved_by=approved_by,
        approved_at=approved_at,
        tarefas=_bloco_tarefas(tarefas),
        independencia=_bloco_independencia(independencia),
        backlog=_bloco_backlog(com_backlog),
    )

    if com_diretorio:
        dir_plano = Path(dir) / core / f"{numero}-{nome}"
        dir_plano.mkdir(parents=True, exist_ok=True)
        (dir_plano / f"{numero}-{nome}.md").write_text(texto, encoding="utf-8")
        return dir_plano

    core_dir = Path(dir) / core
    core_dir.mkdir(parents=True, exist_ok=True)
    arquivo = core_dir / f"{numero}-{nome}.md"
    arquivo.write_text(texto, encoding="utf-8")
    return arquivo


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


def log_ativacao(dir: Path, *, entradas: list[tuple[str, str]], nome: str = "ativacao.log") -> Path:
    """Escreve `<dir>/<nome>` — log de sessão no formato de
    `activation_notice.anunciar_instructions_loaded`. Devolve o caminho do log.

    Cada item de `entradas` é `(caminho, load_reason)`, uma linha por item, na ordem dada.
    """
    linhas = "".join(f"instrução carregada: {caminho} (load_reason={motivo})\n" for caminho, motivo in entradas)
    alvo = Path(dir) / nome
    alvo.parent.mkdir(parents=True, exist_ok=True)
    alvo.write_text(linhas, encoding="utf-8")
    return alvo
