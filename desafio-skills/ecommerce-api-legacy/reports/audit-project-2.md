# Audit Report — ecommerce-api-legacy

> Gerado pela skill `/refactor-arch` — Fase 2 (reauditoria pós-refatoração MVC, commit 4feb166).

```
================================
ARCHITECTURE AUDIT REPORT
================================
Project: ecommerce-api-legacy
Stack:   JavaScript (Node.js) + Express.js 4.22.1
Files:   17 analyzed | ~427 lines of code

Summary
CRITICAL: 2 | HIGH: 0 | MEDIUM: 1 | LOW: 3

Findings

[CRITICAL] Broken Access Control — Exclusão de Usuário sem Autenticação
File: src/routes/user.routes.js:7-14
Description: O handler router.delete('/:id', ...) chama diretamente userController.deleteUser
             sem qualquer middleware de autenticação ou autorização antes dele. Não existe
             nenhum middleware de auth em todo o projeto (nenhum arquivo authMiddleware, jwt,
             requireRole, etc.).
Impact: Qualquer requisição anônima pode apagar qualquer usuário do sistema (e, em cascata,
        suas matrículas e pagamentos), sem necessidade de login ou permissão de admin —
        falha crítica de controle de acesso (OWASP A01:2021 Broken Access Control).
Recommendation: Criar um middleware de autenticação (ex: verificação de JWT) e um middleware
                de autorização por papel (ex: requireRole('admin')), aplicando-os em
                user.routes.js antes do handler DELETE.

[CRITICAL] Broken Access Control — Relatório Financeiro Exposto sem Autenticação
File: src/routes/admin.routes.js:7-14
Description: router.get('/financial-report', ...) expõe receita, lista de alunos e valores
             pagos por curso sem nenhuma verificação de identidade ou papel do requisitante.
Impact: Dados financeiros sensíveis (receita por curso, nomes de alunos, valores pagos)
        ficam publicamente acessíveis a qualquer cliente HTTP que conheça a rota.
Recommendation: Aplicar o mesmo middleware de autenticação/autorização de admin usado em
                user.routes.js também em admin.routes.js, antes do handler de
                /financial-report.

[MEDIUM] Validação Superficial nas Rotas
File: src/controllers/checkout.controller.js:9-12,31
Description: processCheckout valida apenas presença (truthy) de userName, email, courseId e
             cardNumber (linhas 9-12), mas não valida formato: email não é checado contra um
             padrão de e-mail válido, e cardNumber só precisa começar com "4"
             (cardNumber.startsWith(VISA_CARD_PREFIX), linha 31) sem verificar se é uma
             sequência numérica de tamanho válido. Não há biblioteca de schema (joi/zod/
             express-validator) em uso.
Impact: Dados malformados (e-mails inválidos, "cartões" com letras ou tamanho arbitrário)
        podem ser persistidos no banco, degradando a qualidade dos dados e dificultando
        validações futuras de pagamento real.
Recommendation: Adicionar validação de formato (regex de e-mail, checagem de dígitos e
                comprimento do cartão) no controller antes de prosseguir, ou introduzir uma
                biblioteca de schema (zod/joi) na camada de rota.

[LOW] Código Morto — Função verifyPassword Nunca Utilizada
File: src/utils/password.js:10-14
Description: A função verifyPassword(password, storedHash) é exportada mas não é chamada em
             nenhum controller, rota ou model do projeto — não existe endpoint de login.
Impact: Sugere uma funcionalidade de autenticação planejada mas nunca implementada, o que
        confunde novos desenvolvedores sobre o real fluxo de acesso da API.
Recommendation: Remover a função se não houver plano de curto prazo de implementar login, ou
                criar a rota de autenticação que efetivamente a utilize.

[LOW] Código Morto — Configurações Nunca Consumidas
File: src/config/settings.js:4-5
Description: paymentGatewayKey e smtpUser são lidos de process.env (com fallback hardcoded
             'dev-only-insecure-key' e 'no-reply@example.com') mas nenhum controller, model ou
             rota do projeto os importa ou utiliza — o checkout ainda decide o status do
             pagamento apenas com cardNumber.startsWith(VISA_CARD_PREFIX), sem chamar um
             gateway real.
Impact: Configuração morta sugere integração de gateway de pagamento e envio de e-mail que
        não existem de fato; o fallback 'dev-only-insecure-key' hardcoded para um segredo,
        embora hoje inofensivo por estar sem uso, se tornaria um risco assim que a integração
        real fosse implementada copiando esse padrão.
Recommendation: Remover as chaves não utilizadas de settings.js e .env.example, ou implementar
                de fato a integração com o gateway de pagamento; quando essa integração
                existir, eliminar o fallback e falhar a inicialização se a env var estiver
                ausente.

[LOW] Magic Number — Status "active" sem Constante Nomeada
File: src/db/index.js:12,21-22 e src/models/course.model.js:3
Description: O valor literal 1 é usado repetidamente para indicar curso ativo
             (active INTEGER na criação da tabela, VALUES (?, ?, 1) nos seeds, e
             AND active = 1 na query de course.model.js) sem nenhuma constante nomeada
             equivalente a COURSE_ACTIVE presente em config/constants.js.
Impact: Leitores do código precisam inferir pelo contexto que "1" significa "ativo"; um
        futuro estado adicional (ex: "pausado") exigiria grep manual por todos os literais 1.
Recommendation: Adicionar COURSE_ACTIVE = 1 (e, se necessário, COURSE_INACTIVE = 0) em
                config/constants.js e substituir os literais em db/index.js e
                course.model.js.

================================
Total: 6 findings
================================
```
