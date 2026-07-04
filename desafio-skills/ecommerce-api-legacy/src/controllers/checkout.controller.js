const userModel = require('../models/user.model');
const courseModel = require('../models/course.model');
const enrollmentModel = require('../models/enrollment.model');
const paymentModel = require('../models/payment.model');
const auditLogModel = require('../models/auditLog.model');
const { hashPassword } = require('../utils/password');
const { PAYMENT_STATUS_PAID, PAYMENT_STATUS_DENIED, VISA_CARD_PREFIX } = require('../config/constants');

async function processCheckout(db, { userName, email, password, courseId, cardNumber }) {
    if (!userName || !email || !courseId || !cardNumber) {
        throw Object.assign(new Error('userName, email, courseId e cardNumber são obrigatórios'), { status: 400 });
    }

    const course = await courseModel.findActiveById(db, courseId);
    if (!course) {
        throw Object.assign(new Error('Curso não encontrado'), { status: 404 });
    }

    const existingUser = await userModel.findByEmail(db, email);
    let userId;

    if (existingUser) {
        userId = existingUser.id;
    } else {
        if (!password) {
            throw Object.assign(new Error('password é obrigatório para criar uma conta'), { status: 400 });
        }
        userId = await userModel.create(db, { name: userName, email, passwordHash: hashPassword(password) });
    }

    const status = cardNumber.startsWith(VISA_CARD_PREFIX) ? PAYMENT_STATUS_PAID : PAYMENT_STATUS_DENIED;
    if (status === PAYMENT_STATUS_DENIED) {
        throw Object.assign(new Error('Pagamento recusado'), { status: 400 });
    }

    const enrollmentId = await enrollmentModel.create(db, { userId, courseId });
    await paymentModel.create(db, { enrollmentId, amount: course.price, status });
    await auditLogModel.record(db, `Checkout curso ${courseId} por usuário ${userId}`);

    return { enrollmentId };
}

module.exports = { processCheckout };
