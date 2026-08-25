#!/usr/bin/env python3
"""Projeção de backlog e de situação — unidade 0002-09.

Duas superfícies derivadas de uma fonte única: o estado real vive no frontmatter de cada unidade
(`unit_id`, `state`, título). Este módulo projeta o backlog no arquivo do plano — o miolo entre
`<!-- backlog:start -->`/`<!-- backlog:end -->` — e a coluna Situação da linha do plano em
`_planos.md`. Por serem derivadas de uma leitura só do disco, as duas nunca divergem entre si; e
`regioes.escrever_regiao` só grava se o resultado mudou, o que dá a idempotência que o critério de
aceite exige (norma, decisão 17 e "Estado derivado de verificação").

Tudo é validado antes de qualquer escrita: plano sem os marcadores do backlog, ou sem linha
correspondente em `_planos.md`, levanta `ValueError` sem tocar em nenhum dos dois arquivos — inclusive
em `dry_run`, que nunca grava.

Sobre "X de Y derivadas" (D-03, fechado pela L-18 / unidade 0001-07). Y vem da contagem de
unidades **previstas** na seção `## Escopo` do plano — toda linha numerada de toda tabela da
seção, incluindo as de correções fora de fase. Escopo ilegível ou ausente conta como
desconhecido: o rodapé diz "desconhecido" em vez de arriscar um total errado, e a situação
nunca projeta `concluído` por não saber contar (ver `_contar_previstas` e `_situacao`).

`projetar` aceita **diretório** ou **arquivo do plano** (unidade 0001-14). Quem decide o ramo é o
`plan_size` **declarado**; a forma de `alvo` só localiza o arquivo. A primeira implementação
ramificava pela forma — diretório sempre projetava como grande —, e isso foi corrigido na revisão
de 2026-08-25: medido contra o plano real `0001`, que é grande, passá-lo **como arquivo** devolvia
região vazia e situação lida de `status`, sem levantar, e gravava essa situação em `_planos.md`.
Projeção errada que parece certa é a classe da `L-18`.

Porte ausente ou desconhecido cai no ramo do **grande**, e é deliberado: grande levanta quando falta
o marcador, então o caso não reconhecido falha alto. Cair no pequeno faria o oposto — projetar em
silêncio a partir de `status`, que é justamente o defeito acima.
"""

from __future__ import annotations

import re
from datetime import date
from pathlib import Path
from typing import NamedTuple

import lib
import numeracao
import regioes

_H1 = re.compile(r"^#\s+(.+?)\s*$")
_ESCOPO_HEADING = re.compile(r"(?m)^##\s+Escopo\s*$")
_PROXIMO_H2 = re.compile(r"(?m)^##\s")
_LINHA_TABELA_NUMERADA = re.compile(r"(?m)^\|\s*\d+\s*\|")
_TAREFAS_HEADING = re.compile(r"(?m)^##\s+Tarefas\s*$")
_ITEM_TAREFA = re.compile(r"(?m)^-\s+\[( |x|X)\]\s+(.+?)\s*$")


class _Unidade(NamedTuple):
    arquivo: Path
    unit_id: str | None
    state: str | None
    titulo: str | None


