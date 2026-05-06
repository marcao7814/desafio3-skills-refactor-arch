# Erros Encontrados — code-smells-project
### Análise Integrada com Tipos e Classificações de Code Smells

**Arquivo analisado:** `desafio-skills/code-smells-project/models.py`  
**Total de problemas:** 14 findings

---

## O que é um Code Smell?

Na engenharia de software, *code smells* são sintomas de que algo está errado no design ou na implementação, prejudicando manutenção, testabilidade e evolução do sistema. Os problemas abaixo foram classificados segundo a escala de severidade baseada em MVC e SOLID.

| Severidade | Critério |
|-----------|---------|
| **CRITICAL** | Falhas graves de segurança ou arquitetura — expõem dados, permitem ataques ou violam completamente a separação de responsabilidades |
| **HIGH** | Violações fortes de MVC/SOLID que dificultam manutenção e testes — acoplamento excessivo, lógica no lugar errado |
| **MEDIUM** | Problemas de padronização, duplicação ou performance moderada — queries N+1, magic numbers, validações ausentes |
| **LOW** | Melhorias de legibilidade — nomenclatura ruim, variáveis obscuras, código desorganizado |

---

## CRITICAL

### 1 — SQL Injection via concatenação direta (GET)
**Arquivo:** `models.py` — linha 28  
**Tipo de Code Smell:** SQL Injection  
**Categoria:** Falha de Segurança

```python
cursor.execute("SELECT * FROM produtos WHERE id = " + str(id))
```

**Descrição:**  
Concatenação direta de input do usuário na query SQL. Qualquer valor passado como `id` é interpretado como parte do comando SQL — um atacante pode enviar `1 OR 1=1` ou `1; DROP TABLE produtos` e obter ou destruir dados.

**Por que é CRITICAL:**  
SQL Injection é uma das vulnerabilidades mais exploradas do mundo (OWASP Top 1). Uma única requisição maliciosa pode expor toda a base de dados ou corrompê-la permanentemente. Não requer autenticação para ser explorada.

**Solução:**  
Usar parâmetros parametrizáveis — nunca concatenar valores externos diretamente na query:
```python
cursor.execute("SELECT * FROM produtos WHERE id = ?", (id,))
```

---

### 2 — SQL Injection via concatenação direta (INSERT produtos)
**Arquivo:** `models.py` — linha 47  
**Tipo de Code Smell:** SQL Injection  
**Categoria:** Falha de Segurança

```python
cursor.execute(
    "INSERT INTO produtos (nome, descricao, preco, estoque, categoria) VALUES ('" +
    nome + "', '" + descricao + "', " + str(preco) + ", " + str(estoque) + ", '" + categoria + "')"
)
```

**Descrição:**  
INSERT com concatenação de strings para todos os campos. Um valor como `nome = "x', 'y', 0, 0, 'z'); DROP TABLE produtos; --"` executa comandos arbitrários no banco.

**Por que é CRITICAL:**  
Mesmo impacto do item anterior, porém numa operação de escrita — o atacante pode não apenas ler mas modificar, inserir ou apagar registros diretamente.

**Solução:**  
```python
cursor.execute(
    "INSERT INTO produtos (nome, descricao, preco, estoque, categoria) VALUES (?, ?, ?, ?, ?)",
    (nome, descricao, preco, estoque, categoria)
)
```

---

### 3 — SQL Injection via concatenação direta (UPDATE produtos)
**Arquivo:** `models.py` — linha 58  
**Tipo de Code Smell:** SQL Injection  
**Categoria:** Falha de Segurança

```python
cursor.execute(
    "UPDATE produtos SET nome = '" + nome + "', descricao = '" + descricao +
    "', preco = " + str(preco) + ", estoque = " + str(estoque) +
    ", categoria = '" + categoria + "' WHERE id = " + str(id)
)
```

**Descrição:**  
UPDATE com concatenação em todos os campos e no filtro `WHERE id`. Permite alterar registros arbitrários ou executar subcomandos SQL.

**Por que é CRITICAL:**  
Afeta operação de atualização — um atacante pode modificar qualquer linha do banco manipulando o `id` ou os valores dos campos.

**Solução:**  
```python
cursor.execute(
    "UPDATE produtos SET nome=?, descricao=?, preco=?, estoque=?, categoria=? WHERE id=?",
    (nome, descricao, preco, estoque, categoria, id)
)
```

