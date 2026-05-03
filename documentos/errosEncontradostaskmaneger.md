# Erros Encontrados Manualmente - task-manager-api

Projeto: `desafio-skills/task-manager-api`
Linguagem: Python
Framework: Flask 3.0.0
Banco: SQLite com SQLAlchemy ORM

---

## CRITICAL

### 1 - CRITICAL
**Arquivo:** `models/user.py` — linhas 29 e 32

```python
def set_password(self, pwd):
    self.password = hashlib.md5(pwd.encode()).hexdigest()

def check_password(self, pwd):
    return self.password == hashlib.md5(pwd.encode()).hexdigest()
```

MD5 usado para hash de senha sem salt. MD5 é um algoritmo de hash criptograficamente quebrado há décadas, não projetado para senhas, trivialmente reversível via rainbow tables e GPU cracking. Sem salt, senhas iguais produzem hashes iguais. Deve-se usar bcrypt, argon2 ou scrypt com salt automático.

---

### 2 - CRITICAL
**Arquivo:** `app.py` — linha 13

```python
app.config['SECRET_KEY'] = 'super-secret-key-123'
```

Chave secreta hardcoded no código-fonte. A `SECRET_KEY` do Flask é usada para assinar sessões e tokens — qualquer pessoa com acesso ao repositório pode forjar sessões autenticadas. Deve ser lida de variável de ambiente (`.env`) e nunca commitada.

---

### 3 - CRITICAL
**Arquivo:** `services/notification_service.py` — linha 10

```python
self.email_password = 'senha123'
```

Credencial de email hardcoded diretamente no código. Senha do servidor SMTP em texto puro na classe — qualquer acesso ao repositório expõe a conta de email. Deve estar em variável de ambiente.

---

### 4 - CRITICAL
**Arquivo:** `routes/user_routes.py` — linha 147

```python
return jsonify({
    'message': 'Login realizado com sucesso',
    'user': user.to_dict(),
    'token': 'fake-jwt-token-' + str(user.id)
}), 200
```

Token de autenticação completamente falso. O sistema possui endpoint de login mas retorna um token fictício não verificável. Qualquer cliente pode forjar o token apenas conhecendo o `user_id`. Não há middleware que valide esse token em nenhum endpoint — o sistema inteiro opera sem autenticação real.

---

### 5 - CRITICAL
**Arquivo:** `models/user.py` — linhas 17 a 25

```python
def to_dict(self):
    return {
        'id': self.id,
        'name': self.name,
        'email': self.email,
        'password': self.password,   # <--- hash da senha exposto
        'role': self.role,
        'active': self.active,
        'created_at': str(self.created_at)
    }
```

Hash da senha incluído na serialização do usuário. Todo endpoint que retorna um usuário (GET `/users`, GET `/users/<id>`, POST `/users`, POST `/login`, GET `/reports/user/<id>`) inclui o campo `password` com o hash MD5. Exposição de hash facilita ataques offline de dicionário.

---

## HIGH

### 1 - HIGH
**Arquivo:** todos os arquivos de rotas — `task_routes.py`, `user_routes.py`, `report_routes.py`

Nenhum endpoint da API possui autenticação ou autorização. Qualquer requisição anônima pode:
- Listar, criar, editar e deletar usuários
- Acessar relatórios com dados de produtividade e estatísticas de todos os usuários
- Alterar role de usuário para `admin` via PUT `/users/<id>`
- Deletar qualquer task ou categoria

O endpoint de login existe mas o token gerado nunca é verificado em nenhuma rota.

---

### 2 - HIGH
**Arquivo:** `routes/task_routes.py` — linhas 41 a 56

```python
for t in tasks:
    # ...
    if t.user_id:
        user = User.query.get(t.user_id)   # query dentro do loop
    if t.category_id:
        cat = Category.query.get(t.category_id)   # query dentro do loop
```

N+1 queries no endpoint `GET /tasks`. Para cada task são executadas até 2 queries adicionais (user + category). Com 100 tasks, isso resulta em até 201 queries no banco. O SQLAlchemy já possui o relacionamento definido via `db.relationship` nos models — basta usar `t.user` e `t.category` com eager loading (`joinedload`).

---

### 3 - HIGH
**Arquivo:** `routes/report_routes.py` — linhas 53 a 67

```python
users = User.query.all()
user_stats = []
for u in users:
    user_tasks = Task.query.filter_by(user_id=u.id).all()   # query dentro do loop
    total = len(user_tasks)
    completed = 0
    for t in user_tasks:
        if t.status == 'done':
            completed = completed + 1
```

