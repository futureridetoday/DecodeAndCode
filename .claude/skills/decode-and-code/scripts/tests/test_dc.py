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

import json
import os
import re
import shutil
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
    "guidelines-aplicaveis",
    "criar-guideline",
    "criar-principio",
    "adicionar-guardrail",
    "archive",
    "restore",
    "rethink-start",
    "rethink-record",
    "lint-guardrails",
    "huddle-iniciar",
    "huddle-abrir",
    "huddle-fechar",
    "huddle-concluir",
    "huddle-pauta",
    "huddle-fecho",
    "huddle-lint",
    "huddle-lint-relatorio",
    "huddle-migrar",
    "log-resolver",
    "metodo-listar",
    "metodo-levado",
    "descobrir",
    "setup-iniciar",
    "setup-perfil",
    "setup-registrar",
    "setup-decididas",
    "setup-concluir",
    "setup-lint",
    "setup-escopo",
    "explicar",
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
plan_type: feature
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


class TestCriarGuideline(_ProjetoCase):
    """Plano 0007, T5 — `{nome, descricao, paths, corpo}` pelo stdin, raiz pelo `cwd`."""

    def setUp(self):
        super().setUp()
        self.bootstrap()
        (self.projeto / "src").mkdir()
        (self.projeto / "src" / "botao.tsx").write_text("x", encoding="utf-8")

    def entrada(self, **kw) -> str:
        dados = {"nome": "design-system", "descricao": "Use shadcn.", "paths": ["src/**/*"],
                 "corpo": "Componentes de src/ui."}
        dados.update(kw)
        return json.dumps(dados)

    def test_grava_e_registra_na_raiz_do_projeto(self):
        r = self.dc("criar-guideline", entrada=self.entrada())
        self.assertEqual(r.returncode, 0, r.stderr)
        alvo = self.projeto / ".claude" / "rules" / "design-system.md"
        self.assertEqual(Path(r.stdout.strip()).resolve(), alvo)
        self.assertTrue((self.projeto / ".claude" / "rules" / "registry.json").is_file())

    def test_aguardando_grava_paths_pending(self):
        r = self.dc("criar-guideline", entrada=self.entrada(paths=["app/**/*"], aguardando=True))
        self.assertEqual(r.returncode, 0, r.stderr)

    def test_reprovada_e_codigo_1_sem_arquivo(self):
        r = self.dc("criar-guideline", entrada=self.entrada(paths=["app/**/*"]))
        self.assertEqual(r.returncode, 1, r.stderr)
        self.assertTrue(r.stdout.strip())
        self.assertFalse((self.projeto / ".claude" / "rules" / "design-system.md").exists())

    def test_stdin_vazio_e_codigo_2(self):
        r = self.dc("criar-guideline", entrada="")
        self.assertEqual(r.returncode, 2)
        self.assertSemTraceback(r)

    def test_json_sem_campo_e_codigo_2(self):
        r = self.dc("criar-guideline", entrada=json.dumps({"nome": "x"}))
        self.assertEqual(r.returncode, 2)
        self.assertSemTraceback(r)


class TestCriarPrincipio(_ProjetoCase):
    """Plano 0016 — `{nome, enunciado, teste}` pelo stdin, raiz pelo `cwd`."""

    def setUp(self):
        super().setUp()
        self.bootstrap()

    def entrada(self, **kw) -> str:
        dados = {"nome": "Marca nova sem código novo", "enunciado": "Marca nova entra só por tokens.",
                 "teste": "Adicionar uma marca muda só tokens vindos do Figma."}
        dados.update(kw)
        return json.dumps(dados)

    def test_grava_na_raiz_do_projeto(self):
        r = self.dc("criar-principio", entrada=self.entrada())
        self.assertEqual(r.returncode, 0, r.stderr)
        alvo = self.projeto / ".claude" / "rules" / "principles.md"
        self.assertEqual(Path(r.stdout.strip()).resolve(), alvo)
        self.assertIn("## Marca nova sem código novo", alvo.read_text(encoding="utf-8"))

    def test_repetido_e_codigo_1(self):
        self.dc("criar-principio", entrada=self.entrada())
        r = self.dc("criar-principio", entrada=self.entrada())
        self.assertEqual(r.returncode, 1, r.stderr)
        self.assertTrue(r.stdout.strip())

    def test_json_sem_campo_e_codigo_2(self):
        r = self.dc("criar-principio", entrada=json.dumps({"nome": "x"}))
        self.assertEqual(r.returncode, 2)
        self.assertSemTraceback(r)


