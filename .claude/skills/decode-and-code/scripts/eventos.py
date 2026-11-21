#!/usr/bin/env python3
"""Log de uso do método — plano 0018, primeiro item do ciclo de evolução da norma.

Mora em `<projeto>/.claude/log/`, que carrega o próprio `.gitignore` (`*`): a pasta fica fora do
git sem que nada edite o `.gitignore` do projeto (`D-04`). Só escreve em projeto com
`<plan_root>/_planos.md`, a marca do bootstrap (`D-16`): com o plugin no escopo de usuário, os
hooks rodam em todo projeto aberto, e criar a pasta num repositório que nunca adotou o método é o
efeito colateral que o `0001` recusa (*Materializar não pode ser automático*).

- `eventos.jsonl`: uma linha JSON por evento, só acréscimo, com `data` (`D-05`). Evento com mais de
  `VALIDADE_DIAS` sai na escrita seguinte, e `consumir` apaga o que a revisão do ciclo já leu
  (`D-08`).
- `erros/E-XX.md`: um por saída 2 do `dc.py` (`D-06`, `D-14`), com frontmatter e referências — o
  comando, o código, o fim da saída, o `HEAD`, o working tree e a versão do plugin. Sai só por
  `resolver`, nunca por prazo. A numeração vem de `erros/.ultimo`, que só cresce e que nada apaga.
- `metodo/M-XX.md` (plano 0019): feedback ao método, à espera de ser levado ao repositório dele.
  Nasce de `huddle-fechar <H-XX> método` ou de `resolver(<E-XX>, "método")`, com os caminhos
  absolutos trocados (`D-06`), e sai só por `levado`. Numeração em `metodo/.ultimo`.

Nenhuma função levanta para quem chama: o log nunca muda o código de saída nem a resposta de
quem o usa. `resolver` devolve o motivo da recusa em vez de levantar.
"""

from __future__ import annotations

import json
import os
import re
import subprocess
from datetime import date, datetime, timedelta
from pathlib import Path

import lib

VALIDADE_DIAS = 14
ALARME_DIAS = 7
LINHAS_DA_SAIDA = 40

_ID_RE = re.compile(r"^E-(\d+)$")
_METODO_RE = re.compile(r"^M-(\d+)$")
_DESTINO_RE = re.compile(r"^(H-\d+|L-\d+|método|descartado: .*\S.*)$")
METODO = "método"


def _agora() -> datetime:
    return datetime.now().replace(microsecond=0)


def dir_log(projeto: Path) -> Path:
    return Path(projeto) / ".claude" / "log"


def ativo(projeto: Path) -> bool:
    """Há `<plan_root>/_planos.md` no projeto — a marca do bootstrap (`D-16`)."""
    try:
        return (Path(projeto) / lib.config()["plan_root"] / "_planos.md").is_file()
    except Exception:
        return False


def _preparar(projeto: Path) -> Path:
    pasta = dir_log(projeto)
    pasta.mkdir(parents=True, exist_ok=True)
    ignora = pasta / ".gitignore"
    if not ignora.exists():
        ignora.write_text("*\n", encoding="utf-8")
    return pasta


def eventos(projeto: Path, agora: datetime | None = None) -> list[dict]:
    """Os eventos vivos, na ordem: sem os de mais de `VALIDADE_DIAS` e sem linha ilegível."""
    arquivo = dir_log(projeto) / "eventos.jsonl"
    try:
        linhas = arquivo.read_text(encoding="utf-8").splitlines()
    except (OSError, UnicodeDecodeError):
        return []
    limite = ((agora or _agora()) - timedelta(days=VALIDADE_DIAS)).isoformat()
    lidos = []
    for linha in linhas:
        try:
            evento = json.loads(linha)
        except ValueError:
            continue
        if isinstance(evento, dict) and str(evento.get("data", "")) >= limite:
            lidos.append(evento)
    return lidos


def registrar(projeto: Path, evento: dict, agora: datetime | None = None) -> None:
    """Acrescenta `evento` com `data`, numa escrita só, em modo de acréscimo. Nunca levanta.

    Só acréscimo, nunca reescrita: o `InstructionsLoaded` dispara um processo por instrução,
    vários ao mesmo tempo, e ler-filtrar-reescrever perdia eventos — medido em 2026-11-20, 4 a 6
    de 10 hooks simultâneos sobreviviam. O evento vencido some da leitura e sai no `consumir`.
    """
    try:
        if not ativo(projeto):
            return
        linha = json.dumps({"data": (agora or _agora()).isoformat(), **evento}, ensure_ascii=False) + "\n"
        descritor = os.open(_preparar(projeto) / "eventos.jsonl", os.O_WRONLY | os.O_APPEND | os.O_CREAT, 0o644)
        try:
            os.write(descritor, linha.encode("utf-8"))
        finally:
            os.close(descritor)
    except Exception:
        pass


