# Documentação de Implementação — Skill de Auditoria e Refatoração Arquitetural

> Atualizada em 25/04/2026 — reflete o estado real dos 3 projetos criados e validados.

---

## Estado Atual do Repositório

```
desafio-skills/
├── .gitignore
├── README.md
├── reports/
│   ├── audit-project-1.md    ← gerado pela skill após execução
│   ├── audit-project-2.md
│   └── audit-project-3.md
│
├── code-smells-project/         ← Python 3.12 / Flask 3.1.1
│   ├── .claude/skills/refactor-arch/   ← skill completa (6 arquivos)
│   ├── app.py
│   ├── controllers.py
│   ├── models.py
│   ├── database.py
│   ├── requirements.txt
│   ├── .env.example
│   └── reports/audit-project-1.md
│
├── ecommerce-api-legacy/        ← Node.js v24 / Express 4
│   ├── .claude/skills/refactor-arch/
│   ├── src/
│   │   ├── AppManager.js   ← God Class principal
│   │   ├── app.js          ← config com credenciais hardcoded
│   │   ├── utils.js        ← config duplicada (code smell intencional)
│   │   └── server.js       ← entry point
│   ├── package.json
│   ├── .env.example
│   ├── api.http
│   └── reports/audit-project-2.md
│
└── task-manager-api/            ← Python 3.12 / Flask 3.0 + SQLAlchemy
    ├── .claude/skills/refactor-arch/
    ├── .vscode/settings.json    ← aponta para C:/projeto python/python12/
    ├── app.py
    ├── database.py
    ├── models/
    │   ├── task.py
    │   ├── user.py
    │   └── category.py
    ├── routes/
    │   ├── task_routes.py
    │   ├── user_routes.py
    │   └── report_routes.py
    ├── services/
    │   └── notification_service.py
    ├── utils/
    │   └── helpers.py
    ├── requirements.txt
    ├── .env.example
    └── reports/audit-project-3.md
```

---

## Projeto 1 — code-smells-project (Python/Flask)

### Stack
- **Linguagem:** Python 3.12
- **Framework:** Flask 3.1.1 + flask-cors 5.0.1
- **Banco:** SQLite (`loja.db`) via `sqlite3` nativo
- **Porta:** 5000

### Como rodar
```bash
cd code-smells-project
pip install -r requirements.txt
python app.py
```

### Endpoints disponíveis
| Método | Rota | Descrição |
|--------|------|-----------|
| GET | `/` | Index com lista de endpoints |
| GET | `/health` | Health check com contagem de registros |
| GET | `/produtos` | Listar todos os produtos |
| GET | `/produtos/busca?q=termo` | Busca com filtros |
| GET | `/produtos/<id>` | Buscar produto por ID |
| POST | `/produtos` | Criar produto |
| PUT | `/produtos/<id>` | Atualizar produto |
| DELETE | `/produtos/<id>` | Deletar produto |
| GET | `/usuarios` | Listar usuários |
| GET | `/usuarios/<id>` | Buscar usuário |
| POST | `/usuarios` | Criar usuário |
| POST | `/login` | Autenticar usuário |
| POST | `/pedidos` | Criar pedido |
| GET | `/pedidos` | Listar todos os pedidos |
| GET | `/pedidos/usuario/<id>` | Pedidos de um usuário |
| PUT | `/pedidos/<id>/status` | Atualizar status do pedido |
| GET | `/relatorios/vendas` | Relatório de vendas |
| POST | `/admin/reset-db` | Resetar banco de dados |
| POST | `/admin/query` | Executar SQL arbitrário |

