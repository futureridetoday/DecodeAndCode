#!/usr/bin/env python3
"""Lint de invariantes de rule e guideline — unidades 0001-03, 0001-09 e 0001-11.

Dá oráculo estrutural a `.claude/rules/*.md`: afirma que o arquivo é uma rule bem formada e que
`paths:`, quando declarado, compila como glob — nunca julga se o conteúdo normativo é o certo
(`L-01` do plano — isso é humano). Mesmo padrão de `lint_unidade.lint` e `lint_skill.lint`: lista
vazia quando aprovada, frontmatter malformado vira problema na lista, nunca exceção.

`paths:` ausente é princípio; presente, cada entrada precisa compilar via `fnmatch.translate` +
`re.compile` — é a única diferença mecânica entre as duas camadas (norma, seção *Não inventar
ativação*). A validação por regex de lista (`[...]`) é deliberada: `regioes.ler_campo` não
interpreta YAML, e o formato inline já é o que o resto do frontmatter deste repositório usa
(`tags: [...]`, `dependencies: []`).

`lint_guideline` estende `lint_rule` para o caso em que `paths:` é obrigatório, não opcional: uma
guideline sem escopo, ou com escopo que não casa nada no disco, aprova a forma e nunca ativa — a
falha silenciosa que a norma nomeia em *Ativação silenciosa é o modo de falha da própria camada*.
Casamento contra o disco usa `Path.glob` a partir de `lib.repo_root()`, nunca fixture.

`auditar_arvore` dá o mesmo tratamento à árvore inteira — `.claude/rules/` e `.claude/rules-off/`
da raiz real —, e é o gate estrutural que fecha a `L-26`: um `.md` em subdiretório de `rules/`
continua carregando porque o matcher do Claude Code recursa, e nada além deste check recusava
isso antes de acontecer de novo.
"""

from __future__ import annotations

import fnmatch
import json
import re
import shutil
import tempfile
from pathlib import Path

import lib
import regioes
import registry

CAMPOS_FRONTMATTER = ("name", "description")

_PATHS_LISTA_RE = re.compile(r"^\[(.*)\]$", re.DOTALL)


def lint_rule(path: Path) -> list[str]:
    """Verifica se `path` é uma rule bem formada — lista vazia quando aprovada.

    Levanta `FileNotFoundError` se o caminho não existe. Frontmatter ausente ou malformado entra
    na lista devolvida, nunca é exceção.
    """
    texto = path.read_text(encoding="utf-8")
    corpo = _corpo(texto)

    problemas: list[str] = []
    problemas.extend(_checar_frontmatter(path))
    problemas.extend(_checar_paths(path))
    problemas.extend(_checar_corpo(corpo))
    return problemas


def _corpo(texto: str) -> str:
    """Conteúdo após o frontmatter — o texto inteiro se não houver '---' de abertura."""
    linhas = texto.splitlines()
    if not linhas or linhas[0].strip() != "---":
        return texto
    for i in range(1, len(linhas)):
        if linhas[i].strip() == "---":
            return "\n".join(linhas[i + 1 :])
    return ""


def _checar_frontmatter(path: Path) -> list[str]:
    """Exige `name` e `description` não vazios — malformado devolve problema, não exceção."""
    try:
        valores = {chave: regioes.ler_campo(path, chave) for chave in CAMPOS_FRONTMATTER}
    except ValueError:
        return ["frontmatter ausente ou malformado — sem '---' de abertura e fechamento"]

    return [
        f"campo obrigatório ausente ou vazio no frontmatter: {chave}"
        for chave, valor in valores.items()
        if not (valor and valor.strip())
    ]


def _entradas_de_paths(valor: str) -> list[str] | None:
    """Entradas de `paths: [...]` — None se a sintaxe não é uma lista `[...]`."""
    m = _PATHS_LISTA_RE.match(valor.strip())
    if m is None:
        return None
    miolo = m.group(1).strip()
    if not miolo:
        return []
    return [pedaco.strip().strip('"').strip("'") for pedaco in miolo.split(",")]


