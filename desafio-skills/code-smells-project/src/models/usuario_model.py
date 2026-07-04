from werkzeug.security import generate_password_hash, check_password_hash


def get_all_usuarios(db):
    rows = db.execute(
        "SELECT id, nome, email, tipo, criado_em FROM usuarios"
    ).fetchall()
    return [dict(row) for row in rows]


def get_usuario_by_id(db, usuario_id):
    row = db.execute(
        "SELECT id, nome, email, tipo, criado_em FROM usuarios WHERE id=?",
        (usuario_id,)
    ).fetchone()
    return dict(row) if row else None


def get_usuario_by_email(db, email):
    row = db.execute(
        "SELECT * FROM usuarios WHERE email=?", (email,)
    ).fetchone()
    return dict(row) if row else None


def create_usuario(db, nome, email, senha, tipo='cliente'):
    cursor = db.execute(
        "INSERT INTO usuarios (nome, email, senha_hash, tipo) VALUES (?, ?, ?, ?)",
        (nome, email, generate_password_hash(senha), tipo)
    )
    db.commit()
    return cursor.lastrowid


def verify_password(usuario, senha):
    return check_password_hash(usuario['senha_hash'], senha)
