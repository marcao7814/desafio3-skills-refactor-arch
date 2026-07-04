# Relatório de Auditoria — code-smells-project

> Gerado pela skill `/refactor-arch` — Fase 2.

================================
ARCHITECTURE AUDIT REPORT
================================
Project: code-smells-project
Stack:   Python + Flask 3.1.1
Files:   4 analyzed | ~784 lines of code

Summary
CRITICAL: 6 | HIGH: 3 | MEDIUM: 3 | LOW: 2

Findings

[CRITICAL] Hardcoded Credentials / Secrets
File: app.py:7
Description: app.config["SECRET_KEY"] = "minha-chave-super-secreta-123"
             com valor literal hardcoded diretamente no código-fonte.
Impact: Segredo comprometido em qualquer repositório git. Qualquer
        pessoa com acesso ao código pode forjar tokens de sessão.
Recommendation: Substituir por os.environ.get('SECRET_KEY') carregado de
                .env (nunca versionado) via config/settings.py.

[CRITICAL] Hardcoded Credentials / Secrets — Exposição em Resposta de API
File: controllers.py:289
Description: health_check() retorna "secret_key": "minha-chave-super-secreta-123"
             diretamente no corpo JSON da resposta HTTP pública.
Impact: Qualquer cliente que acesse GET /health obtém o SECRET_KEY da
        aplicação, anulando completamente a proteção de sessões.
Recommendation: Remover secret_key da resposta do health_check. Nunca
                expor segredos em endpoints públicos.

[CRITICAL] SQL Injection — Autenticação Bypassável
File: models.py:109-111
Description: Query de login construída por concatenação de strings:
             "SELECT * FROM usuarios WHERE email = '" + email +
             "' AND senha = '" + senha + "'"
             Um valor como email = "' OR '1'='1" autentica sem senha.
Impact: Bypass completo de autenticação. Atacante acessa qualquer conta
        sem credenciais válidas. Risco máximo de comprometimento de dados.
