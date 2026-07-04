const userModel = require('../models/user.model');
const enrollmentModel = require('../models/enrollment.model');
const paymentModel = require('../models/payment.model');

async function deleteUser(db, rawId) {
    const id = Number(rawId);
    if (!Number.isInteger(id) || id <= 0) {
        throw Object.assign(new Error('id inválido'), { status: 400 });
    }

    const user = await userModel.findById(db, id);
    if (!user) {
        throw Object.assign(new Error('Usuário não encontrado'), { status: 404 });
    }

    const enrollments = await enrollmentModel.findByUserId(db, id);
    const enrollmentIds = enrollments.map((enrollment) => enrollment.id);

    await paymentModel.deleteByEnrollmentIds(db, enrollmentIds);
    await enrollmentModel.deleteByUserId(db, id);
    await userModel.remove(db, id);
}

module.exports = { deleteUser };
