#!/usr/bin/env python3
"""Teste declarado da unidade 0001-14 — o `derive` ramifica por `plan_size`.

Quatro frentes, uma por oráculo que a unidade fecha:

- `scaffold.aprovar` — pequeno e médio produzem `<core>/<NNNN>-<nome>.md` **sem** subpasta nova
  (`TestAlvoPorPorte`); grande continua com subpasta, como hoje.
- `backlog.projetar` no pequeno — nunca escreve região de backlog, nunca levanta por marcador
  ausente, e a situação vem de `status` (`TestBacklogPequeno`).
- `backlog.projetar` no médio — a região espelha `## Tarefas`, e a situação só conclui com ao
  menos uma tarefa e todas marcadas (`TestBacklogMedio`).
- `backlog.projetar` no grande — quem decide o ramo é o `plan_size` **declarado**, e a forma do
  `alvo` só localiza o arquivo; porte ausente cai no grande e falha alto. O plano real `0001`
  prova a não-regressão, e que passá-lo como arquivo dá o mesmo que passá-lo como diretório
  (`TestBacklogGrande`).

Árvore inteiramente temporária, como em `test_situacao.py` — só o teste do plano real `0001` lê o
repositório de verdade, e em `dry_run`, sem escrever nada.
"""

from __future__ import annotations

import sys
import tempfile
import unittest
from pathlib import Path
from unittest import mock

sys.path.insert(0, str(Path(__file__).resolve().parent))
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import backlog
import fixtures
import lib
import regioes
import scaffold

CABECALHO_TABELA = (
    "| # | Plano | Core | Módulo | Origem | Situação | Aprovado |\n"
    "|---|---|---|---|---|---|---|\n"
)

PLANO_REAL_0001 = (
    lib.repo_root()
    / "docs"
    / "plan"
    / "model"
    / "0001-decode-and-code-foundation"
    / "0001-decode-and-code-foundation.md"
)

DIR_UNIDADES_REAIS = PLANO_REAL_0001.parent


def _inserir_tarefas(arquivo: Path, itens: list[tuple[bool, str]]) -> None:
    """Substitui o corpo do plano por uma `## Tarefas` com os itens dados, antes do `## Backlog`."""
    linhas = "\n".join(f"- [{'x' if feita else ' '}] {texto}" for feita, texto in itens)
    bloco = f"## Tarefas\n\n{linhas}\n\n"
    texto = arquivo.read_text(encoding="utf-8")
    arquivo.write_text(texto.replace("## Backlog", bloco + "## Backlog"), encoding="utf-8")


class _BaseComRaizTemporaria(unittest.TestCase):
    """`_inbox/` e `_planos.md` vazios, com `plan_root`/`REPO_ROOT` mockados — mesmo padrão de
    `test_porte_e_aprovacao.py`."""

    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self._tmp.cleanup)
        self.raiz = Path(self._tmp.name).resolve()

        (self.raiz / "_inbox").mkdir()
        self.planos_md = self.raiz / "_planos.md"
        self.planos_md.write_text(
            f"<!-- planos:start -->\n{CABECALHO_TABELA}<!-- planos:end -->\n", encoding="utf-8"
        )

        patcher_plan_root = mock.patch.object(lib, "plan_root", return_value=self.raiz)
        patcher_plan_root.start()
        self.addCleanup(patcher_plan_root.stop)

        patcher_repo_root = mock.patch.object(scaffold.move_md, "REPO_ROOT", self.raiz)
        patcher_repo_root.start()
        self.addCleanup(patcher_repo_root.stop)

    def _escrever_plano_inbox(self, nome: str, plan_size: str) -> Path:
        plano = self.raiz / "_inbox" / f"{nome}.md"
        plano.write_text(
            "---\n"
            'plan_id: ""\n'
            "core: builder\n"
            f"module: {nome}\n"
            'block: ""\n'
            "status: draft\n"
            f"plan_size: {plan_size}\n"
            "approved_by: Teste\n"
            "approved_at: 2026-08-25\n"
            "---\n\n"
            f"# {nome}\n",
            encoding="utf-8",
        )
        return plano


