#!/usr/bin/env python3
"""Testes do porte e da raiz dos planos no formato 2 — subparte 2.2.05 do redesign (K-03).

Codex, *Porte*: o pequeno tem tarefas e nenhuma unidade; o médio, uma unidade; o grande, duas ou
mais. *Raiz dos planos*: sem pasta por parte do sistema — o pequeno é arquivo, médio e grande são
pasta. *Independência entre planos*: todo plano a declara. O plano do formato 1 segue a regra de
antes, e os testes dele continuam nos arquivos de sempre.
"""

from __future__ import annotations

import sys
import tempfile
import unittest
from pathlib import Path
from unittest import mock

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import backlog
import lib
import lint_plano
import nomenclatura
import porte
import regioes
import scaffold

CABECALHO = "| # | Plano | Core | Módulo | Origem | Situação | Aprovado |\n|---|---|---|---|---|---|---|\n"


def _texto(
    plan_size: str,
    *,
    unidades: int | None = None,
    tarefas: bool = False,
    sem: tuple[str, ...] = (),
    core: str | None = None,
    plan_id: str = '""',
    status: str = "draft",
    backlog_regiao: bool = False,
) -> str:
    linhas = ["---", f"plan_id: {plan_id}", f"status: {status}", f"plan_size: {plan_size}",
              "plan_type: feature", "format_version: 2", "approved_by: Teste",
              "approved_at: 2026-11-27"]
    if core:
        linhas.append(f"core: {core}")
    linhas += ["---", "", "# exemplo", ""]
    secoes = {
        "Objetivo": "Uma frase.",
        "Histórias": "Como quem usa, quero algo, para um fim.",
        "Independência": "Um plano só: sem a parte A, a B não serve.",
        "Recursos": "Nenhum recurso do projeto.",
    }
    for nome, corpo in secoes.items():
        if nome not in sem:
            linhas += [f"## {nome}", "", corpo, ""]
    if tarefas:
        linhas += ["## Tarefas", "", "- [x] fazer a coisa", "- [ ] conferir", ""]
    if unidades is not None:
        linhas += ["## Unidades", "", "| # | Unidade | Entrega |", "|---|---|---|"]
        linhas += [f"| {i} | u{i} | e{i} |" for i in range(1, unidades + 1)] + [""]
    if backlog_regiao:
        linhas += ["## Backlog", "", "<!-- backlog:start -->", "<!-- backlog:end -->", ""]
    return "\n".join(linhas) + "\n"


class _Raiz(unittest.TestCase):
    def setUp(self) -> None:
        self._tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self._tmp.cleanup)
        self.raiz = Path(self._tmp.name).resolve()
        (self.raiz / "_inbox").mkdir()
        (self.raiz / "system").mkdir()
        (self.raiz / "_planos.md").write_text(
            f"<!-- planos:start -->\n{CABECALHO}<!-- planos:end -->\n", encoding="utf-8"
        )
        for alvo, valor in ((lib, "plan_root"),):
            p = mock.patch.object(alvo, valor, return_value=self.raiz)
            p.start()
            self.addCleanup(p.stop)
        for nome, valor in (("REPO_ROOT", self.raiz), ("esta_versionado", lambda *a, **k: False)):
            p = mock.patch.object(scaffold.move_md, nome, valor)
            p.start()
            self.addCleanup(p.stop)

    def escrever(self, caminho: Path, texto: str) -> Path:
        caminho.parent.mkdir(parents=True, exist_ok=True)
        caminho.write_text(texto, encoding="utf-8")
        return caminho


class TestLintPlanoFormatoAtual(_Raiz):
    def _lint(self, texto: str) -> list[str]:
        return lint_plano.lint(self.escrever(self.raiz / "_inbox" / "exemplo.md", texto))

    def test_pequeno_com_tarefas_aprova(self) -> None:
        self.assertEqual(self._lint(_texto("pequeno", tarefas=True)), [])

    def test_pequeno_com_unidades_reprova(self) -> None:
        problemas = self._lint(_texto("pequeno", tarefas=True, unidades=1))
        self.assertTrue(any("pequeno não tem unidade" in p for p in problemas), problemas)

    def test_pequeno_sem_tarefas_reprova(self) -> None:
        self.assertIn("pequeno exige '## Tarefas'", self._lint(_texto("pequeno")))

    def test_medio_com_uma_unidade_aprova(self) -> None:
        self.assertEqual(self._lint(_texto("médio", unidades=1)), [])

    def test_medio_com_duas_unidades_reprova(self) -> None:
        problemas = self._lint(_texto("médio", unidades=2))
        self.assertTrue(any("exatamente 1 unidade" in p for p in problemas), problemas)

    def test_grande_com_uma_unidade_reprova(self) -> None:
        problemas = self._lint(_texto("grande", unidades=1))
        self.assertTrue(any("duas ou mais" in p for p in problemas), problemas)

    def test_grande_com_duas_aprova(self) -> None:
        self.assertEqual(self._lint(_texto("grande", unidades=2)), [])

    def test_independencia_vale_em_todo_porte(self) -> None:
        for porte_, extra in (("pequeno", {"tarefas": True}), ("médio", {"unidades": 1})):
            with self.subTest(porte=porte_):
                problemas = self._lint(_texto(porte_, sem=("Independência",), **extra))
                self.assertIn("formato 2 exige '## Independência'", problemas)

    def test_cada_secao_obrigatoria_falta_sozinha(self) -> None:
        for secao in lint_plano.SECOES_DO_FORMATO_ATUAL:
            with self.subTest(secao=secao):
                problemas = self._lint(_texto("médio", unidades=1, sem=(secao,)))
                self.assertEqual(problemas, [f"formato 2 exige '## {secao}'"])


