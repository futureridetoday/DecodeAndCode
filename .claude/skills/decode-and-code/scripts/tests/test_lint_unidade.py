#!/usr/bin/env python3
"""Testes do gate de entrada — unidade 0002-06.

O que dá valor à unidade é o par do critério de aceite: as duas instâncias
reais citadas em Arquivos aprovam sem ressalva, e uma unidade sintética sem
critério de aceite e com 15 passos devolve exatamente os dois problemas.
As demais dimensões (frontmatter, blocos, teto) são cobertas isoladamente
contra uma unidade sintética mínima que, sozinha, já aprova.
"""

from __future__ import annotations

import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import lib
import lint_unidade

UNIDADE_VALIDA = """\
---
name: exemplo
type: unit
project: AmFlow
description: unidade sintética para teste do lint
tags: []

core: builder
module: dev-units
block: ""
owner: builder
unit_id: 0009-01
unit_type: dev

state: spec
test: caminho/para/test_exemplo.py
verified_at: ""

author: Teste
created: 2026-07-25
status: draft
version: 1.0.0
updated: ""

scope: project
auto_load: false
dependencies: []
---

# 0009-01 — Unidade sintética

**Responsabilidade:** existir só para o teste do lint.

## Contrato

| Campo | Detalhe |
|---|---|
| Entrada | Nenhuma |

## Sequência

1. Primeiro passo
2. Segundo passo
3. Terceiro passo

## Arquivos

| Arquivo | Papel |
|---|---|
| `caminho/para/arquivo.py` | Criar |

## Dependências

Nenhuma.

## Normas aplicáveis

| Norma | Onde |
|---|---|
| Exemplo | em algum lugar |

## Critério de aceite

> O teste passa.

## Verificação

| Item | Valor |
|---|---|
| Teste | caminho/para/test_exemplo.py |
"""


class TestUnidadesReais(unittest.TestCase):
    """As duas instâncias reais citadas em Arquivos — devem aprovar sem ressalva."""

    def test_handler_auth_aprova(self):
        alvo = lib.plan_root() / "hub" / "0001-mcp" / "01-handler-auth.md"
        self.assertEqual(lint_unidade.lint(alvo), [])

    def test_lib_base_aprova(self):
        alvo = lib.plan_root() / "builder" / "0002-dev-units" / "01-lib-base.md"
        self.assertEqual(lint_unidade.lint(alvo), [])


class TestArquivoInexistente(unittest.TestCase):
    def test_levanta_file_not_found_error(self):
        with tempfile.TemporaryDirectory() as tmp:
            alvo = Path(tmp) / "nao-existe.md"
            with self.assertRaises(FileNotFoundError):
                lint_unidade.lint(alvo)


