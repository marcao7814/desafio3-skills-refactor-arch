const express = require('express');
const checkoutController = require('../controllers/checkout.controller');

function createCheckoutRouter(db) {
    const router = express.Router();

    router.post('/', async (req, res, next) => {
        try {
            const { userName, email, password, courseId, cardNumber } = req.body;
            const result = await checkoutController.processCheckout(db, {
                userName,
                email,
                password,
                courseId,
                cardNumber,
            });
            res.status(200).json({ msg: 'Sucesso', enrollment_id: result.enrollmentId });
        } catch (err) {
            next(err);
        }
    });

    return router;
}

module.exports = createCheckoutRouter;