class TestAlvoPorPorte(_BaseComRaizTemporaria):
    """Critério de aceite: pequeno e médio produzem arquivo sem diretório novo — o teste afirma
    a ausência da pasta, não só a presença do arquivo. Grande não muda."""

    def test_pequeno_produz_arquivo_sem_diretorio_novo(self):
        plano = self._escrever_plano_inbox("plano-pequeno", "pequeno")

        alvo = scaffold.aprovar(plano)

        self.assertEqual(alvo, self.raiz / "builder" / "0001-plano-pequeno.md")
        self.assertTrue(alvo.is_file())
        self.assertFalse((self.raiz / "builder" / "0001-plano-pequeno").exists())

    def test_medio_produz_arquivo_sem_diretorio_novo(self):
        plano = self._escrever_plano_inbox("plano-medio", "médio")

        alvo = scaffold.aprovar(plano)

        self.assertEqual(alvo, self.raiz / "builder" / "0001-plano-medio.md")
        self.assertTrue(alvo.is_file())
        self.assertFalse((self.raiz / "builder" / "0001-plano-medio").exists())

    def test_grande_produz_diretorio_e_arquivo_dentro_como_hoje(self):
        plano = self._escrever_plano_inbox("plano-grande", "grande")

        alvo = scaffold.aprovar(plano)

        self.assertEqual(
            alvo, self.raiz / "builder" / "0001-plano-grande" / "0001-plano-grande.md"
        )
        self.assertTrue(alvo.is_file())

    def test_pequeno_nao_ganha_secao_de_backlog(self):
        plano = self._escrever_plano_inbox("plano-pequeno-b", "pequeno")

        alvo = scaffold.aprovar(plano)

        self.assertNotIn("## Backlog", alvo.read_text(encoding="utf-8"))
        self.assertIsNone(regioes.ler_regiao(alvo, "backlog"))

    def test_medio_ganha_secao_de_backlog(self):
        plano = self._escrever_plano_inbox("plano-medio-b", "médio")

        alvo = scaffold.aprovar(plano)

        self.assertIn("## Backlog", alvo.read_text(encoding="utf-8"))
        self.assertIsNotNone(regioes.ler_regiao(alvo, "backlog"))


class _BaseBacklogSemDiretorio(unittest.TestCase):
    """Plano pequeno/médio real — sem diretório —, mais a linha correspondente em `_planos.md`."""

    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self._tmp.cleanup)
        self.raiz = Path(self._tmp.name).resolve()

        patcher = mock.patch.object(lib, "plan_root", return_value=self.raiz)
        patcher.start()
        self.addCleanup(patcher.stop)

    def _montar(self, *, plan_size: str, status: str = "approved", com_backlog: bool = False) -> Path:
        arquivo = fixtures.plano(
            self.raiz,
            core="builder",
            nome="exemplo",
            numero="0009",
            plan_size=plan_size,
            status=status,
            com_backlog=com_backlog,
            com_diretorio=False,
        )
        href = "builder/0009-exemplo.md"
        linha = f"| 0009 | [exemplo]({href}) | builder | exemplo | — | em desenvolvimento | 2026-08-24 |\n"
        fixtures.planos_md(self.raiz, linhas=[linha])
        return arquivo


