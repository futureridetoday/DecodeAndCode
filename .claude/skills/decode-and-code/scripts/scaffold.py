#!/usr/bin/env python3
"""Scaffold da aprovação de um plano — unidade 0002-05.

Transforma um plano aprovado no `_inbox` em estrutura permanente numa operação só: monta o alvo
`<core>/<NNNN>-<nome>/<NNNN>-<nome>.md`, delega a movimentação a `move-md.py` — que já
reescreve os links nas duas direções, resolve symlink e ignora bloco de código — e registra
`plan_id`/`status` no plano e a linha correspondente em `_planos.md` (decisão D-04 do plano 0002).

Move primeiro, escreve o frontmatter depois: se a movimentação falhar, o plano continua íntegro no
`_inbox` e a operação é retomável; o inverso deixaria um plano marcado como aprovado sem nunca ter
saído do lugar.

`move-md.py` tem hífen no nome do arquivo — não é importável por `import` direto. É carregado por
`importlib.util`, como o próprio teste do move-md já faz, para que `REPO_ROOT` continue
substituível por mock nos testes desta unidade também.

`move_script` resolve contra a raiz da **skill** (`lib._config_path().parent`), nunca contra
`lib.repo_root()` — é a correção da `0004-04`. `move-md.py` mora dentro de `scripts/` da própria
skill (mecanismo, `D-06` do plano `0004-installable-method`), e resolver pela raiz do projeto é o
que fazia este módulo ser o único dos 20 que não importava a partir de um pacote instalado: o
projeto ao redor podia nem existir ainda. `runners`, no mesmo `config.json`, continua relativo ao
**projeto** — `test-python.sh` é instância de quem instala (`D-05`), não mecanismo. Os dois campos
têm quadros de referência diferentes, e é por isso que se resolvem contra raízes diferentes.

O `<nome>` do alvo é o nome do próprio arquivo do plano (decisão 19 — o plano mantém o nome ao sair
do `_inbox`), não o campo `module` do frontmatter: os dois costumam coincidir quando o plano cria o
módulo, mas nada garante que sejam o mesmo valor.

`block` não é lido: a fórmula do alvo usa só `core` e `<nome>` no formato 1, e só `<nome>` no 2.

O alvo ramifica por `plan_size` (unidade 0001-14): pequeno e médio vão direto para
`<core>/<NNNN>-<nome>.md`, sem subpasta — pasta para um arquivo só é custo puro, e no pequeno
ela nunca ganharia companhia, porque o porte não decompõe nada. Só o grande recebe a subpasta
`<core>/<NNNN>-<nome>/<NNNN>-<nome>.md`, como sempre foi. `move_md.mover` já garante o diretório
pai com `mkdir(parents=True, exist_ok=True)` — nenhum `mkdir` extra é necessário para o caso
sem subpasta.

**Formato 2** (codex, *Raiz dos planos*, subparte 2.2.05): o plano vai para a raiz dos planos, sem
pasta por parte do sistema — o pequeno como `<NNNN>-<nome>.md`, o médio e o grande como
`<NNNN>-<nome>/<NNNN>-<nome>.md` — e `core` é campo opcional. O que está acima, com `core` como
pasta, vale para o plano do formato 1 (codex, *Plano anterior ao redesign*).

A concorrência entre planos não é medida aqui: o codex a define por comportamento, que script não
mede, e a revisão a confere por julgamento (K-07).
"""

from __future__ import annotations

import importlib.util
from datetime import date
from pathlib import Path

import lib
import nomenclatura
import numeracao
import regioes

_spec = importlib.util.spec_from_file_location(
    "move_md", lib._config_path().parent / lib.config()["move_script"]
)
move_md = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(move_md)



def _campo_vazio(valor: str | None) -> bool:
    """True se o campo está ausente ou sem valor real.

    Inclui o padrão `""` que o repositório usa para campo vazio no frontmatter (ex.: `block: ""`
    em `0002-dev-units.md`) — sem isso, um `core: ""` não preenchido passaria como valor válido,
    porque `ler_campo` nunca interpreta o texto como YAML (decisão D-01).
    """
    if valor is None:
        return True
    return valor.strip(" \t\"'") == ""


