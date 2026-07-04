from flask import Blueprint, request, jsonify
from controllers.pedido_controller import (
    processar_pedido, listar_pedidos_usuario,
    listar_todos_pedidos, atualizar_status
)
from database import get_db

pedido_bp = Blueprint('pedidos', __name__)


@pedido_bp.route('', methods=['POST'])
def post_pedido():
    dados = request.get_json(silent=True) or {}
    resultado = processar_pedido(get_db(), dados.get('usuario_id'), dados.get('itens', []))
    return jsonify({'dados': resultado, 'sucesso': True, 'mensagem': 'Pedido criado com sucesso'}), 201


@pedido_bp.route('', methods=['GET'])
def get_pedidos():
    return jsonify({'dados': listar_todos_pedidos(get_db()), 'sucesso': True}), 200


@pedido_bp.route('/usuario/<int:usuario_id>', methods=['GET'])
def get_pedidos_usuario(usuario_id):
    return jsonify({'dados': listar_pedidos_usuario(get_db(), usuario_id), 'sucesso': True}), 200


@pedido_bp.route('/<int:pedido_id>/status', methods=['PUT'])
def put_status_pedido(pedido_id):
    dados = request.get_json(silent=True) or {}
    atualizar_status(get_db(), pedido_id, dados.get('status', ''))
    return jsonify({'sucesso': True, 'mensagem': 'Status atualizado'}), 200
