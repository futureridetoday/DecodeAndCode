#!/usr/bin/env python3
"""Testes do ponto de entrada único `dc.py` — `P-14` do plano `apply-plugin-review`.

`dc.py` é um dispatcher fino, e o que ele promete é o **comando**: argumentos, código de saída,
stdin. Mock de `subprocess.run` não prova nada disso (`.claude/rules/scripts.md`, *Comando
externo*), então estes testes executam o `dc.py` de verdade, por `subprocess` com o interpretador
atual, contra projetos montados em `tempfile`.

O `dc.py` roda a partir do **pacote** que `empacotar.construir` escreve em `tempfile`, não do
checkout: `lib.repo_root()` tenta o `__file__` primeiro, e rodando daqui ele acharia este
repositório — a suíte escreveria nele. A partir do pacote o `__file__` não resolve projeto algum e o
`cwd` decide, que é exatamente o caso do plugin instalado.

Cada skill tem um `dc.py` próprio (`skills/<skill>/dc.py`), atalho que executa o compartilhado: é o
comando que a liberação de permissão casa, e o caminho dele não leva `..` que o modelo normalize.
`TestAtalhoDeSkill` confere que os quatro são idênticos e que repassam argumentos, stdin e código de
saída — sempre a partir do pacote.

`scaffold.concorrentes` tem a classe própria `TestConcorrentes`, chamada direto com `plan_root`
trocado por mock — como `test_scaffold.py`.
"""

from __future__ import annotations

import os
import re
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from unittest import mock

sys.path.insert(0, str(Path(__file__).resolve().parent))
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import empacotar
import fixtures
import lib
import lint_unidade
import scaffold
import verificacao

SUBCOMANDOS = (
    "validar-nome",
    "concorrencia",
    "bootstrap",
    "aprovar",
    "proxima-unidade",
    "lint-unidade",
    "lint-plano",
    "projetar-backlog",
    "handoff",
    "verificar",
    "normas",
)

_tmp_pacote: tempfile.TemporaryDirectory | None = None
_PACOTE: Path | None = None
_DC: Path | None = None


def setUpModule() -> None:
    global _tmp_pacote, _PACOTE, _DC
    _tmp_pacote = tempfile.TemporaryDirectory()
    _PACOTE = Path(_tmp_pacote.name).resolve() / "pkg"
    empacotar.construir(_PACOTE)
    _DC = _PACOTE / "skills" / "decode-and-code" / "scripts" / "dc.py"


def tearDownModule() -> None:
    _tmp_pacote.cleanup()


def _executar(
    cwd: Path, *args: str, entrada: str | None = None, script: Path | None = None
) -> subprocess.CompletedProcess:
    """Roda `dc.py` de verdade em `cwd` — o compartilhado do pacote, ou `script` (o atalho de uma skill).

    A sentinela de reentrância sai do ambiente do filho: esta suíte pode rodar dentro de uma
    verificação, e o runner que `verificar` chama aqui é o stub do teste, que não recursa.
    """
    ambiente = {k: v for k, v in os.environ.items() if k != verificacao.SENTINELA_REENTRANCIA}
    ambiente["PYTHONIOENCODING"] = "utf-8"
    return subprocess.run(
        [sys.executable, str(script or _DC), *args],
        cwd=cwd,
        input=entrada,
        capture_output=True,
        text=True,
        encoding="utf-8",
        env=ambiente,
        timeout=60,
    )


_PLANO = """\
---
name: {nome}
type: plan
project: projeto-sintetico
plan_id: ""
{core}module: {module}
block: ""
status: draft
plan_size: grande
approved_by: Teste
approved_at: 2026-10-15
---

# {nome}

## Escopo

| # | Unidade | Responsabilidade |
|---|---|---|
| 01 | unidade-sintetica | existir só para o teste do dc.py |

## Fonte

- Teste do `dc.py`.
"""

_RUNNER_STUB = "#!/bin/sh\necho 'Ran 1 test stub'\necho OK\nexit {codigo}\n"

_LINHA_BUILDER = (
    "| 0001 | [outro](builder/0001-outro/0001-outro.md) | builder | outro"
    " | — | em desenvolvimento | 2026-07-01 |\n"
)


class _ProjetoCase(unittest.TestCase):
    """Um projeto descartável por teste, com `dc.py` rodando a partir dele."""

    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self._tmp.cleanup)
        self.projeto = Path(self._tmp.name).resolve() / "projeto"
        self.projeto.mkdir()
        self.raiz_planos = self.projeto / "docs" / "plan"

    def dc(self, *args: str, entrada: str | None = None) -> subprocess.CompletedProcess:
        return _executar(self.projeto, *args, entrada=entrada)

    def bootstrap(self) -> None:
        r = self.dc("bootstrap")
        self.assertEqual(r.returncode, 0, r.stderr)

    def plano_no_inbox(self, nome: str = "plano-sintetico", *, core: str | None = "builder",
                       module: str = "modulo-sintetico") -> Path:
        linha_core = f"core: {core}\n" if core is not None else ""
        alvo = self.raiz_planos / "_inbox" / f"{nome}.md"
        alvo.write_text(_PLANO.format(nome=nome, core=linha_core, module=module), encoding="utf-8")
        return alvo

    def aprovar(self, **kwargs) -> Path:
        """Bootstrap, plano no `_inbox` e `aprovar` — devolve o diretório do plano aprovado."""
        self.bootstrap()
        plano = self.plano_no_inbox(**kwargs)
        r = self.dc("aprovar", str(plano.relative_to(self.projeto)))
        self.assertEqual(r.returncode, 0, r.stderr)
        return Path(r.stdout.strip()).parent

    def stub_de_runner(self, codigo: int = 0, script: str | None = None) -> None:
        """O runner do projeto: sai com `codigo`, ou roda `script` (corpo de `sh`) no lugar do padrão."""
        runner = self.projeto / "scripts" / "test-python.sh"
        runner.parent.mkdir(parents=True, exist_ok=True)
        texto = f"#!/bin/sh\n{script}\n" if script is not None else _RUNNER_STUB.format(codigo=codigo)
        runner.write_text(texto, encoding="utf-8")
        runner.chmod(0o755)

    def unidade(self, dir_plano: Path, nome: str = "01-unidade-sintetica.md", **kwargs) -> Path:
        kwargs.setdefault("test", "scripts/tests/test_sintetico.py")
        return fixtures.unidade(
            dir_plano, nome=nome, unit_id=f"{dir_plano.name[:4]}-{nome[:2]}", core="builder",
            module="modulo-sintetico", **kwargs,
        )

    def assertSemTraceback(self, r: subprocess.CompletedProcess) -> None:
        self.assertNotIn("Traceback", r.stderr)


