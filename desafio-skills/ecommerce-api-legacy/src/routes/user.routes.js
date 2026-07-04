const express = require('express');
const userController = require('../controllers/user.controller');

function createUserRouter(db) {
    const router = express.Router();

    router.delete('/:id', async (req, res, next) => {
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
