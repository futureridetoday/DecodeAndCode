#!/usr/bin/env python3
"""Testes de `reconciliar.comparar/relatorio` — unidade 0001-17.

As duas árvores (`origem`, `copia`) são sintéticas, uma em cada `tempfile.TemporaryDirectory()` —
o mecanismo não pede fonte real para provar os quatro veredictos. `TestNaoEscreve` prova o
contrato de só-leitura tirando o SHA-256 da árvore da cópia inteira antes e depois de rodar as
duas funções, no mesmo espírito do par sintético/real de `test_empacotamento.py`: aqui não há
"árvore real" a construir, então a garantia vem de hash agregado, não de fixture dupla.
"""

from __future__ import annotations

import hashlib
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import reconciliar


def _sha_arvore(raiz: Path) -> str:
    """SHA-256 agregado de toda `raiz` — nome relativo e conteúdo de cada arquivo, em ordem."""
    hasher = hashlib.sha256()
    for caminho in sorted(raiz.rglob("*")):
        if caminho.is_file():
            hasher.update(caminho.relative_to(raiz).as_posix().encode("utf-8"))
            hasher.update(caminho.read_bytes())
    return hasher.hexdigest()


class _BaseDuasArvores(unittest.TestCase):
    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self._tmp.cleanup)
        raiz = Path(self._tmp.name).resolve()
        self.origem = raiz / "origem"
        self.copia = raiz / "copia"
        self.origem.mkdir()
        self.copia.mkdir()


class TestComparar(_BaseDuasArvores):
    def test_quatro_veredictos(self):
        (self.origem / "identico.py").write_text("igual\n", encoding="utf-8")
        (self.copia / "identico.py").write_text("igual\n", encoding="utf-8")

        (self.origem / "mudou.py").write_text("versão da origem\n", encoding="utf-8")
        (self.copia / "mudou.py").write_text("versão da cópia\n", encoding="utf-8")

        (self.origem / "novo.py").write_text("só existe na origem\n", encoding="utf-8")
        (self.copia / "fork.py").write_text("só existe na cópia\n", encoding="utf-8")

        resultado = {item["componente"]: item["veredito"] for item in reconciliar.comparar(self.origem, self.copia)}

        self.assertEqual(resultado["identico.py"], "idêntico")
        self.assertEqual(resultado["mudou.py"], "divergente")
        self.assertEqual(resultado["novo.py"], "só na origem")
        self.assertEqual(resultado["fork.py"], "só na cópia")

    def test_ignora_pycache(self):
        (self.origem / "modulo.py").write_text("conteúdo\n", encoding="utf-8")
        (self.copia / "modulo.py").write_text("conteúdo\n", encoding="utf-8")
        sem_pycache = reconciliar.comparar(self.origem, self.copia)

        pycache = self.origem / "__pycache__"
        pycache.mkdir()
        (pycache / "modulo.cpython-310.pyc").write_text("lixo de bytecode\n", encoding="utf-8")

        com_pycache = reconciliar.comparar(self.origem, self.copia)
        self.assertEqual(com_pycache, sem_pycache)

    def test_diretorio_ausente_levanta(self):
        with self.assertRaises(FileNotFoundError):
            reconciliar.comparar(self.origem / "nao-existe", self.copia)


def _skill_md(dir_skill: Path, versao: str) -> None:
    (dir_skill / "SKILL.md").write_text(
        f"---\nname: exemplo\nversion: {versao}\n---\n\nCorpo.\n", encoding="utf-8"
    )


class TestRelatorio(_BaseDuasArvores):
    def test_versao_e_contexto_nunca_veredito(self):
        _skill_md(self.origem, "1.0.0")
        _skill_md(self.copia, "1.0.0")
        (self.origem / "script.py").write_text("origem\n", encoding="utf-8")
        (self.copia / "script.py").write_text("cópia\n", encoding="utf-8")

        linhas = reconciliar.relatorio(self.origem, self.copia)
        texto = "\n".join(linhas)

        self.assertIn("1.0.0", texto)
        self.assertTrue(any("divergente" in linha for linha in linhas))

    def test_copia_sem_skill_md_nao_levanta(self):
        _skill_md(self.origem, "1.0.0")
        (self.origem / "script.py").write_text("origem\n", encoding="utf-8")
        (self.copia / "script.py").write_text("origem\n", encoding="utf-8")

        linhas = reconciliar.relatorio(self.origem, self.copia)
        self.assertTrue(any("não declarada" in linha for linha in linhas))


class TestNaoEscreve(_BaseDuasArvores):
    def test_nenhuma_das_duas_funcoes_escreve(self):
        (self.origem / "script.py").write_text("origem\n", encoding="utf-8")
        (self.copia / "script.py").write_text("cópia\n", encoding="utf-8")
        _skill_md(self.copia, "1.0.0")

        antes = _sha_arvore(self.copia)
        reconciliar.comparar(self.origem, self.copia)
        reconciliar.relatorio(self.origem, self.copia)
        depois = _sha_arvore(self.copia)

        self.assertEqual(antes, depois)


if __name__ == "__main__":
    unittest.main()