def consumir(projeto: Path, quantos: int) -> int:
    """Apaga os `quantos` primeiros eventos vivos — o que a revisão do ciclo já leu — e, junto, os
    vencidos. Por posição, não por data: eventos do mesmo segundo ficam dos dois lados da marca.
    É a única reescrita do arquivo, e só roda no `huddle-concluir`. Devolve quantos vivos saíram.
    Nunca levanta."""
    try:
        vivos = eventos(projeto)
        quantos = max(0, min(quantos, len(vivos)))
        texto = "".join(json.dumps(e, ensure_ascii=False) + "\n" for e in vivos[quantos:])
        (_preparar(projeto) / "eventos.jsonl").write_text(texto, encoding="utf-8")
        return quantos
    except Exception:
        return 0


def _git(projeto: Path, *args: str) -> str:
    try:
        r = subprocess.run(["git", *args], cwd=projeto, capture_output=True, text=True, timeout=5)
    except (OSError, subprocess.SubprocessError):
        return ""
    return r.stdout.strip() if r.returncode == 0 else ""


def _versao_plugin() -> str:
    """`version` do manifesto: `.claude-plugin/plugin.json` no pacote, `.claude/plugin.json` na fonte."""
    raiz = Path(__file__).resolve().parents[3]
    for manifesto in (raiz / ".claude-plugin" / "plugin.json", raiz / "plugin.json"):
        try:
            return str(json.loads(manifesto.read_text(encoding="utf-8")).get("version", ""))
        except (OSError, ValueError):
            continue
    return ""


def _proximo_id(pasta: Path, prefixo: str = "E") -> str:
    contador = pasta / ".ultimo"
    try:
        ultimo = int(contador.read_text(encoding="utf-8").strip())
    except (OSError, ValueError):
        ultimo = 0
    padrao = re.compile(rf"^{prefixo}-(\d+)$")
    existentes = [int(m.group(1)) for p in pasta.glob(f"{prefixo}-*.md") if (m := padrao.match(p.stem))]
    proximo = max([ultimo, *existentes]) + 1
    contador.write_text(f"{proximo}\n", encoding="utf-8")
    return f"{prefixo}-{proximo:02d}"


def _frontmatter(campos: dict) -> str:
    return "---\n" + "".join(f"{chave}: {json.dumps(valor, ensure_ascii=False)}\n" for chave, valor in campos.items()) + "---\n"


def _cerca(texto: str) -> str:
    return "`" * max(3, max((len(r) for r in re.findall(r"`+", texto)), default=0) + 1)


def registrar_erro(
    projeto: Path, comando: list[str], codigo: int, saida: str, alvo: str = "", agora: datetime | None = None
) -> str | None:
    """Escreve o próximo `erros/E-XX.md` e registra o evento `erro`. Devolve o id, ou `None` quando
    o projeto não tem o método ou a escrita falhou. Nunca levanta."""
    try:
        if not ativo(projeto):
            return None
        agora = agora or _agora()
        pasta = _preparar(projeto) / "erros"
        pasta.mkdir(exist_ok=True)
        id_erro = _proximo_id(pasta)

        fim = "\n".join(saida.rstrip().splitlines()[-LINHAS_DA_SAIDA:])
        cerca = _cerca(fim)
        modificados = [linha[3:] for linha in _git(projeto, "status", "--porcelain").splitlines() if len(linha) > 3]
        arquivos = "\n".join(f"- [`{c}`](../../../{c})" for c in modificados) or "(nenhum)"
        frontmatter = {
            "id": id_erro,
            "data": agora.isoformat(),
            "comando": " ".join(comando),
            "codigo": codigo,
            "alvo": alvo,
            "head": _git(projeto, "rev-parse", "HEAD"),
            "versao": _versao_plugin(),
        }
        texto = (
            _frontmatter(frontmatter)
            + f"\n# {id_erro} — saída {codigo} do dc.py\n\n"
            + f"## Saída\n\n{cerca}\n{fim}\n{cerca}\n\n## Working tree\n\n{arquivos}\n"
        )
        (pasta / f"{id_erro}.md").write_text(texto, encoding="utf-8")
        registrar(projeto, {"classe": "erro", "id": id_erro, "comando": comando[:1], "codigo": codigo}, agora)
        return id_erro
    except Exception:
        return None


