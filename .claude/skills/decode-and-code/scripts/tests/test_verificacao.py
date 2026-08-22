#!/usr/bin/env python3
"""Testes do oráculo de verificação — unidade 0002-08.

O que dá valor à unidade é o par do critério de aceite: uma unidade
temporária apontando para um teste controlável vira `verified` quando ele
passa, e volta a `spec` — com `verified_at` limpo — quando ele passa a
falhar. As demais dimensões (test ausente, teste inexistente, extensão sem
runner, dry_run, runner `.ts`) são cobertas isoladamente contra uma unidade
sintética mínima.

`subprocess.run` é sempre mockado — nunca chamado de verdade. Um teste real
apontaria `scripts/test-python.sh` para este próprio pacote
(`.claude/skills/dev-units/scripts`), que contém este arquivo: a chamada
real reexecutaria a suíte inteira de dentro do próprio teste, que
reexecutaria de novo, recursivamente. Medido nesta sessão: a primeira versão
sem mock chegou a 763 processos órfãos antes de ser morta à mão — `.kill()`
do `subprocess` do Python mata só o filho direto, não a árvore inteira que
`test-python.sh` gera por baixo.
"""

from __future__ import annotations

import os
import sys
import tempfile
import unittest
from datetime import date
from pathlib import Path
from unittest import mock

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import lib
import regioes
import verificacao


def setUpModule():
    """Limpa a sentinela de reentrância antes de toda a suíte.

    Esta suíte roda dentro de uma verificação sempre que `verificar()` é
    chamado sobre a unidade 0002-08 — é o desenho, não acidente. Nenhum teste
    aqui executa subprocesso de verdade: todos mockam. A sentinela existe para
    barrar execução real aninhada, então mantê-la ligada aqui só impediria os
    mocks de rodar, e a unidade jamais poderia ser promovida.

    Os testes que exercitam a própria sentinela a religam via `mock.patch.dict`.
    """
    os.environ.pop(verificacao.SENTINELA_REENTRANCIA, None)

UNIDADE = """\
---
name: exemplo
type: unit
project: AmFlow
description: unidade sintética para teste da verificação
tags: []

core: builder
module: dev-units
block: ""
owner: builder
unit_id: 0009-01
unit_type: dev

state: {state}
test: {test}
verified_at: {verified_at}

author: Teste
created: 2026-07-25
status: draft
version: 1.0.0
updated: ""

scope: project
auto_load: false
dependencies: []
---

# 0009-01 — Unidade sintética

**Responsabilidade:** existir só para o teste da verificação.
"""


def _escreve_unidade(caminho: Path, test: str, state: str = "spec", verified_at: str = '""') -> None:
    caminho.write_text(
        UNIDADE.format(test=test, state=state, verified_at=verified_at), encoding="utf-8"
    )


class TestSemTesteDeclarado(unittest.TestCase):
    def test_levanta_value_error(self):
        with tempfile.TemporaryDirectory() as tmp:
            alvo = Path(tmp) / "unidade.md"
            _escreve_unidade(alvo, test="")
            with self.assertRaises(ValueError):
                verificacao.verificar(alvo)


class TestTesteInexistente(unittest.TestCase):
    """Regride de `verified` para `spec` e limpa `verified_at` — sem exceção."""

    def test_resulta_em_spec_e_limpa_verified_at(self):
        with tempfile.TemporaryDirectory() as tmp:
            raiz = Path(tmp).resolve()
            unidade = raiz / "unidade.md"
            _escreve_unidade(
                unidade,
                test="caminho/que/nao/existe/test_fantasma.py",
                state="verified",
                verified_at="2020-01-01",
            )
            with mock.patch.object(lib, "repo_root", return_value=raiz):
                estado, escreveu = verificacao.verificar(unidade)

            self.assertEqual(estado, "spec")
            self.assertTrue(escreveu)
            self.assertEqual(regioes.ler_campo(unidade, "state"), "spec")
            self.assertEqual(regioes.ler_campo(unidade, "verified_at"), '""')


class TestExtensaoSemRunner(unittest.TestCase):
    def test_levanta_value_error(self):
        with tempfile.TemporaryDirectory() as tmp:
            raiz = Path(tmp).resolve()
            (raiz / "test_algo.js").write_text("// js\n", encoding="utf-8")
            unidade = raiz / "unidade.md"
            _escreve_unidade(unidade, test="test_algo.js")

            with mock.patch.object(lib, "repo_root", return_value=raiz):
                with self.assertRaises(ValueError):
                    verificacao.verificar(unidade)


