# Proposal — Skill `/refactor-arch` para Claude Code

## Resumo Executivo

Este documento descreve a proposta de implementação da Skill `/refactor-arch`, uma solução automatizada de auditoria e refatoração arquitetural baseada em Claude Code. A skill analisa codebases existentes, detecta anti-patterns classificados por severidade, gera relatórios estruturados e refatora o código para o padrão MVC — de forma agnóstica à tecnologia utilizada.

---

## Problema

Projetos de software acumulam dívida técnica ao longo do tempo. Os sintomas mais comuns são:

- **God Classes** contendo banco de dados, lógica de negócio e roteamento em um único arquivo
- **Credenciais hardcoded** no código-fonte expondo dados sensíveis
- **SQL Injection** por uso de concatenação de strings em queries
- **Lógica de negócio dentro de rotas**, impossibilitando testes unitários
- **Ausência de validação** nas entradas das APIs
- **Error handling duplicado** em cada rota em vez de centralizado

Auditar e corrigir esses problemas manualmente é lento, sujeito a erros e dependente do conhecimento individual de cada desenvolvedor.

---

## Solução Proposta

Uma **Custom Skill para Claude Code** que automatiza o processo completo de auditoria e refatoração em 3 fases sequenciais, executada com um único comando:

```bash
claude "/refactor-arch"
```

### Fase 1 — Análise do Projeto
Detecta automaticamente linguagem, framework, dependências, domínio de negócio e arquitetura atual. Produz um resumo estruturado do estado do projeto.

### Fase 2 — Auditoria de Arquitetura
Cruza o código contra um catálogo de anti-patterns com sinais de detecção precisos. Gera relatório com arquivo e linha exatos para cada problema. **Pausa e solicita confirmação do desenvolvedor antes de modificar qualquer arquivo.**

### Fase 3 — Refatoração para MVC
Reestrutura o projeto para o padrão Model-View-Controller, eliminando todos os anti-patterns identificados. Valida que a aplicação continua funcionando após as mudanças.

---

## Escopo de Entrega

### Projetos-Alvo

| Projeto | Linguagem | Framework | Domínio |
|---------|-----------|-----------|---------|
| `code-smells-project` | Python | Flask | E-commerce API |
| `ecommerce-api-legacy` | Node.js | Express | LMS com checkout |
| `task-manager-api` | Python | Flask | Task Manager |

### Arquivos da Skill

A skill é composta por 6 arquivos Markdown localizados em `.claude/skills/refactor-arch/`:

| Arquivo | Responsabilidade |
|---------|-----------------|
| `SKILL.md` | Prompt principal — instrui o agente nas 3 fases |
| `01-project-analysis.md` | Heurísticas de detecção de stack e arquitetura |
| `02-antipatterns-catalog.md` | Catálogo de ≥8 anti-patterns com sinais de detecção |
| `03-report-template.md` | Template padronizado do relatório de auditoria |
| `04-mvc-guidelines.md` | Regras do padrão MVC alvo por linguagem |
| `05-refactoring-playbook.md` | ≥8 padrões de transformação com exemplos antes/depois |

---

## Catálogo de Anti-Patterns Cobertos

### CRITICAL
- **God Class / God File** — arquivo único com múltiplos domínios e responsabilidades
- **Hardcoded Credentials** — segredos expostos no código-fonte
- **SQL Injection** — queries construídas com concatenação de strings

### HIGH
- **Lógica de Negócio no Controller/Route** — handlers de rota com >30 linhas de lógica
- **Forte Acoplamento** — ausência de injeção de dependência
- **Estado Global Mutável** — variáveis globais modificadas entre requests

### MEDIUM
- **Query N+1** — queries SQL dentro de loops
- **Validação Ausente nas Rotas** — entradas não validadas
- **Error Handling Duplicado** — try/catch repetido em cada rota
- **APIs Deprecated** — uso de APIs obsoletas do Python/Flask e Node.js/Express

### LOW
- **Magic Numbers** — literais numéricos sem constantes nomeadas
- **Nomenclatura Ruim** — nomes genéricos ou mistura de idiomas
- **Código Morto** — blocos comentados ou funções não utilizadas

---

## Agnóstica de Tecnologia

A skill deve funcionar sem modificações nos 3 projetos (2 Python, 1 Node.js). Isso é garantido por:

1. `SKILL.md` usa termos genéricos — "arquivo-fonte", "entry point", "rota" — sem citar linguagem
2. `01-project-analysis.md` tem heurísticas de detecção para ambas as linguagens
3. `02-antipatterns-catalog.md` tem sinais de detecção separados para Python e JavaScript
4. `04-mvc-guidelines.md` define estruturas de pastas para Python/Flask **e** Node.js/Express
5. `05-refactoring-playbook.md` traz exemplos antes/depois em ambas as linguagens

