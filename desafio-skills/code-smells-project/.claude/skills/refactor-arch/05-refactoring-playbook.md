# Playbook de Refatoração

Para cada anti-pattern identificado na Fase 2, aplique o padrão de transformação correspondente.

---

## Padrão 1 — Extrair Configuração Hardcoded

**Aplica-se a:** C2 — Hardcoded Credentials / Secrets

**Antes (Python):**
```python
app.config['SECRET_KEY'] = 'minha-chave-super-secreta-123'
DATABASE = 'sqlite:///db.sqlite3'
PORT = 5000
```

**Depois:**
```python
# config/settings.py
import os
SECRET_KEY = os.environ.get('SECRET_KEY', 'dev-only-insecure-key')
DATABASE_URL = os.environ.get('DATABASE_URL', 'sqlite:///app.db')
PORT = int(os.environ.get('PORT', 5000))
```

**Antes (Node.js):**
```javascript
const JWT_SECRET = 'super-secret-jwt-key-hardcoded-123';
const PORT = 3000;
const DB_PATH = './lms.db';
```

**Depois:**
```javascript
// config/settings.js
module.exports = {
    JWT_SECRET: process.env.JWT_SECRET || 'dev-only-insecure-key',
    PORT: parseInt(process.env.PORT) || 3000,
    DB_PATH: process.env.DB_PATH || './lms.db',
};
```

Criar também `.env.example` com as variáveis sem valores reais:
```
SECRET_KEY=your-secret-key-here
DATABASE_URL=sqlite:///app.db
PORT=5000
```

---

## Padrão 2 — Quebrar God Class por Domínio

**Aplica-se a:** C1 — God Class / God File

**Antes:**
```python
# models.py (200+ linhas — múltiplos domínios)
def criar_produto(nome, preco, estoque): ...
def buscar_produto(id): ...
def fazer_pedido(usuario_id, itens): ...
def autenticar_usuario(email, senha): ...
def listar_usuarios(): ...
```

**Depois:**
```python
# models/produto_model.py
def get_all_produtos(db): ...
def get_produto_by_id(db, produto_id): ...
def create_produto(db, nome, preco, estoque): ...

# models/pedido_model.py
def create_pedido(db, usuario_id, total): ...
def get_pedidos_by_usuario(db, usuario_id): ...

# models/usuario_model.py
def get_usuario_by_email(db, email): ...
def create_usuario(db, nome, email, senha): ...
```

**Node.js equivalente:**
```javascript
// Antes: GodManager.js (400+ linhas)
// Depois:
// models/usuario.model.js — apenas queries de usuario
// models/curso.model.js   — apenas queries de curso
// models/pagamento.model.js — apenas queries de pagamento
```

---

## Padrão 3 — Corrigir SQL Injection

**Aplica-se a:** C3 — SQL Injection

**Antes (Python — f-string):**
```python
produto = db.execute(f'SELECT * FROM produtos WHERE id={id}').fetchone()
db.execute(f'DELETE FROM produtos WHERE id={id}')
```

**Depois:**
```python
produto = db.execute('SELECT * FROM produtos WHERE id=?', (id,)).fetchone()
db.execute('DELETE FROM produtos WHERE id=?', (id,))
```

**Antes (Python — concatenação):**
```python
query = "SELECT * FROM usuarios WHERE email='" + email + "'"
```

**Depois:**
```python
query = "SELECT * FROM usuarios WHERE email=?"
usuario = db.execute(query, (email,)).fetchone()
```

**Antes (Node.js — template literal):**
```javascript
const curso = db.prepare(`SELECT * FROM cursos WHERE id = ${id}`).get();
```

**Depois:**
```javascript
const curso = db.prepare('SELECT * FROM cursos WHERE id = ?').get(id);
```

---

## Padrão 4 — Extrair Lógica de Negócio para Controller

**Aplica-se a:** H1 — Lógica de Negócio no Controller/Route

**Antes (Python — lógica pesada na rota):**
```python
@app.route('/pedidos', methods=['POST'])
def criar_pedido():
    dados = request.json
    usuario_id = dados.get('usuario_id')
    itens = dados.get('itens', [])
    total = 0
    for item in itens:
        produto = db.execute('SELECT * FROM produtos WHERE id=?', (item['produto_id'],)).fetchone()
        if produto['estoque'] < item['quantidade']:
            return jsonify({'erro': 'Sem estoque'}), 400
        total += produto['preco'] * item['quantidade']
    # ... mais 20 linhas de lógica
```

