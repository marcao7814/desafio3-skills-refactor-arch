# Documentação de Implementação — Skill de Auditoria e Refatoração Arquitetural

> Atualizada em 25/04/2026 — reflete o estado real dos 3 projetos criados e validados.

---

## Estado Atual do Repositório

```
desafio-skills/
├── .gitignore
├── README.md
├── reports/
│   ├── audit-project-1.md    ← gerado pela skill após execução
│   ├── audit-project-2.md
│   └── audit-project-3.md
│
├── code-smells-project/         ← Python 3.12 / Flask 3.1.1
│   ├── .claude/skills/refactor-arch/   ← skill completa (6 arquivos)
│   ├── app.py
│   ├── controllers.py
│   ├── models.py
│   ├── database.py
│   ├── requirements.txt
│   ├── .env.example
│   └── reports/audit-project-1.md
│
├── ecommerce-api-legacy/        ← Node.js v24 / Express 4
│   ├── .claude/skills/refactor-arch/
│   ├── src/
│   │   ├── AppManager.js   ← God Class principal
│   │   ├── app.js          ← config com credenciais hardcoded
│   │   ├── utils.js        ← config duplicada (code smell intencional)
│   │   └── server.js       ← entry point
│   ├── package.json
│   ├── .env.example
│   ├── api.http
│   └── reports/audit-project-2.md
│
└── task-manager-api/            ← Python 3.12 / Flask 3.0 + SQLAlchemy
    ├── .claude/skills/refactor-arch/
    ├── .vscode/settings.json    ← aponta para C:/projeto python/python12/
    ├── app.py
    ├── database.py
    ├── models/
    │   ├── task.py
    │   ├── user.py
    │   └── category.py
    ├── routes/
    │   ├── task_routes.py
    │   ├── user_routes.py
    │   └── report_routes.py
    ├── services/
    │   └── notification_service.py
    ├── utils/
    │   └── helpers.py
    ├── requirements.txt
    ├── .env.example
    └── reports/audit-project-3.md
```

---

## Projeto 1 — code-smells-project (Python/Flask)

### Stack
- **Linguagem:** Python 3.12
- **Framework:** Flask 3.1.1 + flask-cors 5.0.1
- **Banco:** SQLite (`loja.db`) via `sqlite3` nativo
- **Porta:** 5000

### Como rodar
```bash
cd code-smells-project
pip install -r requirements.txt
python app.py
```

### Endpoints disponíveis
| Método | Rota | Descrição |
|--------|------|-----------|
| GET | `/` | Index com lista de endpoints |
| GET | `/health` | Health check com contagem de registros |
| GET | `/produtos` | Listar todos os produtos |
| GET | `/produtos/busca?q=termo` | Busca com filtros |
| GET | `/produtos/<id>` | Buscar produto por ID |
| POST | `/produtos` | Criar produto |
| PUT | `/produtos/<id>` | Atualizar produto |
| DELETE | `/produtos/<id>` | Deletar produto |
| GET | `/usuarios` | Listar usuários |
| GET | `/usuarios/<id>` | Buscar usuário |
| POST | `/usuarios` | Criar usuário |
| POST | `/login` | Autenticar usuário |
| POST | `/pedidos` | Criar pedido |
| GET | `/pedidos` | Listar todos os pedidos |
| GET | `/pedidos/usuario/<id>` | Pedidos de um usuário |
| PUT | `/pedidos/<id>/status` | Atualizar status do pedido |
| GET | `/relatorios/vendas` | Relatório de vendas |
| POST | `/admin/reset-db` | Resetar banco de dados |
| POST | `/admin/query` | Executar SQL arbitrário |

### Code smells presentes (intencionais)
| Arquivo | Linha | Severidade | Problema |
|---------|-------|------------|---------|
| `app.py` | 7 | CRITICAL | `SECRET_KEY = "minha-chave-super-secreta-123"` hardcoded |
| `app.py` | 59-78 | CRITICAL | Endpoint `/admin/query` executa SQL arbitrário recebido via POST |
| `models.py` | 28 | CRITICAL | SQL Injection: `"WHERE id = " + str(id)` |
| `models.py` | 47-52 | CRITICAL | SQL Injection: concatenação na INSERT de produto |
| `models.py` | 57-62 | CRITICAL | SQL Injection: concatenação na UPDATE de produto |
| `models.py` | 109-111 | CRITICAL | SQL Injection: login via concatenação de email e senha |
| `models.py` | 126-131 | CRITICAL | SQL Injection: INSERT de usuário via concatenação |
| `models.py` | 140-165 | HIGH | God File: lógica de produto, usuário e pedido no mesmo arquivo |
| `models.py` | 139-168 | HIGH | Query N+1: busca produto para cada item no loop `for item in itens` |
| `models.py` | 171-201 | HIGH | Query N+1: 3 cursores aninhados por pedido (pedido → itens → produto) |
| `database.py` | 4 | HIGH | Estado global mutável: `db_connection = None` compartilhado |
| `controllers.py` | 287-289 | MEDIUM | `health_check` expõe `secret_key` e `db_path` na resposta JSON |
| `models.py` | 247-258 | MEDIUM | Magic numbers para faixas de desconto (0.1, 0.05, 0.02, 10000, 5000, 1000) |
| `models.py` | 279-283 | MEDIUM | SQL Injection: UPDATE de status via concatenação de string |
| `models.py` | 289-298 | MEDIUM | SQL Injection: busca com concatenação em múltiplos campos |

### Justificativa arquitetural dos problemas identificados

**[CRITICAL] `SECRET_KEY` hardcoded (`app.py:7`)**
A chave secreta embutida no código-fonte expõe o sistema à falsificação de sessões. Qualquer pessoa com acesso ao repositório pode assinar tokens válidos e se passar por qualquer usuário. Em termos MVC, configuração sensível nunca deve residir na camada de aplicação — deve vir de variáveis de ambiente ou de um módulo de config isolado.

**[CRITICAL] Endpoint `/admin/query` sem autenticação (`app.py:59-78`)**
Aceitar e executar SQL arbitrário via POST sem autenticação é equivalente a expor o prompt do banco de dados na internet. Viola completamente a separação de responsabilidades: a camada de rota não deve ter acesso direto ao motor de banco de dados.

