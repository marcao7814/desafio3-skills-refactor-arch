# Passo a Passo — Implementação da Skill `/refactor-arch`

> Guia de execução sequencial. Siga cada passo na ordem indicada.  
> Referência completa: [documentacao.md](documentacao.md)

---

## PRÉ-REQUISITOS

Antes de começar, confirme que você tem:

- [ ] Claude Code instalado (`claude --version`)
- [ ] Python 3.x instalado (`python --version`)
- [ ] Node.js instalado (`node --version`)
- [ ] Git configurado (`git config user.name`)
- [ ] Repositório base do desafio clonado (fork no GitHub)

---

## ETAPA 1 — Criar a estrutura de pastas da skill

Execute dentro da raiz do repositório clonado:

```bash
mkdir -p code-smells-project/.claude/skills/refactor-arch
mkdir -p code-smells-project/reports
mkdir -p ecommerce-api-legacy/.claude/skills/refactor-arch
mkdir -p ecommerce-api-legacy/reports
mkdir -p task-manager-api/.claude/skills/refactor-arch
mkdir -p task-manager-api/reports
```

Resultado esperado:
```
desafio-skills/
├── code-smells-project/.claude/skills/refactor-arch/   ✓
├── ecommerce-api-legacy/.claude/skills/refactor-arch/  ✓
└── task-manager-api/.claude/skills/refactor-arch/      ✓
```

---

## ETAPA 2 — Criar o arquivo SKILL.md

**Arquivo:** `code-smells-project/.claude/skills/refactor-arch/SKILL.md`

Este é o prompt principal da skill. Crie o arquivo com o conteúdo abaixo:

```markdown
# /refactor-arch — Arquitetura MVC Audit & Refactor Skill

Você é um especialista em arquitetura de software. Ao ser invocado com `/refactor-arch`,
execute as 3 fases abaixo em sequência. Leia os arquivos de referência antes de cada fase.

---

## FASE 1 — ANÁLISE DO PROJETO

Leia `01-project-analysis.md` para as heurísticas de detecção.

### Tarefas:
1. Percorra todos os arquivos-fonte do projeto atual (ignore node_modules, __pycache__, .venv, dist, build).
2. Detecte: linguagem principal, framework, dependências, domínio de negócio, arquitetura atual.
3. Mapeie todos os arquivos-fonte com número de linhas.
4. Identifique as tabelas/entidades de banco de dados.

### Saída obrigatória:
================================
PHASE 1: PROJECT ANALYSIS
================================
Language:      <linguagem>
Framework:     <framework + versão>
Dependencies:  <lista de dependências relevantes>
Domain:        <descrição do domínio de negócio>
Architecture:  <descrição da arquitetura atual>
Source files:  <N> files analyzed
DB tables:     <lista de tabelas ou entidades>
================================

---

## FASE 2 — AUDITORIA DE ARQUITETURA

Leia `02-antipatterns-catalog.md` e `03-report-template.md` antes de começar.

### Tarefas:
1. Analise cada arquivo-fonte linha por linha.
2. Cruze o código contra o catálogo de anti-patterns.
3. Para cada problema encontrado, registre: severidade, arquivo, linhas exatas, descrição, impacto, recomendação.
4. Ordene os findings por severidade: CRITICAL → HIGH → MEDIUM → LOW.
5. Gere o relatório seguindo estritamente o template em `03-report-template.md`.

### REGRA OBRIGATÓRIA:
PARE após gerar o relatório e pergunte:
"Phase 2 complete. Proceed with refactoring (Phase 3)? [y/n]"
Somente prossiga para a Fase 3 se o usuário responder "y".
NUNCA modifique arquivos sem confirmação explícita.

---

## FASE 3 — REFATORAÇÃO PARA MVC

Leia `04-mvc-guidelines.md` e `05-refactoring-playbook.md` antes de começar.

### Tarefas:
1. Crie a nova estrutura de diretórios MVC conforme `04-mvc-guidelines.md`.
2. Para cada anti-pattern encontrado, aplique o padrão de transformação do `05-refactoring-playbook.md`.
3. Extraia configurações hardcoded para `config/settings.py` ou `config/settings.js`.
4. Crie Models para abstrair acesso a dados (sem lógica de negócio).
5. Crie Controllers com a lógica de negócio (sem queries SQL diretas).
6. Crie Views/Routes apenas com roteamento (sem lógica).
7. Centralize error handling em `middlewares/`.
8. Mantenha um entry point claro (`app.py` ou `app.js`).

### Validação após refatoração:
- Tente iniciar a aplicação e verifique que não há erros de boot.
- Verifique que os endpoints originais estão presentes nas rotas.
- Confirme que não há imports quebrados.

### Saída obrigatória:
================================
PHASE 3: REFACTORING COMPLETE
================================
New Project Structure:
<árvore de diretórios>

Validation:
  ✓/✗ Application boots without errors
  ✓/✗ All endpoints respond correctly
  ✓/✗ Zero anti-patterns remaining
================================

Salve o relatório da Fase 2 em `reports/audit-project-N.md`.
```