class TestGateDeEntrada(unittest.TestCase):
    """Contra uma unidade sintética mínima que aprova — cada teste quebra uma dimensão por vez."""

    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self._tmp.cleanup)
        self.dir = Path(self._tmp.name)

    def _escreve(self, texto: str, nome: str = "unidade.md") -> Path:
        alvo = self.dir / nome
        alvo.write_text(texto, encoding="utf-8")
        return alvo

    def test_unidade_valida_aprova(self):
        alvo = self._escreve(UNIDADE_VALIDA)
        self.assertEqual(lint_unidade.lint(alvo), [])

    def test_campo_obrigatorio_ausente(self):
        texto = UNIDADE_VALIDA.replace("module: dev-units\n", "")
        alvo = self._escreve(texto)
        problemas = lint_unidade.lint(alvo)
        self.assertTrue(any("module" in p for p in problemas), problemas)

    def test_frontmatter_ausente_por_completo(self):
        alvo = self._escreve("# Sem frontmatter\n\nConteúdo qualquer.\n")
        problemas = lint_unidade.lint(alvo)
        self.assertTrue(any("frontmatter" in p for p in problemas), problemas)

    def test_unit_id_fora_do_formato(self):
        texto = UNIDADE_VALIDA.replace("unit_id: 0009-01", "unit_id: abc")
        alvo = self._escreve(texto)
        problemas = lint_unidade.lint(alvo)
        self.assertTrue(any("unit_id" in p for p in problemas), problemas)

    def test_unit_type_invalido(self):
        texto = UNIDADE_VALIDA.replace("unit_type: dev", "unit_type: feature")
        alvo = self._escreve(texto)
        problemas = lint_unidade.lint(alvo)
        self.assertTrue(any("unit_type" in p for p in problemas), problemas)

    def test_bloco_responsabilidade_ausente(self):
        texto = UNIDADE_VALIDA.replace(
            "**Responsabilidade:** existir só para o teste do lint.\n\n", ""
        )
        alvo = self._escreve(texto)
        problemas = lint_unidade.lint(alvo)
        self.assertTrue(any("Responsabilidade" in p for p in problemas), problemas)

    def test_cada_bloco_de_heading_ausente_e_reportado(self):
        for bloco in lint_unidade.BLOCOS_CORPO:
            with self.subTest(bloco=bloco):
                texto = UNIDADE_VALIDA.replace(f"## {bloco}\n\n", "", 1)
                alvo = self._escreve(texto, nome=f"sem-{bloco}.md")
                problemas = lint_unidade.lint(alvo)
                self.assertTrue(any(bloco in p for p in problemas), (bloco, problemas))

    def test_sequencia_vazia(self):
        texto = UNIDADE_VALIDA.replace(
            "1. Primeiro passo\n2. Segundo passo\n3. Terceiro passo\n", ""
        )
        alvo = self._escreve(texto)
        problemas = lint_unidade.lint(alvo)
        self.assertTrue(any("Sequência" in p for p in problemas), problemas)

    def test_sequencia_acima_do_teto(self):
        passos = "\n".join(f"{i}. passo {i}" for i in range(1, 16))
        texto = UNIDADE_VALIDA.replace(
            "1. Primeiro passo\n2. Segundo passo\n3. Terceiro passo", passos
        )
        alvo = self._escreve(texto)
        problemas = lint_unidade.lint(alvo)
        self.assertTrue(any("acima do teto" in p for p in problemas), problemas)

    def test_criterio_de_aceite_vazio(self):
        texto = UNIDADE_VALIDA.replace(
            "## Critério de aceite\n\n> O teste passa.\n", "## Critério de aceite\n\n"
        )
        alvo = self._escreve(texto)
        problemas = lint_unidade.lint(alvo)
        self.assertTrue(any("Critério de aceite" in p for p in problemas), problemas)

    def test_arquivos_sem_caminho_concreto(self):
        texto = UNIDADE_VALIDA.replace(
            "| `caminho/para/arquivo.py` | Criar |", "| `arquivo.py` | Criar |"
        )
        alvo = self._escreve(texto)
        problemas = lint_unidade.lint(alvo)
        self.assertTrue(any("Arquivos" in p for p in problemas), problemas)

    def test_sem_criterio_e_muitos_passos_devolve_exatamente_dois_problemas(self):
        passos = "\n".join(f"{i}. passo {i}" for i in range(1, 16))
        texto = UNIDADE_VALIDA.replace(
            "1. Primeiro passo\n2. Segundo passo\n3. Terceiro passo", passos
        ).replace(
            "## Critério de aceite\n\n> O teste passa.\n", "## Critério de aceite\n\n"
        )
        alvo = self._escreve(texto)
        problemas = lint_unidade.lint(alvo)
        self.assertEqual(len(problemas), 2, problemas)

    def test_devolve_todos_os_problemas_de_uma_vez(self):
        texto = (
            UNIDADE_VALIDA.replace("module: dev-units\n", "")
            .replace("unit_type: dev", "unit_type: feature")
            .replace(
                "| `caminho/para/arquivo.py` | Criar |", "| `arquivo.py` | Criar |"
            )
        )
        alvo = self._escreve(texto)
        problemas = lint_unidade.lint(alvo)
        self.assertTrue(any("module" in p for p in problemas), problemas)
        self.assertTrue(any("unit_type" in p for p in problemas), problemas)
        self.assertTrue(any("Arquivos" in p for p in problemas), problemas)
        self.assertEqual(len(problemas), 3, problemas)


if __name__ == "__main__":
    unittest.main()
