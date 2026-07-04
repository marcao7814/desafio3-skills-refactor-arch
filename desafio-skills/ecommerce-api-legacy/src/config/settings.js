module.exports = {
    port: parseInt(process.env.PORT, 10) || 3000,
    dbPath: process.env.DB_PATH || ':memory:',
    paymentGatewayKey: process.env.PAYMENT_GATEWAY_KEY || 'dev-only-insecure-key',
    smtpUser: process.env.SMTP_USER || 'no-reply@example.com',
};