---

### 4 — SQL Injection via concatenação direta (DELETE produtos)
**Arquivo:** `models.py` — linha 68  
**Tipo de Code Smell:** SQL Injection  
**Categoria:** Falha de Segurança

```python
cursor.execute("DELETE FROM produtos WHERE id = " + str(id))
```

**Descrição:**  
DELETE com concatenação direta do `id`. Passando `id = "1 OR 1=1"` apaga todos os registros da tabela de uma vez.

**Por que é CRITICAL:**  
Operação destrutiva sem parâmetros seguros — permite deleção em massa de dados.

**Solução:**  
```python
cursor.execute("DELETE FROM produtos WHERE id = ?", (id,))
```

---

### 5 — SQL Injection + Bypass de Autenticação (SELECT usuários)
**Arquivo:** `models.py` — linha 109  
**Tipo de Code Smell:** SQL Injection / Authentication Bypass  
**Categoria:** Falha de Segurança Crítica

```python
cursor.execute(
    "SELECT * FROM usuarios WHERE email = '" + email + "' AND senha = '" + senha + "'"
)
```

**Descrição:**  
Email e senha concatenados diretamente na query de autenticação. Passando `email = "' OR '1'='1' --"` e qualquer senha, o `WHERE` sempre retorna verdadeiro — qualquer pessoa entra no sistema sem credenciais válidas.

**Por que é CRITICAL:**  
Permite bypass total da autenticação. Um atacante pode acessar qualquer conta sem conhecer a senha — incluindo contas administrativas.

**Solução:**  
```python
cursor.execute(
    "SELECT * FROM usuarios WHERE email = ? AND senha = ?",
    (email, senha)
)
```

---

### 6 — SQL Injection via concatenação direta (INSERT usuários)
**Arquivo:** `models.py` — linha 127  
**Tipo de Code Smell:** SQL Injection  
**Categoria:** Falha de Segurança

```python
cursor.execute(
    "INSERT INTO usuarios (nome, email, senha, tipo) VALUES ('" +
    nome + "', '" + email + "', '" + senha + "', '" + tipo + "')"
)
```

**Descrição:**  
Cadastro de usuários com concatenação direta. Permite criação de usuários com payload malicioso nos campos ou escalada de privilégios manipulando o campo `tipo`.

**Por que é CRITICAL:**  
Além de SQL Injection clássico, um atacante pode se cadastrar como `tipo = "admin"` ou encerrar o INSERT e executar outros comandos.

**Solução:**  
```python
cursor.execute(
    "INSERT INTO usuarios (nome, email, senha, tipo) VALUES (?, ?, ?, ?)",
    (nome, email, senha, tipo)
)
```

---

## HIGH

### 1 — Query N+1 em loop (criar pedido)
**Arquivo:** `models.py` — linha 139  
**Tipo de Code Smell:** Query N+1  
**Categoria:** Bloatheads / Performance

```python
for item in itens:
    cursor.execute("SELECT * FROM produtos WHERE id = " + str(item["produto_id"]))
    produto = cursor.fetchone()
```

**Descrição:**  
Para cada item do pedido é executada uma query separada ao banco. Se o pedido tiver 50 itens, são 50 queries individuais — o que poderia ser resolvido com uma única query usando `IN (...)`.

**Por que é HIGH:**  
Em sistemas com volume moderado de pedidos, isso degrada a performance significativamente. Além disso, contém SQL Injection secundário pelo `str(item["produto_id"])`.

**Solução:**  
Coletar todos os IDs primeiro e buscar em uma única query:
```python
ids = [item["produto_id"] for item in itens]
placeholders = ",".join("?" * len(ids))
cursor.execute(f"SELECT * FROM produtos WHERE id IN ({placeholders})", ids)
```

---

### 2 — Cursores aninhados (listar pedidos por usuário)
**Arquivo:** `models.py` — linha 173  
**Tipo de Code Smell:** Callback Hell / Cursores Aninhados  
**Categoria:** Bloatheads / Legibilidade

```python
cursor = db.cursor()
cursor.execute("SELECT * FROM pedidos WHERE usuario_id = " + str(usuario_id))
rows = cursor.fetchall()
for row in rows:
    cursor2 = db.cursor()
    cursor2.execute("SELECT * FROM itens_pedido WHERE pedido_id = " + str(row["id"]))
    itens = cursor2.fetchall()
    for item in itens:
        cursor3 = db.cursor()
```

