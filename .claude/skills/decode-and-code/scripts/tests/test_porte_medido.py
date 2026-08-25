#!/usr/bin/env python3
"""Teste declarado da unidade 0001-15 — `porte.medir` e `porte.registrar`.

`TestMedirGrandeFechado`, `TestMedirNaoMedidoComMotivo` e `TestRegistrar` mockam `lib.repo_root`
a par de `subprocess.run` — no mesmo padrão de `test_verificacao.py` — porque só assim o cálculo
de `linhas_alteradas` passa do pré-checagem `relative_to(repo_root())` e chega ao `subprocess`
mockado. `TestMedirPequenoEMedio` não precisa: sem arquivo declarado, `medir` nunca tenta git, e
o teste afirma isso mesmo (`subprocess.run` não chamado). `TestBacklogRegistraNaTransicao` mocka
`backlog.porte.registrar` inteiro — testa só a fiação da transição, não a medição em si.

Um único teste executa `git` de verdade — `TestComandoContraGitReal`, e a razão de ele existir
está no seu próprio docstring. Todos os demais mockam `subprocess.run`.
"""

from __future__ import annotations

import subprocess
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
import porte


def _inserir_tarefas(arquivo: Path, itens: list[tuple[bool, str]]) -> None:
    """Mesmo helper de `test_derive_por_porte.py` — insere `## Tarefas` antes de `## Backlog`."""
    linhas = "\n".join(f"- [{'x' if feita else ' '}] {texto}" for feita, texto in itens)
    bloco = f"## Tarefas\n\n{linhas}\n\n"
    texto = arquivo.read_text(encoding="utf-8")
    arquivo.write_text(texto.replace("## Backlog", bloco + "## Backlog"), encoding="utf-8")


class _BaseComRepoFake(unittest.TestCase):
    """`plan_root` e `repo_root` mockados para o mesmo tempdir — o plano sintético precisa
    "estar dentro" do repositório para `_linhas_alteradas` chegar ao `subprocess` mockado."""

    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self._tmp.cleanup)
        self.raiz = Path(self._tmp.name).resolve()

        patcher_plan_root = mock.patch.object(lib, "plan_root", return_value=self.raiz)
        patcher_plan_root.start()
        self.addCleanup(patcher_plan_root.stop)

        patcher_repo_root = mock.patch.object(lib, "repo_root", return_value=self.raiz)
        patcher_repo_root.start()
        self.addCleanup(patcher_repo_root.stop)


class TestMedirGrandeFechado(_BaseComRepoFake):
    """Critério de aceite: unidades contadas, caminhos deduplicados, linhas do numstat mockado."""

    def setUp(self):
        super().setUp()
        self.dir_plano = fixtures.plano(
            self.raiz, core="builder", nome="exemplo", numero="0009",
            plan_size="grande", previstas=2,
        )
        fixtures.unidade(self.dir_plano, nome="01-a.md", unit_id="0009-01", state="verified")
        fixtures.unidade(self.dir_plano, nome="02-b.md", unit_id="0009-02", state="verified")

    def _mock_subprocess(self):
        return mock.patch.object(
            porte.subprocess,
            "run",
            side_effect=[
                mock.Mock(returncode=0, stdout=b"aaaa1111\n", stderr=b""),
                mock.Mock(returncode=0, stdout=b"3\t2\tcaminho/para/arquivo.py\n", stderr=b""),
            ],
        )

    def test_unidades_contadas_e_caminho_duplicado_conta_uma_vez(self):
        with self._mock_subprocess():
            resultado = porte.medir(self.dir_plano)

        self.assertEqual(resultado["porte_declarado"], "grande")
        self.assertEqual(resultado["unidades_ou_tarefas"], 2)
        # Duas unidades, cada uma declarando o mesmo `caminho/para/arquivo.py` (fixtures.unidade) —
        # o caminho conta uma vez só.
        self.assertEqual(resultado["arquivos_declarados"], ["caminho/para/arquivo.py"])
        self.assertEqual(resultado["linhas_alteradas"], 5)
        self.assertIsNone(resultado["motivo_nao_medido"])

    def test_comando_git_recebe_so_os_arquivos_declarados(self):
        with self._mock_subprocess() as executar:
            porte.medir(self.dir_plano)

        comando_diff = executar.call_args_list[1].args[0]
        self.assertEqual(comando_diff[:3], ["git", "diff", "--numstat"])
        self.assertEqual(comando_diff[-1], "caminho/para/arquivo.py")


