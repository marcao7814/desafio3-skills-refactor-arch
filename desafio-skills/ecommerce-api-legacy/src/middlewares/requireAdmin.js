const settings = require('../config/settings');

function requireAdmin(req, res, next) {
    const providedKey = req.header('x-admin-key');

    if (!providedKey || providedKey !== settings.adminApiKey) {
        return next(Object.assign(new Error('Acesso negado: credencial de administrador ausente ou inválida'), { status: 401 }));
    }

    next();
}

module.exports = requireAdmin;