---

## Estrutura de Diretórios da Entrega

```
desafio-skills/
├── README.md
│
├── code-smells-project/
│   ├── .claude/skills/refactor-arch/
│   │   ├── SKILL.md
│   │   ├── 01-project-analysis.md
│   │   ├── 02-antipatterns-catalog.md
│   │   ├── 03-report-template.md
│   │   ├── 04-mvc-guidelines.md
│   │   └── 05-refactoring-playbook.md
│   ├── src/                           ← código refatorado
│   └── reports/audit-project-1.md
│
├── ecommerce-api-legacy/
│   ├── .claude/skills/refactor-arch/  ← cópia idêntica
│   ├── src/                           ← código refatorado
│   └── reports/audit-project-2.md
│
├── task-manager-api/
│   ├── .claude/skills/refactor-arch/  ← cópia idêntica
│   ├── src/                           ← código refatorado
│   └── reports/audit-project-3.md
│
└── reports/                           ← relatórios consolidados
    ├── audit-project-1.md
    ├── audit-project-2.md
    └── audit-project-3.md
```

---

## Estrutura MVC Alvo

### Python/Flask
```
src/
├── config/settings.py       ← variáveis de ambiente (sem hardcoded)
├── models/<entidade>_model.py    ← acesso a dados
├── controllers/<entidade>_controller.py  ← lógica de negócio
├── views/routes.py          ← apenas roteamento
├── middlewares/error_handler.py  ← error handling centralizado
└── app.py                   ← entry point
```

### Node.js/Express
```
src/
├── config/settings.js
├── models/<entidade>.model.js
├── controllers/<entidade>.controller.js
├── routes/<entidade>.routes.js
├── middlewares/errorHandler.js
└── app.js
```

---

## Critérios de Aceite

Todos os critérios abaixo devem ser atingidos nos **3 projetos**:

| Critério | Obrigatoriedade |
|----------|----------------|
| Fase 1 detecta stack corretamente | OBRIGATÓRIO — 3/3 |
| Fase 2 encontra ≥5 findings | OBRIGATÓRIO — 3/3 |
| Fase 2 inclui ≥1 CRITICAL ou HIGH | OBRIGATÓRIO — 3/3 |
| Fase 2 pausa e pede confirmação antes da Fase 3 | OBRIGATÓRIO — 3/3 |
| Fase 3 cria estrutura MVC | OBRIGATÓRIO — 3/3 |
| Aplicação funciona após refatoração | OBRIGATÓRIO — 3/3 |

---

## Fluxo de Execução

```
Desenvolvedor executa: claude "/refactor-arch"
          │
          ▼
┌─────────────────────┐
│   FASE 1: ANÁLISE   │  ← lê o código, detecta stack, imprime resumo
└─────────┬───────────┘
          │
          ▼
┌─────────────────────┐
│  FASE 2: AUDITORIA  │  ← analisa anti-patterns, gera relatório
└─────────┬───────────┘
          │
          ▼
   [PAUSA — aguarda confirmação y/n do desenvolvedor]
          │
         [y]
          ▼
┌─────────────────────┐
│ FASE 3: REFATORAÇÃO │  ← reestrutura para MVC, valida funcionamento
└─────────────────────┘
          │
          ▼
   Relatório salvo em reports/audit-project-N.md
```

---

## README.md — Seções Obrigatórias

O `README.md` do repositório deve conter:

**A) Análise Manual** — problemas identificados antes de executar a skill, por projeto, com severidade e justificativa.

**B) Construção da Skill** — decisões de design, anti-patterns escolhidos e por quê, como a agnóstica de tecnologia foi garantida, desafios encontrados.

**C) Resultados** — resumo dos 3 relatórios, comparação antes/depois, checklist de validação preenchido, logs das aplicações rodando após refatoração.

**D) Como Executar** — pré-requisitos, comandos por projeto, como validar que a refatoração funcionou.

---

## Ferramenta Utilizada

**Claude Code** — com o recurso de **Custom Skills** em `.claude/skills/`.

Invocação: `claude "/refactor-arch"` dentro do diretório do projeto.

Formato dos arquivos de referência: **Markdown**.

---

## Referências

- Claude Code: Skills — documentação oficial sobre criação de Skills
- Claude Code: Overview — visão geral do Claude Code
- The Complete Guide to Building Skills for Claude (PDF)
- Equipping Agents for the Real World with Agent Skills — blog oficial da Anthropic
