#!/usr/bin/env python3
"""Ponto de entrada único dos scripts do método — `P-14` do plano `apply-plugin-review`.

As três skills pré-aprovavam `Bash` inteiro no `allowed-tools`: qualquer comando de shell passava
sem pedir no turno da skill, em todo projeto que instalasse o plugin. Estreitar a regra exige **um**
comando para casar — `Bash(python3 "${CLAUDE_SKILL_DIR}/dc.py" *)` —, e este arquivo é esse comando.
É um dispatcher fino: `argparse` e formato de saída; a lógica fica nos módulos, que os testes já
cobrem.

O comando que a skill cita é o `dc.py` **da pasta dela** (`skills/<skill>/dc.py`), um atalho de poucas
linhas que executa este. O caminho direto para cá exigiria `..`, e o modelo o normaliza antes de
rodar — a regra de permissão casa o texto do comando, e deixava de casar.

Rode-o a partir do **diretório do projeto**: instalado como plugin, `lib.repo_root()` não acha o
projeto pelo `__file__` e cai para o `cwd`.

Contrato de saída: texto simples em stdout, um item por linha. Código `0` quando ok ou aprovado;
`1` quando há problema ou reprovação (lint com problemas, nome inválido, `verificar` fora de
`verified`, `concorrencia` com conflito ou não verificável); `2` para erro de uso ou exceção, com a
mensagem em stderr e sem traceback. Fora de `verified`, `verificar` acrescenta o motivo: a saída do
teste, cortada nas últimas 80 linhas (e dizendo que cortou). `normas` sai `0` mesmo com linhas não
resolvidas: elas vão na saída, sob `Não resolvidas:`, para o executor relatar.
"""

from __future__ import annotations

import argparse
import os
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

OK = 0
REPROVADO = 1
ERRO = 2

# Quanto da saída de um teste reprovado o `verificar` mostra — o fim, onde as suítes põem a falha.
_LINHAS_DE_SAIDA = 80

# Seção do stdin do `handoff` → parâmetro de `handoff.gerar`.
_SECOES_HANDOFF = {"## Fila": "fila", "## Pendências": "pendencias", "## Sugestão": "sugestao"}


# Os módulos são importados dentro de cada handler: um `config.json` malformado, por exemplo,
# levanta ao importar `scaffold`, e fora de `main` isso escaparia como traceback com código 1.


def _validar_nome(args: argparse.Namespace) -> int:
    import nomenclatura

    motivos = nomenclatura.validar_nome(args.nome)
    for motivo in motivos:
        print(motivo)
    if not motivos:
        print("ok")
    return REPROVADO if motivos else OK


def _concorrencia(args: argparse.Namespace) -> int:
    import scaffold

    linhas = scaffold.concorrentes(Path(args.plano))
    if linhas is None:
        print(f"não verificável: o plano não declara 'core' — {args.plano}")
        return REPROVADO
    for linha in linhas:
        print(linha)
    if not linhas:
        print("sem conflito")
    return REPROVADO if linhas else OK


def _bootstrap(args: argparse.Namespace) -> int:
    import bootstrap

    criados = bootstrap.iniciar(Path(args.projeto))
    for caminho in criados:
        print(caminho)
    if not criados:
        print("nada a criar")
    return OK


def _aprovar(args: argparse.Namespace) -> int:
    import scaffold

    print(scaffold.aprovar(Path(args.plano), args.dry_run))
    return OK


def _proxima_unidade(args: argparse.Namespace) -> int:
    import numeracao

    print(numeracao.proxima_unidade(args.dir_plano))
    return OK


def _lint_unidade(args: argparse.Namespace) -> int:
    import lint_unidade

    status = OK
    for arquivo in args.arquivos:
        problemas = lint_unidade.lint(Path(arquivo))
        for problema in problemas:
            print(f"{arquivo}: {problema}")
        if problemas:
            status = REPROVADO
        else:
            print(f"{arquivo}: ok")
    return status


def _lint_plano(args: argparse.Namespace) -> int:
    import lint_plano

    status = OK
    for arquivo in args.arquivos:
        problemas = lint_plano.lint(Path(arquivo))
        for problema in problemas:
            print(f"{arquivo}: {problema}")
        if problemas:
            status = REPROVADO
        else:
            print(f"{arquivo}: ok")
    return status


def _projetar_backlog(args: argparse.Namespace) -> int:
    import backlog

    miolo, situacao = backlog.projetar(Path(args.alvo), args.dry_run)
    print(f"situação: {situacao}")
    if args.dry_run:
        # Fora do dry-run o backlog já está no plano; só nele a saída precisa trazê-lo.
        for linha in miolo.splitlines():
            print(linha)
    return OK


def _ler_secoes_do_handoff(texto: str) -> dict[str, str]:
    """As três seções do stdin, por parâmetro de `handoff.gerar` — `ValueError` se falta ou repete uma.

    Só os três títulos exatos delimitam; qualquer outra linha, `## ` incluído, é conteúdo da seção
    corrente. O que vem antes da primeira seção é descartado.
    """
    secoes: dict[str, list[str]] = {}
    atual: str | None = None
    for linha in texto.splitlines():
        parametro = _SECOES_HANDOFF.get(linha.rstrip())
        if parametro is None:
            if atual is not None:
                secoes[atual].append(linha)
            continue
        if parametro in secoes:
            raise ValueError(f"seção repetida no stdin — {linha.rstrip()}")
        secoes[parametro] = []
        atual = parametro

    ausentes = [titulo for titulo, parametro in _SECOES_HANDOFF.items() if parametro not in secoes]
    if ausentes:
        raise ValueError(f"stdin sem a(s) seção(ões): {', '.join(ausentes)}")
    return {parametro: "\n".join(linhas).strip() for parametro, linhas in secoes.items()}


