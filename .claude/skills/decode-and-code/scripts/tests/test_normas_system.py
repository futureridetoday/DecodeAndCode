#!/usr/bin/env python3
"""Testes da camada normativa em docs/plan/system/ — unidades 0001-08, 0001-18 e 0004-03.

O que precisa ficar provado é o critério de aceite: os dois documentos de linguagem
migraram do AmFlow desacoplados — todo link relativo dos documentos de `docs/plan/system/`
resolve em disco, e nenhum dos dois carrega instância do repositório de origem (core,
serviço, caminho de `docs/mvp/` ou o invariante `D10` do Worker).

A 0001-18 acrescenta os três pontos onde o gate de agent, fechado em `modelo-dev-units.md`,
reabriu: a seção *Modelos*, a decisão 18 e a pendência que citava a troca automática de
modelo por modo. Cada caso verifica por **conteúdo**, nunca por número de linha — a norma
muda a cada edição, e comparar linha transformaria o teste em falso alarme.

A 0004-03 divide `modelo-dev-units.md` em mecanismo (viaja no pacote) e
`registro-dev-units.md` (evidência, decisões e história deste projeto, não viaja). Os três
invariantes: o mecanismo não carrega marca de instância deste projeto, o registro existe e
cita o mecanismo, e o mecanismo nunca cita o registro de volta.
"""

from __future__ import annotations

import re
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import lib

_SYSTEM_DIR = lib.plan_root() / "system"

_LINK_RE = re.compile(r"\[[^\]]*\]\(([^)]+)\)")

# Instância do AmFlow que o `language-policy.md` e o `estudo-runtime-e-dependencias.md`
# não podem carregar — a norma cita como vinculantes só o que está aqui (§ *Contrato*
# e *Critério de aceite* da unidade 0001-08).
_MARCAS_AMFLOW = (
    "AmFlow",
    "docs/mvp",
    "native-only",
    "D10",
    "Worker",
    "builder",
    "backlog-worker",
    "smoke-tests.py",
    "hard-memory",
)


def _sem_blocos_de_codigo(texto: str) -> str:
    """Remove o miolo de blocos ```...``` — exemplo/template não é link a resolver."""
    fora = []
    dentro = False
    for linha in texto.splitlines():
        if linha.lstrip().startswith("```"):
            dentro = not dentro
            continue
        if not dentro:
            fora.append(linha)
    return "\n".join(fora)


def _corpo_normativo(texto: str) -> str:
    """Remove as notas de cabeçalho — blocos `>` antes da primeira seção `##`.

    É ali que vivem *Procedência* e *Como usar este documento*, e nomear o repositório de
    origem é o propósito delas: documento migrado que esconde de onde veio mente sobre a
    própria evidência. A exceção é **explícita e delimitada** justamente para não virar a
    exceção silenciosa que deixou a lista de marcas passar sem `"AmFlow"` (`L-23`).
    """
    linhas = []
    no_cabecalho = True
    for linha in texto.splitlines():
        if no_cabecalho and linha.startswith("## "):
            no_cabecalho = False
        if no_cabecalho and linha.lstrip().startswith(">"):
            continue
        linhas.append(linha)
    return "\n".join(linhas)


def _links_relativos(texto: str) -> list[str]:
    achados = []
    for alvo in _LINK_RE.findall(_sem_blocos_de_codigo(texto)):
        if alvo.startswith(("http://", "https://", "mailto:")):
            continue
        achados.append(alvo.split("#", 1)[0])
    return achados


class TestLinksDosDocumentosDeSystemResolvem(unittest.TestCase):
    def test_todo_link_relativo_resolve_em_disco(self):
        arquivos = sorted(_SYSTEM_DIR.glob("*.md"))
        self.assertTrue(arquivos, f"nenhum .md encontrado em {_SYSTEM_DIR}")
        for arquivo in arquivos:
            texto = arquivo.read_text(encoding="utf-8")
            for alvo in _links_relativos(texto):
                destino = (arquivo.parent / alvo).resolve()
                self.assertTrue(
                    destino.is_file(),
                    f"{arquivo.name}: link morto — {alvo!r} não resolve em {destino}",
                )


class TestDocumentosDeLinguagemSemInstanciaDoAmFlow(unittest.TestCase):
    def test_language_policy_existe_e_sem_instancia(self):
        self._sem_instancia(_SYSTEM_DIR / "language-policy.md")

    def test_estudo_runtime_existe_e_sem_instancia(self):
        self._sem_instancia(_SYSTEM_DIR / "estudo-runtime-e-dependencias.md")

    def test_language_policy_sem_secao_6_antiga(self):
        # "O que fica superado" — a lista de docs/mvp/ do AmFlow. Não tem objeto aqui.
        texto = (_SYSTEM_DIR / "language-policy.md").read_text(encoding="utf-8")
        self.assertNotIn("O que fica superado", texto)

    def _sem_instancia(self, arquivo: Path) -> None:
        self.assertTrue(arquivo.is_file(), f"documento não existe: {arquivo}")
        corpo = _corpo_normativo(arquivo.read_text(encoding="utf-8"))
        for marca in _MARCAS_AMFLOW:
            self.assertNotIn(marca, corpo, f"{arquivo.name}: instância do AmFlow — {marca!r}")