**Descrição:**  
Três cursores aninhados (`cursor`, `cursor2`, `cursor3`) para buscar pedidos, itens e produtos em loops encadeados. Estrutura análoga ao *Callback Hell* — cada nível adiciona complexidade e dificulta rastreamento de erros.

**Por que é HIGH:**  
Além da ilegibilidade, gera múltiplas queries desnecessárias (N+1 em dois níveis). Qualquer mudança no schema impacta os três níveis de aninhamento.

**Solução:**  
Substituir por JOINs ou queries únicas com mapeamento posterior em Python.

---

### 3 — Cursores aninhados (listar todos os pedidos)
**Arquivo:** `models.py` — linha 210  
**Tipo de Code Smell:** Callback Hell / Cursores Aninhados  
**Categoria:** Bloatheads / Performance

```python
cursor = db.cursor()
cursor.execute("SELECT * FROM pedidos")
rows = cursor.fetchall()
for row in rows:
    cursor2 = db.cursor()
    cursor2.execute("SELECT * FROM itens_pedido WHERE pedido_id = " + str(row["id"]))
    itens = cursor2.fetchall()
    for item in itens:
        cursor3 = db.cursor()
```

**Descrição:**  
Mesma estrutura de cursores aninhados porém listando **todos** os pedidos sem filtro. Com volumes reais de dados, isso pode gerar centenas de queries por requisição.

**Por que é HIGH:**  
`SELECT * FROM pedidos` sem paginação + N+1 em dois níveis = risco real de timeout e sobrecarga do banco em produção.

**Solução:**  
Usar JOIN entre `pedidos`, `itens_pedido` e `produtos` numa única query com `GROUP BY` ou processar com ORM adequado.

---

### 4 — Senha exposta em listagem de usuários
**Arquivo:** `models.py` — linha 75  
**Tipo de Code Smell:** Sensitive Data Exposure  
**Categoria:** Falha de Segurança / Violação de Privacidade

```python
result.append({
    "id": row["id"],
    "nome": row["nome"],
    "email": row["email"],
    "senha": row["senha"],   # ← exposto
    "tipo": row["tipo"],
    "criado_em": row["criado_em"]
})
```

**Descrição:**  
A função `get_todos_usuarios()` inclui o campo `senha` no resultado retornado pela API. Qualquer pessoa com acesso ao endpoint recebe as senhas de todos os usuários.

**Por que é HIGH:**  
Exposição de credenciais em massa. Mesmo que as senhas estejam hasheadas, a exposição do hash facilita ataques de dicionário offline.

**Solução:**  
Nunca incluir `senha` na serialização de respostas. Remover o campo do dicionário retornado.

---

### 5 — Senha exposta ao buscar usuário por ID
**Arquivo:** `models.py` — linha 92  
**Tipo de Code Smell:** Sensitive Data Exposure + SQL Injection  
**Categoria:** Falha de Segurança

```python
cursor.execute("SELECT * FROM usuarios WHERE id = " + str(id))
row = cursor.fetchone()
if row:
    return {
        "id": row["id"],
        "nome": row["nome"],
        "email": row["email"],
        "senha": row["senha"],   # ← exposto
        ...
    }
```

**Descrição:**  
Duplo problema: SQL Injection no `WHERE id =` concatenado + campo `senha` incluído na resposta. A query também usa `SELECT *` retornando todos os campos indiscriminadamente.

**Por que é HIGH:**  
Combina dois vetores de ataque: injeção para acessar qualquer registro + exposição do hash da senha do registro acessado.

**Solução:**  
Usar query parametrizada com campos específicos: `SELECT id, nome, email, tipo, criado_em FROM usuarios WHERE id = ?`

---

### 6 — SQL Injection em criação de pedido
**Arquivo:** `models.py` — linha 120  
**Tipo de Code Smell:** SQL Injection  
**Categoria:** Falha de Segurança

```python
cursor.execute("SELECT * FROM produtos WHERE id = " + str(item["produto_id"]))
```

**Descrição:**  
Concatenação de `produto_id` vindo do payload da requisição. O valor não é validado nem sanitizado antes de ser inserido na query.