N+1 queries no relatório de sumário. Para cada usuário é feita uma query separada de tasks. Pode ser resolvido com uma única query usando `GROUP BY` e `COUNT` no banco, ou com eager loading via SQLAlchemy.

---

### 4 - HIGH
**Arquivo:** `models/task.py` — linhas 50 a 59

```python
def is_overdue(self):
    if self.due_date:
        if self.due_date < datetime.utcnow():
        if self.status != 'done' and self.status != 'cancelled':   # indentação errada
                return True
            else:
                return False
        else:
            return False
    else:
        return False
```

Indentação incorreta no método `is_overdue()` — a segunda condição `if` está no mesmo nível do bloco `if self.due_date`, causando `IndentationError` ou comportamento incorreto. O método nunca é chamado por isso (as rotas duplicam a lógica inline), mas o bug está presente no código do model.

---

### 5 - HIGH
**Arquivo:** `routes/task_routes.py` — linha 61; `routes/report_routes.py` — linha 160; `routes/user_routes.py` — linhas 99, 109

```python
except:
    return jsonify({'error': 'Erro interno'}), 500
```

`except` genérico sem capturar a exceção (`bare except`). Silencia todos os erros incluindo `KeyboardInterrupt`, `SystemExit` e erros de programação. O erro original nunca é logado, impossibilitando diagnóstico. Deve-se usar `except Exception as e` e ao menos logar `str(e)`.

---

### 6 - HIGH
**Arquivo:** `utils/seed.py` — linhas 17, 23, 29

```python
u1.set_password('1234')
u2.set_password('abcd')
u3.set_password('pass')
```

Senhas extremamente fracas no seed. Além de fracas, estão em texto puro no código-fonte. Combinado com o MD5 sem salt, qualquer usuário seedado é trivialmente comprometível. O usuário admin (`u1`) usa senha `'1234'`.

---

### 7 - HIGH
**Arquivo:** `app.py` — linha 15

```python
CORS(app)
```

CORS configurado sem restrição de origins. `CORS(app)` sem parâmetros permite requisições de qualquer domínio (`Access-Control-Allow-Origin: *`). Em produção deve-se especificar `origins=['https://meu-frontend.com']` para limitar acesso.

---

## MEDIUM

### 1 - MEDIUM
**Arquivo:** `app.py` — linha 34

```python
app.run(debug=True, host='0.0.0.0', port=5000)
```

Modo debug ativo com binding em todas as interfaces de rede. `debug=True` expõe o Werkzeug Debugger interativo que permite execução arbitrária de código Python no servidor via navegador. `host='0.0.0.0'` expõe a porta para toda a rede. Em produção deve ser `debug=False` e usar um servidor WSGI (gunicorn/uWSGI).

---

### 2 - MEDIUM
**Arquivos:** `task_routes.py` linhas 30–39, 70–79, 235–236; `user_routes.py` linha 125; `report_routes.py` linhas 34–43

Lógica de verificação de `overdue` duplicada em pelo menos 5 lugares:

```python
if t.due_date:
    if t.due_date < datetime.utcnow():
        if t.status != 'done' and t.status != 'cancelled':
            # overdue = True
```

O model `Task` já possui o método `is_overdue()` para isso, mas nenhuma rota o utiliza. Violação do princípio DRY — qualquer mudança na lógica precisa ser replicada manualmente em todos os pontos.

---

### 3 - MEDIUM
**Arquivo:** `routes/task_routes.py` — linha 14

```python
tasks = Task.query.all()
```

`GET /tasks` retorna todas as tasks sem paginação. Em produção com grandes volumes, isso pode retornar milhares de registros em uma única requisição, sobrecarregando banco e memória. Deve-se implementar paginação com `limit`/`offset` ou cursor.

---

### 4 - MEDIUM
**Arquivo:** `routes/report_routes.py` — blueprint e rotas de categoria

```python
report_bp = Blueprint('reports', __name__)

@report_bp.route('/categories', methods=['GET'])
@report_bp.route('/categories', methods=['POST'])
@report_bp.route('/categories/<int:cat_id>', methods=['PUT'])
@report_bp.route('/categories/<int:cat_id>', methods=['DELETE'])
```

CRUD de categorias implementado dentro da blueprint de relatórios. Viola separação de responsabilidades — categorias não são relatórios. Deveria existir uma `category_bp` separada.