---

## ETAPA 3 — Criar 01-project-analysis.md

**Arquivo:** `code-smells-project/.claude/skills/refactor-arch/01-project-analysis.md`

```markdown
# Heurísticas de Análise de Projeto

## Detecção de Linguagem
- Presença de `*.py` → Python
- Presença de `*.js` + `package.json` → Node.js/JavaScript
- Presença de `*.ts` + `tsconfig.json` → TypeScript
- Presença de `*.go` + `go.mod` → Go
- Presença de `*.java` + `pom.xml` ou `build.gradle` → Java

## Detecção de Framework
- `requirements.txt` contém `flask` → Flask
- `requirements.txt` contém `django` → Django
- `requirements.txt` contém `fastapi` → FastAPI
- `package.json` dependencies contém `express` → Express.js
- `package.json` contém `@nestjs/core` → NestJS

## Detecção de Arquitetura Atual
- **Monolítica simples:** todos os arquivos na raiz, sem subpastas de domínio
- **Parcialmente organizada:** tem pastas (models/, routes/, services/) mas com responsabilidades misturadas
- **MVC limpa:** tem models/, views/ ou routes/, controllers/ com responsabilidades bem definidas

## Detecção de Domínio de Negócio
- Tabelas/modelos/rotas com: `produto`, `product`, `pedido`, `order`, `carrinho`, `cart` → E-commerce
- Tabelas/modelos/rotas com: `task`, `tarefa`, `todo` → Task Manager
- Tabelas/modelos/rotas com: `curso`, `course`, `aluno`, `student`, `aula`, `lesson` → LMS/EAD
- Tabelas/modelos/rotas com: `user`, `usuario`, `auth`, `login` → complemento de qualquer domínio

## Mapeamento de Banco de Dados
Buscar por:
- `CREATE TABLE` (SQL puro)
- `db.Model` (Flask-SQLAlchemy)
- `mongoose.Schema` (MongoDB/Node.js)
- `sequelize.define` (Node.js/Sequelize)
- `@Entity` (Java/TypeORM)

Liste o nome de cada entidade/tabela encontrada.
```

---

## ETAPA 4 — Criar 02-antipatterns-catalog.md

**Arquivo:** `code-smells-project/.claude/skills/refactor-arch/02-antipatterns-catalog.md`