def _checar_paths(path: Path) -> list[str]:
    """`paths:` ausente é princípio, sem problema; presente exige lista de globs válidos."""
    try:
        valor = regioes.ler_campo(path, "paths")
    except ValueError:
        return []
    if valor is None:
        return []

    entradas = _entradas_de_paths(valor)
    if entradas is None:
        return [f"paths não está no formato de lista '[...]': {valor!r}"]

    problemas = []
    for entrada in entradas:
        try:
            re.compile(fnmatch.translate(entrada))
        except re.error as erro:
            problemas.append(f"paths contém glob inválido {entrada!r}: {erro}")
    return problemas


def _checar_corpo(corpo: str) -> list[str]:
    """Corpo vazio abaixo do frontmatter é falha silenciosa — a rule carrega e não diz nada."""
    if not corpo.strip():
        return ["corpo vazio — rule carrega e não diz nada"]
    return []


def lint_guideline(path: Path, raiz: Path | None = None) -> list[str]:
    """Verifica se `path` é uma guideline válida — lista vazia quando aprovada.

    Estende `lint_rule` com o que só faz sentido quando `paths:` é obrigatório: presente,
    não vazio, e casando ao menos um arquivo que existe sob `raiz` (padrão: `lib.repo_root()`).
    Formato de lista e compilação de glob já são responsabilidade de `lint_rule` — aqui não se
    repete. Com `paths_pending: true` no frontmatter, o casamento no disco é dispensado — o
    caminho ainda não existe (plano 0007, `D-08`); as demais checagens continuam.

    Mesmo contrato de `lint_rule`: levanta `FileNotFoundError` se `path` não existe.
    """
    problemas = lint_rule(path)
    problemas.extend(_checar_paths_guideline(path, raiz))
    return problemas


def _checar_paths_guideline(path: Path, raiz: Path | None = None) -> list[str]:
    """`paths:` ausente ou vazio reprova; presente, ao menos uma entrada precisa casar
    arquivo real — checado por `Path.glob` a partir de `raiz`, contra o disco, salvo
    `paths_pending: true`."""
    try:
        valor = regioes.ler_campo(path, "paths")
    except ValueError:
        return []  # frontmatter malformado — já reportado por lint_rule

    if valor is None:
        return ["guideline sem 'paths:' — isso é princípio, não guideline"]

    entradas = _entradas_de_paths(valor)
    if entradas is None:
        return []  # formato de lista inválido — já reportado por lint_rule
    if not entradas:
        return ["'paths:' presente e vazio — guideline sem escopo"]

    if (regioes.ler_campo(path, "paths_pending") or "").strip() == "true":
        return []

    raiz = raiz if raiz is not None else lib.repo_root()
    for entrada in entradas:
        try:
            if any(raiz.glob(entrada)):
                return []
        except (ValueError, NotImplementedError):
            continue  # glob que não compila — já reportado por lint_rule

    return [f"'paths:' não casa nenhum arquivo existente no repositório: {entradas!r}"]


_NOME_GUIDELINE_RE = re.compile(r"^[a-z0-9]+(-[a-z0-9]+)*$")
_CURINGA_RE = re.compile(r"[*?\[]")


def _problema_de_padrao(padrao: str) -> str | None:
    """Recusa o padrão fora do subconjunto em que o lint e o Claude Code concordam (`D-02`)."""
    if "{" in padrao or "," in padrao:
        return f"padrão com chave ou vírgula não é gerado: {padrao!r}"
    if padrao.startswith("/"):
        return f"padrão com '/' inicial — paths é relativo à raiz do projeto: {padrao!r}"
    if padrao.endswith("/**"):
        return f"padrão terminado em '/**' — a forma de pasta inteira é 'dir/**/*': {padrao!r}"
    primeiro, separador, _ = padrao.partition("/")
    if not separador or (primeiro != "**" and _CURINGA_RE.search(primeiro)):
        return f"padrão precisa começar por diretório ou por '**/': {padrao!r}"
    return None