### Code smells presentes (intencionais)
| Arquivo | Linha | Severidade | Problema |
|---------|-------|------------|---------|
| `app.py` | 7 | CRITICAL | `SECRET_KEY = "minha-chave-super-secreta-123"` hardcoded |
| `app.py` | 59-78 | CRITICAL | Endpoint `/admin/query` executa SQL arbitrário recebido via POST |
| `models.py` | 28 | CRITICAL | SQL Injection: `"WHERE id = " + str(id)` |
| `models.py` | 47-52 | CRITICAL | SQL Injection: concatenação na INSERT de produto |
| `models.py` | 57-62 | CRITICAL | SQL Injection: concatenação na UPDATE de produto |
| `models.py` | 109-111 | CRITICAL | SQL Injection: login via concatenação de email e senha |
| `models.py` | 126-131 | CRITICAL | SQL Injection: INSERT de usuário via concatenação |
| `models.py` | 140-165 | HIGH | God File: lógica de produto, usuário e pedido no mesmo arquivo |
| `models.py` | 139-168 | HIGH | Query N+1: busca produto para cada item no loop `for item in itens` |
| `models.py` | 171-201 | HIGH | Query N+1: 3 cursores aninhados por pedido (pedido → itens → produto) |
| `database.py` | 4 | HIGH | Estado global mutável: `db_connection = None` compartilhado |
| `controllers.py` | 287-289 | MEDIUM | `health_check` expõe `secret_key` e `db_path` na resposta JSON |
| `models.py` | 247-258 | MEDIUM | Magic numbers para faixas de desconto (0.1, 0.05, 0.02, 10000, 5000, 1000) |
| `models.py` | 279-283 | MEDIUM | SQL Injection: UPDATE de status via concatenação de string |
| `models.py` | 289-298 | MEDIUM | SQL Injection: busca com concatenação em múltiplos campos |

### Dados de seed (criados na primeira conexão)
- 10 produtos nas categorias: informatica, moveis, vestuario
- 3 usuários: `admin@loja.com/admin123`, `joao@email.com/123456`, `maria@email.com/senha123`

---

## Projeto 2 — ecommerce-api-legacy (Node.js/Express)

### Stack
- **Linguagem:** Node.js v24
- **Framework:** Express 4.18.2
- **Banco:** SQLite in-memory via `sqlite3` (async/callback)
- **Porta:** 3000

### Como rodar
```bash
cd ecommerce-api-legacy
npm install
npm start
# ou: node src/server.js
```

### Endpoints disponíveis
| Método | Rota | Descrição |
|--------|------|-----------|
| POST | `/api/checkout` | Checkout com criação de usuário, matrícula e pagamento |
| GET | `/api/admin/financial-report` | Relatório financeiro por curso |
| DELETE | `/api/users/:id` | Deletar usuário (sem cascade) |

### Estrutura de arquivos fonte
| Arquivo | Responsabilidade |
|---------|-----------------|
| `src/AppManager.js` | God Class: DB init + todas as rotas em `setupRoutes()` |
| `src/app.js` | Config com credenciais hardcoded (paymentGatewayKey, dbPass, smtpUser) |
| `src/utils.js` | Duplicata de `app.js` — mesma config repetida (code smell intencional) |
| `src/server.js` | Entry point: instancia AppManager, chama `initDb()` e `setupRoutes()` |

### Code smells presentes (intencionais)
| Arquivo | Linha | Severidade | Problema |
|---------|-------|------------|---------|
| `src/app.js` | 1-6 | CRITICAL | Credenciais hardcoded: `dbPass`, `paymentGatewayKey`, `smtpUser` |
| `src/utils.js` | 1-6 | CRITICAL | Duplicata das mesmas credenciais hardcoded |
| `src/AppManager.js` | 1-139 | CRITICAL | God Class: DB + rotas de checkout, relatório e usuários em 1 classe |
| `src/AppManager.js` | 9-10 | HIGH | Estado global mutável: `this.currentUser` e `globalCache` no singleton |
| `src/AppManager.js` | 92-128 | HIGH | Query N+1 no relatório: `enrollments.forEach` com queries aninhadas |
| `src/AppManager.js` | 43-78 | HIGH | Toda lógica de negócio do checkout dentro de callbacks de rota |
| `src/app.js` | 9 | MEDIUM | `globalCache` — objeto global mutável entre requests |
| `src/AppManager.js` | 46 | MEDIUM | Lógica de aprovação de cartão por prefixo do número (`cc.startsWith("4")`) |
| `src/utils.js` | 17-23 | MEDIUM | `badCrypto()`: função de hash insegura usada para senhas |
| `src/AppManager.js` | 131-137 | MEDIUM | DELETE sem cascade: matrículas e pagamentos ficam órfãos no banco |

### Dados de seed (iniciados no `initDb()`)
- 2 cursos: `Clean Architecture (R$997)`, `Docker (R$497)`
- 1 usuário: `leonan@fullcycle.com.br / 123`
- 1 matrícula e 1 pagamento já existentes

