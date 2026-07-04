from models.relatorio_model import get_stats_pedidos
from config.constants import (
    LIMITE_DESCONTO_ALTO, LIMITE_DESCONTO_MEDIO, LIMITE_DESCONTO_BAIXO,
    DESCONTO_ALTO, DESCONTO_MEDIO, DESCONTO_BAIXO
)


def gerar_relatorio_vendas(db):
    stats = get_stats_pedidos(db)
    faturamento = stats['faturamento']
    total_pedidos = stats['total_pedidos']

    if faturamento > LIMITE_DESCONTO_ALTO:
        desconto = faturamento * DESCONTO_ALTO
    elif faturamento > LIMITE_DESCONTO_MEDIO:
        desconto = faturamento * DESCONTO_MEDIO
    elif faturamento > LIMITE_DESCONTO_BAIXO:
        desconto = faturamento * DESCONTO_BAIXO
    else:
        desconto = 0

    ticket_medio = round(faturamento / total_pedidos, 2) if total_pedidos > 0 else 0

    return {
        'total_pedidos': total_pedidos,
        'faturamento_bruto': round(faturamento, 2),
        'desconto_aplicavel': round(desconto, 2),
        'faturamento_liquido': round(faturamento - desconto, 2),
        'pedidos_pendentes': stats['pendentes'],
        'pedidos_aprovados': stats['aprovados'],
        'pedidos_cancelados': stats['cancelados'],
        'ticket_medio': ticket_medio
    }
