# Relatório de Auditoria — Projeto 2

================================
ARCHITECTURE AUDIT REPORT
================================
Project: code-smells-project
Stack:   Python + Flask 3.1.1
Files:   4 analyzed | ~780 lines of code

Summary
CRITICAL: 6 | HIGH: 3 | MEDIUM: 3 | LOW: 2

Findings

[CRITICAL] Hardcoded Credentials / Secrets
File: app.py:7
Description: app.config["SECRET_KEY"] = "minha-chave-super-secreta-123"
             com valor literal hardcoded diretamente no código-fonte.
Impact: Segredo comprometido em qualquer repositório git. Qualquer
        pessoa com acesso ao código pode forjar tokens de sessão.
Recommendation: Substituir por os.environ.get('SECRET_KEY') e definir
                o valor em variável de ambiente ou arquivo .env
                (nunca versionado). Adicionar config/settings.py.

[CRITICAL] Hardcoded Credentials / Secrets — Exposição em Resposta de API
File: controllers.py:289
Description: health_check() retorna "secret_key": "minha-chave-super-secreta-123"
             diretamente no corpo JSON da resposta HTTP pública.
Impact: Qualquer cliente que acesse GET /health obtém o SECRET_KEY
        da aplicação, anulando completamente a proteção de sessões.
Recommendation: Remover secret_key da resposta do health_check.
                Nunca expor segredos em endpoints públicos.

[CRITICAL] SQL Injection — Autenticação Bypassável
File: models.py:109-111
Description: Query de login construída por concatenação de strings:
             "SELECT * FROM usuarios WHERE email = '" + email +
             "' AND senha = '" + senha + "'"
             Qualquer valor como email = "' OR '1'='1" autentica sem senha.
Impact: Bypass completo de autenticação. Atacante acessa qualquer conta
        sem credenciais válidas. Risco máximo de comprometimento de dados.
Recommendation: Usar parâmetros parametrizados:
                db.execute("SELECT * FROM usuarios WHERE email=? AND senha_hash=?",
                (email, hash))

[CRITICAL] SQL Injection — Operações CRUD (múltiplas ocorrências)
File: models.py:28, 47-50, 57-62, 68, 92, 127-130, 174, 280
Description: Todas as queries de produto, usuário e pedido são construídas
             por concatenação direta, exemplos:
             L28:  "SELECT * FROM produtos WHERE id = " + str(id)
             L47:  "INSERT INTO produtos ... VALUES ('" + nome + "', '"...
             L280: "UPDATE pedidos SET status = '" + novo_status + "' WHERE id = " + str(pedido_id)
Impact: Execução de SQL arbitrário em qualquer operação CRUD.
        Possível exfiltração, corrupção ou destruição total do banco.
Recommendation: Substituir todas as concatenações por placeholders "?":
                db.execute("SELECT * FROM produtos WHERE id=?", (id,))

[CRITICAL] SQL Injection — Busca Dinâmica de Produtos
File: models.py:288-297
Description: buscar_produtos() constrói query dinâmica concatenando
             parâmetros da requisição:
             query += " AND (nome LIKE '%" + termo + "%' OR descricao LIKE
             '%" + termo + "%')" e query += " AND categoria = '" + categoria + "'"
Impact: Parâmetros de busca (?q=&categoria=) podem injetar SQL arbitrário
        via query string da URL sem qualquer autenticação.
Recommendation: Usar parâmetros e lista de filtros dinâmica:
                params = []; cláusulas separadas com "?" para cada filtro.

[CRITICAL] Endpoints Administrativos sem Autenticação
File: app.py:47-78
Description: Dois endpoints críticos sem qualquer verificação de identidade:
             /admin/reset-db (POST, L47-57): deleta TODOS os registros
             (itens_pedido, pedidos, produtos, usuarios).
             /admin/query (POST, L59-78): executa SQL arbitrário recebido
             no corpo da requisição — equivale a acesso irrestrito ao banco.
Impact: Qualquer requisição HTTP não autenticada pode apagar todos os dados
        ou executar qualquer operação SQL. Risco de destruição total.
Recommendation: Adicionar middleware de autenticação obrigatório nesses
                endpoints. Considerar remover /admin/query de produção.

[HIGH] God Class / God File
File: models.py:1-314
Description: models.py concentra 314 linhas com funções de 4 domínios
             distintos: get_todos_produtos/criar_produto/atualizar_produto
             (domínio produto), login_usuario/criar_usuario (domínio usuario),
             criar_pedido/get_todos_pedidos (domínio pedido) e
             relatorio_vendas (domínio relatório) — tudo no mesmo arquivo.
Impact: Impossível testar domínios em isolamento. Qualquer alteração em
        lógica de pedido pode quebrar inadvertidamente código de produto.
