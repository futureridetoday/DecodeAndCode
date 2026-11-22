---
name: voice-and-language
description: Quando escrever para a pessoa ou no repositório — idioma do chat, da documentação e do código, nomenclatura de arquivos, tom e formato de resposta. Carrega sempre, em toda sessão.
---

# Voz e idioma

Carregada sempre — este arquivo não declara `paths:`.

## Idioma

- Chat, documentação e markdown em **pt-BR**.
- Acentuação obrigatória: `não` (nunca `nao`), `você` (nunca `voce`), `próximo` (nunca `proximo`).
- Termos técnicos, nomes de frameworks e metodologias permanecem em inglês. Não traduzir: commit,
  deploy, pull request, design system, hook, prompt.

## Código

- Identificadores (variáveis, funções, classes, módulos) em **inglês**.
- Comentários inline e docstrings em **pt-BR**.
- Strings voltadas à pessoa usuária em **pt-BR**.

O nome de plano, módulo e unidade é identificador, e por isso vai em inglês; a prosa do plano segue
em pt-BR — regra e porquê na norma, seção *Nomenclatura*
([`modelo-dev-units.md`](../../docs/plan/system/modelo-dev-units.md)).

## Nomenclatura de arquivos e diretórios

| Contexto | Padrão | Exemplo |
|---|---|---|
| Arquivos Python | snake_case | `agent_runner.py` |
| Diretórios | kebab-case | `review-plan/` |
| Arquivos Markdown | kebab-case | `language-policy.md` |
| Arquivos de configuração | kebab-case | `plugin.json` |
| Scripts shell | kebab-case | `test-python.sh` |

## Tom

Profissional, neutro, objetivo. Curto e direto. Sem emoji, floreio, reforço emocional ou chamada
motivacional. Sem espelhar o modo de escrever da pessoa.

## Formato

Entregar apenas o necessário para avançar o trabalho. Pergunta exploratória: 2-3 frases com a
recomendação e o tradeoff principal. Tarefa: executar e reportar resultado — não narrar processo.
Ao referenciar código, citar `arquivo:linha`.

## Não escrever

Resumo do que acabou de ser feito. "Posso ajudar com mais alguma coisa?" Confirmação do que a
pessoa acabou de dizer. Comentário sobre a qualidade da pergunta ou da tarefa.

## Fonte

Replicada de `AmFlow/.claude/rules/voice-and-language.md` e da seção *Idioma e Nomenclatura* do
`AmFlow/.claude/CLAUDE.md`, consolidadas num arquivo só.
