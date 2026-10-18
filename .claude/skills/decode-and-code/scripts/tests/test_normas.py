#!/usr/bin/env python3
"""Testes de `normas.resolver` — `L-08` do plano `apply-plugin-review`.

`TestFormasDeLinha` isola cada forma da coluna *Onde* (e cada motivo de não resolver) contra a mesma
unidade e o mesmo documento sintéticos, em `tempfile`. `TestContraUnidadeReal` é o caso contra a
instância: a unidade `04` do plano `0001`, com os números que a medição deu — sem ele o teste prova
só o mecanismo, nunca que as formas que as unidades reais usam resolvem (`L-31`).

O documento sintético cobre o que o resolvedor decide: títulos de nível 2, 3 e 4, um título com
sufixo, outro com numeração (`3. `), um bloco de código com `##` de exemplo, e um frontmatter com
comentário `# about` — que, tomado por título, seria seção.
"""

from __future__ import annotations

import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import fixtures
import lib
import normas

_DOCUMENTO = """\
---
# about
name: regras
---

# Regras

## Alfa

Texto de alfa.

### Alfa filho

Texto do filho.

#### Neto de alfa

Texto do neto.

## Beta — com sufixo

Texto de beta.

```
## Cabeçalho de exemplo
```

Resto de beta.

## 3. Gama numerada

Texto de gama.
"""

_TRECHO_ALFA = """\
## Alfa

Texto de alfa.

### Alfa filho

Texto do filho.

#### Neto de alfa

Texto do neto."""

_LINHA_PADRAO = "| Norma | Onde |\n|---|---|"
_LINK = "[`regras.md`](../system/regras.md)"


class _SinteticoCase(unittest.TestCase):
    """Uma unidade em `plano/` e um documento em `system/`, ambos descartáveis."""

    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self._tmp.cleanup)
        self.raiz = Path(self._tmp.name).resolve()
        (self.raiz / "system").mkdir()
        self.documento = self.raiz / "system" / "regras.md"
        self.documento.write_text(_DOCUMENTO, encoding="utf-8")

    def unidade(self, *linhas: str) -> Path:
        """Unidade válida cuja tabela de normas tem só `linhas` (uma célula por linha, já com `|`)."""
        texto = fixtures.UNIDADE_VALIDA
        self.assertIn(_LINHA_PADRAO, texto)
        alvo = self.raiz / "plano" / "01-sintetica.md"
        alvo.parent.mkdir(exist_ok=True)
        alvo.write_text(texto.replace(_LINHA_PADRAO, "\n".join((_LINHA_PADRAO, *linhas))), encoding="utf-8")
        return alvo

    def resolver(self, *linhas: str):
        return normas.resolver(self.unidade(*linhas))

    def um_motivo(self, *linhas: str) -> str:
        """Resolve `linhas` e exige que a última seja a única não resolvida; devolve o motivo."""
        resolvidas, nao_resolvidas = self.resolver(*linhas)
        self.assertEqual(len(nao_resolvidas), 1, nao_resolvidas)
        self.assertEqual(nao_resolvidas[0].linha, linhas[-1].strip())
        return nao_resolvidas[0].motivo