class TestLog(_ProjetoCase):
    """Plano 0018 — o `main` registra toda chamada e a saída 2 vira `E-XX`; `log-resolver` o apaga."""

    def setUp(self):
        super().setUp()
        self.bootstrap()
        for args in (["init", "-q"], ["config", "user.name", "Ana Lima"], ["config", "user.email", "a@a"]):
            subprocess.run(["git", *args], cwd=self.projeto, check=True)
        self.erros = self.projeto / ".claude" / "log" / "erros"

    def eventos(self) -> list[dict]:
        arquivo = self.projeto / ".claude" / "log" / "eventos.jsonl"
        return [json.loads(l) for l in arquivo.read_text(encoding="utf-8").splitlines()]

    def test_toda_chamada_vira_evento(self):
        self.assertEqual(self.dc("validar-nome", "nome-bom").returncode, 0)
        self.assertEqual(self.eventos()[-1]["comando"], ["validar-nome"])
        self.assertEqual(self.eventos()[-1]["codigo"], 0)

    def test_excecao_mantem_stderr_e_grava_e_xx_com_traceback(self):
        r = self.dc("normas", "nao-existe.md")
        self.assertEqual(r.returncode, 2)
        self.assertEqual(r.stderr.count("\n"), 1)
        self.assertSemTraceback(r)
        texto = (self.erros / "E-01.md").read_text(encoding="utf-8")
        self.assertIn("Traceback", texto)
        self.assertIn('alvo: "nao-existe.md"', texto)

    def test_erro_de_uso_do_argparse_grava_e_xx(self):
        r = self.dc("normas")
        self.assertEqual(r.returncode, 2)
        self.assertIn("argparse", (self.erros / "E-01.md").read_text(encoding="utf-8"))

    def test_log_que_nao_escreve_nao_muda_a_saida(self):
        shutil.rmtree(self.projeto / ".claude" / "log")
        (self.projeto / ".claude" / "log").write_text("arquivo no lugar da pasta", encoding="utf-8")
        r = self.dc("normas", "nao-existe.md")
        self.assertEqual(r.returncode, 2)
        self.assertSemTraceback(r)

    def test_projeto_sem_bootstrap_nao_ganha_log(self):
        outro = self.projeto.parent / "sem-metodo"
        (outro / ".claude").mkdir(parents=True)
        (outro / "docs").mkdir()
        self.assertEqual(_executar(outro, "validar-nome", "nome-bom").returncode, 0)
        self.assertFalse((outro / ".claude" / "log").exists())

    def test_log_resolver(self):
        self.dc("normas", "nao-existe.md")
        recusado = self.dc("log-resolver", "E-01", "metodo")
        self.assertEqual(recusado.returncode, 1, recusado.stderr)
        self.assertTrue((self.erros / "E-01.md").exists())
        self.assertEqual(self.dc("log-resolver", "E-01", "H-01").returncode, 1)
        self.dc("huddle-iniciar")
        self.dc("huddle-abrir", "pergunta", entrada="Por que o normas falhou?")
        r = self.dc("log-resolver", "E-01", "H-01")
        self.assertEqual(r.returncode, 0, r.stdout + r.stderr)
        self.assertFalse((self.erros / "E-01.md").exists())

    def test_pauta_resume_o_log_e_concluir_apaga_so_o_que_ela_mostrou(self):
        self.dc("huddle-iniciar")
        self.dc("normas", "nao-existe.md")
        pauta = self.dc("huddle-pauta")
        self.assertIn("## Log desde", pauta.stdout)
        self.assertIn("comando normas, saída 2: 1", pauta.stdout)
        self.assertIn("E-01 aberto desde", pauta.stdout)
        self.dc("validar-nome", "depois-da-pauta")
        r = self.dc("huddle-concluir")
        self.assertEqual(r.returncode, 0, r.stderr)
        comandos = [e.get("comando") for e in self.eventos()]
        self.assertNotIn(["normas"], comandos)
        self.assertIn(["validar-nome"], comandos)
        self.assertTrue((self.erros / "E-01.md").exists())