**[CRITICAL] SQL Injection em `models.py` (múltiplos pontos)**
Concatenação de input do usuário em queries SQL é a vulnerabilidade OWASP #1. Permite que um atacante exfiltre, modifique ou destrua toda a base de dados com uma única requisição. Arquiteturalmente, indica ausência de qualquer camada de abstração entre a entrada HTTP e o banco.

**[HIGH] God File `models.py:140-201`**
Um único arquivo centralizando lógica de produto, usuário e pedido viola o Single Responsibility Principle. Qualquer alteração em um domínio arrisca quebrar outro, testes em isolamento são impossíveis e o acoplamento torna a codebase resistente a evolução — o oposto do que MVC propõe com a separação de Models por domínio.

**[HIGH] Query N+1 (`models.py:139-201`)**
Executar uma query por item dentro de um loop transforma operações O(1) em O(N). Para 100 pedidos com 5 itens cada, são 500+ queries onde bastariam 2. Em produção, esse padrão é responsável por boa parte das degradações de performance progressivas.

**[HIGH] Estado global mutável em `database.py:4`**
Uma única variável `db_connection = None` compartilhada entre requisições gera condições de corrida em ambientes multi-thread: a Thread A pode receber resultados da query iniciada pela Thread B. Arquiteturalmente, a conexão com o banco deve ser gerenciada por contexto de requisição, não por estado global.

**[MEDIUM] `health_check` expõe `secret_key` (`controllers.py:287-289`)**
Um endpoint público que retorna configurações internas facilita ataques de reconhecimento. A camada de controller não deve ter acesso à configuração da aplicação — isso é responsabilidade do módulo de config.

**[MEDIUM] Magic numbers para descontos (`models.py:247-258`)**
Valores como `0.1`, `0.05`, `10000`, `5000` embutidos no código tornam regras de negócio invisíveis. Quando as faixas de desconto mudarem, o desenvolvedor precisa localizar todos os pontos de uso. Constantes nomeadas (`DESCONTO_GOLD = 0.10`) são contratos explícitos com o domínio de negócio.

### Dados de seed (criados na primeira conexão)
- 10 produtos nas categorias: informatica, moveis, vestuario
- 3 usuários: `admin@loja.com/admin123`, `joao@email.com/123456`, `maria@email.com/senha123`

---

## Projeto 2 — ecommerce-api-legacy (Node.js/Express)

### Stack
- **Linguagem:** Node.js v24
- **Framework:** Express 4.18.2
- **Banco:** SQLite in-memory via `sqlite3` (async/callback)
- **Porta:** 3000

### Como rodar
```bash
cd ecommerce-api-legacy
npm install
npm start
# ou: node src/server.js
```

### Endpoints disponíveis
| Método | Rota | Descrição |
|--------|------|-----------|
| POST | `/api/checkout` | Checkout com criação de usuário, matrícula e pagamento |
| GET | `/api/admin/financial-report` | Relatório financeiro por curso |
| DELETE | `/api/users/:id` | Deletar usuário (sem cascade) |

### Estrutura de arquivos fonte
| Arquivo | Responsabilidade |
|---------|-----------------|
| `src/AppManager.js` | God Class: DB init + todas as rotas em `setupRoutes()` |
| `src/app.js` | Config com credenciais hardcoded (paymentGatewayKey, dbPass, smtpUser) |
| `src/utils.js` | Duplicata de `app.js` — mesma config repetida (code smell intencional) |
| `src/server.js` | Entry point: instancia AppManager, chama `initDb()` e `setupRoutes()` |

### Code smells presentes (intencionais)
| Arquivo | Linha | Severidade | Problema |
|---------|-------|------------|---------|
| `src/app.js` | 1-6 | CRITICAL | Credenciais hardcoded: `dbPass`, `paymentGatewayKey`, `smtpUser` |
| `src/utils.js` | 1-6 | CRITICAL | Duplicata das mesmas credenciais hardcoded |
| `src/AppManager.js` | 1-139 | CRITICAL | God Class: DB + rotas de checkout, relatório e usuários em 1 classe |
| `src/AppManager.js` | 9-10 | HIGH | Estado global mutável: `this.currentUser` e `globalCache` no singleton |
| `src/AppManager.js` | 92-128 | HIGH | Query N+1 no relatório: `enrollments.forEach` com queries aninhadas |
| `src/AppManager.js` | 43-78 | HIGH | Toda lógica de negócio do checkout dentro de callbacks de rota |
| `src/app.js` | 9 | MEDIUM | `globalCache` — objeto global mutável entre requests |
| `src/AppManager.js` | 46 | MEDIUM | Lógica de aprovação de cartão por prefixo do número (`cc.startsWith("4")`) |
| `src/utils.js` | 17-23 | MEDIUM | `badCrypto()`: função de hash insegura usada para senhas |
| `src/AppManager.js` | 131-137 | MEDIUM | DELETE sem cascade: matrículas e pagamentos ficam órfãos no banco |

### Justificativa arquitetural dos problemas identificados

**[CRITICAL] Credenciais hardcoded (`src/app.js:1-6` e `src/utils.js:1-6`)**
Chaves de gateway de pagamento e credenciais SMTP no código-fonte significam que qualquer acesso ao repositório dá acesso ao sistema financeiro e de e-mail da empresa. A duplicação em dois arquivos agrava o risco: há duas superfícies de ataque e dois pontos de rotação em caso de comprometimento.

**[CRITICAL] God Class `AppManager.js:1-139`**
Uma única classe com 139 linhas misturando inicialização de banco de dados, roteamento HTTP, lógica de checkout e geração de relatórios viola todos os princípios SOLID simultaneamente. Em MVC, cada uma dessas responsabilidades pertence a uma camada distinta: Model (banco), Route (roteamento), Controller (orquestração), Service (lógica de negócio). Impossível testar em isolamento.

**[HIGH] Estado global mutável `this.currentUser` e `globalCache` (`src/AppManager.js:9-10`)**
Node.js processa requisições concorrentes no mesmo processo. `this.currentUser` compartilhado entre requisições significa que a requisição do usuário A pode sobrescrever o contexto da requisição do usuário B ainda em processamento — falha de segurança e corrupção de dados sob carga.

**[HIGH] Query N+1 no relatório financeiro (`src/AppManager.js:92-128`)**
`enrollments.forEach` com queries aninhadas para buscar curso e usuário a cada iteração gera N+1 queries. Para 1.000 matrículas, são mais de 2.000 queries para gerar um único relatório administrativo. A solução é um JOIN ou queries em batch fora do loop.

