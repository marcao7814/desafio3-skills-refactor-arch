# Audit Report — ecommerce-api-legacy

> Gerado pela skill `/refactor-arch` — Fase 2.

```
================================
ARCHITECTURE AUDIT REPORT
================================
Project: ecommerce-api-legacy
Stack:   JavaScript (Node.js) + Express.js 4.22.1
Files:   4 analyzed | ~200 lines of code

Summary
CRITICAL: 3 | HIGH: 3 | MEDIUM: 3 | LOW: 3

Findings

[CRITICAL] God Class / God File
File: src/AppManager.js:1-141
Description: A classe AppManager concentra, em um único arquivo, inicialização de banco
             (initDb), definição de rotas HTTP, queries SQL diretas e regras de negócio
             de 3 domínios distintos (checkout/pagamento, relatório financeiro, gestão de
             usuários) dentro do método setupRoutes(). Não há separação entre camadas.
Impact: Qualquer alteração em um domínio (ex: regra de pagamento) arrisca quebrar os
        outros (relatório, exclusão de usuário). Impossível testar em isolamento ou
        reaproveitar lógica de negócio fora do contexto HTTP.
Recommendation: Separar em models/ (courseModel.js, userModel.js, enrollmentModel.js,
                paymentModel.js), services/ (checkoutService.js, financialReportService.js),
                controllers/ (checkoutController.js, adminController.js, userController.js)
                e routes/ apenas com o mapeamento de endpoints.

[CRITICAL] Hardcoded Credentials / Secrets
File: src/utils.js:1-7
Description: Objeto config com segredos literais no código-fonte: dbPass:
             "senha_super_secreta_prod_123", paymentGatewayKey: "pk_live_1234567890abcdef"
             (chave com prefixo de produção) e smtpUser embutidos diretamente no arquivo.
Impact: Segredos expostos no controle de versão (Git). Qualquer pessoa com acesso ao
        repositório pode usar a chave de gateway de pagamento em produção ou a senha do
        banco. Vazamento crítico em caso de repositório público ou comprometido.
Recommendation: Mover todos os valores para variáveis de ambiente (já existe .env.example
                com PORT/DB_PATH/JWT_SECRET) e ler via process.env em config/settings.js,
                nunca commitando o .env real.

[CRITICAL] Criptografia de Senha Insegura (Custom/Broken Crypto)
File: src/utils.js:17-23 (usado em src/AppManager.js:68)
Description: badCrypto(pwd) não é uma função de hash — apenas repete a codificação Base64
             da senha 10000 vezes e trunca o resultado em 10 caracteres
             (hash += Buffer.from(pwd).toString('base64').substring(0, 2)). Base64 é
             reversível, não é hashing. Além disso, na criação de usuário em checkout, a
             senha usa fallback fixo "123456" quando não informada (AppManager.js:68).
Impact: Senhas armazenadas em texto praticamente reversível. Comprometimento do banco expõe
        as senhas reais de todos os usuários. Usuários sem senha informada recebem uma
        senha previsível e compartilhada ("123456"), facilitando account takeover.
Recommendation: Substituir por bcrypt/argon2 (ex: bcrypt.hash(pwd, 12)) e tornar o campo de
                senha obrigatório na criação de conta, rejeitando a requisição com 400 em
                vez de aplicar um valor padrão.

[HIGH] Lógica de Negócio no Controller/Route
File: src/AppManager.js:28-78
Description: O handler app.post('/api/checkout', ...) tem ~50 linhas com queries SQL
             encadeadas, verificação de curso, criação de usuário, hashing de senha,
             decisão de status de pagamento (cc.startsWith("4") ? "PAID" : "DENIED"),
             criação de matrícula, registro de pagamento e log de auditoria — tudo dentro
             do handler de rota, sem camada de serviço.
Impact: Regra de negócio de checkout não pode ser reutilizada (ex: por um job assíncrono)
        nem testada sem subir um servidor HTTP completo. Alto risco de regressão a cada
        mudança na rota.
Recommendation: Extrair para um CheckoutService.processCheckout(dados) que recebe dados já
                validados pelo controller e devolve um resultado; o controller apenas
                chama o service e traduz o resultado em resposta HTTP.

[HIGH] Forte Acoplamento / Sem Injeção de Dependência
File: src/AppManager.js:6-8
Description: this.db = new sqlite3.Database(':memory:') é instanciado diretamente dentro
             do construtor de AppManager, acoplando a classe a uma implementação concreta
             de banco de dados.
Impact: Impossível substituir o banco por um mock em testes unitários ou trocar de SQLite
        para outro banco sem reescrever AppManager inteiro.
Recommendation: Injetar a conexão de banco (ou um repositório) via construtor:
                constructor(db) { this.db = db; }, criando a instância real apenas no
                composition root (app.js).

[HIGH] Estado Global Mutável
File: src/utils.js:9-15 (mutado a partir de src/AppManager.js:59)
Description: let globalCache = {} é uma variável de módulo mutável, alterada pela função
             logAndCache(key, data) chamada a cada checkout bem-sucedido
             (logAndCache(`last_checkout_${userId}`, course.title)). O estado é
             compartilhado entre todas as requisições concorrentes.
Impact: Em ambiente com múltiplas requisições simultâneas (ou múltiplas instâncias do
        processo), o cache pode ser sobrescrito de forma imprevisível entre usuários
        diferentes, causando vazamento de dados entre sessões.
Recommendation: Remover o cache global em memória; usar um cache dedicado (Redis) com
                chave por sessão/usuário ou eliminar a funcionalidade se não for essencial.

[MEDIUM] Query N+1
File: src/AppManager.js:80-129
Description: GET /api/admin/financial-report busca todos os cursos e, para cada curso,
             executa uma query de matrículas (this.db.all(... WHERE course_id = ?)); para
             cada matrícula, executa mais duas queries aninhadas (buscar usuário e buscar
             pagamento). O resultado é N (cursos) x M (matrículas) x 2 queries adicionais.
Impact: Para um catálogo com dezenas de cursos e centenas de matrículas, o endpoint gera
        centenas/milhares de round-trips ao banco, degradando drasticamente a performance.
Recommendation: Substituir por uma única query com JOINs entre courses, enrollments, users
                e payments, agregando os dados em memória a partir de um único resultset.

[MEDIUM] Validação Ausente nas Rotas
File: src/AppManager.js:131-137
Description: DELETE /api/users/:id usa req.params.id diretamente em uma query sem validar
             se é um id numérico válido ou se o usuário existe, e apaga o registro de
             users sem tratar matrículas/pagamentos relacionados — o próprio texto de
             resposta admite: "mas as matrículas e pagamentos ficaram sujos no banco.".
Impact: Registros órfãos em enrollments e payments após a exclusão, corrompendo a
        integridade referencial e quebrando o relatório financeiro (usuário 'Unknown').
Recommendation: Validar o id recebido, verificar existência do usuário e, dentro de uma
                transação, excluir ou anonimizar os registros dependentes (ou aplicar
                soft delete) antes de remover o usuário.

[MEDIUM] Error Handling Ausente
File: src/AppManager.js:92-127
Description: Nas queries aninhadas de GET /api/admin/financial-report
             (this.db.all(...) e this.db.get(...) dentro dos forEach), o parâmetro err de
             callback nunca é verificado — qualquer falha do SQLite é silenciosamente
             ignorada e o processamento continua como se tivesse funcionado.
Impact: Erros de banco passam despercebidos, produzindo relatórios financeiros incompletos
        ou incorretos sem qualquer log ou resposta de erro ao cliente.
Recommendation: Tratar err em cada callback, interrompendo o processamento e retornando
                500 com log do erro; centralizar esse tratamento em um helper reutilizável.

[LOW] Magic Numbers
File: src/utils.js:19,22 e src/AppManager.js:46
Description: for(let i = 0; i < 10000; i++) e hash.substring(0, 10) em badCrypto, e
             cc.startsWith("4") em AppManager.js para decidir aprovação do pagamento, sem
             nenhuma constante nomeada explicando os valores.
Impact: Leitores do código não conseguem inferir o significado de "10000", "10" ou "4" sem
        ler a lógica inteira; mudanças acidentais nesses valores passam despercebidas.
Recommendation: Extrair para constantes nomeadas (ex: const CARD_BRAND_VISA_PREFIX = '4',
                const HASH_ROUNDS = 10000) ou eliminar ao trocar por bcrypt.

[LOW] Nomenclatura Ruim
File: src/AppManager.js:29-33
Description: Variáveis extraídas do corpo da requisição usam abreviações obscuras:
             let u = req.body.usr; let e = req.body.eml; let p = req.body.pwd;
             let cid = req.body.c_id; let cc = req.body.card; — tanto os nomes internos
             quanto os próprios campos do contrato da API (usr, eml, pwd, c_id) não
             comunicam intenção.
Impact: Aumenta o tempo de leitura e a chance de erro ao dar manutenção; dificulta o
        entendimento do contrato da API por consumidores externos.
Recommendation: Renomear para nomes descritivos (userName, email, password, courseId,
                cardNumber) e padronizar o contrato do payload da API na mesma convenção.

[LOW] Código Morto
File: src/server.js:1-17 e src/utils.js:2,3,5,10
Description: src/server.js duplica exatamente a inicialização de src/app.js, mas não é
             referenciado em nenhum lugar do package.json (main e scripts.start apontam
             para src/app.js) — nunca é executado. Em utils.js, dbUser, dbPass, smtpUser e
             totalRevenue são declarados e exportados mas nunca lidos em nenhum outro
             arquivo do projeto.
Impact: Arquivos e variáveis mortos confundem novos desenvolvedores sobre qual é o
        entry point real e sugerem funcionalidades (revenue tracking, SMTP, usuário de
        banco dedicado) que não existem de fato.
Recommendation: Remover src/server.js e as variáveis não utilizadas de utils.js, ou, caso
                sejam funcionalidades planejadas, documentar isso explicitamente.

================================
Total: 12 findings
================================
```