class TestMetodo(_ProjetoCase):
    """Plano 0019 — evidência no `huddle-abrir`, destino `método` no `huddle-fechar` e no
    `log-resolver`, e a fila `metodo-listar` / `metodo-levado`."""

    def setUp(self):
        super().setUp()
        self.bootstrap()
        for args in (["init", "-q"], ["config", "user.name", "Ana Lima"], ["config", "user.email", "a@a"]):
            subprocess.run(["git", *args], cwd=self.projeto, check=True)
        self.huddle = self.raiz_planos / "system" / "huddle" / "ana-lima.md"
        self.metodo = self.projeto / ".claude" / "log" / "metodo"

    def abrir(self, evidencia: str, texto: str = "O lint corta a tarefa de várias linhas.") -> subprocess.CompletedProcess:
        return self.dc("huddle-abrir", "padrão", "--evidencia", evidencia, entrada=texto)

    def test_evidencia_no_fim_do_corpo_e_a_pauta_mostra_o_texto(self):
        r = self.abrir("E-03")
        self.assertEqual(r.returncode, 0, r.stdout + r.stderr)
        self.assertIn("várias linhas.\n\nEvidência: E-03\n", self.huddle.read_text(encoding="utf-8"))
        pauta = self.dc("huddle-pauta").stdout
        self.assertIn("H-01 · padrão · ", pauta)
        self.assertIn("O lint corta a tarefa", pauta)
        self.assertNotIn("Evidência", pauta)
        self.assertEqual(self.dc("huddle-lint").returncode, 0)

    def test_evidencia_fora_do_vocabulario_e_codigo_1_sem_escrever(self):
        self.dc("huddle-iniciar")
        antes = self.huddle.read_text(encoding="utf-8")
        r = self.abrir("palpite")
        self.assertEqual(r.returncode, 1, r.stderr)
        self.assertEqual(self.huddle.read_text(encoding="utf-8"), antes)

    def test_fechar_metodo_sem_texto_nao_fecha(self):
        self.abrir("E-03")
        r = self.dc("huddle-fechar", "H-01", "método", entrada="")
        self.assertEqual(r.returncode, 1, r.stderr)
        self.assertIn("### H-01", self.huddle.read_text(encoding="utf-8"))
        self.assertFalse(self.metodo.exists())

    def test_fechar_metodo_grava_m_xx_e_fecha(self):
        self.abrir("E-03")
        self.abrir("bloqueio: sem-segredo", texto="Outro.")
        r = self.dc("huddle-fechar", "H-01", "método", entrada="O backlog corta tarefa de várias linhas.")
        self.assertEqual(r.returncode, 0, r.stdout + r.stderr)
        self.assertEqual(self.dc("huddle-fechar", "H-02", "método", entrada="Genérico.").returncode, 0)
        primeiro = (self.metodo / "M-01.md").read_text(encoding="utf-8")
        for esperado in ('origem: "H-01"', 'evidencia: "E-03"', "O backlog corta tarefa"):
            self.assertIn(esperado, primeiro)
        self.assertIn('evidencia: ""', (self.metodo / "M-02.md").read_text(encoding="utf-8"))
        self.assertNotIn("sem-segredo", (self.metodo / "M-02.md").read_text(encoding="utf-8"))
        huddle = self.huddle.read_text(encoding="utf-8")
        self.assertNotIn("### H-01", huddle)
        self.assertRegex(huddle, r"\| H-01 \| `padrão` \| [\d-]+ \| método: M-01 \|")

    def test_fechar_metodo_com_gravacao_falhando_nao_fecha(self):
        self.abrir("E-03")
        self.metodo.parent.mkdir(parents=True, exist_ok=True)
        self.metodo.write_text("arquivo no lugar da pasta", encoding="utf-8")
        r = self.dc("huddle-fechar", "H-01", "método", entrada="Genérico.")
        self.assertEqual(r.returncode, 1, r.stderr)
        self.assertIn("### H-01", self.huddle.read_text(encoding="utf-8"))

    def test_fechar_metodo_id_que_nao_esta_aberto(self):
        self.dc("huddle-iniciar")
        r = self.dc("huddle-fechar", "H-09", "método", entrada="Genérico.")
        self.assertEqual(r.returncode, 1, r.stderr)
        self.assertFalse(self.metodo.exists())

    def test_log_resolver_metodo_listar_e_levar(self):
        self.dc("normas", "nao-existe.md")
        r = self.dc("log-resolver", "E-01", "método")
        self.assertEqual(r.returncode, 0, r.stdout + r.stderr)
        self.assertIn("método: M-01", r.stdout)
        self.assertFalse((self.projeto / ".claude" / "log" / "erros" / "E-01.md").exists())
        self.abrir("L-04")
        self.dc("huddle-fechar", "H-01", "método", entrada="Genérico.")

        listado = self.dc("metodo-listar")
        self.assertEqual(listado.returncode, 0, listado.stderr)
        self.assertIn("=== M-01", listado.stdout)
        self.assertIn("=== M-02", listado.stdout)
        self.assertIn('origem: "E-01"', listado.stdout)
        self.assertNotIn(str(self.projeto), listado.stdout)
        self.assertIn("M-01 (de E-01) pendente desde", self.dc("huddle-pauta").stdout)

        self.assertEqual(self.dc("metodo-levado", "M-01", "  ").returncode, 1)
        r = self.dc("metodo-levado", "M-01", "DecodeAndCode H-22")
        self.assertEqual(r.returncode, 0, r.stdout + r.stderr)
        self.assertFalse((self.metodo / "M-01.md").exists())
        self.assertEqual(self.dc("metodo-levado", "M-01", "de novo").returncode, 1)

    def test_listar_vazio(self):
        r = self.dc("metodo-listar")
        self.assertEqual(r.returncode, 0, r.stderr)
        self.assertIn("nenhum M-XX pendente", r.stdout)

    def test_log_fora_do_git(self):
        self.dc("huddle-iniciar")
        subprocess.run(["git", "add", "-A"], cwd=self.projeto, check=True)
        subprocess.run(["git", "commit", "-qm", "c"], cwd=self.projeto, check=True)
        self.abrir("E-03")
        subprocess.run(["git", "add", "-A"], cwd=self.projeto, check=True)
        subprocess.run(["git", "commit", "-qm", "c2"], cwd=self.projeto, check=True)
        self.dc("huddle-fechar", "H-01", "método", entrada="Genérico.")
        status = subprocess.run(["git", "status", "--porcelain"], cwd=self.projeto, capture_output=True, text=True).stdout
        self.assertNotIn(".claude/log", status)
        self.assertTrue((self.metodo / "M-01.md").exists())


