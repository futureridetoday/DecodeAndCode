#!/usr/bin/env python3
"""Testes do scaffold da aprovação — unidade 0002-05.

Árvore inteiramente temporária, como em test_nomenclatura.py e test_numeracao.py — mas aqui dois
pontos precisam ficar sob controle do teste ao mesmo tempo: `lib.plan_root` (do qual dependem
`core_dir`, `inbox` e `planos_md`) e `move_md.REPO_ROOT` (do qual depende a varredura de
referências externas). Os dois apontam para a mesma raiz temporária — o mesmo que test_move_md.py
já faz sozinho, com `REPO_ROOT`.

O plano de teste linka para `../system/norma.md`, e um arquivo externo linka de volta para o plano.
É o caso que falhou na execução manual do plano 0002 real: a direção de dentro foi lembrada, a de
fora não.

`plan_size: grande` nos três planos sintéticos (0001-14) — antes desta unidade o campo era só um
rótulo sem efeito, e valia `pequeno` por não importar; passou a decidir o alvo de `aprovar`, e o
que esta suíte verifica é justamente o alvo com subpasta (`self.alvo` com `<numero>-<nome>/` no
meio), que só o `grande` produz. `test_porte_e_aprovacao.py` é quem cobre `pequeno` de verdade.
"""

from __future__ import annotations

import sys
import tempfile
import unittest
from pathlib import Path
from unittest import mock

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import lib
import regioes
import scaffold

CABECALHO_TABELA = (
    "| # | Plano | Core | Módulo | Origem | Situação | Aprovado |\n"
    "|---|---|---|---|---|---|---|\n"
)


class TestAprovarCaminhoFeliz(unittest.TestCase):
    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self._tmp.cleanup)
        self.raiz = Path(self._tmp.name).resolve()

        (self.raiz / "_inbox").mkdir()
        (self.raiz / "system").mkdir()
        (self.raiz / "system" / "norma.md").write_text("# norma\n", encoding="utf-8")

        self.planos_md = self.raiz / "_planos.md"
        self.planos_md.write_text(
            "<!-- planos:start -->\n"
            f"{CABECALHO_TABELA}"
            "| 0001 | [outro](builder/0001-outro/0001-outro.md) | builder | outro"
            " | — | em desenvolvimento | 2026-07-01 |\n"
            "<!-- planos:end -->\n",
            encoding="utf-8",
        )

        self.plano = self.raiz / "_inbox" / "evolucao-tools.md"
        self.plano.write_text(
            "---\n"
            'plan_id: ""\n'
            "core: builder\n"
            "module: evolucao-tools\n"
            'block: ""\n'
            "status: draft\n"
            "plan_size: grande\n"
            "approved_by: Bortoli\n"
            "approved_at: 2026-08-24\n"
            "---\n\n"
            "# evolucao-tools\n\n"
            "ver [norma](../system/norma.md)\n",
            encoding="utf-8",
        )

        # Referência de fora para dentro — a direção que a execução manual esqueceu.
        self.externo = self.raiz / "system" / "outro-doc.md"
        self.externo.write_text(
            "cita o plano [aqui](../_inbox/evolucao-tools.md)\n", encoding="utf-8"
        )

        patcher_plan_root = mock.patch.object(lib, "plan_root", return_value=self.raiz)
        patcher_plan_root.start()
        self.addCleanup(patcher_plan_root.stop)

        patcher_repo_root = mock.patch.object(scaffold.move_md, "REPO_ROOT", self.raiz)
        patcher_repo_root.start()
        self.addCleanup(patcher_repo_root.stop)

        self.alvo = self.raiz / "builder" / "0002-evolucao-tools" / "0002-evolucao-tools.md"

    def test_move_o_plano_para_o_alvo(self):
        # Critério de aceite da unidade.
        alvo = scaffold.aprovar(self.plano)
        self.assertEqual(alvo, self.alvo)
        self.assertTrue(alvo.is_file())
        self.assertFalse(self.plano.exists())

    def test_links_internos_ganham_um_nivel(self):
        scaffold.aprovar(self.plano)
        conteudo = self.alvo.read_text(encoding="utf-8")
        self.assertIn("../../system/norma.md", conteudo)

    def test_referencia_externa_e_corrigida(self):
        # A direção que falhou na execução manual do plano 0002 real.
        scaffold.aprovar(self.plano)
        conteudo = self.externo.read_text(encoding="utf-8")
        self.assertIn("../builder/0002-evolucao-tools/0002-evolucao-tools.md", conteudo)
        self.assertNotIn("_inbox/evolucao-tools.md", conteudo)

    def test_plano_sai_com_a_regiao_de_backlog_pronta_para_projetar(self):
        # L-01 do plano 0006: sem os marcadores, backlog.projetar derruba o
        # último passo do derive. Plano nenhum os traz — nada os pedia.
        alvo = scaffold.aprovar(self.plano)
        self.assertEqual(regioes.ler_regiao(alvo, "backlog"), "\n")
        self.assertIn("## Backlog", alvo.read_text(encoding="utf-8"))

    def test_secao_de_backlog_existente_nao_e_duplicada(self):
        self.plano.write_text(
            self.plano.read_text(encoding="utf-8")
            + "\n## Backlog\n\n<!-- backlog:start -->\njá tinha\n<!-- backlog:end -->\n",
            encoding="utf-8",
        )
        alvo = scaffold.aprovar(self.plano)
        conteudo = alvo.read_text(encoding="utf-8")
        self.assertEqual(conteudo.count("<!-- backlog:start -->"), 1)
        self.assertIn("já tinha", conteudo)

    def test_backlog_entra_antes_da_fonte_quando_ela_existe(self):
        self.plano.write_text(
            self.plano.read_text(encoding="utf-8") + "\n## Fonte\n\n- algo\n",
            encoding="utf-8",
        )
        conteudo = scaffold.aprovar(self.plano).read_text(encoding="utf-8")
        self.assertLess(conteudo.index("## Backlog"), conteudo.index("## Fonte"))

    def test_frontmatter_recebe_plan_id_e_status(self):
        alvo = scaffold.aprovar(self.plano)
        self.assertEqual(regioes.ler_campo(alvo, "plan_id"), '"0002"')
        self.assertEqual(regioes.ler_campo(alvo, "status"), "approved")

    def test_planos_md_ganha_linha_do_plano(self):
        # A coluna Aprovado recebe o `approved_at` declarado no plano (2026-08-24, no
        # frontmatter de self.plano) — nunca a data em que o teste roda (unidade 0001-12, L-16).
        scaffold.aprovar(self.plano)
        conteudo = self.planos_md.read_text(encoding="utf-8")
        self.assertIn(
            "| 0002 | [evolucao-tools](builder/0002-evolucao-tools/0002-evolucao-tools.md)"
            " | builder | evolucao-tools | — | em desenvolvimento | 2026-08-24 |",
            conteudo,
        )

    def test_linha_anterior_de_planos_md_e_preservada(self):
        scaffold.aprovar(self.plano)
        conteudo = self.planos_md.read_text(encoding="utf-8")
        self.assertIn("| 0001 | [outro](builder/0001-outro/0001-outro.md)", conteudo)


