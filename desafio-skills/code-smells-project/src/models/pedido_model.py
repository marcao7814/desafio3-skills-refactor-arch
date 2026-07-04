def create_pedido(db, usuario_id, total):
    cursor = db.execute(
        "INSERT INTO pedidos (usuario_id, status, total) VALUES (?, 'pendente', ?)",
        (usuario_id, total)
    )
    return cursor.lastrowid


def add_item_pedido(db, pedido_id, produto_id, quantidade, preco_unitario):
    db.execute(
        "INSERT INTO itens_pedido (pedido_id, produto_id, quantidade, preco_unitario) VALUES (?, ?, ?, ?)",
        (pedido_id, produto_id, quantidade, preco_unitario)
    )


def get_pedidos_by_usuario(db, usuario_id):
    rows = db.execute("""
        SELECT p.id, p.usuario_id, p.status, p.total, p.criado_em,
               ip.produto_id, ip.quantidade, ip.preco_unitario,
               pr.nome AS produto_nome
        FROM pedidos p
        LEFT JOIN itens_pedido ip ON ip.pedido_id = p.id
        LEFT JOIN produtos pr ON pr.id = ip.produto_id
        WHERE p.usuario_id = ?
    """, (usuario_id,)).fetchall()
    return _agregar_pedidos(rows)


def get_all_pedidos(db):
    rows = db.execute("""
        SELECT p.id, p.usuario_id, p.status, p.total, p.criado_em,
               ip.produto_id, ip.quantidade, ip.preco_unitario,
               pr.nome AS produto_nome
        FROM pedidos p
        LEFT JOIN itens_pedido ip ON ip.pedido_id = p.id
        LEFT JOIN produtos pr ON pr.id = ip.produto_id
    """).fetchall()
    return _agregar_pedidos(rows)


def update_status_pedido(db, pedido_id, novo_status):
    db.execute(
        "UPDATE pedidos SET status=? WHERE id=?",
        (novo_status, pedido_id)
    )
    db.commit()


def _agregar_pedidos(rows):
    pedidos = {}
    for row in rows:
        pid = row['id']
        if pid not in pedidos:
            pedidos[pid] = {
                'id': pid,
                'usuario_id': row['usuario_id'],
                'status': row['status'],
                'total': row['total'],
                'criado_em': row['criado_em'],
                'itens': []
            }
        if row['produto_id']:
            pedidos[pid]['itens'].append({
                'produto_id': row['produto_id'],
                'produto_nome': row['produto_nome'] or 'Desconhecido',
                'quantidade': row['quantidade'],
                'preco_unitario': row['preco_unitario']
            })
    return list(pedidos.values())
