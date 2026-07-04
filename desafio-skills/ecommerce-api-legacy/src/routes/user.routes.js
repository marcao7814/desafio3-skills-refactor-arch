const express = require('express');
const userController = require('../controllers/user.controller');
const requireAdmin = require('../middlewares/requireAdmin');

function createUserRouter(db) {
    const router = express.Router();

    router.delete('/:id', requireAdmin, async (req, res, next) => {
        try {
            await userController.deleteUser(db, req.params.id);
            res.json({ msg: 'Usuário e registros relacionados removidos com sucesso' });
        } catch (err) {
            next(err);
        }
    });

    return router;
}

module.exports = createUserRouter;