---

### 5 - MEDIUM
**Arquivo:** `services/notification_service.py` — linha 6

```python
self.notifications = []
```

Histórico de notificações armazenado em lista Python em memória. Toda vez que a aplicação reinicia, o histórico é perdido. Com múltiplos workers (gunicorn), cada processo tem sua própria lista — notificações de um processo são invisíveis aos outros.

---

### 6 - MEDIUM
**Arquivo:** `routes/user_routes.py` — linha 61

```python
if len(password) < 4:
    return jsonify({'error': 'Senha deve ter no mínimo 4 caracteres'}), 400
```

Política de senha mínima de 4 caracteres — extremamente fraca. Combinado com MD5 sem salt, senhas como `"1234"`, `"abcd"` e `"pass"` (usadas no seed) são aceitas sem nenhuma restrição adicional de complexidade.

---

### 7 - MEDIUM
**Arquivo:** `utils/helpers.py` — linhas 26 a 30

```python
def log_action(action, details=None):
    timestamp = datetime.utcnow()
    print(f"[{timestamp}] ACTION: {action}")
    if details:
        print(f"  DETAILS: {details}")
```

Sistema de log usando `print()`. Em produção `print()` vai para stdout sem controle de nível, sem formatação estruturada e sem destino configurável. Deve-se usar o módulo `logging` do Python com níveis (INFO, WARNING, ERROR) e handlers.

---

## LOW

### 1 - LOW
**Arquivos:** `app.py` linha 7; `task_routes.py` linha 7; `user_routes.py` linha 6; `utils/helpers.py` linhas 3–6

Imports não utilizados espalhados por vários arquivos:
- `app.py`: `os`, `sys`, `json`, `datetime` (datetime usado apenas em health)
- `task_routes.py`: `json`, `os`, `sys`, `time`
- `user_routes.py`: `hashlib`, `json`
- `helpers.py`: `os`, `sys`, `math`

Aumentam o tempo de inicialização e criam dependências implícitas desnecessárias.

---

### 2 - LOW
**Arquivo:** `models/user.py` — linhas 34 a 37; `models/task.py` — linhas 38 a 43

```python
def is_admin(self):
    if self.role == 'admin':
        return True
    else:
        return False

def validate_status(self, new_status):
    valid = ['pending', 'in_progress', 'done', 'cancelled']
    if new_status in valid:
        return True
    else:
        return False
```

Anti-padrão `if x: return True else: return False`. Pode ser simplificado para `return self.role == 'admin'` e `return new_status in valid` — mais legível e idiomático em Python.

---

### 3 - LOW
**Arquivo:** `utils/helpers.py` — linhas 9 a 11

```python
def format_date(date_obj):
    if date_obj:
        return str(date_obj)
    return None
```

Função helper que apenas chama `str()`. Não adiciona valor — poderia ser substituída por `str(date_obj) if date_obj else None` inline. Funções triviais sem comportamento específico aumentam a superfície de código sem benefício.

---

### 4 - LOW
**Arquivo:** `utils/helpers.py` — linhas 23 a 25

```python
def generate_id():
    import uuid
    return str(uuid.uuid4())
```

Import dentro de função. `import uuid` deve estar no topo do módulo. Import interno é executado toda vez que a função é chamada (embora Python faça cache, é considerado má prática e dificulta análise estática).

---

### 5 - LOW
**Arquivo:** `routes/task_routes.py` — linhas 17 a 28 vs. `models/task.py` — linhas 23 a 36

O `GET /tasks` monta manualmente o dicionário de cada task duplicando exatamente o que `task.to_dict()` já faz. A lógica de serialização está em dois lugares — qualquer campo novo no model precisa ser adicionado em ambos.

---

## RESUMO

| Severidade | Quantidade |
|-----------|------------|
| CRITICAL  | 5          |
| HIGH      | 7          |
| MEDIUM    | 7          |
| LOW       | 5          |
| **Total** | **24**     |

**Principais categorias de problemas:**
- Segurança: MD5 sem salt para senhas, SECRET_KEY hardcoded, credencial SMTP exposta, token fake, senha exposta no `to_dict()`
- Autenticação/Autorização: zero proteção nos endpoints, login sem JWT real
- Performance: N+1 queries em listagem de tasks e relatório de usuários
- Qualidade de código: lógica `overdue` duplicada em 5 lugares, bare except, serialização duplicada
- Configuração: debug=True + 0.0.0.0, CORS aberto, política de senha fraca
