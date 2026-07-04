# code-smells-project

API de E-commerce em Python/Flask usada como entrada do desafio `refactor-arch`.

Arquitetura MVC: `src/models`, `src/controllers`, `src/views`, `src/config`, `src/middlewares`.

## Como rodar

```bash
pip install -r requirements.txt
python src/app.py
```

Opcionalmente, copie `.env.example` para `.env` e ajuste `SECRET_KEY`, `DATABASE_URL`,
`PORT` e `DEBUG` antes de rodar.

A aplicação sobe em `http://localhost:5000`. O banco SQLite (`loja.db`) é criado
automaticamente no primeiro boot, já com produtos e usuários de exemplo (senhas
armazenadas com hash).
