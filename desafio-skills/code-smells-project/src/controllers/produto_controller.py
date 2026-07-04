from models.produto_model import (
    get_all_produtos, get_produto_by_id, search_produtos,
    create_produto, update_produto, delete_produto
)
from config.constants import CATEGORIAS_VALIDAS, NOME_MIN_LEN, NOME_MAX_LEN


def listar_produtos(db):
    return get_all_produtos(db)


def buscar_produto(db, produto_id):
    produto = get_produto_by_id(db, produto_id)
    if not produto:
        raise LookupError('Produto não encontrado')
    return produto


def pesquisar_produtos(db, termo='', categoria=None, preco_min=None, preco_max=None):
    return search_produtos(db, termo, categoria, preco_min, preco_max)


def criar_produto(db, dados):
    _validar_dados_produto(dados)
    return create_produto(
        db,
        dados['nome'],
        dados.get('descricao', ''),
        dados['preco'],
        dados['estoque'],
        dados.get('categoria', 'geral')
    )


def atualizar_produto(db, produto_id, dados):
    if not get_produto_by_id(db, produto_id):
        raise LookupError('Produto não encontrado')
    _validar_dados_produto(dados)
    update_produto(
        db,
        produto_id,
        dados['nome'],
        dados.get('descricao', ''),
        dados['preco'],
        dados['estoque'],
        dados.get('categoria', 'geral')
    )


def remover_produto(db, produto_id):
    if not get_produto_by_id(db, produto_id):
        raise LookupError('Produto não encontrado')
    delete_produto(db, produto_id)


def _validar_dados_produto(dados):
    if not dados:
        raise ValueError('Dados inválidos')
    for campo in ('nome', 'preco', 'estoque'):
        if campo not in dados:
            raise ValueError(f'{campo} é obrigatório')
    nome = dados['nome']
    if len(nome) < NOME_MIN_LEN:
        raise ValueError('Nome muito curto')
    if len(nome) > NOME_MAX_LEN:
        raise ValueError('Nome muito longo')
    if dados['preco'] < 0:
        raise ValueError('Preço não pode ser negativo')
    if dados['estoque'] < 0:
        raise ValueError('Estoque não pode ser negativo')
    categoria = dados.get('categoria', 'geral')
    if categoria not in CATEGORIAS_VALIDAS:
        raise ValueError(f'Categoria inválida. Válidas: {CATEGORIAS_VALIDAS}')
