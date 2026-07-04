from models.produto_model import get_produto_by_id, update_estoque
from models.pedido_model import (
    create_pedido, add_item_pedido,
    get_pedidos_by_usuario, get_all_pedidos,
    update_status_pedido as _update_status
)
from config.constants import STATUS_VALIDOS


def processar_pedido(db, usuario_id, itens):
    if not usuario_id:
        raise ValueError('usuario_id é obrigatório')
    if not itens:
        raise ValueError('Pedido deve ter pelo menos 1 item')

    total = 0
    itens_validados = []
    for item in itens:
        produto = get_produto_by_id(db, item['produto_id'])
        if not produto:
            raise ValueError(f"Produto {item['produto_id']} não encontrado")
        if produto['estoque'] < item['quantidade']:
            raise ValueError(f"Estoque insuficiente para {produto['nome']}")
        total += produto['preco'] * item['quantidade']
        itens_validados.append((produto, item))

    pedido_id = create_pedido(db, usuario_id, total)
    for produto, item in itens_validados:
        add_item_pedido(db, pedido_id, item['produto_id'], item['quantidade'], produto['preco'])
        update_estoque(db, item['produto_id'], item['quantidade'])
    db.commit()

    return {'pedido_id': pedido_id, 'total': total}


def listar_pedidos_usuario(db, usuario_id):
    return get_pedidos_by_usuario(db, usuario_id)


def listar_todos_pedidos(db):
    return get_all_pedidos(db)


def atualizar_status(db, pedido_id, novo_status):
    if novo_status not in STATUS_VALIDOS:
        raise ValueError(f'Status inválido. Válidos: {STATUS_VALIDOS}')
    _update_status(db, pedido_id, novo_status)
    return novo_status