class TestAprovarDryRun(unittest.TestCase):
    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self._tmp.cleanup)
        self.raiz = Path(self._tmp.name).resolve()

        (self.raiz / "_inbox").mkdir()
        (self.raiz / "system").mkdir()
        (self.raiz / "system" / "norma.md").write_text("# norma\n", encoding="utf-8")

        self.planos_md = self.raiz / "_planos.md"
        self.planos_original = (
            "<!-- planos:start -->\n"
            f"{CABECALHO_TABELA}"
            "| 0001 | [outro](builder/0001-outro/0001-outro.md) | builder | outro"
            " | — | em desenvolvimento | 2026-07-01 |\n"
            "<!-- planos:end -->\n"
        )
        self.planos_md.write_text(self.planos_original, encoding="utf-8")

        self.plano = self.raiz / "_inbox" / "evolucao-tools.md"
        self.plano.write_text(
            "---\n"
            'plan_id: ""\n'
            "core: builder\n"
            "module: evolucao-tools\n"
            'block: ""\n'
            "status: draft\n"
            "plan_size: grande\n"
            "approved_by: Bortoli\n"
            "approved_at: 2026-08-24\n"
            "---\n\n"
            "# evolucao-tools\n\n"
            "ver [norma](../system/norma.md)\n",
            encoding="utf-8",
        )

        patcher_plan_root = mock.patch.object(lib, "plan_root", return_value=self.raiz)
        patcher_plan_root.start()
        self.addCleanup(patcher_plan_root.stop)

        patcher_repo_root = mock.patch.object(scaffold.move_md, "REPO_ROOT", self.raiz)
        patcher_repo_root.start()
        self.addCleanup(patcher_repo_root.stop)

        self.alvo = self.raiz / "builder" / "0002-evolucao-tools" / "0002-evolucao-tools.md"

    def test_dry_run_nao_escreve_nada(self):
        alvo = scaffold.aprovar(self.plano, dry_run=True)

        self.assertEqual(alvo, self.alvo)
        self.assertTrue(self.plano.exists())
        self.assertFalse(alvo.exists())
        self.assertEqual(self.planos_md.read_text(encoding="utf-8"), self.planos_original)