class TestAjuda(unittest.TestCase):
    def test_help_lista_todos_os_subcomandos(self):
        r = _executar(Path(tempfile.gettempdir()), "--help")
        self.assertEqual(r.returncode, 0, r.stderr)
        for subcomando in SUBCOMANDOS:
            with self.subTest(subcomando=subcomando):
                self.assertIn(subcomando, r.stdout)

    def test_cada_subcomando_tem_ajuda_propria(self):
        for subcomando in SUBCOMANDOS:
            with self.subTest(subcomando=subcomando):
                r = _executar(Path(tempfile.gettempdir()), subcomando, "--help")
                self.assertEqual(r.returncode, 0, r.stderr)

    def test_skills_citam_so_subcomandos_que_existem(self):
        """Drift entre o que as skills mandam rodar e o que o `dc.py` aceita só apareceria em sessão."""
        citados: set[str] = set()
        for nome in lib.SKILLS:
            texto = (lib.repo_root() / ".claude" / "skills" / nome / "SKILL.md").read_text(encoding="utf-8")
            citados.update(re.findall(r'dc\.py" ([a-z][\w-]*)', texto))
        self.assertTrue(citados, "nenhuma skill cita um subcomando do dc.py")
        for subcomando in sorted(citados):
            with self.subTest(subcomando=subcomando):
                self.assertIn(subcomando, SUBCOMANDOS)
                r = _executar(Path(tempfile.gettempdir()), subcomando, "--help")
                self.assertEqual(r.returncode, 0, r.stderr)


class TestAtalhoDeSkill(_ProjetoCase):
    """`skills/<skill>/dc.py` — o comando que as skills citam e que a permissão casa (`P-14`)."""

    def _atalhos_do_pacote(self) -> dict[str, Path]:
        return {nome: _PACOTE / "skills" / nome / "dc.py" for nome in lib.SKILLS}

    def _atalho(self, skill: str, *args: str, entrada: str | None = None, cwd: Path | None = None):
        return _executar(
            cwd or self.projeto, *args, entrada=entrada, script=self._atalhos_do_pacote()[skill]
        )

    def test_os_quatro_da_fonte_sao_identicos(self):
        fonte = lib.repo_root() / ".claude" / "skills"
        textos = {nome: (fonte / nome / "dc.py").read_bytes() for nome in lib.SKILLS}
        self.assertEqual(len(set(textos.values())), 1, "os atalhos divergem entre as skills")

    def test_o_pacote_leva_o_atalho_de_cada_skill(self):
        for nome, atalho in self._atalhos_do_pacote().items():
            with self.subTest(skill=nome):
                self.assertTrue(atalho.is_file(), atalho)

    def test_ajuda_e_a_do_compartilhado_com_o_mesmo_prog(self):
        for nome in lib.SKILLS:
            with self.subTest(skill=nome):
                r = self._atalho(nome, "--help")
                self.assertEqual(r.returncode, 0, r.stderr)
                self.assertIn("usage: dc.py", r.stdout)
                for subcomando in SUBCOMANDOS:
                    self.assertIn(subcomando, r.stdout)

    def test_repassa_argumentos_e_o_codigo_de_saida_de_cada_faixa(self):
        for nome in lib.SKILLS:
            with self.subTest(skill=nome):
                ok = self._atalho(nome, "validar-nome", "catalogo-produtos")
                self.assertEqual((ok.returncode, ok.stdout), (0, "ok\n"), ok.stderr)
                reprovado = self._atalho(nome, "validar-nome", "0001-Foo")
                self.assertEqual(reprovado.returncode, 1, reprovado.stderr)
                self.assertEqual(len(reprovado.stdout.splitlines()), 2)
                uso = self._atalho(nome)
                self.assertEqual(uso.returncode, 2)
                self.assertNotIn("Traceback", uso.stderr)

    def test_erro_de_excecao_sai_com_2_e_mensagem_sem_traceback(self):
        r = self._atalho("implement", "lint-unidade", str(self.projeto / "nao-existe.md"))
        self.assertEqual(r.returncode, 2)
        self.assertIn("nao-existe.md", r.stderr)
        self.assertNotIn("Traceback", r.stderr)

    def test_o_projeto_e_o_cwd_e_nao_a_pasta_do_pacote(self):
        """O atalho executa o compartilhado do pacote, e `lib.repo_root()` ainda acha o projeto pelo `cwd`."""
        r = self._atalho("review-plan", "bootstrap")
        self.assertEqual(r.returncode, 0, r.stderr)
        self.assertIn(str(self.raiz_planos / "_planos.md"), r.stdout.splitlines())
        self.assertTrue((self.raiz_planos / "system" / "modelo-dev-units.md").is_file())

    def test_repassa_o_stdin(self):
        dir_plano = self.aprovar()
        r = self._atalho("derive", "handoff", str(dir_plano), entrada=TestHandoff.STDIN)
        self.assertEqual((r.returncode, r.stdout.strip()), (0, str(dir_plano / "_handoff.md")), r.stderr)
        self.assertIn("Nenhuma pendência do humano.", (dir_plano / "_handoff.md").read_text(encoding="utf-8"))

    def test_stdin_incompleto_chega_ao_compartilhado_e_sai_com_2(self):
        dir_plano = self.aprovar()
        r = self._atalho("derive", "handoff", str(dir_plano), entrada="## Fila\n\nso isto\n")
        self.assertEqual(r.returncode, 2)
        self.assertIn("## Pendências", r.stderr)