class TestRegressaoVerdeParaVermelho(unittest.TestCase):
    """O critério de aceite da unidade: teste que passa a falhar rebaixa o estado."""

    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self._tmp.cleanup)
        self.raiz = Path(self._tmp.name).resolve()

        pacote_tests = self.raiz / "pacote" / "tests"
        pacote_tests.mkdir(parents=True)
        (pacote_tests / "test_controlavel.py").write_text(
            "# resultado controlado pelo mock de subprocess.run no teste\n", encoding="utf-8"
        )

        self.unidade = self.raiz / "unidade.md"
        _escreve_unidade(self.unidade, test="pacote/tests/test_controlavel.py")

        patcher = mock.patch.object(lib, "repo_root", return_value=self.raiz)
        patcher.start()
        self.addCleanup(patcher.stop)

    def _rodar_com_saida(self, codigo: int) -> tuple[str, bool]:
        with mock.patch.object(
            verificacao.subprocess,
            "run",
            return_value=mock.Mock(returncode=codigo, stdout=b"Ran 1 tests\n\nOK\n", stderr=b""),
        ) as executar:
            resultado = verificacao.verificar(self.unidade)
        args, kwargs = executar.call_args
        self.assertEqual(
            args[0],
            [str(self.raiz / "scripts" / "test-python.sh"), "pacote/tests/test_controlavel.py"],
        )
        self.assertEqual(kwargs["cwd"], self.raiz)
        return resultado

    def test_verde_promove_a_verified(self):
        estado, escreveu = self._rodar_com_saida(0)
        self.assertEqual(estado, "verified")
        self.assertTrue(escreveu)
        self.assertEqual(regioes.ler_campo(self.unidade, "state"), "verified")
        self.assertEqual(
            regioes.ler_campo(self.unidade, "verified_at"), date.today().isoformat()
        )

    def test_vermelho_rebaixa_a_spec_e_limpa_verified_at(self):
        self._rodar_com_saida(0)
        estado, escreveu = self._rodar_com_saida(1)
        self.assertEqual(estado, "spec")
        self.assertTrue(escreveu)
        self.assertEqual(regioes.ler_campo(self.unidade, "state"), "spec")
        self.assertEqual(regioes.ler_campo(self.unidade, "verified_at"), '""')

    def test_reexecucao_com_mesmo_resultado_nao_escreve(self):
        self._rodar_com_saida(0)
        _, escreveu = self._rodar_com_saida(0)
        self.assertFalse(escreveu)


