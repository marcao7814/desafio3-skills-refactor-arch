from models.usuario_model import (
    get_all_usuarios, get_usuario_by_id, get_usuario_by_email,
    create_usuario, verify_password
)


def listar_usuarios(db):
    return get_all_usuarios(db)


def buscar_usuario(db, usuario_id):
    usuario = get_usuario_by_id(db, usuario_id)
    if not usuario:
        raise ValueError('Usuário não encontrado')
    return usuario


def registrar_usuario(db, dados):
    if not dados:
        raise ValueError('Dados inválidos')
    nome = dados.get('nome', '')
    email = dados.get('email', '')
    senha = dados.get('senha', '')
    if not nome or not email or not senha:
        raise ValueError('Nome, email e senha são obrigatórios')
    return create_usuario(db, nome, email, senha)


def autenticar(db, dados):
    if not dados:
        raise ValueError('Dados inválidos')
    email = dados.get('email', '')
    senha = dados.get('senha', '')
    if not email or not senha:
        raise ValueError('Email e senha são obrigatórios')
    usuario = get_usuario_by_email(db, email)
    if not usuario or not verify_password(usuario, senha):
        raise PermissionError('Email ou senha inválidos')
    return {
        'id': usuario['id'],
        'nome': usuario['nome'],
        'email': usuario['email'],
        'tipo': usuario['tipo']
    }
