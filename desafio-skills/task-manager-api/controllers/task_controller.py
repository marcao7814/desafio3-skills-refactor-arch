from datetime import datetime

from sqlalchemy.orm import joinedload

from database import db
from models.task import Task
from models.user import User
from models.category import Category
from config.constants import (
    VALID_STATUSES,
    MIN_TITLE_LENGTH,
    MAX_TITLE_LENGTH,
    MIN_PRIORITY,
    MAX_PRIORITY,
    DEFAULT_PRIORITY,
)
from utils.helpers import parse_date, sanitize_string, calculate_percentage
from controllers.errors import NotFoundError


def _validate_title(title):
    if not title or len(title) < MIN_TITLE_LENGTH:
        raise ValueError(f'Título deve ter no mínimo {MIN_TITLE_LENGTH} caracteres')
    if len(title) > MAX_TITLE_LENGTH:
        raise ValueError(f'Título deve ter no máximo {MAX_TITLE_LENGTH} caracteres')


def _validate_status(status):
    if status not in VALID_STATUSES:
        raise ValueError('Status inválido')


def _validate_priority(priority):
    if priority is None or priority < MIN_PRIORITY or priority > MAX_PRIORITY:
        raise ValueError(f'Prioridade deve ser entre {MIN_PRIORITY} e {MAX_PRIORITY}')


def _serialize_with_relations(task):
    data = task.to_dict()
    data['user_name'] = task.user.name if task.user else None
    data['category_name'] = task.category.name if task.category else None
    return data


def _tags_to_string(tags):
    return ','.join(tags) if isinstance(tags, list) else tags


def list_tasks():
    tasks = Task.query.options(joinedload(Task.user), joinedload(Task.category)).all()
    return [_serialize_with_relations(t) for t in tasks]


def get_task(task_id):
    task = Task.query.options(joinedload(Task.user), joinedload(Task.category)).get(task_id)
    if not task:
        raise NotFoundError('Task não encontrada')
    return _serialize_with_relations(task)


def create_task(data):
    title = sanitize_string(data.get('title'))
    _validate_title(title)

    status = data.get('status', 'pending')
    _validate_status(status)

    priority = data.get('priority', DEFAULT_PRIORITY)
    _validate_priority(priority)

    user_id = data.get('user_id')
    if user_id and not User.query.get(user_id):
        raise NotFoundError('Usuário não encontrado')

    category_id = data.get('category_id')
    if category_id and not Category.query.get(category_id):
        raise NotFoundError('Categoria não encontrada')

    task = Task(
        title=title,
        description=data.get('description', ''),
        status=status,
        priority=priority,
        user_id=user_id,
        category_id=category_id,
    )

    due_date = data.get('due_date')
    if due_date:
        parsed = parse_date(due_date)
        if not parsed:
            raise ValueError('Formato de data inválido. Use YYYY-MM-DD')
        task.due_date = parsed

    tags = data.get('tags')
    if tags:
        task.tags = _tags_to_string(tags)

    db.session.add(task)
    db.session.commit()
    return task.to_dict()


def update_task(task_id, data):
    task = Task.query.get(task_id)
    if not task:
        raise NotFoundError('Task não encontrada')

    if 'title' in data:
        title = sanitize_string(data['title'])
        _validate_title(title)
        task.title = title

    if 'description' in data:
        task.description = data['description']

    if 'status' in data:
        _validate_status(data['status'])
        task.status = data['status']

    if 'priority' in data:
        _validate_priority(data['priority'])
        task.priority = data['priority']

    if 'user_id' in data:
        if data['user_id'] and not User.query.get(data['user_id']):
            raise NotFoundError('Usuário não encontrado')
        task.user_id = data['user_id']

    if 'category_id' in data:
        if data['category_id'] and not Category.query.get(data['category_id']):
            raise NotFoundError('Categoria não encontrada')
        task.category_id = data['category_id']

    if 'due_date' in data:
        if data['due_date']:
            parsed = parse_date(data['due_date'])
            if not parsed:
                raise ValueError('Formato de data inválido. Use YYYY-MM-DD')
            task.due_date = parsed
        else:
            task.due_date = None

    if 'tags' in data:
        task.tags = _tags_to_string(data['tags'])

    task.updated_at = datetime.utcnow()
    db.session.commit()
    return task.to_dict()


def delete_task(task_id):
    task = Task.query.get(task_id)
    if not task:
        raise NotFoundError('Task não encontrada')
    db.session.delete(task)
    db.session.commit()


def search_tasks(query, status, priority, user_id):
    tasks = Task.query

    if query:
        tasks = tasks.filter(
            db.or_(
                Task.title.like(f'%{query}%'),
                Task.description.like(f'%{query}%'),
            )
        )
    if status:
        tasks = tasks.filter(Task.status == status)
    if priority:
        tasks = tasks.filter(Task.priority == int(priority))
    if user_id:
        tasks = tasks.filter(Task.user_id == int(user_id))

    return [t.to_dict() for t in tasks.all()]


def task_stats():
    total = Task.query.count()
    by_status = {status: Task.query.filter_by(status=status).count() for status in VALID_STATUSES}
    overdue = sum(1 for t in Task.query.all() if t.is_overdue())

    return {
        'total': total,
        'pending': by_status['pending'],
        'in_progress': by_status['in_progress'],
        'done': by_status['done'],
        'cancelled': by_status['cancelled'],
        'overdue': overdue,
        'completion_rate': calculate_percentage(by_status['done'], total),
    }


def get_tasks_by_user(user_id):
    if not User.query.get(user_id):
        raise NotFoundError('Usuário não encontrado')
    return [t.to_dict() for t in Task.query.filter_by(user_id=user_id).all()]