class TestErroDeUso(unittest.TestCase):
    def test_sem_subcomando_e_codigo_2_sem_traceback(self):
        r = _executar(Path(tempfile.gettempdir()))
        self.assertEqual(r.returncode, 2)
        self.assertNotIn("Traceback", r.stderr)

    def test_subcomando_desconhecido_e_codigo_2(self):
        r = _executar(Path(tempfile.gettempdir()), "nao-existe")
        self.assertEqual(r.returncode, 2)
        self.assertNotIn("Traceback", r.stderr)


class TestValidarNome(_ProjetoCase):
    def test_nome_valido_e_codigo_0(self):
        r = self.dc("validar-nome", "catalogo-produtos")
        self.assertEqual((r.returncode, r.stdout), (0, "ok\n"), r.stderr)

    def test_nome_invalido_e_codigo_1_com_um_motivo_por_linha(self):
        r = self.dc("validar-nome", "0001-Foo")
        self.assertEqual(r.returncode, 1, r.stderr)
        motivos = r.stdout.splitlines()
        self.assertEqual(len(motivos), 2, motivos)
        self.assertTrue(any("caractere" in m for m in motivos), motivos)
        self.assertTrue(any("prefixo numérico" in m for m in motivos), motivos)


class TestBootstrap(_ProjetoCase):
    def test_cria_a_estrutura_e_lista_o_que_criou(self):
        r = self.dc("bootstrap")
        self.assertEqual(r.returncode, 0, r.stderr)
        criados = r.stdout.splitlines()
        self.assertIn(str(self.raiz_planos / "_planos.md"), criados)
        self.assertIn(str(self.raiz_planos / "system" / "modelo-dev-units.md"), criados)
        for caminho in criados:
            self.assertTrue(Path(caminho).exists(), caminho)

    def test_segunda_execucao_nao_cria_nada(self):
        self.bootstrap()
        r = self.dc("bootstrap")
        self.assertEqual((r.returncode, r.stdout), (0, "nada a criar\n"), r.stderr)

    def test_projeto_por_argumento_vale_mais_que_o_cwd(self):
        r = _executar(self.projeto.parent, "bootstrap", str(self.projeto))
        self.assertEqual(r.returncode, 0, r.stderr)
        self.assertTrue((self.raiz_planos / "_planos.md").is_file())

    def test_projeto_inexistente_e_codigo_2(self):
        r = self.dc("bootstrap", str(self.projeto / "nao-existe"))
        self.assertEqual(r.returncode, 2)
        self.assertIn("projeto não existe", r.stderr)
        self.assertSemTraceback(r)


class TestConcorrencia(_ProjetoCase):
    def _planos_md(self, *linhas: str) -> None:
        fixtures.planos_md(self.raiz_planos, linhas=list(linhas))

    def test_conflito_e_codigo_1_com_a_linha_inteira(self):
        self.bootstrap()
        self._planos_md(_LINHA_BUILDER)
        plano = self.plano_no_inbox(core="builder", module="outro-modulo")
        r = self.dc("concorrencia", str(plano))
        self.assertEqual(r.returncode, 1, r.stderr)
        self.assertEqual(r.stdout.splitlines(), [_LINHA_BUILDER.strip()])

    def test_sem_conflito_e_codigo_0(self):
        self.bootstrap()
        self._planos_md(_LINHA_BUILDER)
        plano = self.plano_no_inbox(core="hub", module="outro-modulo")
        r = self.dc("concorrencia", str(plano))
        self.assertEqual((r.returncode, r.stdout), (0, "sem conflito\n"), r.stderr)

    def test_plano_sem_core_e_nao_verificavel_com_codigo_1(self):
        self.bootstrap()
        self._planos_md(_LINHA_BUILDER)
        plano = self.plano_no_inbox(core=None)
        r = self.dc("concorrencia", str(plano))
        self.assertEqual(r.returncode, 1, r.stderr)
        self.assertIn("não verificável", r.stdout)
        self.assertSemTraceback(r)


class TestAprovar(_ProjetoCase):
    def test_dry_run_devolve_o_alvo_e_nao_move_nada(self):
        self.bootstrap()
        plano = self.plano_no_inbox()
        r = self.dc("aprovar", "--dry-run", str(plano.relative_to(self.projeto)))
        alvo = self.raiz_planos / "builder" / "0001-plano-sintetico" / "0001-plano-sintetico.md"
        self.assertEqual((r.returncode, r.stdout.strip()), (0, str(alvo)), r.stderr)
        self.assertTrue(plano.is_file())
        self.assertFalse(alvo.exists())

    def test_aprova_move_e_registra_em_planos_md(self):
        dir_plano = self.aprovar()
        arquivo = dir_plano / "0001-plano-sintetico.md"
        self.assertTrue(arquivo.is_file())
        self.assertFalse((self.raiz_planos / "_inbox" / "plano-sintetico.md").exists())
        planos = (self.raiz_planos / "_planos.md").read_text(encoding="utf-8")
        self.assertIn("0001-plano-sintetico.md", planos)
        self.assertIn("em desenvolvimento", planos)

    def test_plano_sem_core_e_codigo_2_sem_traceback_e_sem_mover(self):
        self.bootstrap()
        plano = self.plano_no_inbox(core=None)
        r = self.dc("aprovar", str(plano))
        self.assertEqual(r.returncode, 2)
        self.assertIn("core", r.stderr)
        self.assertSemTraceback(r)
        self.assertTrue(plano.is_file())