def criar_guideline(
    raiz: Path,
    nome: str,
    descricao: str,
    paths: list[str],
    corpo: str,
    aguardando: bool = False,
) -> Path:
    """Grava `<raiz>/.claude/rules/<nome>.md` só se a guideline passar em `lint_guideline`.

    `name` e `description` vão com escape JSON, que é YAML válido; cada entrada de `paths`, entre
    aspas duplas. Com `aguardando=True`, grava `paths_pending: true` e o casamento no disco é
    dispensado (`D-08`). Levanta `ValueError` para entrada ou guideline inválida e
    `FileExistsError` se o nome já existe em `rules/` ou `rules-off/` — nos dois casos, nada fica
    no disco.
    """
    if not _NOME_GUIDELINE_RE.match(nome):
        raise ValueError(f"nome de guideline fora de kebab-case ASCII: {nome!r}")
    if not paths:
        raise ValueError("guideline sem 'paths' — isso é princípio, não guideline")
    problemas = [p for p in map(_problema_de_padrao, paths) if p]
    if problemas:
        raise ValueError("; ".join(problemas))

    dir_rules = raiz / ".claude" / "rules"
    for existente in (dir_rules / f"{nome}.md", raiz / ".claude" / "rules-off" / f"{nome}.md"):
        if existente.exists():
            raise FileExistsError(f"guideline já existe: {existente}")

    frontmatter = [
        f"name: {json.dumps(nome)}",
        f"description: {json.dumps(descricao, ensure_ascii=False)}",
        f"paths: {json.dumps(paths, ensure_ascii=False)}",
    ]
    if aguardando:
        frontmatter.append("paths_pending: true")
    texto = "---\n" + "\n".join(frontmatter) + "\n---\n\n" + corpo.strip() + "\n"

    with tempfile.TemporaryDirectory() as tmp:
        provisorio = Path(tmp) / f"{nome}.md"
        provisorio.write_text(texto, encoding="utf-8")
        problemas = lint_guideline(provisorio, raiz=raiz)
        if problemas:
            raise ValueError("; ".join(problemas))
        dir_rules.mkdir(parents=True, exist_ok=True)
        destino = dir_rules / f"{nome}.md"
        shutil.move(str(provisorio), destino)
    registry.registrar(raiz, nome)
    return destino


TETO_PRINCIPIOS = 5
_ENUNCIADO_RE = re.compile(r"(?m)^\*\*Enunciado:\*\*")
_TITULO_RE = re.compile(r"(?m)^##[ \t]+(.+?)[ \t]*$")
_DESCRICAO_PRINCIPIOS = "Princípios do projeto: como decidir. Carrega sempre, em toda sessão."


def _rules_de_principio(dir_rules: Path) -> list[Path]:
    """`.md` direto em `dir_rules` sem `paths:` — onde o teto conta (norma, *Princípio*)."""
    if not dir_rules.is_dir():
        return []
    return [p for p in sorted(dir_rules.glob("*.md")) if not registry._e_guideline(p)]


