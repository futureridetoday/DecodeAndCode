#!/usr/bin/env python3
"""O ciclo inteiro, do pacote construído ao fechamento — unidade 0004-05.

`empacotar.construir` é a única coisa importada **deste repositório**: o resto do ciclo —
`bootstrap`, `scaffold`, `lint_unidade`, `verificacao`, `backlog`, `porte` — é carregado a partir
da árvore que `construir` acabou de escrever, por `_carregar_pacote`, que troca `sys.path`/
`sys.modules` pelo tempo do módulo e devolve tudo como estava em `tearDownModule`. Sem essa troca,
`import lib` dentro do `scaffold` carregado resolveria para o `lib` já em cache — o **deste**
repositório, importado por todo outro `test_*.py` na coleta — e o teste provaria o mecanismo, nunca
o pacote (a mesma lição da `L-31`, aplicada ao processo de import em vez de ao conteúdo de arquivo).

`TestModulosVemDoPacote` confere isso diretamente: o `__file__` do `lib` carregado fica dentro do
pacote, não deste checkout.

Git real fica de fora em dois pontos, os mesmos que `scaffold`/`porte` tocam em qualquer plano real
(`B-04`, e a nota da unidade sobre `porte._linhas_alteradas`): `move_md.esta_versionado` (o mesmo
mock dos quatro arquivos que já movem plano) e `porte._linhas_alteradas` — aqui ela dispararia de
verdade, porque o projeto sintético *é* a raiz resolvida depois do bootstrap.

`SENTINELA_REENTRANCIA` é limpa em `setUpModule` como em `test_verificacao.py`: esta unidade agora
também chama `verificacao.verificar` de verdade contra um subprocesso real (o stub de runner), e
pode rodar dentro da própria verificação de si mesma (gate de saída do modo `implement`).
"""

from __future__ import annotations

import importlib
import os
import sys
import tempfile
import unittest
from datetime import date
from pathlib import Path
from types import SimpleNamespace
from unittest import mock

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import empacotar

_NOMES_ISOLADOS = (
    "lib",
    "regioes",
    "numeracao",
    "nomenclatura",
    "porte",
    "bootstrap",
    "scaffold",
    "lint_unidade",
    "verificacao",
    "backlog",
)


def _carregar_pacote(scripts_dir: Path) -> tuple[SimpleNamespace, "callable"]:
    """Importa os módulos do mecanismo a partir de `scripts_dir`, isolados do que a suíte já tem
    em `sys.modules` vindo do repositório. Devolve o namespace carregado e a função que desfaz a
    troca — chamada em `tearDownModule`, e também no próprio `except` se o import falhar no meio.
    """
    originais = {nome: sys.modules.pop(nome, None) for nome in _NOMES_ISOLADOS}
    sys.path.insert(0, str(scripts_dir))

    def _restaurar() -> None:
        if str(scripts_dir) in sys.path:
            sys.path.remove(str(scripts_dir))
        for nome in _NOMES_ISOLADOS:
            sys.modules.pop(nome, None)
        for nome, modulo in originais.items():
            if modulo is not None:
                sys.modules[nome] = modulo

    try:
        modulos = {nome: importlib.import_module(nome) for nome in _NOMES_ISOLADOS}
    except BaseException:
        _restaurar()
        raise
    return SimpleNamespace(**modulos), _restaurar


_tmp_pacote: tempfile.TemporaryDirectory | None = None
_destino_pacote: Path | None = None
_restaurar_isolamento = None
pacote: SimpleNamespace | None = None


def setUpModule() -> None:
    global _tmp_pacote, _destino_pacote, _restaurar_isolamento, pacote
    _tmp_pacote = tempfile.TemporaryDirectory()
    _destino_pacote = Path(_tmp_pacote.name).resolve() / "pkg"
    empacotar.construir(_destino_pacote)

    scripts_dir = _destino_pacote / "skills" / "decode-and-code" / "scripts"
    pacote, _restaurar_isolamento = _carregar_pacote(scripts_dir)

    os.environ.pop(pacote.verificacao.SENTINELA_REENTRANCIA, None)


def tearDownModule() -> None:
    _restaurar_isolamento()
    _tmp_pacote.cleanup()


