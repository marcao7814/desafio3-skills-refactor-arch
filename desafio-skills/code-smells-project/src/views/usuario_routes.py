from flask import Blueprint, request, jsonify
from controllers.usuario_controller import listar_usuarios, buscar_usuario, registrar_usuario
from database import get_db

usuario_bp = Blueprint('usuarios', __name__)


@usuario_bp.route('', methods=['GET'])
def get_usuarios():
    return jsonify({'dados': listar_usuarios(get_db()), 'sucesso': True}), 200


@usuario_bp.route('/<int:usuario_id>', methods=['GET'])
def get_usuario(usuario_id):
    usuario = buscar_usuario(get_db(), usuario_id)
    return jsonify({'dados': usuario, 'sucesso': True}), 200


@usuario_bp.route('', methods=['POST'])
def post_usuario():
    dados = request.get_json(silent=True) or {}
    usuario_id = registrar_usuario(get_db(), dados)
    return jsonify({'dados': {'id': usuario_id}, 'sucesso': True}), 201
