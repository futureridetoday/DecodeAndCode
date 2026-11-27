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
`verified`); `2` para erro de uso ou exceção, com a
mensagem em stderr e sem traceback. Fora de `verified`, `verificar` acrescenta o motivo: a saída do
teste, cortada nas últimas 80 linhas (e dizendo que cortou). `normas` sai `0` mesmo com linhas não
resolvidas: elas vão na saída, sob `Não resolvidas:`, para o executor relatar.
"""

from __future__ import annotations

import argparse
import json
import os
import re
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


def _entrada_code(args: argparse.Namespace) -> int:
    import entrega

    problemas = entrega.entrada(Path(args.alvo))
    for problema in problemas:
        print(problema)
    if not problemas:
        print("ok")
    return REPROVADO if problemas else OK


def _aprovar_entrega(args: argparse.Namespace) -> int:
    import entrega

    print(entrega.aprovar(Path(args.alvo), args.por, args.data))
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


def _guidelines_aplicaveis(args: argparse.Namespace) -> int:
    import lib
    import normas

    achadas = normas.aplicaveis(Path(args.unidade), lib.repo_root())
    linhas = [a.linha for a in achadas if a.linha]
    avisos = [a for a in achadas if a.aviso]
    if not achadas:
        print("nenhuma guideline casa os arquivos da unidade")
    for linha in linhas:
        print(linha)
    if avisos:
        print("Avisos:")
        for a in avisos:
            print(f"{a.nome} — {a.aviso}")
    return OK


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
            aguardando=bool(dados.get("aguardando", False)), replace=args.replace,
        )
    except (ValueError, FileExistsError) as erro:
        print(erro)
        return REPROVADO
    print(alvo)
    return OK


def _criar_principio(args: argparse.Namespace) -> int:
    import lib
    import rules

    dados = _ler_json_do_stdin("criar-principio", ("nome", "enunciado", "teste"))
    try:
        alvo = rules.criar_principio(
            lib.repo_root(), dados["nome"], dados["enunciado"], dados["teste"],
            descricao=str(dados.get("descricao", "")), replace=args.replace,
        )
    except ValueError as erro:
        print(erro)
        return REPROVADO
    print(alvo)
    return OK


def _adicionar_guardrail(args: argparse.Namespace) -> int:
    import guardrail
    import lib

    dados = _ler_json_do_stdin("adicionar-guardrail", ("regra", "proibido", "permitido"))
    try:
        alvo = guardrail.adicionar(
            lib.repo_root(), dados["regra"], dados["proibido"], dados["permitido"], replace=args.replace
        )
    except ValueError as erro:
        print(erro)
        return REPROVADO
    print(alvo)
    return OK


# Editar, arquivar e restaurar — plano 0020, norma *Camada normativa → Editar e arquivar*.

_CAMADAS = ("principle", "guideline", "guardrail")


def _quem_decide(raiz: Path) -> str:
    """`git config user.name` como está — `ValueError` com a instrução quando falta (`huddle.usuario`)."""
    import subprocess

    import huddle

    huddle.usuario(raiz)
    return subprocess.run(
        ["git", "config", "user.name"], cwd=raiz, capture_output=True, text=True
    ).stdout.strip()


def _archive(args: argparse.Namespace) -> int:
    import guardrail
    import lib
    import rules

    raiz = lib.repo_root()
    motivo = "" if sys.stdin.isatty() else sys.stdin.read()
    if not motivo.strip():
        print("archive lê o motivo do stdin, e ele é obrigatório")
        return REPROVADO
    arquivar = {
        "principle": rules.archive_principle,
        "guideline": rules.archive_guideline,
        "guardrail": guardrail.archive,
    }[args.camada]
    try:
        alvo = arquivar(raiz, args.nome, motivo, _quem_decide(raiz))
    except ValueError as erro:
        print(erro)
        return REPROVADO
    print(alvo)
    return OK


def _restore(args: argparse.Namespace) -> int:
    import guardrail
    import lib
    import rules

    raiz = lib.repo_root()
    if args.camada == "guardrail":
        # Fora do `try`: stdin vazio ou incompleto é erro de uso, código 2, como nos outros comandos.
        dados = _ler_json_do_stdin("restore guardrail", ("proibido", "permitido"))
    try:
        if args.camada == "guardrail":
            alvo = guardrail.restore(raiz, args.nome, dados["proibido"], dados["permitido"])
        elif args.camada == "principle":
            alvo = rules.restore_principle(raiz, args.nome)
        else:
            alvo = rules.restore_guideline(raiz, args.nome)
    except ValueError as erro:
        print(erro)
        return REPROVADO
    print(alvo)
    return OK


def _rethink_start(args: argparse.Namespace) -> int:
    import lib
    import rethink

    dados = _ler_json_do_stdin("rethink-start", ("mudanca",))
    raiz = lib.repo_root()
    try:
        alvo = rethink.start(raiz, str(dados["mudanca"]), _quem_decide(raiz))
    except ValueError as erro:
        print(erro)
        return REPROVADO
    print(alvo)
    return OK


def _rethink_record(args: argparse.Namespace) -> int:
    import lib
    import rethink

    dados = _ler_json_do_stdin("rethink-record", ("camada", "nome", "decisao", "motivo"))
    try:
        rethink.record(lib.repo_root(), dados["camada"], str(dados["nome"]), dados["decisao"], str(dados["motivo"]))
    except ValueError as erro:
        print(erro)
        return REPROVADO
    print(f"registrada: {dados['camada']} {dados['nome']} {dados['decisao']}")
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

# A seção do codex que o `huddle-fecho` imprime: os gatilhos de quando registrar e o fecho da etapa.
_SECOES_DO_FECHO = ("Huddle",)


def _pessoa() -> tuple[Path, str, Path]:
    """`(raiz, usuario, arquivo)` de quem está na sessão — `ValueError` sem `user.name` no git."""
    import huddle
    import lib

    raiz = lib.repo_root()
    usuario = huddle.usuario(raiz)
    return raiz, usuario, huddle.caminho(raiz, usuario)


def _log_resolver(args: argparse.Namespace) -> int:
    """Apaga o `E-XX` com o destino que o resolveu (plano 0018, `D-08`, `D-15`)."""
    import re

    import eventos
    import huddle
    import lib

    abertas = None
    if args.destino.strip().startswith("H-"):
        _, _, arquivo = _pessoa()
        texto = arquivo.read_text(encoding="utf-8") if arquivo.is_file() else ""
        abertas = set(re.findall(r"(?m)^###\s+(H-\d+)\b", huddle._secao(texto, "Abertas") or ""))
    raiz = lib.repo_root()
    motivo = eventos.resolver(raiz, args.id, args.destino, abertas)
    if motivo:
        print(motivo)
        return REPROVADO
    if args.destino.strip() == eventos.METODO:
        # O `E-XX` não se reusa, então só um `M-XX` nasce dele (plano 0019, `D-05`).
        id_metodo = next((m["id"] for m in eventos.metodos(raiz) if m["origem"] == args.id), "?")
        print(f"{args.id} resolvido: {eventos.METODO}: {id_metodo} — revise com metodo-listar antes de levar")
        return OK
    print(f"{args.id} resolvido: {args.destino.strip()}")
    return OK


def _metodo_listar(args: argparse.Namespace) -> int:
    """Cada `M-XX` pendente, inteiro, para a pessoa revisar antes de levar (plano 0019, `D-06`)."""
    import eventos
    import lib

    pendentes = eventos.metodos(lib.repo_root())
    if not pendentes:
        print("nenhum M-XX pendente")
        return OK
    for i, metodo in enumerate(pendentes):
        if i:
            print()
        print(f"=== {metodo['id']} · {metodo['arquivo'].relative_to(lib.repo_root())}")
        print(metodo["arquivo"].read_text(encoding="utf-8").rstrip())
    return OK


def _metodo_levado(args: argparse.Namespace) -> int:
    """Apaga o `M-XX` que a pessoa levou ao repositório do método, com o lugar (plano 0019, `D-04`)."""
    import eventos
    import lib

    motivo = eventos.levado(lib.repo_root(), args.id, args.onde)
    if motivo:
        print(motivo)
        return REPROVADO
    print(f"{args.id} levado: {' '.join(args.onde.split())}")
    return OK


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
        print(huddle.abrir(arquivo, args.tipo, texto, args.autor or usuario, evidencia=args.evidencia))
    except ValueError as erro:
        print(erro)
        return REPROVADO
    return OK


def _huddle_fechar(args: argparse.Namespace) -> int:
    import eventos
    import huddle

    raiz, _, arquivo = _pessoa()
    if args.destino.strip() == eventos.METODO:
        return _fechar_para_metodo(raiz, arquivo, args.id)
    try:
        huddle.fechar(arquivo, args.id, args.destino)
    except ValueError as erro:
        print(erro)
        return REPROVADO
    print(f"{args.id} fechada")
    return OK


def _fechar_para_metodo(raiz: Path, arquivo: Path, h_id: str) -> int:
    """`huddle-fechar <H-XX> método` (plano 0019, `D-06`): o texto genérico vem do stdin, já
    aprovado na conversa; o `M-XX` é gravado antes, e a entrada só fecha se ele existir."""
    import eventos
    import huddle

    texto = "" if sys.stdin.isatty() else sys.stdin.read()
    if not texto.strip():
        print(f"{h_id} não fechada: '{eventos.METODO}' lê do stdin o texto genérico, sem nada do projeto")
        return REPROVADO
    try:
        aberta = huddle.entrada(arquivo, h_id)
    except (ValueError, OSError):
        print(f"{h_id} não está em '## Abertas'")
        return REPROVADO
    id_metodo = eventos.registrar_metodo(raiz, h_id, texto, aberta["evidencia"])
    if id_metodo is None:
        print(f"{h_id} não fechada: não foi possível gravar o M-XX em {eventos.dir_log(raiz) / 'metodo'}")
        return REPROVADO
    try:
        huddle.fechar(arquivo, h_id, f"{eventos.METODO}: {id_metodo}")
    except ValueError as erro:
        (eventos.dir_log(raiz) / "metodo" / f"{id_metodo}.md").unlink(missing_ok=True)
        print(erro)
        return REPROVADO
    print(f"{h_id} fechada: {eventos.METODO}: {id_metodo} — revise com metodo-listar antes de levar")
    return OK


def _huddle_concluir(args: argparse.Namespace) -> int:
    import huddle
    from datetime import date

    raiz, _, arquivo = _pessoa()
    data = args.data or date.today().isoformat()
    huddle.concluir(arquivo, data)
    print(f"last_huddle: {data}")
    _consumir_log(raiz)
    return OK


def _consumir_log(raiz: Path) -> None:
    """Apaga os eventos até a última `huddle-pauta` — o que a conversa já leu (plano 0018, `D-08`)."""
    import eventos

    lidos = eventos.eventos(raiz)
    marcas = [i for i, e in enumerate(lidos) if e.get("classe") == "comando" and e.get("comando") == ["huddle-pauta"]]
    if marcas:
        saiu = eventos.consumir(raiz, marcas[-1] + 1)
        print(f"log: {saiu} evento(s) lido(s) na pauta, apagado(s)")


def _resumo_log(raiz: Path, desde: str) -> list[str]:
    """As linhas de log da pauta: contagem por classe desde `desde` e os `E-XX` abertos (plano 0018)."""
    from collections import Counter
    from datetime import date

    import eventos

    contagem: Counter = Counter()
    for e in eventos.eventos(raiz):
        if str(e.get("data", ""))[:10] < desde:
            continue
        classe = e.get("classe")
        if classe == "comando":
            nome = (e.get("comando") or ["?"])[0]
            contagem[f"comando {nome}" + (f", saída {e.get('codigo')}" if e.get("codigo") else "")] += 1
        elif classe == "bloqueio":
            contagem[f"bloqueio {e.get('regra')}"] += 1
    atrasados = set(eventos.atrasados(raiz, date.today()))
    linhas = [f"- {chave}: {n}" for chave, n in sorted(contagem.items())]
    linhas += [
        f"- {id_erro} aberto desde {data[:10]}" + (f" — há {eventos.ALARME_DIAS} dias ou mais" if id_erro in atrasados else "")
        for id_erro, data in eventos.erros(raiz)
    ]
    linhas += [
        f"- {m['id']} (de {m['origem']}) pendente desde {m['data'][:10]} — leve-o e rode metodo-levado"
        for m in eventos.metodos(raiz)
    ]
    return linhas


def _huddle_pauta(args: argparse.Namespace) -> int:
    import huddle

    raiz, _, arquivo = _pessoa()
    if not arquivo.exists():
        print(f"sem huddle: {arquivo}")
        return OK
    pauta = huddle.pauta(arquivo, args.desde)
    log = _resumo_log(raiz, pauta["desde"])
    if log:
        print(f"## Log desde {pauta['desde']}")
        print("\n".join(log))
        print()
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
    """Imprime a seção *Huddle* do codex do pacote — quando Claude registra e o que declara no fim
    da etapa. O codex nunca é copiado ao projeto (K-12), então a fonte é sempre o pacote."""
    for titulo in _SECOES_DO_FECHO:
        _imprimir_secao_do_codex(titulo)
    return OK


# Seções do codex que explicam o método por inteiro, para o `explicar` sem argumento.
_SECOES_DO_METODO = ("Workflow", "Decode", "Porte", "Cold-start")

# `explicar <seção>`: as seções do codex que o setup, o rethink e o huddle leem, pelo título.
_SECOES_AVULSAS = {
    "huddle": ("Huddle",),
    "camada-normativa": ("Princípio", "Guideline", "Guardrail"),
    "rethink": ("Rethink",),
    "setup": ("Setup",),
}

# `explicar <nome>` que imprime um procedimento compartilhado, e não o codex (K-13).
_PROCEDIMENTOS = {
    # O que o setup, o rethink e o huddle compartilham (plano 0020, `D-07`, `L-06`).
    "conversa": "suggestion-conversation.md",
}


def _imprimir_secao_do_codex(titulo: str) -> None:
    import normas

    capitulo, trecho = normas.secao_do_codex(titulo)
    print(f"### codex/{capitulo.name} § {titulo}")
    print(trecho)
    print()


def _codex(args: argparse.Namespace) -> int:
    """Imprime as seções do codex pelo título exato, na ordem pedida — o que cada skill lê do método."""
    for titulo in args.titulos:
        _imprimir_secao_do_codex(titulo)
    return OK


def _explicar(args: argparse.Namespace) -> int:
    """Imprime, do codex do pacote, as seções que explicam Decode → Code, a seção nomeada em
    `secao`, ou o procedimento compartilhado com esse nome."""
    import normas

    if args.secao in _PROCEDIMENTOS:
        arquivo = normas.procedimentos_dir() / _PROCEDIMENTOS[args.secao]
        texto = arquivo.read_text(encoding="utf-8")
        corpo = re.sub(r"\A---\n.*?\n---\n", "", texto, count=1, flags=re.S).strip()
        print(f"### procedures/{arquivo.name}")
        print(corpo)
        print()
        return OK
    nomes = _SECOES_AVULSAS[args.secao] if args.secao else _SECOES_DO_METODO
    for titulo in nomes:
        _imprimir_secao_do_codex(titulo)
    return OK


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


def _setup_escopo(args: argparse.Namespace) -> int:
    import escopo
    import lib

    projeto = lib.repo_root()
    if args.aplicar:
        escreveu = escopo.habilitar(projeto)
        print("habilitado" if escreveu else "já estava habilitado")
        return OK
    estado = escopo.estado(projeto)
    print(f"habilitado: {str(estado['habilitado']).lower()}")
    print(f"marketplace: {str(estado['marketplace']).lower()}")
    return OK


# Registro do setup — plano 0009, unidade 01. Todos resolvem `<plan_root>/system/setup.md` do projeto.


def _setup_arquivo() -> Path:
    import lib
    import setup

    return setup.caminho(lib.repo_root())


def _setup_existente(comando: str) -> Path:
    arquivo = _setup_arquivo()
    if not arquivo.is_file():
        raise FileNotFoundError(f"{comando}: {arquivo} não existe — rode `dc.py setup-iniciar`")
    return arquivo


def _setup_iniciar(args: argparse.Namespace) -> int:
    import lib
    import setup

    criado = setup.iniciar(lib.repo_root())
    print(criado if criado else f"já existe: {_setup_arquivo()}")
    return OK


def _setup_perfil(args: argparse.Namespace) -> int:
    import setup

    dados = _ler_json_do_stdin("setup-perfil", ("objetivo", "escopo", "stack", "confirmacao"))
    arquivo = _setup_existente("setup-perfil")
    try:
        setup.perfil(arquivo, dados["objetivo"], dados["escopo"], dados["stack"], dados["confirmacao"])
    except ValueError as erro:
        print(erro)
        return REPROVADO
    print(f"perfil gravado: {arquivo}")
    return OK


def _setup_registrar(args: argparse.Namespace) -> int:
    import setup

    dados = _ler_json_do_stdin("setup-registrar", ("chave", "tipo", "origem", "resultado", "detalhe"))
    arquivo = _setup_existente("setup-registrar")
    try:
        setup.registrar(
            arquivo, dados["chave"], dados["tipo"], dados["origem"], dados["resultado"], dados["detalhe"]
        )
    except ValueError as erro:
        print(erro)
        return REPROVADO
    print(f"registrada: {dados['chave']}")
    return OK


def _setup_decididas(args: argparse.Namespace) -> int:
    import setup

    for chave in setup.decididas(_setup_existente("setup-decididas")):
        print(chave)
    return OK


def _setup_concluir(args: argparse.Namespace) -> int:
    import setup
    from datetime import date

    arquivo = _setup_existente("setup-concluir")
    data = args.data or date.today().isoformat()
    try:
        setup.concluir(arquivo, data)
    except ValueError as erro:
        print(erro)
        return REPROVADO
    print(f"completed_at: {data}")
    return OK


def _setup_lint(args: argparse.Namespace) -> int:
    import setup

    arquivo = _setup_existente("setup-lint")
    problemas = setup.lint(arquivo)
    for problema in problemas:
        print(f"{arquivo}: {problema}")
    if not problemas:
        print(f"{arquivo}: ok")
    return REPROVADO if problemas else OK


def _descobrir(args: argparse.Namespace) -> int:
    import descoberta
    import lib

    print(descoberta.formatar(descoberta.descobrir(lib.repo_root())))
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

    p = comando(
        "entrada-code",
        "gate de entrada do code: a unidade (ou o plano pequeno) está pronta e as anteriores aprovadas (1 se não)",
        _entrada_code,
    )
    p.add_argument("alvo")

    p = comando(
        "aprovar-entrega",
        "grava a aprovação do usuário sobre a entrega (P7); a unidade dev/plan precisa estar verified",
        _aprovar_entrega,
    )
    p.add_argument("alvo")
    p.add_argument("--por", required=True, help="quem aprova: o usuário")
    p.add_argument("--data", help="padrão: hoje")

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

    p = comando(
        "guidelines-aplicaveis",
        "imprime, pronta para 'Normas aplicáveis', a linha de cada guideline cujo paths: casa um "
        "arquivo da tabela 'Arquivos' da unidade, e sob 'Avisos:' as que não dá para citar (0 sempre)",
        _guidelines_aplicaveis,
    )
    p.add_argument("unidade")

    substituir = "troca a existente de mesmo nome, no mesmo lugar, só se a nova passar (1 se não existe)"

    p = comando(
        "criar-guideline",
        "grava e registra uma guideline em .claude/rules/; lê do stdin JSON "
        "{nome, descricao, paths, corpo[, aguardando]} (1 se reprovada)",
        _criar_guideline,
    )
    p.add_argument("--replace", action="store_true", help=substituir)

    p = comando(
        "criar-principio",
        "acrescenta um princípio a .claude/rules/principles.md, com teto de 5; lê do stdin JSON "
        "{nome, enunciado, teste[, descricao]} (1 se reprovado)",
        _criar_principio,
    )
    p.add_argument("--replace", action="store_true", help=substituir)

    p = comando(
        "adicionar-guardrail",
        "acrescenta uma regra a .claude/guardrails.json provada pelo par; lê do stdin JSON "
        "{regra, proibido, permitido} (1 se reprovada)",
        _adicionar_guardrail,
    )
    p.add_argument("--replace", action="store_true", help=substituir)

    p = comando(
        "archive",
        "move o item para .claude/archive/ com archived_at, archived_by (git user.name) e reason; lê o "
        "motivo do stdin (1 sem motivo, sem user.name ou com nome desconhecido)",
        _archive,
    )
    p.add_argument("camada", choices=_CAMADAS)
    p.add_argument("nome")

    p = comando(
        "restore",
        "devolve o item arquivado com o mesmo nome, só se passar de novo no escritor; guardrail lê do "
        "stdin JSON {proibido, permitido} (1 se não está arquivado ou não passa)",
        _restore,
    )
    p.add_argument("camada", choices=_CAMADAS)
    p.add_argument("nome")

    comando(
        "rethink-start",
        "abre a seção do rethink em <plan_root>/system/rethink.md; lê do stdin JSON {mudanca} (1 se recusado)",
        _rethink_start,
    )

    comando(
        "rethink-record",
        "acrescenta uma decisão ao rethink.md; lê do stdin JSON {camada, nome, decisao, motivo} (1 se recusada)",
        _rethink_record,
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
    p.add_argument(
        "--evidencia",
        help="origem da entrada, opcional: E-XX, L-XX, 'bloqueio: <regra>', 'gate: <comando>' ou 'revisão: <plano>'",
    )

    p = comando(
        "huddle-fechar",
        "fecha uma entrada aberta com o destino (1 se o id não está aberto); com destino 'método', "
        "lê do stdin o texto genérico e grava .claude/log/metodo/M-XX.md antes de fechar (1 sem texto)",
        _huddle_fechar,
    )
    p.add_argument("id")
    p.add_argument("destino")

    p = comando(
        "log-resolver",
        "apaga .claude/log/erros/<E-XX>.md com o destino que o resolveu: H-XX aberto no huddle da "
        "pessoa, L-XX, 'método' (grava o M-XX antes) ou 'descartado: <motivo>' (1 se recusado, sem apagar)",
        _log_resolver,
    )
    p.add_argument("id")
    p.add_argument("destino")

    comando("metodo-listar", "mostra inteiro cada .claude/log/metodo/M-XX.md pendente", _metodo_listar)

    p = comando(
        "metodo-levado",
        "apaga o M-XX levado ao repositório do método e registra onde (1 se 'onde' vazio ou o M-XX não existe)",
        _metodo_levado,
    )
    p.add_argument("id")
    p.add_argument("onde")

    p = comando("huddle-concluir", "grava a data do huddle em last_huddle", _huddle_concluir)
    p.add_argument("--data", help="padrão: hoje")

    p = comando("huddle-pauta", "abertas da pessoa e commits desde o último huddle", _huddle_pauta)
    p.add_argument("--desde", help="padrão: last_huddle, ou created")

    comando("huddle-fecho", "imprime a seção Huddle do codex: quando registrar e o fecho", _huddle_fecho)

    p = comando("codex", "imprime seções do codex pelo título exato (2 se um título não existe)", _codex)
    p.add_argument("titulos", nargs="+", metavar="título")

    p = comando(
        "explicar",
        "imprime, do codex, as seções que explicam o método, a seção nomeada ou o procedimento",
        _explicar,
    )
    p.add_argument("secao", nargs="?", choices=sorted({*_SECOES_AVULSAS, *_PROCEDIMENTOS}))

    comando("huddle-lint", "valida o arquivo de huddle da pessoa (1 se tem problema)", _huddle_lint)

    comando(
        "huddle-lint-relatorio",
        "confere a linha de fecho do relatório no stdin contra o huddle da pessoa (1 se reprovada)",
        _huddle_lint_relatorio,
    )

    comando("huddle-migrar", "move o huddle único de projeto para o arquivo da pessoa", _huddle_migrar)

    comando("descobrir", "inventaria as fontes do projeto e a norma que ele já tem, sem classificar", _descobrir)

    comando("setup-iniciar", "cria <plan_root>/system/setup.md, sem sobrescrever", _setup_iniciar)

    comando(
        "setup-perfil",
        "grava o perfil no setup.md; lê do stdin JSON {objetivo, escopo, stack, confirmacao} (1 se recusado)",
        _setup_perfil,
    )

    comando(
        "setup-registrar",
        "registra uma decisão no setup.md; lê do stdin JSON {chave, tipo, origem, resultado, detalhe} "
        "(1 se recusada)",
        _setup_registrar,
    )

    comando("setup-decididas", "lista as chaves já registradas no setup.md", _setup_decididas)

    p = comando("setup-concluir", "grava a data de conclusão do setup em completed_at", _setup_concluir)
    p.add_argument("--data", help="padrão: hoje")

    comando("setup-lint", "valida o setup.md do projeto (1 se tem problema)", _setup_lint)

    p = comando(
        "setup-escopo",
        "mostra se o plugin está habilitado no .claude/settings.json do projeto; --aplicar habilita",
        _setup_escopo,
    )
    p.add_argument("--aplicar", action="store_true", help="grava enabledPlugins e extraKnownMarketplaces")

    return parser


def _registrar(lista: list[str], codigo: int, saida: str, args: argparse.Namespace | None) -> None:
    """Evento de toda chamada e, na saída 2, o `E-XX` (plano 0018, `D-05`, `D-14`). Nunca muda o
    código nem o stderr: qualquer falha do log fica aqui."""
    try:
        import eventos
        import lib

        projeto = lib.repo_root()
        alvo = next((str(getattr(args, k)) for k in ("unidade", "plano", "dir_plano") if getattr(args, k, None)), "")
        eventos.registrar(projeto, {"classe": "comando", "comando": lista[:1], "codigo": codigo, "alvo": alvo})
        if codigo == ERRO:
            eventos.registrar_erro(projeto, lista, codigo, saida, alvo)
    except Exception:
        pass


def main(argv: list[str] | None = None) -> int:
    lista = list(sys.argv[1:] if argv is None else argv)
    try:
        args = _parser().parse_args(argv)
    except SystemExit as saida:
        if saida.code not in (0, None):  # erro de uso: o argparse já escreveu a mensagem em stderr
            _registrar(lista, ERRO, f"erro de uso do argparse: dc.py {' '.join(lista)}", None)
        raise
    try:
        codigo = args.handler(args)
    except Exception as erro:  # contrato: exceção vira código 2 e mensagem, nunca traceback
        print(f"erro: {type(erro).__name__}: {erro}", file=sys.stderr)
        import traceback

        _registrar(lista, ERRO, traceback.format_exc(), args)
        return ERRO
    _registrar(lista, codigo, "", args)
    return codigo


if __name__ == "__main__":
    sys.exit(main())