class TestProximaUnidade(_ProjetoCase):
    def test_diretorio_sem_unidade_comeca_em_01(self):
        dir_plano = self.aprovar()
        r = self.dc("proxima-unidade", str(dir_plano))
        self.assertEqual((r.returncode, r.stdout), (0, "01\n"), r.stderr)

    def test_toma_o_numero_seguinte_ao_maior_em_disco(self):
        dir_plano = self.aprovar()
        self.unidade(dir_plano, "01-unidade-sintetica.md")
        r = self.dc("proxima-unidade", str(dir_plano))
        self.assertEqual((r.returncode, r.stdout), (0, "02\n"), r.stderr)

    def test_diretorio_inexistente_e_codigo_2(self):
        self.bootstrap()
        r = self.dc("proxima-unidade", str(self.raiz_planos / "nao-existe"))
        self.assertEqual(r.returncode, 2)
        self.assertSemTraceback(r)


class TestLintUnidade(_ProjetoCase):
    def test_unidade_valida_e_codigo_0(self):
        unidade = fixtures.unidade(self.projeto)
        r = self.dc("lint-unidade", str(unidade))
        self.assertEqual((r.returncode, r.stdout), (0, f"{unidade}: ok\n"), r.stderr)

    def test_unidade_com_problema_e_codigo_1_com_o_arquivo_em_cada_linha(self):
        ruim = fixtures.unidade(self.projeto, nome="02-ruim.md")
        ruim.write_text(ruim.read_text(encoding="utf-8").replace("## Contrato", "## Outra coisa"), encoding="utf-8")
        r = self.dc("lint-unidade", str(ruim))
        self.assertEqual(r.returncode, 1, r.stderr)
        linhas = r.stdout.splitlines()
        self.assertTrue(linhas, r.stdout)
        for linha in linhas:
            self.assertTrue(linha.startswith(f"{ruim}: "), linha)
        self.assertTrue(any("Contrato" in linha for linha in linhas), linhas)

    def test_varios_arquivos_reportam_cada_um_e_o_pior_decide_o_codigo(self):
        boa = fixtures.unidade(self.projeto, nome="01-boa.md")
        ruim = fixtures.unidade(self.projeto, nome="02-ruim.md")
        ruim.write_text(ruim.read_text(encoding="utf-8").replace("## Contrato", "## Outra coisa"), encoding="utf-8")
        r = self.dc("lint-unidade", str(boa), str(ruim))
        self.assertEqual(r.returncode, 1, r.stderr)
        linhas = r.stdout.splitlines()
        self.assertIn(f"{boa}: ok", linhas)
        self.assertTrue(any(linha.startswith(f"{ruim}: ") and linha != f"{ruim}: ok" for linha in linhas), linhas)

    def test_arquivo_inexistente_e_codigo_2_sem_traceback(self):
        r = self.dc("lint-unidade", str(self.projeto / "nao-existe.md"))
        self.assertEqual(r.returncode, 2)
        self.assertIn("nao-existe.md", r.stderr)
        self.assertSemTraceback(r)


class TestLintPlano(_ProjetoCase):
    """`lint-plano` — o que o `intake` roda sobre o esboço que grava no `_inbox` (`P-06`)."""

    def _plano(self, nome: str = "plano-bom", **kwargs) -> Path:
        """Plano sintético em `docs/plan/<core>/` — `pequeno` e sem backlog é o formato que aprova."""
        kwargs.setdefault("plan_size", "pequeno")
        kwargs.setdefault("com_backlog", False)
        return fixtures.plano(self.raiz_planos, nome=nome, com_diretorio=False, **kwargs)

    def test_plano_bem_formado_e_codigo_0_com_o_arquivo_na_linha(self):
        plano = self._plano()
        r = self.dc("lint-plano", str(plano))
        self.assertEqual((r.returncode, r.stdout), (0, f"{plano}: ok\n"), r.stderr)

    def test_plano_com_problema_e_codigo_1_com_o_arquivo_em_cada_linha(self):
        # `grande` sem `## Independência`: o lint recusa, e o motivo vem na saída.
        ruim = self._plano("plano-ruim", plan_size="grande", previstas=1, com_backlog=True)
        r = self.dc("lint-plano", str(ruim))
        self.assertEqual(r.returncode, 1, r.stderr)
        linhas = r.stdout.splitlines()
        self.assertTrue(linhas, r.stdout)
        for linha in linhas:
            self.assertTrue(linha.startswith(f"{ruim}: "), linha)
        self.assertTrue(any("Independência" in linha for linha in linhas), linhas)

    def test_varios_arquivos_reportam_cada_um_e_o_pior_decide_o_codigo(self):
        boa = self._plano("plano-bom")
        ruim = self._plano("plano-ruim", plan_size="médio", tarefas=False, com_backlog=True)
        r = self.dc("lint-plano", str(boa), str(ruim))
        self.assertEqual(r.returncode, 1, r.stderr)
        linhas = r.stdout.splitlines()
        self.assertIn(f"{boa}: ok", linhas)
        self.assertTrue(any(linha.startswith(f"{ruim}: ") and linha != f"{ruim}: ok" for linha in linhas), linhas)

    def test_esboco_no_inbox_sem_numero_e_lido_pelo_mesmo_comando(self):
        """O destino real do `intake`: `_inbox/<nome>.md`, que ainda não tem número."""
        self.bootstrap()
        esboco = self.plano_no_inbox()  # `grande` sem `## Independência` nem backlog
        r = self.dc("lint-plano", str(esboco.relative_to(self.projeto)))
        self.assertEqual(r.returncode, 1, r.stderr)
        self.assertIn(f"{esboco.relative_to(self.projeto)}: ", r.stdout)

    def test_arquivo_inexistente_e_codigo_2_sem_traceback(self):
        r = self.dc("lint-plano", str(self.projeto / "nao-existe.md"))
        self.assertEqual(r.returncode, 2)
        self.assertIn("nao-existe.md", r.stderr)
        self.assertSemTraceback(r)