def _ja_aprovado(plano: Path) -> bool:
    """True quando o plano já saiu do `_inbox` com número atribuído.

    Derivação incremental (`D-12`) reinvoca `aprovar` sobre um plano já movido, e sem esta
    guarda a chamada morre em `nomenclatura.validar_nome`: o stem já carrega o prefixo
    numérico que a validação recusa por construção. Correção pontual de 2026-08-24 —
    formalizada com teste declarado pela unidade `0001-06` (`L-17`).
    """
    if _campo_vazio(regioes.ler_campo(plano, "plan_id")):
        return False
    return lib.inbox().resolve() not in plano.resolve().parents


def _mover(origem: Path, destino: Path) -> None:
    """Move o plano compondo move-md — nunca reimplementando a reescrita de links."""
    conteudo = origem.read_text(encoding="utf-8")
    novo_conteudo, _ = move_md.reescrever_links_internos(conteudo, origem.parent, destino.parent)
    move_md.mover(origem, destino)
    destino.write_text(novo_conteudo, encoding="utf-8")
    move_md.reescrever_referencias(origem, destino, dry_run=False)


def _linha_planos_md(
    numero: str, nome: str, core: str | None, module: str | None, alvo: Path, approved_at: str
) -> str:
    href = alvo.relative_to(lib.plan_root()).as_posix()
    return (
        f"| {numero} | [{nome}]({href}) | {core or '—'} | {module or ''} | — | "
        f"em desenvolvimento | {approved_at} |\n"
    )


def _registrar_planos_md(
    numero: str, nome: str, core: str | None, module: str | None, alvo: Path, approved_at: str
) -> None:
    caminho = lib.planos_md()
    miolo = regioes.ler_regiao(caminho, "planos")
    linha = _linha_planos_md(numero, nome, core, module, alvo, approved_at)
    regioes.escrever_regiao(caminho, "planos", (miolo or "") + linha)