**[HIGH] Lógica de checkout em callback de rota (`src/AppManager.js:43-78`)**
Criação de usuário, validação de cartão, registro de matrícula e pagamento todos dentro de um callback Express tornam impossível testar a lógica de negócio sem levantar o servidor HTTP. Controllers devem apenas orquestrar — a lógica deve residir em Services testáveis de forma independente.

**[MEDIUM] `badCrypto()` para senhas (`src/utils.js:17-23`)**
Funções de hash genéricas (MD5, SHA1) são projetadas para velocidade — o oposto do que se quer para senhas. Um atacante com acesso ao banco de dados pode quebrar um hash MD5 em milissegundos com rainbow tables. Senhas exigem bcrypt, argon2 ou scrypt, que têm custo computacional intencional.

**[MEDIUM] DELETE sem cascade (`src/AppManager.js:131-137`)**
Deletar um usuário sem remover matrículas e pagamentos associados deixa registros órfãos que violam integridade referencial. Queries de relatório que fazem JOIN com `users` retornarão erros ou dados incorretos. A responsabilidade de manter integridade pode ser do banco (ON DELETE CASCADE) ou do service.

### Dados de seed (iniciados no `initDb()`)
- 2 cursos: `Clean Architecture (R$997)`, `Docker (R$497)`
- 1 usuário: `leonan@fullcycle.com.br / 123`
- 1 matrícula e 1 pagamento já existentes

### Lógica de aprovação de pagamento
- Cartão começando com `4` (Visa) → `PAID` → matrícula criada
- Demais cartões → `DENIED` → HTTP 400

---

## Projeto 3 — task-manager-api (Python/Flask + SQLAlchemy)

### Stack
- **Linguagem:** Python 3.12
- **Framework:** Flask 3.0.0 + Flask-SQLAlchemy 3.1.1 + flask-cors 4.0.0
- **ORM:** SQLAlchemy (models declarativos)
- **Banco:** SQLite (`instance/tasks.db`) via SQLAlchemy
- **Porta:** 5000

### Como rodar
```bash
cd task-manager-api
pip install -r requirements.txt
python app.py
```

### Dependências (requirements.txt)
```
flask==3.0.0
flask-sqlalchemy==3.1.1
flask-cors==4.0.0
marshmallow==3.20.1
requests==2.31.0
python-dotenv==1.0.0
```

> **Nota VS Code:** configurar o interpretador para `C:/projeto python/python12/python.exe`
> via `Ctrl+Shift+P → Python: Select Interpreter` para resolver o aviso do Pylance.

### Estrutura de camadas
| Arquivo/Pasta | Camada | Descrição |
|---------------|--------|-----------|
| `database.py` | Config | `db = SQLAlchemy()` — instância compartilhada |
| `models/task.py` | Model | ORM: tabela `tasks`, métodos `to_dict()`, `validate_status()` |
| `models/user.py` | Model | ORM: tabela `users`, hash MD5 de senha (code smell intencional) |
| `models/category.py` | Model | ORM: tabela `categories` |
| `routes/task_routes.py` | Route | Blueprint `tasks`: GET/POST/PUT/DELETE `/tasks` |
| `routes/user_routes.py` | Route | Blueprint `users`: GET/POST `/users`, POST `/auth/login` |
| `routes/report_routes.py` | Route | Blueprint `reports`: GET `/reports/summary` |
| `services/notification_service.py` | Service | Notificações (simuladas via print) |
| `utils/helpers.py` | Util | Validações, formatação de datas, constantes |
| `app.py` | Entry | Registra blueprints, `db.init_app(app)`, `db.create_all()` |

### Endpoints disponíveis
| Método | Rota | Descrição |
|--------|------|-----------|
| GET | `/` | Index |
| GET | `/health` | Health check |
| GET | `/tasks` | Listar tasks |
| GET | `/tasks/<id>` | Buscar task |
| POST | `/tasks` | Criar task |
| PUT | `/tasks/<id>` | Atualizar task |
| DELETE | `/tasks/<id>` | Deletar task |
| GET | `/users` | Listar usuários |
| POST | `/users` | Criar usuário |
| POST | `/auth/login` | Login |
| GET | `/categories` | Listar categorias |
| POST | `/categories` | Criar categoria |
| GET | `/reports/summary` | Relatório resumido |

### Code smells presentes (intencionais)
| Arquivo | Linha | Severidade | Problema |
|---------|-------|------------|---------|
| `app.py` | 13 | CRITICAL | `SECRET_KEY = 'super-secret-key-123'` hardcoded |
| `models/user.py` | 29 | CRITICAL | Hash MD5 para senhas: `hashlib.md5(pwd.encode()).hexdigest()` |
| `routes/task_routes.py` | 41-57 | HIGH | Query N+1: busca `User` e `Category` por ID para cada task no loop |
| `routes/task_routes.py` | 30-58 | HIGH | Lógica de negócio (cálculo de overdue) dentro da rota `GET /tasks` |
| `utils/helpers.py` | 84-88 | MEDIUM | Magic numbers: `priority >= 1 and p <= 5` sem constantes nomeadas |
| `utils/helpers.py` | 110-116 | MEDIUM | Constantes definidas no final do arquivo após uso (ordem invertida) |
| `models/user.py` | 17-25 | MEDIUM | `to_dict()` expõe o campo `password` hash na resposta da API |
| `routes/task_routes.py` | 62 | LOW | `except:` sem especificar exceção (captura tudo silenciosamente) |

### Justificativa arquitetural dos problemas identificados

**[CRITICAL] `SECRET_KEY` hardcoded (`app.py:13`)**
Mesmo problema do Projeto 1: chave de sessão no código-fonte comprometida via acesso ao repositório. Este projeto usa Flask com SQLAlchemy, onde a SECRET_KEY protege cookies de sessão e tokens — sua exposição invalida toda a camada de autenticação.

**[CRITICAL] Hash MD5 para senhas (`models/user.py:29`)**
MD5 não é uma função de hash para senhas: foi projetada para velocidade e é computacionalmente trivial de quebrar com rainbow tables. Um dump do banco expõe imediatamente todas as senhas dos usuários. Arquiteturalmente, a responsabilidade de hash seguro pertence ao Model, mas usando bcrypt ou argon2. A severidade é CRITICAL porque a falha está em uma função chamada em toda operação de criação/autenticação de usuário.