class TestAdicionarGuardrail(_ProjetoCase):
    """Plano 0007, T5 — `{regra, proibido, permitido}` pelo stdin."""

    REGRA = {"nome": "sem-classname", "ferramenta": "^Write$", "detector": "className=",
             "mensagem": "Estilo vai no .styles.ts."}

    def setUp(self):
        super().setUp()
        self.bootstrap()

    def entrada(self, **regra) -> str:
        return json.dumps({
            "regra": {**self.REGRA, **regra},
            "proibido": {"tool_name": "Write", "tool_input": {"content": '<a className="x"/>'}},
            "permitido": {"tool_name": "Write", "tool_input": {"content": "<A/>"}},
        })

    def test_grava_no_guardrails_do_projeto(self):
        r = self.dc("adicionar-guardrail", entrada=self.entrada())
        self.assertEqual(r.returncode, 0, r.stderr)
        arquivo = self.projeto / ".claude" / "guardrails.json"
        self.assertEqual(json.loads(arquivo.read_text(encoding="utf-8"))["regras"][0]["nome"], "sem-classname")

    def test_regra_que_nao_prova_e_codigo_1(self):
        r = self.dc("adicionar-guardrail", entrada=self.entrada(detector="nunca-casa"))
        self.assertEqual(r.returncode, 1, r.stderr)
        self.assertFalse((self.projeto / ".claude" / "guardrails.json").exists())

    def test_stdin_vazio_e_codigo_2(self):
        r = self.dc("adicionar-guardrail", entrada="")
        self.assertEqual(r.returncode, 2)
        self.assertSemTraceback(r)