class TestMedirNaoMedidoComMotivo(_BaseComRepoFake):
    """Critério de aceite: nunca zero, nunca exceção — cada falha é um caso isolado."""

    def setUp(self):
        super().setUp()
        self.dir_plano = fixtures.plano(
            self.raiz, core="builder", nome="exemplo", numero="0009",
            plan_size="grande", previstas=1,
        )
        fixtures.unidade(self.dir_plano, nome="01-a.md", unit_id="0009-01", state="verified")

    def test_comando_git_nao_encontrado(self):
        with mock.patch.object(porte.subprocess, "run", side_effect=FileNotFoundError):
            resultado = porte.medir(self.dir_plano)

        self.assertIsNone(resultado["linhas_alteradas"])
        self.assertEqual(resultado["motivo_nao_medido"], "comando git não encontrado")

    def test_git_falha(self):
        with mock.patch.object(
            porte.subprocess,
            "run",
            return_value=mock.Mock(returncode=128, stdout=b"", stderr=b"fatal: not a git repository"),
        ):
            resultado = porte.medir(self.dir_plano)

        self.assertIsNone(resultado["linhas_alteradas"])
        self.assertEqual(resultado["motivo_nao_medido"], "git falhou")

    def test_plano_sem_commit_de_criacao(self):
        with mock.patch.object(
            porte.subprocess, "run", return_value=mock.Mock(returncode=0, stdout=b"", stderr=b"")
        ):
            resultado = porte.medir(self.dir_plano)

        self.assertIsNone(resultado["linhas_alteradas"])
        self.assertEqual(resultado["motivo_nao_medido"], "plano sem commit de criação")

    def test_grande_sem_caminho_declarado_diz_o_motivo_em_vez_de_none(self):
        """Grande cujas unidades não declaram `## Arquivos` — lista vazia, não `None`. Antes da
        `L-28` a célula saía com a string `não medido (None)`, numa tabela que é append-only."""
        vazio = fixtures.plano(
            self.raiz, core="builder", nome="sem-arquivos", numero="0011",
            plan_size="grande", previstas=1,
        )

        with mock.patch.object(porte.subprocess, "run") as executar:
            resultado = porte.medir(vazio)

        executar.assert_not_called()
        self.assertEqual(resultado["arquivos_declarados"], [])
        self.assertEqual(resultado["motivo_nao_medido"], "nenhum caminho declarado")
        self.assertIn(
            "não medido (nenhum caminho declarado)",
            porte._linha_tabela(resultado, "../builder/0011-sem-arquivos.md"),
        )


class TestMedirPequenoEMedio(unittest.TestCase):
    """`—`/`não declarado` fora do grande, e nunca chama git — não há arquivo para restringir."""

    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self._tmp.cleanup)
        self.raiz = Path(self._tmp.name).resolve()

        patcher = mock.patch.object(lib, "plan_root", return_value=self.raiz)
        patcher.start()
        self.addCleanup(patcher.stop)

    def test_pequeno_nao_tem_unidades_nem_arquivos_nem_linhas(self):
        arquivo = fixtures.plano(
            self.raiz, core="builder", nome="exemplo", numero="0009",
            plan_size="pequeno", status="done", com_diretorio=False,
        )

        with mock.patch.object(porte.subprocess, "run") as executar:
            resultado = porte.medir(arquivo)

        executar.assert_not_called()
        self.assertEqual(resultado["porte_declarado"], "pequeno")
        self.assertIsNone(resultado["unidades_ou_tarefas"])
        self.assertIsNone(resultado["arquivos_declarados"])
        self.assertIsNone(resultado["linhas_alteradas"])
        self.assertIsNone(resultado["motivo_nao_medido"])

    def test_medio_conta_tarefas_mas_nao_declara_arquivos(self):
        arquivo = fixtures.plano(
            self.raiz, core="builder", nome="exemplo", numero="0009",
            plan_size="médio", com_backlog=True, com_diretorio=False,
        )
        _inserir_tarefas(arquivo, [(True, "Única")])

        with mock.patch.object(porte.subprocess, "run") as executar:
            resultado = porte.medir(arquivo)

        executar.assert_not_called()
        self.assertEqual(resultado["porte_declarado"], "médio")
        self.assertEqual(resultado["unidades_ou_tarefas"], 1)
        self.assertIsNone(resultado["arquivos_declarados"])
        self.assertIsNone(resultado["linhas_alteradas"])


