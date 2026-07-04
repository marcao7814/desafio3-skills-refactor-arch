from datetime import datetime, timedelta

from database import db
from models.task import Task
from models.user import User
from models.category import Category
from config.constants import VALID_STATUSES
from utils.helpers import calculate_percentage
from controllers.errors import NotFoundError


def build_summary_report():
    total_tasks = Task.query.count()
    total_users = User.query.count()
    total_categories = Category.query.count()

    by_status = {status: Task.query.filter_by(status=status).count() for status in VALID_STATUSES}
    by_priority = {p: Task.query.filter_by(priority=p).count() for p in range(1, 6)}

    overdue_tasks = [t for t in Task.query.all() if t.is_overdue()]

    seven_days_ago = datetime.utcnow() - timedelta(days=7)
    recent_tasks = Task.query.filter(Task.created_at >= seven_days_ago).count()
    recent_done = Task.query.filter(
        Task.status == 'done',
        Task.updated_at >= seven_days_ago,
    ).count()

    total_counts = dict(
        db.session.query(Task.user_id, db.func.count(Task.id))
        .group_by(Task.user_id)
        .all()
    )
    done_counts = dict(
        db.session.query(Task.user_id, db.func.count(Task.id))
        .filter(Task.status == 'done')
        .group_by(Task.user_id)
        .all()
    )

    user_stats = []
    for u in User.query.all():
        total = total_counts.get(u.id, 0)
        completed = done_counts.get(u.id, 0)
        user_stats.append({
            'user_id': u.id,
            'user_name': u.name,
            'total_tasks': total,
            'completed_tasks': completed,
            'completion_rate': calculate_percentage(completed, total),
        })

    return {
        'generated_at': str(datetime.utcnow()),
        'overview': {
            'total_tasks': total_tasks,
            'total_users': total_users,
            'total_categories': total_categories,
        },
        'tasks_by_status': {
            'pending': by_status['pending'],
            'in_progress': by_status['in_progress'],
            'done': by_status['done'],
            'cancelled': by_status['cancelled'],
        },
        'tasks_by_priority': {
            'critical': by_priority[1],
            'high': by_priority[2],
            'medium': by_priority[3],
            'low': by_priority[4],
            'minimal': by_priority[5],
        },
        'overdue': {
            'count': len(overdue_tasks),
            'tasks': [
                {
                    'id': t.id,
                    'title': t.title,
                    'due_date': str(t.due_date),
                    'days_overdue': (datetime.utcnow() - t.due_date).days,
                }
                for t in overdue_tasks
            ],
        },
        'recent_activity': {
            'tasks_created_last_7_days': recent_tasks,
            'tasks_completed_last_7_days': recent_done,
        },
        'user_productivity': user_stats,
    }


def build_user_report(user_id):
    user = User.query.get(user_id)
    if not user:
        raise NotFoundError('Usuário não encontrado')

    tasks = Task.query.filter_by(user_id=user_id).all()
    total = len(tasks)
    by_status = {status: 0 for status in VALID_STATUSES}
    overdue = 0
    high_priority = 0

    for t in tasks:
        by_status[t.status] = by_status.get(t.status, 0) + 1
        if t.priority <= 2:
            high_priority += 1
        if t.is_overdue():
            overdue += 1

    return {
        'user': {
            'id': user.id,
            'name': user.name,
            'email': user.email,
        },
        'statistics': {
            'total_tasks': total,
            'done': by_status['done'],
            'pending': by_status['pending'],
            'in_progress': by_status['in_progress'],
            'cancelled': by_status['cancelled'],
            'overdue': overdue,
            'high_priority': high_priority,
            'completion_rate': calculate_percentage(by_status['done'], total),
        },
    }
