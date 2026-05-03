# Erros Encontrados Manualmente - ecommerce-api-legacy

Projeto: `desafio-skills/ecommerce-api-legacy`
Linguagem: Node.js / JavaScript
Framework: Express.js
Banco: SQLite3 (em memória)

---

## CRITICAL

### 1 - CRITICAL
**Arquivo:** `src/utils.js` — linhas 3 e 4

```javascript
dbPass: "senha_super_secreta_prod_123",
paymentGatewayKey: "pk_live_1234567890abcdef",
```

Credenciais de produção hardcoded diretamente no código-fonte. Senha do banco e chave de gateway de pagamento expostas — qualquer pessoa com acesso ao repositório tem acesso total às credenciais de produção. Deveriam estar em variáveis de ambiente (`.env`).

---

### 2 - CRITICAL
**Arquivo:** `src/utils.js` — linhas 17 a 23

```javascript
function badCrypto(pwd) {
    let hash = "";
    for(let i = 0; i < 10000; i++) {
        hash += Buffer.from(pwd).toString('base64').substring(0, 2);
    }
    return hash.substring(0, 10);
}
```

Algoritmo de criptografia completamente inseguro. A função `badCrypto` aplica base64 (codificação, não hash) e trunca para 10 caracteres. Base64 é reversível — qualquer senha pode ser recuperada trivialmente. Deve-se usar bcrypt, argon2 ou scrypt com salt.

---

### 3 - CRITICAL
**Arquivo:** `src/AppManager.js` — linha 18

```javascript
this.db.run("INSERT INTO users (name, email, pass) VALUES ('Leonan', 'leonan@fullcycle.com.br', '123')");
```

Senha `'123'` armazenada em texto puro no seed do banco. Além de expor a senha de um usuário, demonstra que o sistema não aplica hashing na persistência de senhas — violação direta de boas práticas de segurança.

---

### 4 - CRITICAL
**Arquivo:** `src/AppManager.js` — linha 44

```javascript
console.log(`Processando cartão ${cc} na chave ${config.paymentGatewayKey}`);
```

Número completo do cartão de crédito e chave de API do gateway de pagamento sendo logados no console. Dados de cartão nunca devem aparecer em logs — viola PCI-DSS e expõe informações financeiras sensíveis em qualquer sistema de log centralizado.

---

### 5 - CRITICAL
**Arquivo:** `src/AppManager.js` — linha 45

```javascript
let status = cc.startsWith("4") ? "PAID" : "DENIED";
```

Lógica de aprovação de pagamento completamente falsa. Qualquer cartão iniciado com "4" é aprovado sem nenhuma integração real com gateway. Um atacante pode forçar aprovação enviando qualquer número começando com "4". Não há integração real de pagamento.

---

### 6 - CRITICAL
**Arquivo:** `src/AppManager.js` — linha 66

```javascript
let hash = badCrypto(p || "123456");
```

Senha padrão `"123456"` usada quando nenhuma senha é fornecida no checkout. Combinado com o `badCrypto` inseguro, usuários criados sem senha ficam com credencial trivialmente adivinháveis e reversíveis.

---

## HIGH

### 1 - HIGH
**Arquivo:** `src/AppManager.js` — linha 78

```javascript
app.get('/api/admin/financial-report', (req, res) => {
```

Endpoint administrativo completamente sem autenticação ou autorização. Qualquer pessoa que conheça a URL pode acessar o relatório financeiro completo com dados de alunos, receita por curso e status de pagamentos — exposição total de dados financeiros e pessoais.

---

### 2 - HIGH
**Arquivo:** `src/AppManager.js` — linhas 37 a 76 (callback hell)

```javascript
this.db.get("SELECT * FROM courses WHERE id = ? ...", (err, course) => {
    this.db.get("SELECT id FROM users WHERE email = ?", (err, user) => {
        this.db.run("INSERT INTO enrollments ...", function(err) {
            self.db.run("INSERT INTO payments ...", function(err) {
                self.db.run("INSERT INTO audit_logs ...", (err) => {
                    // ...
                });
            });
        });
    });
});
```

Cinco níveis de callbacks aninhados (Callback Hell / Pyramid of Doom). Código extremamente difícil de manter, testar e depurar. Erros em callbacks internos são silenciados. Deve-se usar Promises ou async/await.

---

### 3 - HIGH
**Arquivo:** `src/AppManager.js` — linhas 126 a 131

```javascript
app.delete('/api/users/:id', (req, res) => {
    let id = req.params.id;
    this.db.run("DELETE FROM users WHERE id = ?", [id], (err) => {
        res.send("Usuário deletado, mas as matrículas e pagamentos ficaram sujos no banco.");
    });
});
```

Deleção de usuário sem cascade. Matrículas e pagamentos relacionados ao usuário permanecem no banco com `user_id` órfão — corrupção de integridade referencial. O próprio código admite o problema no texto da resposta. Deve-se deletar registros dependentes ou usar soft delete.

---

### 4 - HIGH
**Arquivo:** `src/AppManager.js` — linhas 29 a 34

```javascript
let u = req.body.usr;
let e = req.body.eml;
let p = req.body.pwd;
let cid = req.body.c_id;
let cc = req.body.card;
```