```markdown
# Catálogo de Anti-Patterns

---

## CRITICAL

### C1 — God Class / God File
- Sinal: arquivo único com >200 linhas contendo queries SQL + lógica de negócio + validação + formatação
- Sinal: classe com >10 métodos de domínios diferentes
- Exemplo Python: `models.py` com funções criar_produto, fazer_pedido, autenticar_usuario no mesmo arquivo
- Exemplo JS: `GodManager.js` com métodos de usuário, produto e pedido na mesma classe

### C2 — Hardcoded Credentials / Secrets
- Sinal: SECRET_KEY = "..." literal no código-fonte
- Sinal: password = "...", DB_PASSWORD = "...", API_KEY = "..." com valor hardcoded
- Sinal: connection string com usuário/senha inline
- Regex Python/JS: `(SECRET|PASSWORD|KEY|TOKEN)\s*=\s*["'][^"']{4,}["']`

### C3 — SQL Injection
- Sinal: query com concatenação de string: "SELECT * FROM " + tabela
- Sinal: f-string em query Python: f"SELECT * FROM users WHERE id={user_id}"
- Sinal: .format() em query SQL
- Sinal: template string JS em query: `SELECT * FROM users WHERE id=${userId}`

---

## HIGH

### H1 — Lógica de Negócio no Controller/Route
- Sinal: função de rota com >30 linhas
- Sinal: query SQL diretamente dentro de @app.route ou router.get/post
- Sinal: múltiplos if/else de regra de negócio dentro do handler de rota

### H2 — Forte Acoplamento / Sem Injeção de Dependência
- Sinal: instância de banco criada dentro de funções de negócio (ex: conn = sqlite3.connect(...))
- Sinal: import direto de módulos concretos sem abstração

### H3 — Estado Global Mutável
- Sinal: variável global modificada por múltiplas funções
- Sinal: uso de `global` keyword em Python dentro de funções de rota
- Sinal: variável de módulo mutável compartilhada entre requests

---

## MEDIUM

### M1 — Query N+1
- Sinal: query SQL ou ORM dentro de loop `for`
- Exemplo: for pedido in pedidos: db.execute("SELECT * FROM itens WHERE pedido_id=?", pedido.id)
- Solução: usar JOIN ou prefetch

### M2 — Validação Ausente nas Rotas
- Sinal: request.json.get(campo) ou req.body.campo sem verificação de None/undefined
- Sinal: ausência de qualquer schema de validação (sem marshmallow, joi, zod, pydantic)

### M3 — Error Handling Duplicado
- Sinal: bloco try/catch ou try/except repetido identicamente em cada rota
- Sinal: autenticação verificada manualmente em cada rota em vez de decorator/middleware

### M4 — APIs Deprecated
Python:
- `from flask.ext.*` → removido no Flask 1.0+
- `import distutils` → deprecated Python 3.10+, removido 3.12

Node.js:
- `new Buffer(...)` → deprecated desde Node 6, usar Buffer.from()
- `require('url').parse(...)` → deprecated, usar new URL()
- `res.send(404)` → deprecated Express 4, usar res.status(404).send()

Regex JS: `new Buffer\(`, `require\('url'\)\.parse`, `res\.send\(\d{3}\)`
Regex Python: `from flask\.ext`, `import distutils`

---

## LOW

### L1 — Magic Numbers
- Sinal: número literal sem contexto: if status == 3:, time.sleep(60), limit = 100
- Solução: extrair para constante nomeada em config/constants

### L2 — Nomenclatura Ruim
- Sinal: variáveis de 1-2 letras fora de loops (x, d, tmp)
- Sinal: nomes genéricos sem contexto: data, info, result, obj
- Sinal: mistura de idiomas (inglês/português) em nomes de função no mesmo arquivo

### L3 — Código Morto / Comentado
- Sinal: blocos de código comentados com # ou // por mais de 5 linhas consecutivas
- Sinal: funções definidas mas nunca referenciadas no código
```

---

## ETAPA 5 — Criar 03-report-template.md

**Arquivo:** `code-smells-project/.claude/skills/refactor-arch/03-report-template.md`

```markdown
# Template do Relatório de Auditoria

Use EXATAMENTE este formato na Fase 2:

================================
ARCHITECTURE AUDIT REPORT
================================
Project: <nome-do-projeto>
Stack:   <linguagem> + <framework>
Files:   <N> analyzed | ~<total> lines of code

Summary
CRITICAL: <N> | HIGH: <N> | MEDIUM: <N> | LOW: <N>

Findings

[CRITICAL] <Nome do Anti-Pattern>
File: <caminho/arquivo.ext>:<linha-início>-<linha-fim>
Description: <descrição objetiva — citar o trecho de código problemático>
Impact: <consequência técnica ou de negócio>
Recommendation: <ação concreta para corrigir>

[HIGH] <Nome do Anti-Pattern>
File: <caminho/arquivo.ext>:<linha>
Description: <descrição>
Impact: <impacto>
Recommendation: <recomendação>

[MEDIUM] <Nome do Anti-Pattern>
File: <caminho/arquivo.ext>:<linha-início>-<linha-fim>
Description: <descrição>
Impact: <impacto>
Recommendation: <recomendação>

[LOW] <Nome do Anti-Pattern>
File: <caminho/arquivo.ext>:<linha>
Description: <descrição>
Impact: <impacto>
Recommendation: <recomendação>

================================
Total: <N> findings
================================

## Regras obrigatórias:
- Cada finding DEVE ter arquivo E linhas exatas
- Ordenar sempre: CRITICAL → HIGH → MEDIUM → LOW
- Description deve citar o trecho problemático real, não genérico
- Mínimo de 5 findings por projeto
- Ao menos 1 CRITICAL ou HIGH obrigatório
```

---

## ETAPA 6 — Criar 04-mvc-guidelines.md

**Arquivo:** `code-smells-project/.claude/skills/refactor-arch/04-mvc-guidelines.md`

```markdown
# Guidelines de Arquitetura MVC

## Estrutura Alvo — Python/Flask

src/
├── config/
│   └── settings.py          ← variáveis de ambiente e configuração
├── models/
│   └── <entidade>_model.py  ← acesso a dados, queries, ORM
├── controllers/
│   └── <entidade>_controller.py  ← lógica de negócio
├── views/
│   └── routes.py            ← apenas roteamento
├── middlewares/
│   └── error_handler.py     ← tratamento centralizado de erros
└── app.py                   ← composition root, registra blueprints

## Estrutura Alvo — Node.js/Express

src/
├── config/
│   └── settings.js          ← variáveis de ambiente
├── models/
│   └── <entidade>.model.js  ← acesso a dados
├── controllers/
│   └── <entidade>.controller.js  ← lógica de negócio
├── routes/
│   └── <entidade>.routes.js ← apenas roteamento
├── middlewares/
│   └── errorHandler.js      ← tratamento centralizado de erros
└── app.js                   ← entry point

## Responsabilidades por Camada

**Models** — APENAS:
- Queries SQL ou chamadas ORM
- Mapeamento de dados (row → objeto)
NÃO PODE TER: lógica de negócio, validação de request, formatação de response

**Controllers** — APENAS:
- Lógica de negócio
- Validação de dados de entrada
- Orquestração de calls aos models
NÃO PODE TER: queries SQL diretas, headers HTTP, status codes hardcoded

**Views/Routes** — APENAS:
- Definição de rotas (path + método HTTP)
- Extração de parâmetros (req.body, request.json)
- Chamada ao controller e retorno da response
NÃO PODE TER: lógica de negócio, queries, cálculos

**Config** — OBRIGATÓRIO:
- Variáveis via os.environ.get() (Python) ou process.env (Node.js)
- Valores default seguros para desenvolvimento
- Nunca commitar valores reais — criar .env.example
```

---

## ETAPA 7 — Criar 05-refactoring-playbook.md

**Arquivo:** `code-smells-project/.claude/skills/refactor-arch/05-refactoring-playbook.md`

```markdown
# Playbook de Refatoração

Padrões de transformação para cada anti-pattern, com exemplos antes/depois.

---

## Padrão 1 — Extrair Configuração Hardcoded

**Antes (Python):**
```python
app.config['SECRET_KEY'] = 'minha-chave-super-secreta-123'
DATABASE = 'sqlite:///db.sqlite3'
```
**Depois:**
```python
# config/settings.py
import os
SECRET_KEY = os.environ.get('SECRET_KEY', 'dev-key-change-in-prod')
DATABASE_URL = os.environ.get('DATABASE_URL', 'sqlite:///db.sqlite3')
```

**Antes (Node.js):**
```javascript
const SECRET = 'hardcoded-secret';
const DB_URL = 'mongodb://localhost:27017/mydb';
```
**Depois:**
```javascript
// config/settings.js
module.exports = {
  SECRET: process.env.SECRET || 'dev-key-change-in-prod',
  DB_URL: process.env.DB_URL || 'mongodb://localhost:27017/mydb',
};
```

---

## Padrão 2 — Extrair Query para Model

**Antes (Python — query direto na rota):**
```python
@app.route('/produtos')
def listar_produtos():
    conn = sqlite3.connect('db.sqlite3')
    produtos = conn.execute('SELECT * FROM produtos').fetchall()
    return jsonify(produtos)
```
**Depois:**
```python
# models/produto_model.py
def get_all_produtos(db):
    return db.execute('SELECT * FROM produtos').fetchall()

# controllers/produto_controller.py
from models.produto_model import get_all_produtos
def listar_produtos(db):
    return get_all_produtos(db)

# views/routes.py
@app.route('/produtos')
def produtos_route():
    return jsonify(listar_produtos(get_db()))
```

**Antes (Node.js):**
```javascript
router.get('/users', async (req, res) => {
  const users = await db.query('SELECT * FROM users');
  res.json(users);
});
```
**Depois:**
```javascript
// models/user.model.js
async function getAllUsers(db) {
  return db.query('SELECT * FROM users');
}

// controllers/user.controller.js
async function listarUsuarios(db) {
  return getAllUsers(db);
}

// routes/user.routes.js
router.get('/users', async (req, res, next) => {
  try {
    const users = await listarUsuarios(db);
    res.json(users);
  } catch (err) { next(err); }
});
```

---

## Padrão 3 — Quebrar God Class por Domínio

**Antes:**
```python
# models.py (350 linhas — todos os domínios misturados)
def criar_produto(nome, preco): ...
def fazer_pedido(usuario_id, items): ...
def autenticar_usuario(email, senha): ...
```
**Depois:**
```
models/
├── produto_model.py   ← apenas funções de produto
├── pedido_model.py    ← apenas funções de pedido
└── usuario_model.py   ← apenas funções de usuário

controllers/
├── produto_controller.py
├── pedido_controller.py
└── usuario_controller.py
```

---

## Padrão 4 — Corrigir SQL Injection

**Antes:**
```python
user_id = request.args.get('id')
query = f"SELECT * FROM usuarios WHERE id={user_id}"
resultado = db.execute(query)
```
**Depois:**
```python
user_id = request.args.get('id')
resultado = db.execute("SELECT * FROM usuarios WHERE id=?", (user_id,))
```

**Antes (Node.js):**
```javascript
const query = `SELECT * FROM users WHERE id=${req.params.id}`;
```
**Depois:**
```javascript
const query = 'SELECT * FROM users WHERE id = ?';
db.query(query, [req.params.id]);
```

---

## Padrão 5 — Extrair Lógica de Negócio da Rota

**Antes (Node.js — >30 linhas de lógica na rota):**
```javascript
router.post('/checkout', async (req, res) => {
  const { userId, items } = req.body;
  let total = 0;
  for (const item of items) {
    const produto = await db.query('SELECT * FROM produtos WHERE id=?', [item.id]);
    if (produto.estoque < item.quantidade) {
      return res.status(400).json({ error: 'Sem estoque' });
    }
    total += produto.preco * item.quantidade;
  }
  // ... mais 30 linhas
});
```
**Depois:**
```javascript
// controllers/checkout.controller.js
async function processarCheckout(userId, items, db) {
  await verificarEstoque(items, db);
  const total = await calcularTotal(items, db);
  return criarPedido(userId, items, total, db);
}

// routes/checkout.routes.js
router.post('/checkout', async (req, res, next) => {
  try {
    const resultado = await processarCheckout(req.body.userId, req.body.items, db);
    res.json(resultado);
  } catch (err) { next(err); }
});
```

---

## Padrão 6 — Centralizar Error Handling

**Antes (repetido em cada rota):**
```javascript
router.get('/users', async (req, res) => {
  try { ... }
  catch(err) { res.status(500).json({ error: err.message }); }
});
```
**Depois:**
```javascript
// middlewares/errorHandler.js
function errorHandler(err, req, res, next) {
  const status = err.status || 500;
  res.status(status).json({ error: err.message });
}
module.exports = errorHandler;

// app.js — registrar por último
app.use(errorHandler);

// rotas — apenas propagar
router.get('/users', async (req, res, next) => {
  try { ... }
  catch(err) { next(err); }
});
```

**Python equivalente:**
```python
# middlewares/error_handler.py
def register_error_handlers(app):
    @app.errorhandler(Exception)
    def handle_exception(e):
        return jsonify({'error': str(e)}), 500

# app.py
register_error_handlers(app)
```

---

## Padrão 7 — Eliminar Query N+1

**Antes:**
```python
pedidos = db.execute("SELECT * FROM pedidos").fetchall()
for pedido in pedidos:
    itens = db.execute("SELECT * FROM itens WHERE pedido_id=?", (pedido['id'],)).fetchall()
```
**Depois:**
```python
pedidos_com_itens = db.execute("""
    SELECT p.*, i.produto_id, i.quantidade, i.preco
    FROM pedidos p
    LEFT JOIN itens i ON i.pedido_id = p.id
""").fetchall()
```

---

## Padrão 8 — Substituir Magic Numbers por Constantes

**Antes:**
```python
if usuario['role'] == 2:
    desconto = preco * 0.15
if status == 3:
    enviar_email_confirmacao()
```
**Depois:**
```python
# config/constants.py
ROLE_ADMIN = 2
STATUS_PEDIDO_CONFIRMADO = 3
DESCONTO_PREMIUM = 0.15

# uso
if usuario['role'] == ROLE_ADMIN:
    desconto = preco * DESCONTO_PREMIUM
```

---

## Padrão 9 — Corrigir APIs Deprecated (Node.js)

**Antes:**
```javascript
const buf = new Buffer(data);              // deprecated Node 6
const parsed = require('url').parse(url);  // deprecated
res.send(404);                             // deprecated Express 4
```
**Depois:**
```javascript
const buf = Buffer.from(data);
const parsed = new URL(url);
res.status(404).send();
```

---

## Padrão 10 — Adicionar Validação de Entrada

**Antes:**
```python
@app.route('/usuarios', methods=['POST'])
def criar_usuario():
    dados = request.json
    criar_usuario_model(dados.get('nome'), dados.get('email'))
```
**Depois:**
```python
@app.route('/usuarios', methods=['POST'])
def criar_usuario():
    dados = request.json or {}
    nome = dados.get('nome')
    email = dados.get('email')
    if not nome or not email:
        return jsonify({'error': 'nome e email são obrigatórios'}), 400
    if '@' not in email:
        return jsonify({'error': 'email inválido'}), 400
    criar_usuario_model(nome, email)
```
```

---

## ETAPA 8 — Copiar a skill para os outros projetos

Com os 6 arquivos criados em `code-smells-project/.claude/skills/refactor-arch/`, copie para os demais projetos:

```bash
cp -r code-smells-project/.claude/skills/refactor-arch ecommerce-api-legacy/.claude/skills/
cp -r code-smells-project/.claude/skills/refactor-arch task-manager-api/.claude/skills/
```

---

## ETAPA 9 — Analisar manualmente os 3 projetos (antes de executar a skill)

Leia o código de cada projeto e documente no `README.md` da raiz do repositório — seção **"Análise Manual"**.

Para cada projeto, registre **mínimo 5 problemas** no formato:

```
### Projeto 1 — code-smells-project (Python/Flask)

| # | Arquivo | Linha(s) | Severidade | Problema | Justificativa |
|---|---------|----------|------------|----------|---------------|
| 1 | models.py | 1-350 | CRITICAL | God Class | ... |
| 2 | app.py | 8 | CRITICAL | Hardcoded SECRET_KEY | ... |
| 3 | models.py | 45 | HIGH | SQL Injection via f-string | ... |
| 4 | controllers.py | 120-150 | MEDIUM | Query N+1 no loop | ... |
| 5 | models.py | 200 | LOW | Magic number sem constante | ... |
```

Requisito mínimo por projeto:
- ≥1 CRITICAL ou HIGH
- ≥2 MEDIUM
- ≥2 LOW

---

## ETAPA 10 — Executar a skill no Projeto 1

```bash
cd code-smells-project
claude "/refactor-arch"
```

**Verificar Fase 1:**
- [ ] Detectou Python + Flask
- [ ] Descreveu o domínio como E-commerce
- [ ] Listou os 4 arquivos-fonte
- [ ] Listou as tabelas (produtos, usuarios, pedidos, itens_pedido)

**Verificar Fase 2:**
- [ ] Relatório segue o template (cabeçalho, Summary, Findings, Total)
- [ ] Cada finding tem arquivo e linha exatos
- [ ] Findings ordenados CRITICAL → LOW
- [ ] Mínimo 5 findings
- [ ] Ao menos 1 CRITICAL ou HIGH
- [ ] Skill parou e pediu confirmação [y/n] ← OBRIGATÓRIO

**Responder "y" para prosseguir para a Fase 3.**

**Verificar Fase 3:**
- [ ] Criou estrutura de pastas MVC (`config/`, `models/`, `controllers/`, `views/`, `middlewares/`)
- [ ] Extraiu configurações hardcoded para `config/settings.py`
- [ ] Aplicação inicia sem erros
- [ ] Endpoints originais respondem

**Salvar o relatório:**
```bash
# Copie o relatório gerado na Fase 2 para:
reports/audit-project-1.md
```

---

## ETAPA 11 — Executar a skill no Projeto 2

```bash
cd ../ecommerce-api-legacy
claude "/refactor-arch"
```

**Verificar Fase 1:**
- [ ] Detectou Node.js + Express
- [ ] Descreveu o domínio (LMS / checkout)
- [ ] Listou os arquivos-fonte

**Verificar Fase 2:**
- [ ] Relatório segue template
- [ ] Mínimo 5 findings
- [ ] Ao menos 1 CRITICAL ou HIGH
- [ ] Skill pausou e pediu confirmação [y/n]

**Responder "y" para prosseguir.**

**Verificar Fase 3:**
- [ ] Estrutura MVC para Node.js criada
- [ ] `app.js` é o entry point limpo
- [ ] `npm start` ou `node app.js` funciona sem erros

**Salvar o relatório:**
```bash
reports/audit-project-2.md
```

---

## ETAPA 12 — Executar a skill no Projeto 3

```bash
cd ../task-manager-api
claude "/refactor-arch"
```

> Este projeto já tem alguma organização de pastas (`models/`, `routes/`, `services/`).  
> A skill deve detectar isso na Fase 1 como "Parcialmente organizada" e ainda encontrar problemas na Fase 2.

**Verificar Fase 1:**
- [ ] Detectou Python + Flask
- [ ] Descreveu o domínio como Task Manager
- [ ] Identificou arquitetura parcialmente organizada

**Verificar Fase 2:**
- [ ] Mínimo 5 findings (mesmo em projeto parcialmente organizado)
- [ ] Ao menos 1 CRITICAL ou HIGH
- [ ] Skill pausou e pediu confirmação

**Responder "y" para prosseguir.**

**Verificar Fase 3:**
- [ ] Melhorou a estrutura existente sem quebrar o que já estava correto
- [ ] Aplicação funciona após refatoração

**Salvar o relatório:**
```bash
reports/audit-project-3.md
```

---

## ETAPA 13 — Iterar se necessário

Se a skill não encontrou problemas suficientes ou a refatoração falhou:

1. Identifique qual arquivo de referência precisa de ajuste
2. Adicione sinais de detecção mais específicos em `02-antipatterns-catalog.md`
3. Adicione padrões de transformação em `05-refactoring-playbook.md`
4. Re-execute a skill no projeto que falhou

É normal precisar de **2 a 4 iterações** até a skill funcionar bem nos 3 projetos.

---

## ETAPA 14 — Completar o README.md

Adicione ao `README.md` da raiz as 4 seções obrigatórias:

**A) Análise Manual** (já feito na Etapa 9)

