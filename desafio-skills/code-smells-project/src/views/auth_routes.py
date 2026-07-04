from flask import Blueprint, request, jsonify
from controllers.usuario_controller import autenticar
from database import get_db

auth_bp = Blueprint('auth', __name__)


@auth_bp.route('/login', methods=['POST'])
def post_login():
    dados = request.get_json(silent=True) or {}
    usuario = autenticar(get_db(), dados)
    return jsonify({'dados': usuario, 'sucesso': True, 'mensagem': 'Login OK'}), 200