def criar_principio(raiz: Path, nome: str, enunciado: str, teste: str, descricao: str = "") -> Path:
    """Acrescenta `## <nome>`, *Enunciado* e *Teste* a `<raiz>/.claude/rules/principles.md`.

    Plano 0016. Cria o arquivo com frontmatter se faltar — `descricao` vale só aí, e vazia usa a
    padrão. O teto conta as seções com `**Enunciado:**` em toda rule sem `paths:`, não os `##`:
    seção de fonte ou de protocolo não é princípio. Levanta `ValueError` para campo vazio ou em mais
    de uma linha, nome repetido entre os títulos dessas rules, teto atingido ou arquivo que reprova
    em `lint_rule`; em todos os casos, nada muda no disco.
    """
    campos = {"nome": nome, "enunciado": enunciado, "teste": teste}
    for chave, valor in campos.items():
        if not valor.strip():
            raise ValueError(f"princípio com '{chave}' vazio")
        if "\n" in valor.strip():
            raise ValueError(f"princípio com '{chave}' em mais de uma linha: {valor!r}")
    nome, enunciado, teste = (valor.strip() for valor in campos.values())

    dir_rules = raiz / ".claude" / "rules"
    existentes = _rules_de_principio(dir_rules)
    textos = [p.read_text(encoding="utf-8") for p in existentes]
    total = sum(len(_ENUNCIADO_RE.findall(texto)) for texto in textos)
    if total >= TETO_PRINCIPIOS:
        raise ValueError(f"teto de {TETO_PRINCIPIOS} princípios atingido: há {total}")
    titulos = {t.casefold() for texto in textos for t in _TITULO_RE.findall(texto)}
    if nome.casefold() in titulos:
        raise ValueError(f"princípio já existe: {nome!r}")

    destino = dir_rules / "principles.md"
    if destino.exists():
        atual = destino.read_text(encoding="utf-8").rstrip("\n") + "\n"
    else:
        descricao = descricao.strip() or _DESCRICAO_PRINCIPIOS
        atual = (
            "---\n"
            f"name: {json.dumps('principles')}\n"
            f"description: {json.dumps(descricao, ensure_ascii=False)}\n"
            "---\n"
        )
    texto = atual + f"\n## {nome}\n\n**Enunciado:** {enunciado}\n\n**Teste:** {teste}\n"

    with tempfile.TemporaryDirectory() as tmp:
        provisorio = Path(tmp) / "principles.md"
        provisorio.write_text(texto, encoding="utf-8")
        problemas = lint_rule(provisorio)
        if registry._e_guideline(provisorio):
            problemas.append("principles.md declara 'paths:' — com escopo, deixa de ser princípio")
        if problemas:
            raise ValueError("; ".join(problemas))
        dir_rules.mkdir(parents=True, exist_ok=True)
        shutil.move(str(provisorio), destino)
    return destino


def auditar_arvore() -> list[str]:
    """Varre `.claude/rules/` e `.claude/rules-off/` da raiz real — lista vazia quando a árvore
    está sã.

    Três recusas isoladas (norma, seção *Validar a ativação*): um `.md` em qualquer subdiretório
    de `rules/` — a `L-26` inteira, porque o matcher recursa e o arquivo continua carregando; um
    `.md` direto em `rules/` que reprova em `lint_rule`; um `.md` direto em `rules-off/` que
    reprova em `lint_guideline`, porque volta a ser ligado um dia e o defeito espera lá dentro.
    Só leitura — auditoria que corrige sozinha esconde o defeito que deveria mostrar.
    """
    dir_rules = lib.repo_root() / ".claude" / "rules"
    dir_off = dir_rules.parent / "rules-off"

    problemas: list[str] = []
    problemas.extend(_checar_subdiretorio(dir_rules))
    problemas.extend(_checar_lint_direto(dir_rules, lint_rule))
    problemas.extend(_checar_lint_direto(dir_off, lint_guideline))
    return problemas


def _checar_subdiretorio(dir_rules: Path) -> list[str]:
    """`.md` fora do nível direto de `dir_rules` — o matcher do Claude Code recursa (`L-26`)."""
    if not dir_rules.is_dir():
        return []
    return [
        f"'.md' em subdiretório de rules/, continua carregando (L-26): {p.relative_to(dir_rules)}"
        for p in sorted(dir_rules.rglob("*.md"))
        if p.parent != dir_rules
    ]


def _checar_lint_direto(diretorio: Path, lint) -> list[str]:
    """Roda `lint` sobre cada `.md` direto em `diretorio` — reprovação vira problema nomeado."""
    if not diretorio.is_dir():
        return []
    problemas = []
    for arquivo in sorted(diretorio.glob("*.md")):
        achados = lint(arquivo)
        if achados:
            problemas.append(f"{arquivo}: {'; '.join(achados)}")
    return problemas
