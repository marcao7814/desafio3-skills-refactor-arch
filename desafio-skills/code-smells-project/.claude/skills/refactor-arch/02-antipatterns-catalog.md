# Catálogo de Anti-Patterns

Use este catálogo na Fase 2 para identificar problemas no código. Para cada sinal encontrado, registre o arquivo e as linhas exatas.

---

## CRITICAL

### C1 — God Class / God File
**Descrição:** Um único arquivo ou classe concentra responsabilidades de múltiplos domínios — queries SQL, lógica de negócio, validação e formatação coexistem no mesmo lugar.

**Sinais de detecção:**
- Arquivo com >150 linhas contendo funções de domínios diferentes (ex: produtos + pedidos + usuários no mesmo arquivo)
- Classe com >8 métodos públicos de domínios distintos
- Arquivo chamado `GodManager`, `AppManager`, `MainController` ou similar

**Exemplos:**
```python
# Python: models.py com funções de múltiplos domínios
def criar_produto(...): ...    # domínio produto
def fazer_pedido(...): ...     # domínio pedido
def autenticar_usuario(...):...# domínio usuario — tudo no mesmo arquivo
```
```javascript
// Node.js: GodManager.js com métodos de todos os domínios
class GodManager {
    login() {...}        // autenticação
    listarCursos() {...} // cursos
    processarCheckout(){...} // pagamento — tudo na mesma classe
}
```

---

### C2 — Hardcoded Credentials / Secrets
**Descrição:** Segredos, chaves e senhas escritos diretamente no código-fonte.

**Sinais de detecção:**
- `SECRET_KEY = "..."` com valor literal
- `PASSWORD = "..."`, `API_KEY = "..."`, `TOKEN = "..."` com valor hardcoded
- Connection string com usuário/senha inline
- Regex Python/JS: `(SECRET|PASSWORD|KEY|TOKEN)\s*[=:]\s*["'][^"']{4,}["']`

**Exemplos:**
```python
app.config['SECRET_KEY'] = 'minha-chave-super-secreta-123'
ADMIN_PASSWORD = 'admin@123'
```
```javascript
const JWT_SECRET = 'super-secret-jwt-key-hardcoded-123';
const ADMIN_PASSWORD = 'admin@123';
```

---

### C3 — SQL Injection
**Descrição:** Query SQL construída com concatenação de strings ou interpolação direta de variáveis externas.

**Sinais de detecção:**
- f-string Python em query: `f"SELECT * FROM ... WHERE id={var}"`
- Concatenação: `"SELECT * FROM " + tabela + " WHERE id=" + str(id)`
- Template literal JS em query: `` `SELECT * FROM users WHERE id=${req.params.id}` ``
- `.format()` em query SQL Python

**Exemplos:**
```python
query = f"SELECT * FROM produtos WHERE id={user_id}"       # CRÍTICO
query = "DELETE FROM produtos WHERE id=" + str(product_id) # CRÍTICO
```
```javascript
const query = `SELECT * FROM cursos WHERE id = ${id}`;     // CRÍTICO
```

---

## HIGH

### H1 — Lógica de Negócio no Controller/Route
**Descrição:** Handlers de rota contêm regras de negócio que deveriam estar em uma camada de serviço/controller separada.

**Sinais de detecção:**
- Função de rota com >25 linhas de código
- Query SQL diretamente dentro de `@app.route(...)` ou `router.get/post/put/delete(...)`
- Múltiplos `if/else` com regras de negócio dentro do handler de rota
- Cálculos de total, desconto ou validações complexas dentro da rota

**Exemplos:**
```python
@app.route('/checkout', methods=['POST'])
def checkout():
    # 50+ linhas de lógica de negócio aqui
    total = 0
    for item in itens:
        produto = db.execute(...)  # query dentro da rota
        if produto['estoque'] < item['quantidade']:  # regra de negócio
            ...
```

---

### H2 — Forte Acoplamento / Sem Injeção de Dependência
**Descrição:** Dependências concretas instanciadas dentro das funções de negócio, impedindo testes e substituição.

**Sinais de detecção:**
- `conn = sqlite3.connect(...)` ou `db = new Database(...)` dentro de funções de negócio
- Import direto de módulos concretos sem abstração
- Instância de banco criada dentro de cada função (não injetada)

**Exemplos:**
```python
def fazer_pedido(usuario_id, itens):
    conn = sqlite3.connect('db.sqlite3')  # acoplamento direto
    ...
```

---

### H3 — Estado Global Mutável
**Descrição:** Variáveis globais modificadas por múltiplas funções, causando comportamento imprevisível em ambientes concorrentes.

**Sinais de detecção:**
- Uso de `global` keyword em Python dentro de funções de rota
- Dicionários ou listas globais modificados entre requests
- Instância única compartilhada com estado (`currentUser`, `sessionTokens` como atributos de instância singleton)

**Exemplos:**
```python
sessao_atual = {}  # global mutável

def handle_login():
    global sessao_atual
    sessao_atual = usuario  # modifica estado global
```
```javascript
class GodManager {
    constructor() {
        this.currentUser = null;    // estado mutável no singleton
        this.sessionTokens = {};
    }
}
module.exports = new GodManager(); // singleton exportado
```