class TestEditarArquivar(_ProjetoCase):
    """Plano 0020, tarefa 7 — `--replace`, `archive`, `restore`, `rethink-start` e `rethink-record`."""

    REGRA = TestAdicionarGuardrail.REGRA
    PROIBIDO = {"tool_name": "Write", "tool_input": {"content": '<a className="x"/>'}}
    PERMITIDO = {"tool_name": "Write", "tool_input": {"content": "<A/>"}}

    def setUp(self):
        super().setUp()
        self.bootstrap()
        for args in (["init", "-q"], ["config", "user.name", "Ana Lima"], ["config", "user.email", "a@a"]):
            subprocess.run(["git", *args], cwd=self.projeto, check=True)
        (self.projeto / "src").mkdir()
        (self.projeto / "src" / "a.ts").write_text("x", encoding="utf-8")
        self.rules = self.projeto / ".claude" / "rules"
        self.arquivo = self.projeto / ".claude" / "archive"

    def ok(self, *args: str, entrada: str | None = None) -> subprocess.CompletedProcess:
        r = self.dc(*args, entrada=entrada)
        self.assertEqual(r.returncode, 0, r.stdout + r.stderr)
        return r

    def principio(self, enunciado="Ajudar a economizar.", *flags):
        dados = {"nome": "North star", "enunciado": enunciado, "teste": "Mostra o que poupou."}
        return self.dc("criar-principio", *flags, entrada=json.dumps(dados))

    def guideline(self, corpo="# Paleta\n\nAzul.", *flags):
        dados = {"nome": "paleta", "descricao": "Vale no src.", "paths": ["src/**/*"], "corpo": corpo}
        return self.dc("criar-guideline", *flags, entrada=json.dumps(dados))

    def guardrail(self, *flags, **regra):
        dados = {"regra": {**self.REGRA, **regra}, "proibido": self.PROIBIDO, "permitido": self.PERMITIDO}
        return self.dc("adicionar-guardrail", *flags, entrada=json.dumps(dados))

    def test_replace_nos_tres_escritores(self):
        self.assertEqual(self.principio().returncode, 0)
        self.assertEqual(self.guideline().returncode, 0)
        self.assertEqual(self.guardrail().returncode, 0)

        self.assertEqual(self.principio("Consciência das compras.", "--replace").returncode, 0)
        self.assertEqual(self.guideline("# Paleta\n\nLaranja.", "--replace").returncode, 0)
        self.assertEqual(self.guardrail("--replace", mensagem="Estilo no tema.").returncode, 0)

        self.assertIn("Consciência das compras.", (self.rules / "principles.md").read_text(encoding="utf-8"))
        self.assertIn("Laranja.", (self.rules / "paleta.md").read_text(encoding="utf-8"))
        regras = json.loads((self.projeto / ".claude" / "guardrails.json").read_text(encoding="utf-8"))["regras"]
        self.assertEqual([r["mensagem"] for r in regras], ["Estilo no tema."])

    def test_replace_de_item_inexistente_e_codigo_1(self):
        for r in (self.principio("x", "--replace"), self.guideline("# P\n\nx", "--replace"),
                  self.guardrail("--replace")):
            with self.subTest(saida=r.stdout):
                self.assertEqual(r.returncode, 1, r.stderr)

    def test_archive_das_tres_camadas_com_o_user_name(self):
        self.principio()
        self.guideline()
        self.guardrail()
        for camada, nome in (("principle", "North star"), ("guideline", "paleta"), ("guardrail", "sem-classname")):
            with self.subTest(camada=camada):
                self.ok("archive", camada, nome, entrada="Rumo novo.\n")
        self.assertIn("**archived_by:** Ana Lima", (self.arquivo / "rules" / "principles.md").read_text(encoding="utf-8"))
        self.assertIn('archived_by: "Ana Lima"', (self.arquivo / "rules" / "paleta.md").read_text(encoding="utf-8"))
        morta = json.loads((self.arquivo / "guardrails.json").read_text(encoding="utf-8"))["regras"][0]
        self.assertEqual((morta["archived_by"], morta["reason"]), ("Ana Lima", "Rumo novo."))

    def test_archive_sem_motivo_e_codigo_1(self):
        self.guideline()
        r = self.dc("archive", "guideline", "paleta", entrada="  \n")
        self.assertEqual(r.returncode, 1, r.stderr)
        self.assertTrue((self.rules / "paleta.md").exists())

    def test_archive_com_nome_desconhecido_e_codigo_1(self):
        r = self.dc("archive", "guardrail", "nao-existe", entrada="Motivo.")
        self.assertEqual(r.returncode, 1, r.stderr)
        self.assertSemTraceback(r)

    def test_archive_sem_user_name_e_codigo_1(self):
        self.guideline()
        subprocess.run(["git", "config", "--unset", "user.name"], cwd=self.projeto, check=True)
        ambiente = {"GIT_CONFIG_GLOBAL": os.devnull, "GIT_CONFIG_NOSYSTEM": "1"}
        with mock.patch.dict(os.environ, ambiente):
            r = self.dc("archive", "guideline", "paleta", entrada="Motivo.")
        self.assertEqual(r.returncode, 1, r.stderr)
        self.assertIn("git config user.name", r.stdout)
        self.assertTrue((self.rules / "paleta.md").exists())

    def test_camada_fora_da_lista_e_erro_de_uso(self):
        self.assertEqual(self.dc("archive", "regra", "x", entrada="Motivo.").returncode, 2)

    def test_restore_das_tres_camadas(self):
        self.principio()
        self.guideline()
        self.guardrail()
        for camada, nome in (("principle", "North star"), ("guideline", "paleta"), ("guardrail", "sem-classname")):
            self.ok("archive", camada, nome, entrada="Rumo novo.")
        self.ok("restore", "principle", "North star")
        self.ok("restore", "guideline", "paleta")
        self.ok("restore", "guardrail", "sem-classname",
                entrada=json.dumps({"proibido": self.PROIBIDO, "permitido": self.PERMITIDO}))
        self.assertIn("## North star", (self.rules / "principles.md").read_text(encoding="utf-8"))
        self.assertTrue((self.rules / "paleta.md").exists())
        regras = json.loads((self.projeto / ".claude" / "guardrails.json").read_text(encoding="utf-8"))["regras"]
        self.assertEqual([r["nome"] for r in regras], ["sem-classname"])

    def test_restore_do_que_nao_esta_arquivado_ou_nao_passa_e_codigo_1(self):
        self.assertEqual(self.dc("restore", "guideline", "paleta").returncode, 1)
        self.guardrail()
        self.ok("archive", "guardrail", "sem-classname", entrada="Motivo.")
        par_invertido = json.dumps({"proibido": self.PERMITIDO, "permitido": self.PROIBIDO})
        self.assertEqual(self.dc("restore", "guardrail", "sem-classname", entrada=par_invertido).returncode, 1)

    def test_restore_de_guardrail_sem_par_e_codigo_2(self):
        r = self.dc("restore", "guardrail", "sem-classname", entrada="")
        self.assertEqual(r.returncode, 2)
        self.assertSemTraceback(r)

    def test_rethink_start_e_record(self):
        self.ok("rethink-start", entrada=json.dumps({"mudanca": "Marca laranja."}))
        self.ok("rethink-record", entrada=json.dumps(
            {"camada": "guideline", "nome": "paleta", "decisao": "arquivado", "motivo": "Marca laranja."}
        ))
        texto = (self.raiz_planos / "system" / "rethink.md").read_text(encoding="utf-8")
        self.assertRegex(texto, r"## \d{4}-\d{2}-\d{2} · Ana Lima\n\n\*\*O que mudou:\*\* Marca laranja\.")
        self.assertTrue(texto.endswith("| guideline | paleta | arquivado | Marca laranja. |\n"))

    def test_rethink_record_fora_do_vocabulario_e_codigo_1(self):
        self.ok("rethink-start", entrada=json.dumps({"mudanca": "Marca laranja."}))
        r = self.dc("rethink-record", entrada=json.dumps(
            {"camada": "guideline", "nome": "paleta", "decisao": "editada", "motivo": ""}
        ))
        self.assertEqual(r.returncode, 1, r.stderr)

    def test_rethink_json_incompleto_e_codigo_2(self):
        for comando in ("rethink-start", "rethink-record"):
            with self.subTest(comando=comando):
                r = self.dc(comando, entrada=json.dumps({}))
                self.assertEqual(r.returncode, 2)
                self.assertSemTraceback(r)