**Por que é HIGH:**  
Input externo (corpo da requisição) sendo concatenado diretamente — vetor de injeção num fluxo de negócio crítico (criação de pedido).

**Solução:**  
```python
cursor.execute("SELECT * FROM produtos WHERE id = ?", (item["produto_id"],))
```

---

## MEDIUM

### 1 — Magic Numbers em cálculo de desconto
**Arquivo:** `models.py` — linha 257  
**Tipo de Code Smell:** Magic Numbers  
**Categoria:** LOW → promovido a MEDIUM por contexto de negócio

```python
desconto = 0
if faturamento > 10000:
    desconto = faturamento * 0.1
elif faturamento > 5000:
    desconto = faturamento * 0.05
elif faturamento > 1000:
    desconto = faturamento * 0.02
```

**Descrição:**  
Valores `10000`, `5000`, `1000`, `0.1`, `0.05` e `0.02` aparecem diretamente no código sem nenhuma constante nomeada. Não há como saber se `0.1` representa 10% de desconto, uma taxa ou outro valor sem ler todo o contexto.

**Relação com Tipos de Code Smells:**  
Classifica como *Magic Numbers* — categoria LOW por convenção, mas promovido a MEDIUM aqui pois regras de negócio financeiras hardcoded são mais difíceis de auditar e alterar com segurança.

**Solução:**  
```python
LIMITE_DESCONTO_ALTO   = 10000
LIMITE_DESCONTO_MEDIO  = 5000
LIMITE_DESCONTO_BAIXO  = 1000
TAXA_DESCONTO_ALTO     = 0.10
TAXA_DESCONTO_MEDIO    = 0.05
TAXA_DESCONTO_BAIXO    = 0.02
```

---

### 2 — SQL Injection via busca dinâmica com concatenação
**Arquivo:** `models.py` — linha 289  
**Tipo de Code Smell:** SQL Injection / Query Dinâmica Insegura  
**Categoria:** Falha de Segurança (MEDIUM — filtros opcionais)

```python
query = "SELECT * FROM produtos WHERE 1=1"
if termo:
    query += " AND (nome LIKE '%" + termo + "%' OR descricao LIKE '%" + termo + "%')"
if categoria:
    query += " AND categoria = '" + categoria + "'"
if preco_min:
    query += " AND preco >= " + str(preco_min)
if preco_max:
    query += " AND preco <= " + str(preco_max)
```

**Descrição:**  
Query montada dinamicamente por concatenação de strings para suportar filtros opcionais de busca. Todos os parâmetros — `termo`, `categoria`, `preco_min`, `preco_max` — são injetáveis diretamente.

**Relação com Tipos de Code Smells:**  
Combina *Código Duplicado* (padrão de concatenação repetido 4 vezes) com *SQL Injection*. A abordagem de construção dinâmica de queries é um anti-pattern conhecido.

**Solução:**  
Usar lista de condições com parâmetros separados:
```python
conditions = ["1=1"]
params = []
if termo:
    conditions.append("(nome LIKE ? OR descricao LIKE ?)")
    params.extend([f"%{termo}%", f"%{termo}%"])
if categoria:
    conditions.append("categoria = ?")
    params.append(categoria)
query = "SELECT * FROM produtos WHERE " + " AND ".join(conditions)
cursor.execute(query, params)
```

---

### 3 — Código Duplicado na busca dinâmica
**Arquivo:** `models.py` — linha 289  
**Tipo de Code Smell:** Código Duplicado (DRY Violation)  
**Categoria:** MEDIUM

**Descrição:**  
O padrão `query += " AND campo = '" + valor + "'"` é repetido 4 vezes com variações mínimas. Qualquer refatoração para usar parâmetros exigirá modificar todos os 4 pontos.

**Relação com Tipos de Code Smells:**  
*Código Duplicado* — viola o princípio DRY. Se uma regra muda (ex: adicionar sanitização de `termo`), precisa ser aplicada em múltiplos lugares. A chance de inconsistência é alta.

**Solução:**  
Centralizar a construção da query em um helper reutilizável que receba os filtros como dicionário.

---

## LOW

### 1 — Variáveis com nomes genéricos (cursor, cursor2, cursor3)
**Arquivo:** `models.py` — linha 173  
**Tipo de Code Smell:** Variáveis Abreviadas / Nomenclatura Ruim  
**Categoria:** LOW

