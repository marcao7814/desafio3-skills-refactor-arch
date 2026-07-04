from flask import jsonify

from controllers.errors import NotFoundError, ConflictError, UnauthorizedError, ForbiddenError


def register_error_handlers(app):
    @app.errorhandler(ValueError)
    def handle_value_error(e):
        return jsonify({'error': str(e)}), 400

    @app.errorhandler(UnauthorizedError)
    def handle_unauthorized(e):
        return jsonify({'error': str(e)}), 401

    @app.errorhandler(ForbiddenError)
    def handle_forbidden(e):
        return jsonify({'error': str(e)}), 403

    @app.errorhandler(NotFoundError)
    def handle_not_found(e):
        return jsonify({'error': str(e)}), 404

    @app.errorhandler(404)
    def handle_404(e):
        return jsonify({'error': 'Recurso não encontrado'}), 404

    @app.errorhandler(ConflictError)
    def handle_conflict(e):
        return jsonify({'error': str(e)}), 409

    @app.errorhandler(Exception)
    def handle_generic(e):
        return jsonify({'error': 'Erro interno do servidor'}), 500
