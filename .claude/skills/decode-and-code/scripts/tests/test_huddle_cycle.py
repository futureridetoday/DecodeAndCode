#!/usr/bin/env python3
"""Testes do ciclo do huddle por pessoa — plano 0008.

T1: identidade (`huddle.usuario`) contra `git` real num repositório `tempfile`, com a configuração
global e de sistema isoladas pelo ambiente, e caminho do arquivo da pessoa (`huddle.caminho`).
"""

from __future__ import annotations

import os
import subprocess
import sys
import tempfile
import unittest
from datetime import date
from pathlib import Path
from unittest import mock

sys.path.insert(0, str(Path(__file__).resolve().parent))
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import huddle
import lib
import regioes

# Isola o `git` da configuração desta máquina: sem isso, o `user.name` global vazaria no teste.
_GIT_ISOLADO = {"GIT_CONFIG_GLOBAL": os.devnull, "GIT_CONFIG_NOSYSTEM": "1"}


class _ProjetoGit(unittest.TestCase):
    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self._tmp.cleanup)
        self.projeto = Path(self._tmp.name).resolve()
        ambiente = mock.patch.dict(os.environ, _GIT_ISOLADO)
        ambiente.start()
        self.addCleanup(ambiente.stop)
        subprocess.run(["git", "init", "-q"], cwd=self.projeto, check=True)
        # E-mail só para os commits do teste; o `user.name` fica por conta de cada caso.
        subprocess.run(["git", "config", "user.email", "t@t"], cwd=self.projeto, check=True)

    def nome(self, valor: str) -> None:
        subprocess.run(["git", "config", "user.name", valor], cwd=self.projeto, check=True)


class TestUsuario(_ProjetoGit):
    def test_nome_com_espaco_vira_kebab_case(self):
        self.nome("Bortoli Rafael")
        self.assertEqual(huddle.usuario(self.projeto), "bortoli-rafael")

    def test_nome_acentuado_vira_ascii(self):
        self.nome("José Ávila da Conceição")
        self.assertEqual(huddle.usuario(self.projeto), "jose-avila-da-conceicao")

    def test_pontuacao_e_espacos_repetidos_colapsam(self):
        self.nome("  Ana  O'Neil  ")
        self.assertEqual(huddle.usuario(self.projeto), "ana-o-neil")

    def test_nome_ausente_recusa_dizendo_como_configurar(self):
        with self.assertRaises(ValueError) as ctx:
            huddle.usuario(self.projeto)
        self.assertIn("git config user.name", str(ctx.exception))

    def test_nome_sem_letra_ascii_recusa(self):
        self.nome("李")
        with self.assertRaises(ValueError):
            huddle.usuario(self.projeto)


class TestCaminho(unittest.TestCase):
    def test_arquivo_da_pessoa_sob_plan_root(self):
        projeto = Path("/projeto")
        esperado = projeto / lib.config()["plan_root"] / "system" / "huddle" / "bortoli-rafael.md"
        self.assertEqual(huddle.caminho(projeto, "bortoli-rafael"), esperado)


# --- T2 ---------------------------------------------------------------------------------------

HOJE = date.today().isoformat()


class _ProjetoComHuddle(_ProjetoGit):
    """Projeto git com o arquivo da pessoa `ana` criado por `iniciar`."""

    def setUp(self):
        super().setUp()
        self.nome("Ana")
        self.arquivo = huddle.caminho(self.projeto, "ana")
        huddle.iniciar(self.arquivo, projeto=self.projeto, usuario="ana")

    def texto(self) -> str:
        return self.arquivo.read_text(encoding="utf-8")

    def secao(self, nome: str) -> str:
        return huddle._secao(self.texto(), nome) or ""

    def commit(self, mensagem: str = "c") -> None:
        subprocess.run(["git", "add", "-A"], cwd=self.projeto, check=True)
        subprocess.run(["git", "commit", "-q", "--allow-empty", "-m", mensagem], cwd=self.projeto, check=True)


class TestIniciarPorPessoa(_ProjetoComHuddle):
    def test_esqueleto_tem_os_tres_campos_da_pessoa(self):
        self.assertEqual(regioes.ler_campo(self.arquivo, "owner"), "ana")
        self.assertEqual(regioes.ler_campo(self.arquivo, "last_huddle"), '""')
        self.assertEqual(regioes.ler_campo(self.arquivo, "reminder_days"), "7")

    def test_project_vem_do_projeto_passado(self):
        self.assertEqual(regioes.ler_campo(self.arquivo, "project"), self.projeto.name)

    def test_esqueleto_passa_no_lint(self):
        self.assertEqual(huddle.lint_arquivo(self.arquivo), [])

    def test_sem_projeto_continua_funcionando(self):
        destino = self.projeto / "outro.md"
        self.assertEqual(huddle.iniciar(destino), destino)
        self.assertEqual(huddle.lint_arquivo(destino), [])


