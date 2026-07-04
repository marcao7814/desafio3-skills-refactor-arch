const express = require('express');
const settings = require('./config/settings');
const { createDb, initSchema } = require('./db');
const createCheckoutRouter = require('./routes/checkout.routes');
const createAdminRouter = require('./routes/admin.routes');
const createUserRouter = require('./routes/user.routes');
const errorHandler = require('./middlewares/errorHandler');

const app = express();
app.use(express.json());

const db = createDb();
initSchema(db);

app.use('/api/checkout', createCheckoutRouter(db));
app.use('/api/admin', createAdminRouter(db));
app.use('/api/users', createUserRouter(db));

app.use(errorHandler);

app.listen(settings.port, () => {
    console.log(`API rodando em http://localhost:${settings.port}`);
});

module.exports = app;