def _campo(arquivo: Path, chave: str) -> str:
    """Valor de `chave` no frontmatter que `_frontmatter` escreveu, ou `""`."""
    for linha in arquivo.read_text(encoding="utf-8").splitlines()[1:]:
        if linha.startswith(f"{chave}:"):
            return str(json.loads(linha[len(chave) + 1:].strip()))
        if linha.strip() == "---":
            break
    return ""


def _data_do_erro(arquivo: Path) -> str:
    return _campo(arquivo, "data")


def erros(projeto: Path) -> list[tuple[str, str]]:
    """`(id, data)` de cada `E-XX` aberto, em ordem de id. Nunca levanta."""
    try:
        pasta = dir_log(projeto) / "erros"
        achados = []
        for arquivo in pasta.glob("E-*.md"):
            m = _ID_RE.match(arquivo.stem)
            if m:
                achados.append((int(m.group(1)), arquivo.stem, _data_do_erro(arquivo)))
        return [(id_erro, data) for _, id_erro, data in sorted(achados)]
    except Exception:
        return []


def atrasados(projeto: Path, hoje: date, dias: int = ALARME_DIAS) -> list[str]:
    """Ids dos `E-XX` abertos há `dias` ou mais (`D-08`)."""
    limite = (hoje - timedelta(days=dias)).isoformat()
    return [id_erro for id_erro, data in erros(projeto) if data and data[:10] <= limite]


def resolver(projeto: Path, id_erro: str, destino: str, abertas: set[str] | None = None) -> str | None:
    """Apaga `erros/<id_erro>.md` e registra o evento `resolvido`. Devolve `None`, ou o motivo da
    recusa — e então nada é apagado. `destino` é `H-XX` (presente em `abertas`, quando dado),
    `L-XX`, `método` ou `descartado: <motivo>` (`D-08`, `D-15`).

    Com `método` (plano 0019, `D-05`), o `M-XX` é gravado a partir do `E-XX` **antes** de o apagar;
    se a gravação falhar, o `E-XX` fica. O evento leva o destino `método: M-XX`."""
    if not _ID_RE.match(id_erro):
        return f"id fora do formato E-XX: {id_erro!r}"
    destino = destino.strip()
    if not _DESTINO_RE.match(destino):
        return f"destino fora do vocabulário (H-XX, L-XX, método ou 'descartado: <motivo>'): {destino!r}"
    if destino.startswith("H-") and abertas is not None and destino not in abertas:
        return f"{destino} não está entre as abertas do huddle da pessoa"
    arquivo = dir_log(projeto) / "erros" / f"{id_erro}.md"
    if not arquivo.is_file():
        return f"erro não encontrado: {id_erro}"
    if destino == METODO:
        id_metodo = _metodo_do_erro(projeto, arquivo)
        if id_metodo is None:
            return f"não foi possível gravar o M-XX de {id_erro} — o {id_erro} continua aberto"
        destino = f"{METODO}: {id_metodo}"
    try:
        arquivo.unlink()
    except OSError as erro:
        return f"não foi possível apagar {arquivo}: {erro}"
    registrar(projeto, {"classe": "resolvido", "id": id_erro, "destino": destino})
    return None


# Feedback ao método — plano 0019.


def sem_caminhos(texto: str, projeto: Path) -> str:
    """Troca a raiz do projeto por `<projeto>` e o diretório da pessoa por `~` (`D-06`).

    Só caminho absoluto, mecanicamente: nome de plano ou trecho de código continuam no texto, e a
    pessoa os revisa no `metodo-listar` (`L-03`). O mais longo primeiro, porque o projeto costuma
    morar dentro da home; cada um na forma dada e na resolvida (`/var` e `/private/var`)."""
    trocas: dict[str, str] = {}
    for caminho, marca in ((Path.home(), "~"), (Path(projeto), "<projeto>")):
        for forma in {str(caminho), str(caminho.resolve())}:
            if len(forma) > 1:
                trocas[forma] = marca
    for forma in sorted(trocas, key=len, reverse=True):
        texto = re.sub(re.escape(forma) + r"(?![\w.-])", lambda _m, m=trocas[forma]: m, texto)
    return texto


