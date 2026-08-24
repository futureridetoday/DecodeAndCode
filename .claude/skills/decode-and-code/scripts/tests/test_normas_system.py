#!/usr/bin/env python3
"""Testes da camada normativa em docs/plan/system/ — unidade 0001-08.

O que precisa ficar provado é o critério de aceite: os dois documentos de linguagem
migraram do AmFlow desacoplados — todo link relativo dos documentos de `docs/plan/system/`
resolve em disco, e nenhum dos dois carrega instância do repositório de origem (core,
serviço, caminho de `docs/mvp/` ou o invariante `D10` do Worker).
"""

from __future__ import annotations

import re
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import lib

_SYSTEM_DIR = lib.plan_root() / "system"

_LINK_RE = re.compile(r"\[[^\]]*\]\(([^)]+)\)")

# Instância do AmFlow que o `language-policy.md` e o `estudo-runtime-e-dependencias.md`
# não podem carregar — a norma cita como vinculantes só o que está aqui (§ *Contrato*
# e *Critério de aceite* da unidade 0001-08).
_MARCAS_AMFLOW = (
    "AmFlow",
    "docs/mvp",
    "native-only",
    "D10",
    "Worker",
    "builder",
    "backlog-worker",
    "smoke-tests.py",
    "hard-memory",
)


def _sem_blocos_de_codigo(texto: str) -> str:
    """Remove o miolo de blocos ```...``` — exemplo/template não é link a resolver."""
    fora = []
    dentro = False
    for linha in texto.splitlines():
        if linha.lstrip().startswith("```"):
            dentro = not dentro
            continue
        if not dentro:
            fora.append(linha)
    return "\n".join(fora)


def _corpo_normativo(texto: str) -> str:
    """Remove as notas de cabeçalho — blocos `>` antes da primeira seção `##`.

    É ali que vivem *Procedência* e *Como usar este documento*, e nomear o repositório de
    origem é o propósito delas: documento migrado que esconde de onde veio mente sobre a
    própria evidência. A exceção é **explícita e delimitada** justamente para não virar a
    exceção silenciosa que deixou a lista de marcas passar sem `"AmFlow"` (`L-23`).
    """
    linhas = []
    no_cabecalho = True
    for linha in texto.splitlines():
        if no_cabecalho and linha.startswith("## "):
            no_cabecalho = False
        if no_cabecalho and linha.lstrip().startswith(">"):
            continue
        linhas.append(linha)
    return "\n".join(linhas)


def _links_relativos(texto: str) -> list[str]:
    achados = []
    for alvo in _LINK_RE.findall(_sem_blocos_de_codigo(texto)):
        if alvo.startswith(("http://", "https://", "mailto:")):
            continue
        achados.append(alvo.split("#", 1)[0])
    return achados


class TestLinksDosDocumentosDeSystemResolvem(unittest.TestCase):
    def test_todo_link_relativo_resolve_em_disco(self):
        arquivos = sorted(_SYSTEM_DIR.glob("*.md"))
        self.assertTrue(arquivos, f"nenhum .md encontrado em {_SYSTEM_DIR}")
        for arquivo in arquivos:
            texto = arquivo.read_text(encoding="utf-8")
            for alvo in _links_relativos(texto):
                destino = (arquivo.parent / alvo).resolve()
                self.assertTrue(
                    destino.is_file(),
                    f"{arquivo.name}: link morto — {alvo!r} não resolve em {destino}",
                )


class TestDocumentosDeLinguagemSemInstanciaDoAmFlow(unittest.TestCase):
    def test_language_policy_existe_e_sem_instancia(self):
        self._sem_instancia(_SYSTEM_DIR / "language-policy.md")

    def test_estudo_runtime_existe_e_sem_instancia(self):
        self._sem_instancia(_SYSTEM_DIR / "estudo-runtime-e-dependencias.md")

    def test_language_policy_sem_secao_6_antiga(self):
        # "O que fica superado" — a lista de docs/mvp/ do AmFlow. Não tem objeto aqui.
        texto = (_SYSTEM_DIR / "language-policy.md").read_text(encoding="utf-8")
        self.assertNotIn("O que fica superado", texto)

    def _sem_instancia(self, arquivo: Path) -> None:
        self.assertTrue(arquivo.is_file(), f"documento não existe: {arquivo}")
        corpo = _corpo_normativo(arquivo.read_text(encoding="utf-8"))
        for marca in _MARCAS_AMFLOW:
            self.assertNotIn(marca, corpo, f"{arquivo.name}: instância do AmFlow — {marca!r}")


if __name__ == "__main__":
    unittest.main()