Recommendation: Usar parâmetros: db.execute("SELECT * FROM usuarios WHERE
                email=? AND senha_hash=?", (email, hash)).

[CRITICAL] SQL Injection — Operações CRUD (múltiplas ocorrências)
File: models.py:28, 47-50, 57-62, 68, 92, 126-130, 140, 148-166, 174, 280
Description: Todas as queries de produto, usuário e pedido são construídas
             por concatenação direta, ex.: L28 "SELECT * FROM produtos
             WHERE id = " + str(id); L47-50 INSERT com nome/descrição
             concatenados; L280 UPDATE pedidos SET status = '" +
             novo_status + "'.
Impact: Execução de SQL arbitrário em qualquer operação CRUD. Possível
        exfiltração, corrupção ou destruição total do banco.
Recommendation: Substituir todas as concatenações por placeholders "?":
                db.execute("SELECT * FROM produtos WHERE id=?", (id,)).

[CRITICAL] SQL Injection — Busca Dinâmica de Produtos
File: models.py:288-297
Description: buscar_produtos() concatena parâmetros vindos da query string
             diretamente na cláusula WHERE: query += " AND (nome LIKE '%"
             + termo + "%' ...)" e "AND categoria = '" + categoria + "'".
Impact: Parâmetros de busca (?q=&categoria=) permitem injetar SQL
        arbitrário sem qualquer autenticação prévia.
Recommendation: Usar lista de cláusulas parametrizadas com "?" e params=[]
                acumulado por filtro ativo.

[CRITICAL] Endpoints Administrativos sem Autenticação
File: app.py:47-78
Description: /admin/reset-db (POST, L47-57) deleta todos os registros de
             itens_pedido, pedidos, produtos e usuarios sem checar
             identidade. /admin/query (POST, L59-78) executa qualquer SQL
             recebido no corpo da requisição.
Impact: Qualquer requisição HTTP não autenticada apaga todos os dados ou
        executa SQL arbitrário. Risco de destruição total do sistema.
Recommendation: Adicionar middleware de autenticação/autorização obrigatório
                nesses endpoints; remover /admin/query em produção.

[HIGH] God Class / God File
File: models.py:1-315, controllers.py:1-293
Description: models.py concentra funções de 4 domínios distintos
             (produto, usuário, pedido, relatório) no mesmo arquivo;
             controllers.py replica a mesma mistura no nível de rota.
Impact: Impossível testar domínios isoladamente. Alteração em lógica de
        pedido pode quebrar inadvertidamente código de produto/usuário.
Recommendation: Separar em models/produto_model.py, usuario_model.py,
                pedido_model.py, relatorio_model.py e controllers
                equivalentes por domínio.

[HIGH] Senhas Armazenadas e Expostas em Texto Plano
File: database.py:75-83 | models.py:83, 99
Description: Seed data insere senhas literais ("admin123", "123456",
             "senha123") em texto plano (database.py:75-83).
             get_todos_usuarios() (models.py:83) e get_usuario_por_id()
             (models.py:99) retornam o campo "senha" cru nas respostas JSON.
Impact: GET /usuarios vaza todas as senhas em texto plano — comprometimento
        completo de credenciais de todos os usuários.
Recommendation: Usar werkzeug.security.generate_password_hash /
                check_password_hash; nunca incluir "senha" nas respostas.

[HIGH] Estado Global Mutável
File: database.py:4, 8-9
Description: db_connection = None é global no módulo; get_db() usa
             "global db_connection" para atribuir e reaproveitar a mesma
             conexão SQLite (check_same_thread=False) entre requisições.
Impact: Corrupção de dados possível em produção com múltiplos workers;
        impossível substituir a conexão em testes unitários isolados.
Recommendation: Usar flask.g por request ou um connection pool adequado;
                eliminar o singleton global.

[MEDIUM] Query N+1
File: models.py:171-201, 203-233
Description: get_pedidos_usuario() e get_todos_pedidos() abrem cursor2
             para itens_pedido e, para cada item, cursor3 para buscar o
             produto (L187-199 e L219-231) — 10 pedidos de 5 itens geram
             ~60 queries em vez de 2.
Impact: Degradação de performance que cresce com o volume de pedidos;
        risco de timeout em produção com dados reais.
Recommendation: Substituir por JOIN único: SELECT p.*, ip.*, pr.nome FROM
                pedidos p JOIN itens_pedido ip ON ... JOIN produtos pr ON ...

[MEDIUM] Error Handling Duplicado
File: controllers.py:10-12, 21-22, 60-62, 95-96 (e mais 9 funções)
Description: O bloco except Exception as e: return jsonify({"erro":
             str(e)}), 500 é repetido de forma idêntica em praticamente
             todas as 13 funções do arquivo, com print() inconsistente
             (algumas logam, outras não).
Impact: Alterar o formato de erro exige editar 13 lugares; logging
        inconsistente dificulta observabilidade.
Recommendation: Centralizar em @app.errorhandler(Exception) em app.py e
                remover os try/except repetidos dos controllers.

[MEDIUM] Validação Ausente nas Rotas
File: controllers.py:167-171, 237-240
Description: login() chama dados.get("email") sem checar se
             request.get_json() retornou None (ocorre quando o body não é
             application/json ou está vazio); mesmo padrão em
             atualizar_status_pedido.
Impact: AttributeError "NoneType has no attribute 'get'" derruba o
        endpoint e expõe stack trace ao cliente.
Recommendation: Usar request.get_json(silent=True) e retornar 400 se None,
                antes de qualquer .get().

[LOW] Magic Numbers
File: models.py:256-262 | controllers.py:47-52
Description: relatorio_vendas() usa literais sem nome (10000, 5000, 1000
             e 0.1, 0.05, 0.02 para desconto); criar_produto() usa 2 e 200
             como limites de nome e uma lista inline de categorias válidas.
Impact: Intenção dos valores ilegível; alterar um percentual de desconto
        exige localizar números soltos, com risco de edição incorreta.
Recommendation: Extrair constantes nomeadas em config/constants.py:
                DESCONTO_PREMIUM = 0.10, NOME_MIN_LEN = 2, etc.

[LOW] Nomenclatura Ruim
File: models.py:187, 191, 219, 223
Description: Variáveis cursor2 e cursor3 usadas em get_pedidos_usuario()
             e get_todos_pedidos() para diferenciar cursores aninhados,
             sem comunicar propósito.
Impact: Dificulta leitura e manutenção do código com cursores aninhados
        em múltiplos níveis.
Recommendation: Eliminar os cursores aninhados resolvendo o N+1 com JOIN
                (torna a renomeação desnecessária).

================================
Total: 14 findings
================================

---

## Status pós-refatoração (Fase 3)

Todos os 14 findings foram corrigidos na nova estrutura MVC em `src/`
(ver árvore e validação no resultado da Fase 3). Os arquivos legados
citados acima (`app.py`, `controllers.py`, `models.py`, `database.py`
na raiz) foram removidos do projeto.