# Ignora o argumento — só precisa existir e sair 0 sem imprimir sinal de skip/zero-teste
# (`verificacao._execucao_incompleta`), para que o gate de saída promova a `verified`.
_RUNNER_STUB = "#!/bin/sh\necho 'Ran 1 test stub'\necho OK\nexit 0\n"

_PLANO = """\
---
name: ciclo-sintetico
type: plan
project: projeto-sintetico
plan_id: ""
core: builder
module: ciclo-sintetico
block: ""
status: draft
plan_size: grande
approved_by: Teste
approved_at: 2026-08-28
---

# Ciclo sintético

## Escopo

| # | Unidade | Responsabilidade |
|---|---|---|
| 01 | unidade-sintetica | existir só para o teste do ciclo instalado |

## Fonte

- Teste do ciclo instalado — unidade 0004-05.
"""

_UNIDADE = """\
---
name: unidade-sintetica
type: unit
project: projeto-sintetico
description: unidade sintética para o teste do ciclo instalado
tags: []

core: builder
module: ciclo-sintetico
block: ""
owner: builder
unit_id: 0001-01
unit_type: dev

state: spec
test: scripts/tests/test_unidade_sintetica.py
verified_at: ""

author: Teste
created: 2026-08-28
status: draft
version: 1.0.0
updated: ""

scope: project
auto_load: false
dependencies: []
---

# 0001-01 — unidade-sintetica

**Responsabilidade:** existir só para o teste do ciclo instalado.

## Contrato

| Campo | Detalhe |
|---|---|
| Entrada | Nenhuma |

## Sequência

1. Passo único, sintético.

## Arquivos

| Caminho | O que muda |
|---|---|
| `scripts/algo.py` | sintético |

## Dependências

Nenhuma.

## Normas aplicáveis

| Norma | Onde |
|---|---|
| Exemplo | em algum lugar |

## Critério de aceite

O teste declarado passa pelo runner que o projeto declara.

## Verificação

Rodada por `scripts/test-python.sh`, o runner que o projeto declara em `runners`.
"""


def _bootstrap_e_stub_de_runner(projeto: Path) -> None:
    """Bootstrap mais o stub de runner que a unidade prevê (`D-05`) — o projeto declara o seu."""
    pacote.bootstrap.iniciar(projeto)
    runner = projeto / "scripts" / "test-python.sh"
    runner.parent.mkdir(parents=True, exist_ok=True)
    runner.write_text(_RUNNER_STUB, encoding="utf-8")
    runner.chmod(0o755)


def _escrever_plano_no_inbox(projeto: Path) -> Path:
    caminho = projeto / "docs" / "plan" / "_inbox" / "ciclo-sintetico.md"
    caminho.parent.mkdir(parents=True, exist_ok=True)
    caminho.write_text(_PLANO, encoding="utf-8")
    return caminho


def _escrever_unidade_e_alvo_do_teste(dir_plano: Path, projeto: Path) -> Path:
    unidade = dir_plano / "01-unidade-sintetica.md"
    unidade.write_text(_UNIDADE, encoding="utf-8")

    teste = projeto / "scripts" / "tests" / "test_unidade_sintetica.py"
    teste.parent.mkdir(parents=True, exist_ok=True)
    teste.write_text(
        "# stub — nunca executado diretamente; o runner ignora o conteúdo\n", encoding="utf-8"
    )
    return unidade


class TestModulosVemDoPacote(unittest.TestCase):
    """Critério de aceite: o `__file__` do módulo usado está dentro do pacote, não do repositório."""

    def test_lib_carregado_e_do_pacote_nao_do_repositorio(self):
        repo_real = str(empacotar.lib.repo_root())
        caminho_carregado = str(Path(pacote.lib.__file__).resolve())

        self.assertTrue(caminho_carregado.startswith(str(_destino_pacote)), caminho_carregado)
        self.assertFalse(caminho_carregado.startswith(repo_real), caminho_carregado)


