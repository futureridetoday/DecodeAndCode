#!/usr/bin/env python3
"""Testes do plano 0024 — a proposta em forma de PRD no plano grande.

H1: o `lint-plano` exige, no grande do formato 2, as três seções `###` dentro de `## Proposta` e
`## Teste do plano inteiro`. H2: com unidades no disco, cada `R-NN` declarado tem dono, e o
`lint-unidade` recusa a citação de um `R-NN` que o plano não declara.
"""

from __future__ import annotations

import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import lint_plano
import lint_unidade

SECOES = {
    "Métricas de sucesso": "- tempo: hoje 10 s, alvo 2 s, medido no log",
    "Requisitos não funcionais e restrições": "- **R-01** compatível com Python 3.10\n- R-02 sem dependência nova",
    "Fases de entrega": "- Fase 1: o usuário vê a proposta completa",
}


def _plano(
    tamanho: str = "grande",
    *,
    sem: tuple[str, ...] = (),
    teste_inteiro: str | None = "Confere as fases.",
    formato: int | None = 2,
    unidades: int = 2,
) -> str:
    cab = ["---", 'plan_id: "0001"', "status: approved", f"plan_size: {tamanho}", "plan_type: feature"]
    if formato:
        cab.append(f"format_version: {formato}")
    if tamanho == "pequeno":
        cab += ["test: tests/test_x.py", "state: spec", 'verified_at: ""']
    linhas = cab + ["---", "", "# x", "", "## Objetivo", "", "Uma frase.", "", "## Proposta", ""]
    for nome, corpo in SECOES.items():
        if nome not in sem:
            linhas += [f"### {nome}", "", corpo, ""]
    linhas += ["## Histórias", "", "H1.", "", "## Independência", "", "Um plano.", "",
               "## Recursos", "", "Nenhum.", ""]
    if tamanho == "pequeno":
        linhas += ["## Tarefas", "", "- [ ] fazer", ""]
    else:
        linhas += ["## Unidades", "", "| # | Unidade | Entrega |", "|---|---|---|"]
        linhas += [f"| {i} | u{i} | e{i} |" for i in range(1, unidades + 1)] + [""]
        if teste_inteiro is not None:
            linhas += ["## Teste do plano inteiro", "", teste_inteiro, ""]
    return "\n".join(linhas) + "\n"


def _unidade(numero: str, criterio: str) -> str:
    return (
        f"---\nunit_id: 0001-{numero}\nunit_type: dev\nstate: spec\ntest: tests/test_a.py\n"
        'verified_at: ""\napproved_by: ""\napproved_at: ""\n---\n\n# u\n\n'
        f"## História\n\nComo quem usa, quero algo.\n\n## Critério de aceite\n\n{criterio}\n\n"
        "## Tarefas\n\n- fazer\n\n## Arquivos\n\n| Arquivo | O quê |\n|---|---|\n| `src/a.py` | criar |\n\n"
        "## Guidelines\n\nnenhuma\n\n## Recursos\n\nnenhum\n\n## Decisões e lacunas\n\nnenhuma\n\n"
        "## Depende de\n\nnada\n"
    )


class _Base(unittest.TestCase):
    def setUp(self) -> None:
        self._tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self._tmp.cleanup)
        self.pasta = Path(self._tmp.name) / "0001-exemplo"
        self.pasta.mkdir()
        self.plano = self.pasta / "0001-exemplo.md"

    def escrever_plano(self, texto: str) -> Path:
        self.plano.write_text(texto, encoding="utf-8")
        return self.plano

    def escrever_unidade(self, numero: str, criterio: str) -> Path:
        caminho = self.pasta / f"{numero}-u.md"
        caminho.write_text(_unidade(numero, criterio), encoding="utf-8")
        return caminho


class TestH1SecoesDoGrande(_Base):
    def _lint(self, texto: str) -> list[str]:
        return lint_plano.lint(self.escrever_plano(texto))

    def test_grande_com_as_quatro_aprova(self) -> None:
        self.assertEqual(self._lint(_plano()), [])

    def test_cada_secao_ausente_reprova(self) -> None:
        for nome in SECOES:
            with self.subTest(secao=nome):
                problemas = self._lint(_plano(sem=(nome,)))
                self.assertEqual(len(problemas), 1, problemas)
                self.assertIn(nome, problemas[0])

    def test_sem_teste_do_plano_inteiro_reprova(self) -> None:
        problemas = self._lint(_plano(teste_inteiro=None))
        self.assertEqual(problemas, ["grande exige '## Teste do plano inteiro'"])

    def test_pequeno_sem_as_secoes_aprova(self) -> None:
        self.assertEqual(self._lint(_plano("pequeno", sem=tuple(SECOES))), [])

    def test_medio_sem_as_secoes_aprova(self) -> None:
        self.assertEqual(self._lint(_plano("médio", sem=tuple(SECOES), unidades=1)), [])

    def test_formato_1_nao_muda(self) -> None:
        texto = _plano(sem=tuple(SECOES), teste_inteiro=None, formato=None)
        self.assertFalse(any("Métricas" in p or "Teste do plano inteiro" in p for p in self._lint(texto)))


class TestH2DonoDaRestricao(_Base):
    def test_sem_unidades_nao_confere_dono(self) -> None:
        self.assertEqual(lint_plano.lint(self.escrever_plano(_plano())), [])

    def test_restricao_sem_dono_reprova(self) -> None:
        self.escrever_plano(_plano())
        self.escrever_unidade("01", "Cobre R-01.")
        self.escrever_unidade("02", "Sem citação.")
        problemas = lint_plano.lint(self.plano)
        self.assertEqual(len(problemas), 1, problemas)
        self.assertIn("R-02", problemas[0])

    def test_dono_na_unidade_ou_no_teste_do_plano_aprova(self) -> None:
        self.escrever_plano(_plano(teste_inteiro="Cobre R-02 no fim."))
        self.escrever_unidade("01", "Cobre R-01.")
        self.escrever_unidade("02", "Sem citação.")
        self.assertEqual(lint_plano.lint(self.plano), [])

    def test_citacao_fora_do_criterio_nao_e_dono(self) -> None:
        self.escrever_plano(_plano(teste_inteiro="Cobre R-02."))
        self.escrever_unidade("01", "Sem citação.")
        self.escrever_unidade("02", "Sem citação.")
        problemas = lint_plano.lint(self.plano)
        self.assertEqual(len(problemas), 1, problemas)
        self.assertIn("R-01", problemas[0])

    def test_lint_unidade_recusa_restricao_nao_declarada(self) -> None:
        self.escrever_plano(_plano())
        ok = self.escrever_unidade("01", "Cobre R-01.")
        ruim = self.escrever_unidade("02", "Cobre R-09.")
        self.assertEqual(lint_unidade.lint(ok), [])
        problemas = lint_unidade.lint(ruim)
        self.assertEqual(len(problemas), 1, problemas)
        self.assertIn("R-09", problemas[0])

    def test_lint_unidade_de_plano_medio_nao_confere(self) -> None:
        self.escrever_plano(_plano("médio", unidades=1))
        unidade = self.escrever_unidade("01", "Cobre R-09.")
        self.assertEqual(lint_unidade.lint(unidade), [])


if __name__ == "__main__":
    unittest.main()