class TestLintReminderDays(_ProjetoComHuddle):
    def test_reminder_days_invalido_reprova(self):
        for valor in ("-1", "sete", "1.5", '""'):
            with self.subTest(valor=valor):
                regioes.escrever_campos(self.arquivo, {"reminder_days": valor})
                problemas = huddle.lint_arquivo(self.arquivo)
                self.assertTrue(any("reminder_days" in p for p in problemas), problemas)

    def test_reminder_days_zero_aprova(self):
        regioes.escrever_campos(self.arquivo, {"reminder_days": "0"})
        self.assertEqual(huddle.lint_arquivo(self.arquivo), [])


class TestAbrir(_ProjetoComHuddle):
    def test_primeira_entrada_e_h01_com_data_de_hoje_e_autor(self):
        h_id = huddle.abrir(self.arquivo, "pergunta", "Qual o teto do intake?", "ana")
        self.assertEqual(h_id, "H-01")
        self.assertIn(f"### H-01 · `pergunta` · {HOJE} · ana", self.secao("Abertas"))
        self.assertIn("Qual o teto do intake?", self.secao("Abertas"))
        self.assertEqual(huddle.lint_arquivo(self.arquivo), [])

    def test_proximo_id_considera_abertas_e_fechadas(self):
        huddle.abrir(self.arquivo, "pergunta", "a", "ana")
        huddle.abrir(self.arquivo, "padrão", "b", "ana")
        huddle.fechar(self.arquivo, "H-02", "descartada")
        self.assertEqual(huddle.abrir(self.arquivo, "observação", "c", "ana"), "H-03")

    def test_insere_no_fim_de_abertas(self):
        huddle.abrir(self.arquivo, "pergunta", "primeira", "ana")
        huddle.abrir(self.arquivo, "pergunta", "segunda", "ana")
        abertas = self.secao("Abertas")
        self.assertLess(abertas.index("primeira"), abertas.index("segunda"))
        self.assertNotIn("primeira", self.secao("Fechadas"))

    def test_tipo_fora_do_vocabulario_recusado_sem_escrever(self):
        antes = self.texto()
        with self.assertRaises(ValueError):
            huddle.abrir(self.arquivo, "ideia", "x", "ana")
        self.assertEqual(self.texto(), antes)

    def test_cria_o_arquivo_se_faltar(self):
        outro = huddle.caminho(self.projeto, "beto")
        self.assertEqual(huddle.abrir(outro, "pergunta", "x", "beto"), "H-01")
        self.assertEqual(regioes.ler_campo(outro, "owner"), "beto")
        self.assertEqual(regioes.ler_campo(outro, "project"), self.projeto.name)

    def test_recusa_enquanto_existir_o_arquivo_unico_de_projeto(self):
        antigo = self.arquivo.parent.parent / "huddle.md"
        antigo.write_text("x", encoding="utf-8")
        antes = self.texto()
        with self.assertRaises(ValueError) as ctx:
            huddle.abrir(self.arquivo, "pergunta", "x", "ana")
        self.assertIn("huddle-migrar", str(ctx.exception))
        self.assertEqual(self.texto(), antes)


class TestFechar(_ProjetoComHuddle):
    def test_move_para_fechadas_com_data_e_destino(self):
        huddle.abrir(self.arquivo, "pergunta", "corpo da entrada", "ana")
        huddle.fechar(self.arquivo, "H-01", "virou guideline .claude/rules/x.md")
        self.assertNotIn("H-01", self.secao("Abertas"))
        self.assertNotIn("corpo da entrada", self.texto())
        self.assertIn(
            f"| H-01 | `pergunta` | {HOJE} | virou guideline .claude/rules/x.md |", self.secao("Fechadas")
        )
        self.assertEqual(huddle.lint_arquivo(self.arquivo), [])

    def test_fecha_so_a_entrada_pedida(self):
        huddle.abrir(self.arquivo, "pergunta", "fica", "ana")
        huddle.abrir(self.arquivo, "pergunta", "sai", "ana")
        huddle.fechar(self.arquivo, "H-02", "descartada")
        self.assertIn("fica", self.secao("Abertas"))
        self.assertNotIn("sai", self.secao("Abertas"))

    def test_barra_vertical_no_destino_nao_quebra_a_tabela(self):
        huddle.abrir(self.arquivo, "pergunta", "x", "ana")
        huddle.fechar(self.arquivo, "H-01", "a | b")
        self.assertIn("a \\| b", self.secao("Fechadas"))

    def test_id_inexistente_recusado_sem_escrever(self):
        antes = self.texto()
        with self.assertRaises(ValueError):
            huddle.fechar(self.arquivo, "H-09", "x")
        self.assertEqual(self.texto(), antes)

    def test_secao_extra_depois_de_fechadas_continua_no_lugar(self):
        huddle.abrir(self.arquivo, "pergunta", "x", "ana")
        with self.arquivo.open("a", encoding="utf-8") as f:
            f.write("\n---\n\n## Notas\n\ntexto livre\n")
        huddle.fechar(self.arquivo, "H-01", "descartada")
        texto = self.texto()
        self.assertLess(texto.index("| H-01 |"), texto.index("---\n\n## Notas"))
        self.assertIn("texto livre", self.secao("Notas"))


class TestEvidencia(_ProjetoComHuddle):
    """Plano 0019, `D-07` — evidência opcional, prefixo de vocabulário fechado, no fim do corpo."""

    def test_cinco_prefixos_aceitos(self):
        for valor in ("E-03", "L-04 do 0017", "bloqueio: sem-segredo", "gate: lint-plano", "revisão: 0019"):
            with self.subTest(valor=valor):
                self.assertTrue(huddle.evidencia_valida(valor))

    def test_fora_do_vocabulario_recusado(self):
        for valor in ("palpite", "E-", "E-3x", "bloqueio:", "gate:   ", "H-01", "E-03\nL-01"):
            with self.subTest(valor=valor):
                self.assertFalse(huddle.evidencia_valida(valor))

    def test_linha_no_fim_do_corpo_e_a_pauta_mostra_o_texto(self):
        huddle.abrir(self.arquivo, "padrão", "Primeira linha.\n\nSegunda.", "ana", evidencia="E-03")
        self.assertEqual(huddle.entrada(self.arquivo, "H-01")["evidencia"], "E-03")
        self.assertTrue(huddle.entrada(self.arquivo, "H-01")["texto"].endswith("Evidência: E-03"))
        [aberta] = huddle.pauta(self.arquivo)["abertas"]
        self.assertTrue(aberta["texto"].startswith("Primeira linha."))
        self.assertEqual(huddle.lint_arquivo(self.arquivo), [])

    def test_evidencia_invalida_recusada_sem_escrever(self):
        antes = self.texto()
        with self.assertRaises(ValueError):
            huddle.abrir(self.arquivo, "padrão", "x", "ana", evidencia="palpite")
        self.assertEqual(self.texto(), antes)

    def test_sem_evidencia_continua_como_antes(self):
        huddle.abrir(self.arquivo, "pergunta", "x", "ana")
        self.assertEqual(huddle.entrada(self.arquivo, "H-01")["evidencia"], "")
        self.assertNotIn("Evidência:", self.texto())

    def test_lint_recusa_linha_fora_do_vocabulario(self):
        huddle.abrir(self.arquivo, "pergunta", "x\n\nEvidência: palpite", "ana")
        problemas = huddle.lint_arquivo(self.arquivo)
        self.assertTrue(any("H-01: evidência" in p for p in problemas), problemas)

    def test_entrada_que_nao_esta_aberta(self):
        with self.assertRaises(ValueError):
            huddle.entrada(self.arquivo, "H-09")


class TestConcluir(_ProjetoComHuddle):
    def test_grava_last_huddle(self):
        huddle.concluir(self.arquivo, "2026-11-15")
        self.assertEqual(regioes.ler_campo(self.arquivo, "last_huddle"), "2026-11-15")


class TestPauta(_ProjetoComHuddle):
    def test_abertas_e_commits_desde_created(self):
        huddle.abrir(self.arquivo, "pergunta", "**Título da entrada.**", "ana")
        self.commit("primeiro commit")
        p = huddle.pauta(self.arquivo)
        self.assertEqual([a["id"] for a in p["abertas"]], ["H-01"])
        self.assertEqual(p["desde"], HOJE)
        self.assertTrue(any("primeiro commit" in c for c in p["commits"]), p["commits"])
        self.assertEqual(p["omitidos"], 0)
        self.assertIsNone(p["aviso"])

    def test_desde_padrao_e_last_huddle_quando_preenchido(self):
        huddle.concluir(self.arquivo, "2026-01-02")
        self.assertEqual(huddle.pauta(self.arquivo)["desde"], "2026-01-02")

    def test_desde_explicito_vence(self):
        self.assertEqual(huddle.pauta(self.arquivo, desde="2025-05-05")["desde"], "2025-05-05")

    def test_no_maximo_50_commits_e_a_contagem_dos_omitidos(self):
        for i in range(53):
            self.commit(f"c{i}")
        p = huddle.pauta(self.arquivo)
        self.assertEqual(len(p["commits"]), 50)
        self.assertEqual(p["omitidos"], 3)

    def test_sem_git_lista_vazia_e_aviso(self):
        with tempfile.TemporaryDirectory() as tmp:
            arquivo = Path(tmp) / "h.md"
            huddle.iniciar(arquivo, projeto=Path(tmp), usuario="ana")
            p = huddle.pauta(arquivo)
        self.assertEqual(p["commits"], [])
        self.assertTrue(p["aviso"])


class TestMigrar(_ProjetoGit):
    def setUp(self):
        super().setUp()
        self.nome("Ana")
        self.antigo = self.projeto / lib.config()["plan_root"] / "system" / "huddle.md"
        huddle.iniciar(self.antigo, projeto=self.projeto)
        texto = self.antigo.read_text(encoding="utf-8")
        for campo in ("owner", "last_huddle", "reminder_days"):
            texto = "".join(l for l in texto.splitlines(True) if not l.startswith(f"{campo}:"))
        self.antigo.write_text(texto, encoding="utf-8")
        subprocess.run(["git", "add", "-A"], cwd=self.projeto, check=True)
        subprocess.run(["git", "commit", "-q", "-m", "huddle antigo"], cwd=self.projeto, check=True)
        self.destino = huddle.caminho(self.projeto, "ana")

    def test_move_por_git_mv_e_acrescenta_os_campos(self):
        self.assertEqual(huddle.migrar(self.projeto, "ana"), self.destino)
        self.assertFalse(self.antigo.exists())
        self.assertEqual(regioes.ler_campo(self.destino, "owner"), "ana")
        self.assertEqual(regioes.ler_campo(self.destino, "last_huddle"), '""')
        self.assertEqual(regioes.ler_campo(self.destino, "reminder_days"), "7")
        status = subprocess.run(
            ["git", "status", "--porcelain"], cwd=self.projeto, capture_output=True, text=True
        ).stdout
        self.assertIn("R", status.split()[0])
        self.assertEqual(huddle.lint_arquivo(self.destino), [])

    def test_recusa_se_o_destino_ja_existe(self):
        huddle.iniciar(self.destino, projeto=self.projeto, usuario="ana")
        with self.assertRaises(FileExistsError):
            huddle.migrar(self.projeto, "ana")
        self.assertTrue(self.antigo.exists())

    def test_sem_arquivo_antigo_nao_faz_nada(self):
        huddle.migrar(self.projeto, "ana")
        self.assertIsNone(huddle.migrar(self.projeto, "beto"))
        self.assertFalse(huddle.caminho(self.projeto, "beto").exists())


# --- T3 ---------------------------------------------------------------------------------------


class TestLintRelatorioComArquivo(_ProjetoComHuddle):
    def setUp(self):
        super().setUp()
        self.h1 = huddle.abrir(self.arquivo, "pergunta", "a", "ana")
        self.h2 = huddle.abrir(self.arquivo, "padrão", "b", "ana")

    def lint(self, linha: str) -> list[str]:
        return huddle.lint_relatorio(f"Relatório.\n\n{linha}\n", arquivo=self.arquivo)

    def test_zero_aprova(self):
        self.assertEqual(self.lint("entradas novas no huddle: 0"), [])

    def test_n_coerente_com_ids_de_hoje_aprova(self):
        self.assertEqual(self.lint("entradas novas no huddle: 2 (H-01, H-02)"), [])

    def test_sem_a_linha_reprova(self):
        self.assertTrue(huddle.lint_relatorio("Relatório.", arquivo=self.arquivo))

    def test_n_positivo_sem_ids_reprova(self):
        self.assertTrue(self.lint("entradas novas no huddle: 2"))

    def test_n_divergente_da_quantidade_de_ids_reprova(self):
        problemas = self.lint("entradas novas no huddle: 3 (H-01, H-02)")
        self.assertTrue(any("3" in p for p in problemas), problemas)

    def test_zero_com_ids_reprova(self):
        self.assertTrue(self.lint("entradas novas no huddle: 0 (H-01)"))

    def test_id_inexistente_reprova(self):
        problemas = self.lint("entradas novas no huddle: 1 (H-09)")
        self.assertTrue(any("H-09" in p for p in problemas), problemas)

    def test_id_antigo_reprova(self):
        texto = self.texto().replace(f"### H-01 · `pergunta` · {HOJE}", "### H-01 · `pergunta` · 2026-01-01")
        self.arquivo.write_text(texto, encoding="utf-8")
        problemas = self.lint("entradas novas no huddle: 1 (H-01)")
        self.assertTrue(any("H-01" in p for p in problemas), problemas)

    def test_id_fechado_reprova(self):
        huddle.fechar(self.arquivo, "H-02", "descartada")
        problemas = self.lint("entradas novas no huddle: 1 (H-02)")
        self.assertTrue(any("H-02" in p for p in problemas), problemas)

    def test_sem_arquivo_mantem_o_contrato_de_hoje(self):
        self.assertEqual(huddle.lint_relatorio("entradas novas no huddle: 2"), [])
        self.assertTrue(huddle.lint_relatorio("sem linha"))


if __name__ == "__main__":
    unittest.main()
