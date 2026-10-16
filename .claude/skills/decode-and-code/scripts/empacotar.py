#!/usr/bin/env python3
"""Empacota o método num plugin instalável — unidade 0001-16.

`construir` lê sempre da árvore real (`lib.repo_root()`), nunca de um parâmetro de origem: o
plugin é o que este repositório produz de si mesmo, e origem configurável reabriria a pergunta
que a unidade fecha. `materializar` é a exceção — recebe a origem porque copia **uma** guideline
específica, não a árvore inteira.

Invariante 2 do `CLAUDE.md`: nada específico de projeto viaja no plugin. `construir` decide isso
por **exclusão de caminho** (`scripts/tests/`, `__pycache__`, `docs/`, `guardrails.json` — nenhum
dos quatro é fonte copiada); `verificar` decide por **busca de conteúdo** na árvore já construída —
o par que fecha o invariante nos dois sentidos.

**Pacote enxuto — `P-05` e `D-02` do plano `apply-plugin-review`.** O que só serve a quem
desenvolve o método fica no repositório: `empacotar.py`, `reconciliar.py` (compara contra o
AmFlow) e `lint_skill.py` não são importados por script de runtime nem por hook, só pelos testes
(`_SCRIPTS_DE_DESENVOLVIMENTO`). Dos três hooks do `settings.json` viajam dois,
`PreToolUse` e `InstructionsLoaded` (`_EVENTOS_DO_PACOTE`): `SubagentStart` e
`InstructionsLoaded` são hooks de anúncio, e nenhum chega ao modelo; não há registro de projeto que
instala o plugin usando o controle de três estados da norma (*Validar a ativação*). O
`InstructionsLoaded` fica por ser o log desse controle, e o `SubagentStart` continua no
`settings.json` deste repositório. O `PreToolUse` fica porque é o guardrail.

`${CLAUDE_PLUGIN_ROOT}` é o que separa pacote de cópia: `hooks/hooks.json` reescreve a âncora
`${CLAUDE_PROJECT_DIR}/.claude/hooks` do `settings.json` para `${CLAUDE_PLUGIN_ROOT}/hooks`.
"""

from __future__ import annotations

import hashlib
import json
import re
import shutil
import subprocess
import zipfile
from pathlib import Path

import lib

_ANCORA_PROJETO = "${CLAUDE_PROJECT_DIR}/.claude/hooks"
_ANCORA_PLUGIN = "${CLAUDE_PLUGIN_ROOT}/hooks"

# Os hooks que viajam, por evento — a **única** lista (`D-02`, `P-05`). Os scripts de `hooks/` não
# têm lista própria: saem dos comandos destes eventos (`_scripts_dos_hooks`), então um evento só
# entra ou sai do pacote aqui.
_EVENTOS_DO_PACOTE = ("PreToolUse", "InstructionsLoaded")

# Só da pasta compartilhada, e só no pacote: nenhum runtime nem hook os importa (`P-05`).
_SCRIPTS_DE_DESENVOLVIMENTO = ("empacotar.py", "reconciliar.py", "lint_skill.py")

_SCRIPT_DO_HOOK_RE = re.compile(re.escape(_ANCORA_PROJETO) + r"/([\w.-]+\.py)")

_PROJECT_RE = re.compile(r"(?m)^project:.*$")

_DESTINO_DEFAULT = "dist/decode-and-code"

_MANIFESTO_RELATIVO = Path(".claude-plugin") / "plugin.json"

# As skills que viajam são as de `lib.SKILLS` — lista explícita, nunca `.claude/skills/*`: uma skill
# de desenvolvimento deste repositório não pode vazar para quem instala (`P-03`, `D-01`). A pasta
# compartilhada não é skill (não tem `SKILL.md`): guarda `scripts/`, `config.json` e, no pacote,
# `reference/`, e as quatro a citam por `${CLAUDE_SKILL_DIR}/../decode-and-code/`.
_PASTA_COMPARTILHADA = "decode-and-code"


def _resolver_destino(destino: Path | str) -> Path:
    """Relativo resolve contra a raiz do repositório; absoluto passa direto."""
    destino = Path(destino)
    return destino if destino.is_absolute() else (lib.repo_root() / destino)


def _fontes() -> dict[str, Path]:
    raiz = lib.repo_root()
    skills = raiz / ".claude" / "skills"
    return {
        "manifesto": raiz / ".claude" / "plugin.json",
        "compartilhada": skills / _PASTA_COMPARTILHADA,
        **{f"skill {nome}": skills / nome for nome in lib.SKILLS},
        "hooks": raiz / ".claude" / "hooks",
        "settings": raiz / ".claude" / "settings.json",
        "norma": raiz / "docs" / "plan" / "system" / "modelo-dev-units.md",
    }


