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
_DESTINO_RE = re.compile(r"^(H-\d+|L-\d+|descartado: .*\S.*)$")


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


def _proximo_id(pasta: Path) -> str:
    contador = pasta / ".ultimo"
    try:
        ultimo = int(contador.read_text(encoding="utf-8").strip())
    except (OSError, ValueError):
        ultimo = 0
    existentes = [int(m.group(1)) for p in pasta.glob("E-*.md") if (m := _ID_RE.match(p.stem))]
    proximo = max([ultimo, *existentes]) + 1
    contador.write_text(f"{proximo}\n", encoding="utf-8")
    return f"E-{proximo:02d}"


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
        cerca = "`" * max(3, max((len(r) for r in re.findall(r"`+", fim)), default=0) + 1)
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
            "---\n"
            + "".join(f"{chave}: {json.dumps(valor, ensure_ascii=False)}\n" for chave, valor in frontmatter.items())
            + f"---\n\n# {id_erro} — saída {codigo} do dc.py\n\n"
            + f"## Saída\n\n{cerca}\n{fim}\n{cerca}\n\n## Working tree\n\n{arquivos}\n"
        )
        (pasta / f"{id_erro}.md").write_text(texto, encoding="utf-8")
        registrar(projeto, {"classe": "erro", "id": id_erro, "comando": comando[:1], "codigo": codigo}, agora)
        return id_erro
    except Exception:
        return None


def _data_do_erro(arquivo: Path) -> str:
    for linha in arquivo.read_text(encoding="utf-8").splitlines()[1:]:
        if linha.startswith("data:"):
            return json.loads(linha[len("data:"):].strip())
        if linha.strip() == "---":
            break
    return ""


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
    `L-XX` ou `descartado: <motivo>` (`D-08`, `D-15`)."""
    if not _ID_RE.match(id_erro):
        return f"id fora do formato E-XX: {id_erro!r}"
    destino = destino.strip()
    if not _DESTINO_RE.match(destino):
        return f"destino fora do vocabulário (H-XX, L-XX ou 'descartado: <motivo>'): {destino!r}"
    if destino.startswith("H-") and abertas is not None and destino not in abertas:
        return f"{destino} não está entre as abertas do huddle da pessoa"
    arquivo = dir_log(projeto) / "erros" / f"{id_erro}.md"
    if not arquivo.is_file():
        return f"erro não encontrado: {id_erro}"
    try:
        arquivo.unlink()
    except OSError as erro:
        return f"não foi possível apagar {arquivo}: {erro}"
    registrar(projeto, {"classe": "resolvido", "id": id_erro, "destino": destino})
    return None