class TestProjetarBacklog(_ProjetoCase):
    def test_projeta_a_situacao_e_grava_o_backlog_no_plano(self):
        dir_plano = self.aprovar()
        self.unidade(dir_plano)
        r = self.dc("projetar-backlog", str(dir_plano))
        self.assertEqual((r.returncode, r.stdout), (0, "situação: em desenvolvimento\n"), r.stderr)
        plano = (dir_plano / "0001-plano-sintetico.md").read_text(encoding="utf-8")
        self.assertIn("01-unidade-sintetica.md", plano)

    def test_dry_run_mostra_o_backlog_e_nao_escreve(self):
        dir_plano = self.aprovar()
        self.unidade(dir_plano)
        arquivo = dir_plano / "0001-plano-sintetico.md"
        antes = arquivo.read_text(encoding="utf-8")
        r = self.dc("projetar-backlog", "--dry-run", str(dir_plano))
        self.assertEqual(r.returncode, 0, r.stderr)
        linhas = r.stdout.splitlines()
        self.assertEqual(linhas[0], "situação: em desenvolvimento")
        self.assertTrue(any("01-unidade-sintetica.md" in linha for linha in linhas[1:]), linhas)
        self.assertEqual(arquivo.read_text(encoding="utf-8"), antes)

    def test_plano_fora_de_planos_md_e_codigo_2(self):
        self.bootstrap()
        orfao = fixtures.plano(self.raiz_planos, core="builder", nome="orfao", numero="0007")
        r = self.dc("projetar-backlog", str(orfao))
        self.assertEqual(r.returncode, 2)
        self.assertIn("não tem linha", r.stderr)
        self.assertSemTraceback(r)


class TestHandoff(_ProjetoCase):
    STDIN = (
        "## Fila\n\n1. `0001-01` primeiro\n2. `0001-02` depois\n\n"
        "## Pendências\n\nNenhuma pendência do humano.\n\n"
        "## Sugestão\n\nComeçar pela `0001-01`, porque a outra depende dela.\n"
    )

    def test_grava_o_handoff_com_as_tres_secoes_vindas_do_stdin(self):
        dir_plano = self.aprovar()
        r = self.dc("handoff", str(dir_plano), entrada=self.STDIN)
        alvo = dir_plano / "_handoff.md"
        self.assertEqual((r.returncode, r.stdout.strip()), (0, str(alvo)), r.stderr)
        texto = alvo.read_text(encoding="utf-8")
        self.assertIn("1. `0001-01` primeiro\n2. `0001-02` depois", texto)
        self.assertIn("Nenhuma pendência do humano.", texto)
        self.assertIn("Começar pela `0001-01`, porque a outra depende dela.", texto)

    def test_cada_secao_ausente_e_codigo_2_sem_gravar(self):
        dir_plano = self.aprovar()
        for titulo in ("## Fila", "## Pendências", "## Sugestão"):
            with self.subTest(ausente=titulo):
                entrada = "".join(
                    f"{t}\n\ntexto\n\n" for t in ("## Fila", "## Pendências", "## Sugestão") if t != titulo
                )
                r = self.dc("handoff", str(dir_plano), entrada=entrada)
                self.assertEqual(r.returncode, 2, r.stdout)
                self.assertIn(titulo, r.stderr)
                self.assertSemTraceback(r)
                self.assertFalse((dir_plano / "_handoff.md").exists())

    def test_stdin_vazio_e_codigo_2(self):
        dir_plano = self.aprovar()
        r = self.dc("handoff", str(dir_plano), entrada="")
        self.assertEqual(r.returncode, 2)
        self.assertSemTraceback(r)

    def test_secao_repetida_e_codigo_2(self):
        dir_plano = self.aprovar()
        r = self.dc("handoff", str(dir_plano), entrada=self.STDIN + "\n## Fila\n\noutra\n")
        self.assertEqual(r.returncode, 2)
        self.assertIn("repetida", r.stderr)
        self.assertFalse((dir_plano / "_handoff.md").exists())

    def test_heading_de_outro_nivel_dentro_da_secao_nao_a_encerra(self):
        dir_plano = self.aprovar()
        entrada = self.STDIN.replace("1. `0001-01` primeiro", "### Grupo A\n\n1. `0001-01` primeiro")
        r = self.dc("handoff", str(dir_plano), entrada=entrada)
        self.assertEqual(r.returncode, 0, r.stderr)
        self.assertIn("### Grupo A", (dir_plano / "_handoff.md").read_text(encoding="utf-8"))

    def test_plano_inexistente_e_codigo_2(self):
        self.bootstrap()
        r = self.dc("handoff", str(self.raiz_planos / "builder" / "0001-nao-existe"), entrada=self.STDIN)
        self.assertEqual(r.returncode, 2)
        self.assertSemTraceback(r)