Recommendation: Separar em models/produto_model.py, models/usuario_model.py,
                models/pedido_model.py, models/relatorio_model.py.

[HIGH] Senhas Armazenadas e Expostas em Texto Plano
File: database.py:75-78 | models.py:80-87, 94-102
Description: Seed data insere senhas literais ("admin123", "123456",
             "senha123") diretamente no banco (database.py:75-78).
             get_todos_usuarios() e get_usuario_por_id() retornam o campo
             "senha" nas respostas JSON (models.py:83, 99) — expondo texto
             plano para qualquer chamador da API.
Impact: Qualquer chamada a GET /usuarios vaza todas as senhas em texto plano.
        Comprometimento completo de credenciais de todos os usuários.
Recommendation: Usar werkzeug.security.generate_password_hash/check_password_hash.
                Nunca incluir o campo senha nas respostas de listagem.

[HIGH] Estado Global Mutável
File: database.py:4, 8-9
Description: db_connection = None declarado como global no módulo.
             get_db() usa "global db_connection" para modificar esse estado:
             a conexão SQLite é compartilhada como singleton entre todas
             as requisições concorrentes.
Impact: check_same_thread=False mascara falhas de thread-safety.
        Em produção com múltiplos workers, corrupção de dados é possível.
        Impossível substituir a conexão em testes unitários.
Recommendation: Usar flask.g para conexão por request, ou connection pool
                adequado. Remover o singleton global.

[MEDIUM] Query N+1
File: models.py:185-200, 219-232
Description: get_pedidos_usuario() e get_todos_pedidos() executam para
             cada pedido: 1 query em itens_pedido e depois 1 query por item
             em produtos (cursor3.execute dentro de loop for item in itens).
             Com 10 pedidos de 5 itens = 60 queries ao invés de 2.
Impact: Degradação exponencial de performance conforme volume de pedidos.
        Timeout em produção com volume real.
Recommendation: Usar JOIN ou subquery única:
                SELECT p.*, ip.*, pr.nome FROM pedidos p
                JOIN itens_pedido ip ON ip.pedido_id = p.id
                JOIN produtos pr ON pr.id = ip.produto_id

[MEDIUM] Error Handling Duplicado
File: controllers.py:10-12, 21-22, 60-62, 95-96 (e mais 9 funções)
Description: Bloco try/except com retorno idêntico repetido em todas as
             13 funções do controllers.py:
             except Exception as e: return jsonify({"erro": str(e)}), 500
             O mesmo padrão aparece em controllers.py inteiro sem variação.
Impact: Manutenção: alterar o formato do erro exige 13 edições. Logs
        inconsistentes pois alguns imprimem o erro (L11, L61) outros não.
Recommendation: Criar middleware centralizado com @app.errorhandler(Exception)
                em app.py e remover os try/except repetidos dos controllers.

[MEDIUM] Validação Ausente nas Rotas
File: controllers.py:168-170
Description: login() chama dados.get("email") sem verificar se dados
             (request.get_json()) retornou None — o que ocorre quando o
             Content-Type não é application/json ou o body está vazio.
             Idêntico em atualizar_status_pedido (L239).
Impact: AttributeError "NoneType has no attribute 'get'" expõe stack
        trace ao cliente e derruba o endpoint.
Recommendation: Verificar if not dados antes de .get(). Usar
                request.get_json(silent=True) e retornar 400 se None.

[LOW] Magic Numbers
File: models.py:257-261 | controllers.py:47, 50, 52
Description: relatorio_vendas() usa literais sem nome: 10000, 5000, 1000
             (limiares de faturamento) e 0.1, 0.05, 0.02 (percentuais
             de desconto). criar_produto() usa 2 e 200 (limites de nome)
             e lista inline de strings para categorias válidas (L52).
Impact: Intenção dos valores ilegível. Alterar percentual de desconto
        exige localizar números em contexto, com risco de edição errada.
Recommendation: Definir constantes nomeadas:
                DESCONTO_PREMIUM = 0.10; LIMITE_FATURAMENTO_PREMIUM = 10000
                NOME_MIN_LEN = 2; NOME_MAX_LEN = 200

[LOW] Nomenclatura Ruim
File: models.py:186-192, 219-224
Description: Variáveis cursor2 e cursor3 usadas em get_pedidos_usuario()
             e get_todos_pedidos() para diferenciar cursores aninhados.
             Nomes não comunicam propósito.
Impact: Dificulta compreensão e manutenção do código com cursores
        aninhados em múltiplos níveis.
Recommendation: Renomear para cursor_itens e cursor_produto ou,
                preferencialmente, eliminar os cursores aninhados
                resolvendo o N+1 com JOIN.

================================
Total: 14 findings
================================
