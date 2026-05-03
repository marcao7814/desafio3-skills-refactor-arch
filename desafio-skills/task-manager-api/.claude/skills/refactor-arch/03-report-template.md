# Template do Relatório de Auditoria

Use **exatamente** este formato ao gerar o relatório na Fase 2.

---

## Formato do Relatório

```
================================
ARCHITECTURE AUDIT REPORT
================================
Project: <nome-do-diretório-do-projeto>
Stack:   <Linguagem> + <Framework versão>
Files:   <N> analyzed | ~<total de linhas> lines of code

Summary
CRITICAL: <N> | HIGH: <N> | MEDIUM: <N> | LOW: <N>

Findings

[CRITICAL] <Nome Exato do Anti-Pattern>
File: <caminho/relativo/arquivo.ext>:<linha-início>-<linha-fim>
Description: <descrição objetiva citando o trecho problemático real>
Impact: <consequência técnica ou de segurança>
Recommendation: <ação concreta e específica para corrigir>

[HIGH] <Nome Exato do Anti-Pattern>
File: <caminho/relativo/arquivo.ext>:<linha>
Description: <descrição>
Impact: <impacto>
Recommendation: <recomendação>

[MEDIUM] <Nome Exato do Anti-Pattern>
File: <caminho/relativo/arquivo.ext>:<linha-início>-<linha-fim>
Description: <descrição>
Impact: <impacto>
Recommendation: <recomendação>

[LOW] <Nome Exato do Anti-Pattern>
File: <caminho/relativo/arquivo.ext>:<linha>
Description: <descrição>
Impact: <impacto>
Recommendation: <recomendação>

================================
Total: <N> findings
================================
```

---

## Regras de Preenchimento

1. **Arquivo e linhas são obrigatórios** em todos os findings — nunca deixar apenas o nome do arquivo sem linhas.
2. **Ordenação:** CRITICAL primeiro, depois HIGH, MEDIUM, LOW. Nunca misturar severidades.
3. **Description específica:** citar o trecho de código real que causou o finding (ex: `f"SELECT * FROM usuarios WHERE id={user_id}"` na linha 45).
4. **Mínimo de 5 findings** por projeto — se encontrar menos, revisar o catálogo e reanalizar.
5. **Ao menos 1 CRITICAL ou HIGH** obrigatório em qualquer projeto analisado.
6. **Múltiplos findings do mesmo anti-pattern** são permitidos e esperados (ex: SQL Injection em 3 lugares = 3 findings).

---

## Exemplo Preenchido

```
================================
ARCHITECTURE AUDIT REPORT
================================
Project: code-smells-project
Stack:   Python + Flask 3.1.1
Files:   4 analyzed | ~350 lines of code

Summary
CRITICAL: 3 | HIGH: 2 | MEDIUM: 3 | LOW: 2

Findings

[CRITICAL] God Class / God File
File: models.py:1-180
Description: Arquivo único contém funções de 3 domínios: criar_produto(),
             fazer_pedido(), autenticar_usuario() — sem separação de responsabilidades.
Impact: Impossível testar em isolamento. Qualquer mudança afeta todos os domínios.
Recommendation: Separar em models/produto_model.py, models/pedido_model.py,
                models/usuario_model.py com responsabilidade única.

[CRITICAL] Hardcoded Credentials
File: app.py:8
Description: app.config['SECRET_KEY'] = 'minha-chave-super-secreta-123' hardcoded.
Impact: Segredo exposto no controle de versão. Comprometimento de toda a sessão.
Recommendation: Usar os.environ.get('SECRET_KEY', 'dev-only-default') em config/settings.py.

[CRITICAL] SQL Injection
File: models.py:22
Description: query = f"SELECT * FROM produtos WHERE id={id}" — id não sanitizado.
Impact: Atacante pode executar SQL arbitrário, expor ou destruir dados.
Recommendation: Usar parâmetros: db.execute("SELECT * FROM produtos WHERE id=?", (id,))

================================
Total: 10 findings
================================
```