def projetar(alvo: Path, dry_run: bool = False) -> tuple[str, str]:
    """Projeta o backlog do plano e a situação derivada — devolve `(backlog, situacao)`.

    `alvo` aceita diretório ou arquivo do plano; o ramo vem do `plan_size` **declarado**, e a forma
    só localiza o arquivo — ver o módulo para o defeito que essa ordem corrige.

    Levanta `ValueError` se o plano não tem linha correspondente em `_planos.md`. Em médio e
    grande, levanta também se faltam os marcadores `backlog:start`/`backlog:end`; no pequeno essa
    ausência não é erro — não existe região para projetar (unidade 0001-14). As checagens que
    levantam rodam antes de qualquer escrita.

    O caminho é resolvido na entrada: `lib.plan_root()` já vem resolvido, e `relative_to` entre um
    caminho resolvido e outro não quebra com `ValueError` obscuro — foi o que aconteceu ao chamar com
    caminho relativo em 2026-07-26. É o mesmo cuidado que a unidade 0002-01 fixou e que o `move-md`
    aprendeu com symlink.
    """
    alvo = Path(alvo).resolve()
    arquivo_do_plano = alvo / f"{alvo.name}.md" if alvo.is_dir() else alvo
    plan_size = _plan_size(arquivo_do_plano)

    href = arquivo_do_plano.relative_to(lib.plan_root()).as_posix()
    miolo_planos = regioes.ler_regiao(lib.planos_md(), "planos")
    if miolo_planos is None:
        raise ValueError(f"região 'planos' ausente em {lib.planos_md()}")
    if f"]({href})" not in miolo_planos:
        raise ValueError(f"plano {href!r} não tem linha em {lib.planos_md()}")

    if plan_size == "pequeno":
        backlog, situacao = _projetar_pequeno(arquivo_do_plano)
        escreve_backlog = False
    elif plan_size == "médio":
        backlog, situacao = _projetar_medio(arquivo_do_plano)
        escreve_backlog = True
    else:
        backlog, situacao = _projetar_grande(arquivo_do_plano.parent, arquivo_do_plano)
        escreve_backlog = True

    if dry_run:
        return backlog, situacao

    if escreve_backlog:
        regioes.escrever_regiao(arquivo_do_plano, "backlog", backlog)
    regioes.escrever_regiao(lib.planos_md(), "planos", _substituir_situacao(miolo_planos, href, situacao))

    return backlog, situacao


def _plan_size(arquivo_do_plano: Path) -> str | None:
    """`plan_size` normalizado — sem aspas nem espaço; `None` se ausente ou vazio."""
    bruto = regioes.ler_campo(arquivo_do_plano, "plan_size")
    if bruto is None:
        return None
    normalizado = bruto.strip(" \t\"'")
    return normalizado or None


def _projetar_grande(dir_plano: Path, arquivo_do_plano: Path) -> tuple[str, str]:
    """Comportamento inalterado desde antes da 0001-14: unidades derivadas em `dir_plano`,
    contra o previsto em `## Escopo`."""
    if regioes.ler_regiao(arquivo_do_plano, "backlog") is None:
        raise ValueError(f"marcador 'backlog' não existe em {arquivo_do_plano}")
    previstas = _contar_previstas(arquivo_do_plano.read_text(encoding="utf-8"))
    unidades = sorted(_unidades(dir_plano), key=_chave_ordenacao)
    return _montar_backlog(unidades, previstas), _situacao(unidades, previstas)


def _projetar_medio(arquivo_do_plano: Path) -> tuple[str, str]:
    """A região espelha `## Tarefas`; a situação vem das caixas marcadas — médio não deriva
    unidade nenhuma, então não há `state` para ler."""
    if regioes.ler_regiao(arquivo_do_plano, "backlog") is None:
        raise ValueError(f"marcador 'backlog' não existe em {arquivo_do_plano}")
    tarefas = _tarefas(arquivo_do_plano.read_text(encoding="utf-8"))
    return _montar_backlog_tarefas(tarefas), _situacao_tarefas(tarefas)


_STATUS_SITUACAO = {"approved": "em desenvolvimento", "done": "concluído"}


def _projetar_pequeno(arquivo_do_plano: Path) -> tuple[str, str]:
    """Sem região de backlog — não existe o que projetar ali. A situação vem de `status`,
    escrito pelo humano (`aprovar` grava `approved`; só o humano grava `done`, nenhum script
    escreve). Fora do vocabulário conhecido falha fechado, nunca `concluído` — mesma regra da
    L-18 aplicada à única fonte que o pequeno tem."""
    status = regioes.ler_campo(arquivo_do_plano, "status")
    normalizado = status.strip(" \t\"'") if status else None
    return "", _STATUS_SITUACAO.get(normalizado, "em desenvolvimento")


def _contar_previstas(texto_plano: str) -> int | None:
    """Conta as unidades previstas em `## Escopo` — soma de toda linha numerada, em toda tabela
    da seção, até o próximo heading de nível 2. `None` se a seção não existir — escopo ilegível
    nunca vira zero por engano."""
    inicio = _ESCOPO_HEADING.search(texto_plano)
    if inicio is None:
        return None
    resto = texto_plano[inicio.end() :]
    fim = _PROXIMO_H2.search(resto)
    bloco = resto[: fim.start()] if fim else resto
    return len(_LINHA_TABELA_NUMERADA.findall(bloco))


def _unidades(dir_plano: Path) -> list[_Unidade]:
    """Lê `unit_id`, `state` e título de cada `NN-*.md` do diretório — nunca o arquivo do plano."""
    arquivo_do_plano = f"{dir_plano.name}.md"
    unidades = []
    for item in dir_plano.iterdir():
        if not item.is_file() or item.name == arquivo_do_plano:
            continue
        if not numeracao.PADRAO_ARQUIVO_UNIDADE.match(item.name):
            continue
        unit_id = regioes.ler_campo(item, "unit_id")
        state = regioes.ler_campo(item, "state")
        unidades.append(_Unidade(item, unit_id, state, _titulo(item, unit_id)))
    return unidades


def _chave_ordenacao(unidade: _Unidade) -> tuple[bool, str, str]:
    """Por `unit_id` — nunca pela ordem do sistema de arquivos, que varia por plataforma.

    `unit_id` ausente ordena por último, pelo nome do arquivo — nunca quebra a ordenação inteira.
    """
    return (unidade.unit_id is None, unidade.unit_id or "", unidade.arquivo.name)


def _primeiro_h1(path: Path) -> str | None:
    """Primeiro `# título` do corpo — nunca da região de frontmatter, que também começa com `#`."""
    linhas = path.read_text(encoding="utf-8").splitlines()
    if not linhas or linhas[0].strip() != "---":
        return None

    fim = None
    for i in range(1, len(linhas)):
        if linhas[i].strip() == "---":
            fim = i
            break
    if fim is None:
        return None

    for linha in linhas[fim + 1 :]:
        m = _H1.match(linha)
        if m:
            return m.group(1)
    return None


def _titulo(path: Path, unit_id: str | None) -> str | None:
    """Título do H1, sem o prefixo `unit_id — `.

    O prefixo é reconhecido pelo `unit_id` já lido do frontmatter — nunca por um padrão genérico de
    dígitos — para que um H1 fora da convenção não tenha texto cortado por engano.
    """
    bruto = _primeiro_h1(path)
    if bruto is None:
        return None
    prefixo = f"{unit_id} — "
    if unit_id and bruto.startswith(prefixo):
        return bruto[len(prefixo) :]
    return bruto


def _linha_unidade(unidade: _Unidade) -> str:
    """Uma linha da tabela — unidade sem título entra como problema visível, nunca como exceção."""
    texto_link = unidade.unit_id or unidade.arquivo.stem
    titulo = unidade.titulo or "(sem título)"
    estado = f"`{unidade.state}`" if unidade.state else "—"
    return f"| [{texto_link}]({unidade.arquivo.name}) | {titulo} | {estado} |"


def _plural(quantidade: int, singular: str, plural: str) -> str:
    return singular if quantidade == 1 else plural


def _montar_rodape(unidades: list[_Unidade], previstas: int | None) -> str:
    total = len(unidades)
    verificadas = sum(1 for u in unidades if u.state == "verified")
    hoje = date.today().isoformat()
    total_previsto = "desconhecido" if previstas is None else str(previstas)
    return (
        f"{total} de {total_previsto} {_plural(total, 'derivada', 'derivadas')} · "
        f"{verificadas} {_plural(verificadas, 'verificada', 'verificadas')} · "
        f"atualizado em {hoje}"
    )


def _montar_backlog(unidades: list[_Unidade], previstas: int | None) -> str:
    """O miolo completo da região `backlog` — tabela, linha em branco e rodapé."""
    linhas = ["", "| Unidade | Título | Estado |", "|---|---|---|"]
    linhas += [_linha_unidade(u) for u in unidades]
    linhas += ["", _montar_rodape(unidades, previstas)]
    return "\n".join(linhas) + "\n"