def construir(destino: Path | str = _DESTINO_DEFAULT) -> list[Path]:
    """Constrói a árvore do plugin em `destino`, sempre do zero. Devolve os caminhos escritos.

    Levanta `FileNotFoundError` nomeando a fonte ausente antes de escrever qualquer coisa —
    checagem completa primeiro, escrita depois.
    """
    destino = _resolver_destino(destino)
    fontes = _fontes()
    for nome, caminho in fontes.items():
        if not caminho.exists():
            raise FileNotFoundError(f"fonte ausente para {nome!r}: {caminho}")

    hooks = _hooks_do_pacote(fontes["settings"])
    scripts_dos_hooks = _scripts_dos_hooks(hooks)
    for nome in scripts_dos_hooks:
        if not (fontes["hooks"] / nome).is_file():
            raise FileNotFoundError(f"hook citado no settings.json sem fonte: {fontes['hooks'] / nome}")

    if destino.exists():
        shutil.rmtree(destino)
    destino.mkdir(parents=True)

    nome_plugin = json.loads(fontes["manifesto"].read_text(encoding="utf-8"))["name"]

    escritos: list[Path] = [_copiar_manifesto(fontes["manifesto"], destino)]
    escritos.extend(_copiar_skill(fontes["compartilhada"], destino, nome_plugin))
    for nome in lib.SKILLS:
        escritos.extend(_copiar_skill(fontes[f"skill {nome}"], destino, nome_plugin))
    escritos.append(_copiar_norma(fontes["norma"], destino, nome_plugin))
    escritos.extend(_copiar_hooks(fontes["hooks"], destino, scripts_dos_hooks))
    escritos.append(_escrever_hooks_json(hooks, destino))
    return escritos


def _copiar_manifesto(origem: Path, destino: Path) -> Path:
    alvo = destino / ".claude-plugin" / "plugin.json"
    alvo.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(origem, alvo)
    return alvo


def _copiar_skill(origem: Path, destino: Path, nome_plugin: str) -> list[Path]:
    """Copia uma pasta de `skills/` inteira, exceto `scripts/tests/`, `__pycache__` e `.DS_Store`.

    Serve às quatro skills e à pasta compartilhada: o destino é `skills/<nome da pasta de origem>`, e
    o `SKILL.md` — que só as skills têm — passa por `_declarar_o_plugin`. Só a pasta compartilhada
    perde também `_SCRIPTS_DE_DESENVOLVIMENTO` (`P-05`): é onde `scripts/` mora, e uma skill não
    deveria perder em silêncio um arquivo que por acaso tenha um desses nomes.

    `.DS_Store` entrou por medição, não por antecipação (`L-32`): a reconciliação da `0001-17`
    acusou um dentro da pasta da skill, e o pacote o levava — lixo do Finder da máquina que
    construiu. `verificar` não o pegava, porque não há nome de projeto dentro de um `.DS_Store`.
    A exclusão vive **só aqui**: ensinar `verificar` a recusar lixo criaria duas listas do mesmo
    fato (invariante 1). Lixo novo entra nesta lista quando for observado, nunca antes.
    """
    alvo = destino / "skills" / origem.name
    ignorar = ["__pycache__", "tests", ".DS_Store"]
    if origem.name == _PASTA_COMPARTILHADA:
        ignorar.extend(_SCRIPTS_DE_DESENVOLVIMENTO)
    shutil.copytree(origem, alvo, ignore=shutil.ignore_patterns(*ignorar))
    if (alvo / "SKILL.md").is_file():
        _declarar_o_plugin(alvo / "SKILL.md", nome_plugin)
    return [p for p in sorted(alvo.rglob("*")) if p.is_file()]


def _declarar_o_plugin(skill_md: Path, nome_plugin: str) -> None:
    """`project:` do frontmatter passa a declarar o **plugin**, não o repositório que o produziu.

    A fonte continua declarando o repositório que a produziu, que é o correto para um artefato
    deste projeto (padrão de frontmatter, `CLAUDE.md` global). O que não pode é a cópia distribuída
    chegar em outro projeto declarando o nosso — é o defeito que o `huddle.md` teve, e a reescrita
    aqui é a mesma classe da âncora de hook: derivado se corrige no build, fonte permanece honesta.
    """
    texto = skill_md.read_text(encoding="utf-8")
    skill_md.write_text(_PROJECT_RE.sub(f"project: {nome_plugin}", texto, count=1), encoding="utf-8")


