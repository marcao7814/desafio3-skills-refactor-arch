#Erros encontados manualmente

C:\Projetos ia 03-2026\Desafio Fullcycle\desafio skill de auditoria\desafio-skills\code-smells-project\models.py
1-  CRITICAL 
get_produto_por_id(id):
    db = get_db()
    cursor = db.cursor()

    cursor.execute("SELECT * FROM produtos WHERE id = " + str(id))

linha 28 - possivel ingestão de dependencia 
    concatenação direta com input do usuário


2  - CRITICAL  
 cursor.execute(
        "INSERT INTO produtos (nome, descricao, preco, estoque, categoria) VALUES ('" +
        nome + "', '" + descricao + "', " + str(preco) + ", " + str(estoque) + ", '" + categoria + "')"
    )
    db.commit()

linha 47 o insert tem que ser feito com aparmetros parametrizaveis ou seja ao jogar string pode executar um comando sql como o drop table

3- CRITICAL    
 cursor.execute(
        "UPDATE produtos SET nome = '" + nome + "', descricao = '" + descricao +
        "', preco = " + str(preco) + ", estoque = " + str(estoque) +
        ", categoria = '" + categoria + "' WHERE id = " + str(id)
    )
    db.commit()
 linha 58 update tem que ser feito com parmetros parametrizaveis ou seja ao jogar string pode executar um comando sql como o drop table

4- CRITICAL 
def deletar_produto(id):
    db = get_db()
    cursor = db.cursor()
    cursor.execute("DELETE FROM produtos WHERE id = " + str(id))
    db.commit()
    return True

linha 68 delete tem que ser feito com parmetros parametrizaveis ou seja ao jogar string pode executar um comando sql como o drop table

5- CRITICAL 
cursor.execute(
        "SELECT * FROM usuarios WHERE email = '" + email + "' AND senha = '" + senha + "'"
    )
    row = cursor.fetchone()
    if row:
        return {
            "id": row["id"],
            "nome": row["nome"],
            "email": row["email"],
            "tipo": row["tipo"]
        }
    return None
linha 109  email e senha concatenados — bypass de autenticação direto


6- CRITICAL     

cursor.execute(
        "INSERT INTO usuarios (nome, email, senha, tipo) VALUES ('" +
        nome + "', '" + email + "', '" + senha + "', '" + tipo + "')"
    )
 linha 127 possivel ingestão de dependencia 
    concatenação direta com input do usuário



1- HIGH linha 139 loop com query aninhada
    for item in itens:
        cursor.execute("SELECT * FROM produtos WHERE id = " + str(item["produto_id"]))
        produto = cursor.fetchone()
        if produto is None:
            return {"erro": "Produto " + str(item["produto_id"]) + " não encontrado"}
        if produto["estoque"] < item["quantidade"]:
            return {"erro": "Estoque insuficiente para " + produto["nome"]}
        total = total + (produto["preco"] * item["quantidade"])

    cursor.execute(
        "INSERT INTO pedidos (usuario_id, status, total) VALUES (" +
        str(usuario_id) + ", 'pendente', " + str(total) + ")"
    )
    pedido_id = cursor.lastrowid
    

   2- HIGH linha 173 cursores aninhados 
   cursor = db.cursor()
    cursor.execute("SELECT * FROM pedidos WHERE usuario_id = " + str(usuario_id))
    rows = cursor.fetchall()
    result = []
    for row in rows:
        pedido = {
            "id": row["id"],
            "usuario_id": row["usuario_id"],
            "status": row["status"],
            "total": row["total"],
            "criado_em": row["criado_em"],
            "itens": []
        }

        cursor2 = db.cursor()
        cursor2.execute("SELECT * FROM itens_pedido WHERE pedido_id = " + str(row["id"]))
        itens = cursor2.fetchall()
        for item in itens:
            cursor3 = db.cursor()


3- HIGH linha 210 cursores aninhados
 cursor = db.cursor()
    cursor.execute("SELECT * FROM pedidos")
    rows = cursor.fetchall()
    result = []
    for row in rows:

        pedido = {
            "id": row["id"],
            "usuario_id": row["usuario_id"],
            "status": row["status"],
            "total": row["total"],
            "criado_em": row["criado_em"],
            "itens": []
        }
        cursor2 = db.cursor()
        cursor2.execute("SELECT * FROM itens_pedido WHERE pedido_id = " + str(row["id"]))
        itens = cursor2.fetchall()
        for item in itens:
            cursor3 = db.cursor()

