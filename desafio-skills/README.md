# Skill de Auditoria e Refatoração Arquitetural — `/refactor-arch`

Skill para Claude Code que automatiza análise, auditoria e refatoração de projetos legados para o padrão MVC, agnóstica de tecnologia (Python/Flask e Node.js/Express).

---

## Análise Manual

Antes de criar a skill, cada projeto foi analisado manualmente para identificar os principais problemas arquiteturais e de segurança.

### Projeto 1 — code-smells-project (Python/Flask)

API de E-commerce com ~780 linhas em 4 arquivos (`app.py`, `controllers.py`, `models.py`, `database.py`).

| Arquivo | Linha | Severidade | Problema |
|---------|-------|------------|---------|
| `app.py` | 7 | **CRITICAL** | `SECRET_KEY = "minha-chave-super-secreta-123"` hardcoded |
| `app.py` | 59–78 | **CRITICAL** | Endpoint `/admin/query` executa SQL arbitrário sem autenticação |
| `models.py` | 28, 47–62, 109–111 | **CRITICAL** | SQL Injection em múltiplos pontos via concatenação de strings |
| `models.py` | 140–201 | **HIGH** | God File: produto, usuário e pedido no mesmo arquivo |
| `database.py` | 4 | **HIGH** | Estado global mutável: `db_connection = None` singleton compartilhado entre requisições |
| `models.py` | 185–200 | **MEDIUM** | Query N+1: loop com query por item dentro de loop de pedidos |
| `controllers.py` | 287–289 | **MEDIUM** | `health_check` expõe `secret_key` na resposta JSON pública |
| `models.py` | 247–258 | **MEDIUM** | Magic numbers para faixas de desconto (0.1, 0.05, 10000, 5000) |
| `models.py` | 186–192 | **LOW** | Variáveis `cursor2`, `cursor3` sem nome descritivo |

**Justificativas principais:**
- **SQL Injection**: vulnerabilidade OWASP #1 — qualquer parâmetro de URL ou corpo de requisição pode exfiltrar ou destruir o banco inteiro.
- **God File `models.py`**: viola SRP; impossível testar produto sem arriscar quebrar pedido.
- **Estado global `db_connection`**: em ambiente multi-thread, Thread A pode receber resultado da query da Thread B.

### Projeto 2 — ecommerce-api-legacy (Node.js/Express)

LMS API com fluxo de checkout em 4 arquivos (`AppManager.js`, `app.js`, `utils.js`, `server.js`).

| Arquivo | Linha | Severidade | Problema |
|---------|-------|------------|---------|
| `src/app.js` | 1–6 | **CRITICAL** | Credenciais hardcoded: `paymentGatewayKey`, `smtpUser`, `dbPass` |
| `src/utils.js` | 1–6 | **CRITICAL** | Duplicata das mesmas credenciais em arquivo separado |
| `src/AppManager.js` | 1–139 | **CRITICAL** | God Class: DB + roteamento + checkout + relatório numa única classe |
| `src/AppManager.js` | 9–10 | **HIGH** | Estado global mutável: `this.currentUser` e `globalCache` no singleton |
| `src/AppManager.js` | 92–128 | **HIGH** | Query N+1 no relatório financeiro: `forEach` com queries aninhadas |
| `src/AppManager.js` | 43–78 | **HIGH** | Toda lógica de checkout dentro de callback de rota |
| `src/utils.js` | 17–23 | **MEDIUM** | `badCrypto()`: MD5 para senhas — quebrável com rainbow tables em milissegundos |
| `src/AppManager.js` | 131–137 | **MEDIUM** | DELETE de usuário sem cascade — matrículas e pagamentos ficam órfãos |

**Justificativas principais:**
- **God Class `AppManager.js`**: viola todos os princípios SOLID — uma classe com DB, HTTP, negócio e relatório é impossível de testar.
- **`this.currentUser` no singleton**: Node.js é single-threaded mas processa requisições concorrentes via event loop; estado compartilhado entre requisições é falha de segurança real.

### Projeto 3 — task-manager-api (Python/Flask + SQLAlchemy)

API de Task Manager com separação parcial em camadas (`models/`, `routes/`, `services/`, `utils/`).

| Arquivo | Linha | Severidade | Problema |
|---------|-------|------------|---------|
| `app.py` | 13 | **CRITICAL** | `SECRET_KEY = 'super-secret-key-123'` hardcoded (`.env.example` existe mas não é usado) |
| `models/user.py` | 29, 32 | **CRITICAL** | Hash MD5 sem salt para senhas — quebrável com rainbow tables |
| `routes/user_routes.py` | 210 | **CRITICAL** | Token de login `'fake-jwt-token-' + str(user.id)` — previsível, sem assinatura |
| `routes/report_routes.py` | 1–223 | **CRITICAL** | God File: 3 domínios distintos (tasks, users, categories) em um único blueprint |
| `routes/task_routes.py` | 41–57 | **HIGH** | Query N+1: `User.query.get()` e `Category.query.get()` dentro de loop |
| `routes/report_routes.py` | 13–101 | **HIGH** | 88 linhas de lógica de agregação diretamente na função de rota |
| `routes/task_routes.py` | 30–39 | **HIGH** | Lógica `is_overdue` duplicada em 6+ lugares, ignorando `Task.is_overdue()` já existente |
| `utils/helpers.py` | 84–88 | **MEDIUM** | Magic numbers: `priority >= 1 and p <= 5` sem constantes nomeadas |
| `models/user.py` | 17–25 | **MEDIUM** | `to_dict()` inclui campo `password` nas respostas da API |

**Justificativas principais:**
- **Token falso**: ausência de autenticação real — qualquer cliente pode se passar por qualquer usuário montando `fake-jwt-token-<id>`.
- **Lógica duplicada**: `is_overdue()` já existe no Model mas nunca é chamado; corrigir a regra exige editar 6+ arquivos.

---

## Construção da Skill

### Estrutura de arquivos

A skill está em `.claude/skills/refactor-arch/` com 6 arquivos:

| Arquivo | Função |
|---------|--------|
| `SKILL.md` | Prompt principal: instrui as 3 fases, formatos de saída e regra de pausa obrigatória |
| `01-project-analysis.md` | Heurísticas de detecção de linguagem, framework, domínio e arquitetura por artefatos observáveis |
| `02-antipatterns-catalog.md` | 13 anti-patterns com sinais de detecção e regex para Python e Node.js |
| `03-report-template.md` | Template exato do relatório com regras de preenchimento e exemplo preenchido |
| `04-mvc-guidelines.md` | Estrutura MVC alvo + responsabilidades por camada para Python e Node.js |
| `05-refactoring-playbook.md` | 10 padrões de transformação antes/depois em ambas as linguagens |

Cada arquivo é carregado somente na fase em que é necessário — o `SKILL.md` instrui explicitamente: *"Leia `01-project-analysis.md` antes da Fase 1"*, *"Leia `02-antipatterns-catalog.md` e `03-report-template.md` antes da Fase 2"*. Isso mantém o contexto relevante e o agente focado.

### Anti-patterns selecionados (13 total)

| ID | Nome | Severidade | Por que incluir |
|----|------|------------|----------------|
| C1 | God Class / God File | CRITICAL | Presente nos 3 projetos — viola SRP, impossível testar em isolamento |
| C2 | Hardcoded Credentials | CRITICAL | Presente nos 3 projetos — risco imediato via acesso ao repositório |
| C3 | SQL Injection | CRITICAL | 7 ocorrências no Projeto 1 — OWASP #1, destruição total do banco com 1 requisição |
| H1 | Lógica de Negócio no Route | HIGH | Presente nos 3 projetos — torna lógica intestável sem levantar servidor |
| H2 | Forte Acoplamento | HIGH | Projetos 1 e 2 — conexões instanciadas dentro de funções de negócio |
| H3 | Estado Global Mutável | HIGH | Projetos 1 e 2 — compartilhamento entre requisições causa bugs silenciosos |
| M1 | Query N+1 | MEDIUM | Presente nos 3 projetos — invisível em dev, crítico em produção |
| M2 | Validação Ausente | MEDIUM | Presente nos 3 projetos — inputs chegam direto ao banco sem verificação |
| M3 | Error Handling Duplicado | MEDIUM | Projetos 1 e 2 — mesmo try/except em 10+ rotas |
| M4 | APIs Deprecated | MEDIUM | Obrigatório por requisito — `new Buffer()`, `res.send(statusCode)`, MD5 para senhas |
| L1 | Magic Numbers | LOW | Presente nos 3 projetos — regras de negócio como literais opacos |
| L2 | Nomenclatura Ruim | LOW | `cursor2`, `cursor3`, `d`, `tmp` em código de produção |
| L3 | Código Morto | LOW | `NotificationService` nunca chamado, funções comentadas |

### Como a agnósticidade de tecnologia foi garantida

**1. Detecção por artefatos observáveis, não por suposição**

O `01-project-analysis.md` usa sinais concretos:
- `*.py` + ausência de `package.json` → Python
- `package.json` com `"express"` → Node.js/Express
- `db.Model` / `SQLAlchemy` → Flask-SQLAlchemy
- `sqlite3.connect` / `better-sqlite3` → SQLite direto

**2. Anti-patterns com exemplos em ambas as linguagens**

Cada anti-pattern no catálogo tem exemplos Python e JavaScript com regex de detecção para cada. Ex: SQL Injection tem regex `f"SELECT.*{` para Python e `` `SELECT.*${ `` para JavaScript.

**3. Playbook com transformações bilíngues**

Todos os 10 padrões de refatoração têm versão Python e Node.js lado a lado.

**4. Guidelines MVC adaptadas por linguagem**

O `04-mvc-guidelines.md` define estruturas de diretórios distintas para Flask (`src/config/`, `src/models/`, `src/controllers/`, `src/views/`, `src/middlewares/`) e Express (`src/config/`, `src/models/`, `src/controllers/`, `src/routes/`, `src/middlewares/`).

### Regra de pausa na Fase 2

A confirmação antes da Fase 3 foi implementada com ênfase tipográfica intencional no `SKILL.md`:

```
### REGRA OBRIGATÓRIA:
NUNCA modifique, crie ou delete arquivos antes desta confirmação.
```

Testes iniciais mostraram que o agente tendia a prosseguir automaticamente quando a instrução estava em texto corrido. A combinação de heading `###`, maiúsculas e posicionamento imediatamente antes do ponto de pausa resolveu o problema.

---

## Resultados

### Resumo dos relatórios de auditoria

| Projeto | Stack | Findings | CRITICAL | HIGH | MEDIUM | LOW |
|---------|-------|----------|----------|------|--------|-----|
| code-smells-project | Python/Flask | 14 | 6 | 3 | 3 | 2 |
| ecommerce-api-legacy | Node.js/Express | 6* | 2 | 0 | 1 | 3 |
| task-manager-api | Python/Flask + SQLAlchemy | 17 | 5 | 5 | 5 | 2 |

*Nota: o Projeto 2 foi auditado após a refatoração MVC já aplicada; os findings reflectem problemas remanescentes na estrutura refatorada (ex: ausência de autenticação nas rotas).

### Comparação antes/depois

**Projeto 1 — code-smells-project**

```
ANTES                          DEPOIS
app.py (88 linhas)             src/
controllers.py (292 linhas)    ├── config/
database.py (86 linhas)        │   ├── settings.py   (SECRET_KEY via os.environ)
models.py (314 linhas)         │   └── constants.py  (magic numbers nomeados)
                               ├── models/
                               │   ├── produto_model.py
                               │   ├── pedido_model.py
                               │   ├── usuario_model.py
                               │   └── relatorio_model.py
                               ├── controllers/
                               │   ├── produto_controller.py
                               │   ├── pedido_controller.py
                               │   ├── usuario_controller.py
                               │   └── relatorio_controller.py
                               ├── views/
                               │   ├── produto_routes.py
                               │   ├── pedido_routes.py
                               │   ├── auth_routes.py
                               │   └── relatorio_routes.py
                               ├── middlewares/
                               │   └── error_handler.py
                               └── app.py  (composition root)
```

**Projeto 2 — ecommerce-api-legacy**

```
ANTES                          DEPOIS
src/                           src/
├── AppManager.js (141 linhas) ├── config/
├── app.js (25 linhas)         │   ├── settings.js   (vars via process.env)
├── utils.js (25 linhas)       │   └── constants.js
└── server.js                  ├── models/
                               │   ├── user.model.js
                               │   ├── course.model.js
                               │   ├── enrollment.model.js
                               │   └── payment.model.js
                               ├── controllers/
                               │   ├── checkout.controller.js
                               │   ├── user.controller.js
                               │   └── financialReport.controller.js
                               ├── routes/
                               │   ├── checkout.routes.js
                               │   ├── user.routes.js
                               │   └── admin.routes.js
                               ├── middlewares/
                               │   ├── errorHandler.js
                               │   └── requireAdmin.js
                               └── app.js  (composition root)
```

**Projeto 3 — task-manager-api**

```
ANTES                          DEPOIS
app.py                         app.py
database.py                    database.py
models/ (3 arquivos)           config/
routes/ (3 arquivos, 733 linhas) │   ├── settings.py  (SECRET_KEY + credenciais via os.environ)
services/                      │   └── constants.py (VALID_STATUSES, VALID_ROLES centralizados)
utils/                         controllers/
                               │   ├── task_controller.py
                               │   ├── user_controller.py
                               │   ├── category_controller.py
                               │   └── report_controller.py
                               models/ (mantidos, is_overdue() agora utilizado)
                               views/ (rotas finas — apenas parse + chamada ao controller)
                               middlewares/
                               │   └── error_handler.py (centralizado, 9 rotas simplificadas)
                               utils/ (mantido)
```

### Checklist de validação

#### Projeto 1 — code-smells-project

**Fase 1 — Análise**
- [x] Linguagem detectada: Python
- [x] Framework detectado: Flask 3.1.1
- [x] Domínio: E-commerce API (produtos, pedidos, usuários)
- [x] Arquivos analisados: 4 arquivos, ~780 linhas

**Fase 2 — Auditoria**
- [x] Relatório segue o template
- [x] Cada finding tem arquivo e linhas exatos
- [x] Findings ordenados CRITICAL → LOW
- [x] 14 findings identificados (≥5)
- [x] Detecção de APIs deprecated: N/A para este projeto
- [x] Skill pausou e pediu confirmação antes da Fase 3

**Fase 3 — Refatoração**
- [x] Estrutura MVC criada em `src/`
- [x] Configuração extraída para `src/config/settings.py` com `os.environ`
- [x] Models criados por domínio em `src/models/`
- [x] Views/Routes em `src/views/`
- [x] Controllers em `src/controllers/`
- [x] Error handling centralizado em `src/middlewares/error_handler.py`
- [x] Entry point limpo: `src/app.py`
- [x] Aplicação inicia sem erros (`python -c "import app"` OK)

#### Projeto 2 — ecommerce-api-legacy

**Fase 1 — Análise**
- [x] Linguagem detectada: JavaScript (Node.js)
- [x] Framework detectado: Express.js 4.22.1
- [x] Domínio: LMS API com fluxo de checkout
- [x] Arquivos analisados: 17 arquivos, ~427 linhas

**Fase 2 — Auditoria**
- [x] Relatório segue o template
- [x] Cada finding tem arquivo e linhas exatos
- [x] Findings ordenados CRITICAL → LOW
- [x] 6 findings identificados (≥5)
- [x] Detecção de APIs deprecated incluída (`new Buffer()` → `Buffer.from()`)
- [x] Skill pausou e pediu confirmação antes da Fase 3

