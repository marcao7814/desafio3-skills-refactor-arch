# Audit Report — task-manager-api

> Gerado pela skill `/refactor-arch` — Fase 2.

```
================================
ARCHITECTURE AUDIT REPORT
================================
Project: task-manager-api
Stack:   Python + Flask 3.0.0 (Flask-SQLAlchemy 3.1.1)
Files:   16 analyzed | ~1256 lines of code

Summary
CRITICAL: 5 | HIGH: 5 | MEDIUM: 5 | LOW: 2

Findings

[CRITICAL] Hardcoded Credentials / Secrets
File: app.py:13
Description: app.config['SECRET_KEY'] = 'super-secret-key-123' está fixo no código-fonte, mesmo existindo um .env.example com SECRET_KEY. O valor nunca é lido de variável de ambiente.
Impact: Chave de sessão exposta no controle de versão; qualquer pessoa com acesso ao repositório pode forjar cookies/sessões assinadas pela aplicação.
Recommendation: Mover para config/settings.py usando os.environ.get('SECRET_KEY', 'dev-only-insecure-default') e carregar via python-dotenv (já presente no requirements.txt mas não utilizado).

[CRITICAL] Hardcoded Credentials / Secrets
File: services/notification_service.py:7-10
Description: email_host, email_user e email_password ('senha123') estão hardcoded dentro do __init__ da classe NotificationService.
Impact: Credenciais de e-mail SMTP expostas no repositório; comprometimento da conta de e-mail se o código vazar.
Recommendation: Extrair para config/settings.py e ler via os.environ.get('EMAIL_PASSWORD'), nunca com valor literal no código.

[CRITICAL] Hash de Senha com Algoritmo Inseguro (MD5)
File: models/user.py:29,32
Description: set_password() e check_password() usam hashlib.md5(pwd.encode()).hexdigest() para armazenar e comparar senhas. MD5 é criptograficamente quebrado e sem salt, vulnerável a rainbow tables e colisões.
Impact: Senhas de usuários podem ser recuperadas por força bruta/rainbow table em caso de vazamento do banco de dados.
Recommendation: Usar werkzeug.security.generate_password_hash/check_password_hash (já disponível via Flask) ou bcrypt/argon2, sempre com salt.

[CRITICAL] Autenticação Falsa (Token Fixo Previsível)
File: routes/user_routes.py:210
Description: O endpoint /login retorna 'token': 'fake-jwt-token-' + str(user.id) — um "token" totalmente previsível baseado apenas no ID do usuário, sem assinatura ou expiração. Nenhuma rota protegida sequer valida esse token.
Impact: Qualquer requisição pode se passar por qualquer usuário simplesmente montando a string 'fake-jwt-token-<id>'; não há controle de acesso real na API.
Recommendation: Implementar JWT real (ex: flask-jwt-extended) com assinatura via SECRET_KEY vindo de config, expiração e validação obrigatória via middleware/decorator em todas as rotas protegidas.

[CRITICAL] God File — Múltiplos Domínios em Um Único Arquivo de Rotas
File: routes/report_routes.py:1-223
Description: Um único blueprint mistura queries e lógica de negócio de 3 domínios distintos (tasks, users, categories): summary_report (linhas 13-101) agrega Task+User+Category, user_report (103-155) cruza Task+User, e o CRUD completo de categorias (157-223) faz queries diretas sem camada de serviço.
Impact: Qualquer mudança em uma entidade arrisca quebrar relatórios de outra; impossível testar cada domínio isoladamente; arquivo cresce sem limite conforme novos relatórios são adicionados.
Recommendation: Separar em controllers/report_controller.py (lógica/agregação) + views/report_routes.py (rotas finas) + controllers/category_controller.py dedicado para o CRUD de categorias.

[HIGH] God File — Controller de Tasks Concentra Query + Lógica + Validação + Formatação
File: routes/task_routes.py:1-299
Description: Arquivo de 299 linhas onde cada rota (get_tasks, create_task, update_task, search_tasks, task_stats) executa queries SQLAlchemy, valida payload manualmente, calcula overdue e monta o dicionário de resposta, tudo na mesma função.
Impact: Duplicação massiva de lógica (overdue calculado 3x no mesmo arquivo), dificuldade de manutenção e testes unitários impossíveis sem subir o Flask inteiro.
Recommendation: Extrair para controllers/task_controller.py (validação + regras) e models/task_model.py (acesso a dados), deixando routes/task_routes.py apenas com roteamento.

[HIGH] God File — Controller de Usuários Mistura Domínio de Tasks
File: routes/user_routes.py:1-211
Description: Blueprint de usuários contém get_user_tasks (153-183) que reimplementa manualmente toda a serialização e cálculo de overdue de Task, além do CRUD de User e login — múltiplas responsabilidades no mesmo arquivo.
Impact: Alteração na regra de "overdue" precisa ser replicada em 3+ arquivos diferentes; alto risco de inconsistência entre respostas de endpoints diferentes.
Recommendation: Mover get_user_tasks para controllers/task_controller.py (reaproveitando a mesma função usada por /tasks) e manter user_routes.py focado apenas em User.

[HIGH] Lógica de Negócio Duplicada Ignorando Métodos Já Existentes no Model
File: routes/report_routes.py:33-43,132-135; routes/task_routes.py:30-39,71-80,283-287; routes/user_routes.py:171-180
Description: A verificação "due_date < utcnow() and status not in (done, cancelled)" é reescrita manualmente com if/else aninhados em pelo menos 6 lugares diferentes, mesmo o model Task já definir is_overdue() em models/task.py:50-60 (nunca chamado) e validate_status()/validate_priority() (models/task.py:38-48, também nunca chamados).
Impact: Qualquer correção na regra de "atrasado" exige editar 6 arquivos/funções; alto risco de divergência (um endpoint já pode ficar desatualizado em relação aos outros).
Recommendation: Usar task.is_overdue() em todos os pontos e substituir as validações manuais de status/priority pelas já existentes no model (ou movê-las para o controller).

[HIGH] Lógica de Negócio no Controller/Route
File: routes/report_routes.py:13-101
Description: A função summary_report tem 88 linhas e realiza toda a agregação estatística (contagens por status/prioridade, cálculo de overdue, produtividade por usuário) diretamente no handler da rota, sem nenhuma camada intermediária.
Impact: Impossível testar a lógica de relatório sem subir o servidor Flask completo; rota difícil de ler e manter.
Recommendation: Extrair para controllers/report_controller.py::build_summary_report(), deixando a rota apenas com `return jsonify(build_summary_report()), 200`.

[MEDIUM] Query N+1
File: routes/task_routes.py:41-57 (get_tasks)
Description: Para cada task retornada pelo Task.query.all(), o código executa User.query.get(t.user_id) e Category.query.get(t.category_id) dentro do loop for.
Impact: Uma listagem de 100 tasks gera até 200 queries adicionais ao banco, degradando performance conforme a tabela cresce.
Recommendation: Usar eager loading do SQLAlchemy (joinedload(Task.user), joinedload(Task.category)) em uma única query.

[MEDIUM] Query N+1
File: routes/report_routes.py:53-68 (summary_report) e routes/report_routes.py:157-165 (get_categories)
Description: user_stats faz Task.query.filter_by(user_id=u.id).all() dentro do loop `for u in users`, e get_categories faz Task.query.filter_by(category_id=c.id).count() dentro do loop `for c in categories`.
Impact: Relatório de resumo e listagem de categorias ficam O(N) em número de queries, lentos à medida que a base cresce.
Recommendation: Substituir por uma única query agregada (db.session.query(Task.user_id, func.count()).group_by(Task.user_id)).

[MEDIUM] Validação Ausente / Inconsistente
File: routes/report_routes.py:180,201-202
Description: create_category e update_category aceitam data.get('color', '#000000') e data['color'] sem nenhuma validação de formato, apesar de já existir is_valid_color() em utils/helpers.py:52-55 — que nunca é chamada em nenhum lugar do projeto.
Impact: É possível salvar categorias com cor em formato inválido (ex: 'abc', '', ou HTML/JS malicioso em texto livre), quebrando o front-end que espera um hex válido.
Recommendation: Chamar is_valid_color(data['color']) antes de persistir e retornar 400 se inválido.

[MEDIUM] Error Handling Duplicado
File: routes/task_routes.py:146-154,217-223,231-238; routes/user_routes.py:80-90,127-132,144-151; routes/report_routes.py:182-188,204-209,217-223
Description: O mesmo bloco try/except idêntico (db.session.add/commit, except: db.session.rollback(); return jsonify({'error': ...}), 500) é repetido em pelo menos 9 rotas diferentes, várias vezes com except: genérico (sem capturar a exceção), silenciando qualquer erro inesperado.
Impact: Qualquer mudança na estratégia de tratamento de erro (ex: logging estruturado, Sentry) precisa ser replicada manualmente em 9+ lugares; bare except esconde bugs reais.
Recommendation: Criar middlewares/error_handler.py com @app.errorhandler(Exception) centralizado e um helper de transação reaproveitado pelos controllers.

[LOW] Código Morto
File: services/notification_service.py:1-48
Description: A classe NotificationService (send_email, notify_task_assigned, notify_task_overdue, get_notifications) nunca é importada ou instanciada em nenhum outro arquivo do projeto.
Impact: Código morto aumenta a superfície de manutenção e confunde novos desenvolvedores sobre se notificações estão realmente ativas; também mantém credenciais hardcoded sem nenhum benefício funcional.
Recommendation: Remover o arquivo ou integrá-lo de fato ao fluxo de create_task/update_task se a funcionalidade for necessária.

[LOW] Constantes Duplicadas / Magic Strings
File: models/task.py:39; routes/task_routes.py:110,177; routes/user_routes.py:71,120
Description: A lista ['pending', 'in_progress', 'done', 'cancelled'] (e ['user','admin','manager'] para roles) é reescrita literalmente em pelo menos 4 lugares diferentes, apesar de já existirem VALID_STATUSES e VALID_ROLES definidos em utils/helpers.py:110-111 e nunca importados.
Impact: Adicionar um novo status (ex: 'blocked') exige lembrar de atualizar 4+ arquivos manualmente; risco real de inconsistência entre validações.
Recommendation: Importar VALID_STATUSES/VALID_ROLES de utils/helpers.py (ou mover para config/constants.py) e reutilizar em todos os pontos de validação.

================================
Total: 17 findings
================================
```