class TestVerificar(_ProjetoCase):
    def _unidade_com_teste(self) -> tuple[Path, Path]:
        dir_plano = self.aprovar()
        unidade = self.unidade(dir_plano)
        teste = self.projeto / "scripts" / "tests" / "test_sintetico.py"
        teste.parent.mkdir(parents=True, exist_ok=True)
        teste.write_text("# o runner de teste ignora o conteúdo\n", encoding="utf-8")
        return dir_plano, unidade

    def test_teste_que_passa_e_codigo_0_e_grava_o_estado(self):
        self.stub_de_runner(0)
        _, unidade = self._unidade_com_teste()
        r = self.dc("verificar", str(unidade))
        self.assertEqual((r.returncode, r.stdout), (0, "estado: verified\n"), r.stderr)
        self.assertIn("state: verified", unidade.read_text(encoding="utf-8"))

    def test_dry_run_roda_o_teste_e_nao_grava_estado(self):
        self.stub_de_runner(0)
        _, unidade = self._unidade_com_teste()
        antes = unidade.read_text(encoding="utf-8")
        r = self.dc("verificar", "--dry-run", str(unidade))
        self.assertEqual((r.returncode, r.stdout), (0, "estado: verified\n"), r.stderr)
        self.assertEqual(unidade.read_text(encoding="utf-8"), antes)

    def test_teste_que_falha_e_codigo_1(self):
        self.stub_de_runner(1)
        _, unidade = self._unidade_com_teste()
        r = self.dc("verificar", str(unidade))
        self.assertEqual(r.returncode, 1, r.stderr)
        self.assertEqual(r.stdout.splitlines()[0], "estado: spec")
        self.assertIn("state: spec", unidade.read_text(encoding="utf-8"))

    def test_dry_run_de_teste_que_falha_mostra_a_mensagem_da_falha(self):
        """O executor só chega ao teste por aqui: sem a saída, `spec` não diz o que consertar."""
        self.stub_de_runner(script="echo 'FAIL: test_algo (tests.test_sintetico)'\n"
                                   "echo 'AssertionError: 1 != 2' >&2\nexit 1")
        _, unidade = self._unidade_com_teste()
        antes = unidade.read_text(encoding="utf-8")
        r = self.dc("verificar", "--dry-run", str(unidade))
        self.assertEqual(r.returncode, 1, r.stderr)
        linhas = r.stdout.splitlines()
        self.assertEqual(linhas[0], "estado: spec")
        self.assertIn("FAIL: test_algo (tests.test_sintetico)", linhas)
        self.assertIn("AssertionError: 1 != 2", linhas)
        self.assertEqual(unidade.read_text(encoding="utf-8"), antes)

    def test_saida_longa_e_cortada_nas_ultimas_80_linhas_dizendo_que_cortou(self):
        self.stub_de_runner(script='i=1\nwhile [ "$i" -le 200 ]; do echo "linha $i"; i=$((i+1)); done\nexit 1')
        _, unidade = self._unidade_com_teste()
        r = self.dc("verificar", "--dry-run", str(unidade))
        self.assertEqual(r.returncode, 1, r.stderr)
        linhas = r.stdout.splitlines()
        self.assertEqual(linhas[0], "estado: spec")
        self.assertIn("cortada", linhas[1])
        self.assertIn("80 de 200", linhas[1])
        self.assertEqual(linhas[2:], [f"linha {i}" for i in range(121, 201)])

    def test_saida_curta_aparece_inteira_sem_aviso_de_corte(self):
        self.stub_de_runner(script='echo "so isto"\nexit 1')
        _, unidade = self._unidade_com_teste()
        r = self.dc("verificar", "--dry-run", str(unidade))
        self.assertNotIn("cortada", r.stdout)
        self.assertEqual(r.stdout.splitlines()[-1], "so isto")

    def test_teste_que_passa_nao_imprime_a_saida(self):
        self.stub_de_runner(script='echo "ruido do runner"\necho "Ran 1 test"\nexit 0')
        _, unidade = self._unidade_com_teste()
        r = self.dc("verificar", "--dry-run", str(unidade))
        self.assertEqual((r.returncode, r.stdout), (0, "estado: verified\n"), r.stderr)

    def test_teste_declarado_e_ausente_no_disco_e_spec_com_codigo_1(self):
        self.stub_de_runner(0)
        dir_plano = self.aprovar()
        unidade = self.unidade(dir_plano)
        r = self.dc("verificar", str(unidade))
        self.assertEqual(r.returncode, 1, r.stderr)
        linhas = r.stdout.splitlines()
        self.assertEqual(linhas[0], "estado: spec")
        self.assertTrue(any("não existe no disco" in linha and "test_sintetico.py" in linha for linha in linhas), linhas)

    def test_unidade_sem_test_declarado_e_codigo_2(self):
        dir_plano = self.aprovar()
        unidade = self.unidade(dir_plano, test="")
        r = self.dc("verificar", str(unidade))
        self.assertEqual(r.returncode, 2)
        self.assertIn("test", r.stderr)
        self.assertSemTraceback(r)