**Fase 3 — Refatoração**
- [x] Estrutura MVC criada em `src/`
- [x] Configuração extraída para `src/config/settings.js` com `process.env`
- [x] Models criados por entidade em `src/models/`
- [x] Routes em `src/routes/`
- [x] Controllers em `src/controllers/`
- [x] Error handling centralizado em `src/middlewares/errorHandler.js`
- [x] Entry point limpo: `src/app.js`
- [x] Aplicação inicia sem erros

#### Projeto 3 — task-manager-api

**Fase 1 — Análise**
- [x] Linguagem detectada: Python
- [x] Framework detectado: Flask 3.0.0 + Flask-SQLAlchemy 3.1.1
- [x] Domínio: API de Task Manager
- [x] Arquivos analisados: 16 arquivos, ~1256 linhas

**Fase 2 — Auditoria**
- [x] Relatório segue o template
- [x] Cada finding tem arquivo e linhas exatos
- [x] Findings ordenados CRITICAL → LOW
- [x] 17 findings identificados (≥5)
- [x] Detecção de APIs deprecated: MD5 para senhas detectado como deprecated
- [x] Skill pausou e pediu confirmação antes da Fase 3

**Fase 3 — Refatoração**
- [x] Estrutura MVC criada (`config/`, `controllers/`, `views/`, `middlewares/`)
- [x] Configuração extraída para `config/settings.py` com `os.environ`
- [x] Models mantidos e is_overdue() / validate_status() agora utilizados
- [x] Views/Routes em `views/` (finas — apenas parse + chamada ao controller)
- [x] Controllers em `controllers/`
- [x] Error handling centralizado em `middlewares/error_handler.py`
- [x] Entry point limpo: `app.py`
- [x] Aplicação inicia sem erros, endpoints originais respondem corretamente

---

## Como Executar

### Pré-requisitos

- [Claude Code](https://docs.anthropic.com/en/docs/claude-code/overview) instalado e autenticado
- Python 3.10+ (para os projetos Python/Flask)
- Node.js 18+ (para o projeto Node.js/Express)

### Projeto 1 — code-smells-project (Python/Flask)

```bash
cd code-smells-project
pip install -r requirements.txt
claude "/refactor-arch"
```

Para validar a refatoração:

```bash
cd src
python app.py          # aplicação deve iniciar na porta 5000
# Em outro terminal:
curl http://localhost:5000/health
curl http://localhost:5000/produtos
```

### Projeto 2 — ecommerce-api-legacy (Node.js/Express)

```bash
cd ecommerce-api-legacy
npm install
claude "/refactor-arch"
```

Para validar a refatoração:

```bash
node src/app.js        # aplicação deve iniciar na porta 3000
# Em outro terminal:
curl -X POST http://localhost:3000/api/checkout \
  -H "Content-Type: application/json" \
  -d '{"userName":"test","email":"t@t.com","courseId":1,"cardNumber":"4111111111111111","paymentMethod":"credit_card"}'
```

### Projeto 3 — task-manager-api (Python/Flask + SQLAlchemy)

```bash
cd task-manager-api
pip install -r requirements.txt
claude "/refactor-arch"
```

Para validar a refatoração:

```bash
python app.py          # aplicação deve iniciar na porta 5000
# Em outro terminal:
curl http://localhost:5000/health
curl http://localhost:5000/tasks
curl http://localhost:5000/reports/summary
```

### Como validar que a refatoração funcionou

1. **Aplicação inicia sem erros** — nenhum `ImportError`, `ModuleNotFoundError` ou `SyntaxError` no terminal
2. **Endpoints originais respondem** — todos os endpoints do projeto original retornam o mesmo status HTTP
3. **Estrutura MVC presente** — pastas `config/`, `models/`, `controllers/`, `views/` (ou `routes/`), `middlewares/` criadas
4. **Sem hardcoded secrets** — `grep -r "SECRET_KEY\s*=" src/` não deve retornar valores literais
5. **Relatório salvo** — `reports/audit-project-N.md` deve ter conteúdo real (não o placeholder)