class TestAprovarFormatoAtual(_Raiz):
    def _plano(self, plan_size: str, **extra) -> Path:
        return self.escrever(self.raiz / "_inbox" / "add-coisa.md", _texto(plan_size, **extra))

    def test_pequeno_vai_para_a_raiz_como_arquivo(self) -> None:
        alvo = scaffold.aprovar(self._plano("pequeno", tarefas=True))
        self.assertEqual(alvo, self.raiz / "0001-add-coisa.md")
        self.assertTrue(alvo.is_file())
        self.assertIsNone(regioes.ler_regiao(alvo, "backlog"))

    def test_medio_vai_para_uma_pasta_na_raiz_com_backlog(self) -> None:
        alvo = scaffold.aprovar(self._plano("médio", unidades=1))
        self.assertEqual(alvo, self.raiz / "0001-add-coisa" / "0001-add-coisa.md")
        self.assertIsNotNone(regioes.ler_regiao(alvo, "backlog"))

    def test_sem_core_aprova_e_a_tabela_mostra_traco(self) -> None:
        scaffold.aprovar(self._plano("grande", unidades=2))
        linha = [l for l in (self.raiz / "_planos.md").read_text(encoding="utf-8").splitlines()
                 if l.startswith("| 0001")][0]
        self.assertIn("| [add-coisa](0001-add-coisa/0001-add-coisa.md) | — |", linha)

    def test_core_declarado_nao_vira_pasta(self) -> None:
        alvo = scaffold.aprovar(self._plano("médio", unidades=1, core="builder"))
        self.assertEqual(alvo.parent.parent, self.raiz)
        self.assertFalse((self.raiz / "builder").exists())

    def test_formato_1_sem_core_continua_recusado(self) -> None:
        texto = _texto("pequeno", tarefas=True).replace("format_version: 2\n", "")
        plano = self.escrever(self.raiz / "_inbox" / "add-coisa.md", texto)
        with self.assertRaises(ValueError) as erro:
            scaffold.aprovar(plano, dry_run=True)
        self.assertIn("core", str(erro.exception))


class TestBacklogEPorteFormatoAtual(_Raiz):
    def _aprovado(self, plan_size: str, **extra) -> Path:
        plano = self.escrever(self.raiz / "_inbox" / "add-coisa.md", _texto(plan_size, **extra))
        return scaffold.aprovar(plano)

    def _unidade(self, pasta: Path, n: int, state: str, approved_at: str = '""') -> None:
        self.escrever(pasta / f"0{n}-u{n}.md",
                      f"---\nunit_id: 0001-0{n}\nstate: {state}\napproved_at: {approved_at}\n---\n\n# u{n}\n")

    def test_medio_fecha_com_o_teste_e_a_aprovacao_da_entrega(self) -> None:
        alvo = self._aprovado("médio", unidades=1)
        self._unidade(alvo.parent, 1, "spec")
        _, situacao = backlog.projetar(alvo.parent, dry_run=True)
        self.assertEqual(situacao, "em desenvolvimento")
        self._unidade(alvo.parent, 1, "verified")
        _, situacao = backlog.projetar(alvo.parent, dry_run=True)
        self.assertEqual(situacao, "em desenvolvimento", "verde sem aprovação não fecha (P7)")
        self._unidade(alvo.parent, 1, "verified", approved_at="2026-11-27")
        conteudo, situacao = backlog.projetar(alvo.parent, dry_run=True)
        self.assertEqual(situacao, "concluído")
        self.assertIn("0001-01", conteudo)

    def test_grande_so_fecha_com_todas_as_previstas(self) -> None:
        alvo = self._aprovado("grande", unidades=2)
        self._unidade(alvo.parent, 1, "verified")
        self.assertEqual(backlog.projetar(alvo.parent, dry_run=True)[1], "em desenvolvimento")

    def test_porte_do_medio_conta_a_unidade(self) -> None:
        alvo = self._aprovado("médio", unidades=1)
        self._unidade(alvo.parent, 1, "verified")
        self.assertEqual(porte.medir(alvo.parent)["unidades_ou_tarefas"], 1)

    def test_porte_do_pequeno_conta_as_tarefas(self) -> None:
        alvo = self._aprovado("pequeno", tarefas=True)
        medida = porte.medir(alvo)
        self.assertEqual(medida["unidades_ou_tarefas"], 2)
        self.assertIsNone(medida["arquivos_declarados"])


class TestColisaoNaRaiz(_Raiz):
    def test_colide_com_plano_aprovado_na_raiz(self) -> None:
        self.escrever(self.raiz / "0003-add-coisa" / "0003-add-coisa.md", "x\n")
        self.assertEqual(nomenclatura.ha_colisao("add-coisa", None), self.raiz / "0003-add-coisa")

    def test_colide_com_rascunho_no_inbox(self) -> None:
        self.escrever(self.raiz / "_inbox" / "add-coisa.md", "x\n")
        self.assertIsNotNone(nomenclatura.ha_colisao("add-coisa", None))

    def test_sem_colisao(self) -> None:
        self.assertIsNone(nomenclatura.ha_colisao("add-outra", None))


if __name__ == "__main__":
    unittest.main()