class TestExecucaoIncompleta(unittest.TestCase):
    """Critério de aceite da 0005-01: skip ou zero-teste nunca promove, mesmo com exit 0 (F1-F3)."""

    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self._tmp.cleanup)
        self.raiz = Path(self._tmp.name).resolve()

        pacote_tests = self.raiz / "pacote" / "tests"
        pacote_tests.mkdir(parents=True)
        (pacote_tests / "test_controlavel.py").write_text(
            "# resultado controlado pelo mock de subprocess.run no teste\n", encoding="utf-8"
        )

        self.unidade = self.raiz / "unidade.md"
        _escreve_unidade(self.unidade, test="pacote/tests/test_controlavel.py")

        patcher = mock.patch.object(lib, "repo_root", return_value=self.raiz)
        patcher.start()
        self.addCleanup(patcher.stop)

    def _rodar_com_saida(self, codigo: int, stdout: bytes) -> tuple[str, bool]:
        with mock.patch.object(
            verificacao.subprocess,
            "run",
            return_value=mock.Mock(returncode=codigo, stdout=stdout, stderr=b""),
        ):
            return verificacao.verificar(self.unidade)

    def test_zero_teste_com_exit_zero_nunca_promove(self):
        """F1/F2 — `setUpClass` com `SkipTest` derruba a classe: `Ran 0 tests`, exit 0."""
        estado, _ = self._rodar_com_saida(0, stdout=b"Ran 0 tests\n\nOK (skipped=1)\n")
        self.assertEqual(estado, "spec")

    def test_skip_parcial_com_exit_zero_nunca_promove(self):
        """F1/F3 — skip parcial mantém testsRun > 0; hoje só falha por acidente de outro arquivo."""
        estado, _ = self._rodar_com_saida(
            0, stdout=b"Ran 11 tests\n\nFAILED (failures=1, skipped=8)\n"
        )
        self.assertEqual(estado, "spec")

    def test_saida_limpa_sem_sinais_promove(self):
        estado, _ = self._rodar_com_saida(0, stdout=b"Ran 5 tests\n\nOK\n")
        self.assertEqual(estado, "verified")

    def test_vitest_zero_teste_com_exit_zero_nunca_promove(self):
        """Medição 2026-08-12 — filtro que não casa nada, `vitest` também devolve exit 0."""
        estado, _ = self._rodar_com_saida(
            0, stdout=b" Test Files  1 skipped (1)\n      Tests  331 skipped (331)\n"
        )
        self.assertEqual(estado, "spec")

    def test_vitest_skip_parcial_com_exit_zero_nunca_promove(self):
        """Medição 2026-08-12 — filtro casando um bloco só, skip parcial com exit 0."""
        estado, _ = self._rodar_com_saida(
            0, stdout=b" Test Files  1 passed (1)\n      Tests  3 passed | 17 skipped (20)\n"
        )
        self.assertEqual(estado, "spec")

    def test_vitest_tudo_passa_promove(self):
        """Medição 2026-08-12 — sem skip na linha de resumo, `vitest` promove normalmente."""
        estado, _ = self._rodar_com_saida(
            0, stdout=b" Test Files  1 passed (1)\n      Tests  20 passed (20)\n"
        )
        self.assertEqual(estado, "verified")

    def test_vitest_skipped_no_nome_do_teste_nao_bloqueia(self):
        """Não-regressão do `## Contrato` da 0006-01: sem âncora, 'N skipped' num nome de teste

        casaria e bloquearia unidade sadia. A linha de resumo é o que conta, não o corpo da saída.
        """
        estado, _ = self._rodar_com_saida(
            0,
            stdout=(
                b" test: returns 5 skipped items - PASS\n"
                b" Test Files  1 passed (1)\n"
                b"      Tests  20 passed (20)\n"
            ),
        )
        self.assertEqual(estado, "verified")


class TestGranularidadeDeArquivo(unittest.TestCase):
    """Dois arquivos de teste no mesmo pacote não se acoplam — critério de aceite da 0005-02."""

    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self._tmp.cleanup)
        self.raiz = Path(self._tmp.name).resolve()

        pacote_tests = self.raiz / "pacote" / "tests"
        pacote_tests.mkdir(parents=True)
        (pacote_tests / "test_falha.py").write_text(
            "# resultado controlado pelo mock de subprocess.run no teste\n", encoding="utf-8"
        )
        (pacote_tests / "test_passa.py").write_text(
            "# resultado controlado pelo mock de subprocess.run no teste\n", encoding="utf-8"
        )

        self.unidade_falha = self.raiz / "unidade_falha.md"
        _escreve_unidade(self.unidade_falha, test="pacote/tests/test_falha.py")
        self.unidade_passa = self.raiz / "unidade_passa.md"
        _escreve_unidade(self.unidade_passa, test="pacote/tests/test_passa.py")

        patcher = mock.patch.object(lib, "repo_root", return_value=self.raiz)
        patcher.start()
        self.addCleanup(patcher.stop)

    def _comando_de(self, unidade: Path, codigo: int, stdout: bytes) -> tuple[str, list]:
        with mock.patch.object(
            verificacao.subprocess,
            "run",
            return_value=mock.Mock(returncode=codigo, stdout=stdout, stderr=b""),
        ) as executar:
            estado, _ = verificacao.verificar(unidade)
        return estado, executar.call_args[0][0]

    def test_arquivo_que_falha_nao_influencia_o_que_passa_no_mesmo_pacote(self):
        estado_falha, comando_falha = self._comando_de(
            self.unidade_falha, codigo=1, stdout=b"Ran 1 tests\n\nFAILED (failures=1)\n"
        )
        estado_passa, comando_passa = self._comando_de(
            self.unidade_passa, codigo=0, stdout=b"Ran 1 tests\n\nOK\n"
        )

        self.assertEqual(estado_falha, "spec")
        self.assertEqual(estado_passa, "verified")
        # Cada comando aponta para o arquivo declarado, não para o pacote —
        # pré-0005-02 os dois reduziam a "pacote" e ficavam idênticos, o que
        # acoplaria as duas unidades ao resultado de uma suíte só.
        self.assertEqual(comando_falha[-1], "pacote/tests/test_falha.py")
        self.assertEqual(comando_passa[-1], "pacote/tests/test_passa.py")