**B) Construção da Skill:**
- Quais anti-patterns foram incluídos e por quê
- Como a agnóstica de tecnologia foi garantida (heurísticas separadas por linguagem)
- Desafios encontrados e como foram resolvidos

**C) Resultados:**
- Resumo dos 3 relatórios de auditoria
- Tabela comparativa antes/depois para cada projeto
- Checklist de validação preenchido
- Logs ou prints das aplicações rodando após refatoração

**D) Como Executar:**
```markdown
## Pré-requisitos
- Claude Code instalado
- Python 3.x (projetos 1 e 3)
- Node.js (projeto 2)

## Executar a skill

### Projeto 1 — code-smells-project
cd code-smells-project
claude "/refactor-arch"

### Projeto 2 — ecommerce-api-legacy
cd ecommerce-api-legacy
claude "/refactor-arch"

### Projeto 3 — task-manager-api
cd task-manager-api
claude "/refactor-arch"

## Validar resultado
# Python
cd <projeto-refatorado>
pip install -r requirements.txt
python app.py

# Node.js
cd ecommerce-api-legacy
npm install
node src/app.js
```

---

## ETAPA 15 — Commitar e publicar

```bash
# Na raiz do repositório
git add .
git status   # revisar o que vai ser commitado

git commit -m "feat: add refactor-arch skill and refactored projects

- Add SKILL.md with 3-phase architecture audit and refactor flow
- Add 5 reference files: analysis, antipatterns, template, guidelines, playbook
- Refactor code-smells-project to MVC (Python/Flask)
- Refactor ecommerce-api-legacy to MVC (Node.js/Express)
- Refactor task-manager-api to MVC (Python/Flask)
- Add audit reports for all 3 projects"

git push origin main
```

---

## CHECKLIST FINAL

Antes de entregar, confirme:

### Repositório
- [ ] Fork público no GitHub
- [ ] `README.md` com seções A, B, C, D preenchidas
- [ ] `reports/audit-project-1.md` salvo
- [ ] `reports/audit-project-2.md` salvo
- [ ] `reports/audit-project-3.md` salvo
- [ ] Código refatorado dos 3 projetos commitado

### Skill (nos 3 projetos)
- [ ] `SKILL.md` presente
- [ ] `01-project-analysis.md` presente
- [ ] `02-antipatterns-catalog.md` com ≥8 anti-patterns
- [ ] `03-report-template.md` presente
- [ ] `04-mvc-guidelines.md` com estruturas Python e Node.js
- [ ] `05-refactoring-playbook.md` com ≥8 padrões antes/depois

### Critérios de aceite (todos obrigatórios nos 3 projetos)
- [ ] Fase 1 detecta stack corretamente — **3/3 projetos**
- [ ] Fase 2 encontra ≥5 findings — **3/3 projetos**
- [ ] Fase 2 inclui ≥1 CRITICAL ou HIGH — **3/3 projetos**
- [ ] Fase 3 aplicação funciona após refatoração — **3/3 projetos**
