def get_all_produtos(db):
    rows = db.execute("SELECT * FROM produtos").fetchall()
    return [dict(row) for row in rows]


def get_produto_by_id(db, produto_id):
    row = db.execute(
        "SELECT * FROM produtos WHERE id = ?", (produto_id,)
    ).fetchone()
    return dict(row) if row else None


def search_produtos(db, termo='', categoria=None, preco_min=None, preco_max=None):
    query = "SELECT * FROM produtos WHERE 1=1"
    params = []
    if termo:
        query += " AND (nome LIKE ? OR descricao LIKE ?)"
        params.extend([f"%{termo}%", f"%{termo}%"])
    if categoria:
        query += " AND categoria = ?"
        params.append(categoria)
    if preco_min is not None:
        query += " AND preco >= ?"
        params.append(preco_min)
    if preco_max is not None:
        query += " AND preco <= ?"
        params.append(preco_max)
    rows = db.execute(query, params).fetchall()
    return [dict(row) for row in rows]


def create_produto(db, nome, descricao, preco, estoque, categoria):
    cursor = db.execute(
        "INSERT INTO produtos (nome, descricao, preco, estoque, categoria) VALUES (?, ?, ?, ?, ?)",
        (nome, descricao, preco, estoque, categoria)
    )
    db.commit()
    return cursor.lastrowid


def update_produto(db, produto_id, nome, descricao, preco, estoque, categoria):
    db.execute(
        "UPDATE produtos SET nome=?, descricao=?, preco=?, estoque=?, categoria=? WHERE id=?",
        (nome, descricao, preco, estoque, categoria, produto_id)
    )
    db.commit()


def delete_produto(db, produto_id):
    db.execute("DELETE FROM produtos WHERE id=?", (produto_id,))
    db.commit()


def update_estoque(db, produto_id, quantidade):
    db.execute(
        "UPDATE produtos SET estoque = estoque - ? WHERE id = ?",
        (quantidade, produto_id)
    )