def _situacao(unidades: list[_Unidade], previstas: int | None) -> str:
    """`concluído` só quando o total previsto é conhecido, coincide com o derivado e todas as
    derivadas estão `verified`. Lista vazia ou escopo ilegível (`previstas is None`) nunca conta
    como concluída — falhar fechado é a correção que a L-18 exige."""
    if not unidades or previstas is None or len(unidades) != previstas:
        return "em desenvolvimento"
    if all(u.state == "verified" for u in unidades):
        return "concluído"
    return "em desenvolvimento"


def _tarefas(texto_plano: str) -> list[tuple[bool, str]] | None:
    """Itens de `## Tarefas` — `(concluída, texto)` por linha, na ordem em que aparecem no plano.
    `None` se a seção não existir — mesmo padrão de `_contar_previstas` para `## Escopo`: fonte
    ilegível não vira lista vazia por engano, porque as duas projetam `em desenvolvimento` de
    formas diferentes (ver `_situacao_tarefas` e `_montar_backlog_tarefas`)."""
    inicio = _TAREFAS_HEADING.search(texto_plano)
    if inicio is None:
        return None
    resto = texto_plano[inicio.end() :]
    fim = _PROXIMO_H2.search(resto)
    bloco = resto[: fim.start()] if fim else resto
    return [(marca.lower() == "x", texto.strip()) for marca, texto in _ITEM_TAREFA.findall(bloco)]


def _rodape_tarefas(tarefas: list[tuple[bool, str]] | None) -> str:
    hoje = date.today().isoformat()
    if tarefas is None:
        return f"tarefas: desconhecido · atualizado em {hoje}"
    total = len(tarefas)
    feitas = sum(1 for feita, _ in tarefas if feita)
    return (
        f"{feitas} de {total} {_plural(feitas, 'tarefa concluída', 'tarefas concluídas')} · "
        f"atualizado em {hoje}"
    )


def _montar_backlog_tarefas(tarefas: list[tuple[bool, str]] | None) -> str:
    """O miolo da região `backlog` no médio — espelha `## Tarefas` como checklist, mais rodapé.

    `None` (seção ausente) não impede a escrita: o rodapé diz 'desconhecido' em vez de arriscar
    uma contagem errada, no mesmo espírito de `_montar_rodape` para escopo ilegível."""
    if tarefas is None:
        return "\n" + _rodape_tarefas(None) + "\n"
    linhas = [""] + [f"- [{'x' if feita else ' '}] {texto}" for feita, texto in tarefas]
    linhas += ["", _rodape_tarefas(tarefas)]
    return "\n".join(linhas) + "\n"


def _situacao_tarefas(tarefas: list[tuple[bool, str]] | None) -> str:
    """`concluído` só com ao menos uma tarefa e todas marcadas. Lista vazia ou `## Tarefas`
    ausente (`None`) nunca conta como concluída — a mesma regra de falhar fechado que a L-18
    exige de `_situacao`, aplicada à fonte que o médio tem."""
    if not tarefas:
        return "em desenvolvimento"
    if all(feita for feita, _ in tarefas):
        return "concluído"
    return "em desenvolvimento"


def _substituir_situacao(miolo: str, href: str, nova_situacao: str) -> str:
    """Troca só a coluna Situação da linha que linka para `href` — as demais, inclusive Origem, ficam como estão."""
    alvo = f"]({href})"
    linhas = miolo.split("\n")
    for i, linha in enumerate(linhas):
        if alvo in linha:
            linhas[i] = _substituir_coluna(linha, nova_situacao)
            return "\n".join(linhas)
    raise ValueError(f"nenhuma linha contém {alvo!r}")


def _substituir_coluna(linha: str, nova_situacao: str) -> str:
    partes = linha.split("|")
    if len(partes) != 9:
        raise ValueError(f"linha de _planos.md não tem 7 colunas — {linha!r}")
    partes[6] = f" {nova_situacao} "
    return "|".join(partes)