---

## MEDIUM

### M1 — Query N+1
**Descrição:** Uma query principal retorna N registros, e para cada um é feita uma query adicional dentro de um loop.

**Sinais de detecção:**
- `db.execute(...)` ou `db.prepare(...).get(...)` dentro de loop `for`
- ORM query dentro de `for ... in lista_de_registros`
- Busca de entidade relacionada (ex: buscar produto para cada item do pedido) dentro de loop

**Exemplos:**
```python
pedidos = db.execute("SELECT * FROM pedidos").fetchall()
for pedido in pedidos:
    itens = db.execute("SELECT * FROM itens WHERE pedido_id=?", (pedido['id'],)) # N+1
```
```javascript
for (const m of matriculas) {
    const curso = db.prepare('SELECT * FROM cursos WHERE id = ?').get(m.curso_id); // N+1
}
```

---

### M2 — Validação Ausente nas Rotas
**Descrição:** Dados de entrada aceitos sem verificação de presença, tipo ou formato.

**Sinais de detecção:**
- `dados.get('campo')` ou `req.body.campo` usado diretamente sem verificar `None`/`undefined`
- Ausência de qualquer schema de validação (sem marshmallow, pydantic, joi, zod, express-validator)
- Campos obrigatórios passados direto para INSERT/UPDATE sem verificação

**Exemplos:**
```python
def handle_criar_produto():
    dados = request.json
    nome = dados.get('nome')   # pode ser None
    preco = dados.get('preco') # pode ser None ou negativo
    criar_produto(nome, preco) # sem validação
```

---

### M3 — Error Handling Duplicado / Ausente
**Descrição:** Tratamento de erros repetido identicamente em cada rota, ou ausência de error handling em rotas críticas.

**Sinais de detecção:**
- Bloco `try/except` ou `try/catch` com o mesmo conteúdo em 3 ou mais rotas
- `res.status(500).json({ erro: err.message })` repetido em múltiplas rotas
- Rotas sem nenhum tratamento de erro que poderiam lançar exceções

---

### M4 — APIs Deprecated
**Descrição:** Uso de APIs obsoletas que foram removidas ou marcadas como deprecated.

**Sinais de detecção Python:**
- `from flask.ext.*` — removido no Flask 1.0+
- `import distutils` — deprecated Python 3.10+, removido 3.12
- `from distutils import ...`

**Sinais de detecção Node.js:**
- `new Buffer(...)` — deprecated desde Node.js 6, substituir por `Buffer.from(...)`
- `require('url').parse(...)` — deprecated, substituir por `new URL(...)`
- `res.send(404)` / `res.send(200)` / `res.send(500)` — deprecated Express 4, usar `res.status(N).send()`
- `res.sendfile(...)` — deprecated, usar `res.sendFile(...)`

**Regex de busca JS:** `new Buffer\(`, `require\(['"]url['"]\)\.parse`, `res\.send\(\d{3}\)`
**Regex de busca Python:** `from flask\.ext`, `import distutils`, `from distutils`

---

## LOW

### L1 — Magic Numbers
**Descrição:** Literais numéricos sem contexto espalhados pelo código, sem constantes nomeadas.

**Sinais de detecção:**
- `if status == 1` / `if status == 2` / `if status == 3` sem constante explicando o significado
- `if role == 2` sem constante `ROLE_ADMIN = 2`
- `* 0.15` / `* 0.10` sem constante para percentual
- `time.sleep(60)`, `limit = 100`, `MAX = 500` sem nome explicativo

**Exemplos:**
```python
if usuario['role'] == 2:      # O que significa role 2?
    desconto = preco * 0.15   # O que é 0.15?
if status == 3:               # O que é status 3?
    enviar_email()
```

---

### L2 — Nomenclatura Ruim
**Descrição:** Nomes de variáveis, funções ou parâmetros que não comunicam intenção.

**Sinais de detecção:**
- Variáveis de 1-2 letras fora de loops curtos: `x`, `d`, `tmp`, `t`, `p`, `s`
- Nomes genéricos sem contexto: `data`, `info`, `result`, `obj`, `item`, `val`
- Parâmetros com abreviações: `usr`, `prd`, `req_data`
- Mistura de idiomas em nomes de função no mesmo arquivo (ex: `criarProduto` ao lado de `deleteProduct`)

---

### L3 — Código Morto / Comentado
**Descrição:** Código comentado por longos blocos ou funções definidas que nunca são chamadas.

**Sinais de detecção:**
- 5 ou mais linhas consecutivas comentadas com `#` (Python) ou `//` (JS)
- Funções definidas mas sem nenhuma chamada no código-fonte
- Blocos `/* ... */` de código antigo comentado (JS)

**Exemplos:**
```python
# def enviar_email(para, assunto, corpo):
#     transporter = ...
#     transporter.sendMail({...})
#     ...mais 10 linhas comentadas
```