## Fase 3 — Status da Refatoração

Todos os 17 findings foram corrigidos na refatoração para MVC (ver estrutura em `config/`, `models/`, `controllers/`, `views/`, `middlewares/`). Detalhes:

- **Secrets**: `SECRET_KEY` e credenciais de e-mail movidos para `config/settings.py`, lidos via `os.environ` com `python-dotenv`. `services/notification_service.py` (código morto) foi removido.
- **Senha em MD5**: substituído por `werkzeug.security.generate_password_hash`/`check_password_hash`.
- **Token de login falso**: substituído por token assinado e com expiração via `itsdangerous.URLSafeTimedSerializer` (chave vinda de `config/settings.py`).
- **God Files** (`report_routes.py`, `task_routes.py`, `user_routes.py`): lógica de negócio extraída para `controllers/task_controller.py`, `controllers/user_controller.py`, `controllers/category_controller.py` e `controllers/report_controller.py`; rotas em `views/*.py` ficaram finas (apenas parsing de request + chamada ao controller).
- **Duplicação de lógica de overdue/validação**: centralizada em `Task.is_overdue()` e nas funções de validação dos controllers, usando constantes de `config/constants.py`.
- **Query N+1**: eliminada com `joinedload` (tasks → user/category) e queries agregadas com `GROUP BY` (contagem de tasks por usuário/categoria).
- **Validação de cor ausente**: `is_valid_color()` (já existente em `utils/helpers.py`) agora é chamada em `create_category`/`update_category`.
- **Error handling duplicado**: centralizado em `middlewares/error_handler.py`, mapeando `ValueError` → 400, `UnauthorizedError` → 401, `ForbiddenError` → 403, `NotFoundError` → 404, `ConflictError` → 409, `Exception` → 500 (preservando os códigos HTTP originais).
- **Constantes duplicadas**: `VALID_STATUSES`/`VALID_ROLES`/etc. centralizadas em `config/constants.py` e reutilizadas por todos os controllers.

Validado: aplicação sobe sem erros, todos os endpoints originais respondem (testado via `curl` após `seed.py`), e os status codes HTTP originais (400/401/403/404/409/500) foram preservados.
