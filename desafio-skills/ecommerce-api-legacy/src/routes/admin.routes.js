const express = require('express');
const financialReportController = require('../controllers/financialReport.controller');
const requireAdmin = require('../middlewares/requireAdmin');

function createAdminRouter(db) {
    const router = express.Router();

    router.get('/financial-report', requireAdmin, async (req, res, next) => {
        try {
            const report = await financialReportController.getFinancialReport(db);
            res.json(report);
        } catch (err) {
            next(err);
        }
    });

    return router;
}

module.exports = createAdminRouter;