def _copiar_norma(origem: Path, destino: Path, nome_plugin: str) -> Path:
    """Leva a norma-mecanismo para `reference/`, ao lado da skill — unidade `0004-04`.

    `bootstrap.iniciar` materializa de lá quando o método roda de um pacote instalado (as skills já
    citam `<plan_root>/system/modelo-dev-units.md`, e sem isto o projeto que instala não tem a fonte
    que elas citam — `L-31` do plano `0001`). Fica fora de `docs/`, que `construir` nunca
    copia (invariante 2): é **um** arquivo nomeado, o operativo que a `0004-03` já separou do
    registro deste projeto, não a árvore inteira de `docs/plan`.

    `project:` do frontmatter passa pela mesma reescrita que os `SKILL.md` já recebem
    (`_declarar_o_plugin`) — sem ela, a cópia distribuída declara no próprio frontmatter o nome do
    repositório que a produziu, e `verificar` acusa: a mesma classe de vazamento da `L-31`, medida
    nesta unidade num arquivo que ainda não existia quando aquela lacuna foi escrita.
    """
    alvo = destino / "skills" / "decode-and-code" / "reference" / origem.name
    alvo.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(origem, alvo)
    _declarar_o_plugin(alvo, nome_plugin)
    return alvo


def _hooks_do_pacote(settings: Path) -> dict:
    """O bloco `hooks` de `settings.json` reduzido a `_EVENTOS_DO_PACOTE` — a fonte continua com os quatro."""
    bloco = json.loads(settings.read_text(encoding="utf-8")).get("hooks", {})
    return {evento: bloco[evento] for evento in _EVENTOS_DO_PACOTE if evento in bloco}


def _scripts_dos_hooks(hooks: dict) -> list[str]:
    """Nomes dos scripts citados nos comandos de `hooks` — o que `hooks/` leva sai daqui, sem lista própria."""
    comandos = [
        hook.get("command", "") for grupos in hooks.values() for grupo in grupos for hook in grupo["hooks"]
    ]
    return sorted({nome for comando in comandos for nome in _SCRIPT_DO_HOOK_RE.findall(comando)})


def _copiar_hooks(origem: Path, destino: Path, scripts: list[str]) -> list[Path]:
    """Copia para `hooks/` só os `scripts` citados pelos eventos que viajam (`P-05`), não `*.py`."""
    alvo = destino / "hooks"
    alvo.mkdir(parents=True, exist_ok=True)
    escritos = []
    for nome in scripts:
        copia = alvo / nome
        shutil.copy2(origem / nome, copia)
        escritos.append(copia)
    return escritos


def _escrever_hooks_json(hooks: dict, destino: Path) -> Path:
    """Gera `hooks/hooks.json` com o bloco `hooks` recebido (`_hooks_do_pacote`), âncora trocada."""
    texto = json.dumps({"hooks": hooks}, ensure_ascii=False, indent=2).replace(
        _ANCORA_PROJETO, _ANCORA_PLUGIN
    )

    alvo = destino / "hooks" / "hooks.json"
    alvo.parent.mkdir(parents=True, exist_ok=True)
    alvo.write_text(texto + "\n", encoding="utf-8")
    return alvo


def _marcadores_instancia() -> tuple[str, ...]:
    """O nome do repositório que produziu o pacote — lido de `lib.repo_root()`, nunca hardcoded.

    **A lista tinha quatro marcadores e três eram falso positivo** (`L-31`, medido em 2026-08-26
    construindo do repositório real): `guardrails.json` acusava `guardrail.py` e o hook, que
    **precisam** nomear o arquivo que leem; `docs/plan` acusava o default de `lib.py` e do
    `config.json`, que é justamente a configurabilidade que a `0001-01` entregou; e
    `CLAUDE_PROJECT_DIR` acusava a constante `_ANCORA_PROJETO` deste módulo — o verificador
    reprovando o código que faz a substituição.

    Sobra o que é instância por definição: **nome de projeto**. Nome de arquivo que o mecanismo lê
    e caminho default que o mecanismo resolve são mecanismo, não instância.
    """
    return (lib.repo_root().name,)