Nomes de variáveis completamente abreviados e sem semântica (`u`, `e`, `p`, `cid`, `cc`). Dificulta leitura, manutenção e revisão de segurança. Além disso, não há validação de formato para nenhum dos campos (email, número de cartão, ID de curso).

---

### 5 - HIGH
**Arquivo:** `src/app.js` e `src/server.js` — arquivos duplicados

Os dois arquivos têm conteúdo **idêntico** (17/18 linhas). Manter dois entry points com o mesmo código gera confusão sobre qual é o real ponto de entrada, dificulta manutenção e pode causar comportamento inesperado. Um deve ser removido.

---

### 6 - HIGH
**Arquivo:** `src/AppManager.js` — linhas 56 a 60

```javascript
self.db.run("INSERT INTO audit_logs ...", [`Checkout curso ${cid} por ${userId}`], (err) => {
    logAndCache(`last_checkout_${userId}`, course.title);
    res.status(200).json({ msg: "Sucesso", enrollment_id: enrId });
});
```

Erro no INSERT de `audit_logs` é completamente ignorado (o parâmetro `err` não é verificado). Falhas de auditoria passam silenciosamente — o sistema perde rastreabilidade de operações críticas sem nenhum alerta.

---

## MEDIUM

### 1 - MEDIUM
**Arquivo:** `src/AppManager.js` — linha 26

```javascript
const self = this;
```

Uso inconsistente de `self` e `this` no mesmo método. Em alguns callbacks usa `self.db`, em outros `this.db`. Isso indica falta de padronização e pode causar bugs sutis se o contexto de `this` mudar. Com arrow functions, `self` é desnecessário.

---

### 2 - MEDIUM
**Arquivo:** `src/utils.js` — linhas 9 e 10

```javascript
let globalCache = {};
let totalRevenue = 0;
```

Estado global mutável compartilhado entre requisições. Em ambiente com múltiplas requisições concorrentes, `globalCache` pode vazar dados de um usuário para outro. `totalRevenue` é exportado mas nunca atualizado — variável morta que confunde o leitor.

---

### 3 - MEDIUM
**Arquivo:** `src/AppManager.js` — linha 80

```javascript
this.db.all("SELECT * FROM courses", [], (err, courses) => {
```

Sem paginação nem limite de registros. Em produção com milhares de cursos, matrículas e usuários, as queries sem `LIMIT` podem retornar volumes massivos de dados, degradando a performance ou causando timeout.

---

### 4 - MEDIUM
**Arquivo:** `src/AppManager.js` — linhas 12 a 16 (criação das tabelas)

```javascript
this.db.run("CREATE TABLE enrollments (id INTEGER PRIMARY KEY, user_id INTEGER, course_id INTEGER)");
this.db.run("CREATE TABLE payments (id INTEGER PRIMARY KEY, enrollment_id INTEGER, amount REAL, status TEXT)");
```

Sem foreign key constraints e sem índices nas colunas de join (`user_id`, `course_id`, `enrollment_id`). Consultas de relatório fazem joins sem índice, resultando em full table scans. Integridade referencial não é garantida pelo banco.

---

### 5 - MEDIUM
**Arquivo:** `src/AppManager.js` — linha 28

```javascript
app.post('/api/checkout', (req, res) => {
```

O endpoint de checkout cria um novo usuário automaticamente se o email não existir, sem verificar senha de usuários existentes. Um usuário com email já cadastrado pode fazer checkout usando qualquer senha (ou sem senha) e ser matriculado sem autenticação real.

---

## LOW

### 1 - LOW
**Arquivo:** `src/AppManager.js` — linhas 4 a 133 (God Class)

`AppManager` viola o Princípio da Responsabilidade Única (SRP). A classe concentra: inicialização do banco, criação de schema, seed de dados, definição de rotas, lógica de negócio (checkout, pagamento, matrícula), auditoria e relatórios. Deve ser separada em camadas (routes, services, repositories).

---

### 2 - LOW
**Arquivo:** `src/AppManager.js` — linha 12

```javascript
this.db.run("CREATE TABLE users (id INTEGER PRIMARY KEY, name TEXT, email TEXT, pass TEXT)");
```

Nomenclatura inconsistente e pouco descritiva: `pass` em vez de `password_hash`, `active` como `INTEGER` em vez de `BOOLEAN`. Campo `email` sem constraint `UNIQUE` — permite cadastro duplicado do mesmo email no banco.

---

### 3 - LOW
**Arquivo:** `src/utils.js` — linha 1

```javascript
const config = {
    dbUser: "admin_master",
    ...
    port: 3000
};
```

Configurações de porta e outros parâmetros hardcoded sem fallback para variáveis de ambiente. O `.env.example` define `PORT=3000` mas o código ignora essa variável — inconsistência entre documentação e implementação real.

---

## RESUMO

| Severidade | Quantidade |
|-----------|------------|
| CRITICAL  | 6          |
| HIGH      | 6          |
| MEDIUM    | 5          |
| LOW       | 3          |
| **Total** | **20**     |

**Principais categorias de problemas:**
- Segurança: credenciais hardcoded, criptografia fraca, dados sensíveis em logs, endpoints sem autenticação
- Qualidade de código: callback hell, God Class, variáveis abreviadas, código duplicado
- Banco de dados: sem integridade referencial, sem índices, deleção incompleta
- Lógica de negócio: validação de pagamento falsa, criação de usuário sem autenticação