class TestCicloCompleto(unittest.TestCase):
    """Os seis passos, encadeados — cada um afirmado antes do próximo."""

    def test_bootstrap_aprovar_lint_verificar_fechar(self):
        with tempfile.TemporaryDirectory() as tmp:
            projeto = Path(tmp).resolve()

            # 1 — bootstrap: a estrutura e a norma chegam ao projeto.
            _bootstrap_e_stub_de_runner(projeto)
            self.assertTrue((projeto / ".claude").is_dir())
            self.assertTrue((projeto / "docs" / "plan" / "_planos.md").is_file())
            self.assertTrue(
                (projeto / "docs" / "plan" / "system" / "modelo-dev-units.md").is_file()
            )

            plano = _escrever_plano_no_inbox(projeto)

            with (
                mock.patch.object(pacote.lib, "repo_root", return_value=projeto),
                mock.patch.object(pacote.scaffold.move_md, "REPO_ROOT", projeto),
                mock.patch.object(
                    pacote.scaffold.move_md, "esta_versionado", return_value=False
                ) as versionado_mock,
                mock.patch.object(
                    pacote.porte, "_linhas_alteradas", return_value=(3, None)
                ) as linhas_mock,
            ):
                # 2 — scaffold.aprovar: numeração, movimentação e a linha em _planos.md.
                alvo = pacote.scaffold.aprovar(plano)
                self.assertEqual(
                    alvo,
                    projeto
                    / "docs" / "plan" / "builder" / "0001-ciclo-sintetico" / "0001-ciclo-sintetico.md",
                )
                self.assertTrue(alvo.is_file())
                versionado_mock.assert_called()

                planos_md = projeto / "docs" / "plan" / "_planos.md"
                miolo_planos = pacote.regioes.ler_regiao(planos_md, "planos")
                self.assertIn("0001-ciclo-sintetico", miolo_planos)

                # 3 — unidade escrita, e lint_unidade.lint: o gate de entrada aceita.
                unidade = _escrever_unidade_e_alvo_do_teste(alvo.parent, projeto)
                self.assertEqual(pacote.lint_unidade.lint(unidade), [])

                # 4 — verificacao.verificar: o gate de saída roda o runner do projeto e projeta state.
                estado, escreveu = pacote.verificacao.verificar(unidade)
                self.assertEqual(estado, "verified")
                self.assertTrue(escreveu)
                self.assertEqual(
                    pacote.regioes.ler_campo(unidade, "verified_at"), date.today().isoformat()
                )

                # 5 — backlog.projetar: a situação vira concluído, e o plano ganha status: done.
                _texto_backlog, situacao = pacote.backlog.projetar(alvo.parent)
                self.assertEqual(situacao, "concluído")
                linhas_mock.assert_called()

                # 6 — fechamento: status: done no plano, situação projetada em _planos.md e a
                # linha de porte-medido.md — sem nenhuma chamada real a git nos dois pontos mockados.
                self.assertEqual(pacote.regioes.ler_campo(alvo, "status"), "done")

                miolo_planos_final = pacote.regioes.ler_regiao(planos_md, "planos")
                linha_do_plano = next(
                    linha for linha in miolo_planos_final.split("\n") if "0001-ciclo-sintetico" in linha
                )
                self.assertIn("concluído", linha_do_plano)

                porte_medido = projeto / "docs" / "plan" / "system" / "porte-medido.md"
                self.assertTrue(porte_medido.is_file())
                self.assertIn("ciclo-sintetico", porte_medido.read_text(encoding="utf-8"))


class TestSemBootstrapScaffoldAprovarFalha(unittest.TestCase):
    """O caso negativo — o defeito que abriu o plano `0004`, preso num teste (`## Escopo`, *O que
    foi medido*: `scaffold.aprovar` morre com `FileNotFoundError` em `_planos.md` num projeto zerado)."""

    def test_scaffold_aprovar_levanta_sem_bootstrap(self):
        with tempfile.TemporaryDirectory() as tmp:
            projeto_cru = Path(tmp).resolve()
            plano = _escrever_plano_no_inbox(projeto_cru)

            with mock.patch.object(pacote.lib, "repo_root", return_value=projeto_cru):
                with self.assertRaises(FileNotFoundError):
                    pacote.scaffold.aprovar(plano)


if __name__ == "__main__":
    unittest.main()
