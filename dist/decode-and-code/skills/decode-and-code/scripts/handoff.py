#!/usr/bin/env python3
"""Prompt de orquestração gravado pelo `derive` — plano 0003.

O `derive` terminava entregando estrutura, unidades e backlog, e nada que dissesse como conduzir a
execução daquilo. A ponte era feita à mão, e a qualidade do que vinha depois dependia inteiramente
de quanto aquele texto acertava.

`gerar` grava `_handoff.md` no diretório do plano. **Só o grande o tem**: médio e pequeno executam
na mesma sessão em que foram aprovados, e não há ponte entre sessões a construir.

**Divisão entre script e julgamento, a mesma do resto do método.** Aqui vive o esqueleto e o que se
mede sem opinar — commit, unidades derivadas e verificadas, próximo número livre. A fila, as
pendências do humano e a sugestão de por onde começar chegam por parâmetro, porque são julgamento
de quem deriva.

**O que este módulo deliberadamente não mede: a suíte.** Rodá-la aqui a faria rodar dentro de si
mesma quando o teste deste módulo executasse, que é a recursão contra a qual `verificacao` mantém
uma sentinela. E baked-in ela envelheceria no primeiro commit. O prompt carrega o **comando** e a
regra de somar as duas linhas `Ran` — quem lê mede. É a divergência `L-03` do plano 0003, e ela
fortalece o desenho em vez de enfraquecê-lo: número declarado é alegação, e o prompt inteiro existe
para dizer isso.

O arquivo é **projeção**, regerada a cada `derive` incremental. O prefixo `_` o mantém fora de
`numeracao.PADRAO_ARQUIVO_UNIDADE`, que é o que conta unidades aqui e em `porte`.
"""

from __future__ import annotations

import subprocess
from datetime import date
from pathlib import Path

import lib
import numeracao
import porte
import regioes

NOME_ARQUIVO = "_handoff.md"

_ESQUELETO = """\
# Orquestração — plano {plano}

Você orquestra a execução deste plano. **Você não executa unidade** — unidades rodam em cold-start
próprio, uma por vez. Você prepara, revisa o que volta, e versiona depois de revisar.

## Como disparar cold-start

Dois comandos, um por cenário:

| Comando | Cenário |
|---|---|
| `/implement <unidade>` | **Sessão nova** — já chega em cold-start por conta própria, executa o modo `implement` da skill direto |
| `/delegate <unidade>` | **Esta sessão** — delega ao agent `developer`, sem gastar o contexto de orquestração que você guarda |

## Regras que não mudam

- **Aprovação é do humano.** Nenhum `derive` sem ele dizer, explicitamente, para aquele alvo
- `state` e `verified_at` **nunca se editam à mão** — são projetados por script a partir do teste
- **Nunca editar o miolo entre marcadores** (`<!-- backlog:start -->`, `<!-- planos:start -->`)
- Quem executa unidade **entrega arquivos e relatório, não commita**
- Unidade insuficiente é defeito **da unidade**: a correção volta para quem deriva, como `L-XX`
- Ação irreversível ou que toque mais de 5 arquivos: apresentar antes, aguardar aprovação
- **Todo número que este prompt afirma é alegação.** Meça com o oráculo do projeto, nunca com um
  equivalente montado na hora

## Como revisar — leia antes da primeira entrega

`{norma}`, seção *Como revisar uma entrega*. Ela é a parte que decide a qualidade do que sai, e
não está copiada aqui de propósito: uma fonte por fato.

O que ela exige em uma linha: **medir em vez de reler o relatório**.

## Estado no momento em que este arquivo foi gerado

Gerado em {gerado_em}, sobre o commit `{commit}`. **Confira antes de agir** — se divergir do que
você medir, o que vale é a sua medição, e a divergência merece ser reportada.

| | |
|---|---|
| Unidades derivadas | {derivadas} |
| Verificadas | {verificadas} |
| Próximo número livre | {proxima} |

A suíte **não** está contada aqui, e é deliberado: número declarado envelhece no primeiro commit.
Rode você mesmo, e **some as duas linhas `Ran`** — o total é a soma, nunca a última linha:

```
./scripts/test-python.sh
```

## A fila

{fila}

## Pendências do humano

{pendencias}

## Onde eu começaria, e por quê

{sugestao}

> Sugestão registrada, não decisão. Quem escolhe a ordem é o humano.

## Onde ler, antes de qualquer coisa

1. `.claude/CLAUDE.md` — invariantes e protocolo
2. `{norma}` — a norma
3. `{skill}` — os três modos
4. `{plano_md}` — o plano, com *Escopo*, *Decisões* e *Lacunas*
"""


