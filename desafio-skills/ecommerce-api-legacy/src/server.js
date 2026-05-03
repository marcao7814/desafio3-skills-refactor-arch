const express = require('express');
const AppManager = require('./AppManager');
const { config } = require('./utils');

const app = express();
app.use(express.json());

const manager = new AppManager();
manager.initDb();
manager.setupRoutes(app);

app.listen(config.port, () => {
    console.log('='.repeat(50));
    console.log('SERVIDOR INICIADO');
    console.log(`Rodando em http://localhost:${config.port}`);
    console.log('='.repeat(50));
});