class TestLintGuardrails(_ProjetoCase):
    def setUp(self):
        super().setUp()
        self.bootstrap()
        self.arquivo = self.projeto / ".claude" / "guardrails.json"
        self.arquivo.parent.mkdir(parents=True, exist_ok=True)

    def test_arquivo_valido_e_ok(self):
        self.arquivo.write_text('{"regras": []}', encoding="utf-8")
        r = self.dc("lint-guardrails")
        self.assertEqual(r.returncode, 0, r.stderr)
        self.assertIn("ok", r.stdout)

    def test_arquivo_malformado_e_codigo_1(self):
        self.arquivo.write_text('{"regras": [{"nome": "x"}]}', encoding="utf-8")
        r = self.dc("lint-guardrails")
        self.assertEqual(r.returncode, 1)
        self.assertIn("ferramenta", r.stdout)

    def test_arquivo_ausente_e_codigo_2(self):
        r = self.dc("lint-guardrails")
        self.assertEqual(r.returncode, 2)
        self.assertSemTraceback(r)


class TestSetup(_ProjetoCase):
    """Plano 0009, unidade 01 — os seis `setup-*` sobre `<plan_root>/system/setup.md`."""

    REGISTRO = '{"chave": "usar-ruff", "tipo": "guideline", "origem": "stack", "resultado": "aceita", "detalhe": "python.md"}'

    def setUp(self):
        super().setUp()
        self.bootstrap()
        self.arquivo = self.raiz_planos / "system" / "setup.md"

    def test_iniciar_cria_e_nao_sobrescreve(self):
        r = self.dc("setup-iniciar")
        self.assertEqual(r.returncode, 0, r.stderr)
        self.assertTrue(self.arquivo.is_file())
        r = self.dc("setup-iniciar")
        self.assertEqual(r.returncode, 0, r.stderr)
        self.assertIn("já existe", r.stdout)

    def test_ciclo_completo_com_lint_e_decididas(self):
        self.dc("setup-iniciar")
        perfil = '{"objetivo": "o", "escopo": "e", "stack": "s", "confirmacao": "c"}'
        self.assertEqual(self.dc("setup-perfil", entrada=perfil).returncode, 0)
        self.assertEqual(self.dc("setup-registrar", entrada=self.REGISTRO).returncode, 0)
        self.assertEqual(self.dc("setup-decididas").stdout.splitlines(), ["usar-ruff"])
        r = self.dc("setup-concluir", "--data", "2026-11-16")
        self.assertEqual((r.returncode, r.stdout.strip()), (0, "completed_at: 2026-11-16"), r.stderr)
        r = self.dc("setup-lint")
        self.assertEqual(r.returncode, 0, r.stdout + r.stderr)

    def test_concluir_sem_data_usa_hoje(self):
        from datetime import date

        self.dc("setup-iniciar")
        r = self.dc("setup-concluir")
        self.assertEqual(r.returncode, 0, r.stderr)
        self.assertIn(date.today().isoformat(), r.stdout)

    def test_valor_recusado_sai_com_1_sem_mudar_o_arquivo(self):
        self.dc("setup-iniciar")
        antes = self.arquivo.read_text(encoding="utf-8")
        ruim = self.REGISTRO.replace('"guideline"', '"convenção"')
        r = self.dc("setup-registrar", entrada=ruim)
        self.assertEqual(r.returncode, 1, r.stderr)
        self.assertEqual(self.dc("setup-concluir", "--data", "ontem").returncode, 1)
        self.assertEqual(self.arquivo.read_text(encoding="utf-8"), antes)

    def test_lint_reprovado_sai_com_1(self):
        self.dc("setup-iniciar")
        self.arquivo.write_text(
            self.arquivo.read_text(encoding="utf-8") + "| a | regra | stack | aceita | x | 2026-11-16 |\n",
            encoding="utf-8",
        )
        self.assertEqual(self.dc("setup-lint").returncode, 1)

    def test_stdin_vazio_ou_incompleto_sai_com_2(self):
        self.dc("setup-iniciar")
        for subcomando in ("setup-perfil", "setup-registrar"):
            with self.subTest(subcomando=subcomando, entrada="vazio"):
                r = self.dc(subcomando, entrada="")
                self.assertEqual(r.returncode, 2)
                self.assertSemTraceback(r)
            with self.subTest(subcomando=subcomando, entrada="incompleto"):
                r = self.dc(subcomando, entrada='{"chave": "x"}')
                self.assertEqual(r.returncode, 2)
                self.assertSemTraceback(r)

    def test_arquivo_ausente_sai_com_2(self):
        for subcomando in ("setup-decididas", "setup-lint", "setup-concluir"):
            with self.subTest(subcomando=subcomando):
                r = self.dc(subcomando)
                self.assertEqual(r.returncode, 2)
                self.assertSemTraceback(r)
        r = self.dc("setup-registrar", entrada=self.REGISTRO)
        self.assertEqual(r.returncode, 2)