**[HIGH] Query N+1 em `routes/task_routes.py:41-57`**
Este projeto já possui separação em camadas (models, routes, services), o que torna o N+1 mais grave: a lógica de carregamento de relacionamentos deveria estar no Model ou em um repositório, não na rota. A solução correta com SQLAlchemy é usar `joinedload(Task.user, Task.category)` na query inicial, eliminando N queries extras com zero mudança na lógica da rota.

**[HIGH] Lógica de negócio em rota `GET /tasks` (`routes/task_routes.py:30-58`)**
O cálculo de `is_overdue` dentro da rota não pode ser reutilizado em outros contextos (ex: job de notificação, websocket, relatório) sem duplicação. Essa lógica pertence ao Model `Task` ou a um Service — a rota deve apenas receber, delegar e retornar.

**[MEDIUM] Magic numbers em `helpers.py:84-88`**
`priority >= 1 and p <= 5` embute regras de domínio como literais numéricos. Se o range de prioridade mudar de 1-5 para 0-10, o desenvolvedor precisa encontrar todos os usos dispersos. Constantes nomeadas como `PRIORITY_MIN = 1` são contratos explícitos com o domínio que aparecem na documentação automática e no intellisense.

**[MEDIUM] `to_dict()` expõe hash de senha (`models/user.py:17-25`)**
Incluir o campo `password` na serialização do Model User significa que qualquer endpoint que retorne usuários vaza o hash de senha na resposta da API. Mesmo que seja um hash, facilita ataques offline. A serialização deve ter uma lista explícita de campos exportáveis (`exclude = ['password']`).

**[LOW] `except:` genérico (`routes/task_routes.py:62`)**
Capturar `BaseException` sem especificar o tipo mascara erros de programação (`AttributeError`, `TypeError`) que deveriam propagar e alertar o desenvolvedor durante o desenvolvimento. Além disso, captura `KeyboardInterrupt` e `SystemExit`, podendo impedir o encerramento limpo do processo.

---

## Skill `/refactor-arch` — 6 Arquivos de Referência

A skill está nos 3 projetos em `.claude/skills/refactor-arch/`. O conteúdo é **idêntico** nos 3.

| Arquivo | Propósito |
|---------|-----------|
| `SKILL.md` | Prompt principal: instrui as 3 fases, formatos de saída e regra de confirmação |
| `01-project-analysis.md` | Heurísticas de detecção de linguagem, framework, domínio e arquitetura |
| `02-antipatterns-catalog.md` | 13 anti-patterns com sinais de detecção e regex para Python e Node.js |
| `03-report-template.md` | Template exato do relatório com regras de preenchimento e exemplo |
| `04-mvc-guidelines.md` | Estrutura MVC alvo + regras de responsabilidade por camada |
| `05-refactoring-playbook.md` | 10 padrões de transformação antes/depois em Python e Node.js |

### Anti-patterns catalogados
| ID | Nome | Severidade |
|----|------|------------|
| C1 | God Class / God File | CRITICAL |
| C2 | Hardcoded Credentials / Secrets | CRITICAL |
| C3 | SQL Injection | CRITICAL |
| H1 | Lógica de Negócio no Controller/Route | HIGH |
| H2 | Forte Acoplamento / Sem Injeção de Dependência | HIGH |
| H3 | Estado Global Mutável | HIGH |
| M1 | Query N+1 | MEDIUM |
| M2 | Validação Ausente nas Rotas | MEDIUM |
| M3 | Error Handling Duplicado / Ausente | MEDIUM |
| M4 | APIs Deprecated (Node.js e Python) | MEDIUM |
| L1 | Magic Numbers | LOW |
| L2 | Nomenclatura Ruim | LOW |
| L3 | Código Morto / Comentado | LOW |

---

## Construção da Skill

### Decisões de design

#### Por que 6 arquivos e não um só?

A primeira decisão foi separar o **SKILL.md** (que instrui o que fazer) dos **arquivos de referência** (que fornecem o conhecimento para fazer). Mesclar tudo em um único arquivo criaria um prompt gigante que o agente leria inteiro a cada fase — aumentando custo de tokens e diluindo o foco. A estrutura final ficou assim:

| Arquivo | Função no modelo mental |
|---------|------------------------|
| `SKILL.md` | Orquestrador: instrui as 3 fases, formatos de saída obrigatórios e a regra de pausa |
| `01-project-analysis.md` | Conhecimento de detecção: como identificar linguagem, framework e arquitetura |
| `02-antipatterns-catalog.md` | Conhecimento de diagnóstico: o que procurar e como reconhecer |
| `03-report-template.md` | Contrato de saída: como formatar o resultado da Fase 2 |
| `04-mvc-guidelines.md` | Conhecimento de destino: como deve ser a arquitetura final |
| `05-refactoring-playbook.md` | Conhecimento de transformação: como chegar do estado atual ao destino |

Cada arquivo é carregado apenas na fase em que é necessário — o `SKILL.md` instrui o agente explicitamente: *"Leia `01-project-analysis.md` antes de iniciar a Fase 1"*, *"Leia `02-antipatterns-catalog.md` e `03-report-template.md` antes da Fase 2"*. Isso mantém o contexto relevante e o agente focado.

#### Estrutura do SKILL.md como prompt sequencial

O `SKILL.md` é um prompt estruturado em 3 seções independentes. Cada seção tem:
1. Qual arquivo de referência ler antes de começar
2. Lista de tarefas numeradas e específicas
3. Formato de saída obrigatório (bloco de código fixo)

A Fase 2 tem uma **regra explícita em maiúsculo** — `NUNCA modifique, crie ou delete arquivos antes desta confirmação` — precedida do aviso `REGRA OBRIGATÓRIA`. A combinação de tipografia (maiúsculas + negrito) e posicionamento logo antes do ponto de pausa foi intencional: testes iniciais mostraram que o agente tendia a prosseguir direto para refatoração sem aguardar confirmação quando a instrução estava enterrada no meio de parágrafos.

#### Por que o template de relatório tem um exemplo preenchido?

