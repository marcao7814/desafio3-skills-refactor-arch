# Guidelines de Arquitetura MVC

Use este guia na Fase 3 para criar a estrutura de destino correta para cada linguagem.

---

## Estrutura Alvo — Python / Flask

```
src/
├── config/
│   ├── settings.py          ← variáveis de ambiente e configuração (sem hardcoded)
│   └── constants.py         ← constantes nomeadas (STATUS_*, ROLE_*, etc.)
├── models/
│   └── <entidade>_model.py  ← acesso a dados, queries SQL, ORM
├── controllers/
│   └── <entidade>_controller.py  ← lógica de negócio, orquestra models
├── views/
│   └── <entidade>_routes.py ← apenas roteamento, extração de params, chamada ao controller
├── middlewares/
│   └── error_handler.py     ← tratamento centralizado de exceções
└── app.py                   ← composition root: cria app, registra blueprints
```

**Entry point mínimo (`app.py`):**
```python
from flask import Flask
from flask_cors import CORS
from config.settings import SECRET_KEY
from views.produto_routes import produto_bp
from views.pedido_routes import pedido_bp
from middlewares.error_handler import register_error_handlers
from database import init_db

def create_app():
    app = Flask(__name__)
    app.config['SECRET_KEY'] = SECRET_KEY
    CORS(app)
    app.register_blueprint(produto_bp, url_prefix='/produtos')
    app.register_blueprint(pedido_bp, url_prefix='/pedidos')
    register_error_handlers(app)
    return app

if __name__ == '__main__':
    app = create_app()
    init_db()
    app.run(debug=True, port=5000)
```

---

## Estrutura Alvo — Node.js / Express

```
src/
├── config/
│   ├── settings.js          ← process.env com defaults seguros
│   └── constants.js         ← STATUS_*, ROLE_*, DISCOUNT_*
├── models/
│   └── <entidade>.model.js  ← acesso a dados, queries SQL
├── controllers/
│   └── <entidade>.controller.js  ← lógica de negócio
├── routes/
│   └── <entidade>.routes.js ← apenas roteamento
├── middlewares/
│   └── errorHandler.js      ← error handling centralizado
└── app.js                   ← entry point
```

**Entry point mínimo (`app.js`):**
```javascript
const express = require('express');
const cors = require('cors');
const { PORT } = require('./config/settings');
const cursoRoutes = require('./routes/curso.routes');
const authRoutes = require('./routes/auth.routes');
const errorHandler = require('./middlewares/errorHandler');

const app = express();
app.use(express.json());
app.use(cors());
app.use('/cursos', cursoRoutes);
app.use('/auth', authRoutes);
app.use(errorHandler); // SEMPRE registrar por último

app.listen(PORT, () => console.log(`API rodando na porta ${PORT}`));
module.exports = app;
```

---

## Responsabilidades por Camada

### Config
- **DEVE conter:** leitura de `os.environ.get()` / `process.env` com valores default seguros
- **NÃO DEVE conter:** lógica de negócio, imports de outros módulos da aplicação

```python
# config/settings.py
import os
SECRET_KEY = os.environ.get('SECRET_KEY', 'dev-only-insecure-default')
DATABASE_URL = os.environ.get('DATABASE_URL', 'sqlite:///app.db')
PORT = int(os.environ.get('PORT', 5000))
```

### Models
- **DEVE conter:** queries SQL parametrizadas, ORM calls, mapeamento de row → dict
- **NÃO DEVE conter:** lógica de negócio, validação de request, decisões condicionais de negócio, `print()`

```python
# models/produto_model.py
def get_produto_by_id(db, produto_id):
    row = db.execute("SELECT * FROM produtos WHERE id = ?", (produto_id,)).fetchone()
    return dict(row) if row else None

def create_produto(db, nome, preco, estoque):
    cursor = db.execute(
        "INSERT INTO produtos (nome, preco, estoque) VALUES (?, ?, ?)",
        (nome, preco, estoque)
    )
    db.commit()
    return cursor.lastrowid
```

### Controllers
- **DEVE conter:** lógica de negócio, validação de dados, orquestração de models, cálculos
- **NÃO DEVE conter:** queries SQL diretas, `request.json`, `jsonify()`, `res.json()`, headers HTTP

```python
# controllers/produto_controller.py
from models.produto_model import get_produto_by_id, create_produto

def listar_produtos(db):
    return get_all_produtos(db)

def buscar_produto(db, produto_id):
    produto = get_produto_by_id(db, produto_id)
    if not produto:
        raise ValueError('Produto não encontrado')
    return produto

def criar_produto(db, nome, preco, estoque):
    if not nome or preco is None:
        raise ValueError('nome e preco são obrigatórios')
    if preco < 0:
        raise ValueError('preco não pode ser negativo')
    return create_produto(db, nome, preco, estoque)
```

### Views / Routes
- **DEVE conter:** definição de rota (path + método HTTP), extração de `request.json` / `req.body`, chamada ao controller, retorno da response
- **NÃO DEVE conter:** lógica de negócio, queries SQL, cálculos, regras de validação complexas

```python
# views/produto_routes.py
from flask import Blueprint, request, jsonify
from controllers.produto_controller import listar_produtos, criar_produto, buscar_produto
from database import get_db

produto_bp = Blueprint('produtos', __name__)

@produto_bp.route('/', methods=['GET'])
def get_produtos():
    return jsonify(listar_produtos(get_db())), 200

@produto_bp.route('/<int:produto_id>', methods=['GET'])
def get_produto(produto_id):
    try:
        return jsonify(buscar_produto(get_db(), produto_id)), 200
    except ValueError as e:
        return jsonify({'erro': str(e)}), 404

@produto_bp.route('/', methods=['POST'])
def post_produto():
    dados = request.json or {}
    try:
        produto_id = criar_produto(get_db(), dados.get('nome'), dados.get('preco'), dados.get('estoque', 0))
        return jsonify({'id': produto_id}), 201
    except ValueError as e:
        return jsonify({'erro': str(e)}), 400
```

### Middlewares
- **DEVE conter:** error handling centralizado, autenticação/autorização, logging
- **NÃO DEVE conter:** lógica de negócio específica de domínio

```python
# middlewares/error_handler.py
from flask import jsonify

def register_error_handlers(app):
    @app.errorhandler(ValueError)
    def handle_value_error(e):
        return jsonify({'erro': str(e)}), 400

    @app.errorhandler(Exception)
    def handle_generic_error(e):
        return jsonify({'erro': 'Erro interno do servidor'}), 500
```

```javascript
// middlewares/errorHandler.js
function errorHandler(err, req, res, next) {
    const status = err.status || 500;
    const message = err.message || 'Erro interno do servidor';
    res.status(status).json({ erro: message });
}
module.exports = errorHandler;
```

---

## Regra de Ouro

> Se você está escrevendo uma query SQL em uma rota, está errado.
> Se você está escrevendo `request.json` em um controller, está errado.
> Se você está escrevendo `jsonify()` em um model, está errado.