```python
cursor = db.cursor()
cursor2 = db.cursor()
cursor3 = db.cursor()
```

**Descrição:**  
Cursores nomeados sequencialmente sem indicar seu propósito. `cursor` poderia ser `pedidos_cursor`, `cursor2` poderia ser `itens_cursor`, `cursor3` poderia ser `produtos_cursor`.

**Relação com Tipos de Code Smells:**  
*Variáveis Abreviadas / Obscurity* — o código é lido muito mais vezes do que é escrito. Nomes como `cursor2` e `cursor3` obrigam o leitor a rastrear o contexto para entender o que cada um representa. Aumenta a carga cognitiva sem necessidade.

**Solução:**  
```python
pedidos_cursor  = db.cursor()
itens_cursor    = db.cursor()
produtos_cursor = db.cursor()
```

---

### 2 — Variável inicializada fora do bloco condicional
**Arquivo:** `models.py` — linha 256  
**Tipo de Code Smell:** Dead Code / Organização de Código  
**Categoria:** LOW

```python
desconto = 0
if faturamento > 10000:
    desconto = faturamento * 0.1
elif faturamento > 5000:
    desconto = faturamento * 0.05
elif faturamento > 1000:
    desconto = faturamento * 0.02
```

**Descrição:**  
`desconto = 0` é inicializado antes do bloco condicional como fallback. Embora funcione, obscurece a intenção — não fica claro que `0` é o valor padrão para faturamentos abaixo de `1000`. Junto com os magic numbers do item MEDIUM-1, dificulta a leitura das regras de negócio.

**Relação com Tipos de Code Smells:**  
*Speculative Generality* parcial — o valor `0` poderia ser mais explícito como constante `SEM_DESCONTO = 0` ou o bloco poderia ser transformado numa função com retorno explícito em cada branch.

**Solução:**  
Refatorar para função com retorno explícito:
```python
def calcular_desconto(faturamento):
    if faturamento > LIMITE_DESCONTO_ALTO:
        return faturamento * TAXA_DESCONTO_ALTO
    if faturamento > LIMITE_DESCONTO_MEDIO:
        return faturamento * TAXA_DESCONTO_MEDIO
    if faturamento > LIMITE_DESCONTO_BAIXO:
        return faturamento * TAXA_DESCONTO_BAIXO
    return 0
```

---

## Resumo dos Findings

| # | Descrição | Tipo de Smell | Severidade | Linha |
|---|-----------|--------------|-----------|-------|
| 1 | SQL Injection — SELECT produtos | SQL Injection | CRITICAL | 28 |
| 2 | SQL Injection — INSERT produtos | SQL Injection | CRITICAL | 47 |
| 3 | SQL Injection — UPDATE produtos | SQL Injection | CRITICAL | 58 |
| 4 | SQL Injection — DELETE produtos | SQL Injection | CRITICAL | 68 |
| 5 | SQL Injection + Auth Bypass — SELECT usuários | SQL Injection / Auth Bypass | CRITICAL | 109 |
| 6 | SQL Injection — INSERT usuários | SQL Injection | CRITICAL | 127 |
| 7 | Query N+1 em loop de itens | Query N+1 | HIGH | 139 |
| 8 | Cursores aninhados — pedidos por usuário | Callback Hell | HIGH | 173 |
| 9 | Cursores aninhados — todos os pedidos | Callback Hell | HIGH | 210 |
| 10 | Senha exposta em listagem geral | Sensitive Data Exposure | HIGH | 75 |
| 11 | Senha exposta ao buscar por ID | Sensitive Data Exposure + SQL Injection | HIGH | 92 |
| 12 | SQL Injection em criação de pedido | SQL Injection | HIGH | 120 |
| 13 | Magic Numbers em cálculo de desconto | Magic Numbers | MEDIUM | 257 |
| 14 | SQL Injection + DRY na busca dinâmica | SQL Injection / Código Duplicado | MEDIUM | 289 |
| 15 | Código Duplicado na query dinâmica | Código Duplicado | MEDIUM | 289 |
| 16 | Nomenclatura genérica (cursor, cursor2, cursor3) | Variáveis Abreviadas | LOW | 173 |
| 17 | Variável fora do bloco condicional | Dead Code / Organização | LOW | 256 |

**Total:** 6 CRITICAL · 6 HIGH · 3 MEDIUM · 2 LOW = **17 findings**