4- HIGH senha exposta linha 75 pode expor a senha de todos usuarios
def get_todos_usuarios():
    db = get_db()
    cursor = db.cursor()
    cursor.execute("SELECT * FROM usuarios")
    rows = cursor.fetchall()
    result = []
    for row in rows:
        result.append({
            "id": row["id"],
            "nome": row["nome"],
            "email": row["email"],
            "senha": row["senha"],
            "tipo": row["tipo"],
            "criado_em": row["criado_em"]
        })
    return result


5- HIGH  enha exposta por ID
def get_usuario_por_id(id):
    db = get_db()
    cursor = db.cursor()
    cursor.execute("SELECT * FROM usuarios WHERE id = " + str(id))
    row = cursor.fetchone()
    if row:
        return {
            "id": row["id"],
            "nome": row["nome"],
            "email": row["email"],
            "senha": row["senha"],
            "tipo": row["tipo"],
            "criado_em": row["criado_em"]
        }
    return None

- def get_usuario_por_id(id):
    db = get_db()
    cursor = db.cursor()
    cursor.execute("SELECT * FROM usuarios WHERE id = " + str(id))
    row = cursor.fetchone()

linha 92 - possivel ingestão de dependencia 
    concatenação direta com input do usuário

7 def criar_pedido(usuario_id, itens):
    db = get_db()
    cursor = db.cursor()

    total = 0

    for item in itens:
        cursor.execute("SELECT * FROM produtos WHERE id = " + str(item["produto_id"]))
        produto = cursor.fetchone()
linha 120 possivel ingestão de dependencia 
    concatenação direta com input do usuário


1- MEDIUM linha 257  deve-se nomear constantes
 desconto = 0
    if faturamento > 10000:
        desconto = faturamento * 0.1
    elif faturamento > 5000:
        desconto = faturamento * 0.05
    elif faturamento > 1000:
        desconto = faturamento * 0.02


2- MEDIUM  linha 289 Query com concatenação de texto
query = "SELECT * FROM produtos WHERE 1=1"
    if termo:
        query += " AND (nome LIKE '%" + termo + "%' OR descricao LIKE '%" + termo + "%')"
    if categoria:
        query += " AND categoria = '" + categoria + "'"
    if preco_min:
        query += " AND preco >= " + str(preco_min)
    if preco_max:
        query += " AND preco <= " + str(preco_max)

3- MEDIUM SQL Injection via busca dinâmica concatenação da query
def buscar_produtos(termo, categoria=None, preco_min=None, preco_max=None):
    db = get_db()
    cursor = db.cursor()

    query = "SELECT * FROM produtos WHERE 1=1"
    if termo:
        query += " AND (nome LIKE '%" + termo + "%' OR descricao LIKE '%" + termo + "%')"
    if categoria:
        query += " AND categoria = '" + categoria + "'"
    if preco_min:
        query += " AND preco >= " + str(preco_min)
    if preco_max:
        query += " AND preco <= " + str(preco_max)

    
    
    
    1 LOW - Linha 173 cursor, cursor2, cursor3 - nome genérico
    cursor.execute(query)


     rows = cursor.fetchall()
    result = []
    for row in rows:
        pedido = {
            "id": row["id"],
            "usuario_id": row["usuario_id"],
            "status": row["status"],
            "total": row["total"],
            "criado_em": row["criado_em"],
            "itens": []
        }

        cursor2 = db.cursor()
        cursor2.execute("SELECT * FROM itens_pedido WHERE pedido_id = " + str(row["id"]))
        itens = cursor2.fetchall()
        for item in itens:
            cursor3 = db.cursor()
            cursor3.execute("SELECT nome FROM produtos WHERE id = " + str(item["produto_id"]))
            prod = cursor3.fetchone()


 2- LOW  linha 256 variável fora do bloco condicional 
desconto = 0
    if faturamento > 10000:
        desconto = faturamento * 0.1
    elif faturamento > 5000: