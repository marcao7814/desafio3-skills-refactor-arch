from database import db
from models.category import Category
from models.task import Task
from config.constants import DEFAULT_COLOR
from utils.helpers import is_valid_color, sanitize_string
from controllers.errors import NotFoundError


def _task_counts_by_category():
    return dict(
        db.session.query(Task.category_id, db.func.count(Task.id))
        .group_by(Task.category_id)
        .all()
    )


def list_categories():
    categories = Category.query.all()
    counts = _task_counts_by_category()
    result = []
    for c in categories:
        data = c.to_dict()
        data['task_count'] = counts.get(c.id, 0)
        result.append(data)
    return result


def create_category(data):
    name = sanitize_string(data.get('name'))
    if not name:
        raise ValueError('Nome é obrigatório')

    color = data.get('color', DEFAULT_COLOR)
    if not is_valid_color(color):
        raise ValueError('Cor inválida. Use o formato hexadecimal (#RRGGBB)')

    category = Category(
        name=name,
        description=data.get('description', ''),
        color=color,
    )
    db.session.add(category)
    db.session.commit()
    return category.to_dict()


def update_category(cat_id, data):
    category = Category.query.get(cat_id)
    if not category:
        raise NotFoundError('Categoria não encontrada')

    if 'name' in data:
        category.name = sanitize_string(data['name'])
    if 'description' in data:
        category.description = data['description']
    if 'color' in data:
        if not is_valid_color(data['color']):
            raise ValueError('Cor inválida. Use o formato hexadecimal (#RRGGBB)')
        category.color = data['color']

    db.session.commit()
    return category.to_dict()


def delete_category(cat_id):
    category = Category.query.get(cat_id)
    if not category:
        raise NotFoundError('Categoria não encontrada')
    db.session.delete(category)
    db.session.commit()
