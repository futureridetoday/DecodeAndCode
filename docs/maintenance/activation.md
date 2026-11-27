---
# about
name: activation
type: doc
project: ""
description: Como se valida que guidelines e guardrails do projeto carregam — o controle de três estados, a auditoria da árvore de rules e as operações que escrevem a camada
tags: [manutencao, ativacao, rules]

# history
author: Bortoli
created: 2026-11-27
status: stable
version: 1.0.0
updated: ""

# system
scope: project
source: ""
auto_load: false
checksum: ""
dependencies: [codex-guide]
---

# Validar a ativação

Documentação de manutenção: serve a quem mantém o plugin, não ao método. O que princípio, guideline e
guardrail são está no codex, seções *Princípio*, *Guideline* e *Guardrail*.

Dois atos permanecem humanos, e nenhum script os substitui: **abrir uma sessão nova**, e **tocar um
arquivo do escopo** de uma guideline. O que deixa de ser julgamento é o que se conclui depois de
feito isso — vira gate onde é estrutural, e relatório onde só a sessão real prova algo.

`rules.auditar_arvore()` roda sem argumento e devolve `[]` quando a árvore de `.claude/rules/` e
`.claude/rules-off/` está sã — recusa isoladamente um `.md` em subdiretório de `rules/` (o matcher recursa, e o arquivo continua carregando), uma rule malformada em `rules/`, e
uma guideline quebrada em `rules-off/`, porque ela volta a ser ligada um dia.

`activation_notice.relatorio(caminho_log, sessao)` lê o log de ativação —
`.claude/log/eventos.jsonl` do projeto, onde o hook `InstructionsLoaded` grava com o `session_id`
([`skills-and-scripts.md`](skills-and-scripts.md), *Log de uso*), filtrado pela `sessao` quando dada — e devolve uma linha por instrução carregada,
com caminho, motivo e veredito:

```
python3 -c "
import sys; sys.path.insert(0, '<scripts-da-skill>')
import activation_notice
for linha in activation_notice.relatorio('.claude/log/eventos.jsonl', '<session_id>'):
    print(linha)
"
```

`<scripts-da-skill>` é o `scripts/` da pasta compartilhada: `.claude/skills/decode-and-code/scripts`
no checkout que a contém; no plugin instalado, o caminho que as skills citam como
`${CLAUDE_SKILL_DIR}/../decode-and-code/scripts`. A variável só é substituída no corpo da skill —
num arquivo lido, como este, ela chega literal.

**O controle de três estados**, e que qualquer projeto que instalar o plugin
repete para validar a própria camada: guideline **ligada** produz entrada no log; movida para
**subdiretório** de `rules/` também produz entrada — é o defeito; movida para o diretório **irmão**
`rules-off/` não produz entrada nenhuma.

Os resultados de cada medição não são recopiados aqui — vivem em *Validação de ponta a ponta*, no
plano que instanciou este mecanismo pela primeira vez.

**Ligar e desligar uma guideline é operação, não edição de arquivo.** `desligar` move o arquivo para
`.claude/rules-off/` — diretório **irmão**, fora do que o Claude Code carrega —, e `ligar` devolve, sempre por
`Path.rename`, nunca reescrita; o `registry.json` que acompanha é projeção, nunca fonte, e reporta
divergência entre o que ele registra e o estado real do disco em vez de escolher um dos dois em
silêncio.

**Escrever guideline e guardrail também é operação.** `dc.py criar-guideline` grava a guideline só
depois de ela passar em `lint_guideline` e a registra; `paths` sai no subconjunto em que o lint e o
Claude Code concordam, e caminho que ainda não existe leva `paths_pending: true`, que dispensa só o
casamento no disco. `dc.py adicionar-guardrail` acrescenta a regra só depois de ela, avaliada
sozinha, negar o caso proibido e liberar o permitido; `dc.py lint-guardrails` valida o arquivo
inteiro. Os guias [`create-guideline.md`](../../recursos/create-guideline.md) e
[`create-guardrail.md`](../../recursos/create-guardrail.md) dão o passo a passo.
