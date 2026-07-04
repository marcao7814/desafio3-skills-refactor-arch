import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

from flask import Flask, jsonify
from flask_cors import CORS
from config.settings import SECRET_KEY, PORT, DEBUG
from database import init_db, close_db, get_db
from views.produto_routes import produto_bp
from views.usuario_routes import usuario_bp
from views.auth_routes import auth_bp
from views.pedido_routes import pedido_bp
from views.relatorio_routes import relatorio_bp
from middlewares.error_handler import register_error_handlers


def create_app():
    app = Flask(__name__)
    app.config['SECRET_KEY'] = SECRET_KEY
    CORS(app)

    app.register_blueprint(produto_bp, url_prefix='/produtos')
    app.register_blueprint(usuario_bp, url_prefix='/usuarios')
    app.register_blueprint(auth_bp)
    app.register_blueprint(pedido_bp, url_prefix='/pedidos')
    app.register_blueprint(relatorio_bp, url_prefix='/relatorios')

    register_error_handlers(app)
    app.teardown_appcontext(close_db)

    @app.route('/')
    def index():
        return jsonify({
            'mensagem': 'Bem-vindo à API da Loja',
            'versao': '1.0.0',
            'endpoints': {
                'produtos': '/produtos',
                'usuarios': '/usuarios',
                'pedidos': '/pedidos',
                'login': '/login',
                'relatorios': '/relatorios/vendas',
                'health': '/health'
            }
        })

    @app.route('/health')
    def health_check():
        db = get_db()
        produtos = db.execute("SELECT COUNT(*) FROM produtos").fetchone()[0]
        usuarios = db.execute("SELECT COUNT(*) FROM usuarios").fetchone()[0]
        pedidos = db.execute("SELECT COUNT(*) FROM pedidos").fetchone()[0]
        return jsonify({
            'status': 'ok',
            'database': 'connected',
            'counts': {'produtos': produtos, 'usuarios': usuarios, 'pedidos': pedidos},
            'versao': '1.0.0'
        })

    return app


if __name__ == '__main__':
    app = create_app()
    init_db()
    print('=' * 50)
    print('SERVIDOR INICIADO')
    print(f'Rodando em http://localhost:{PORT}')
    print('=' * 50)
    app.run(host='0.0.0.0', port=PORT, debug=DEBUG)