### Lógica de aprovação de pagamento
- Cartão começando com `4` (Visa) → `PAID` → matrícula criada
- Demais cartões → `DENIED` → HTTP 400

---

## Projeto 3 — task-manager-api (Python/Flask + SQLAlchemy)

### Stack
- **Linguagem:** Python 3.12
- **Framework:** Flask 3.0.0 + Flask-SQLAlchemy 3.1.1 + flask-cors 4.0.0
- **ORM:** SQLAlchemy (models declarativos)
- **Banco:** SQLite (`instance/tasks.db`) via SQLAlchemy
- **Porta:** 5000

### Como rodar
```bash
cd task-manager-api
pip install -r requirements.txt
python app.py
```

### Dependências (requirements.txt)
```
flask==3.0.0
flask-sqlalchemy==3.1.1
flask-cors==4.0.0
marshmallow==3.20.1
requests==2.31.0
python-dotenv==1.0.0
```

> **Nota VS Code:** configurar o interpretador para `C:/projeto python/python12/python.exe`
> via `Ctrl+Shift+P → Python: Select Interpreter` para resolver o aviso do Pylance.

### Estrutura de camadas
| Arquivo/Pasta | Camada | Descrição |
|---------------|--------|-----------|
| `database.py` | Config | `db = SQLAlchemy()` — instância compartilhada |
| `models/task.py` | Model | ORM: tabela `tasks`, métodos `to_dict()`, `validate_status()` |
| `models/user.py` | Model | ORM: tabela `users`, hash MD5 de senha (code smell intencional) |
| `models/category.py` | Model | ORM: tabela `categories` |
| `routes/task_routes.py` | Route | Blueprint `tasks`: GET/POST/PUT/DELETE `/tasks` |
| `routes/user_routes.py` | Route | Blueprint `users`: GET/POST `/users`, POST `/auth/login` |
| `routes/report_routes.py` | Route | Blueprint `reports`: GET `/reports/summary` |
| `services/notification_service.py` | Service | Notificações (simuladas via print) |
| `utils/helpers.py` | Util | Validações, formatação de datas, constantes |
| `app.py` | Entry | Registra blueprints, `db.init_app(app)`, `db.create_all()` |

### Endpoints disponíveis
| Método | Rota | Descrição |
|--------|------|-----------|
| GET | `/` | Index |
| GET | `/health` | Health check |
| GET | `/tasks` | Listar tasks |
| GET | `/tasks/<id>` | Buscar task |
| POST | `/tasks` | Criar task |
| PUT | `/tasks/<id>` | Atualizar task |
| DELETE | `/tasks/<id>` | Deletar task |
| GET | `/users` | Listar usuários |
| POST | `/users` | Criar usuário |
| POST | `/auth/login` | Login |
| GET | `/categories` | Listar categorias |
| POST | `/categories` | Criar categoria |
| GET | `/reports/summary` | Relatório resumido |

### Code smells presentes (intencionais)
| Arquivo | Linha | Severidade | Problema |
|---------|-------|------------|---------|
| `app.py` | 13 | CRITICAL | `SECRET_KEY = 'super-secret-key-123'` hardcoded |
| `models/user.py` | 29 | CRITICAL | Hash MD5 para senhas: `hashlib.md5(pwd.encode()).hexdigest()` |
| `routes/task_routes.py` | 41-57 | HIGH | Query N+1: busca `User` e `Category` por ID para cada task no loop |
| `routes/task_routes.py` | 30-58 | HIGH | Lógica de negócio (cálculo de overdue) dentro da rota `GET /tasks` |
| `utils/helpers.py` | 84-88 | MEDIUM | Magic numbers: `priority >= 1 and p <= 5` sem constantes nomeadas |
| `utils/helpers.py` | 110-116 | MEDIUM | Constantes definidas no final do arquivo após uso (ordem invertida) |
| `models/user.py` | 17-25 | MEDIUM | `to_dict()` expõe o campo `password` hash na resposta da API |
| `routes/task_routes.py` | 62 | LOW | `except:` sem especificar exceção (captura tudo silenciosamente) |

---

## Skill `/refactor-arch` — 6 Arquivos de Referência

A skill está nos 3 projetos em `.claude/skills/refactor-arch/`. O conteúdo é **idêntico** nos 3.