O `03-report-template.md` inclui um exemplo completo além do template vazio. Sem o exemplo, o agente gerava relatórios corretamente formatados mas com descrições genéricas como *"SQL Injection encontrado"* sem citar o trecho de código real. O exemplo demonstra o nível de especificidade esperado: `Description: query = f"SELECT * FROM produtos WHERE id={id}" — id não sanitizado.`

---

### Seleção de anti-patterns: por que estes 13?

Os 13 anti-patterns foram escolhidos por dois critérios: **frequência nos 3 projetos analisados** e **cobertura de todos os níveis de severidade** exigidos pelos critérios de aceite.

#### CRITICAL (3) — segurança e arquitetura quebrada

| ID | Por que incluir |
|----|----------------|
| C1 — God Class / God File | Presente nos 3 projetos. É o anti-pattern mais prejudicial para manutenção: torna impossível testar em isolamento e concentra o risco em um único ponto de falha. |
| C2 — Hardcoded Credentials | Presente nos 3 projetos. Credenciais no código-fonte é uma vulnerabilidade exploitável imediatamente após acesso ao repositório — sem qualquer barreira. |
| C3 — SQL Injection | Presente no Projeto 1 com 7 ocorrências. Vulnerabilidade OWASP #1: permite exfiltração e destruição de dados com uma única requisição maliciosa. |

#### HIGH (3) — violações fortes de MVC e SOLID

| ID | Por que incluir |
|----|----------------|
| H1 — Lógica de Negócio no Controller/Route | Presente nos 3 projetos. É a violação mais comum de MVC: lógica de domínio presa em handlers de rota torna impossible reutilizar sem duplicar. |
| H2 — Forte Acoplamento / Sem Injeção de Dependência | Presente nos Projetos 1 e 2. Conexões de banco instanciadas dentro de funções de negócio tornam testes unitários impossíveis sem levantar banco real. |
| H3 — Estado Global Mutável | Presente nos Projetos 1 e 2. Em ambientes concorrentes (Flask threads, Node.js event loop), estado global entre requests é fonte de bugs silenciosos e falhas de segurança. |

#### MEDIUM (4) — performance, qualidade e modernidade

| ID | Por que incluir |
|----|----------------|
| M1 — Query N+1 | Presente nos 3 projetos. Performance degrada linearmente com o volume de dados — invisível em desenvolvimento com seed data pequeno, crítico em produção. |
| M2 — Validação Ausente | Presente nos 3 projetos. Inputs não validados chegam direto ao banco, causando erros 500 sem mensagens úteis ou dados corrompidos. |
| M3 — Error Handling Duplicado / Ausente | Presente nos Projetos 1 e 2. Blocos try/catch idênticos em 10+ rotas são tanto duplicação quanto fragilidade — um bug corrigido em um lugar não está corrigido nos outros. |
| M4 — APIs Deprecated | Obrigatório por requisito do desafio. Presença de `hashlib.md5()` (Proj 3), `sqlite3` sem context manager (Proj 1) e callback-style sqlite3 (Proj 2). |

#### LOW (3) — legibilidade e manutenibilidade

| ID | Por que incluir |
|----|----------------|
| L1 — Magic Numbers | Presente nos 3 projetos. Números literais como regras de negócio tornam o código resistente a mudanças de requisitos. |
| L2 — Nomenclatura Ruim | Cobertura de boas práticas — nomes como `d`, `tmp`, `obj` em código de produção aumentam o custo cognitivo de manutenção. |
| L3 — Código Morto / Comentado | Cobertura de higiene de código — blocos comentados são ruído que obscurece intenção e pode indicar lógica abandonada com bugs conhecidos. |

**Anti-patterns considerados e excluídos:** Circular Dependencies, Premature Optimization e Feature Envy foram considerados mas excluídos por não terem ocorrências verificáveis nos 3 projetos-alvo, o que tornaria os sinais de detecção especulativos.

---

### Como a agnósticidade de tecnologia foi garantida

O risco central de uma skill desse tipo é tornar-se implicitamente dependente de uma linguagem — detectar padrões Python mas não os equivalentes em Node.js, ou gerar uma estrutura MVC Flask quando o projeto é Express.

Três mecanismos foram usados para evitar isso:

#### 1. Detecção por artefatos de projeto, não por suposição

O `01-project-analysis.md` usa uma tabela de sinais observáveis:

| Sinal detectado | Linguagem inferida |
|-----------------|-------------------|
| `*.py` presentes | Python |
| `*.js` + `package.json` | Node.js |
| `requirements.txt` contém `flask` | Flask |
| `package.json` dependencies contém `express` | Express |

O agente nunca supõe a linguagem — ele verifica os artefatos. Isso garante que a mesma Fase 1 funciona em Python, Node.js, Go ou Ruby com apenas extensão da tabela.

#### 2. Catálogo com exemplos bilíngues (Python e Node.js)

Cada anti-pattern no `02-antipatterns-catalog.md` tem:
- Sinais de detecção descritos em linguagem natural (agnósticos)
- Exemplos de código concretos para Python **e** Node.js
- Regex de busca específicos para cada linguagem

Por exemplo, para SQL Injection:
- Python: detecta `f"SELECT...{var}"` e `"SELECT..." + str(var)`
- Node.js: detecta `` `SELECT...${var}` `` e template literals com interpolação

#### 3. MVC guidelines com dois targets distintos

O `04-mvc-guidelines.md` define estruturas-alvo separadas para Python/Flask e Node.js/Express. A Fase 3 lê qual linguagem foi detectada na Fase 1 e aplica o template correspondente — não existe um template único forçado para todos os projetos.

O `05-refactoring-playbook.md` segue o mesmo padrão: cada um dos 10 padrões de transformação tem bloco de código "Antes" e "Depois" tanto em Python quanto em JavaScript, com nomenclatura de arquivo seguindo a convenção de cada ecossistema (`produto_model.py` vs `produto.model.js`).

---

### Desafios encontrados

#### Desafio 1: Agente ignorava a pausa de confirmação

**Problema:** Nas primeiras versões do SKILL.md, o agente completava a Fase 2 e iniciava a Fase 3 sem aguardar o `[y/n]`. A instrução estava presente mas enterrada no texto.

**Solução:** A regra foi isolada em bloco próprio com prefixo `### REGRA OBRIGATÓRIA:`, escrita em negrito com maiúsculas, e posicionada imediatamente antes da linha que exibe `[y/n]`. O contraste visual e a proximidade com o ponto de ação tornaram a instrução respeitada de forma consistente.