class TestBacklogPequeno(_BaseBacklogSemDiretorio):
    """Critério de aceite: não escreve região nenhuma, não levanta por marcador ausente, e a
    situação vem de `status` — `approved` → `em desenvolvimento`, `done` → `concluído`."""

    def test_nao_escreve_regiao_e_nao_levanta_por_marcador_ausente(self):
        arquivo = self._montar(plan_size="pequeno", status="approved")

        backlog_texto, situacao = backlog.projetar(arquivo)

        self.assertEqual(backlog_texto, "")
        self.assertEqual(situacao, "em desenvolvimento")
        self.assertIsNone(regioes.ler_regiao(arquivo, "backlog"))

    def test_status_approved_projeta_em_desenvolvimento(self):
        arquivo = self._montar(plan_size="pequeno", status="approved")

        _, situacao = backlog.projetar(arquivo)

        self.assertEqual(situacao, "em desenvolvimento")

    def test_status_done_projeta_concluido(self):
        arquivo = self._montar(plan_size="pequeno", status="done")

        _, situacao = backlog.projetar(arquivo)

        self.assertEqual(situacao, "concluído")

    def test_status_fora_do_vocabulario_nunca_projeta_concluido(self):
        arquivo = self._montar(plan_size="pequeno", status="draft")

        _, situacao = backlog.projetar(arquivo)

        self.assertEqual(situacao, "em desenvolvimento")

    def test_status_vazio_nunca_projeta_concluido(self):
        arquivo = self._montar(plan_size="pequeno", status="")

        _, situacao = backlog.projetar(arquivo)

        self.assertEqual(situacao, "em desenvolvimento")

    def test_planos_md_recebe_a_situacao_projetada(self):
        arquivo = self._montar(plan_size="pequeno", status="done")

        backlog.projetar(arquivo)

        conteudo = self.raiz.joinpath("_planos.md").read_text(encoding="utf-8")
        self.assertIn(
            "| 0009 | [exemplo](builder/0009-exemplo.md) | builder | exemplo | — | concluído"
            " | 2026-08-24 |",
            conteudo,
        )

    def test_dry_run_nao_escreve_planos_md(self):
        arquivo = self._montar(plan_size="pequeno", status="done")
        antes = self.raiz.joinpath("_planos.md").read_text(encoding="utf-8")

        backlog.projetar(arquivo, dry_run=True)

        self.assertEqual(self.raiz.joinpath("_planos.md").read_text(encoding="utf-8"), antes)


class TestBacklogMedio(_BaseBacklogSemDiretorio):
    """Critério de aceite: a região recebe as tarefas de `## Tarefas`, e a situação só conclui
    com ao menos uma tarefa e todas marcadas."""

    def test_regiao_recebe_as_tarefas_marcadas_e_pendentes(self):
        arquivo = self._montar(plan_size="médio", com_backlog=True)
        _inserir_tarefas(arquivo, [(True, "Primeira"), (False, "Segunda")])

        backlog_texto, _ = backlog.projetar(arquivo)

        self.assertIn("- [x] Primeira", backlog_texto)
        self.assertIn("- [ ] Segunda", backlog_texto)

    def test_escreve_a_regiao_no_arquivo(self):
        arquivo = self._montar(plan_size="médio", com_backlog=True)
        _inserir_tarefas(arquivo, [(True, "Única")])

        backlog.projetar(arquivo)

        self.assertIn("- [x] Única", regioes.ler_regiao(arquivo, "backlog"))

    def test_situacao_concluido_com_ao_menos_uma_e_todas_marcadas(self):
        arquivo = self._montar(plan_size="médio", com_backlog=True)
        _inserir_tarefas(arquivo, [(True, "Única")])

        _, situacao = backlog.projetar(arquivo)

        self.assertEqual(situacao, "concluído")

    def test_situacao_nao_conclui_com_tarefa_pendente(self):
        arquivo = self._montar(plan_size="médio", com_backlog=True)
        _inserir_tarefas(arquivo, [(True, "Primeira"), (False, "Segunda")])

        _, situacao = backlog.projetar(arquivo)

        self.assertEqual(situacao, "em desenvolvimento")

    def test_sem_secao_tarefas_nunca_projeta_concluido(self):
        arquivo = self._montar(plan_size="médio", com_backlog=True)

        _, situacao = backlog.projetar(arquivo)

        self.assertEqual(situacao, "em desenvolvimento")

    def test_sem_regiao_de_backlog_levanta_value_error(self):
        arquivo = self._montar(plan_size="médio", com_backlog=False)
        _inserir_tarefas(arquivo, [(True, "Única")])

        with self.assertRaises(ValueError):
            backlog.projetar(arquivo)