class TestRegistrar(_BaseComRepoFake):
    """Critério de aceite: acrescenta uma linha, preserva o resto, `None` sem escrever na segunda."""

    def setUp(self):
        super().setUp()
        self.dir_plano = fixtures.plano(
            self.raiz, core="builder", nome="exemplo", numero="0009",
            plan_size="grande", previstas=1,
        )
        fixtures.unidade(self.dir_plano, nome="01-a.md", unit_id="0009-01", state="verified")
        self.caminho_tabela = self.raiz / "system" / "porte-medido.md"

    def _mock_subprocess(self):
        return mock.patch.object(
            porte.subprocess,
            "run",
            side_effect=[
                mock.Mock(returncode=0, stdout=b"aaaa1111\n", stderr=b""),
                mock.Mock(returncode=0, stdout=b"1\t1\tcaminho/para/arquivo.py\n", stderr=b""),
            ],
        )

    def test_cria_o_arquivo_com_cabecalho_na_primeira_chamada(self):
        self.assertFalse(self.caminho_tabela.exists())

        with self._mock_subprocess():
            porte.registrar(self.dir_plano)

        self.assertTrue(self.caminho_tabela.is_file())
        self.assertIn("| Plano | Porte declarado |", self.caminho_tabela.read_text(encoding="utf-8"))

    def test_acrescenta_exatamente_uma_linha_com_a_medicao(self):
        with self._mock_subprocess():
            linha = porte.registrar(self.dir_plano)

        conteudo = self.caminho_tabela.read_text(encoding="utf-8")
        self.assertEqual(conteudo.count("| [0009-exemplo]"), 1)
        self.assertIn("| grande | 1 | 1 | 2 |", linha)

    def test_segunda_chamada_nao_mede_nem_escreve(self):
        with self._mock_subprocess():
            porte.registrar(self.dir_plano)
        conteudo_apos_primeira = self.caminho_tabela.read_text(encoding="utf-8")

        with mock.patch.object(porte.subprocess, "run") as executar:
            resultado = porte.registrar(self.dir_plano)

        executar.assert_not_called()
        self.assertIsNone(resultado)
        self.assertEqual(self.caminho_tabela.read_text(encoding="utf-8"), conteudo_apos_primeira)

    def test_preserva_linha_de_outro_plano_ja_registrado(self):
        with self._mock_subprocess():
            porte.registrar(self.dir_plano)
        antes = self.caminho_tabela.read_text(encoding="utf-8")

        outro = fixtures.plano(
            self.raiz, core="builder", nome="segundo", numero="0010",
            plan_size="pequeno", status="done", com_diretorio=False,
        )
        porte.registrar(outro)

        depois = self.caminho_tabela.read_text(encoding="utf-8")
        self.assertIn(antes, depois)
        self.assertIn("[0010-segundo]", depois)


class TestBacklogRegistraNaTransicao(unittest.TestCase):
    """Critério de aceite: `backlog.projetar` registra só no instante em que a situação passa a
    `concluído` — nunca de novo, nunca quando a situação fica `em desenvolvimento`."""

    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self._tmp.cleanup)
        self.raiz = Path(self._tmp.name).resolve()

        patcher = mock.patch.object(lib, "plan_root", return_value=self.raiz)
        patcher.start()
        self.addCleanup(patcher.stop)

        self.dir_plano = fixtures.plano(
            self.raiz, core="builder", nome="exemplo", numero="0009",
            plan_size="grande", previstas=2,
        )
        fixtures.planos_md(
            self.raiz,
            linhas=[
                "| 0009 | [exemplo](builder/0009-exemplo/0009-exemplo.md) | builder"
                " | exemplo | — | em desenvolvimento | 2026-08-24 |\n"
            ],
        )

        patcher_registrar = mock.patch.object(backlog.porte, "registrar")
        self.mock_registrar = patcher_registrar.start()
        self.addCleanup(patcher_registrar.stop)

    def test_transicao_para_concluido_registra_uma_vez(self):
        fixtures.unidade(self.dir_plano, nome="01-a.md", unit_id="0009-01", state="verified")
        fixtures.unidade(self.dir_plano, nome="02-b.md", unit_id="0009-02", state="verified")

        _, situacao = backlog.projetar(self.dir_plano)

        self.assertEqual(situacao, "concluído")
        self.mock_registrar.assert_called_once_with(self.dir_plano)

    def test_segunda_projecao_ja_concluido_nao_registra_de_novo(self):
        fixtures.unidade(self.dir_plano, nome="01-a.md", unit_id="0009-01", state="verified")
        fixtures.unidade(self.dir_plano, nome="02-b.md", unit_id="0009-02", state="verified")

        backlog.projetar(self.dir_plano)
        self.mock_registrar.reset_mock()
        backlog.projetar(self.dir_plano)

        self.mock_registrar.assert_not_called()

    def test_situacao_em_desenvolvimento_nunca_registra(self):
        fixtures.unidade(self.dir_plano, nome="01-a.md", unit_id="0009-01", state="verified")
        fixtures.unidade(self.dir_plano, nome="02-b.md", unit_id="0009-02", state="spec")

        _, situacao = backlog.projetar(self.dir_plano)

        self.assertEqual(situacao, "em desenvolvimento")
        self.mock_registrar.assert_not_called()