def _ancora_de_projeto(destino: Path) -> list[str]:
    """`${CLAUDE_PROJECT_DIR}` (forma de placeholder, com `${...}`) dentro de `hooks/` — onde a
    âncora errada quebra de verdade: um hook cujo comando não passou pela troca de
    `_escrever_hooks_json` continua citando o placeholder de substituição de texto, e o
    processo instalado vai procurar o próprio código — mecanismo, não instância — na árvore de
    quem instalou. Mesmo erro de quadro de referência da `L-24`: ancorar a busca onde ela
    significa alguma coisa, nunca no texto inteiro.

    **Só a forma com `${...}`, não a palavra nua.** Medido em 2026-09-04 (AmFlow, correção do
    guardrail): `pre_tool_use.py` passou a ler `os.environ.get("CLAUDE_PROJECT_DIR")` para achar
    `guardrails.json` — dado do projeto que instala, não o próprio código —, e isso é exatamente
    o que a doc oficial recomenda para um hook (`code.claude.com/docs/en/hooks`, a variável é
    exportada no processo). Buscar a palavra nua reprovava esse uso correto — e a prosa do
    docstring que o explica — junto com o placeholder que de fato indica âncora esquecida.
    """
    pasta = destino / "hooks"
    problemas = []
    for arquivo in sorted(pasta.rglob("*")) if pasta.is_dir() else []:
        if arquivo.is_file() and "${CLAUDE_PROJECT_DIR}" in _texto(arquivo):
            problemas.append(f"{arquivo.relative_to(destino)}: âncora '${{CLAUDE_PROJECT_DIR}}' em hooks/")
    return problemas


def _texto(arquivo: Path) -> str:
    """Conteúdo textual, ou vazio quando o arquivo é binário — nunca levanta."""
    try:
        return arquivo.read_text(encoding="utf-8")
    except (UnicodeDecodeError, ValueError):
        return ""


def verificar(destino: Path | str = _DESTINO_DEFAULT) -> list[str]:
    """Percorre `destino` e devolve um problema por ocorrência de instância do projeto de origem.

    Lista vazia quando o pacote está limpo — mesmo padrão de `lint_*`.

    **O manifesto fica fora do escaneamento, medido nesta sessão (2026-09-01).**
    `.claude-plugin/plugin.json` declara `repository`/`homepage` apontando para o GitHub deste
    método — texto fixo e autoral, correto em qualquer checkout —, e por isso carrega o nome do
    repositório de origem sempre que o diretório local se chamar como o repositório real (o caso
    comum: quem clona não costuma renomear). Não é o vazamento que o marcador persegue — esse é a
    cópia dos `SKILL.md`/norma citando o checkout que os construiu, e `_copiar_manifesto`
    nunca passa pela reescrita que eles recebem (`_declarar_o_plugin`): o manifesto é
    copiado verbatim porque sua função é justamente declarar essa identidade, e ela não muda com o
    nome do diretório de quem constrói.
    """
    destino = _resolver_destino(destino)
    marcadores = _marcadores_instancia()

    problemas = []
    for arquivo in sorted(destino.rglob("*")):
        if not arquivo.is_file():
            continue
        if arquivo.relative_to(destino) == _MANIFESTO_RELATIVO:
            continue
        texto = _texto(arquivo)
        for marcador in marcadores:
            if marcador in texto:
                problemas.append(f"{arquivo.relative_to(destino)}: ocorrência de {marcador!r}")
    problemas.extend(_ancora_de_projeto(destino))
    return problemas


def validar(destino: Path | str = _DESTINO_DEFAULT) -> list[str]:
    """`claude plugin validate` sobre o pacote — lista de problemas, vazia quando aprova.

    **Par de `verificar`, e mede outra coisa.** `verificar` recusa instância do projeto de origem;
    este confere a **estrutura** contra a ferramenta oficial, que conhece o formato do manifesto e
    dos componentes. Ter só o nosso era conhecer só metade.

    Caracterizado contra o binário real em 2026-08-27, antes de escrito (`scripts.md`, *Comando
    externo*): o sinal é o **returncode** — `0` aprova, `1` reprova —, a mensagem sai inteira em
    `stdout`, e `stderr` fica vazio nos três casos medidos (pacote válido, diretório sem manifesto,
    caminho inexistente).

    **`--strict`, medido em 2026-10-15 (Claude Code 2.1.300).** Sem a flag, aviso não reprova: o
    binário sai com `0` e "Validation passed with warnings", e como o sinal aqui é só o returncode,
    os quatro avisos de `${CLAUDE_PLUGIN_ROOT}` sem aspas nos comandos de hook passaram calados.
    Com `--strict` o aviso vira reprovação — exit `1`, última linha "Validation failed (--strict
    treats warnings as errors)" —, a mensagem continua inteira em `stdout` e `stderr` segue vazio.
    Pacote sem aviso sai com `0` com e sem a flag; caminho inexistente e JSON inválido saem com
    `1` com e sem a flag, então a flag só muda o destino do aviso. O alcance é o pacote todo, não só
    os hooks: manifesto sem `description` ou sem `author` também reprova. Roda sem credencial
    (`env -i` com `HOME` vazio dá o mesmo resultado). O glifo do início da linha final muda com o
    locale — comparar pelo texto, nunca pelo glifo.

    Binário ausente **não levanta**: devolve o problema dizendo isso. Quem instala o método pode
    não ter o `claude` no `PATH`, e um gate que estoura nessa condição vira gate que se desliga.
    """
    destino = _resolver_destino(destino)
    try:
        resultado = subprocess.run(
            ["claude", "plugin", "validate", "--strict", str(destino)], capture_output=True
        )
    except FileNotFoundError:
        return ["claude não encontrado no PATH — validação oficial não executada"]

    if resultado.returncode == 0:
        return []
    saida = resultado.stdout.decode("utf-8", errors="replace").strip()
    return [f"claude plugin validate reprovou: {saida}"]