class TestFormasDeLinha(_SinteticoCase):
    def test_link_com_secao_resolve_do_titulo_ate_o_proximo_de_nivel_igual(self):
        resolvidas, nao_resolvidas = self.resolver(f"| Alfa | {_LINK}, seção *Alfa* |")
        self.assertEqual(nao_resolvidas, [])
        self.assertEqual(resolvidas, [normas.Entrada(self.documento, "Alfa", _TRECHO_ALFA)])

    def test_titulo_de_nivel_3_leva_o_neto_e_para_no_nivel_menor(self):
        (entrada,), _ = self.resolver(f"| Filho | {_LINK}, seção *Alfa filho* |")
        self.assertEqual(entrada.secao, "Alfa filho")
        self.assertEqual(
            entrada.trecho,
            "### Alfa filho\n\nTexto do filho.\n\n#### Neto de alfa\n\nTexto do neto.",
        )

    def test_titulo_de_nivel_4_vai_ate_o_proximo_de_nivel_menor(self):
        (entrada,), _ = self.resolver(f"| Neto | {_LINK}, seção *Neto de alfa* |")
        self.assertEqual(entrada.trecho, "#### Neto de alfa\n\nTexto do neto.")

    def test_secao_de_mesmo_nome_usa_a_primeira_coluna(self):
        (entrada,), nao_resolvidas = self.resolver(f"| Alfa filho | {_LINK}, seção de mesmo nome |")
        self.assertEqual(nao_resolvidas, [])
        self.assertEqual(entrada.secao, "Alfa filho")

    def test_secao_de_mesmo_nome_ignora_a_marcacao_da_primeira_coluna(self):
        (entrada,), _ = self.resolver(f"| *Alfa filho* | {_LINK}, seção de mesmo nome |")
        self.assertEqual(entrada.secao, "Alfa filho")

    def test_mesma_secao_repete_arquivo_e_secao_da_linha_anterior(self):
        resolvidas, nao_resolvidas = self.resolver(
            f"| Alfa | {_LINK}, seção *Alfa* |",
            "| Outra razão | mesma seção — e um comentário |",
        )
        self.assertEqual(nao_resolvidas, [])
        self.assertEqual(len(resolvidas), 2)
        self.assertEqual(resolvidas[0], resolvidas[1])

    def test_mesma_secao_encadeia(self):
        resolvidas, _ = self.resolver(
            f"| Alfa | {_LINK}, seção *Alfa* |",
            "| B | mesma seção |",
            "| C | mesma seção |",
        )
        self.assertEqual(len(resolvidas), 3)
        self.assertEqual(resolvidas[0], resolvidas[2])

    def test_secao_sem_a_palavra_secao_tambem_resolve(self):
        (entrada,), _ = self.resolver(f"| Alfa | {_LINK}, *Alfa* |")
        self.assertEqual(entrada.trecho, _TRECHO_ALFA)

    def test_o_nome_e_prefixo_do_titulo(self):
        (entrada,), _ = self.resolver(f"| Beta | {_LINK}, seção *Beta* |")
        self.assertEqual(entrada.secao, "Beta — com sufixo")

    def test_a_numeracao_do_titulo_nao_conta(self):
        (entrada,), _ = self.resolver(f"| Gama | {_LINK}, seção *Gama* |")
        self.assertEqual(entrada.secao, "3. Gama numerada")
        self.assertEqual(entrada.trecho, "## 3. Gama numerada\n\nTexto de gama.")

    def test_titulo_dentro_de_cerca_de_codigo_nao_encerra_a_secao(self):
        (entrada,), _ = self.resolver(f"| Beta | {_LINK}, seção *Beta* |")
        self.assertIn("## Cabeçalho de exemplo", entrada.trecho)
        self.assertTrue(entrada.trecho.endswith("Resto de beta."), entrada.trecho)

    def test_titulo_dentro_de_cerca_de_codigo_nao_e_achado(self):
        self.assertEqual(
            self.um_motivo(f"| X | {_LINK}, seção *Cabeçalho de exemplo* |"),
            "seção não encontrada: Cabeçalho de exemplo",
        )

    def test_frontmatter_nao_tem_titulo(self):
        self.assertEqual(self.um_motivo(f"| X | {_LINK}, seção *about* |"), "seção não encontrada: about")

    def test_arquivo_ausente(self):
        self.assertEqual(
            self.um_motivo("| X | [`some.md`](../system/some.md), seção *Alfa* |"), "arquivo ausente"
        )

    def test_secao_inexistente(self):
        self.assertEqual(
            self.um_motivo(f"| X | {_LINK}, seção *Omega* |"), "seção não encontrada: Omega"
        )

    def test_linha_sem_link(self):
        self.assertEqual(
            self.um_motivo("| Simplicidade primeiro | `.claude/CLAUDE.md`, invariante 2 |"),
            "sem link para o arquivo",
        )

    def test_link_sem_secao(self):
        self.assertEqual(self.um_motivo(f"| X | {_LINK} |"), "link sem seção reconhecida")

    def test_mesma_secao_na_primeira_linha_nao_tem_anterior(self):
        self.assertEqual(
            self.um_motivo("| X | mesma seção |"), "'mesma seção' sem linha anterior resolvida"
        )

    def test_mesma_secao_depois_de_linha_nao_resolvida_nao_pula_para_a_resolvida_antes_dela(self):
        resolvidas, nao_resolvidas = self.resolver(
            f"| Alfa | {_LINK}, seção *Alfa* |",
            f"| X | {_LINK}, seção *Omega* |",
            "| Y | mesma seção |",
        )
        self.assertEqual(len(resolvidas), 1)
        self.assertEqual(
            [m for _, m in nao_resolvidas],
            ["seção não encontrada: Omega", "'mesma seção' sem linha anterior resolvida"],
        )

    def test_ordem_da_tabela_e_cabecalho_e_separador_nao_contam(self):
        resolvidas, nao_resolvidas = self.resolver(
            f"| Beta | {_LINK}, seção *Beta* |",
            "| Sem link | texto |",
            f"| Alfa | {_LINK}, seção *Alfa* |",
        )
        self.assertEqual([e.secao for e in resolvidas], ["Beta — com sufixo", "Alfa"])
        self.assertEqual([n.linha for n in nao_resolvidas], ["| Sem link | texto |"])

    def test_caminho_do_link_e_relativo_a_unidade_e_nao_ao_cwd(self):
        (entrada,), _ = self.resolver(f"| Alfa | {_LINK}, seção *Alfa* |")
        self.assertEqual(entrada.arquivo, self.documento)