| Arquivo | Propósito |
|---------|-----------|
| `SKILL.md` | Prompt principal: instrui as 3 fases, formatos de saída e regra de confirmação |
| `01-project-analysis.md` | Heurísticas de detecção de linguagem, framework, domínio e arquitetura |
| `02-antipatterns-catalog.md` | 13 anti-patterns com sinais de detecção e regex para Python e Node.js |
| `03-report-template.md` | Template exato do relatório com regras de preenchimento e exemplo |
| `04-mvc-guidelines.md` | Estrutura MVC alvo + regras de responsabilidade por camada |
| `05-refactoring-playbook.md` | 10 padrões de transformação antes/depois em Python e Node.js |

### Anti-patterns catalogados
| ID | Nome | Severidade |
|----|------|------------|
| C1 | God Class / God File | CRITICAL |
| C2 | Hardcoded Credentials / Secrets | CRITICAL |
| C3 | SQL Injection | CRITICAL |
| H1 | Lógica de Negócio no Controller/Route | HIGH |
| H2 | Forte Acoplamento / Sem Injeção de Dependência | HIGH |
| H3 | Estado Global Mutável | HIGH |
| M1 | Query N+1 | MEDIUM |
| M2 | Validação Ausente nas Rotas | MEDIUM |
| M3 | Error Handling Duplicado / Ausente | MEDIUM |
| M4 | APIs Deprecated (Node.js e Python) | MEDIUM |
| L1 | Magic Numbers | LOW |
| L2 | Nomenclatura Ruim | LOW |
| L3 | Código Morto / Comentado | LOW |

---

## Ambiente de Execução

| Recurso | Versão / Caminho |
|---------|-----------------|
| Python | 3.12.x em `C:/projeto python/python12/python.exe` |
| Node.js | v24.12.0 |
| Flask (proj 1) | 3.1.1 |
| Flask (proj 3) | 3.0.0 + SQLAlchemy 3.1.1 |
| Express | 4.18.2 |
| SQLite driver Python | nativo (`sqlite3`) |
| SQLite driver Node.js | `sqlite3` (async/callback) |

### Testar os 3 projetos
```bash
# Projeto 1 — porta 5000
cd code-smells-project
"C:/projeto python/python12/python.exe" app.py

# Projeto 2 — porta 3000
cd ecommerce-api-legacy
npm start

# Projeto 3 — porta 5000
cd task-manager-api
"C:/projeto python/python12/python.exe" app.py
```

---

## Executar a Skill

```bash
# Projeto 1
cd code-smells-project
claude "/refactor-arch"

# Projeto 2
cd ../ecommerce-api-legacy
claude "/refactor-arch"

# Projeto 3
cd ../task-manager-api
claude "/refactor-arch"
```

A Fase 2 pausa e exibe:
```
Phase 2 complete. Proceed with refactoring (Phase 3)? [y/n]
```
Responda `y` para prosseguir com a refatoração.

---

## Validação Funcional (Resultados dos Testes)

### Projeto 1 — code-smells-project ✓
Testado com `app.test_client()` — 12 endpoints verificados, todos respondendo corretamente.

### Projeto 2 — ecommerce-api-legacy ✓
Testado via HTTP na porta 3001 — 4 endpoints verificados:
- `GET /api/admin/financial-report` → 200
- `POST /api/checkout` (cartão Visa) → 200 (matrícula criada)
- `POST /api/checkout` (cartão recusado) → 400
- `DELETE /api/users/1` → 200

### Projeto 3 — task-manager-api ✓
Testado com `app.test_client()` — 11 endpoints verificados, todos respondendo corretamente.

---

## Observações Importantes

1. O `code-smells-project` instalou pacotes localmente na pasta do projeto (via `--target`). Para evitar conflitos, use sempre `"C:/projeto python/python12/python.exe"` diretamente.

2. O `ecommerce-api-legacy` usa banco SQLite **in-memory** — os dados são perdidos ao reiniciar o servidor. Isso é intencional para facilitar os testes da skill.

3. O `task-manager-api` usa Flask-SQLAlchemy com banco em `instance/tasks.db` (criado automaticamente na primeira execução via `db.create_all()`).

4. O aviso `Import "flask_sqlalchemy" could not be resolved` no VS Code é resolvido apontando o interpretador para `C:/projeto python/python12/python.exe`. O arquivo `.vscode/settings.json` já está configurado no `task-manager-api/`.
