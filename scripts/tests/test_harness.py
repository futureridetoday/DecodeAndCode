#!/usr/bin/env python3
"""Sentinela do harness de teste Python.

Prova três coisas sobre a infra, não sobre regra de negócio:
o discover encontra os testes, o interpretador é o declarado na norma, e uma
falha real é reportada como falha.

Ver docs/plan/system/language-policy.md §4.
"""

import re
import subprocess
import sys
import unittest
from pathlib import Path

VERSAO_ALVO = (3, 10)
REPO_ROOT = Path(__file__).resolve().parent.parent.parent


class TestHarness(unittest.TestCase):
    def test_discover_encontra_este_arquivo(self):
        # Se este teste roda, o discover funcionou. Trivial por desenho.
        self.assertTrue(True)

    def test_interpretador_e_a_versao_alvo(self):
        self.assertEqual(
            sys.version_info[:2],
            VERSAO_ALVO,
            f"harness rodou em {sys.version_info[0]}.{sys.version_info[1]}; "
            f"a norma exige {VERSAO_ALVO[0]}.{VERSAO_ALVO[1]} — a versão do Cowork",
        )

    def test_script_se_auto_localiza(self):
        # CLAUDE_PLUGIN_ROOT veio vazia nos dois ambientes medidos; todo script
        # precisa achar a própria raiz sem variável de ambiente.
        self.assertTrue((REPO_ROOT / ".claude").is_dir())

    def test_falha_real_e_reportada(self):
        # Roda um teste que falha de propósito, em subprocesso, e confirma que o
        # unittest devolve exit code != 0. Sem isso, um harness quebrado passaria
        # silenciosamente e todo verde seria falso.
        codigo = (
            "import unittest\n"
            "class T(unittest.TestCase):\n"
            "    def test_falha(self):\n"
            "        self.fail('falha proposital')\n"
            "unittest.main()\n"
        )
        resultado = subprocess.run(
            [sys.executable, "-c", codigo],
            capture_output=True,
            text=True,
        )
        self.assertNotEqual(
            resultado.returncode, 0, "unittest não sinalizou falha via exit code"
        )

    def test_rodape_soma_os_testes_de_todos_os_alvos(self):
        # O rodapé contava diretórios e nunca escrevia o total: cada alvo imprime
        # seu próprio `Ran N tests` e a soma ficava com quem lia a saída. Rendeu
        # subcontagem em catorze entregas seguidas — a última reportou 426 onde
        # a suíte tinha 442. Executa o runner de verdade contra dois alvos, como
        # exige `.claude/rules/scripts.md` (*Comando externo*); mock provaria o
        # parsing e não a aritmética que o script agora faz.
        alvos = [
            ".claude/skills/decode-and-code/scripts/tests/test_move_md.py",
            ".claude/skills/decode-and-code/scripts/tests/test_nomenclatura.py",
        ]
        resultado = subprocess.run(
            [str(REPO_ROOT / "scripts" / "test-python.sh"), *alvos],
            capture_output=True,
            text=True,
            cwd=REPO_ROOT,
        )
        self.assertEqual(
            resultado.returncode, 0, resultado.stdout + resultado.stderr
        )

        parciais = [
            int(n) for n in re.findall(r"^Ran (\d+) test", resultado.stdout, re.M)
        ]
        self.assertEqual(
            len(parciais), len(alvos), f"esperava um `Ran` por alvo:\n{resultado.stdout}"
        )

        rodape = re.search(
            r"^OK — (\d+) teste\(s\) em (\d+) diretório\(s\)", resultado.stdout, re.M
        )
        self.assertIsNotNone(rodape, f"rodapé não encontrado:\n{resultado.stdout}")
        self.assertEqual(int(rodape.group(1)), sum(parciais))
        self.assertEqual(int(rodape.group(2)), len(alvos))


if __name__ == "__main__":
    unittest.main()
