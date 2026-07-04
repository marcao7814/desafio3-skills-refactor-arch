def get_stats_pedidos(db):
    total = db.execute("SELECT COUNT(*) FROM pedidos").fetchone()[0]
    faturamento = db.execute("SELECT COALESCE(SUM(total), 0) FROM pedidos").fetchone()[0]
    pendentes = db.execute("SELECT COUNT(*) FROM pedidos WHERE status='pendente'").fetchone()[0]
    aprovados = db.execute("SELECT COUNT(*) FROM pedidos WHERE status='aprovado'").fetchone()[0]
    cancelados = db.execute("SELECT COUNT(*) FROM pedidos WHERE status='cancelado'").fetchone()[0]
    return {
        'total_pedidos': total,
        'faturamento': faturamento,
        'pendentes': pendentes,
        'aprovados': aprovados,
        'cancelados': cancelados,
    }