class TestAprovarErros(unittest.TestCase):
    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self._tmp.cleanup)
        self.raiz = Path(self._tmp.name).resolve()

        (self.raiz / "_inbox").mkdir()
        (self.raiz / "system").mkdir()
        (self.raiz / "system" / "norma.md").write_text("# norma\n", encoding="utf-8")

        self.planos_md = self.raiz / "_planos.md"
        self.planos_original = (
            "<!-- planos:start -->\n"
            f"{CABECALHO_TABELA}"
            "| 0001 | [outro](builder/0001-outro/0001-outro.md) | builder | outro"
            " | — | em desenvolvimento | 2026-07-01 |\n"
            "<!-- planos:end -->\n"
        )
        self.planos_md.write_text(self.planos_original, encoding="utf-8")

        self.plano = self.raiz / "_inbox" / "evolucao-tools.md"
        self.plano.write_text(
            "---\n"
            'plan_id: ""\n'
            "core: builder\n"
            "module: evolucao-tools\n"
            'block: ""\n'
            "status: draft\n"
            "plan_size: grande\n"
            "approved_by: Bortoli\n"
            "approved_at: 2026-08-24\n"
            "---\n\n"
            "# evolucao-tools\n\n"
            "ver [norma](../system/norma.md)\n",
            encoding="utf-8",
        )

        patcher_plan_root = mock.patch.object(lib, "plan_root", return_value=self.raiz)
        patcher_plan_root.start()
        self.addCleanup(patcher_plan_root.stop)

        patcher_repo_root = mock.patch.object(scaffold.move_md, "REPO_ROOT", self.raiz)
        patcher_repo_root.start()
        self.addCleanup(patcher_repo_root.stop)

    def test_core_ausente_levanta_value_error_sem_escrever(self):
        plano = self.raiz / "_inbox" / "sem-core.md"
        plano.write_text(
            "---\n"
            'plan_id: ""\n'
            "core:\n"
            "module: sem-core\n"
            'block: ""\n'
            "status: draft\n"
            "---\n\n# sem-core\n",
            encoding="utf-8",
        )

        with self.assertRaises(ValueError):
            scaffold.aprovar(plano)

        self.assertTrue(plano.exists())
        self.assertEqual(self.planos_md.read_text(encoding="utf-8"), self.planos_original)

    def test_core_vazio_com_aspas_levanta_value_error(self):
        # Convenção do repositório para "vazio" no frontmatter: `core: ""`, não a linha em branco.
        plano = self.raiz / "_inbox" / "outro-sem-core.md"
        plano.write_text(
            "---\n"
            'plan_id: ""\n'
            'core: ""\n'
            "module: outro-sem-core\n"
            'block: ""\n'
            "status: draft\n"
            "---\n\n# outro-sem-core\n",
            encoding="utf-8",
        )

        with self.assertRaises(ValueError):
            scaffold.aprovar(plano)

        self.assertTrue(plano.exists())

    def test_nome_invalido_levanta_value_error_sem_escrever(self):
        plano = self.raiz / "_inbox" / "sozinho.md"
        plano.write_text(
            "---\n"
            'plan_id: ""\n'
            "core: builder\n"
            "module: sozinho\n"
            'block: ""\n'
            "status: draft\n"
            "---\n\n# sozinho\n",
            encoding="utf-8",
        )

        with self.assertRaises(ValueError):
            scaffold.aprovar(plano)

        self.assertTrue(plano.exists())
        self.assertEqual(self.planos_md.read_text(encoding="utf-8"), self.planos_original)

    def test_alvo_existente_levanta_file_exists_error_sem_escrever(self):
        alvo_dir = self.raiz / "builder" / "0002-evolucao-tools"
        alvo_dir.mkdir(parents=True)
        (alvo_dir / "0002-evolucao-tools.md").write_text("já aqui\n", encoding="utf-8")

        with self.assertRaises(FileExistsError):
            scaffold.aprovar(self.plano)

        self.assertTrue(self.plano.exists())
        self.assertEqual(self.planos_md.read_text(encoding="utf-8"), self.planos_original)


if __name__ == "__main__":
    unittest.main()