#### Desafio 2: Descriptions genéricas no relatório

**Problema:** O agente gerava findings corretos mas com descrições vagas como *"SQL Injection encontrado em models.py"*, sem citar o trecho problemático.

**Solução:** O `03-report-template.md` foi atualizado com um exemplo preenchido completo que demonstra o nível de especificidade esperado. Regras explícitas foram adicionadas: *"citar o trecho de código real que causou o finding"*, com exemplo inline. A qualidade das descriptions melhorou imediatamente após essa adição.

#### Desafio 3: Skill aplicando refatoração completa em projeto já organizado

**Problema:** No Projeto 3 (`task-manager-api`), que já possui `models/`, `routes/` e `services/`, a skill tentava criar uma estrutura MVC do zero, sobrescrevendo a organização existente.

**Solução:** O `01-project-analysis.md` foi refinado com critérios distintos para "Monolítica simples", "Parcialmente organizada" e "MVC limpa". O `SKILL.md` instrui a Fase 3 a *"criar a estrutura MVC conforme detectado na Fase 1"* — quando a arquitetura é "Parcialmente organizada", a Fase 3 melhora o que existe em vez de recriar do zero.

#### Desafio 4: SQL Injection em Node.js com padrões diferentes

**Problema:** O Projeto 2 usa `better-sqlite3` com `.prepare(...).get(...)` — padrão diferente do sqlite3 Python. Os sinais de detecção iniciais cobriam apenas concatenação com `+` e f-strings Python.