def _commit() -> str:
    """`HEAD` abreviado — `desconhecido` quando git não responde, nunca exceção."""
    try:
        r = subprocess.run(
            ["git", "rev-parse", "--short", "HEAD"],
            cwd=lib.repo_root(),
            capture_output=True,
        )
    except FileNotFoundError:
        return "desconhecido"
    if r.returncode != 0:
        return "desconhecido"
    return r.stdout.decode("utf-8", errors="replace").strip() or "desconhecido"


def _relativo(caminho: Path, raiz: Path) -> str:
    """Caminho relativo à raiz quando ele está dentro dela; absoluto quando não está.

    `Path.relative_to` levanta `ValueError` para caminho de fora, e o prompt não é lugar de
    exceção obscura — mesma guarda que `porte._linhas_alteradas` usa pelo mesmo motivo. Medido em
    2026-08-27: o caso contra o plano real, que trabalha sobre uma cópia em `tempfile`, quebrava
    aqui antes de escrever qualquer coisa.
    """
    try:
        return caminho.relative_to(raiz).as_posix()
    except ValueError:
        return caminho.as_posix()


def _contagem(dir_plano: Path) -> tuple[int, int]:
    """Unidades derivadas e quantas estão `verified` — lidas do disco, nunca do backlog projetado."""
    unidades = porte._listar_unidades(dir_plano)
    verificadas = sum(1 for u in unidades if (regioes.ler_campo(u, "state") or "").strip() == "verified")
    return len(unidades), verificadas


def gerar(dir_plano: Path, *, fila: str, pendencias: str, sugestao: str) -> Path:
    """Grava `_handoff.md` em `dir_plano` e devolve o caminho. Sobrescreve — é projeção.

    `fila`, `pendencias` e `sugestao` são julgamento de quem deriva, e chegam prontos: o script
    não tem como decidir dependência entre unidades nem o que é pendência do humano.

    Levanta `FileNotFoundError` se `dir_plano` não existir ou não tiver o arquivo do plano — o
    handoff só faz sentido para o porte grande, que é o único com diretório próprio.
    """
    dir_plano = Path(dir_plano)
    plano_md = dir_plano / f"{dir_plano.name}.md"
    if not plano_md.is_file():
        raise FileNotFoundError(f"plano não encontrado para handoff: {plano_md}")

    derivadas, verificadas = _contagem(dir_plano)
    raiz = lib.repo_root()

    texto = _ESQUELETO.format(
        plano=dir_plano.name,
        gerado_em=date.today().isoformat(),
        commit=_commit(),
        derivadas=derivadas,
        verificadas=verificadas,
        proxima=numeracao.proxima_unidade(dir_plano),
        fila=fila.strip(),
        pendencias=pendencias.strip(),
        sugestao=sugestao.strip(),
        norma=_relativo(lib.plan_root() / "system" / "modelo-dev-units.md", raiz),
        skill=_relativo(lib._config_path().parent / "SKILL.md", raiz),
        plano_md=_relativo(plano_md, raiz),
    )

    alvo = dir_plano / NOME_ARQUIVO
    alvo.write_text(texto, encoding="utf-8")
    return alvo
