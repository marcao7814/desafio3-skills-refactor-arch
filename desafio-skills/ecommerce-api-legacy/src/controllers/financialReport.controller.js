const courseModel = require('../models/course.model');
const enrollmentModel = require('../models/enrollment.model');
const paymentModel = require('../models/payment.model');
const userModel = require('../models/user.model');
const { PAYMENT_STATUS_PAID } = require('../config/constants');

async function getFinancialReport(db) {
    const [courses, enrollments, payments, users] = await Promise.all([
        courseModel.findAll(db),
        enrollmentModel.findAll(db),
        paymentModel.findAll(db),
        userModel.findAll(db),
    ]);

    const userById = new Map(users.map((user) => [user.id, user]));
    const paymentByEnrollmentId = new Map(payments.map((payment) => [payment.enrollment_id, payment]));

    return courses.map((course) => {
        const courseEnrollments = enrollments.filter((enrollment) => enrollment.course_id === course.id);

        let revenue = 0;
        const students = courseEnrollments.map((enrollment) => {
            const user = userById.get(enrollment.user_id);
            const payment = paymentByEnrollmentId.get(enrollment.id);

            if (payment && payment.status === PAYMENT_STATUS_PAID) {
                revenue += payment.amount;
            }

            return {
                student: user ? user.name : 'Unknown',
                paid: payment ? payment.amount : 0,
            };
        });

        return { course: course.title, revenue, students };
    });
}

module.exports = { getFinancialReport };
