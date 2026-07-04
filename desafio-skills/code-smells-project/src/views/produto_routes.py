from flask import Blueprint, request, jsonify
from controllers.produto_controller import (
    listar_produtos, buscar_produto, pesquisar_produtos,
    criar_produto, atualizar_produto, remover_produto
)
from database import get_db

produto_bp = Blueprint('produtos', __name__)


@produto_bp.route('', methods=['GET'])
def get_produtos():
    return jsonify({'dados': listar_produtos(get_db()), 'sucesso': True}), 200


@produto_bp.route('/busca', methods=['GET'])
def get_busca_produtos():
    termo = request.args.get('q', '')
    categoria = request.args.get('categoria')
    preco_min_str = request.args.get('preco_min')
    preco_max_str = request.args.get('preco_max')
    preco_min = float(preco_min_str) if preco_min_str else None
    preco_max = float(preco_max_str) if preco_max_str else None
    resultados = pesquisar_produtos(get_db(), termo, categoria, preco_min, preco_max)
    return jsonify({'dados': resultados, 'total': len(resultados), 'sucesso': True}), 200


@produto_bp.route('/<int:produto_id>', methods=['GET'])
def get_produto(produto_id):
    produto = buscar_produto(get_db(), produto_id)
    return jsonify({'dados': produto, 'sucesso': True}), 200


@produto_bp.route('', methods=['POST'])
def post_produto():
    dados = request.get_json(silent=True) or {}
    produto_id = criar_produto(get_db(), dados)
    return jsonify({'dados': {'id': produto_id}, 'sucesso': True, 'mensagem': 'Produto criado'}), 201


@produto_bp.route('/<int:produto_id>', methods=['PUT'])
def put_produto(produto_id):
    dados = request.get_json(silent=True) or {}
    atualizar_produto(get_db(), produto_id, dados)
    return jsonify({'sucesso': True, 'mensagem': 'Produto atualizado'}), 200


@produto_bp.route('/<int:produto_id>', methods=['DELETE'])
def del_produto(produto_id):
    remover_produto(get_db(), produto_id)
    return jsonify({'sucesso': True, 'mensagem': 'Produto deletado'}), 200