class TestComandoContraGitReal(unittest.TestCase):
    """Os únicos testes desta suíte que executam `git` de verdade — e existem exatamente por isso.

    Todos os outros mockam `subprocess.run`, e mock valida o **parsing da saída**, nunca o comando
    montado. Foi o que deixou `--follow` somado a `--reverse` passar: o git responde a essa
    combinação com saída vazia **quando o arquivo foi movido** — e todo plano é movido, do
    `_inbox` para o alvo, pelo próprio `derive`. A suíte ficou verde enquanto `_commit_de_criacao`
    devolvia "plano sem commit de criação" para todo plano versionado (`L-28`).

    O repositório é construído aqui, num tempdir, e reproduz o ciclo de vida do plano: nasce no
    `_inbox`, é movido, é editado. Não depende do histórico deste projeto, que não existiria em
    quem instala o plugin (invariante 2).
    """

    def _git(self, raiz: Path, *args: str) -> str:
        resultado = subprocess.run(["git", *args], cwd=raiz, capture_output=True)
        if resultado.returncode != 0:
            self.fail(f"git {' '.join(args)} falhou: {resultado.stderr.decode(errors='replace')}")
        return resultado.stdout.decode("utf-8", errors="replace").strip()

    def _repo_com_plano_movido(self) -> tuple[Path, str]:
        """Repositório onde `dest/p.md` nasceu como `_inbox/p.md` — devolve a raiz e a criação."""
        tmp = tempfile.TemporaryDirectory()
        self.addCleanup(tmp.cleanup)
        raiz = Path(tmp.name).resolve()

        self._git(raiz, "init", "-q", ".")
        self._git(raiz, "config", "user.email", "teste@exemplo")
        self._git(raiz, "config", "user.name", "teste")

        (raiz / "_inbox").mkdir()
        (raiz / "_inbox" / "p.md").write_text("a\n", encoding="utf-8")
        self._git(raiz, "add", "-A")
        self._git(raiz, "commit", "-qm", "criacao")
        criacao = self._git(raiz, "rev-parse", "HEAD")

        (raiz / "dest").mkdir()
        self._git(raiz, "mv", "_inbox/p.md", "dest/p.md")
        self._git(raiz, "commit", "-qm", "move")
        return raiz, criacao

    def test_acha_a_criacao_de_plano_movido_do_inbox(self):
        raiz, criacao = self._repo_com_plano_movido()

        commit, motivo = porte._commit_de_criacao(Path("dest/p.md"), raiz)

        self.assertIsNone(motivo, "git real não achou o commit de criação de um arquivo movido")
        self.assertEqual(commit, criacao)

    def test_arquivo_recriado_devolve_a_criacao_original_nao_a_ultima(self):
        """Sem `--reverse` o git emite do mais novo para o mais antigo: criar, apagar e recriar
        produz dois commits `A`, e o que interessa é o primeiro — daí `linhas[-1]`, não `[0]`."""
        raiz, criacao = self._repo_com_plano_movido()
        self._git(raiz, "rm", "-q", "dest/p.md")
        self._git(raiz, "commit", "-qm", "apaga")
        (raiz / "dest").mkdir(exist_ok=True)
        (raiz / "dest" / "p.md").write_text("c\n", encoding="utf-8")
        self._git(raiz, "add", "-A")
        self._git(raiz, "commit", "-qm", "recria")

        commit, motivo = porte._commit_de_criacao(Path("dest/p.md"), raiz)

        self.assertIsNone(motivo)
        self.assertEqual(commit, criacao)


if __name__ == "__main__":
    unittest.main()