class TestNormas(_ProjetoCase):
    """`normas` — o que o `implement` roda para receber o conteúdo das normas que a unidade cita (`L-08`)."""

    def _documento(self) -> Path:
        alvo = self.projeto / "docs" / "norma.md"
        alvo.parent.mkdir(parents=True)
        alvo.write_text(
            "# Norma\n\n## Alfa\n\nTexto de alfa.\n\n### Alfa filho\n\nTexto do filho.\n\n"
            "## Beta\n\nTexto de beta.\n",
            encoding="utf-8",
        )
        return alvo

    def _unidade(self, *linhas: str) -> Path:
        self._documento()
        texto = fixtures.UNIDADE_VALIDA.replace("| Norma | Onde |\n|---|---|", "\n".join(("| Norma | Onde |", "|---|---|", *linhas)))
        alvo = self.projeto / "docs" / "plan" / "01-unidade.md"
        alvo.parent.mkdir(parents=True)
        alvo.write_text(texto, encoding="utf-8")
        return alvo

    def test_imprime_cabecalho_relativo_ao_projeto_e_o_trecho(self):
        unidade = self._unidade("| Alfa | [`norma.md`](../norma.md), seção *Alfa* |")
        r = self.dc("normas", str(unidade))
        self.assertEqual(r.returncode, 0, r.stderr)
        self.assertEqual(
            r.stdout.splitlines(),
            ["### docs/norma.md § Alfa", "## Alfa", "", "Texto de alfa.", "", "### Alfa filho", "",
             "Texto do filho.", ""],
        )

    def test_nao_resolvidas_vao_no_fim_com_a_linha_e_o_motivo_e_o_codigo_continua_0(self):
        unidade = self._unidade(
            "| Alfa | [`norma.md`](../norma.md), seção *Alfa* |",
            "| Simplicidade | `.claude/CLAUDE.md`, invariante 2 |",
            "| Omega | [`norma.md`](../norma.md), seção *Omega* |",
        )
        r = self.dc("normas", str(unidade))
        self.assertEqual(r.returncode, 0, r.stderr)
        linhas = r.stdout.splitlines()
        i = linhas.index("Não resolvidas:")
        self.assertEqual(
            linhas[i + 1 :],
            [
                "| Simplicidade | `.claude/CLAUDE.md`, invariante 2 | — sem link para o arquivo",
                "| Omega | [`norma.md`](../norma.md), seção *Omega* | — seção não encontrada: Omega",
            ],
        )
        self.assertEqual(linhas[0], "### docs/norma.md § Alfa")

    def test_todas_resolvidas_nao_imprime_o_rotulo_de_nao_resolvidas(self):
        unidade = self._unidade("| Beta | [`norma.md`](../norma.md), seção de mesmo nome |")
        r = self.dc("normas", str(unidade))
        self.assertEqual(r.returncode, 0, r.stderr)
        self.assertNotIn("Não resolvidas", r.stdout)
        self.assertIn("Texto de beta.", r.stdout)

    def test_secao_citada_por_duas_linhas_sai_uma_vez(self):
        unidade = self._unidade(
            "| Alfa | [`norma.md`](../norma.md), seção *Alfa* |",
            "| Outra razão | mesma seção |",
        )
        r = self.dc("normas", str(unidade))
        self.assertEqual(r.returncode, 0, r.stderr)
        self.assertEqual(r.stdout.count("### docs/norma.md § Alfa"), 1)
        self.assertEqual(r.stdout.count("Texto de alfa."), 1)

    def test_tabela_sem_linhas_diz_que_nao_ha_norma_citada(self):
        unidade = self._unidade()
        r = self.dc("normas", str(unidade))
        self.assertEqual((r.returncode, r.stdout), (0, "nenhuma norma citada\n"), r.stderr)

    def test_o_atalho_da_skill_implement_repassa_o_comando(self):
        unidade = self._unidade("| Alfa | [`norma.md`](../norma.md), seção *Alfa* |")
        r = _executar(
            self.projeto, "normas", str(unidade), script=_PACOTE / "skills" / "implement" / "dc.py"
        )
        self.assertEqual(r.returncode, 0, r.stderr)
        self.assertIn("### docs/norma.md § Alfa", r.stdout)

    def test_unidade_inexistente_e_codigo_2_sem_traceback(self):
        r = self.dc("normas", str(self.projeto / "nao-existe.md"))
        self.assertEqual(r.returncode, 2)
        self.assertIn("nao-existe.md", r.stderr)
        self.assertSemTraceback(r)

    def test_unidade_sem_a_secao_e_codigo_2_sem_traceback(self):
        unidade = fixtures.unidade(self.projeto)
        unidade.write_text(
            unidade.read_text(encoding="utf-8").replace("## Normas aplicáveis", "## Outra coisa"),
            encoding="utf-8",
        )
        r = self.dc("normas", str(unidade))
        self.assertEqual(r.returncode, 2)
        self.assertIn("Normas aplicáveis", r.stderr)
        self.assertSemTraceback(r)