class TestBacklogGrande(unittest.TestCase):
    """Critério de aceite: no grande, backlog e situação saem idênticos aos de hoje — e o ramo vem
    do porte **declarado**, não da forma do `alvo`.

    A primeira implementação ramificava pela forma, e a revisão de 2026-08-25 mediu o efeito no
    plano real `0001`: passado como arquivo em vez de diretório, ele projetava região vazia e
    situação lida de `status`, sem levantar. Projeção errada que parece certa é a `L-18`.
    """

    def test_porte_declarado_vence_a_forma_do_alvo(self):
        """Diretório declarando `pequeno` projeta como pequeno — o campo é o fato, a forma é
        consequência. Antes da correção, este mesmo caso projetava como grande."""
        with tempfile.TemporaryDirectory() as tmp:
            raiz = Path(tmp).resolve()
            with mock.patch.object(lib, "plan_root", return_value=raiz):
                dir_plano = fixtures.plano(
                    raiz,
                    core="builder",
                    nome="exemplo",
                    numero="0009",
                    plan_size="pequeno",
                    previstas=1,
                )
                fixtures.unidade(dir_plano, nome="01-a.md", unit_id="0009-01", state="verified")
                fixtures.planos_md(raiz)

                backlog_texto, situacao = backlog.projetar(dir_plano)

        self.assertEqual(backlog_texto, "")
        self.assertEqual(situacao, "em desenvolvimento")

    def test_porte_ausente_cai_no_grande_e_falha_alto(self):
        """Sem `plan_size` legível, o ramo é o do grande — que levanta por marcador ausente. Cair
        no pequeno projetaria de `status` em silêncio, que é o defeito que a correção fecha."""
        with tempfile.TemporaryDirectory() as tmp:
            raiz = Path(tmp).resolve()
            with mock.patch.object(lib, "plan_root", return_value=raiz):
                dir_plano = fixtures.plano(
                    raiz,
                    core="builder",
                    nome="exemplo",
                    numero="0009",
                    plan_size='""',
                    com_backlog=False,
                )
                fixtures.planos_md(raiz)

                with self.assertRaisesRegex(ValueError, "marcador 'backlog' não existe"):
                    backlog.projetar(dir_plano)

    def test_plano_real_0001_como_arquivo_projeta_igual_ao_diretorio(self):
        """O defeito medido na revisão: como arquivo, o grande devolvia `('', 'em
        desenvolvimento')` em vez do backlog real."""
        por_arquivo = backlog.projetar(PLANO_REAL_0001, dry_run=True)
        por_diretorio = backlog.projetar(DIR_UNIDADES_REAIS, dry_run=True)

        self.assertEqual(por_arquivo, por_diretorio)
        self.assertIn("[0001-01]", por_arquivo[0])

    def test_plano_real_0001_projeta_sem_levantar_e_sem_regredir(self):
        backlog_texto, situacao = backlog.projetar(DIR_UNIDADES_REAIS, dry_run=True)

        self.assertIn("| Unidade | Título | Estado |", backlog_texto)
        self.assertIn("[0001-01]", backlog_texto)
        self.assertEqual(situacao, "em desenvolvimento")

    def test_plano_real_0001_dry_run_e_deterministico(self):
        primeira = backlog.projetar(DIR_UNIDADES_REAIS, dry_run=True)
        segunda = backlog.projetar(DIR_UNIDADES_REAIS, dry_run=True)

        self.assertEqual(primeira, segunda)


if __name__ == "__main__":
    unittest.main()