def empacotar_zip(staging: Path | str | None = None) -> tuple[Path, str]:
    """Zipa a árvore do plugin e devolve `(caminho_do_zip, sha256_hex)` — imprime os dois.

    `staging` ausente constrói no destino default (`_DESTINO_DEFAULT`) antes de zipar; passado,
    assume que quem chamou já construiu ali — o mesmo contrato de `verificar`/`validar`, que também
    recebem a árvore pronta em vez de construí-la.

    **Gate antes da escrita.** `verificar` (vazamento de instância) e `validar` (`claude plugin
    validate`) rodam sobre o staging antes de qualquer byte de zip ser escrito; qualquer problema
    levanta `RuntimeError` — zip que carrega instância do projeto de origem ou reprova o validador
    oficial não deveria existir no disco, nem para inspeção.

    **Layout — raiz do plugin no topo do archive, medido contra a doc oficial, não suposto.**
    `plugin-marketplaces` (*Zip Archive source*, consultada em 2026-09-01) diz que o Claude Code
    procura `.claude-plugin/` na raiz do zip e, se não achar, dentro de uma única pasta de nível 1 —
    os dois layouts instalam. Esta função usa o primeiro. A prova ponta a ponta com `--plugin-url`
    contra um asset real de Release é ato humano; se recusar, o conserto é trocar para o segundo
    layout aqui, não noutro lugar.

    **`date_time` fixo, não o mtime do disco.** `_declarar_o_plugin` reescreve alguns arquivos a
    cada `construir` (os `SKILL.md`, a norma copiada), o que muda o mtime a cada
    build mesmo com o conteúdo idêntico. Um zip que varia byte a byte entre duas construções da
    mesma fonte não serve de artefato reprodutível — por isso todo `ZipInfo` nasce com a mesma
    data, e só o conteúdo decide o hash.
    """
    if staging is None:
        staging = _resolver_destino(_DESTINO_DEFAULT)
        construir(staging)
    else:
        staging = _resolver_destino(staging)

    problemas = verificar(staging) + validar(staging)
    if problemas:
        raise RuntimeError(
            "empacotar_zip: staging reprovado, zip não escrito — " + "; ".join(problemas)
        )

    manifesto = json.loads((staging / ".claude-plugin" / "plugin.json").read_text(encoding="utf-8"))
    caminho_zip = lib.repo_root() / f"decode-and-code-{manifesto['version']}.zip"

    with zipfile.ZipFile(caminho_zip, "w", zipfile.ZIP_DEFLATED) as zf:
        for arquivo in sorted(staging.rglob("*")):
            if not arquivo.is_file():
                continue
            info = zipfile.ZipInfo(str(arquivo.relative_to(staging)), date_time=(1980, 1, 1, 0, 0, 0))
            zf.writestr(info, arquivo.read_bytes(), zipfile.ZIP_DEFLATED)

    sha256 = hashlib.sha256(caminho_zip.read_bytes()).hexdigest()
    print(caminho_zip)
    print(sha256)
    return caminho_zip, sha256


def materializar(origem: Path, projeto: Path) -> Path:
    """Copia a guideline `origem` para `<projeto>/.claude/rules/`. Devolve o caminho escrito.

    Levanta `FileNotFoundError` se `origem` não existir, e `FileExistsError` se o destino já
    existir — nos dois casos, nada é escrito.
    """
    origem = Path(origem)
    if not origem.is_file():
        raise FileNotFoundError(f"origem ausente: {origem}")

    destino = Path(projeto) / ".claude" / "rules" / origem.name
    if destino.exists():
        raise FileExistsError(f"destino já existe — materializar não sobrescreve: {destino}")

    destino.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(origem, destino)
    return destino