_NORMA = _SYSTEM_DIR / "modelo-dev-units.md"
_REGISTRO = _SYSTEM_DIR / "registro-dev-units.md"

# Marcas de instância deste projeto que o mecanismo não pode carregar — unidade 0004-03,
# *Critério de aceite*. Só as que a unidade nomeia: sem elas o documento que viaja no pacote
# não depende de nada que seja específico do `DecodeAndCode`.
_MARCAS_INSTANCIA_MECANISMO = ("0001-", "docs/mvp", "AmFlow", "METR", "DORA")


def _secao(texto: str, cabecalho: str) -> str:
    """Conteúdo entre `cabecalho` e o próximo heading ou separador `---` — ausente levanta."""
    padrao = re.compile(rf"(?ms)^{re.escape(cabecalho)}\s*$\n(.*?)(?=^#|^---\s*$|\Z)")
    m = padrao.search(texto)
    if not m:
        raise AssertionError(f"cabeçalho não encontrado: {cabecalho!r}")
    return m.group(1)


def _linha_da_decisao(texto: str, numero: int) -> str:
    """Linha da tabela de Decisões cujo primeiro campo é `numero` — ex. '| 18 | ... |'."""
    padrao = re.compile(rf"(?m)^\|\s*{numero}\s*\|.*\|\s*$")
    m = padrao.search(texto)
    if not m:
        raise AssertionError(f"linha da decisão {numero} não encontrada")
    return m.group(0)


class TestGateDeAgentReabriu(unittest.TestCase):
    """Unidade 0001-18 — as duas condições que a norma exigia para agent existir foram
    cumpridas, e a seção *Modelos*, a decisão 18 e a lista de pendentes registram isso.
    Cada caso verifica por conteúdo, nunca por número de linha (unidade 0001-18,
    *Critério de aceite*).

    A 0004-03 moveu `## Decisões` para o registro — a decisão 18 e `### Pendentes` são lidas
    de lá; `### Modelos` fica em `## Camada de execução`, que é mecanismo, e continua lida do
    `_NORMA`.
    """

    @classmethod
    def setUpClass(cls):
        cls.texto = _NORMA.read_text(encoding="utf-8")
        cls.texto_registro = _REGISTRO.read_text(encoding="utf-8")

    def test_frase_que_poe_agent_fora_de_escopo_nao_existe_mais(self):
        self.assertNotIn("Fora do escopo desta fase", self.texto)
        self.assertNotIn("Fora do escopo desta fase", self.texto_registro)

    def test_modelos_registra_as_duas_condicoes_cumpridas_com_data(self):
        secao = _secao(self.texto, "### Modelos")
        self.assertIn("2026-07-26", secao, "data em que a skill passou a existir")
        self.assertIn("2026-08-22", secao, "data em que o humano declarou o requisito")
        self.assertIn("papel e processo, nunca a norma", secao)

    def test_decisao_18_preserva_o_que_afirmou_e_ganha_linha_de_revisao(self):
        linha = _linha_da_decisao(self.texto_registro, 18)
        self.assertIn("automatizar exigiria agent", linha)
        self.assertIn("revisado em 2026-08-26", linha)

    def test_pendencia_de_troca_por_modo_sai_da_lista_com_destino_nomeado(self):
        secao = _secao(self.texto_registro, "### Pendentes")
        itens = re.findall(r"(?m)^\d+\.\s.*$", secao)
        self.assertEqual(
            len(itens), 1, f"esperado 1 item pendente, achou {len(itens)}: {itens}"
        )
        self.assertNotIn("Troca automática", "".join(itens))
        self.assertIn("model:", secao)
        self.assertIn("`19`", secao)
        self.assertIn("`20`", secao)


class TestNormaDividaEmMecanismoERegistro(unittest.TestCase):
    """Unidade 0004-03 — o operativo sai para `modelo-dev-units.md`; evidência, decisões e
    história deste projeto saem para `registro-dev-units.md`, citando o mecanismo. O
    mecanismo nunca cita o registro de volta — é o que permite ao primeiro viajar no pacote
    sem o segundo (*Critério de aceite* da unidade).
    """

    def test_mecanismo_sem_marca_de_instancia_deste_projeto(self):
        self.assertTrue(_NORMA.is_file(), f"mecanismo não existe: {_NORMA}")
        corpo = _corpo_normativo(_NORMA.read_text(encoding="utf-8"))
        for marca in _MARCAS_INSTANCIA_MECANISMO:
            self.assertNotIn(marca, corpo, f"{_NORMA.name}: instância deste projeto — {marca!r}")

    def test_registro_existe_com_frontmatter_e_cita_o_mecanismo(self):
        self.assertTrue(_REGISTRO.is_file(), f"registro não existe: {_REGISTRO}")
        texto = _REGISTRO.read_text(encoding="utf-8")
        linhas = texto.splitlines()
        self.assertTrue(linhas and linhas[0].strip() == "---", "registro sem frontmatter")
        self.assertIn(
            "modelo-dev-units.md", texto, "registro não cita o mecanismo"
        )

    def test_mecanismo_nunca_cita_o_registro(self):
        texto = _NORMA.read_text(encoding="utf-8")
        self.assertNotIn(
            "registro-dev-units", texto,
            "mecanismo cita o registro — dependeria de um arquivo que não viaja no pacote",
        )


if __name__ == "__main__":
    unittest.main()