def aprovar(plano: Path, dry_run: bool = False) -> Path:
    """Aprova um plano do `_inbox` — devolve o caminho final, movido ou só calculado em dry-run.

    O alvo depende do `plan_size` declarado (unidade 0001-14): pequeno e médio recebem
    `<core>/<NNNN>-<nome>.md`, sem subpasta; grande recebe `<core>/<NNNN>-<nome>/<NNNN>-<nome>.md`,
    como sempre. `_garantir_secao_backlog` só roda em médio e grande — o pequeno não tem região de
    backlog para garantir, porque não há projeção nenhuma nesse porte.

    **Idempotente:** plano já aprovado devolve o próprio caminho sem escrever nada, para que a
    derivação incremental reinvoque o modo `derive` sem tratar o caso no markdown (`L-17`).

    Levanta `ValueError` se o plano não declara `core`, `plan_size` (ou declara fora do
    vocabulário `lib.PLAN_SIZES_VALIDOS`), `plan_type` (ou declara fora do vocabulário do formato do plano, `lib.PLAN_TYPES_POR_FORMATO`,
    plano 0012), `approved_by`, `approved_at` (ou declara algo que não é
    data ISO), se falta no frontmatter qualquer campo que a aprovação escreve (`plan_id`, `status`
    — a linha tem de existir, ainda que vazia; conferido antes de mover, para não deixar o plano
    meio aprovado), ou se o nome do arquivo falha a validação sintática (`nomenclatura.validar_nome`).
    Levanta `FileExistsError` se o alvo já existe. Em qualquer um dos casos — inclusive em
    `dry_run` — nada é escrito.
    """
    if _ja_aprovado(plano):
        return plano.resolve()

    versao = lib.formato(plano)
    core = regioes.ler_campo(plano, "core")
    if _campo_vazio(core):
        if versao == lib.FORMATO_ANTERIOR:
            raise ValueError(f"plano não declara 'core' — {plano}")
        core = None  # formato 2: a parte do sistema é campo opcional, nunca pasta

    plan_size = regioes.ler_campo(plano, "plan_size")
    if _campo_vazio(plan_size):
        raise ValueError(f"plano não declara 'plan_size' — {plano}")
    plan_size = plan_size.strip(" \t\"'")
    if plan_size not in lib.PLAN_SIZES_VALIDOS:
        raise ValueError(
            f"plan_size fora do vocabulário {lib.PLAN_SIZES_VALIDOS} — {plan_size!r} em {plano}"
        )

    plan_type = regioes.ler_campo(plano, "plan_type")
    if _campo_vazio(plan_type):
        raise ValueError(f"plano não declara 'plan_type' — {plano}")
    plan_type = plan_type.strip(" \t\"'")
    tipos = lib.PLAN_TYPES_POR_FORMATO[versao]
    if plan_type not in tipos:
        raise ValueError(
            f"plan_type fora do vocabulário {tipos} — {plan_type!r} em {plano}"
        )

    approved_by = regioes.ler_campo(plano, "approved_by")
    if _campo_vazio(approved_by):
        raise ValueError(f"plano não declara 'approved_by' — {plano}")

    approved_at = regioes.ler_campo(plano, "approved_at")
    if _campo_vazio(approved_at):
        raise ValueError(f"plano não declara 'approved_at' — {plano}")
    approved_at = approved_at.strip(" \t\"'")
    try:
        date.fromisoformat(approved_at)
    except ValueError:
        raise ValueError(f"approved_at não é data ISO — {approved_at!r} em {plano}")

    module = regioes.ler_campo(plano, "module")

    numero = numeracao.proximo_plano()
    nome = plano.stem
    motivos = nomenclatura.validar_nome(nome)
    if motivos:
        raise ValueError(f"nome de plano inválido {nome!r} — {'; '.join(motivos)}")

    if versao == lib.FORMATO_ATUAL:
        # codex, *Raiz dos planos*: todos juntos na raiz; o pequeno é arquivo, médio e grande, pasta
        base = lib.plan_root()
        pasta = plan_size in ("médio", "grande")
    else:
        base = lib.core_dir(core)
        pasta = plan_size == "grande"
    if pasta:
        alvo = base / f"{numero}-{nome}" / f"{numero}-{nome}.md"
    else:
        alvo = base / f"{numero}-{nome}.md"
    if alvo.exists():
        raise FileExistsError(f"alvo já existe — {alvo}")

    campos = {"plan_id": f'"{numero}"', "status": "approved"}
    for campo in campos:
        if regioes.ler_campo(plano, campo) is None:
            raise ValueError(f"plano não declara '{campo}' no frontmatter — {plano}")

    if dry_run:
        return alvo

    _mover(plano, alvo)
    if plan_size in ("médio", "grande"):
        _garantir_secao_backlog(alvo)
    regioes.escrever_campos(alvo, campos)
    _registrar_planos_md(numero, nome, core, module, alvo, approved_at)

    return alvo


_SECAO_BACKLOG = "## Backlog\n\n<!-- backlog:start -->\n<!-- backlog:end -->\n"


def _garantir_secao_backlog(alvo: Path) -> None:
    """Insere a seção vazia se o plano não a trouxer — `backlog.projetar` exige o par.

    Aqui, e não em `backlog.projetar`: `regioes.escrever_regiao` recusa região
    inexistente de propósito, porque região nova é decisão humana. Aprovar já é
    o momento em que o script monta a estrutura do plano, então criar o bloco
    aqui respeita a regra em vez de contorná-la.

    Antes de `## Fonte` quando ela existe, para seguir a ordem dos planos já no
    repositório; no fim do arquivo quando não existe.
    """
    if regioes.ler_regiao(alvo, "backlog") is not None:
        return

    texto = alvo.read_text(encoding="utf-8")
    fonte = texto.find("\n## Fonte")
    corte = fonte + 1 if fonte != -1 else len(texto)
    alvo.write_text(texto[:corte] + _SECAO_BACKLOG + "\n" + texto[corte:], encoding="utf-8")
