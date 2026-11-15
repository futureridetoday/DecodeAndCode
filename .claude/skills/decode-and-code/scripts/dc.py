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
import json
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


def _ler_json_do_stdin(comando: str, chaves: tuple[str, ...]) -> dict:
    """Objeto JSON do stdin com `chaves` — `ValueError`/`KeyError` (código 2) se vazio ou incompleto."""
    texto = "" if sys.stdin.isatty() else sys.stdin.read()
    if not texto.strip():
        raise ValueError(f"{comando} lê do stdin um objeto JSON com {', '.join(chaves)}")
    dados = json.loads(texto)
    if not isinstance(dados, dict):
        raise ValueError(f"{comando}: o stdin precisa ser um objeto JSON")
    ausentes = [chave for chave in chaves if chave not in dados]
    if ausentes:
        raise KeyError(f"{comando}: faltam no stdin {', '.join(ausentes)}")
    return dados


def _criar_guideline(args: argparse.Namespace) -> int:
    import lib
    import rules

    dados = _ler_json_do_stdin("criar-guideline", ("nome", "descricao", "paths", "corpo"))
    try:
        alvo = rules.criar_guideline(
            lib.repo_root(), dados["nome"], dados["descricao"], dados["paths"], dados["corpo"],
            aguardando=bool(dados.get("aguardando", False)),
        )
    except (ValueError, FileExistsError) as erro:
        print(erro)
        return REPROVADO
    print(alvo)
    return OK


def _adicionar_guardrail(args: argparse.Namespace) -> int:
    import guardrail
    import lib

    dados = _ler_json_do_stdin("adicionar-guardrail", ("regra", "proibido", "permitido"))
    try:
        alvo = guardrail.adicionar(lib.repo_root(), dados["regra"], dados["proibido"], dados["permitido"])
    except ValueError as erro:
        print(erro)
        return REPROVADO
    print(alvo)
    return OK


def _lint_guardrails(args: argparse.Namespace) -> int:
    import guardrail
    import lib

    arquivo = lib.repo_root() / ".claude" / "guardrails.json"
    problemas = guardrail.lint_arquivo(arquivo)
    for problema in problemas:
        print(f"{arquivo}: {problema}")
    if not problemas:
        print(f"{arquivo}: ok")
    return REPROVADO if problemas else OK


# Huddle por pessoa — plano 0008, T4. Todos resolvem o arquivo de quem está na sessão.

# Prefixos das subseções da seção *Huddle* que o `huddle-fecho` imprime (gatilhos e momento).
_SECOES_DO_FECHO = ("Despejo", "Momento")


def _pessoa() -> tuple[Path, str, Path]:
    """`(raiz, usuario, arquivo)` de quem está na sessão — `ValueError` sem `user.name` no git."""
    import huddle
    import lib

    raiz = lib.repo_root()
    usuario = huddle.usuario(raiz)
    return raiz, usuario, huddle.caminho(raiz, usuario)


def _ler_texto_do_stdin(comando: str) -> str:
    texto = "" if sys.stdin.isatty() else sys.stdin.read()
    if not texto.strip():
        raise ValueError(f"{comando} lê o texto do stdin")
    return texto


def _huddle_iniciar(args: argparse.Namespace) -> int:
    import huddle

    raiz, usuario, arquivo = _pessoa()
    criado = huddle.iniciar(arquivo, projeto=raiz, usuario=usuario)
    print(criado if criado else f"já existe: {arquivo}")
    return OK


def _huddle_abrir(args: argparse.Namespace) -> int:
    import huddle

    _, usuario, arquivo = _pessoa()
    texto = _ler_texto_do_stdin("huddle-abrir")
    try:
        print(huddle.abrir(arquivo, args.tipo, texto, args.autor or usuario))
    except ValueError as erro:
        print(erro)
        return REPROVADO
    return OK


def _huddle_fechar(args: argparse.Namespace) -> int:
    import huddle

    _, _, arquivo = _pessoa()
    try:
        huddle.fechar(arquivo, args.id, args.destino)
    except ValueError as erro:
        print(erro)
        return REPROVADO
    print(f"{args.id} fechada")
    return OK


def _huddle_concluir(args: argparse.Namespace) -> int:
    import huddle
    from datetime import date

    _, _, arquivo = _pessoa()
    data = args.data or date.today().isoformat()
    huddle.concluir(arquivo, data)
    print(f"last_huddle: {data}")
    return OK