**Depois:**
```python
# controllers/pedido_controller.py
from models.produto_model import get_produto_by_id
from models.pedido_model import create_pedido, add_item_pedido

def processar_pedido(db, usuario_id, itens):
    if not itens:
        raise ValueError('Itens são obrigatórios')
    total = 0
    for item in itens:
        produto = get_produto_by_id(db, item['produto_id'])
        if not produto:
            raise ValueError(f"Produto {item['produto_id']} não encontrado")
        if produto['estoque'] < item['quantidade']:
            raise ValueError(f"Estoque insuficiente para {produto['nome']}")
        total += produto['preco'] * item['quantidade']
    pedido_id = create_pedido(db, usuario_id, total)
    for item in itens:
        add_item_pedido(db, pedido_id, item)
    return pedido_id

# views/pedido_routes.py
@pedido_bp.route('/', methods=['POST'])
def post_pedido():
    dados = request.json or {}
    try:
        pedido_id = processar_pedido(get_db(), dados.get('usuario_id'), dados.get('itens', []))
        return jsonify({'pedido_id': pedido_id}), 201
    except ValueError as e:
        return jsonify({'erro': str(e)}), 400
```

**Node.js equivalente:**
```javascript
// controllers/checkout.controller.js
async function processarCheckout(db, usuarioId, cursoId, metodoPagamento) {
    const curso = getCursoById(db, cursoId);
    if (!curso) throw Object.assign(new Error('Curso não encontrado'), { status: 404 });
    const valor = calcularValor(db, usuarioId, curso.preco);
    const pagamento = registrarPagamento(db, usuarioId, cursoId, valor, metodoPagamento);
    if (pagamento.status === 'aprovado') {
        matricularUsuario(db, usuarioId, cursoId);
    }
    return pagamento;
}

// routes/checkout.routes.js
router.post('/checkout', async (req, res, next) => {
    try {
        const resultado = await processarCheckout(db, req.body.usuario_id, req.body.curso_id, req.body.metodo_pagamento);
        res.json(resultado);
    } catch (err) { next(err); }
});
```

---

## Padrão 5 — Centralizar Error Handling

**Aplica-se a:** M3 — Error Handling Duplicado

**Antes (Node.js — repetido em cada rota):**
```javascript
app.post('/checkout', async (req, res) => {
    try { ... }
    catch (err) { res.status(500).json({ erro: err.message }); }
});
app.get('/cursos', async (req, res) => {
    try { ... }
    catch (err) { res.status(500).json({ erro: err.message }); }
});
```

**Depois:**
```javascript
// middlewares/errorHandler.js
function errorHandler(err, req, res, next) {
    const status = err.status || 500;
    res.status(status).json({ erro: err.message || 'Erro interno' });
}
module.exports = errorHandler;

// app.js — registrar por último
app.use(errorHandler);

// rotas — apenas propagar com next()
router.post('/checkout', async (req, res, next) => {
    try { ... }
    catch (err) { next(err); }
});
```

**Python equivalente:**
```python
# middlewares/error_handler.py
def register_error_handlers(app):
    @app.errorhandler(ValueError)
    def handle_value_error(e):
        return jsonify({'erro': str(e)}), 400

    @app.errorhandler(404)
    def handle_not_found(e):
        return jsonify({'erro': 'Recurso não encontrado'}), 404

    @app.errorhandler(Exception)
    def handle_generic(e):
        return jsonify({'erro': 'Erro interno do servidor'}), 500
```

---

## Padrão 6 — Eliminar Query N+1

**Aplica-se a:** M1 — Query N+1

**Antes (Python):**
```python
pedidos = db.execute("SELECT * FROM pedidos WHERE usuario_id=?", (usuario_id,)).fetchall()
result = []
for pedido in pedidos:
    itens = db.execute("SELECT * FROM itens WHERE pedido_id=?", (pedido['id'],)).fetchall()
    result.append({**dict(pedido), 'itens': [dict(i) for i in itens]})
```

**Depois:**
```python
rows = db.execute("""
    SELECT p.id, p.total, p.status,
           i.produto_id, i.quantidade, i.preco as item_preco
    FROM pedidos p
    LEFT JOIN itens_pedido i ON i.pedido_id = p.id
    WHERE p.usuario_id = ?
""", (usuario_id,)).fetchall()

pedidos = {}
for row in rows:
    pid = row['id']
    if pid not in pedidos:
        pedidos[pid] = {'id': pid, 'total': row['total'], 'status': row['status'], 'itens': []}
    if row['produto_id']:
        pedidos[pid]['itens'].append({'produto_id': row['produto_id'], 'quantidade': row['quantidade']})
return list(pedidos.values())
```

**Node.js equivalente:**
```javascript
// Antes: query para cada matrícula dentro do loop
// Depois: JOIN único
const rows = db.prepare(`
    SELECT m.*, c.titulo, c.preco as curso_preco
    FROM matriculas m
    JOIN cursos c ON c.id = m.curso_id
    WHERE m.usuario_id = ?
`).all(usuarioId);
```

---

## Padrão 7 — Substituir Magic Numbers por Constantes

**Aplica-se a:** L1 — Magic Numbers

**Antes:**
```python
if usuario['role'] == 2:
    desconto = preco * 0.15
if status == 3:
    enviar_email_confirmacao()
if progresso == 100:
    emitir_certificado()
```

