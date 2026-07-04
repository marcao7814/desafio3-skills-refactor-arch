from itsdangerous import URLSafeTimedSerializer, BadSignature, SignatureExpired

from database import db
from models.user import User
from models.task import Task
from config.settings import SECRET_KEY
from config.constants import VALID_ROLES, MIN_PASSWORD_LENGTH, TOKEN_MAX_AGE_SECONDS
from utils.helpers import validate_email, sanitize_string
from controllers.errors import NotFoundError, ConflictError, UnauthorizedError, ForbiddenError

_serializer = URLSafeTimedSerializer(SECRET_KEY)


def generate_token(user_id):
    return _serializer.dumps({'user_id': user_id})


def verify_token(token):
    try:
        data = _serializer.loads(token, max_age=TOKEN_MAX_AGE_SECONDS)
        return data.get('user_id')
    except (BadSignature, SignatureExpired):
        return None


def _validate_role(role):
    if role not in VALID_ROLES:
        raise ValueError('Role inválido')


def _task_counts_by_user():
    return dict(
        db.session.query(Task.user_id, db.func.count(Task.id))
        .group_by(Task.user_id)
        .all()
    )


def list_users():
    users = User.query.all()
    counts = _task_counts_by_user()
    result = []
    for u in users:
        data = u.to_dict()
        data['task_count'] = counts.get(u.id, 0)
        result.append(data)
    return result


def get_user(user_id):
    user = User.query.get(user_id)
    if not user:
        raise NotFoundError('Usuário não encontrado')
    data = user.to_dict()
    data['tasks'] = [t.to_dict() for t in Task.query.filter_by(user_id=user_id).all()]
    return data


def create_user(data):
    name = sanitize_string(data.get('name'))
    email = data.get('email')
    password = data.get('password')
    role = data.get('role', 'user')

    if not name:
        raise ValueError('Nome é obrigatório')
    if not email:
        raise ValueError('Email é obrigatório')
    if not password:
        raise ValueError('Senha é obrigatória')
    if not validate_email(email):
        raise ValueError('Email inválido')
    if len(password) < MIN_PASSWORD_LENGTH:
        raise ValueError(f'Senha deve ter no mínimo {MIN_PASSWORD_LENGTH} caracteres')
    _validate_role(role)

    if User.query.filter_by(email=email).first():
        raise ConflictError('Email já cadastrado')

    user = User(name=name, email=email, role=role)
    user.set_password(password)

    db.session.add(user)
    db.session.commit()
    return user.to_dict()


def update_user(user_id, data):
    user = User.query.get(user_id)
    if not user:
        raise NotFoundError('Usuário não encontrado')

    if 'name' in data:
        user.name = sanitize_string(data['name'])

    if 'email' in data:
        if not validate_email(data['email']):
            raise ValueError('Email inválido')
        existing = User.query.filter_by(email=data['email']).first()
        if existing and existing.id != user_id:
            raise ConflictError('Email já cadastrado')
        user.email = data['email']

    if 'password' in data:
        if len(data['password']) < MIN_PASSWORD_LENGTH:
            raise ValueError(f'Senha deve ter no mínimo {MIN_PASSWORD_LENGTH} caracteres')
        user.set_password(data['password'])

    if 'role' in data:
        _validate_role(data['role'])
        user.role = data['role']

    if 'active' in data:
        user.active = data['active']

    db.session.commit()
    return user.to_dict()


def delete_user(user_id):
    user = User.query.get(user_id)
    if not user:
        raise NotFoundError('Usuário não encontrado')

    Task.query.filter_by(user_id=user_id).delete()
    db.session.delete(user)
    db.session.commit()


def login(email, password):
    if not email or not password:
        raise ValueError('Email e senha são obrigatórios')

    user = User.query.filter_by(email=email).first()
    if not user or not user.check_password(password):
        raise UnauthorizedError('Credenciais inválidas')

    if not user.active:
        raise ForbiddenError('Usuário inativo')

    return {
        'message': 'Login realizado com sucesso',
        'user': user.to_dict(),
        'token': generate_token(user.id),
    }