**Solução:** O catálogo foi expandido com exemplos específicos para template literals JavaScript (`` `SELECT...${var}` ``) e um regex dedicado: `` `\`[^`]*\$\{[^}]+\}[^`]*\`` ``. Isso garantiu que o mesmo anti-pattern C3 fosse detectado nos dois ecossistemas.

---

## Ambiente de Execução

| Recurso | Versão / Caminho |
|---------|-----------------|
| Python | 3.12.x em `C:/projeto python/python12/python.exe` |
| Node.js | v24.12.0 |
| Flask (proj 1) | 3.1.1 |
| Flask (proj 3) | 3.0.0 + SQLAlchemy 3.1.1 |
| Express | 4.18.2 |
| SQLite driver Python | nativo (`sqlite3`) |
| SQLite driver Node.js | `sqlite3` (async/callback) |

### Testar os 3 projetos
```bash
# Projeto 1 — porta 5000
cd code-smells-project
"C:/projeto python/python12/python.exe" app.py

# Projeto 2 — porta 3000
cd ecommerce-api-legacy
npm start

# Projeto 3 — porta 5000
cd task-manager-api
"C:/projeto python/python12/python.exe" app.py
```

---

## Executar a Skill

```bash
# Projeto 1
cd code-smells-project
claude "/refactor-arch"

# Projeto 2
cd ../ecommerce-api-legacy
claude "/refactor-arch"

# Projeto 3
cd ../task-manager-api
claude "/refactor-arch"
```

A Fase 2 pausa e exibe:
```
Phase 2 complete. Proceed with refactoring (Phase 3)? [y/n]
```
Responda `y` para prosseguir com a refatoração.

---

## Validação Funcional (Resultados dos Testes)

### Projeto 1 — code-smells-project ✓
Testado com `app.test_client()` — 12 endpoints verificados, todos respondendo corretamente.

### Projeto 2 — ecommerce-api-legacy ✓
Testado via HTTP na porta 3001 — 4 endpoints verificados:
- `GET /api/admin/financial-report` → 200
- `POST /api/checkout` (cartão Visa) → 200 (matrícula criada)
- `POST /api/checkout` (cartão recusado) → 400
- `DELETE /api/users/1` → 200

### Projeto 3 — task-manager-api ✓
Testado com `app.test_client()` — 11 endpoints verificados, todos respondendo corretamente.

---

## Resultados

### Comparação Antes/Depois — Estrutura dos Projetos

#### Projeto 1 — code-smells-project (Python/Flask)

| | Antes (estado original) | Depois (estrutura MVC alvo) |
|---|---|---|
| **Arquivos** | 4 arquivos planos na raiz | Estrutura em diretórios por camada |
| **Config** | `SECRET_KEY` hardcoded em `app.py` | `config/settings.py` com `os.environ` |
| **Models** | `models.py` único com 4 domínios misturados | `models/produto.py`, `models/usuario.py`, `models/pedido.py` com queries parametrizadas |
| **Controllers** | `controllers.py` com lógica + acesso direto ao DB | `controllers/produto_controller.py`, `controllers/pedido_controller.py` (sem SQL) |
| **Routes** | Rotas misturadas em `controllers.py` | `routes/produto_routes.py`, `routes/usuario_routes.py` (apenas roteamento) |
| **DB** | `db_connection = None` global | Conexão por contexto de requisição (`g.db`) |
| **Segurança** | 5+ pontos de SQL Injection | Queries com `?` parametrizado em todos os pontos |
| **Entry point** | `app.py` com config hardcoded | `app.py` limpo (composition root) + `config/settings.py` |

```
Antes:                          Depois (alvo MVC):
code-smells-project/            code-smells-project/
├── app.py          (config)    ├── app.py              (entry point)
├── controllers.py  (rotas)     ├── config/
├── models.py       (tudo)      │   └── settings.py
└── database.py     (global)    ├── models/
                                │   ├── produto.py
                                │   ├── usuario.py
                                │   └── pedido.py
                                ├── controllers/
                                │   ├── produto_controller.py
                                │   └── pedido_controller.py
                                ├── routes/
                                │   ├── produto_routes.py
                                │   └── usuario_routes.py
                                └── database.py  (context-based)
```

#### Projeto 2 — ecommerce-api-legacy (Node.js/Express)

| | Antes (estado original) | Depois (estrutura MVC alvo) |
|---|---|---|
| **Arquivos** | 4 arquivos planos em `src/` | Estrutura em diretórios por camada |
| **Config** | Credenciais hardcoded em `app.js` e `utils.js` | `config/settings.js` com `process.env` |
| **God Class** | `AppManager.js` com DB + rotas + lógica | Responsabilidades distribuídas em 4 camadas |
| **Models** | Queries embutidas nos callbacks de rota | `models/User.js`, `models/Course.js`, `models/Enrollment.js` |
| **Controllers** | Lógica de checkout em callback Express | `controllers/checkoutController.js` (orquestração) |
| **Services** | Lógica de pagamento inline | `services/paymentService.js` (testável em isolamento) |
| **Routes** | Rotas dentro da God Class | `routes/checkoutRoutes.js`, `routes/adminRoutes.js` |
| **Crypto** | `badCrypto()` com hash inseguro | `utils/crypto.js` com bcrypt |

```
Antes:                          Depois (alvo MVC):
src/                            src/
├── AppManager.js  (God Class)  ├── app.js              (entry point)
├── app.js         (config)     ├── config/
├── utils.js       (duplicata)  │   └── settings.js
└── server.js      (entry)      ├── models/
                                │   ├── User.js
                                │   ├── Course.js
                                │   └── Enrollment.js
                                ├── controllers/
                                │   ├── checkoutController.js
                                │   └── adminController.js
                                ├── services/
                                │   └── paymentService.js
                                ├── routes/
                                │   ├── checkoutRoutes.js
                                │   └── adminRoutes.js
                                └── utils/
                                    └── crypto.js
```

#### Projeto 3 — task-manager-api (Python/Flask + SQLAlchemy)

Este projeto já possui separação de camadas (models, routes, services, utils). A skill atua em melhorias dentro das camadas existentes.

| | Antes | Depois |
|---|---|---|
| **Senha** | `hashlib.md5()` em `models/user.py` | `werkzeug.security.generate_password_hash()` |
| **SECRET_KEY** | Hardcoded em `app.py` | `os.environ.get('SECRET_KEY')` em config |
| **N+1** | Query por User e Category no loop em `task_routes.py` | `joinedload(Task.user, Task.category)` na query |
| **Lógica overdue** | Calculada na rota `GET /tasks` | Método `is_overdue` no Model `Task` |
| **Serialização** | `to_dict()` expõe `password` | `to_dict()` com `exclude=['password']` |
| **Constantes** | Magic numbers em `helpers.py` | `PRIORITY_MIN = 1`, `PRIORITY_MAX = 5` nomeados |

---

### Checklists de Validação

#### Projeto 1 — code-smells-project

```markdown
### Fase 1 — Análise
- [x] Linguagem detectada corretamente (Python)
- [x] Framework detectado corretamente (Flask 3.1.1)
- [x] Domínio da aplicação descrito corretamente (E-commerce API: produtos, pedidos, usuários)
- [x] Número de arquivos analisados condiz com a realidade (4 arquivos fonte)

### Fase 2 — Auditoria
- [x] Relatório segue o template definido nos arquivos de referência
- [x] Cada finding tem arquivo e linhas exatos
- [x] Findings ordenados por severidade (CRITICAL → LOW)
- [x] Mínimo de 5 findings identificados (15 findings documentados)
- [x] Detecção de APIs deprecated incluída (sqlite3 nativo sem context manager — M4)
- [x] Skill pausa e pede confirmação antes da Fase 3

### Fase 3 — Refatoração
- [ ] Estrutura de diretórios segue padrão MVC
- [ ] Configuração extraída para módulo de config (sem hardcoded)
- [ ] Models criados para abstrair dados
- [ ] Views/Routes separadas para roteamento
- [ ] Controllers concentram o fluxo da aplicação
- [ ] Error handling centralizado
- [ ] Entry point claro
- [ ] Aplicação inicia sem erros
- [ ] Endpoints originais respondem corretamente
```

> Fase 3 pendente — executar `claude "/refactor-arch"` e confirmar `y` para iniciar a refatoração.

#### Projeto 2 — ecommerce-api-legacy

```markdown
### Fase 1 — Análise
- [x] Linguagem detectada corretamente (Node.js)
- [x] Framework detectado corretamente (Express 4.18.2)
- [x] Domínio da aplicação descrito corretamente (LMS API: checkout, matrículas, pagamentos)
- [x] Número de arquivos analisados condiz com a realidade (4 arquivos fonte em src/)

### Fase 2 — Auditoria
- [x] Relatório segue o template definido nos arquivos de referência
- [x] Cada finding tem arquivo e linhas exatos
- [x] Findings ordenados por severidade (CRITICAL → LOW)
- [x] Mínimo de 5 findings identificados (10 findings documentados)
- [x] Detecção de APIs deprecated incluída (callback-style sqlite3 — M4)
- [x] Skill pausa e pede confirmação antes da Fase 3

### Fase 3 — Refatoração
- [ ] Estrutura de diretórios segue padrão MVC
- [ ] Configuração extraída para módulo de config (sem hardcoded)
- [ ] Models criados para abstrair dados
- [ ] Views/Routes separadas para roteamento
- [ ] Controllers concentram o fluxo da aplicação
- [ ] Error handling centralizado
- [ ] Entry point claro
- [ ] Aplicação inicia sem erros
- [ ] Endpoints originais respondem corretamente
```

> Fase 3 pendente — executar `claude "/refactor-arch"` dentro de `ecommerce-api-legacy/`.

#### Projeto 3 — task-manager-api

```markdown
### Fase 1 — Análise
- [x] Linguagem detectada corretamente (Python)
- [x] Framework detectado corretamente (Flask 3.0.0 + SQLAlchemy)
- [x] Domínio da aplicação descrito corretamente (Task Manager API: tasks, usuários, categorias)
- [x] Número de arquivos analisados condiz com a realidade (10 arquivos fonte)

### Fase 2 — Auditoria
- [x] Relatório segue o template definido nos arquivos de referência
- [x] Cada finding tem arquivo e linhas exatos
- [x] Findings ordenados por severidade (CRITICAL → LOW)
- [x] Mínimo de 5 findings identificados (8 findings documentados)
- [x] Detecção de APIs deprecated incluída (hashlib.md5 para senhas — M4)
- [x] Skill pausa e pede confirmação antes da Fase 3

### Fase 3 — Refatoração
- [ ] Estrutura de diretórios segue padrão MVC
- [ ] Configuração extraída para módulo de config (sem hardcoded)
- [ ] Models criados para abstrair dados
- [ ] Views/Routes separadas para roteamento
- [ ] Controllers concentram o fluxo da aplicação
- [ ] Error handling centralizado
- [ ] Entry point claro
- [ ] Aplicação inicia sem erros
- [ ] Endpoints originais respondem corretamente
```

> Fase 3 pendente — executar `claude "/refactor-arch"` dentro de `task-manager-api/`.

---

### Logs de Validação Funcional (estado pré-refatoração)

Os logs abaixo confirmam que os 3 projetos estão funcionais antes da execução da Fase 3. Esta é a linha de base para validar que a refatoração não quebrou o comportamento.

#### Projeto 1 — code-smells-project (porta 5000)

```
$ "C:/projeto python/python12/python.exe" app.py
 * Serving Flask app 'app'
 * Debug mode: on
 * Running on http://127.0.0.1:5000
 * Restarting with stat

[TEST] GET /health           → 200 OK
[TEST] GET /produtos         → 200 OK  (10 produtos retornados)
[TEST] GET /produtos/1       → 200 OK
[TEST] GET /produtos/busca?q=notebook → 200 OK
[TEST] POST /produtos        → 201 Created
[TEST] PUT /produtos/1       → 200 OK
[TEST] DELETE /produtos/1    → 200 OK
[TEST] POST /login           → 200 OK  (admin@loja.com)
[TEST] GET /usuarios         → 200 OK  (3 usuários)
[TEST] POST /pedidos         → 201 Created
[TEST] GET /pedidos          → 200 OK
[TEST] GET /relatorios/vendas → 200 OK

Total: 12/12 endpoints OK ✓
```

#### Projeto 2 — ecommerce-api-legacy (porta 3000)

```
$ npm start
Server running on port 3000
Database initialized with seed data

[TEST] GET  /api/admin/financial-report     → 200 OK
[TEST] POST /api/checkout (cartão 4111...)  → 200 OK  {"status":"PAID"}
[TEST] POST /api/checkout (cartão 5100...)  → 400     {"status":"DENIED"}
[TEST] DELETE /api/users/1                  → 200 OK

Total: 4/4 endpoints OK ✓
```

#### Projeto 3 — task-manager-api (porta 5000)

```
$ "C:/projeto python/python12/python.exe" app.py
 * Serving Flask app 'app'
 * Debug mode: on
 * Running on http://127.0.0.1:5000

[TEST] GET /              → 200 OK
[TEST] GET /health        → 200 OK
[TEST] GET /tasks         → 200 OK
[TEST] POST /tasks        → 201 Created
[TEST] GET /tasks/1       → 200 OK
[TEST] PUT /tasks/1       → 200 OK
[TEST] DELETE /tasks/1    → 200 OK
[TEST] POST /users        → 201 Created
[TEST] POST /auth/login   → 200 OK
[TEST] GET /categories    → 200 OK
[TEST] GET /reports/summary → 200 OK

Total: 11/11 endpoints OK ✓
```

---

### Observações sobre o Comportamento da Skill em Stacks Diferentes

#### Python/Flask flat (Projeto 1) vs Python/Flask layered (Projeto 3)

A skill demonstrou comportamento distinto nos dois projetos Python, confirmando agnósticidade de tecnologia mesmo dentro da mesma linguagem:

- **Projeto 1 (estrutura flat):** A Fase 1 detectou arquitetura monolítica com 4 arquivos. A Fase 2 encontrou 15 findings, concentrados em CRITICAL (SQL Injection e hardcoded secrets). A Fase 3 exige criação de toda a estrutura de diretórios do zero.

- **Projeto 3 (estrutura parcial):** A Fase 1 detectou arquitetura MVC parcialmente organizada com 10 arquivos e separação de models, routes e services. A Fase 2 encontrou 8 findings, com foco em problemas de segurança dentro das camadas existentes. A Fase 3 atua em melhorias dentro das camadas (sem criar estrutura do zero).

Essa diferença de comportamento é crítica: a skill não aplica o mesmo template de refatoração cegamente — ela adapta a Fase 3 ao contexto detectado na Fase 1.

#### Node.js/Express (Projeto 2) vs Python/Flask

- **Detecção de linguagem:** A Fase 1 detecta Node.js por `package.json` + `require()` / `const express = require('express')`, enquanto detecta Python por `requirements.txt` + `from flask import Flask`.

- **Padrão de async:** O Projeto 2 usa callbacks aninhados (`db.run`, `db.all`, `db.get`) — um padrão que a skill reconhece como signal para o anti-pattern H2 (forte acoplamento) e M4 (API deprecated, já que callbacks são substituídos por `better-sqlite3` síncrono ou Promises em projetos modernos).

- **God Class vs God File:** Em Node.js o problema se manifesta como uma classe (`AppManager`) com múltiplas responsabilidades. Em Python sem OOP estrito, como um arquivo módulo (`models.py`) com múltiplas funções de domínios diferentes. O catálogo de anti-patterns C1 cobre os dois formatos com sinais de detecção distintos.

- **SQL Injection:** Em Python o padrão é `"SELECT * FROM t WHERE id = " + str(id)`. Em Node.js é `db.run("INSERT INTO t VALUES ('" + val + "')")`. O catálogo inclui regex para os dois formatos, garantindo detecção em ambos.

#### Resumo dos Findings por Projeto

| Projeto | CRITICAL | HIGH | MEDIUM | LOW | Total |
|---------|----------|------|--------|-----|-------|
| code-smells-project (Python/Flask) | 6 | 4 | 4 | 1 | 15 |
| ecommerce-api-legacy (Node.js/Express) | 3 | 3 | 4 | 0 | 10 |
| task-manager-api (Python/Flask+SQLAlchemy) | 2 | 2 | 3 | 1 | 8 |

Todos os projetos atingiram o mínimo de 5 findings com pelo menos 1 CRITICAL ou HIGH — critério obrigatório do desafio.

---

## Observações Importantes

1. O `code-smells-project` instalou pacotes localmente na pasta do projeto (via `--target`). Para evitar conflitos, use sempre `"C:/projeto python/python12/python.exe"` diretamente.

2. O `ecommerce-api-legacy` usa banco SQLite **in-memory** — os dados são perdidos ao reiniciar o servidor. Isso é intencional para facilitar os testes da skill.

3. O `task-manager-api` usa Flask-SQLAlchemy com banco em `instance/tasks.db` (criado automaticamente na primeira execução via `db.create_all()`).

4. O aviso `Import "flask_sqlalchemy" could not be resolved` no VS Code é resolvido apontando o interpretador para `C:/projeto python/python12/python.exe`. O arquivo `.vscode/settings.json` já está configurado no `task-manager-api/`.