class TestSetupEscopo(_ProjetoCase):
    """Plano 0009, unidade 03 — `setup-escopo` lê e, com `--aplicar`, habilita o plugin."""

    def setUp(self):
        super().setUp()
        self.bootstrap()
        self.settings = self.projeto / ".claude" / "settings.json"

    def test_sem_aplicar_mostra_o_estado_e_nao_escreve(self):
        r = self.dc("setup-escopo")
        self.assertEqual(r.returncode, 0, r.stderr)
        self.assertIn("habilitado: false", r.stdout)
        self.assertIn("marketplace: false", r.stdout)
        self.assertFalse(self.settings.exists())

    def test_aplicar_escreve_e_a_segunda_vez_nao_muda(self):
        r = self.dc("setup-escopo", "--aplicar")
        self.assertEqual((r.returncode, r.stdout.strip()), (0, "habilitado"), r.stderr)
        escrito = self.settings.read_text(encoding="utf-8")
        r = self.dc("setup-escopo", "--aplicar")
        self.assertEqual((r.returncode, r.stdout.strip()), (0, "já estava habilitado"), r.stderr)
        self.assertEqual(self.settings.read_text(encoding="utf-8"), escrito)
        self.assertIn("habilitado: true", self.dc("setup-escopo").stdout)

    def test_json_invalido_sai_com_2_e_o_arquivo_fica_intacto(self):
        self.settings.parent.mkdir(parents=True, exist_ok=True)
        self.settings.write_text("{ quebrado", encoding="utf-8")
        for args in ((), ("--aplicar",)):
            with self.subTest(args=args):
                r = self.dc("setup-escopo", *args)
                self.assertEqual(r.returncode, 2)
                self.assertSemTraceback(r)
        self.assertEqual(self.settings.read_text(encoding="utf-8"), "{ quebrado")


class TestDescobrir(_ProjetoCase):
    """Plano 0009, unidade 02 — `descobrir` inventaria o projeto e sai 0."""

    def test_imprime_fontes_e_ja_existe(self):
        self.bootstrap()
        (self.projeto / "components.json").write_text("{}", encoding="utf-8")
        r = self.dc("descobrir")
        self.assertEqual(r.returncode, 0, r.stderr)
        self.assertIn("### components.json", r.stdout)
        self.assertIn("## Já existe", r.stdout)