def _handoff(args: argparse.Namespace) -> int:
    import handoff

    if sys.stdin.isatty():
        raise ValueError(f"handoff lê do stdin as seções {', '.join(_SECOES_HANDOFF)}")
    secoes = _ler_secoes_do_handoff(sys.stdin.read())
    print(handoff.gerar(Path(args.dir_plano), **secoes))
    return OK


def _verificar(args: argparse.Namespace) -> int:
    import verificacao

    estado, _, saida = verificacao.verificar_com_saida(Path(args.unidade), args.dry_run)
    print(f"estado: {estado}")
    if estado == "verified":
        return OK
    # Sem o motivo, `spec` é um veredito sem diagnóstico — e o executor só chega ao teste por aqui.
    linhas = saida.splitlines()
    if not linhas:
        print("saída do teste: vazia")
    elif len(linhas) > _LINHAS_DE_SAIDA:
        print(f"saída do teste cortada: últimas {_LINHAS_DE_SAIDA} de {len(linhas)} linhas")
        linhas = linhas[-_LINHAS_DE_SAIDA:]
    else:
        print("saída do teste:")
    for linha in linhas:
        print(linha)
    return REPROVADO


def _normas(args: argparse.Namespace) -> int:
    import normas

    resolvidas, nao_resolvidas = normas.resolver(Path(args.unidade))
    if not (resolvidas or nao_resolvidas):
        print("nenhuma norma citada")
    vistas: set[tuple[Path, str]] = set()
    for entrada in resolvidas:
        # Linhas diferentes da tabela podem citar a mesma seção; o conteúdo vem uma vez só.
        if (entrada.arquivo, entrada.secao) in vistas:
            continue
        vistas.add((entrada.arquivo, entrada.secao))
        print(f"### {os.path.relpath(entrada.arquivo)} § {entrada.secao}")
        print(entrada.trecho)
        print()
    if nao_resolvidas:
        print("Não resolvidas:")
        for item in nao_resolvidas:
            print(f"{item.linha} — {item.motivo}")
    return OK


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="dc.py",
        description="Ponto de entrada único dos scripts do método decode-and-code. "
        "Rode a partir do diretório do projeto.",
        epilog="Saída: texto simples, um item por linha.\n"
        "Código 0 = ok ou aprovado; 1 = problema ou reprovação; 2 = erro de uso ou exceção "
        "(mensagem em stderr).",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    sub = parser.add_subparsers(dest="comando", required=True, metavar="<subcomando>")

    def comando(nome: str, ajuda: str, handler) -> argparse.ArgumentParser:
        p = sub.add_parser(nome, help=ajuda, description=ajuda)
        p.set_defaults(handler=handler)
        return p

    p = comando("validar-nome", "valida a sintaxe de um nome de plano ou unidade (1 se inválido)", _validar_nome)
    p.add_argument("nome")

    p = comando(
        "concorrencia",
        "linhas de _planos.md em desenvolvimento no mesmo core ou módulo do plano "
        "(1 se há conflito ou se o plano não declara core)",
        _concorrencia,
    )
    p.add_argument("plano")

    p = comando("bootstrap", "cria a estrutura mínima do método num projeto, sem sobrescrever", _bootstrap)
    p.add_argument("projeto", nargs="?", default=".", help="padrão: o diretório atual")

    p = comando("aprovar", "aprova um plano do _inbox: numera, move e registra em _planos.md", _aprovar)
    p.add_argument("plano")
    p.add_argument("--dry-run", action="store_true", help="só calcula o alvo, sem escrever")

    p = comando("proxima-unidade", "próximo número de unidade livre no diretório do plano", _proxima_unidade)
    p.add_argument("dir_plano")

    p = comando("lint-unidade", "gate de entrada de unidade(s) (1 se alguma tem problema)", _lint_unidade)
    p.add_argument("arquivos", nargs="+", metavar="arquivo")

    p = comando("lint-plano", "formato de plano(s) pelo porte que declaram (1 se algum tem problema)", _lint_plano)
    p.add_argument("arquivos", nargs="+", metavar="plano")

    p = comando("projetar-backlog", "projeta o backlog do plano e a situação em _planos.md", _projetar_backlog)
    p.add_argument("alvo", help="diretório ou arquivo do plano")
    p.add_argument("--dry-run", action="store_true", help="não escreve; mostra também o backlog projetado")

    p = comando(
        "handoff",
        "grava o _handoff.md do plano; lê do stdin as seções '## Fila', '## Pendências' e '## Sugestão'",
        _handoff,
    )
    p.add_argument("dir_plano")

    p = comando("verificar", "roda o teste da unidade e projeta state/verified_at (1 se não verified, mostrando a saída do teste)", _verificar)
    p.add_argument("unidade")
    p.add_argument("--dry-run", action="store_true", help="roda o teste sem gravar estado")

    p = comando(
        "normas",
        "imprime o conteúdo das seções que a unidade cita em 'Normas aplicáveis' e lista, sob "
        "'Não resolvidas:', as linhas que não resolveu (0 sempre que a unidade tem a seção)",
        _normas,
    )
    p.add_argument("unidade")

    return parser


def main(argv: list[str] | None = None) -> int:
    args = _parser().parse_args(argv)
    try:
        return args.handler(args)
    except Exception as erro:  # contrato: exceção vira código 2 e mensagem, nunca traceback
        print(f"erro: {type(erro).__name__}: {erro}", file=sys.stderr)
        return ERRO


if __name__ == "__main__":
    sys.exit(main())
