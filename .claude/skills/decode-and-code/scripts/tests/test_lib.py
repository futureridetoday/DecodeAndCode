#!/usr/bin/env python3
"""Testes do módulo base dos scripts da dev-units — unidade 0002-01.

O que precisa ficar provado é o critério de aceite: a origem dos caminhos não
depende de onde o script foi invocado. Daí o teste que troca de cwd antes de
perguntar pela raiz — inclusive para `/`, onde um fallback por cwd devolveria
outra coisa sem reclamar.
"""

from __future__ import annotations

import importlib.util
import os
import sys
import tempfile
import unittest
from pathlib import Path
from unittest import mock

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import lib


def _carregar_copia_de_lib(destino: Path):
    """Copia `lib.py` para `destino` e carrega essa cópia como módulo à parte.

    É o que reproduz o plugin instalado: o `__file__` do módulo carregado fica
    fora de qualquer projeto, então a primeira tentativa de `repo_root()`
    (a partir do código) não resolve — só a segunda (a partir do `cwd`) pode.
    """
    copia = destino / "lib.py"
    copia.write_text(Path(lib.__file__).read_text(encoding="utf-8"), encoding="utf-8")
    spec = importlib.util.spec_from_file_location(f"lib_copia_{destino.name}", copia)
    modulo = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(modulo)
    return modulo


class TestRepoRoot(unittest.TestCase):
    def test_acha_a_raiz_do_amflow(self):
        raiz = lib.repo_root()
        for marca in lib.ROOT_MARKERS:
            self.assertTrue((raiz / marca).is_dir(), marca)

    def test_independe_do_diretorio_de_trabalho(self):
        esperado = lib.repo_root()
        anterior = Path.cwd()
        try:
            for destino in (
                Path(tempfile.gettempdir()),
                esperado / "docs" / "plan",
                Path(os.sep),
            ):
                os.chdir(destino)
                self.assertEqual(lib.repo_root(), esperado, f"cwd={destino}")
        finally:
            os.chdir(anterior)

    def test_raiz_vem_resolvida(self):
        raiz = lib.repo_root()
        self.assertEqual(raiz, raiz.resolve())

    def test_sem_marcas_acima_levanta_runtime_error(self):
        # Diretório temporário não tem .claude/ + docs/ em nenhum nível acima.
        with tempfile.TemporaryDirectory() as tmp:
            with self.assertRaises(RuntimeError):
                lib._find_repo_root(Path(tmp).resolve())

    def test_resolve_projeto_sintetico_pelo_cwd_quando_o_file_nao_resolve(self):
        # O caso que falha hoje (unidade 0004-01): plugin instalado, `__file__`
        # fora de qualquer projeto, e o projeto de verdade só alcançável pelo `cwd`.
        with tempfile.TemporaryDirectory() as fora, tempfile.TemporaryDirectory() as raiz_projeto:
            fora = Path(fora).resolve()
            projeto = Path(raiz_projeto).resolve()
            (projeto / ".claude").mkdir()
            (projeto / "docs").mkdir()

            lib_fora = _carregar_copia_de_lib(fora)

            anterior = Path.cwd()
            os.chdir(projeto)
            try:
                self.assertEqual(lib_fora.repo_root(), projeto)
            finally:
                os.chdir(anterior)

    def test_cwd_sem_marcas_continua_resolvendo_este_repositorio_pelo_file(self):
        # Regressão: com o `__file__` de verdade (dentro deste repositório), um
        # `cwd` num `tempfile` sem marcas não pode mudar o resultado — o `__file__`
        # resolve primeiro e a suíte inteira depende disso continuar assim.
        esperado = lib.repo_root()
        with tempfile.TemporaryDirectory() as tmp:
            anterior = Path.cwd()
            os.chdir(tmp)
            try:
                self.assertEqual(lib.repo_root(), esperado)
            finally:
                os.chdir(anterior)

    def test_erro_quando_nenhum_dos_dois_resolve_nomeia_os_dois(self):
        with tempfile.TemporaryDirectory() as fora, tempfile.TemporaryDirectory() as sem_marcas:
            fora = Path(fora).resolve()
            sem_marcas = Path(sem_marcas).resolve()

            lib_fora = _carregar_copia_de_lib(fora)

            anterior = Path.cwd()
            os.chdir(sem_marcas)
            try:
                with self.assertRaises(RuntimeError) as ctx:
                    lib_fora.repo_root()
            finally:
                os.chdir(anterior)

            mensagem = str(ctx.exception)
            self.assertIn(str(fora), mensagem)
            self.assertIn(str(sem_marcas), mensagem)

    def test_home_com_as_marcas_nunca_vence_o_projeto_aberto_no_cwd(self):
        # `L-03`, medida em 2026-08-28: plugin instalado mora sob `~/.claude/`,
        # e o passeio a partir do `__file__` passa por `~`. Toda máquina com
        # Claude Code tem `~/.claude/`; basta um `~/docs` para casar as marcas.
        # Sem a guarda, `repo_root()` devolvia a HOME em silêncio — resposta
        # errada com cara de certa, ignorando o projeto aberto no `cwd`.
        with tempfile.TemporaryDirectory() as lar:
            lar = Path(lar).resolve()
            dir_plugin = lar / ".claude" / "plugins" / "decode-and-code" / "scripts"
            dir_plugin.mkdir(parents=True)
            (lar / "docs").mkdir()

            projeto = lar / "projeto-real"
            (projeto / ".claude").mkdir(parents=True)
            (projeto / "docs").mkdir()

            lib_no_plugin = _carregar_copia_de_lib(dir_plugin)

            anterior = Path.cwd()
            os.chdir(projeto)
            try:
                with mock.patch.dict(os.environ, {"HOME": str(lar)}):
                    self.assertEqual(lib_no_plugin.repo_root(), projeto)
            finally:
                os.chdir(anterior)


class TestCaminhosDoPlano(unittest.TestCase):
    def test_plan_root_e_docs_plan(self):
        self.assertTrue(lib.plan_root().is_dir())
        self.assertEqual(
            lib.plan_root().relative_to(lib.repo_root()), Path("docs") / "plan"
        )

    def test_planos_md_existe_no_disco(self):
        # Segunda metade do critério de aceite.
        self.assertTrue(lib.planos_md().is_file())

    def test_inbox_fica_sob_plan_root(self):
        # O diretório pode não existir ainda; o caminho é derivado do mesmo lugar.
        self.assertEqual(lib.inbox().parent, lib.plan_root())
        self.assertEqual(lib.inbox().name, "_inbox")


class TestCoreDir(unittest.TestCase):
    def test_core_existente(self):
        # Deriva um core real do disco em vez de fixar um nome — "builder" é
        # população do AmFlow, ausente aqui (suposição medida na unidade 0001-02).
        candidatos = [
            item.name
            for item in lib.plan_root().iterdir()
            if item.is_dir() and item.name not in ("_inbox", "system")
        ]
        self.assertTrue(candidatos, "nenhum core encontrado sob plan_root()")
        core = candidatos[0]
        self.assertTrue(lib.core_dir(core).is_dir())
        self.assertEqual(lib.core_dir(core).parent, lib.plan_root())

    def test_nome_vazio_e_recusado(self):
        for nome in ("", "   "):
            with self.assertRaises(ValueError):
                lib.core_dir(nome)

    def test_separador_de_caminho_e_recusado(self):
        for nome in ("hub/auth", "hub\\auth", "/hub"):
            with self.assertRaises(ValueError):
                lib.core_dir(nome)


if __name__ == "__main__":
    unittest.main()