class TestHuddle(_ProjetoCase):
    """Plano 0008, T4 — os nove `huddle-*`, resolvendo o arquivo da pessoa pelo `user.name` local."""

    def setUp(self):
        super().setUp()
        self.bootstrap()
        for args in (["init", "-q"], ["config", "user.name", "Ana Lima"], ["config", "user.email", "a@a"]):
            subprocess.run(["git", *args], cwd=self.projeto, check=True)
        self.arquivo = self.raiz_planos / "system" / "huddle" / "ana-lima.md"

    def abrir(self, texto: str = "Qual o teto?", tipo: str = "pergunta") -> subprocess.CompletedProcess:
        return self.dc("huddle-abrir", tipo, entrada=texto)

    def test_iniciar_cria_o_arquivo_da_pessoa(self):
        r = self.dc("huddle-iniciar")
        self.assertEqual(r.returncode, 0, r.stderr)
        self.assertTrue(self.arquivo.is_file())
        self.assertEqual(self.dc("huddle-iniciar").returncode, 0)

    def test_abrir_le_o_texto_do_stdin_e_imprime_o_id(self):
        r = self.abrir()
        self.assertEqual(r.returncode, 0, r.stderr)
        self.assertEqual(r.stdout.strip(), "H-01")
        self.assertIn("Qual o teto?", self.arquivo.read_text(encoding="utf-8"))
        self.assertIn("· ana-lima", self.arquivo.read_text(encoding="utf-8"))

    def test_abrir_com_autor(self):
        r = self.dc("huddle-abrir", "pergunta", "--autor", "Claude", entrada="x")
        self.assertEqual(r.returncode, 0, r.stderr)
        self.assertIn("· Claude", self.arquivo.read_text(encoding="utf-8"))

    def test_abrir_stdin_vazio_e_codigo_2(self):
        r = self.abrir(texto="")
        self.assertEqual(r.returncode, 2)
        self.assertSemTraceback(r)

    def test_abrir_tipo_invalido_e_codigo_1(self):
        r = self.abrir(tipo="ideia")
        self.assertEqual(r.returncode, 1, r.stderr)

    def test_fechar_e_concluir(self):
        self.abrir()
        r = self.dc("huddle-fechar", "H-01", "descartada")
        self.assertEqual(r.returncode, 0, r.stderr)
        r = self.dc("huddle-concluir", "--data", "2026-11-15")
        self.assertEqual(r.returncode, 0, r.stderr)
        texto = self.arquivo.read_text(encoding="utf-8")
        self.assertIn("| H-01 |", texto)
        self.assertIn("last_huddle: 2026-11-15", texto)

    def test_fechar_id_inexistente_e_codigo_1(self):
        self.dc("huddle-iniciar")
        self.assertEqual(self.dc("huddle-fechar", "H-09", "x").returncode, 1)

    def test_pauta_lista_as_abertas(self):
        self.abrir(texto="**Título da pergunta.**")
        r = self.dc("huddle-pauta")
        self.assertEqual(r.returncode, 0, r.stderr)
        self.assertIn("H-01", r.stdout)

    def test_fecho_imprime_o_huddle_do_codex_mesmo_com_a_norma_antiga_no_projeto(self):
        """K-12: a fonte é o codex do pacote; a norma copiada ao projeto não é lida."""
        norma = self.raiz_planos / "system" / "modelo-dev-units.md"
        norma.parent.mkdir(parents=True, exist_ok=True)
        norma.write_text("# Norma antiga\n\n## Huddle\n\nSem as subseções.\n", encoding="utf-8")
        r = self.dc("huddle-fecho")
        self.assertEqual(r.returncode, 0, r.stderr)
        self.assertIn("§ Huddle", r.stdout)
        self.assertNotIn("Sem as subseções", r.stdout)

    def test_explicar_imprime_as_secoes_do_metodo_do_codex(self):
        r = self.dc("explicar")
        self.assertEqual(r.returncode, 0, r.stderr)
        for titulo in ("Workflow", "Decode", "Porte", "Cold-start"):
            with self.subTest(titulo=titulo):
                self.assertIn(f"§ {titulo}", r.stdout)

    def test_lint_do_arquivo_da_pessoa(self):
        self.dc("huddle-iniciar")
        r = self.dc("huddle-lint")
        self.assertEqual(r.returncode, 0, r.stderr)
        self.assertIn("ok", r.stdout)

    def test_lint_relatorio_confere_ids(self):
        self.abrir()
        ok = self.dc("huddle-lint-relatorio", entrada="Feito.\n\nentradas novas no huddle: 1 (H-01)\n")
        self.assertEqual(ok.returncode, 0, ok.stdout + ok.stderr)
        ruim = self.dc("huddle-lint-relatorio", entrada="entradas novas no huddle: 1 (H-07)\n")
        self.assertEqual(ruim.returncode, 1)

    def test_lint_relatorio_sem_arquivo_da_pessoa_reprova_ids_com_1(self):
        r = self.dc("huddle-lint-relatorio", entrada="entradas novas no huddle: 1 (H-01)\n")
        self.assertEqual(r.returncode, 1, r.stderr)
        zero = self.dc("huddle-lint-relatorio", entrada="entradas novas no huddle: 0\n")
        self.assertEqual(zero.returncode, 0, zero.stderr)

    def test_lint_relatorio_stdin_vazio_e_codigo_2(self):
        r = self.dc("huddle-lint-relatorio", entrada="")
        self.assertEqual(r.returncode, 2)
        self.assertSemTraceback(r)

    def test_migrar_move_o_arquivo_unico(self):
        antigo = self.raiz_planos / "system" / "huddle.md"
        antigo.write_text("---\nname: huddle\n# system\nscope: project\n---\n\n## Abertas\n\n## Fechadas\n\n| # | Tipo | Fechada em | Destino |\n|---|---|---|---|\n", encoding="utf-8")
        subprocess.run(["git", "add", "-A"], cwd=self.projeto, check=True)
        subprocess.run(["git", "commit", "-q", "-m", "x"], cwd=self.projeto, check=True)
        r = self.dc("huddle-migrar")
        self.assertEqual(r.returncode, 0, r.stderr)
        self.assertFalse(antigo.exists())
        self.assertTrue(self.arquivo.is_file())
        self.assertIn("nada a migrar", self.dc("huddle-migrar").stdout)

    def test_sem_user_name_e_codigo_2_com_a_instrucao(self):
        subprocess.run(["git", "config", "--unset", "user.name"], cwd=self.projeto, check=True)
        ambiente = {"GIT_CONFIG_GLOBAL": os.devnull, "GIT_CONFIG_NOSYSTEM": "1"}
        with mock.patch.dict(os.environ, ambiente):
            r = self.dc("huddle-iniciar")
        self.assertEqual(r.returncode, 2)
        self.assertIn("git config user.name", r.stderr)


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

    def test_norma_sem_aprovacao_devolve_o_que_falta(self):
        norma = fixtures.unidade(self.raiz, nome="02-norma.md", unit_type="norma", test="")
        estado, _, saida = verificacao.verificar_com_saida(norma, dry_run=True)
        self.assertEqual(estado, "spec")
        self.assertIn("approved_by", saida)
        self.assertIn("approved_at", saida)

    def test_norma_devolve_os_problemas_do_lint(self):
        norma = fixtures.unidade(
            self.raiz, nome="02-norma.md", unit_type="norma", test="pacote/test_x.py",
            approved_by="Bortoli", approved_at="2020-01-01",
        )
        esperado = lint_unidade.lint(norma)
        self.assertTrue(esperado, "norma com test: preenchido precisa ter problema de lint")
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
