# Heurísticas de Análise de Projeto

Use este guia na Fase 1 para detectar automaticamente a stack e a arquitetura do projeto.

---

## Detecção de Linguagem

| Sinal | Linguagem |
|-------|-----------|
| Arquivos `*.py` presentes | Python |
| Arquivos `*.js` + `package.json` | Node.js / JavaScript |
| Arquivos `*.ts` + `tsconfig.json` | TypeScript |
| Arquivos `*.go` + `go.mod` | Go |
| Arquivos `*.java` + `pom.xml` ou `build.gradle` | Java |
| Arquivos `*.rb` + `Gemfile` | Ruby |

---

## Detecção de Framework

### Python
| Arquivo / Conteúdo | Framework |
|--------------------|-----------|
| `requirements.txt` contém `flask` | Flask |
| `requirements.txt` contém `django` | Django |
| `requirements.txt` contém `fastapi` | FastAPI |
| `requirements.txt` contém `tornado` | Tornado |

### Node.js
| `package.json` dependencies | Framework |
|------------------------------|-----------|
| `express` | Express.js |
| `@nestjs/core` | NestJS |
| `fastify` | Fastify |
| `koa` | Koa.js |
| `hapi` | Hapi.js |

### Detectar versão
- Python: ler a linha exata em `requirements.txt` (ex: `flask==3.1.1`)
- Node.js: ler o campo `version` de `express` em `package.json` ou `package-lock.json`

---

## Detecção de Arquitetura Atual

### Monolítica simples
- Todos os arquivos-fonte na raiz do projeto
- Menos de 2 subpastas com código
- Um arquivo com >150 linhas misturando rotas, queries e lógica

### Parcialmente organizada
- Tem subpastas (`models/`, `routes/`, `services/`) mas:
  - Queries SQL aparecem fora de `models/`
  - Lógica de negócio aparece dentro de `routes/`
  - Rotas definidas diretamente em `app.py` ou `app.js`

### MVC limpa
- Pastas `models/`, `controllers/`, `views/` ou `routes/` presentes
- Cada camada tem responsabilidade única verificável
- Entry point (`app.py`/`app.js`) apenas registra blueprints/routers

---

## Detecção de Domínio de Negócio

Analise nomes de tabelas, modelos, rotas e variáveis:

| Palavras-chave | Domínio |
|---------------|---------|
| `produto`, `product`, `pedido`, `order`, `carrinho`, `cart`, `checkout`, `estoque` | E-commerce |
| `task`, `tarefa`, `todo`, `projeto`, `project`, `kanban` | Task Manager |
| `curso`, `course`, `aula`, `lesson`, `aluno`, `student`, `matricula`, `enrollment` | LMS / EAD |
| `usuario`, `user`, `auth`, `login`, `token` | Módulo de autenticação (complemento) |
| `venda`, `sale`, `produto`, `inventory` | Sistema de vendas |

---

## Mapeamento de Banco de Dados

Buscar pelas seguintes expressões nos arquivos-fonte:

| Expressão | Tecnologia |
|-----------|-----------|
| `CREATE TABLE <nome>` | SQL puro |
| `class <Nome>(db.Model)` | Flask-SQLAlchemy |
| `mongoose.Schema(` | MongoDB / Mongoose (Node.js) |
| `sequelize.define('<nome>'` | Sequelize (Node.js) |
| `@Entity()` | TypeORM (TypeScript) |
| `new Database(` / `sqlite3.connect(` | SQLite direto |
| `better-sqlite3` / `Database(` | SQLite (Node.js) |

Para cada entidade encontrada, registre o nome e o arquivo onde foi declarada.

---

## Mapeamento de Arquivos-Fonte

Para cada arquivo-fonte (excluir: `node_modules`, `__pycache__`, `.venv`, `*.db`, `*.pyc`, `*.lock`):
- Caminho relativo
- Número de linhas
- Responsabilidade aparente (rota, model, configuração, utilitário)
