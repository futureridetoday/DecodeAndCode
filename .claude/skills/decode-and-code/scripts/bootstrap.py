#!/usr/bin/env python3
"""Bootstrap do projeto que instala o método — unidade 0004-02.

Cria, num projeto que acabou de instalar o método, a estrutura que todo o resto do ciclo
pressupõe: `_planos.md` com os marcadores e o cabeçalho da tabela, `_inbox/`, `system/` e
`.claude/`. Idempotente e nunca destrutiva — mesmo contrato de `huddle.iniciar` e do bootstrap de
`porte.registrar`: cada caminho só é criado se ainda não existir, item a item, nunca tudo-ou-nada.

`projeto` chega por parâmetro, e é deliberado: antes do bootstrap o projeto não tem as marcas que
`lib.repo_root()` procura — é justamente o que esta operação vai criar. Resolver a raiz aqui seria
circular. `plan_root` vem do `config()`, componível com a entrada:
`projeto / lib.config()["plan_root"]`.

`.claude/` entra na lista porque `root_markers` exige `.claude/` **e** `docs/` — sem os dois a
âncora da `0004-01` não resolveria o projeto depois do bootstrap (`D-04` do plano
`0004-installable-method`). Não cria runner de teste nem `_inbox/_backlog.md` — instância do
projeto que instala, não estrutura do método (`D-05`).

A norma-mecanismo entra na `0004-04`: sem ela, `<plan_root>/system/modelo-dev-units.md` não existe
no projeto que instala, e os três modos da skill citam uma fonte que não está lá (`L-31` do plano
`0001`). `_fonte_norma` procura em dois lugares, na mesma dualidade da `0004-01` — checkout e
pacote são o mesmo diretório num caso e diretórios diferentes no outro: primeiro `reference/`, ao
lado da própria skill, onde `empacotar.construir` a deixa; só se não estiver lá é que se tenta o
`plan_root` **deste** repositório, o caso de rodar de dentro do checkout, sem pacote nenhum no
meio. Idempotente item a item, como o resto de `iniciar`: projeto que já editou a sua cópia da
norma não a perde num segundo bootstrap.

`project:` do frontmatter de `_planos.md` vem do nome do diretório de `projeto`, nunca fixo —
`porte._CONTEUDO_INICIAL` embutia o nome deste repositório e vazava para quem instalasse (`L-31`
do plano `0001`). Sem arquivo de template (`D-20`): o esqueleto vive em `_CONTEUDO_INICIAL`, como
`porte.py` e `huddle.py` já fazem.
"""

from __future__ import annotations

from datetime import date
from pathlib import Path

import lib

_CONTEUDO_INICIAL = """\
---
# about
name: planos
type: doc
project: {projeto}
description: Registro dos planos aprovados para desenvolvimento — fonte da numeração sequencial e da situação de cada plano
tags: [plan, registro, decode-and-code]

# history
author: ""
created: {criado}
status: draft
version: 1.0.0
updated: ""

# system
scope: project
auto_load: false
dependencies: []
---

# Planos aprovados

Registro dos planos que entraram em desenvolvimento. Planos no `_inbox/` **não aparecem aqui** — só
entram na aprovação, momento em que recebem o número.

Este arquivo é a **fonte da numeração**: o script lê o maior número em uso e toma o próximo.

<!-- planos:start -->
| # | Plano | Core | Módulo | Origem | Situação | Aprovado |
|---|---|---|---|---|---|---|
<!-- planos:end -->

> A **situação** é projetada a partir do estado das unidades — `em desenvolvimento` enquanto houver
> unidade não verificada, `concluído` quando todas passarem. Nunca se edita à mão.

> O miolo entre `<!-- planos:start -->` e `<!-- planos:end -->` é **projeção de script**. Texto
> escrito ali se perde na próxima execução.
"""


def _fonte_norma() -> Path:
    """Onde a norma-mecanismo mora, nos dois lugares que a `0004-04` prevê.

    Primeiro `reference/`, ao lado da própria skill — é onde `empacotar.construir` a deixa quando
    o bootstrap roda de um pacote instalado. Só se ela não estiver lá é que se tenta o `plan_root`
    **deste** repositório — o caso de rodar de dentro do checkout, sem pacote nenhum no meio.
    `lib.plan_root()` só entra nesse segundo ramo: chamá-la incondicionalmente reintroduziria, para
    quem roda de um pacote sem projeto nenhum ao redor ainda, o mesmo `RuntimeError` que a
    `0004-01` corrigiu no `scaffold`.

    Levanta `FileNotFoundError` nomeando os dois candidatos se nenhum existir.
    """
    do_pacote = lib._config_path().parent / "reference" / "modelo-dev-units.md"
    if do_pacote.is_file():
        return do_pacote

    try:
        do_checkout = lib.plan_root() / "system" / "modelo-dev-units.md"
    except RuntimeError:
        do_checkout = None
    if do_checkout is not None and do_checkout.is_file():
        return do_checkout

    raise FileNotFoundError(
        f"norma-mecanismo não encontrada — tentado {do_pacote} e {do_checkout}"
    )


def iniciar(projeto: Path) -> list[Path]:
    """Cria a estrutura mínima em `projeto` — devolve os caminhos criados, em ordem.

    Levanta `FileNotFoundError` se `projeto` não existir, antes de escrever qualquer coisa. Cada
    caminho é pulado se já existir — o pulo é por item, nunca tudo-ou-nada: um projeto que já tem
    `_planos.md` mantém suas linhas, mesmo que `_inbox/` ainda falte. A norma segue o mesmo
    contrato: se `<plan_root>/system/modelo-dev-units.md` já existe, não é sobrescrita — um
    projeto que editou a sua cópia não a perde num segundo bootstrap.
    """
    projeto = Path(projeto).resolve()
    if not projeto.is_dir():
        raise FileNotFoundError(f"projeto não existe — {projeto}")

    raiz_planos = projeto / lib.config()["plan_root"]
    criados: list[Path] = []

    planos_md = raiz_planos / "_planos.md"
    if not planos_md.is_file():
        planos_md.parent.mkdir(parents=True, exist_ok=True)
        planos_md.write_text(
            _CONTEUDO_INICIAL.format(projeto=projeto.name, criado=date.today().isoformat()),
            encoding="utf-8",
        )
        criados.append(planos_md)

    for caminho in (raiz_planos / "_inbox", raiz_planos / "system", projeto / ".claude"):
        if not caminho.is_dir():
            caminho.mkdir(parents=True, exist_ok=True)
            criados.append(caminho)

    norma = raiz_planos / "system" / "modelo-dev-units.md"
    if not norma.is_file():
        norma.parent.mkdir(parents=True, exist_ok=True)
        norma.write_text(_fonte_norma().read_text(encoding="utf-8"), encoding="utf-8")
        criados.append(norma)

    return criados