def registrar_metodo(
    projeto: Path, origem: str, texto: str, evidencia: str = "", versao: str | None = None,
    agora: datetime | None = None,
) -> str | None:
    """Escreve o próximo `metodo/M-XX.md` e devolve o id, ou `None` quando o projeto não tem o
    método ou a escrita falhou. Nunca levanta.

    `evidencia` só entra no frontmatter quando é `E-XX` ou `L-XX` — ids sem conteúdo; as outras
    três levam nome do projeto e ficam de fora (`D-04`). O texto passa por `sem_caminhos`."""
    try:
        if not ativo(projeto):
            return None
        pasta = _preparar(projeto) / "metodo"
        pasta.mkdir(exist_ok=True)
        id_metodo = _proximo_id(pasta, "M")
        id_evidencia = re.match(r"[EL]-\d+\b", evidencia.strip())
        campos = {
            "id": id_metodo,
            "origem": origem,
            "data": (agora or _agora()).isoformat(),
            "versao": _versao_plugin() if versao is None else versao,
            "evidencia": id_evidencia.group(0) if id_evidencia else "",
        }
        corpo = sem_caminhos(texto.strip(), projeto)
        (pasta / f"{id_metodo}.md").write_text(
            _frontmatter(campos) + f"\n# {id_metodo} — de {origem}\n\n{corpo}\n", encoding="utf-8"
        )
        return id_metodo
    except Exception:
        return None


def _metodo_do_erro(projeto: Path, arquivo: Path) -> str | None:
    """O `M-XX` mecânico de um `E-XX`: o subcomando sem os argumentos, o código, o fim da saída e a
    versão. Ficam de fora o alvo, o `HEAD` e o working tree (`D-06`) — o alvo também de dentro da
    saída, onde a mensagem da exceção o repete, trocado por `<alvo>`."""
    try:
        conteudo = arquivo.read_text(encoding="utf-8")
        m = re.search(r"(?ms)^## Saída\n\n(`{3,})\n(.*?)\n\1\n", conteudo)
        saida = m.group(2) if m else ""
        alvo = _campo(arquivo, "alvo").strip()
        if alvo:
            saida = re.sub(r"(?<![\w.-])" + re.escape(alvo) + r"(?![\w.-])", "<alvo>", saida)
        subcomando = (_campo(arquivo, "comando").split() or ["?"])[0]
        cerca = _cerca(saida)
        texto = (
            f"Saída {_campo(arquivo, 'codigo')} do `dc.py {subcomando}`.\n\n"
            f"## Saída\n\n{cerca}\n{saida}\n{cerca}"
        )
        return registrar_metodo(projeto, arquivo.stem, texto, versao=_campo(arquivo, "versao"))
    except Exception:
        return None


def metodos(projeto: Path) -> list[dict]:
    """`{"id", "origem", "data", "arquivo"}` de cada `M-XX` pendente, em ordem de id. Nunca levanta."""
    try:
        achados = []
        for arquivo in (dir_log(projeto) / "metodo").glob("M-*.md"):
            m = _METODO_RE.match(arquivo.stem)
            if m:
                achados.append((int(m.group(1)), {"id": arquivo.stem, "origem": _campo(arquivo, "origem"),
                                                   "data": _campo(arquivo, "data"), "arquivo": arquivo}))
        return [dados for _, dados in sorted(achados, key=lambda par: par[0])]
    except Exception:
        return []


def levado(projeto: Path, id_metodo: str, onde: str) -> str | None:
    """Apaga `metodo/<id_metodo>.md` e registra o evento `levado` com `onde`. Devolve `None`, ou o
    motivo da recusa — e então nada é apagado. É a única saída de um `M-XX` (`D-04`)."""
    if not _METODO_RE.match(id_metodo):
        return f"id fora do formato M-XX: {id_metodo!r}"
    onde = " ".join(onde.split())
    if not onde:
        return "diga onde o M-XX foi levado: o H-XX, o L-XX ou o lugar no repositório do método"
    arquivo = dir_log(projeto) / "metodo" / f"{id_metodo}.md"
    if not arquivo.is_file():
        return f"M-XX não encontrado: {id_metodo}"
    try:
        arquivo.unlink()
    except OSError as erro:
        return f"não foi possível apagar {arquivo}: {erro}"
    registrar(projeto, {"classe": "levado", "id": id_metodo, "onde": onde})
    return None