**Depois:**
```python
# config/constants.py
ROLE_ADMIN = 2
ROLE_PROFESSOR = 3
ROLE_ALUNO = 1

STATUS_PEDIDO_PENDENTE = 1
STATUS_PEDIDO_CONFIRMADO = 2
STATUS_PEDIDO_ENVIADO = 3
STATUS_PEDIDO_ENTREGUE = 4

DESCONTO_ADMIN = 0.15
DESCONTO_PROFESSOR = 0.10
PROGRESSO_COMPLETO = 100

# uso
from config.constants import ROLE_ADMIN, STATUS_PEDIDO_ENVIADO, DESCONTO_ADMIN, PROGRESSO_COMPLETO

if usuario['role'] == ROLE_ADMIN:
    desconto = preco * DESCONTO_ADMIN
if status == STATUS_PEDIDO_ENVIADO:
    enviar_email_confirmacao()
if progresso == PROGRESSO_COMPLETO:
    emitir_certificado()
```

**Node.js equivalente:**
```javascript
// config/constants.js
module.exports = {
    ROLE_ADMIN: 2,
    ROLE_PROFESSOR: 3,
    STATUS_PENDENTE: 'pendente',
    STATUS_APROVADO: 'aprovado',
    DESCONTO_ADMIN: 0.15,
    PROGRESSO_COMPLETO: 100,
};
```

---

## Padrão 8 — Corrigir APIs Deprecated (Node.js)

**Aplica-se a:** M4 — APIs Deprecated

**Antes:**
```javascript
// new Buffer() — deprecated Node.js 6
const token = new Buffer(`${id}:${Date.now()}`).toString('base64');
const decoded = new Buffer(token, 'base64').toString();

// require('url').parse — deprecated
const parsed = require('url').parse(req.url);

// res.send(statusCode) — deprecated Express 4
return res.send(401);
return res.send(404);
```

**Depois:**
```javascript
// Buffer.from() — correto
const token = Buffer.from(`${id}:${Date.now()}`).toString('base64');
const decoded = Buffer.from(token, 'base64').toString();

// new URL() — correto
const parsed = new URL(req.url, `http://${req.headers.host}`);

// res.status().send() — correto Express 4
return res.status(401).json({ erro: 'Não autorizado' });
return res.status(404).json({ erro: 'Não encontrado' });
```

---

## Padrão 9 — Adicionar Validação de Entrada

**Aplica-se a:** M2 — Validação Ausente nas Rotas

**Antes:**
```python
def handle_criar_produto():
    dados = request.json
    nome = dados.get('nome')
    preco = dados.get('preco')
    criar_produto(nome, preco)  # nome pode ser None, preco pode ser negativo
```

**Depois:**
```python
def criar_produto(db, nome, preco, estoque=0):
    # validação no controller
    if not nome or not isinstance(nome, str):
        raise ValueError('nome é obrigatório e deve ser texto')
    if preco is None or not isinstance(preco, (int, float)):
        raise ValueError('preco é obrigatório e deve ser número')
    if preco < 0:
        raise ValueError('preco não pode ser negativo')
    if estoque < 0:
        raise ValueError('estoque não pode ser negativo')
    return create_produto(db, nome, float(preco), int(estoque))
```

---

## Padrão 10 — Eliminar Estado Global Mutável

**Aplica-se a:** H3 — Estado Global Mutável

**Antes:**
```python
sessao_atual = {}  # global mutável

def handle_login():
    global sessao_atual
    sessao_atual = autenticar_usuario(email, senha)
```

```javascript
class GodManager {
    constructor() {
        this.currentUser = null;     // estado compartilhado entre requests
        this.sessionTokens = {};
    }
}
module.exports = new GodManager(); // singleton com estado
```

**Depois (Python — sem estado global):**
```python
# Usar request context ou retornar dados diretamente
def handle_login():
    dados = request.json or {}
    usuario = autenticar_usuario(get_db(), dados.get('email'), dados.get('senha'))
    if not usuario:
        return jsonify({'erro': 'Credenciais inválidas'}), 401
    # token gerado e retornado — sem armazenar estado global
    token = gerar_token(usuario['id'])
    return jsonify({'token': token, 'usuario': usuario}), 200
```

**Depois (Node.js — separar estado da lógica):**
```javascript
// Não exportar instância com estado — exportar funções puras ou classe sem singleton
// auth.controller.js
function login(db, email, senha) {
    const usuario = db.prepare('SELECT * FROM usuarios WHERE email=? AND senha=?').get(email, senha);
    if (!usuario) throw Object.assign(new Error('Credenciais inválidas'), { status: 401 });
    const token = Buffer.from(`${usuario.id}:${Date.now()}`).toString('base64');
    return { token, usuario: { id: usuario.id, nome: usuario.nome } };
}
module.exports = { login }; // funções puras, sem estado
```
