Problema,Impacto Principal
Callback Hell,Legibilidade e controle de fluxo.
God Class,Manutenibilidade e rigidez do design.
Variáveis Abreviadas,Compreensão imediata do negócio.
Código Duplicado,Custo de manutenção e risco de bugs.

Na engenharia de software, esses termos descrevem Code Smells (cheiros de código) — sintomas de que algo está errado no design ou na implementação, o que prejudica a manutenção, a testabilidade e a evolução do sistema.

Aqui está uma explicação detalhada de cada um:

1. Callback Hell (Inferno de Callbacks)
Ocorre principalmente em linguagens assíncronas (como JavaScript). Acontece quando várias funções assíncronas são aninhadas umas dentro das outras, criando uma estrutura de código em formato de "pirâmide" que se move horizontalmente para a direita.

Por que é ruim: Torna o código extremamente difícil de ler, debugar e tratar erros, já que o fluxo lógico fica fragmentado.

Solução: Utilizar Promises, async/await ou modularizar as funções em arquivos separados.

Callback Hell (Inferno de Callbacks)
Classificação: MEDIUM

Por que: Embora torne o código difícil de ler e manter, o impacto costuma ficar restrito àquela camada específica de execução assíncrona. Em Java moderno (usando CompletableFuture ou Project Reactor), isso é facilmente mitigado com operadores de encadeamento, mas ainda prejudica a rastreabilidade de erros (Stack Traces complexos).

2. God Class (Classe Deus)
É uma classe que "sabe demais" ou "faz demais". Ela viola o Princípio da Responsabilidade Única (SRP) do SOLID. É aquela classe central do sistema que possui milhares de linhas e está conectada a quase todas as outras partes do software.

Por que é ruim:

Acoplamento Alto: Qualquer mudança nela pode quebrar o sistema inteiro.

Baixa Coesão: Ela trata de assuntos diversos (ex: processa pagamento, envia e-mail e valida CPF na mesma classe).

Solução: Refatoração para dividir as responsabilidades em classes menores e especializadas (serviços, utilitários, entidades).

God Class (Classe Deus)
Classificação: CRITICAL
Por que: É o erro mais estrutural e perigoso. Uma God Class cria um ponto único de falha e um alto acoplamento em todo o sistema. Em ecossistemas como Spring Boot, isso geralmente trava a evolução da aplicação, impede a criação de testes unitários eficazes e torna qualquer refatoração futura um pesadelo de regressão.

3. Variáveis Abreviadas (Obscurity)
É a prática de nomear variáveis com apenas uma letra ou siglas que não deixam claro o propósito do dado (ex: int d = 10; em vez de int diasParaVencimento = 10;).

Por que é ruim: O código é lido muito mais vezes do que é escrito. Variáveis como usr, pts ou temp obrigam o desenvolvedor a gastar energia mental tentando lembrar o que aquele valor representa no contexto.

Exceção: Variáveis de controle de loop muito curtos, como o famoso i em um for.

Solução: Adotar Clean Code. Nomes devem ser descritivos e pronunciáveis.
Variáveis Abreviadas
Classificação: LOW
Por que: É um problema de legibilidade e "limpeza" (Clean Code). Embora dificulte o entendimento para novos desenvolvedores e aumente a carga cognitiva, não costuma causar falhas de execução ou impedir a escalabilidade do sistema por si só. É o mais simples de resolver com ferramentas de refatoração da IDE.


4. Código Duplicado (Duplicate Code)
É o famoso "Ctrl+C, Ctrl+V". Ocorre quando a mesma lógica aparece em dois ou mais lugares do sistema.

Por que é ruim: Viola o princípio DRY (Don't Repeat Yourself). Se você precisar corrigir um bug ou alterar a regra de negócio, terá que lembrar de todos os lugares onde copiou aquele código. Se esquecer um, terá comportamentos inconsistentes.

Solução: Extração de método ou criação de uma classe utilitária/serviço que centralize essa lógica.

Código Duplicado
Classificação: HIGH
Por que: O impacto é direto na manutenção. Se uma regra de negócio muda ou um bug é encontrado na lógica duplicada, você terá que corrigi-lo em múltiplos lugares. A chance de esquecer um ponto e gerar inconsistência de dados (especialmente em transações de banco de dados) é altíssima.


observações:
Para uma visão de arquitetura de sistemas, podemos agrupar os outros principais smells em categorias:1. Os Bloatheads (Inchadores)São códigos, métodos e classes que cresceram tanto que se tornaram impossíveis de gerenciar. Além da God Class, temos:Long Method: Um método com muitas linhas de código. Se você precisa de um comentário para explicar o que uma parte do método faz, essa parte deveria ser um método próprio.Data Clumps: Grupos de variáveis que quase sempre aparecem juntas (ex: inicio_periodo, fim_periodo). Elas deveriam ser transformadas em uma classe própria (como Periodo).2. Os Obstrucionistas de MudançaDificultam a evolução do software. Se você altera algo em um lugar e precisa mexer em outros cinco, você tem:Divergent Change: Quando você precisa alterar uma mesma classe por muitos motivos diferentes (falta de coesão).Shotgun Surgery: O oposto da anterior; quando você faz uma única alteração e precisa realizar pequenos ajustes em várias classes diferentes.3. Os DispensáveisElementos que não servem para nada e apenas poluem o projeto:Lazy Class: Uma classe que não faz o suficiente para justificar sua existência.Dead Code: Código que nunca é executado (funções órfãs, variáveis não utilizadas).Speculative Generality: O famoso "vou deixar isso pronto caso a gente precise no futuro", mas que nunca é usado.4. Os Acopladores (Couplers)Problemas que surgem quando as classes estão excessivamente ligadas:Feature Envy (Inveja de funcionalidade): Quando um método de uma classe parece mais interessado nos dados de outra classe do que nos seus próprios.Inappropriate Intimacy: Quando uma classe usa campos ou métodos privados de outra classe de forma excessiva.Tabela de Comparação de Severidade (Novos Exemplos)Code SmellClassificaçãoPor que?Shotgun SurgeryCriticalTorna a manutenção extremamente lenta e propensa a erros.Feature EnvyHighIndica que a lógica de negócio está no lugar errado.Long MethodMediumDificulta a leitura e os testes unitários.Dead CodeLowAumenta o tamanho do projeto, mas não afeta a execução.