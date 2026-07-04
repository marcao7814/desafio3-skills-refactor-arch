from flask import Blueprint, request, jsonify

from controllers import category_controller

category_bp = Blueprint('categories', __name__)


@category_bp.route('/categories', methods=['GET'])
def get_categories():
    return jsonify(category_controller.list_categories()), 200


@category_bp.route('/categories', methods=['POST'])
def create_category():
    data = request.get_json()
    if not data:
        return jsonify({'error': 'Dados inválidos'}), 400
    return jsonify(category_controller.create_category(data)), 201


@category_bp.route('/categories/<int:cat_id>', methods=['PUT'])
def update_category(cat_id):
    data = request.get_json()
    if not data:
        return jsonify({'error': 'Dados inválidos'}), 400
    return jsonify(category_controller.update_category(cat_id, data)), 200


@category_bp.route('/categories/<int:cat_id>', methods=['DELETE'])
def delete_category(cat_id):
    category_controller.delete_category(cat_id)
    return jsonify({'message': 'Categoria deletada'}), 200
