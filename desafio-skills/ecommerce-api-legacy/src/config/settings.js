module.exports = {
    port: parseInt(process.env.PORT, 10) || 3000,
    dbPath: process.env.DB_PATH || ':memory:',
    adminApiKey: process.env.ADMIN_API_KEY || 'dev-only-insecure-admin-key',
};