class TestComandoTypescript(unittest.TestCase):
    def test_roda_a_partir_de_hub_com_caminho_relativo(self):
        with tempfile.TemporaryDirectory() as tmp:
            raiz = Path(tmp).resolve()
            alvo_teste = raiz / "hub" / "test" / "api" / "mcp.test.ts"
            alvo_teste.parent.mkdir(parents=True)
            alvo_teste.write_text("// ts\n", encoding="utf-8")
            unidade = raiz / "unidade.md"
            _escreve_unidade(unidade, test="hub/test/api/mcp.test.ts")

            with mock.patch.object(lib, "repo_root", return_value=raiz):
                with mock.patch.object(
                    verificacao.subprocess,
                    "run",
                    return_value=mock.Mock(returncode=0, stdout=b"", stderr=b""),
                ) as executar:
                    estado, _ = verificacao.verificar(unidade)

            self.assertEqual(estado, "verified")
            args, kwargs = executar.call_args
            self.assertEqual(args[0], ["npx", "vitest", "run", "test/api/mcp.test.ts"])
            self.assertEqual(kwargs["cwd"], raiz / "hub")


class TestDryRun(unittest.TestCase):
    def test_nao_escreve_e_devolve_escreveu_false(self):
        with tempfile.TemporaryDirectory() as tmp:
            raiz = Path(tmp).resolve()
            pacote_tests = raiz / "pacote" / "tests"
            pacote_tests.mkdir(parents=True)
            (pacote_tests / "test_x.py").write_text("# x\n", encoding="utf-8")
            unidade = raiz / "unidade.md"
            _escreve_unidade(unidade, test="pacote/tests/test_x.py")
            original = unidade.read_text(encoding="utf-8")

            with mock.patch.object(lib, "repo_root", return_value=raiz):
                with mock.patch.object(
                    verificacao.subprocess,
                    "run",
                    return_value=mock.Mock(returncode=0, stdout=b"", stderr=b""),
                ) as executar:
                    estado, escreveu = verificacao.verificar(unidade, dry_run=True)

            executar.assert_called_once()
            self.assertEqual(estado, "verified")
            self.assertFalse(escreveu)
            self.assertEqual(unidade.read_text(encoding="utf-8"), original)


if __name__ == "__main__":
    unittest.main()


class TestSentinelaReentrancia(unittest.TestCase):
    """A proteção que faltava quando a recursão real aconteceu.

    Em 2026-07-25 um caso de teste chamou verificar() sem mock contra uma
    unidade cujo teste vive na própria suíte: cada execução disparava outra,
    e o timeout não continha a árvore — 763 processos órfãos. A sentinela
    transforma o travamento silencioso em erro imediato e nomeado.
    """

    def test_reentrar_levanta_em_vez_de_executar(self):
        with mock.patch.dict(
            os.environ, {verificacao.SENTINELA_REENTRANCIA: "1"}
        ), mock.patch.object(verificacao.subprocess, "run") as run:
            with self.assertRaises(RuntimeError):
                verificacao._executar(
                    Path(__file__).resolve(), verificacao.lib.repo_root()
                )
            run.assert_not_called()

    def test_suite_roda_normalmente_sob_a_sentinela(self):
        # A checagem fica em _executar, não em verificar: com o subprocesso
        # mockado não há recursão possível, e barrar aqui impediria esta
        # unidade de ser promovida quando a suíte roda dentro da verificação.
        with mock.patch.dict(
            os.environ, {verificacao.SENTINELA_REENTRANCIA: "1"}
        ), mock.patch.object(verificacao, "_executar", return_value=(0, "")):
            unidade = verificacao.lib.repo_root() / (
                "docs/plan/builder/0002-dev-units/08-verificacao.md"
            )
            estado, _ = verificacao.verificar(unidade, dry_run=True)
        self.assertEqual(estado, "verified")

    def test_subprocesso_recebe_a_marca(self):
        with mock.patch.object(verificacao.subprocess, "run") as run:
            run.return_value = mock.Mock(returncode=0, stdout=b"", stderr=b"")
            verificacao._executar(
                Path(__file__).resolve(), verificacao.lib.repo_root()
            )
        env = run.call_args.kwargs["env"]
        self.assertEqual(env[verificacao.SENTINELA_REENTRANCIA], "1")
