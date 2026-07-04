from flask import Blueprint, jsonify
from controllers.relatorio_controller import gerar_relatorio_vendas
from database import get_db

relatorio_bp = Blueprint('relatorios', __name__)


@relatorio_bp.route('/vendas', methods=['GET'])
def get_relatorio_vendas():
    return jsonify({'dados': gerar_relatorio_vendas(get_db()), 'sucesso': True}), 200