def _huddle_pauta(args: argparse.Namespace) -> int:
    import huddle

    _, _, arquivo = _pessoa()
    if not arquivo.exists():
        print(f"sem huddle: {arquivo}")
        return OK
    pauta = huddle.pauta(arquivo, args.desde)
    print(f"## Abertas ({len(pauta['abertas'])})")
    for aberta in pauta["abertas"]:
        primeira = next((l for l in aberta["texto"].splitlines() if l.strip()), "")
        print(f"- {aberta['id']} · {aberta['tipo']} · {aberta['data']} · {primeira}")
    print(f"\n## Commits desde {pauta['desde']} ({len(pauta['commits'])})")
    for commit in pauta["commits"]:
        print(f"- {commit}")
    if pauta["omitidos"]:
        print(f"- … e mais {pauta['omitidos']} omitidos")
    if pauta["aviso"]:
        print(f"\naviso: {pauta['aviso']}")
    return OK


def _huddle_fecho(args: argparse.Namespace) -> int:
    """Imprime as subseções de gatilhos e de momento da seção *Huddle*: da norma do projeto, ou da
    do pacote quando a do projeto é anterior a elas (`L-05`), na ordem de `bootstrap._fonte_norma`."""
    import bootstrap
    import lib
    import normas

    candidatas = [lib.plan_root() / "system" / "modelo-dev-units.md"]
    try:
        candidatas.append(bootstrap._fonte_norma())
    except FileNotFoundError:
        pass
    for norma in candidatas:
        achados = [normas._buscar(norma, nome) for nome in _SECOES_DO_FECHO]
        if all(isinstance(a, tuple) for a in achados):
            for titulo, trecho in achados:
                print(f"### {os.path.relpath(norma)} § {titulo}")
                print(trecho)
                print()
            return OK
    raise ValueError(f"seções {_SECOES_DO_FECHO} não encontradas em {[str(c) for c in candidatas]}")


def _huddle_lint(args: argparse.Namespace) -> int:
    import huddle

    _, _, arquivo = _pessoa()
    problemas = huddle.lint_arquivo(arquivo)
    for problema in problemas:
        print(f"{arquivo}: {problema}")
    if not problemas:
        print(f"{arquivo}: ok")
    return REPROVADO if problemas else OK


def _huddle_lint_relatorio(args: argparse.Namespace) -> int:
    import huddle

    _, _, arquivo = _pessoa()
    problemas = huddle.lint_relatorio(_ler_texto_do_stdin("huddle-lint-relatorio"), arquivo=arquivo)
    for problema in problemas:
        print(problema)
    if not problemas:
        print("ok")
    return REPROVADO if problemas else OK


def _huddle_migrar(args: argparse.Namespace) -> int:
    import huddle

    raiz, usuario, _ = _pessoa()
    destino = huddle.migrar(raiz, usuario)
    print(destino if destino else "nada a migrar")
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

    comando(
        "criar-guideline",
        "grava e registra uma guideline em .claude/rules/; lê do stdin JSON "
        "{nome, descricao, paths, corpo[, aguardando]} (1 se reprovada)",
        _criar_guideline,
    )

    comando(
        "adicionar-guardrail",
        "acrescenta uma regra a .claude/guardrails.json provada pelo par; lê do stdin JSON "
        "{regra, proibido, permitido} (1 se reprovada)",
        _adicionar_guardrail,
    )

    comando("lint-guardrails", "valida .claude/guardrails.json do projeto (1 se tem problema)", _lint_guardrails)

    comando("huddle-iniciar", "cria o arquivo de huddle de quem está na sessão, sem sobrescrever", _huddle_iniciar)

    p = comando(
        "huddle-abrir",
        "abre uma entrada no huddle da pessoa e imprime o H-XX; lê o texto do stdin (1 se recusada)",
        _huddle_abrir,
    )
    p.add_argument("tipo")
    p.add_argument("--autor", help="padrão: a pessoa da sessão")

    p = comando("huddle-fechar", "fecha uma entrada aberta com o destino (1 se o id não está aberto)", _huddle_fechar)
    p.add_argument("id")
    p.add_argument("destino")

    p = comando("huddle-concluir", "grava a data do huddle em last_huddle", _huddle_concluir)
    p.add_argument("--data", help="padrão: hoje")

    p = comando("huddle-pauta", "abertas da pessoa e commits desde o último huddle", _huddle_pauta)
    p.add_argument("--desde", help="padrão: last_huddle, ou created")

    comando("huddle-fecho", "imprime os gatilhos e o momento do huddle, da norma", _huddle_fecho)

    comando("huddle-lint", "valida o arquivo de huddle da pessoa (1 se tem problema)", _huddle_lint)

    comando(
        "huddle-lint-relatorio",
        "confere a linha de fecho do relatório no stdin contra o huddle da pessoa (1 se reprovada)",
        _huddle_lint_relatorio,
    )

    comando("huddle-migrar", "move o huddle único de projeto para o arquivo da pessoa", _huddle_migrar)

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