class TestVerificarComSaida(unittest.TestCase):
    """`verificacao.verificar_com_saida` direto — o motivo do veredito, sem quebrar `verificar`.

    `_executar` é trocado por mock: o que se prova aqui é a saída chegando ao chamador, não o comando
    montado (esse é o `TestVerificar` acima, com runner de verdade). O caso de timeout é a exceção:
    o que ele prova é o texto que `_executar` devolve, então o mock está em `subprocess.run`.
    """

    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self._tmp.cleanup)
        self.raiz = Path(self._tmp.name).resolve()
        patcher = mock.patch.object(lib, "repo_root", return_value=self.raiz)
        patcher.start()
        self.addCleanup(patcher.stop)
        self.teste = self.raiz / "pacote" / "test_x.py"
        self.teste.parent.mkdir()
        self.teste.write_text("# ignorado\n", encoding="utf-8")
        self.unidade = fixtures.unidade(self.raiz, test="pacote/test_x.py")

    def test_teste_que_falha_devolve_a_saida_dele(self):
        with mock.patch.object(verificacao, "_executar", return_value=(1, "FAIL: x\nAssertionError: 1 != 2\n")):
            estado, escreveu, saida = verificacao.verificar_com_saida(self.unidade, dry_run=True)
        self.assertEqual((estado, escreveu), ("spec", False))
        self.assertIn("AssertionError: 1 != 2", saida)

    def test_verificar_segue_devolvendo_so_estado_e_escreveu(self):
        with mock.patch.object(verificacao, "_executar", return_value=(1, "FAIL: x\n")):
            self.assertEqual(verificacao.verificar(self.unidade, dry_run=True), ("spec", False))

    def test_teste_declarado_ausente_diz_qual_arquivo(self):
        self.teste.unlink()
        _, _, saida = verificacao.verificar_com_saida(self.unidade, dry_run=True)
        self.assertIn("não existe no disco", saida)
        self.assertIn("pacote/test_x.py", saida)

    def test_norma_devolve_os_problemas_do_lint(self):
        norma = fixtures.unidade(self.raiz, nome="02-norma.md", unit_type="norma", test="")
        esperado = lint_unidade.lint(norma)
        self.assertTrue(esperado, "a norma sem aprovação precisa ter problema de lint")
        estado, _, saida = verificacao.verificar_com_saida(norma, dry_run=True)
        self.assertEqual(estado, "spec")
        self.assertEqual(saida, "\n".join(esperado))

    def test_timeout_devolve_a_causa_em_vez_de_texto_vazio(self):
        expirado = subprocess.TimeoutExpired(cmd="runner", timeout=verificacao.TIMEOUT_SEGUNDOS)
        ambiente = {k: v for k, v in os.environ.items() if k != verificacao.SENTINELA_REENTRANCIA}
        with mock.patch.dict(os.environ, ambiente, clear=True), \
                mock.patch.object(verificacao.subprocess, "run", side_effect=expirado):
            estado, _, saida = verificacao.verificar_com_saida(self.unidade, dry_run=True)
        self.assertEqual(estado, "spec")
        self.assertIn("timeout", saida)


class TestConcorrentes(unittest.TestCase):
    """`scaffold.concorrentes` direto — a regra do `review-plan`, passo 1."""

    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self._tmp.cleanup)
        self.raiz = Path(self._tmp.name).resolve()
        patcher = mock.patch.object(lib, "plan_root", return_value=self.raiz)
        patcher.start()
        self.addCleanup(patcher.stop)

    def _planos_md(self, *linhas: str) -> None:
        fixtures.planos_md(self.raiz, linhas=list(linhas))

    def _plano(self, *, core: str | None, module: str | None) -> Path:
        texto = "---\n"
        if core is not None:
            texto += f"core: {core}\n"
        if module is not None:
            texto += f"module: {module}\n"
        texto += "---\n\n# plano\n"
        alvo = self.raiz / "plano.md"
        alvo.write_text(texto, encoding="utf-8")
        return alvo

    @staticmethod
    def _linha(numero: str, core: str, modulo: str, situacao: str = "em desenvolvimento") -> str:
        return (
            f"| {numero} | [x](x/{numero}-x.md) | {core} | {modulo} | — | {situacao} | 2026-07-01 |\n"
        )

    def test_conflito_no_core(self):
        linha = self._linha("0001", "builder", "outro")
        self._planos_md(linha, self._linha("0002", "hub", "mcp"))
        achadas = scaffold.concorrentes(self._plano(core="builder", module="novo"))
        self.assertEqual(achadas, [linha.strip()])

    def test_conflito_no_modulo_de_outro_core(self):
        linha = self._linha("0002", "hub", "mcp")
        self._planos_md(self._linha("0001", "builder", "outro"), linha)
        achadas = scaffold.concorrentes(self._plano(core="cortex", module="mcp"))
        self.assertEqual(achadas, [linha.strip()])

    def test_conflito_nos_dois_devolve_cada_linha_uma_vez(self):
        a = self._linha("0001", "builder", "mcp")
        b = self._linha("0002", "hub", "mcp")
        self._planos_md(a, b)
        achadas = scaffold.concorrentes(self._plano(core="builder", module="mcp"))
        self.assertEqual(achadas, [a.strip(), b.strip()])

    def test_sem_conflito_devolve_lista_vazia(self):
        self._planos_md(self._linha("0001", "hub", "mcp"))
        achadas = scaffold.concorrentes(self._plano(core="builder", module="novo"))
        self.assertEqual(achadas, [])

    def test_plano_ja_concluido_no_mesmo_core_nao_conta(self):
        self._planos_md(self._linha("0001", "builder", "mcp", situacao="concluído"))
        achadas = scaffold.concorrentes(self._plano(core="builder", module="mcp"))
        self.assertEqual(achadas, [])

    def test_modulo_vazio_nao_casa_com_modulo_vazio(self):
        self._planos_md(self._linha("0001", "hub", ""))
        achadas = scaffold.concorrentes(self._plano(core="builder", module=None))
        self.assertEqual(achadas, [])

    def test_plano_sem_core_e_nao_verificavel(self):
        self._planos_md(self._linha("0001", "builder", "mcp"))
        self.assertIsNone(scaffold.concorrentes(self._plano(core=None, module="mcp")))

    def test_core_vazio_com_aspas_e_nao_verificavel(self):
        self._planos_md(self._linha("0001", "builder", "mcp"))
        self.assertIsNone(scaffold.concorrentes(self._plano(core='""', module="mcp")))

    def test_core_com_aspas_casa_com_o_core_sem_aspas(self):
        linha = self._linha("0001", "builder", "outro")
        self._planos_md(linha)
        achadas = scaffold.concorrentes(self._plano(core='"builder"', module="novo"))
        self.assertEqual(achadas, [linha.strip()])

    def test_regiao_planos_ausente_levanta_value_error(self):
        (self.raiz / "_planos.md").write_text("# sem região\n", encoding="utf-8")
        with self.assertRaises(ValueError):
            scaffold.concorrentes(self._plano(core="builder", module="mcp"))


if __name__ == "__main__":
    unittest.main()