class TestErros(_SinteticoCase):
    def test_unidade_inexistente_levanta_file_not_found(self):
        with self.assertRaises(FileNotFoundError):
            normas.resolver(self.raiz / "nao-existe.md")

    def test_unidade_sem_a_secao_levanta_value_error(self):
        unidade = self.unidade(f"| Alfa | {_LINK}, seção *Alfa* |")
        unidade.write_text(
            unidade.read_text(encoding="utf-8").replace("## Normas aplicáveis", "## Outra coisa"),
            encoding="utf-8",
        )
        with self.assertRaisesRegex(ValueError, "Normas aplicáveis"):
            normas.resolver(unidade)

    def test_tabela_so_com_cabecalho_nao_resolve_nada_e_nao_levanta(self):
        unidade = self.unidade()
        self.assertEqual(normas.resolver(unidade), ([], []))


class TestContraUnidadeReal(unittest.TestCase):
    """A `04` do plano `0001`: as três formas numa tabela de seis linhas — e o que sobra."""

    UNIDADE = lib.plan_root() / "model" / "0001-decode-and-code-foundation" / "04-ddl-guardrail-hook.md"

    def test_resolve_cinco_de_seis_e_a_sexta_e_a_do_claude_md(self):
        resolvidas, nao_resolvidas = normas.resolver(self.UNIDADE)
        self.assertEqual(len(resolvidas), 5)
        self.assertEqual(len(nao_resolvidas), 1)
        self.assertEqual(nao_resolvidas[0].motivo, "sem link para o arquivo")
        self.assertIn("`.claude/CLAUDE.md`, invariante 2", nao_resolvidas[0].linha)

    def test_as_secoes_achadas_sao_as_citadas_na_ordem(self):
        resolvidas, _ = normas.resolver(self.UNIDADE)
        esperado = (
            "O pipeline completo",
            "O pipeline completo",  # a linha "mesma seção"
            "Restrições conhecidas",
            "Decisões",
            "Guardrail fundador",
        )
        for entrada, comeco in zip(resolvidas, esperado, strict=True):
            with self.subTest(secao=comeco):
                self.assertTrue(entrada.secao.startswith(comeco), entrada.secao)
        self.assertEqual(resolvidas[0], resolvidas[1])

    def test_o_trecho_traz_o_conteudo_que_a_unidade_precisa(self):
        resolvidas, _ = normas.resolver(self.UNIDADE)
        decisoes = resolvidas[3]
        self.assertTrue(decisoes.trecho.startswith("## Decisões"))
        self.assertIn("| D-07 |", decisoes.trecho)
        guardrail = resolvidas[4]
        self.assertEqual(guardrail.arquivo, lib.plan_root() / "system" / "modelo-dev-units.md")
        self.assertTrue(guardrail.trecho.startswith("#### Guardrail fundador"))


if __name__ == "__main__":
    unittest.main()
